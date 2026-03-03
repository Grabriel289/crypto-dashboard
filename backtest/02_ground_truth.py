"""
02_ground_truth.py — Compute altcoin season ground truth events.

Input:  data/raw_prices.parquet
Output: output/seasons_ground_truth.csv
        output/altcoin_market_returns.parquet

Season = altcoin market outperforms BTC by >= 10% (30D return),
sustained for >= 7 days, with 14-day cooldown between seasons.
"""
import pandas as pd
import numpy as np
import os

from config import (
    DATA_DIR, OUTPUT_DIR,
    BREADTH_LOOKBACK, SEASON_THRESHOLD, SEASON_MIN_DURATION,
    SEASON_COOLDOWN, PEAK_DRAWDOWN,
)


def calc_altcoin_market_return(prices: pd.DataFrame, lookback: int = BREADTH_LOOKBACK) -> pd.Series:
    """Equal-weight N-day return of all altcoins (ex-BTC)."""
    returns = prices.pct_change(lookback) * 100  # percentage
    alt_returns = returns.drop(columns=["BTCUSDT"], errors="ignore")
    return alt_returns.mean(axis=1, skipna=True)


def calc_btc_return(prices: pd.DataFrame, lookback: int = BREADTH_LOOKBACK) -> pd.Series:
    """BTC N-day return."""
    if "BTCUSDT" not in prices.columns:
        raise ValueError("BTCUSDT not found in price data")
    return prices["BTCUSDT"].pct_change(lookback) * 100


def detect_seasons(outperformance: pd.Series) -> pd.DataFrame:
    """
    Detect altcoin seasons from the outperformance series.

    Season = outperformance > SEASON_THRESHOLD for >= SEASON_MIN_DURATION days.
    Cooldown between seasons = SEASON_COOLDOWN days.
    """
    is_season = outperformance > SEASON_THRESHOLD

    # Find contiguous runs of True
    groups = (is_season != is_season.shift()).cumsum()
    season_groups = is_season.groupby(groups)

    raw_seasons = []
    for group_id, group in season_groups:
        if not group.iloc[0]:  # skip non-season groups
            continue
        if len(group) < SEASON_MIN_DURATION:
            continue
        raw_seasons.append({
            "start_date": group.index[0],
            "end_date": group.index[-1],
            "duration_days": len(group),
        })

    # Apply cooldown — merge seasons that are too close
    merged = []
    for s in raw_seasons:
        if merged and (s["start_date"] - merged[-1]["end_date"]).days < SEASON_COOLDOWN:
            # Extend previous season
            merged[-1]["end_date"] = s["end_date"]
            merged[-1]["duration_days"] = (merged[-1]["end_date"] - merged[-1]["start_date"]).days
        else:
            merged.append(s)

    return merged


def find_peaks(merged_seasons: list, outperformance: pd.Series,
               alt_return: pd.Series, btc_return: pd.Series) -> pd.DataFrame:
    """Find peak date within each season and compute stats."""
    results = []

    for i, season in enumerate(merged_seasons):
        window = outperformance.loc[season["start_date"]:season["end_date"]]
        if window.empty:
            continue

        peak_date = window.idxmax()
        max_outperform = window.max()

        # BTC and alt returns during the season
        alt_at_start = alt_return.loc[:season["start_date"]].iloc[-1] if len(alt_return.loc[:season["start_date"]]) > 0 else 0
        alt_at_end = alt_return.loc[:season["end_date"]].iloc[-1] if len(alt_return.loc[:season["end_date"]]) > 0 else 0
        btc_at_start = btc_return.loc[:season["start_date"]].iloc[-1] if len(btc_return.loc[:season["start_date"]]) > 0 else 0
        btc_at_end = btc_return.loc[:season["end_date"]].iloc[-1] if len(btc_return.loc[:season["end_date"]]) > 0 else 0

        results.append({
            "season_id": i + 1,
            "start_date": season["start_date"],
            "peak_date": peak_date,
            "end_date": season["end_date"],
            "duration_days": season["duration_days"],
            "max_altcoin_outperformance": round(max_outperform, 2),
            "btc_return_during": round(btc_at_end - btc_at_start, 2),
            "alt_return_during": round(alt_at_end - alt_at_start, 2),
        })

    return pd.DataFrame(results)


def main():
    print("=" * 60)
    print("ABM BACKTEST — Step 2: Ground Truth (Altcoin Seasons)")
    print("=" * 60)

    # Load prices
    prices_path = os.path.join(DATA_DIR, "raw_prices.parquet")
    prices = pd.read_parquet(prices_path)
    print(f"Loaded: {len(prices)} days, {len(prices.columns)} symbols")

    # Calculate returns
    alt_return = calc_altcoin_market_return(prices)
    btc_return = calc_btc_return(prices)

    # Outperformance = alt market return - BTC return
    outperformance = alt_return - btc_return
    outperformance = outperformance.dropna()
    print(f"Outperformance series: {len(outperformance)} days")

    # Detect seasons
    raw_seasons = detect_seasons(outperformance)
    print(f"Raw seasons detected: {len(raw_seasons)}")

    # Find peaks and build final table
    seasons_df = find_peaks(raw_seasons, outperformance, alt_return, btc_return)
    print(f"\nFinal seasons: {len(seasons_df)}")
    print(seasons_df.to_string(index=False))

    # Save
    seasons_path = os.path.join(OUTPUT_DIR, "seasons_ground_truth.csv")
    seasons_df.to_csv(seasons_path, index=False)
    print(f"\nSaved: {seasons_path}")

    # Save outperformance and returns for downstream use
    returns_df = pd.DataFrame({
        "altcoin_mkt_return": alt_return,
        "btc_return": btc_return,
        "outperformance": outperformance,
    })
    returns_path = os.path.join(OUTPUT_DIR, "altcoin_market_returns.parquet")
    returns_df.to_parquet(returns_path)
    print(f"Saved: {returns_path}")


if __name__ == "__main__":
    main()
