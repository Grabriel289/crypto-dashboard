"""
RRG Regime Filter — Smoothing & Noise Reduction Test
=====================================================
Tests multiple approaches to reduce whipsaw while preserving crash signals:

1. EMA smoothing on raw score (2mo, 3mo, 4mo)
2. Consecutive-month confirmation (require 2+ months same regime)
3. Higher thresholds (±4, ±5 instead of ±3)
4. Hybrid: EMA + higher threshold
5. Score momentum (direction of score change matters, not just level)

For each variant, measure:
  - Total regime changes (fewer = less whipsaw)
  - Avg regime duration
  - RISK-OFF precision (true crash signals vs false alarms)
  - Crash recall (how many of the 13 crashes were caught)
  - Lead time preserved
  - 1-month flash signals eliminated
"""

import pandas as pd
import numpy as np
from pathlib import Path
from copy import deepcopy

# ── Load Data ─────────────────────────────────────────────────────────

DATA_PATH = Path(__file__).parent / "output" / "rrg_fed_rotation_data.parquet"
BTC_PATH = Path(__file__).parent / "data" / "btc_coingecko.csv"
OUTPUT_DIR = Path(__file__).parent / "output"

df = pd.read_parquet(DATA_PATH)
btc_prices = pd.read_csv(BTC_PATH, parse_dates=["snapped_at"])
btc_prices["date"] = btc_prices["snapped_at"].dt.strftime("%Y-%m")
btc_monthly = btc_prices.groupby("date")["price"].last()

QUADRANT_SCORES = {"Leading": 2, "Improving": 1, "Weakening": -1, "Lagging": -2}

# ── Known crash events (ground truth) ────────────────────────────────

CRASH_EVENTS = [
    {"event": "Taper Tantrum", "month": "2013-06"},
    {"event": "Oil Crash & EM Crisis", "month": "2014-10"},
    {"event": "China Devaluation", "month": "2015-08"},
    {"event": "Volmageddon Q4", "month": "2018-10"},
    {"event": "US-China Trade War", "month": "2018-06"},
    {"event": "Trade War Aug 2019", "month": "2019-08"},
    {"event": "COVID Crash", "month": "2020-03"},
    {"event": "Luna/UST Collapse", "month": "2022-05"},
    {"event": "FTX Collapse", "month": "2022-11"},
    {"event": "SVB Banking Crisis", "month": "2023-03"},
    {"event": "Trump Tariff 2025", "month": "2025-03"},
    {"event": "Oct 2025 Mega Liq", "month": "2025-10"},
    {"event": "Russia-Ukraine", "month": "2022-02"},
]

CRYPTO_PEAKS = [
    {"event": "BTC 2013 Peak", "month": "2013-11"},
    {"event": "BTC 2017 Peak", "month": "2017-12"},
    {"event": "BTC 2021 ATH", "month": "2021-11"},
    {"event": "BTC ETF $73K", "month": "2024-03"},
]

CRYPTO_BOTTOMS = [
    {"event": "BTC 2015 Bottom", "month": "2015-01"},
    {"event": "Crypto Winter Bottom", "month": "2018-12"},
    {"event": "BTC Cycle Bottom", "month": "2022-11"},
]


# ── Build raw monthly scores ─────────────────────────────────────────

def build_raw_scores():
    months = sorted(df["date"].unique())
    scores = {}
    for m in months:
        snap = df[df["date"] == m]
        risk_score = 0
        safe_score = 0
        count = 0
        for _, row in snap.iterrows():
            qs = QUADRANT_SCORES.get(row["quadrant"], 0)
            if row["category"] == "risk":
                risk_score += qs
            elif row["category"] == "safe_haven":
                safe_score += (-qs)
            count += 1
        net = risk_score + safe_score
        max_possible = count * 2 or 1
        normalized = (net / max_possible) * 10
        scores[m] = round(normalized, 1)
    return scores


def month_offset(ym, months):
    y, m = int(ym[:4]), int(ym[5:7])
    m += months
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}"


