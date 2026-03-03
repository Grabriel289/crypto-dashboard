"""
01_fetch_data.py — Fetch historical daily OHLCV from Binance & OKX via ccxt.

Output: data/raw_prices.parquet  (date × symbol pivot of close prices)
        data/raw_volume.parquet  (date × symbol pivot of quote volume)

Run time: ~5-10 minutes (rate-limited fetching).
"""
import ccxt
import pandas as pd
import time
import os
from datetime import datetime

from config import (
    BACKTEST_START, BACKTEST_END, TIMEFRAME,
    CORE_ASSETS, UNIVERSE_BINANCE, UNIVERSE_OKX,
    DATA_DIR, MAX_CONSECUTIVE_MISSING, FILL_METHOD,
    MIN_COVERAGE_PCT, MAX_SINGLE_DAY_RETURN, MIN_SINGLE_DAY_RETURN,
)


def fetch_binance(symbols: list, start: str, end: str) -> pd.DataFrame:
    """Fetch daily OHLCV for a list of Binance symbols."""
    exchange = ccxt.binance({"enableRateLimit": True})
    since = exchange.parse8601(f"{start}T00:00:00Z")
    end_ms = exchange.parse8601(f"{end}T23:59:59Z")

    all_rows = []

    for sym in symbols:
        print(f"  [Binance] Fetching {sym}...", end="", flush=True)
        try:
            cursor = since
            bars = []
            while cursor < end_ms:
                ohlcv = exchange.fetch_ohlcv(sym, TIMEFRAME, since=cursor, limit=1000)
                if not ohlcv:
                    break
                bars.extend(ohlcv)
                cursor = ohlcv[-1][0] + 86400_000  # next day
                time.sleep(0.1)

            for bar in bars:
                ts, o, h, l, c, v = bar
                dt = datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                if dt > end:
                    break
                all_rows.append({
                    "date": dt,
                    "symbol": sym.replace("/", ""),
                    "close": c,
                    "volume": v,
                    "source": "binance",
                })
            print(f" {len(bars)} bars")
        except Exception as e:
            print(f" SKIP ({e})")
            continue

    return pd.DataFrame(all_rows)


def fetch_okx(symbols: list, start: str, end: str) -> pd.DataFrame:
    """Fetch daily OHLCV for OKX symbols (XMR etc.)."""
    exchange = ccxt.okx({"enableRateLimit": True})
    since = exchange.parse8601(f"{start}T00:00:00Z")
    end_ms = exchange.parse8601(f"{end}T23:59:59Z")

    all_rows = []

    for sym in symbols:
        # ccxt expects 'XMR/USDT' format
        ccxt_sym = sym.replace("-", "/")
        print(f"  [OKX] Fetching {ccxt_sym}...", end="", flush=True)
        try:
            cursor = since
            bars = []
            while cursor < end_ms:
                ohlcv = exchange.fetch_ohlcv(ccxt_sym, TIMEFRAME, since=cursor, limit=300)
                if not ohlcv:
                    break
                bars.extend(ohlcv)
                cursor = ohlcv[-1][0] + 86400_000
                time.sleep(0.2)

            for bar in bars:
                ts, o, h, l, c, v = bar
                dt = datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                if dt > end:
                    break
                # Normalize symbol to match Binance format
                norm_sym = sym.replace("-", "")  # XMR-USDT → XMRUSDT
                all_rows.append({
                    "date": dt,
                    "symbol": norm_sym,
                    "close": c,
                    "volume": v,
                    "source": "okx",
                })
            print(f" {len(bars)} bars")
        except Exception as e:
            print(f" SKIP ({e})")
            continue

    return pd.DataFrame(all_rows)


def quality_check(df: pd.DataFrame) -> pd.DataFrame:
    """Apply data quality rules and flag/filter bad data."""
    print("\n--- Data Quality Checks ---")

    # Remove duplicate date/symbol pairs (keep last)
    df = df.drop_duplicates(subset=["date", "symbol"], keep="last")

    # Convert to pivot
    prices = df.pivot_table(index="date", columns="symbol", values="close")
    prices.index = pd.to_datetime(prices.index)
    prices = prices.sort_index()

    # Filter to backtest window
    prices = prices.loc[BACKTEST_START:BACKTEST_END]

    # Check daily returns for anomalies
    returns = prices.pct_change()
    for sym in returns.columns:
        suspect_high = (returns[sym] > MAX_SINGLE_DAY_RETURN).sum()
        suspect_low = (returns[sym] < MIN_SINGLE_DAY_RETURN).sum()
        if suspect_high > 0 or suspect_low > 0:
            print(f"  [WARN] {sym}: {suspect_high} days >+500%, {suspect_low} days <-99%")

    # Coverage check per symbol
    total_days = len(prices)
    for sym in prices.columns:
        coverage = prices[sym].notna().sum() / total_days
        if coverage < MIN_COVERAGE_PCT:
            print(f"  [INFO] {sym}: {coverage:.1%} coverage (< {MIN_COVERAGE_PCT:.0%}) — limited history, kept")

    # Forward fill gaps up to MAX_CONSECUTIVE_MISSING days
    prices = prices.ffill(limit=MAX_CONSECUTIVE_MISSING)

    print(f"  Final: {len(prices)} days, {len(prices.columns)} symbols")
    return prices


def main():
    print("=" * 60)
    print("ABM BACKTEST — Step 1: Fetch Historical Data")
    print(f"Period: {BACKTEST_START} to {BACKTEST_END}")
    print("=" * 60)

    # Dedupe: remove coins from UNIVERSE that are already in CORE
    all_binance = list(set(CORE_ASSETS + UNIVERSE_BINANCE))
    # ccxt expects "BTC/USDT" format
    binance_ccxt = [s.replace("USDT", "/USDT") for s in all_binance]

    print(f"\nFetching {len(binance_ccxt)} symbols from Binance...")
    df_binance = fetch_binance(binance_ccxt, BACKTEST_START, BACKTEST_END)

    print(f"\nFetching {len(UNIVERSE_OKX)} symbols from OKX...")
    df_okx = fetch_okx(UNIVERSE_OKX, BACKTEST_START, BACKTEST_END)

    # Combine
    df_all = pd.concat([df_binance, df_okx], ignore_index=True)
    print(f"\nTotal raw rows: {len(df_all)}")

    # Save raw data
    raw_path = os.path.join(DATA_DIR, "raw_prices_long.parquet")
    df_all.to_parquet(raw_path, index=False)
    print(f"Saved raw data: {raw_path}")

    # Quality check & pivot
    prices = quality_check(df_all)

    # Save pivot table
    prices_path = os.path.join(DATA_DIR, "raw_prices.parquet")
    prices.to_parquet(prices_path)
    print(f"Saved price pivot: {prices_path}")

    # Also save volume pivot
    vol_df = df_all.pivot_table(index="date", columns="symbol", values="volume")
    vol_df.index = pd.to_datetime(vol_df.index)
    vol_df = vol_df.sort_index().loc[BACKTEST_START:BACKTEST_END]
    vol_path = os.path.join(DATA_DIR, "raw_volume.parquet")
    vol_df.to_parquet(vol_path)
    print(f"Saved volume pivot: {vol_path}")

    print("\n--- Done ---")
    print(f"Symbols: {list(prices.columns)}")


if __name__ == "__main__":
    main()
