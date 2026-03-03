"""
03_bm_signals.py — Compute 3 BM signal methods.

Input:  data/raw_prices.parquet
Output: output/bm_signals.parquet  (date × bm values + signal labels)

Methods:
  1. BM_14D  — breadth momentum with 14-day lookback
  2. BM_30D  — breadth momentum with 30-day lookback
  3. EMA     — EMA(7) / EMA(21) crossover on breadth
"""
import pandas as pd
import numpy as np
import os

from config import (
    DATA_DIR, OUTPUT_DIR,
    BREADTH_LOOKBACK, MIN_VALID_COUNT,
    BM14_LOOKBACK, BM14_ENTRY, BM14_EXIT,
    BM30_LOOKBACK, BM30_ENTRY, BM30_EXIT,
    EMA_FAST, EMA_SLOW,
)


def calc_breadth(prices: pd.DataFrame, btc_col: str = "BTCUSDT",
                 lookback: int = BREADTH_LOOKBACK) -> pd.Series:
    """
    Breadth = % of altcoins outperforming BTC on N-day return.
    Dynamic denominator — only coins with valid data count.
    """
    returns = prices.pct_change(lookback)
    btc_ret = returns[btc_col]
    alt_ret = returns.drop(columns=[btc_col])

    outperform = alt_ret.gt(btc_ret, axis=0)

    valid_count = alt_ret.notna().sum(axis=1)
    outperform_count = outperform.sum(axis=1)

    breadth = outperform_count / valid_count * 100

    # If fewer than MIN_VALID_COUNT valid coins, mark as NaN
    breadth[valid_count < MIN_VALID_COUNT] = float("nan")

    return breadth


def signal_bm14(breadth: pd.Series,
                entry_threshold: float = BM14_ENTRY,
                exit_threshold: float = BM14_EXIT) -> tuple:
    """
    BM = Breadth_today - Breadth_14d_ago
    Entry: BM > +threshold
    Exit:  BM < -threshold
    """
    bm = breadth - breadth.shift(BM14_LOOKBACK)

    signal = pd.Series("NEUTRAL", index=bm.index)
    signal[bm > entry_threshold] = "ENTRY"
    signal[bm < exit_threshold] = "EXIT"
    signal[(bm > 0) & (bm <= entry_threshold)] = "RISING"
    signal[(bm < 0) & (bm >= exit_threshold)] = "FALLING"

    return bm, signal


def signal_bm30(breadth: pd.Series,
                entry_threshold: float = BM30_ENTRY,
                exit_threshold: float = BM30_EXIT) -> tuple:
    """
    BM = Breadth_today - Breadth_30d_ago
    Same as BM14 but with longer lookback — slower, less noise.
    """
    bm = breadth - breadth.shift(BM30_LOOKBACK)

    signal = pd.Series("NEUTRAL", index=bm.index)
    signal[bm > entry_threshold] = "ENTRY"
    signal[bm < exit_threshold] = "EXIT"
    signal[(bm > 0) & (bm <= entry_threshold)] = "RISING"
    signal[(bm < 0) & (bm >= exit_threshold)] = "FALLING"

    return bm, signal


def signal_ema_cross(breadth: pd.Series,
                     fast_period: int = EMA_FAST,
                     slow_period: int = EMA_SLOW) -> tuple:
    """
    EMA_fast = EMA(Breadth, 7)
    EMA_slow = EMA(Breadth, 21)
    Entry: fast crosses slow upward
    Exit:  fast crosses slow downward
    """
    ema_fast = breadth.ewm(span=fast_period, adjust=False).mean()
    ema_slow = breadth.ewm(span=slow_period, adjust=False).mean()

    cross = ema_fast - ema_slow
    prev_cross = cross.shift(1)

    signal = pd.Series("NEUTRAL", index=breadth.index)
    signal[cross > 0] = "RISING"
    signal[cross < 0] = "FALLING"

    # Crossover events override RISING/FALLING
    signal[(cross > 0) & (prev_cross <= 0)] = "ENTRY"
    signal[(cross < 0) & (prev_cross >= 0)] = "EXIT"

    return cross, signal


def main():
    print("=" * 60)
    print("ABM BACKTEST — Step 3: BM Signal Methods")
    print("=" * 60)

    # Load prices
    prices_path = os.path.join(DATA_DIR, "raw_prices.parquet")
    prices = pd.read_parquet(prices_path)
    print(f"Loaded: {len(prices)} days, {len(prices.columns)} symbols")

    # Calculate breadth
    breadth = calc_breadth(prices)
    breadth = breadth.dropna()
    print(f"Breadth series: {len(breadth)} days")

    # Method 1: BM_14D
    bm14, sig14 = signal_bm14(breadth)
    entry14 = (sig14 == "ENTRY").sum()
    exit14 = (sig14 == "EXIT").sum()
    print(f"\nBM_14D: {entry14} ENTRY signals, {exit14} EXIT signals")

    # Method 2: BM_30D
    bm30, sig30 = signal_bm30(breadth)
    entry30 = (sig30 == "ENTRY").sum()
    exit30 = (sig30 == "EXIT").sum()
    print(f"BM_30D: {entry30} ENTRY signals, {exit30} EXIT signals")

    # Method 3: EMA crossover
    ema_cross, sig_ema = signal_ema_cross(breadth)
    entry_ema = (sig_ema == "ENTRY").sum()
    exit_ema = (sig_ema == "EXIT").sum()
    print(f"EMA:    {entry_ema} ENTRY signals, {exit_ema} EXIT signals")

    # Build output dataframe
    signals_df = pd.DataFrame({
        "breadth": breadth,
        "bm14": bm14,
        "bm14_signal": sig14,
        "bm30": bm30,
        "bm30_signal": sig30,
        "ema_cross": ema_cross,
        "ema_signal": sig_ema,
    })

    # Save
    out_path = os.path.join(OUTPUT_DIR, "bm_signals.parquet")
    signals_df.to_parquet(out_path)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
