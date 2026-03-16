"""
RRG Composite Regime Filter — Multi-Factor Approach
====================================================
Single-score smoothing fails because:
  - Aggressive smoothing kills lead time (recall drops to 8-23%)
  - Light smoothing keeps the noise (85 changes, 57% false alarms)

Solution: Combine MULTIPLE weak signals into one strong filter.

Factors:
  1. Score Level: raw score (no smoothing — preserve speed)
  2. Score Trend: 2-month direction (rising/falling)
  3. Safe-Haven Rotation: count of GLD/TLT/UUP in Leading/Improving
  4. BTC Quadrant: Lagging = bearish, Leading = bullish
  5. Risk Breadth: % of risk assets in Leading/Improving

Each factor contributes to a composite score. Only trigger regime change
when MULTIPLE factors agree (conviction-based, not threshold-based).
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path(__file__).parent / "output" / "rrg_fed_rotation_data.parquet"
BTC_PATH = Path(__file__).parent / "data" / "btc_coingecko.csv"
OUTPUT_DIR = Path(__file__).parent / "output"

df = pd.read_parquet(DATA_PATH)
btc_prices = pd.read_csv(BTC_PATH, parse_dates=["snapped_at"])
btc_prices["date"] = btc_prices["snapped_at"].dt.strftime("%Y-%m")
btc_monthly = btc_prices.groupby("date")["price"].last()

QUADRANT_SCORES = {"Leading": 2, "Improving": 1, "Weakening": -1, "Lagging": -2}
SAFE_HAVENS = ["GLD", "TLT", "UUP"]
RISK_ASSETS = ["BTC", "IBIT", "ETHA", "QQQ", "IWM", "SMH", "BOTZ", "XLF",
               "XLE", "EEM", "EWJ", "FXI", "HYG", "DBC", "COPX"]

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

ALL_EVENTS = [
    # Crashes
    {"event": "Taper Tantrum", "month": "2013-06", "type": "CRASH"},
    {"event": "Oil Crash & EM Crisis", "month": "2014-10", "type": "CRASH"},
    {"event": "China Devaluation", "month": "2015-08", "type": "CRASH"},
    {"event": "Volmageddon Q4", "month": "2018-10", "type": "CRASH"},
    {"event": "US-China Trade War", "month": "2018-06", "type": "CRASH"},
    {"event": "Trade War Aug 2019", "month": "2019-08", "type": "CRASH"},
    {"event": "COVID Crash", "month": "2020-03", "type": "CRASH"},
    {"event": "Luna/UST Collapse", "month": "2022-05", "type": "CRASH"},
    {"event": "FTX Collapse", "month": "2022-11", "type": "CRASH"},
    {"event": "SVB Banking Crisis", "month": "2023-03", "type": "CRASH"},
    {"event": "Trump Tariff 2025", "month": "2025-03", "type": "CRASH"},
    {"event": "Oct 2025 Mega Liq", "month": "2025-10", "type": "CRASH"},
    {"event": "Russia-Ukraine", "month": "2022-02", "type": "CRASH"},
    # Crypto peaks
    {"event": "BTC 2013 Peak", "month": "2013-11", "type": "PEAK"},
    {"event": "BTC 2017 Peak", "month": "2017-12", "type": "PEAK"},
    {"event": "BTC 2021 ATH", "month": "2021-11", "type": "PEAK"},
    {"event": "BTC ETF $73K", "month": "2024-03", "type": "PEAK"},
    # Bottoms
    {"event": "BTC 2015 Bottom", "month": "2015-01", "type": "BOTTOM"},
    {"event": "Crypto Winter Bottom", "month": "2018-12", "type": "BOTTOM"},
    {"event": "BTC Cycle Bottom", "month": "2022-11", "type": "BOTTOM"},
    # Bullish
    {"event": "Post-COVID Rally", "month": "2020-06", "type": "BULLISH"},
    {"event": "Powell Pivot", "month": "2019-01", "type": "BULLISH"},
    {"event": "QE3 Launch", "month": "2012-09", "type": "BULLISH"},
    {"event": "First Rate Cut", "month": "2024-09", "type": "BULLISH"},
]


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
#  Factor Extraction
# ══════════════════════════════════════════════════════════════════════

def extract_monthly_factors():
    """Extract all factors for each month."""
    months = sorted(df["date"].unique())
    records = []

    for m in months:
        snap = df[df["date"] == m]
        if snap.empty:
            continue

        # Factor 1: Raw regime score
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
        raw_score = round((net / max_possible) * 10, 1)

        # Factor 3: Safe-haven rotation (GLD, TLT, UUP in Leading/Improving)
        sh_bullish = 0
        for sym in SAFE_HAVENS:
            row = snap[snap["symbol"] == sym]
            if not row.empty and row.iloc[0]["quadrant"] in ("Leading", "Improving"):
                sh_bullish += 1

        # Factor 4: BTC quadrant
        btc_row = snap[snap["symbol"] == "BTC"]
        btc_quad = btc_row.iloc[0]["quadrant"] if not btc_row.empty else None

        # Factor 5: Risk breadth (% of risk assets in Leading/Improving)
        risk_total = 0
        risk_bullish = 0
        for _, row in snap[snap["category"] == "risk"].iterrows():
            risk_total += 1
            if row["quadrant"] in ("Leading", "Improving"):
                risk_bullish += 1
        risk_breadth = risk_bullish / risk_total * 100 if risk_total > 0 else 50

        records.append({
            "month": m,
            "raw_score": raw_score,
            "sh_bullish": sh_bullish,  # 0-3 (GLD, TLT, UUP)
            "btc_quad": btc_quad,
            "risk_breadth": round(risk_breadth, 1),
        })

    factors = pd.DataFrame(records).set_index("month")

    # Factor 2: Score trend (2-month change)
    factors["score_trend"] = factors["raw_score"].diff(2)
    # Also 1-month change
    factors["score_mom1"] = factors["raw_score"].diff(1)

    return factors


# ══════════════════════════════════════════════════════════════════════
#  Composite Filter Variants
# ══════════════════════════════════════════════════════════════════════

def filter_v1_conviction(factors):
    """
    V1: Conviction-based — count how many factors agree on direction.
    RISK-OFF when 3+ of 5 factors bearish. RISK-ON when 3+ bullish.
    """
    regimes = {}
    for m, row in factors.iterrows():
        bearish = 0
        bullish = 0

        # Score level
        if row["raw_score"] <= -2:
            bearish += 1
        elif row["raw_score"] >= 2:
            bullish += 1

        # Score trend
        if pd.notna(row["score_trend"]):
            if row["score_trend"] <= -3:
                bearish += 1
            elif row["score_trend"] >= 3:
                bullish += 1

        # Safe haven (3/3 bullish = very bearish for risk)
        if row["sh_bullish"] >= 3:
            bearish += 1
        elif row["sh_bullish"] == 0:
            bullish += 1

        # BTC quadrant
        if row["btc_quad"] == "Lagging":
            bearish += 1
        elif row["btc_quad"] == "Leading":
            bullish += 1

        # Risk breadth
        if row["risk_breadth"] <= 30:
            bearish += 1
        elif row["risk_breadth"] >= 60:
            bullish += 1

        if bearish >= 3:
            regimes[m] = "RISK-OFF"
        elif bullish >= 3:
            regimes[m] = "RISK-ON"
        else:
            regimes[m] = "NEUTRAL"

    return regimes


def filter_v2_conviction_strict(factors):
    """
    V2: Stricter conviction — need 4+ factors for signal.
    """
    regimes = {}
    for m, row in factors.iterrows():
        bearish = 0
        bullish = 0

        if row["raw_score"] <= -2:
            bearish += 1
        elif row["raw_score"] >= 2:
            bullish += 1

        if pd.notna(row["score_trend"]):
            if row["score_trend"] <= -3:
                bearish += 1
            elif row["score_trend"] >= 3:
                bullish += 1

        if row["sh_bullish"] >= 3:
            bearish += 1
        elif row["sh_bullish"] == 0:
            bullish += 1

        if row["btc_quad"] == "Lagging":
            bearish += 1
        elif row["btc_quad"] == "Leading":
            bullish += 1

        if row["risk_breadth"] <= 30:
            bearish += 1
        elif row["risk_breadth"] >= 60:
            bullish += 1

        if bearish >= 4:
            regimes[m] = "RISK-OFF"
        elif bullish >= 4:
            regimes[m] = "RISK-ON"
        else:
            regimes[m] = "NEUTRAL"

    return regimes


def filter_v3_weighted(factors):
    """
    V3: Weighted composite score.
    Each factor maps to a -2 to +2 score. Sum them up.
    Threshold: >= +4 RISK-ON, <= -4 RISK-OFF.
    """
    regimes = {}
    composite_scores = {}

    for m, row in factors.iterrows():
        comp = 0.0

        # Score level (weight: 2x) — most important single factor
        if row["raw_score"] <= -5:
            comp -= 2.0
        elif row["raw_score"] <= -2:
            comp -= 1.0
        elif row["raw_score"] >= 5:
            comp += 2.0
        elif row["raw_score"] >= 2:
            comp += 1.0

        # Score trend (weight: 1.5x)
        if pd.notna(row["score_trend"]):
            if row["score_trend"] <= -4:
                comp -= 1.5
            elif row["score_trend"] <= -2:
                comp -= 0.75
            elif row["score_trend"] >= 4:
                comp += 1.5
            elif row["score_trend"] >= 2:
                comp += 0.75

        # Safe haven rotation (weight: 2x) — strongest crash predictor
        if row["sh_bullish"] >= 3:
            comp -= 2.0
        elif row["sh_bullish"] == 2:
            comp -= 1.0
        elif row["sh_bullish"] == 0:
            comp += 1.5

        # BTC quadrant (weight: 1x)
        if row["btc_quad"] == "Lagging":
            comp -= 1.0
        elif row["btc_quad"] == "Leading":
            comp += 1.0
        elif row["btc_quad"] == "Weakening":
            comp -= 0.5
        elif row["btc_quad"] == "Improving":
            comp += 0.5

        # Risk breadth (weight: 1.5x)
        if row["risk_breadth"] <= 20:
            comp -= 1.5
        elif row["risk_breadth"] <= 35:
            comp -= 0.75
        elif row["risk_breadth"] >= 65:
            comp += 1.5
        elif row["risk_breadth"] >= 50:
            comp += 0.75

        composite_scores[m] = round(comp, 2)

        if comp <= -4.0:
            regimes[m] = "RISK-OFF"
        elif comp >= 4.0:
            regimes[m] = "RISK-ON"
        else:
            regimes[m] = "NEUTRAL"

    return regimes, composite_scores


def filter_v4_weighted_hysteresis(factors):
    """
    V4: Weighted composite + hysteresis.
    Enter at +/-4, exit at +/-1.5. This is the premium version.
    """
    _, composite_scores = filter_v3_weighted(factors)
    months = sorted(composite_scores.keys())

    regimes = {}
    current = "NEUTRAL"

    for m in months:
        s = composite_scores[m]
        if current == "NEUTRAL":
            if s >= 4.0:
                current = "RISK-ON"
            elif s <= -4.0:
                current = "RISK-OFF"
        elif current == "RISK-ON":
            if s <= -4.0:
                current = "RISK-OFF"
            elif s < 1.5:
                current = "NEUTRAL"
        elif current == "RISK-OFF":
            if s >= 4.0:
                current = "RISK-ON"
            elif s > -1.5:
                current = "NEUTRAL"
        regimes[m] = current

    return regimes, composite_scores


def filter_v5_weighted_loose(factors):
    """
    V5: Weighted composite with lower thresholds (+/-3).
    More signals but more noise — tests if lower threshold works with composite.
    """
    _, composite_scores = filter_v3_weighted(factors)
    regimes = {}
    for m, s in composite_scores.items():
        if s <= -3.0:
            regimes[m] = "RISK-OFF"
        elif s >= 3.0:
            regimes[m] = "RISK-ON"
        else:
            regimes[m] = "NEUTRAL"
    return regimes, composite_scores


def filter_v6_weighted_hyst_loose(factors):
    """
    V6: Weighted composite + hysteresis with lower enter (+/-3.5), exit (+/-1.0)
    """
    _, composite_scores = filter_v3_weighted(factors)
    months = sorted(composite_scores.keys())

    regimes = {}
    current = "NEUTRAL"

    for m in months:
        s = composite_scores[m]
        if current == "NEUTRAL":
            if s >= 3.5:
                current = "RISK-ON"
            elif s <= -3.5:
                current = "RISK-OFF"
        elif current == "RISK-ON":
            if s <= -3.5:
                current = "RISK-OFF"
            elif s < 1.0:
                current = "NEUTRAL"
        elif current == "RISK-OFF":
            if s >= 3.5:
                current = "RISK-ON"
            elif s > -1.0:
                current = "NEUTRAL"
        regimes[m] = current

    return regimes, composite_scores


# ══════════════════════════════════════════════════════════════════════
#  Evaluation
# ══════════════════════════════════════════════════════════════════════

def evaluate(name, regimes, scores_dict=None):
    months = sorted(regimes.keys())

    # Basic stats
    changes = sum(1 for i in range(1, len(months))
                  if regimes[months[i]] != regimes[months[i-1]])
    whipsaws = sum(1 for i in range(2, len(months))
                   if regimes[months[i]] == regimes[months[i-2]]
                   and regimes[months[i]] != regimes[months[i-1]])

    # Regime runs
    runs = []
    current = regimes[months[0]]
    run_len = 1
    for i in range(1, len(months)):
        if regimes[months[i]] == current:
            run_len += 1
        else:
            runs.append((current, run_len))
            current = regimes[months[i]]
            run_len = 1
    runs.append((current, run_len))

    regime_stats = {}
    for regime in ["RISK-ON", "RISK-OFF", "NEUTRAL"]:
        r_runs = [r[1] for r in runs if r[0] == regime]
        if r_runs:
            regime_stats[regime] = {
                "count": len(r_runs),
                "avg": round(np.mean(r_runs), 1),
                "median": np.median(r_runs),
                "max": max(r_runs),
                "flashes": sum(1 for r in r_runs if r == 1),
            }
        else:
            regime_stats[regime] = {"count": 0, "avg": 0, "median": 0, "max": 0, "flashes": 0}

    # RISK-OFF precision
    riskoff_starts = []
    for i, m in enumerate(months):
        if regimes[m] == "RISK-OFF":
            if i == 0 or regimes[months[i-1]] != "RISK-OFF":
                riskoff_starts.append(m)

    true_pos = 0
    false_pos = 0
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
                break
        if hit:
            true_pos += 1
        else:
            false_pos += 1
            false_pos_months.append(start_m)

    precision = true_pos / (true_pos + false_pos) * 100 if (true_pos + false_pos) > 0 else 0

    # Crash recall
    crash_details = []
    crashes_caught = 0
    for ce in CRASH_EVENTS:
        cm = ce["month"]
        caught = False
        lead = 0
        for offset in [3, 2, 1, 0]:
            check_m = month_offset(cm, -offset)
            if check_m in regimes and regimes[check_m] == "RISK-OFF":
                caught = True
                lead = offset
                break
        if caught:
            crashes_caught += 1
        crash_details.append({
            "event": ce["event"],
            "month": cm,
            "caught": caught,
            "lead": lead if caught else 0,
        })

    recall = crashes_caught / len(CRASH_EVENTS) * 100

    # Neutral %
    neutral_pct = sum(1 for m in months if regimes[m] == "NEUTRAL") / len(months) * 100

    # All events assessment
    event_results = []
    for ev in ALL_EVENTS:
        em = ev["month"]
        regime_at = regimes.get(em, "N/A")
        regime_before_1 = regimes.get(month_offset(em, -1), "N/A")
        regime_before_2 = regimes.get(month_offset(em, -2), "N/A")
        regime_after_1 = regimes.get(month_offset(em, 1), "N/A")
        score_at = scores_dict.get(em, None) if scores_dict else None

        if ev["type"] == "CRASH":
            hit = any(regimes.get(month_offset(em, -o), "") == "RISK-OFF" for o in range(4))
            lead = max((o for o in range(4) if regimes.get(month_offset(em, -o), "") == "RISK-OFF"), default=0)
        elif ev["type"] == "PEAK":
            # Check if score was deteriorating or RISK-OFF
            hit = (regime_before_1 in ("RISK-OFF", "NEUTRAL") and
                   regime_at in ("RISK-OFF", "NEUTRAL"))
            lead = 1 if regime_before_1 in ("RISK-OFF",) else 0
        elif ev["type"] == "BOTTOM":
            hit = regime_at == "RISK-OFF" or regime_before_1 == "RISK-OFF"
            lead = 0
        elif ev["type"] == "BULLISH":
            hit = regime_at == "RISK-ON" or regime_after_1 == "RISK-ON"
            lead = 0
        else:
            hit = False
            lead = 0

        event_results.append({
            **ev,
            "hit": hit,
            "lead": lead,
            "regime_at": regime_at,
            "regime_before": regime_before_1,
            "score_at": score_at,
        })

    return {
        "name": name,
        "changes": changes,
        "whipsaws": whipsaws,
        "regime_stats": regime_stats,
        "riskoff_signals": len(riskoff_starts),
        "true_pos": true_pos,
        "false_pos": false_pos,
        "false_pos_months": false_pos_months,
        "precision": precision,
        "crashes_caught": crashes_caught,
        "total_crashes": len(CRASH_EVENTS),
        "recall": recall,
        "crash_details": crash_details,
        "neutral_pct": neutral_pct,
        "event_results": event_results,
    }


# ══════════════════════════════════════════════════════════════════════
#  Report
# ══════════════════════════════════════════════════════════════════════

def generate_report(factors, all_results, best_regimes, best_composites):
    lines = []
    lines.append("# RRG Composite Regime Filter -- Multi-Factor Noise Reduction")
    lines.append("")
    lines.append("## Approach")
    lines.append("")
    lines.append("Single-score smoothing (EMA, SMA, thresholds) fails the precision-recall tradeoff:")
    lines.append("- Aggressive smoothing kills recall (8-23% crash detection)")
    lines.append("- Light smoothing keeps noise (85 changes, 57% false alarms)")
    lines.append("")
    lines.append("**Multi-factor composite** combines 5 independent signals:")
    lines.append("1. **Score Level** (raw, no smoothing) -- preserves speed")
    lines.append("2. **Score Trend** (2-month direction) -- catches deterioration")
    lines.append("3. **Safe-Haven Rotation** (GLD+TLT+UUP positions) -- strongest crash predictor")
    lines.append("4. **BTC Quadrant** (Leading/Lagging) -- crypto-specific signal")
    lines.append("5. **Risk Breadth** (% risk assets bullish) -- broad confirmation")
    lines.append("")

    # ── Comparison Table ──
    lines.append("---")
    lines.append("## Head-to-Head: All Variants")
    lines.append("")
    lines.append("| Variant | Changes | Whipsaws | R-OFF Signals | Precision | Recall | Neutral% | Avg R-OFF Dur |")
    lines.append("|---------|---------|----------|---------------|-----------|--------|----------|---------------|")

    for r in all_results:
        rs = r["regime_stats"].get("RISK-OFF", {})
        avg_dur = f"{rs.get('avg', 0):.1f}mo"
        flashes = rs.get("flashes", 0)
        total = rs.get("count", 0)
        flash_str = f" ({flashes}/{total} flash)" if total > 0 else ""
        lines.append(
            f"| {r['name']} | {r['changes']} | {r['whipsaws']} | "
            f"{r['riskoff_signals']} | **{r['precision']:.0f}%** | "
            f"**{r['crashes_caught']}/{r['total_crashes']} ({r['recall']:.0f}%)** | "
            f"{r['neutral_pct']:.0f}% | {avg_dur}{flash_str} |"
        )
    lines.append("")

    # ── Crash-by-Crash Comparison ──
    lines.append("---")
    lines.append("## Crash Detection: Event-by-Event Comparison")
    lines.append("")
    header = "| Event | Month |"
    for r in all_results:
        short_name = r["name"].split(". ")[1] if ". " in r["name"] else r["name"]
        header += f" {short_name} |"
    lines.append(header)
    sep = "|-------|-------|" + "|".join(["---"] * len(all_results)) + "|"
    lines.append(sep)

    for i, ce in enumerate(CRASH_EVENTS):
        row = f"| {ce['event']} | {ce['month']} |"
        for r in all_results:
            cd = r["crash_details"][i]
            if cd["caught"]:
                row += f" HIT {cd['lead']}mo |"
            else:
                row += " MISS |"
        lines.append(row)

    lines.append("")

    # ── Best Variant Full Event Assessment ──
    best = [r for r in all_results if "V6" in r["name"]]
    if not best:
        best = [all_results[-1]]
    best = best[0]

    lines.append("---")
    lines.append(f"## Best Variant Deep Dive: {best['name']}")
    lines.append("")

    lines.append(f"**Regime changes:** {best['changes']} (vs 85 baseline)")
    lines.append(f"**Whipsaws:** {best['whipsaws']} (vs 32 baseline)")
    lines.append(f"**RISK-OFF precision:** {best['precision']:.0f}% (vs 43% baseline)")
    lines.append(f"**Crash recall:** {best['crashes_caught']}/{best['total_crashes']} ({best['recall']:.0f}%)")
    lines.append("")

    # Regime duration
    lines.append("### Regime Duration:")
    lines.append("| Regime | Count | Avg Duration | Max | 1-mo Flashes |")
    lines.append("|--------|-------|-------------|-----|--------------|")
    for regime in ["RISK-ON", "RISK-OFF", "NEUTRAL"]:
        rs = best["regime_stats"].get(regime, {})
        if rs["count"] > 0:
            flash_pct = rs["flashes"] / rs["count"] * 100
            lines.append(f"| {regime} | {rs['count']} | {rs['avg']:.1f}mo | {rs['max']}mo | {rs['flashes']} ({flash_pct:.0f}%) |")
    lines.append("")

    # False alarms
    lines.append(f"### False RISK-OFF Signals ({best['false_pos']}):")
    if best["false_pos_months"]:
        for fm in best["false_pos_months"]:
            lines.append(f"  - {fm}")
    else:
        lines.append("  None!")
    lines.append("")

    # Full event assessment
    lines.append("### All Events Assessment:")
    lines.append("| Event | Month | Type | Regime At | Before | Hit? | Lead |")
    lines.append("|-------|-------|------|-----------|--------|------|------|")
    for er in best["event_results"]:
        hit_str = "**YES**" if er["hit"] else "no"
        score_str = f" ({er['score_at']:+.1f})" if er.get("score_at") is not None else ""
        lines.append(f"| {er['event']} | {er['month']} | {er['type']} | "
                     f"{er['regime_at']}{score_str} | {er['regime_before']} | {hit_str} | {er['lead']}mo |")
    lines.append("")

    # ── Monthly Composite Score Timeline ──
    lines.append("---")
    lines.append("## Monthly Composite Score Timeline (Best Variant)")
    lines.append("")
    lines.append("| Month | Raw Score | SH Rotation | BTC Quad | Risk Breadth | Composite | Regime |")
    lines.append("|-------|-----------|-------------|----------|-------------|-----------|--------|")

    for m, row in factors.iterrows():
        regime = best_regimes.get(m, "--")
        comp = best_composites.get(m, "--")
        comp_str = f"{comp:+.1f}" if comp != "--" else "--"
        btc_q = row["btc_quad"] if row["btc_quad"] else "--"
        sh = f"{int(row['sh_bullish'])}/3"

        # Mark crash months
        crash_mark = ""
        for ce in CRASH_EVENTS:
            if ce["month"] == m:
                crash_mark = f" << {ce['event']}"
                break
        for pe in [e for e in ALL_EVENTS if e["type"] == "PEAK"]:
            if pe["month"] == m:
                crash_mark = f" << {pe['event']}"
                break

        lines.append(f"| {m}{crash_mark} | {row['raw_score']:+.1f} | {sh} | {btc_q} | "
                     f"{row['risk_breadth']:.0f}% | {comp_str} | {regime} |")
    lines.append("")

    # ── Improvement Summary ──
    lines.append("---")
    lines.append("## Improvement Summary: Baseline vs Best")
    lines.append("")
    baseline = all_results[0]
    lines.append("| Metric | Baseline (raw +/-3) | Best Composite | Improvement |")
    lines.append("|--------|--------------------|--------------------|-------------|")
    lines.append(f"| Regime changes | {baseline['changes']} | {best['changes']} | **{(1-best['changes']/baseline['changes'])*100:.0f}% fewer** |")
    lines.append(f"| Whipsaws | {baseline['whipsaws']} | {best['whipsaws']} | **{(1-best['whipsaws']/max(baseline['whipsaws'],1))*100:.0f}% fewer** |")
    lines.append(f"| RISK-OFF precision | {baseline['precision']:.0f}% | {best['precision']:.0f}% | **+{best['precision']-baseline['precision']:.0f}pp** |")
    recall_diff = best['recall'] - baseline['recall']
    recall_str = "**same**" if abs(recall_diff) < 1 else f"**{recall_diff:+.0f}pp**"
    lines.append(f"| Crash recall | {baseline['recall']:.0f}% | {best['recall']:.0f}% | {recall_str} |")
    lines.append(f"| 1-mo RISK-OFF flashes | {baseline['regime_stats']['RISK-OFF']['flashes']} | {best['regime_stats']['RISK-OFF']['flashes']} | **{(1-best['regime_stats']['RISK-OFF']['flashes']/max(baseline['regime_stats']['RISK-OFF']['flashes'],1))*100:.0f}% fewer** |")
    lines.append(f"| Avg RISK-OFF duration | {baseline['regime_stats']['RISK-OFF']['avg']:.1f}mo | {best['regime_stats']['RISK-OFF']['avg']:.1f}mo | **{best['regime_stats']['RISK-OFF']['avg']-baseline['regime_stats']['RISK-OFF']['avg']:+.1f}mo** |")
    lines.append("")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("RRG COMPOSITE REGIME FILTER TEST")
    print("=" * 70)

    factors = extract_monthly_factors()
    print(f"Factors extracted for {len(factors)} months")
    print(f"Columns: {factors.columns.tolist()}")

    # Build raw baseline
    raw_scores = dict(zip(factors.index, factors["raw_score"]))
    from backtest.rrg_smoothing_test import scores_to_regimes
    baseline_regimes = scores_to_regimes(raw_scores, 3.0)

    all_results = []

    # Baseline
    print("\n[0] Baseline (raw +/-3)")
    all_results.append(evaluate("0. Baseline (raw +/-3)", baseline_regimes, raw_scores))

    # V1: Conviction 3/5
    print("[V1] Conviction 3/5 factors")
    v1 = filter_v1_conviction(factors)
    all_results.append(evaluate("V1. Conviction 3/5", v1))

    # V2: Conviction 4/5
    print("[V2] Conviction 4/5 factors")
    v2 = filter_v2_conviction_strict(factors)
    all_results.append(evaluate("V2. Conviction 4/5", v2))

    # V3: Weighted composite +/-4
    print("[V3] Weighted composite +/-4")
    v3_reg, v3_comp = filter_v3_weighted(factors)
    all_results.append(evaluate("V3. Weighted +/-4", v3_reg, v3_comp))

    # V4: Weighted + hysteresis (4/1.5)
    print("[V4] Weighted + hysteresis (4/1.5)")
    v4_reg, v4_comp = filter_v4_weighted_hysteresis(factors)
    all_results.append(evaluate("V4. Weighted+Hyst(4/1.5)", v4_reg, v4_comp))

    # V5: Weighted loose +/-3
    print("[V5] Weighted composite +/-3")
    v5_reg, v5_comp = filter_v5_weighted_loose(factors)
    all_results.append(evaluate("V5. Weighted +/-3", v5_reg, v5_comp))

    # V6: Weighted + hysteresis (3.5/1.0)
    print("[V6] Weighted + hysteresis (3.5/1.0)")
    v6_reg, v6_comp = filter_v6_weighted_hyst_loose(factors)
    all_results.append(evaluate("V6. Weighted+Hyst(3.5/1)", v6_reg, v6_comp))

    # Print summary
    print("\n" + "=" * 90)
    print(f"{'Variant':<32} {'Chg':>4} {'Whip':>5} {'R-OFF':>6} {'Prec':>6} {'Recall':>10} {'Neut%':>6} {'Avg Dur':>8}")
    print("-" * 90)
    for r in all_results:
        rs = r["regime_stats"].get("RISK-OFF", {})
        avg_dur = f"{rs.get('avg', 0):.1f}mo"
        print(f"{r['name']:<32} {r['changes']:>4} {r['whipsaws']:>5} "
              f"{r['riskoff_signals']:>6} {r['precision']:>5.0f}% "
              f"{r['crashes_caught']}/{r['total_crashes']} ({r['recall']:>3.0f}%) "
              f"{r['neutral_pct']:>5.0f}% {avg_dur:>8}")

    # Generate report using V6 as best (or determine dynamically)
    report = generate_report(factors, all_results, v6_reg, v6_comp)
    output_path = OUTPUT_DIR / "rrg_composite_filter.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