# ══════════════════════════════════════════════════════════════════════
#  Smoothing Variants
# ══════════════════════════════════════════════════════════════════════

def apply_ema(scores_dict, span):
    """Apply EMA smoothing to score series."""
    months = sorted(scores_dict.keys())
    values = [scores_dict[m] for m in months]
    s = pd.Series(values, index=months)
    smoothed = s.ewm(span=span, adjust=False).mean()
    return dict(zip(months, smoothed.round(1).tolist()))


def apply_sma(scores_dict, window):
    """Apply simple moving average to score series."""
    months = sorted(scores_dict.keys())
    values = [scores_dict[m] for m in months]
    s = pd.Series(values, index=months)
    smoothed = s.rolling(window=window, min_periods=1).mean()
    return dict(zip(months, smoothed.round(1).tolist()))


def scores_to_regimes(scores_dict, threshold=3.0):
    """Convert scores to regimes using given threshold."""
    months = sorted(scores_dict.keys())
    regimes = {}
    for m in months:
        s = scores_dict[m]
        if s >= threshold:
            regimes[m] = "RISK-ON"
        elif s <= -threshold:
            regimes[m] = "RISK-OFF"
        else:
            regimes[m] = "NEUTRAL"
    return regimes


def apply_consecutive_confirmation(regimes_dict, required=2):
    """Only change regime if new regime holds for N consecutive months."""
    months = sorted(regimes_dict.keys())
    confirmed = {}
    current_confirmed = regimes_dict[months[0]]
    pending = None
    pending_count = 0

    for m in months:
        raw = regimes_dict[m]
        if raw == current_confirmed:
            pending = None
            pending_count = 0
            confirmed[m] = current_confirmed
        elif raw == pending:
            pending_count += 1
            if pending_count >= required:
                current_confirmed = pending
                confirmed[m] = current_confirmed
            else:
                confirmed[m] = current_confirmed
        else:
            pending = raw
            pending_count = 1
            if required == 1:
                current_confirmed = pending
                confirmed[m] = current_confirmed
            else:
                confirmed[m] = current_confirmed

    return confirmed


def apply_hysteresis(scores_dict, enter_threshold=4.0, exit_threshold=2.0):
    """
    Hysteresis: need score > enter_threshold to switch ON,
    but stays ON until score drops below exit_threshold.
    Same logic for OFF.
    """
    months = sorted(scores_dict.keys())
    regimes = {}
    current = "NEUTRAL"

    for m in months:
        s = scores_dict[m]
        if current == "NEUTRAL":
            if s >= enter_threshold:
                current = "RISK-ON"
            elif s <= -enter_threshold:
                current = "RISK-OFF"
        elif current == "RISK-ON":
            if s <= -enter_threshold:
                current = "RISK-OFF"
            elif s < exit_threshold:
                current = "NEUTRAL"
        elif current == "RISK-OFF":
            if s >= enter_threshold:
                current = "RISK-ON"
            elif s > -exit_threshold:
                current = "NEUTRAL"
        regimes[m] = current

    return regimes


def apply_score_momentum(scores_dict, threshold=3.0, momentum_weight=0.5):
    """
    Blend raw score with its 2-month momentum (direction of change).
    Composite = score + momentum_weight * (score - score_2mo_ago)
    """
    months = sorted(scores_dict.keys())
    composite = {}
    for i, m in enumerate(months):
        s = scores_dict[m]
        if i >= 2:
            m_prev2 = months[i - 2]
            mom = scores_dict[m] - scores_dict[m_prev2]
            comp = s + momentum_weight * mom
        else:
            comp = s
        composite[m] = round(comp, 1)
    return scores_to_regimes(composite, threshold)


# ══════════════════════════════════════════════════════════════════════
#  Evaluation
# ══════════════════════════════════════════════════════════════════════

