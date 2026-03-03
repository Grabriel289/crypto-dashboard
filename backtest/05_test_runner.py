"""
05_test_runner.py — Run all 5 tests and generate summary report.

Input:  output/seasons_ground_truth.csv
        output/bm_signals.parquet
        output/ethroc_signals.parquet
        output/altcoin_market_returns.parquet

Output: output/backtest_results.csv
        output/test_summary.md

Tests:
  A: BM lead time (days before season start)
  B: BM false signal rate
  C: ETH/BTC ROC peak warning lead time
  D: ETH/BTC ROC false alarm rate
  E: Combined 3×3 scoring
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

from config import (
    OUTPUT_DIR, PEAK_DRAWDOWN,
    WEIGHT_BM_LEAD, WEIGHT_BM_FALSE, WEIGHT_BM_NOISE,
    WEIGHT_ROC_LEAD, WEIGHT_ROC_FALSE, WEIGHT_ROC_NOISE,
)


# ── Test A — BM Lead Time ─────────────────────────────────────────────

def test_bm_lead_time(bm_signals: pd.DataFrame,
                      seasons: pd.DataFrame) -> pd.DataFrame:
    """
    For each altcoin season, measure how many days before season start
    each BM method first triggers an ENTRY signal.

    Window: 60 days before season start → 30 days after season start.
    """
    results = []

    for _, season in seasons.iterrows():
        start = pd.Timestamp(season["start_date"])
        window_start = start - pd.Timedelta(days=60)
        window_end = start + pd.Timedelta(days=30)
        window = bm_signals.loc[window_start:window_end]

        for method in ["bm14", "bm30", "ema"]:
            col = f"{method}_signal"
            if col not in window.columns:
                continue
            entry_dates = window[window[col] == "ENTRY"].index

            if len(entry_dates) > 0:
                first_entry = entry_dates[0]
                lead_days = (start - first_entry).days
            else:
                lead_days = None

            results.append({
                "season_id": season["season_id"],
                "start_date": start,
                "method": method,
                "lead_days": lead_days,
                "signal_found": lead_days is not None,
            })

    return pd.DataFrame(results)


# ── Test B — BM False Signal Rate ─────────────────────────────────────

def test_bm_false_signal(bm_signals: pd.DataFrame,
                         seasons: pd.DataFrame,
                         forward_window: int = 30) -> pd.DataFrame:
    """
    Count % of ENTRY signals NOT followed by an altcoin season
    within forward_window days.
    """
    results = {}

    for method in ["bm14", "bm30", "ema"]:
        col = f"{method}_signal"
        if col not in bm_signals.columns:
            continue
        all_entries = bm_signals[bm_signals[col] == "ENTRY"].index
        true_positives = 0

        for entry_date in all_entries:
            forward_end = entry_date + pd.Timedelta(days=forward_window)
            # Check if any season starts within the forward window
            in_season = seasons[
                (pd.to_datetime(seasons["start_date"]) >= entry_date) &
                (pd.to_datetime(seasons["start_date"]) <= forward_end)
            ]
            if len(in_season) > 0:
                true_positives += 1

        total = len(all_entries)
        false_rate = (total - true_positives) / total * 100 if total > 0 else 100
        total_days = (bm_signals.index[-1] - bm_signals.index[0]).days
        years = total_days / 365 if total_days > 0 else 1

        results[method] = {
            "total_signals": total,
            "true_positives": true_positives,
            "false_signals": total - true_positives,
            "false_rate_pct": round(false_rate, 1),
            "signals_per_year": round(total / years, 1),
        }

    return pd.DataFrame(results).T


# ── Test C — ETH/BTC ROC Peak Warning Lead Time ──────────────────────

def test_ethroc_lead_time(ethroc_signals: pd.DataFrame,
                          seasons: pd.DataFrame) -> pd.DataFrame:
    """
    For each season peak, measure how many days before peak
    each ETH/BTC ROC method first triggers a peak warning.

    Window: season start → peak + 14 days.
    """
    results = []

    for _, season in seasons.iterrows():
        start = pd.Timestamp(season["start_date"])
        peak = pd.Timestamp(season["peak_date"])
        window_end = peak + pd.Timedelta(days=14)
        window = ethroc_signals.loc[start:window_end]

        for method in ["roc7", "roc14", "roc7c"]:
            col = f"{method}_peak_warning"
            if col not in window.columns:
                continue
            warn_dates = window[window[col] == True].index

            if len(warn_dates) > 0:
                first_warn = warn_dates[0]
                lead_days = (peak - first_warn).days
            else:
                first_warn = None
                lead_days = None

            results.append({
                "season_id": season["season_id"],
                "peak_date": peak,
                "method": method,
                "warn_date": first_warn,
                "lead_days": lead_days,
                "warning_found": lead_days is not None,
            })

    return pd.DataFrame(results)


# ── Test D — ETH/BTC ROC False Alarm Rate ─────────────────────────────

def test_ethroc_false_alarm(ethroc_signals: pd.DataFrame,
                            alt_returns: pd.Series,
                            forward_window: int = 30) -> pd.DataFrame:
    """
    Count % of peak warnings NOT followed by a real altcoin drawdown
    (> PEAK_DRAWDOWN %) within forward_window days.
    """
    results = {}

    for method in ["roc7", "roc14", "roc7c"]:
        col = f"{method}_peak_warning"
        if col not in ethroc_signals.columns:
            continue
        all_warnings = ethroc_signals[ethroc_signals[col] == True].index
        true_alarms = 0

        for warn_date in all_warnings:
            forward_end = warn_date + pd.Timedelta(days=forward_window)
            fwd_returns = alt_returns.loc[warn_date:forward_end]
            if len(fwd_returns) > 0 and fwd_returns.min() < -PEAK_DRAWDOWN:
                true_alarms += 1

        total = len(all_warnings)
        false_alarm_rate = (total - true_alarms) / total * 100 if total > 0 else 100
        total_days = (ethroc_signals.index[-1] - ethroc_signals.index[0]).days
        years = total_days / 365 if total_days > 0 else 1

        results[method] = {
            "total_warnings": total,
            "true_alarms": true_alarms,
            "false_alarms": total - true_alarms,
            "false_alarm_pct": round(false_alarm_rate, 1),
            "warnings_per_year": round(total / years, 1),
        }

    return pd.DataFrame(results).T


# ── Test E — Combined Score ───────────────────────────────────────────

def test_combined_score(bm_lead_df: pd.DataFrame,
                        bm_false_df: pd.DataFrame,
                        roc_lead_df: pd.DataFrame,
                        roc_false_df: pd.DataFrame) -> pd.DataFrame:
    """
    Score each BM × ETH ROC combination (3×3 = 9).
    Select the best combination.
    """
    combinations = []

    for bm_method in ["bm14", "bm30", "ema"]:
        for roc_method in ["roc7", "roc14", "roc7c"]:
            # BM metrics
            bm_leads = bm_lead_df[bm_lead_df["method"] == bm_method]["lead_days"].dropna()
            bm_lead_med = bm_leads.median() if len(bm_leads) > 0 else 0
            bm_false = bm_false_df.loc[bm_method, "false_rate_pct"] if bm_method in bm_false_df.index else 100
            bm_noise = bm_false_df.loc[bm_method, "signals_per_year"] if bm_method in bm_false_df.index else 20

            # ROC metrics
            roc_leads = roc_lead_df[roc_lead_df["method"] == roc_method]["lead_days"].dropna()
            roc_lead_med = roc_leads.median() if len(roc_leads) > 0 else 0
            roc_false = roc_false_df.loc[roc_method, "false_alarm_pct"] if roc_method in roc_false_df.index else 100
            roc_noise = roc_false_df.loc[roc_method, "warnings_per_year"] if roc_method in roc_false_df.index else 20

            # Normalize and weight (higher = better)
            score = (
                min(bm_lead_med / 30, 1.0) * WEIGHT_BM_LEAD * 100 +
                (100 - bm_false) / 100 * WEIGHT_BM_FALSE * 100 +
                min((10 - min(bm_noise, 10)) / 10, 1.0) * WEIGHT_BM_NOISE * 100 +
                min(roc_lead_med / 21, 1.0) * WEIGHT_ROC_LEAD * 100 +
                (100 - roc_false) / 100 * WEIGHT_ROC_FALSE * 100 +
                min((8 - min(roc_noise, 8)) / 8, 1.0) * WEIGHT_ROC_NOISE * 100
            )

            combinations.append({
                "bm_method": bm_method,
                "roc_method": roc_method,
                "bm_lead_med": round(bm_lead_med, 1),
                "bm_false": round(bm_false, 1),
                "bm_noise": round(bm_noise, 1),
                "roc_lead_med": round(roc_lead_med, 1),
                "roc_false": round(roc_false, 1),
                "roc_noise": round(roc_noise, 1),
                "combined_score": round(score, 1),
            })

    df = pd.DataFrame(combinations)
    return df.sort_values("combined_score", ascending=False).reset_index(drop=True)


# ── Summary Report ────────────────────────────────────────────────────

def generate_summary(seasons: pd.DataFrame,
                     bm_lead_df: pd.DataFrame,
                     bm_false_df: pd.DataFrame,
                     roc_lead_df: pd.DataFrame,
                     roc_false_df: pd.DataFrame,
                     combined_df: pd.DataFrame) -> str:
    """Generate markdown test_summary.md report."""
    lines = []
    lines.append("# ABM Signal Validation — Results")
    lines.append(f"## Run date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # Ground Truth Summary
    lines.append("### Ground Truth Summary")
    lines.append(f"- Seasons detected: {len(seasons)}")
    if len(seasons) > 0:
        lines.append(f"- Date range: {seasons['start_date'].min()} to {seasons['end_date'].max()}")
        lines.append("- Seasons:")
        for _, s in seasons.iterrows():
            lines.append(f"  - Season {s['season_id']}: {s['start_date']} → {s['end_date']} "
                         f"(peak: {s['peak_date']}, {s['duration_days']}d, "
                         f"max outperf: {s['max_altcoin_outperformance']}%)")
    lines.append("")

    # Test A — BM Lead Time
    lines.append("### Test A — BM Lead Time")
    lines.append("| Method | Median Lead (days) | Min | Max | Detected/Total |")
    lines.append("|--------|--------------------|-----|-----|----------------|")
    for method in ["bm14", "bm30", "ema"]:
        subset = bm_lead_df[bm_lead_df["method"] == method]
        detected = subset["signal_found"].sum()
        total = len(subset)
        leads = subset["lead_days"].dropna()
        med = f"{leads.median():.0f}" if len(leads) > 0 else "N/A"
        mn = f"{leads.min():.0f}" if len(leads) > 0 else "N/A"
        mx = f"{leads.max():.0f}" if len(leads) > 0 else "N/A"
        label = {"bm14": "BM_14D", "bm30": "BM_30D", "ema": "EMA"}[method]
        lines.append(f"| {label} | {med} | {mn} | {mx} | {detected}/{total} |")
    lines.append("")

    # Test B — BM False Signal Rate
    lines.append("### Test B — BM False Signal Rate")
    lines.append("| Method | Total Signals | False Rate | Signals/Year |")
    lines.append("|--------|---------------|------------|--------------|")
    for method in ["bm14", "bm30", "ema"]:
        if method in bm_false_df.index:
            r = bm_false_df.loc[method]
            label = {"bm14": "BM_14D", "bm30": "BM_30D", "ema": "EMA"}[method]
            lines.append(f"| {label} | {r['total_signals']:.0f} | "
                         f"{r['false_rate_pct']:.1f}% | {r['signals_per_year']:.1f} |")
    lines.append("")

    # Test C — ETH/BTC ROC Peak Lead Time
    lines.append("### Test C — ETH/BTC ROC Peak Lead Time")
    lines.append("| Method | Median Lead (days) | Detected/Total |")
    lines.append("|--------|--------------------|----------------|")
    for method in ["roc7", "roc14", "roc7c"]:
        subset = roc_lead_df[roc_lead_df["method"] == method]
        detected = subset["warning_found"].sum()
        total = len(subset)
        leads = subset["lead_days"].dropna()
        med = f"{leads.median():.0f}" if len(leads) > 0 else "N/A"
        label = {"roc7": "ROC_7D", "roc14": "ROC_14D", "roc7c": "ROC_7D+3D"}[method]
        lines.append(f"| {label} | {med} | {detected}/{total} |")
    lines.append("")

    # Test D — ETH/BTC ROC False Alarm Rate
    lines.append("### Test D — ETH/BTC ROC False Alarm Rate")
    lines.append("| Method | Total Warnings | False Alarm | Warnings/Year |")
    lines.append("|--------|----------------|-------------|---------------|")
    for method in ["roc7", "roc14", "roc7c"]:
        if method in roc_false_df.index:
            r = roc_false_df.loc[method]
            label = {"roc7": "ROC_7D", "roc14": "ROC_14D", "roc7c": "ROC_7D+3D"}[method]
            lines.append(f"| {label} | {r['total_warnings']:.0f} | "
                         f"{r['false_alarm_pct']:.1f}% | {r['warnings_per_year']:.1f} |")
    lines.append("")

    # Test E — Best Combination
    lines.append("### Test E — Best Combination")
    method_labels = {
        "bm14": "BM_14D", "bm30": "BM_30D", "ema": "EMA",
        "roc7": "ROC_7D", "roc14": "ROC_14D", "roc7c": "ROC_7D+3D",
    }
    for i, (_, row) in enumerate(combined_df.head(3).iterrows()):
        bm_label = method_labels.get(row["bm_method"], row["bm_method"])
        roc_label = method_labels.get(row["roc_method"], row["roc_method"])
        lines.append(f"Rank {i + 1}: {bm_label} + {roc_label} — Score: {row['combined_score']:.1f}")
    lines.append("")

    # Verdict
    if len(combined_df) > 0:
        best = combined_df.iloc[0]
        bm_label = method_labels.get(best["bm_method"], best["bm_method"])
        roc_label = method_labels.get(best["roc_method"], best["roc_method"])
        lines.append("### Verdict")
        lines.append(f"**RECOMMENDED: {bm_label} + ETH/BTC {roc_label}**")
        lines.append(f"→ Update ABM_Spec_v2.md Section 2 and 3 accordingly")
        lines.append("")
        lines.append("### Score Breakdown (Top 3)")
        lines.append("| Rank | BM | ROC | BM Lead | BM False | BM Noise | ROC Lead | ROC False | ROC Noise | Score |")
        lines.append("|------|----|-----|---------|----------|----------|----------|-----------|-----------|-------|")
        for i, (_, row) in enumerate(combined_df.head(3).iterrows()):
            lines.append(
                f"| {i + 1} | {method_labels.get(row['bm_method'], row['bm_method'])} | "
                f"{method_labels.get(row['roc_method'], row['roc_method'])} | "
                f"{row['bm_lead_med']}d | {row['bm_false']}% | {row['bm_noise']}/yr | "
                f"{row['roc_lead_med']}d | {row['roc_false']}% | {row['roc_noise']}/yr | "
                f"{row['combined_score']} |"
            )

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("ABM BACKTEST — Step 5: Test Runner")
    print("=" * 60)

    # Load data
    seasons = pd.read_csv(os.path.join(OUTPUT_DIR, "seasons_ground_truth.csv"))
    seasons["start_date"] = pd.to_datetime(seasons["start_date"])
    seasons["peak_date"] = pd.to_datetime(seasons["peak_date"])
    seasons["end_date"] = pd.to_datetime(seasons["end_date"])
    print(f"Seasons: {len(seasons)}")

    bm_signals = pd.read_parquet(os.path.join(OUTPUT_DIR, "bm_signals.parquet"))
    bm_signals.index = pd.to_datetime(bm_signals.index)
    print(f"BM signals: {len(bm_signals)} days")

    ethroc_signals = pd.read_parquet(os.path.join(OUTPUT_DIR, "ethroc_signals.parquet"))
    ethroc_signals.index = pd.to_datetime(ethroc_signals.index)
    print(f"ETH/BTC ROC signals: {len(ethroc_signals)} days")

    returns_df = pd.read_parquet(os.path.join(OUTPUT_DIR, "altcoin_market_returns.parquet"))
    returns_df.index = pd.to_datetime(returns_df.index)
    alt_returns = returns_df["altcoin_mkt_return"]
    print(f"Altcoin returns: {len(alt_returns)} days")

    # ── Test A ──
    print("\n" + "-" * 40)
    print("Test A — BM Lead Time")
    bm_lead_df = test_bm_lead_time(bm_signals, seasons)
    for method in ["bm14", "bm30", "ema"]:
        subset = bm_lead_df[bm_lead_df["method"] == method]
        leads = subset["lead_days"].dropna()
        detected = subset["signal_found"].sum()
        if len(leads) > 0:
            print(f"  {method}: median={leads.median():.0f}d, "
                  f"min={leads.min():.0f}d, max={leads.max():.0f}d, "
                  f"detected={detected}/{len(subset)}")
        else:
            print(f"  {method}: no signals detected")

    # ── Test B ──
    print("\n" + "-" * 40)
    print("Test B — BM False Signal Rate")
    bm_false_df = test_bm_false_signal(bm_signals, seasons)
    for method in bm_false_df.index:
        r = bm_false_df.loc[method]
        print(f"  {method}: total={r['total_signals']:.0f}, "
              f"false={r['false_rate_pct']:.1f}%, "
              f"signals/yr={r['signals_per_year']:.1f}")

    # ── Test C ──
    print("\n" + "-" * 40)
    print("Test C — ETH/BTC ROC Peak Lead Time")
    roc_lead_df = test_ethroc_lead_time(ethroc_signals, seasons)
    for method in ["roc7", "roc14", "roc7c"]:
        subset = roc_lead_df[roc_lead_df["method"] == method]
        leads = subset["lead_days"].dropna()
        detected = subset["warning_found"].sum()
        if len(leads) > 0:
            print(f"  {method}: median={leads.median():.0f}d, "
                  f"detected={detected}/{len(subset)}")
        else:
            print(f"  {method}: no warnings detected")

    # ── Test D ──
    print("\n" + "-" * 40)
    print("Test D — ETH/BTC ROC False Alarm Rate")
    roc_false_df = test_ethroc_false_alarm(ethroc_signals, alt_returns)
    for method in roc_false_df.index:
        r = roc_false_df.loc[method]
        print(f"  {method}: total={r['total_warnings']:.0f}, "
              f"false={r['false_alarm_pct']:.1f}%, "
              f"warnings/yr={r['warnings_per_year']:.1f}")

    # ── Test E ──
    print("\n" + "-" * 40)
    print("Test E — Combined Score (3x3)")
    combined_df = test_combined_score(bm_lead_df, bm_false_df, roc_lead_df, roc_false_df)
    print(combined_df.to_string(index=False))

    # Save results
    results_path = os.path.join(OUTPUT_DIR, "backtest_results.csv")
    combined_df.to_csv(results_path, index=False)
    print(f"\nSaved: {results_path}")

    # Generate and save summary report
    summary = generate_summary(seasons, bm_lead_df, bm_false_df,
                               roc_lead_df, roc_false_df, combined_df)
    summary_path = os.path.join(OUTPUT_DIR, "test_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Saved: {summary_path}")

    # Print verdict
    if len(combined_df) > 0:
        best = combined_df.iloc[0]
        print(f"\n{'=' * 60}")
        print(f"RECOMMENDED: {best['bm_method'].upper()} + ETH/BTC {best['roc_method'].upper()}")
        print(f"Combined Score: {best['combined_score']:.1f}")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
