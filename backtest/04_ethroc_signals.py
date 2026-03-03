"""
04_ethroc_signals.py — Compute 3 ETH/BTC ROC signal methods.

Input:  data/raw_prices.parquet
Output: output/ethroc_signals.parquet  (date × ROC values + signal + peak_warning)

Methods:
  A. ROC_7D     — 7-day rate of change (current, noisy)
  B. ROC_14D    — 14-day rate of change (slower, less noise)
  C. ROC_7D+3D  — 7-day ROC with 3-day below-zero confirmation
"""
import pandas as pd
import numpy as np
import os

from config import (
    DATA_DIR, OUTPUT_DIR,
    ROC7_PERIOD, ROC14_PERIOD,
    ROC7C_PERIOD, ROC7C_CONFIRM,
)


def calc_ethbtc_ratio(prices: pd.DataFrame) -> pd.Series:
    """ETH/BTC price ratio."""
    if "ETHUSDT" not in prices.columns or "BTCUSDT" not in prices.columns:
        raise ValueError("ETHUSDT and BTCUSDT are required")
    return prices["ETHUSDT"] / prices["BTCUSDT"]


def signal_roc7(ethbtc: pd.Series) -> tuple:
    """
    ROC = (ratio_today - ratio_7d_ago) / ratio_7d_ago * 100
    Peak warning: ROC crosses 0 downward.
    """
    roc = ethbtc.pct_change(ROC7_PERIOD) * 100
    prev_roc = roc.shift(1)

    signal = pd.Series("NEUTRAL", index=roc.index)
    signal[roc > 3] = "STRONG"
    signal[(roc > 0) & (roc <= 3)] = "POSITIVE"
    signal[(roc < 0) & (roc >= -3)] = "WARNING"
    signal[roc < -3] = "BEARISH"

    # Peak warning = crosses 0 downward
    peak_warning = (roc <= 0) & (prev_roc > 0)

    return roc, signal, peak_warning


def signal_roc14(ethbtc: pd.Series) -> tuple:
    """
    ROC = (ratio_today - ratio_14d_ago) / ratio_14d_ago * 100
    Slower than ROC_7D — less noise.
    """
    roc = ethbtc.pct_change(ROC14_PERIOD) * 100
    prev_roc = roc.shift(1)

    signal = pd.Series("NEUTRAL", index=roc.index)
    signal[roc > 3] = "STRONG"
    signal[(roc > 0) & (roc <= 3)] = "POSITIVE"
    signal[(roc < 0) & (roc >= -3)] = "WARNING"
    signal[roc < -3] = "BEARISH"

    peak_warning = (roc <= 0) & (prev_roc > 0)

    return roc, signal, peak_warning


def signal_roc7_confirmed(ethbtc: pd.Series,
                          confirm_days: int = ROC7C_CONFIRM) -> tuple:
    """
    ROC_7D must stay below 0 for N consecutive days
    before triggering peak warning. Filters 1-day dip noise.
    """
    roc = ethbtc.pct_change(ROC7C_PERIOD) * 100

    # Rolling confirmation: N consecutive days below zero
    below_zero = (roc < 0).astype(int)
    confirmed = below_zero.rolling(confirm_days).sum() == confirm_days

    confirmed = confirmed.astype(bool)
    prev_confirmed = confirmed.shift(1, fill_value=False)

    signal = pd.Series("NEUTRAL", index=roc.index)
    signal[roc > 3] = "STRONG"
    signal[(roc > 0) & (roc <= 3)] = "POSITIVE"
    signal[roc < 0] = "WARNING"
    signal[roc < -3] = "BEARISH"

    # Peak warning = first day of confirmed streak
    peak_warning = confirmed & ~prev_confirmed

    return roc, signal, peak_warning


def main():
    print("=" * 60)
    print("ABM BACKTEST — Step 4: ETH/BTC ROC Signal Methods")
    print("=" * 60)

    # Load prices
    prices_path = os.path.join(DATA_DIR, "raw_prices.parquet")
    prices = pd.read_parquet(prices_path)
    print(f"Loaded: {len(prices)} days, {len(prices.columns)} symbols")

    # Calculate ETH/BTC ratio
    ethbtc = calc_ethbtc_ratio(prices)
    ethbtc = ethbtc.dropna()
    print(f"ETH/BTC ratio series: {len(ethbtc)} days")

    # Method A: ROC_7D
    roc7, sig7, peak7 = signal_roc7(ethbtc)
    print(f"\nROC_7D:  {peak7.sum()} peak warnings")

    # Method B: ROC_14D
    roc14, sig14, peak14 = signal_roc14(ethbtc)
    print(f"ROC_14D: {peak14.sum()} peak warnings")

    # Method C: ROC_7D + 3-day confirmation
    roc7c, sig7c, peak7c = signal_roc7_confirmed(ethbtc)
    print(f"ROC_7D+3D: {peak7c.sum()} peak warnings")

    # Build output dataframe
    signals_df = pd.DataFrame({
        "ethbtc_ratio": ethbtc,
        "roc7": roc7,
        "roc7_signal": sig7,
        "roc7_peak_warning": peak7,
        "roc14": roc14,
        "roc14_signal": sig14,
        "roc14_peak_warning": peak14,
        "roc7c": roc7c,
        "roc7c_signal": sig7c,
        "roc7c_peak_warning": peak7c,
    })

    # Save
    out_path = os.path.join(OUTPUT_DIR, "ethroc_signals.parquet")
    signals_df.to_parquet(out_path)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