def evaluate_variant(name, regimes_dict, scores_dict):
    """Evaluate a regime variant against known events."""
    months = sorted(regimes_dict.keys())

    # Basic stats
    changes = sum(1 for i in range(1, len(months))
                  if regimes_dict[months[i]] != regimes_dict[months[i-1]])
    whipsaws = sum(1 for i in range(2, len(months))
                   if regimes_dict[months[i]] == regimes_dict[months[i-2]]
                   and regimes_dict[months[i]] != regimes_dict[months[i-1]])

    # Regime durations
    runs = []
    current = regimes_dict[months[0]]
    run_len = 1
    for i in range(1, len(months)):
        if regimes_dict[months[i]] == current:
            run_len += 1
        else:
            runs.append((current, run_len))
            current = regimes_dict[months[i]]
            run_len = 1
    runs.append((current, run_len))

    regime_stats = {}
    for regime in ["RISK-ON", "RISK-OFF", "NEUTRAL"]:
        r_runs = [r[1] for r in runs if r[0] == regime]
        if r_runs:
            regime_stats[regime] = {
                "count": len(r_runs),
                "avg": np.mean(r_runs),
                "median": np.median(r_runs),
                "max": max(r_runs),
                "flashes": sum(1 for r in r_runs if r == 1),
            }
        else:
            regime_stats[regime] = {"count": 0, "avg": 0, "median": 0, "max": 0, "flashes": 0}

    # RISK-OFF precision (how many RISK-OFF starts led to actual crash within 3mo)
    riskoff_starts = []
    for i, m in enumerate(months):
        if regimes_dict[m] == "RISK-OFF":
            if i == 0 or regimes_dict[months[i-1]] != "RISK-OFF":
                riskoff_starts.append(m)

    crash_months_set = {c["month"] for c in CRASH_EVENTS}
    true_pos = 0
    false_pos = 0
    true_pos_events = []
    false_pos_months = []

    for start_m in riskoff_starts:
        hit = False
        for ce in CRASH_EVENTS:
            cm = ce["month"]
            sy, sm = int(start_m[:4]), int(start_m[5:7])
            cy, cmo = int(cm[:4]), int(cm[5:7])
            diff = (cy - sy) * 12 + (cmo - sm)
            if 0 <= diff <= 3:
                hit = True
                true_pos_events.append(ce["event"])
                break
        if hit:
            true_pos += 1
        else:
            false_pos += 1
            false_pos_months.append(start_m)

    precision = true_pos / (true_pos + false_pos) * 100 if (true_pos + false_pos) > 0 else 0

    # Crash recall (how many crashes had RISK-OFF signal in 3mo before)
    crashes_caught = 0
    crashes_missed = []
    crash_details = []
    for ce in CRASH_EVENTS:
        cm = ce["month"]
        caught = False
        lead = 0
        for offset in [3, 2, 1, 0]:
            check_m = month_offset(cm, -offset)
            if check_m in regimes_dict and regimes_dict[check_m] == "RISK-OFF":
                caught = True
                lead = offset
                break
        if caught:
            crashes_caught += 1
            crash_details.append((ce["event"], cm, lead, "HIT"))
        else:
            crashes_missed.append(ce["event"])
            # Check what regime was
            scores_before = []
            for offset in [3, 2, 1, 0]:
                check_m = month_offset(cm, -offset)
                if check_m in regimes_dict:
                    scores_before.append(f"{regimes_dict[check_m]}({scores_dict.get(check_m, '?')})")
            crash_details.append((ce["event"], cm, 0, f"MISS [{', '.join(scores_before)}]"))

    recall = crashes_caught / len(CRASH_EVENTS) * 100

    # Neutral %
    neutral_pct = sum(1 for m in months if regimes_dict[m] == "NEUTRAL") / len(months) * 100

    return {
        "name": name,
        "total_months": len(months),
        "changes": changes,
        "whipsaws": whipsaws,
        "regime_stats": regime_stats,
        "riskoff_signals": len(riskoff_starts),
        "true_pos": true_pos,
        "false_pos": false_pos,
        "precision": precision,
        "crashes_caught": crashes_caught,
        "total_crashes": len(CRASH_EVENTS),
        "recall": recall,
        "crash_details": crash_details,
        "false_pos_months": false_pos_months,
        "neutral_pct": neutral_pct,
    }


# ══════════════════════════════════════════════════════════════════════
#  Report
# ══════════════════════════════════════════════════════════════════════

def generate_report(results):
    lines = []
    lines.append("# RRG Regime Filter -- Smoothing & Noise Reduction Test")
    lines.append("")
    lines.append("## Problem Statement")
    lines.append("")
    lines.append("The raw RRG regime score at +/-3 threshold produces:")
    lines.append("- 85 regime changes in 166 months (flip every 2 months)")
    lines.append("- 86-87% of RISK-ON/OFF signals are 1-month flashes")
    lines.append("- 57% of RISK-OFF signals are false alarms")
    lines.append("- Score flips sign 53% of months")
    lines.append("")
    lines.append("**Goal:** Find a filter that reduces false signals while preserving")
    lines.append("crash detection with adequate lead time.")
    lines.append("")

    # ── Comparison Table ──
    lines.append("---")
    lines.append("## Head-to-Head Comparison")
    lines.append("")
    lines.append("| Variant | Changes | Whipsaws | RISK-OFF Signals | Precision | Crash Recall | Neutral% | Avg RISK-OFF Duration |")
    lines.append("|---------|---------|----------|------------------|-----------|--------------|----------|----------------------|")

    for r in results:
        rs = r["regime_stats"].get("RISK-OFF", {})
        avg_dur = f"{rs.get('avg', 0):.1f}mo"
        lines.append(
            f"| {r['name']} | {r['changes']} | {r['whipsaws']} | "
            f"{r['riskoff_signals']} | {r['precision']:.0f}% | "
            f"{r['crashes_caught']}/{r['total_crashes']} ({r['recall']:.0f}%) | "
            f"{r['neutral_pct']:.0f}% | {avg_dur} |"
        )
    lines.append("")

    # ── Detailed per-variant ──
    lines.append("---")
    lines.append("## Detailed Results")
    lines.append("")

    for r in results:
        lines.append(f"### {r['name']}")
        lines.append("")

        # Regime duration stats
        lines.append("**Regime Duration:**")
        lines.append("| Regime | Count | Avg Duration | 1-mo Flashes |")
        lines.append("|--------|-------|-------------|--------------|")
        for regime in ["RISK-ON", "RISK-OFF", "NEUTRAL"]:
            rs = r["regime_stats"].get(regime, {})
            if rs["count"] > 0:
                flash_pct = rs["flashes"] / rs["count"] * 100
                lines.append(f"| {regime} | {rs['count']} | {rs['avg']:.1f}mo | {rs['flashes']} ({flash_pct:.0f}%) |")
            else:
                lines.append(f"| {regime} | 0 | -- | -- |")
        lines.append("")

        # Crash detection detail
        lines.append("**Crash Detection:**")
        lines.append("| Event | Month | Lead | Result |")
        lines.append("|-------|-------|------|--------|")
        for event_name, month, lead, result in r["crash_details"]:
            lead_str = f"{lead}mo" if "HIT" in result else "--"
            lines.append(f"| {event_name} | {month} | {lead_str} | {result} |")
        lines.append("")

        # False alarms
        if r["false_pos_months"]:
            lines.append(f"**False RISK-OFF signals ({r['false_pos']}):** {', '.join(r['false_pos_months'])}")
        else:
            lines.append("**False RISK-OFF signals: 0**")
        lines.append("")

    # ── Winner Analysis ──
    lines.append("---")
    lines.append("## Finding the Best Filter")
    lines.append("")

    # Score each variant on combined metric
    lines.append("### Composite Score (weighted)")
    lines.append("")
    lines.append("Weights: Precision 30% + Recall 30% + Low Whipsaw 20% + Lead Time 20%")
    lines.append("")
    lines.append("| Variant | Precision | Recall | Whipsaw Reduction | Score |")
    lines.append("|---------|-----------|--------|-------------------|-------|")

    baseline_whipsaws = results[0]["whipsaws"] if results else 1
    best_score = -1
    best_name = ""

    for r in results:
        whipsaw_reduction = (1 - r["whipsaws"] / max(baseline_whipsaws, 1)) * 100
        # Avg lead time from crash details
        leads = [lead for _, _, lead, result in r["crash_details"] if "HIT" in result and lead > 0]
        avg_lead = np.mean(leads) if leads else 0
        lead_score = min(avg_lead / 3 * 100, 100)  # 3mo = perfect

        composite = (r["precision"] * 0.30 + r["recall"] * 0.30 +
                    whipsaw_reduction * 0.20 + lead_score * 0.20)

        if composite > best_score:
            best_score = composite
            best_name = r["name"]

        lines.append(f"| {r['name']} | {r['precision']:.0f}% | {r['recall']:.0f}% | "
                     f"{whipsaw_reduction:.0f}% | **{composite:.1f}** |")

    lines.append("")
    lines.append(f"### Winner: **{best_name}** (score: {best_score:.1f})")
    lines.append("")

    # ── Recommendation ──
    lines.append("---")
    lines.append("## Recommendation for Production")
    lines.append("")
    lines.append("Based on the analysis, the optimal approach depends on use case:")
    lines.append("")
    lines.append("### For Crash Avoidance (conservative):")
    lines.append("- Prioritize **recall** (catch all crashes) over precision")
    lines.append("- Accept some false alarms to never miss a real crash")
    lines.append("- Best: variant with highest recall + reasonable precision")
    lines.append("")
    lines.append("### For Active Trading (balanced):")
    lines.append("- Need both precision AND recall")
    lines.append("- Can't afford false signals (each one costs a trade)")
    lines.append("- Best: variant with highest composite score")
    lines.append("")
    lines.append("### For Trend Confirmation (aggressive):")
    lines.append("- Prioritize **precision** (only act on high-confidence signals)")
    lines.append("- OK to miss some crashes if the signals you do get are reliable")
    lines.append("- Best: variant with highest precision")
    lines.append("")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("RRG SMOOTHING & NOISE REDUCTION TEST")
    print("=" * 70)

    raw_scores = build_raw_scores()
    results = []

    # ── Variant 0: Baseline (raw, threshold +/-3) ──
    print("\n[0] Baseline: Raw score, threshold +/-3")
    regimes_0 = scores_to_regimes(raw_scores, 3.0)
    results.append(evaluate_variant("0. Baseline (raw +/-3)", regimes_0, raw_scores))

    # ── Variant 1: EMA(2) + threshold +/-3 ──
    print("[1] EMA(2) smoothing, threshold +/-3")
    ema2 = apply_ema(raw_scores, span=2)
    regimes_1 = scores_to_regimes(ema2, 3.0)
    results.append(evaluate_variant("1. EMA(2) +/-3", regimes_1, ema2))

    # ── Variant 2: EMA(3) + threshold +/-3 ──
    print("[2] EMA(3) smoothing, threshold +/-3")
    ema3 = apply_ema(raw_scores, span=3)
    regimes_2 = scores_to_regimes(ema3, 3.0)
    results.append(evaluate_variant("2. EMA(3) +/-3", regimes_2, ema3))

    # ── Variant 3: SMA(3) + threshold +/-3 ──
    print("[3] SMA(3) smoothing, threshold +/-3")
    sma3 = apply_sma(raw_scores, window=3)
    regimes_3 = scores_to_regimes(sma3, 3.0)
    results.append(evaluate_variant("3. SMA(3) +/-3", regimes_3, sma3))

    # ── Variant 4: Raw + higher threshold +/-5 ──
    print("[4] Raw score, higher threshold +/-5")
    regimes_4 = scores_to_regimes(raw_scores, 5.0)
    results.append(evaluate_variant("4. Raw +/-5", regimes_4, raw_scores))

    # ── Variant 5: EMA(3) + higher threshold +/-4 ──
    print("[5] EMA(3) + threshold +/-4")
    regimes_5 = scores_to_regimes(ema3, 4.0)
    results.append(evaluate_variant("5. EMA(3) +/-4", regimes_5, ema3))

    # ── Variant 6: 2-month confirmation on raw ──
    print("[6] Raw +/-3 with 2-month confirmation")
    regimes_raw3 = scores_to_regimes(raw_scores, 3.0)
    regimes_6 = apply_consecutive_confirmation(regimes_raw3, required=2)
    results.append(evaluate_variant("6. Raw +/-3, 2mo confirm", regimes_6, raw_scores))

    # ── Variant 7: Hysteresis (enter +/-4, exit +/-2) ──
    print("[7] Hysteresis: enter +/-4, stay until +/-2")
    regimes_7 = apply_hysteresis(raw_scores, enter_threshold=4.0, exit_threshold=2.0)
    results.append(evaluate_variant("7. Hysteresis (4/2)", regimes_7, raw_scores))

    # ── Variant 8: Hysteresis (enter +/-5, exit +/-2) ──
    print("[8] Hysteresis: enter +/-5, stay until +/-2")
    regimes_8 = apply_hysteresis(raw_scores, enter_threshold=5.0, exit_threshold=2.0)
    results.append(evaluate_variant("8. Hysteresis (5/2)", regimes_8, raw_scores))

    # ── Variant 9: EMA(3) + Hysteresis (4/2) ──
    print("[9] EMA(3) + Hysteresis (enter 4, exit 2)")
    regimes_9 = apply_hysteresis(ema3, enter_threshold=4.0, exit_threshold=2.0)
    results.append(evaluate_variant("9. EMA(3) + Hysteresis(4/2)", regimes_9, ema3))

    # ── Variant 10: EMA(2) + Hysteresis (3.5/1.5) ──
    print("[10] EMA(2) + Hysteresis (enter 3.5, exit 1.5)")
    regimes_10 = apply_hysteresis(ema2, enter_threshold=3.5, exit_threshold=1.5)
    results.append(evaluate_variant("10. EMA(2) + Hysteresis(3.5/1.5)", regimes_10, ema2))

    # ── Variant 11: Score momentum composite ──
    print("[11] Score + momentum composite, threshold +/-3")
    regimes_11 = apply_score_momentum(raw_scores, threshold=3.0, momentum_weight=0.5)
    results.append(evaluate_variant("11. Score+Momentum +/-3", regimes_11, raw_scores))

    # ── Variant 12: SMA(2) + Hysteresis (3.5/1.5) ──
    print("[12] SMA(2) + Hysteresis (3.5/1.5)")
    sma2 = apply_sma(raw_scores, window=2)
    regimes_12 = apply_hysteresis(sma2, enter_threshold=3.5, exit_threshold=1.5)
    results.append(evaluate_variant("12. SMA(2) + Hysteresis(3.5/1.5)", regimes_12, sma2))

    # ── Variant 13: EMA(3) + Hysteresis (3.5/1.0) ──
    print("[13] EMA(3) + Hysteresis (3.5/1.0)")
    regimes_13 = apply_hysteresis(ema3, enter_threshold=3.5, exit_threshold=1.0)
    results.append(evaluate_variant("13. EMA(3) + Hysteresis(3.5/1.0)", regimes_13, ema3))

    # Print summary
    print("\n" + "=" * 70)
    print(f"{'Variant':<38} {'Chg':>4} {'Whip':>5} {'R-OFF':>6} {'Prec':>6} {'Recall':>8} {'Neut%':>6}")
    print("-" * 70)
    for r in results:
        print(f"{r['name']:<38} {r['changes']:>4} {r['whipsaws']:>5} "
              f"{r['riskoff_signals']:>6} {r['precision']:>5.0f}% "
              f"{r['crashes_caught']}/{r['total_crashes']} ({r['recall']:>3.0f}%) "
              f"{r['neutral_pct']:>5.0f}%")

    # Generate report
    report = generate_report(results)
    output_path = OUTPUT_DIR / "rrg_smoothing_test.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
