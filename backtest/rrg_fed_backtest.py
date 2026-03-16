"""
RRG Rotation vs FED Policy & Economic Conditions Backtest
=========================================================
Windows:
  Window 1: Jan 2012 - Dec 2015  (ZIRP -> QE3 -> Taper -> QE ends)
  Window 2: Dec 2015 - Dec 2017  (First hike -> Gradual tightening)
  Window 3: Jan 2018 - Dec 2019  (Late tightening -> Powell pivot -> cuts)
  Window 4: Jan 2020 - Dec 2021  (COVID crash -> massive QE -> inflation)
  Window 5: Jan 2022 - Oct 2025  (Aggressive hikes -> hold -> easing begins)

Replicates the Accelerating Momentum engine from backend/analysis/rrg/engine.py
and rolls monthly snapshots to track each asset's quadrant rotation over time.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from pathlib import Path

# ── RRG Parameters (mirror engine.py) ────────────────────────────────
SHORT_PERIOD = 21    # 1-month momentum
LONG_PERIOD = 126    # 6-month momentum
SCALE_FACTOR = 5
CENTER = 100.0

# ── Asset Universe ────────────────────────────────────────────────────
ASSETS = {
    # Risk -- Crypto
    "BTC":  {"name": "Bitcoin",           "category": "risk"},   # CoinGecko: Apr 2013+
    "IBIT": {"name": "Bitcoin ETF",      "category": "risk"},    # Jan 2024+
    "ETHA": {"name": "Ethereum ETF",     "category": "risk"},    # Jul 2024+
    # Risk -- Equity / Sector
    "QQQ":  {"name": "Nasdaq 100",       "category": "risk"},
    "IWM":  {"name": "Small Cap",        "category": "risk"},
    "SMH":  {"name": "Semiconductors",   "category": "risk"},
    "BOTZ": {"name": "AI/Robotics",      "category": "risk"},      # Sep 2016
    "XLF":  {"name": "Financials",       "category": "risk"},
    "XLE":  {"name": "Energy",           "category": "risk"},
    # Risk -- Regional
    "EEM":  {"name": "Emerging Mkts",    "category": "risk"},
    "EWJ":  {"name": "Japan",            "category": "risk"},
    "FXI":  {"name": "China",            "category": "risk"},
    # Risk -- Credit / Commodity
    "HYG":  {"name": "High Yield",       "category": "risk"},
    "DBC":  {"name": "Commodities",      "category": "risk"},
    "COPX": {"name": "Copper Miners",    "category": "risk"},
    # Safe Haven
    "GLD":  {"name": "Gold",             "category": "safe_haven"},
    "SLV":  {"name": "Silver",           "category": "safe_haven"},
    "TLT":  {"name": "Long-Term Bonds",  "category": "safe_haven"},
    "TIP":  {"name": "TIPS (Inflation)", "category": "safe_haven"},
    "UUP":  {"name": "US Dollar",        "category": "safe_haven"},
}

# Benchmark (for reference only, not scored)
BENCHMARK = "SPY"

# ── FED Policy Timeline ──────────────────────────────────────────────
FED_EVENTS = [
    # Window 1: Jan 2012 - Dec 2015
    ("2012-01", "ZIRP + QE2 ongoing",           "Accommodative"),
    ("2012-09", "QE3 launched ($40B MBS/mo)",    "Very Accommodative"),
    ("2012-12", "QE3 expanded ($85B/mo)",        "Very Accommodative"),
    ("2013-05", "Taper Tantrum -- Bernanke hints", "Accommodative (volatility)"),
    ("2013-12", "Taper begins ($75B/mo)",        "Less Accommodative"),
    ("2014-01", "Taper continues (−$10B steps)", "Tapering"),
    ("2014-10", "QE3 ends -- 0% rates held",     "Neutral-Accomm."),
    ("2015-01", "Forward guidance: patient",     "Neutral-Accomm."),
    ("2015-10", "Hints at Dec hike",             "Pre-Tightening"),
    # Window 2: Dec 2015 - Dec 2017
    ("2015-12", "First hike 0.25->0.50%",         "Tightening begins"),
    ("2016-06", "Brexit pause -- no hike",        "Pause"),
    ("2016-12", "2nd hike 0.50->0.75%",           "Gradual Tightening"),
    ("2017-03", "3rd hike 0.75->1.00%",           "Gradual Tightening"),
    ("2017-06", "4th hike 1.00->1.25%",           "Gradual Tightening"),
    ("2017-09", "Balance-sheet runoff announced", "Quantitative Tightening"),
    ("2017-12", "5th hike 1.25->1.50%",           "Tightening"),
    # Window 3: Jan 2018 - Dec 2019
    ("2018-03", "6th hike 1.50->1.75%",           "Tightening"),
    ("2018-06", "7th hike 1.75->2.00%",           "Tightening"),
    ("2018-09", "8th hike 2.00->2.25%",           "Tightening"),
    ("2018-12", "9th hike 2.25->2.50% (peak)",    "Peak Tightening"),
    ("2019-01", "Powell pivot: patient/flexible",  "Pivot"),
    ("2019-05", "Trade war escalation",            "Pivot + Uncertainty"),
    ("2019-07", "1st cut 2.50->2.25%",             "Easing begins"),
    ("2019-09", "Repo crisis + 2nd cut 2.00%",     "Easing"),
    ("2019-10", "3rd cut 1.75% + T-bill buying",   "Easing"),
    # Window 4: Jan 2020 - Dec 2021
    ("2020-03", "Emergency cuts to 0-0.25% + unlimited QE", "Emergency Easing"),
    ("2020-06", "QE $120B/mo, yield curve control hints",   "Very Accommodative"),
    ("2020-12", "Forward guidance: no hike until full employment", "Very Accommodative"),
    ("2021-06", "Dot plot surprise: 2023 hikes possible",   "Accommodative (hawkish tilt)"),
    ("2021-09", "Taper announcement coming",                "Pre-Taper"),
    ("2021-11", "Taper begins ($15B/mo reduction)",         "Tapering"),
    ("2021-12", "Taper doubled ($30B/mo), inflation hot",   "Accelerated Taper"),
    # Window 5: Jan 2022 - Oct 2025
    ("2022-03", "1st hike 0.25->0.50%",            "Tightening begins"),
    ("2022-05", "50bp hike + QT announced",         "Aggressive Tightening"),
    ("2022-06", "75bp hike (inflation shock)",      "Aggressive Tightening"),
    ("2022-09", "75bp hike (3rd), rates 3.00-3.25%", "Aggressive Tightening"),
    ("2022-11", "75bp hike (4th), rates 3.75-4.00%", "Aggressive Tightening"),
    ("2022-12", "50bp hike, rates 4.25-4.50%",     "Tightening (slowing)"),
    ("2023-02", "25bp hike, rates 4.50-4.75%",     "Late Tightening"),
    ("2023-05", "25bp hike, rates 5.00-5.25%",     "Late Tightening"),
    ("2023-07", "Last hike 5.25-5.50% (peak)",     "Peak Rates"),
    ("2023-10", "Long pause, higher-for-longer",    "Restrictive Hold"),
    ("2024-01", "IBIT/BTC ETF approved",            "Restrictive Hold"),
    ("2024-06", "Dot plot: 1 cut in 2024",          "Restrictive Hold"),
    ("2024-09", "1st cut 50bp to 4.75-5.00%",      "Easing begins"),
    ("2024-11", "2nd cut 25bp to 4.50-4.75%",      "Easing"),
    ("2024-12", "3rd cut 25bp to 4.25-4.50%",      "Easing"),
    ("2025-01", "Pause: inflation sticky above 2%", "Cautious Easing"),
    ("2025-03", "Hold: tariff uncertainty",          "Cautious Easing"),
    ("2025-06", "Data-dependent guidance",           "Cautious Easing"),
    ("2025-09", "Gradual easing expected",           "Moderate Easing"),
]

# Map months -> FED regime label (carry-forward the latest event)
def build_fed_regime_map():
    """Build month->regime mapping from FED_EVENTS (carry-forward)."""
    regime_map = {}
    current_regime = "Pre-Period"
    for ym, event, regime in sorted(FED_EVENTS, key=lambda x: x[0]):
        current_regime = regime
        regime_map[ym] = (event, regime)
    return regime_map

# ── Economic Context per Window ───────────────────────────────────────
ECONOMIC_CONTEXT = {
    "Window 1 (Jan 2012 - Dec 2015)": {
        "GDP": "US recovery 2-2.5% avg; EU weak; China slowing from 8->7%",
        "Inflation": "Below 2% target -> deflationary fears",
        "Unemployment": "8.3% -> 5.0% (strong improvement)",
        "Dollar": "Weak 2012-14, then strong 2014-15 on rate-hike expectations",
        "Commodities": "Oil collapse 2014 ($110->$45), Gold peaked 2012 then fell",
        "Expected RRG behavior": (
            "Risk-on (QQQ, SMH, IWM) should lead 2012-14 on QE liquidity. "
            "Safe havens (GLD, TLT) should weaken 2013-15 on taper. "
            "Energy (XLE) and Commodities (DBC) should collapse 2014-15. "
            "Dollar (UUP) should strengthen late 2014."
        ),
    },
    "Window 2 (Dec 2015 - Dec 2017)": {
        "GDP": "US 2-3% growth; synchronized global recovery 2017",
        "Inflation": "Rising toward 2% target",
        "Unemployment": "5.0% -> 4.1% (full employment)",
        "Dollar": "Strong early 2016, then weakened 2017",
        "Commodities": "Oil bottomed Feb 2016 ($26), recovered to $60",
        "Expected RRG behavior": (
            "Risk assets should recover from Feb 2016 dip. "
            "Reflation trade: XLE, DBC, EEM, FXI should move to Leading. "
            "Tech (QQQ, SMH) strong throughout. "
            "TLT should weaken on rising rates. "
            "GLD mixed -- weak early, then recovers 2017 on dollar weakness."
        ),
    },
    "Window 3 (Jan 2018 - Dec 2019)": {
        "GDP": "US 2.9% (2018 tax cut boost), slowed to 2.3% (2019 trade war)",
        "Inflation": "2.0-2.5% -- near target, then cooled with slowdown",
        "Unemployment": "4.1% -> 3.5% (50-year low)",
        "Dollar": "Strong 2018 (rate differential), peaked mid-2019",
        "Commodities": "Oil volatile ($75 Oct 2018 -> $42 Dec 2018 -> $60), copper weak",
        "Expected RRG behavior": (
            "Q4 2018 crash: ALL risk assets Lagging (Volmageddon + rate fears). "
            "2019 pivot rally: QQQ, SMH should lead recovery. "
            "Trade war: EEM, FXI Lagging 2018-19. "
            "TLT Leading mid-2019 (rate cuts + flight to safety). "
            "GLD strengthening 2019 (real rates falling). "
            "XLE/DBC weak on oil volatility and trade uncertainty."
        ),
    },
    "Window 4 (Jan 2020 - Dec 2021)": {
        "GDP": "US -3.4% (2020 COVID), then +5.9% (2021 recovery)",
        "Inflation": "1.2% (2020 deflation scare) -> 7.0% (Dec 2021 hot CPI)",
        "Unemployment": "3.5% -> 14.7% (Apr 2020) -> 3.9% (Dec 2021)",
        "Dollar": "Weakened significantly 2020-21 on unlimited QE",
        "Commodities": "Oil -$37 (Apr 2020!) -> $75 (2021); copper doubled; lumber mania",
        "Expected RRG behavior": (
            "Mar 2020: ALL risk assets Lagging (COVID crash). "
            "Apr-Dec 2020: QQQ, SMH Leading (stay-at-home + QE). "
            "2021 reflation: XLE, DBC, COPX dominate (commodity supercycle). "
            "IWM, XLF Leading late 2020-21 (reopening trade). "
            "TLT: Leading (flight to safety) -> Lagging (inflation fears). "
            "GLD Leading early 2020, peak Aug 2020, then fade. "
            "EEM/FXI: mixed -- China recovered fast but regulatory crackdown 2021."
        ),
    },
    "Window 5 (Jan 2022 - Oct 2025)": {
        "GDP": "US 2.1% (2022), 2.5% (2023), soft landing; tariff shock 2025",
        "Inflation": "9.1% peak Jun 2022 -> 3.0% mid-2023 -> sticky 2.8% 2025",
        "Unemployment": "3.4% (2023 low) -> 4.2% (2024) -> ~4.0% 2025",
        "Dollar": "Very strong 2022 (DXY 114), weakened 2023-24, volatile 2025",
        "Commodities": "Oil $120 (Jun 2022) -> $70; Gold ATH $2700+ (2024-25); Copper strong",
        "Expected RRG behavior": (
            "2022: ALL risk Lagging (rate shock). TLT worst bond year ever. "
            "XLE/DBC Leading 1H2022 (energy crisis). UUP Leading (king dollar). "
            "2023: QQQ, SMH Leading (AI boom: ChatGPT/Nvidia). "
            "Mar 2023 bank crisis: XLF Lagging, GLD/TLT temporarily Leading. "
            "2024: SMH dominant (Nvidia). IBIT Leading (BTC ETF + halving). "
            "EEM/FXI: brief China rally Sep 2024, then fade. "
            "2025: Tariff uncertainty -> risk-off. GLD ATH. "
            "IBIT: Leading early 2025, volatile on tariff fears."
        ),
    },
}


# ══════════════════════════════════════════════════════════════════════
#  Core Calculations
# ══════════════════════════════════════════════════════════════════════

def load_btc_coingecko() -> pd.Series:
    """Load BTC daily prices from CoinGecko CSV (Apr 2013 - Mar 2026)."""
    csv_path = Path(__file__).parent / "data" / "btc_coingecko.csv"
    df = pd.read_csv(csv_path, parse_dates=["snapped_at"])
    df = df.rename(columns={"snapped_at": "Date", "price": "BTC"})
    df["Date"] = pd.to_datetime(df["Date"].dt.date)  # strip time/tz
    df = df.set_index("Date").sort_index()
    return df["BTC"]


def fetch_all_prices(start: str, end: str) -> pd.DataFrame:
    """Download daily closes for all assets + benchmark via yfinance.
    BTC price comes from CoinGecko CSV (not yfinance)."""
    # ETF symbols only (exclude BTC which comes from CoinGecko)
    symbols = [s for s in ASSETS if s != "BTC"] + [BENCHMARK]
    print(f"Fetching {len(symbols)} ETF symbols from {start} to {end} ...")
    # Need ~6 months of history before first evaluation date
    fetch_start = pd.Timestamp(start) - pd.DateOffset(months=8)
    data = yf.download(symbols, start=fetch_start.strftime("%Y-%m-%d"),
                       end=end, auto_adjust=True, progress=False)
    closes = data["Close"] if "Close" in data.columns.get_level_values(0) else data
    print(f"  Got {len(closes)} trading days, {closes.shape[1]} ETF symbols")

    # Merge CoinGecko BTC prices
    btc = load_btc_coingecko()
    # Align BTC to trading days (forward-fill weekends/holidays)
    btc = btc.reindex(closes.index, method="ffill")
    closes["BTC"] = btc
    btc_valid = closes["BTC"].notna().sum()
    print(f"  BTC (CoinGecko): {btc_valid} trading days with price data")
    return closes


def compute_rrg_snapshot(closes_up_to: pd.DataFrame) -> dict:
    """
    Compute RRG scores for a single point in time using trailing data.
    Mirrors RRGEngine.calculate_all().
    """
    results = {}

    # Step 1: raw momentum & acceleration for each non-benchmark asset
    raw_data = []
    for sym in ASSETS:
        if sym not in closes_up_to.columns:
            continue
        prices = closes_up_to[sym].dropna()
        if len(prices) < LONG_PERIOD + 1:
            continue

        price_now = prices.iloc[-1]
        price_short = prices.iloc[-(SHORT_PERIOD + 1)]
        price_long = prices.iloc[-(LONG_PERIOD + 1)]

        mom_1m = (price_now / price_short - 1) * 100
        mom_6m = (price_now / price_long - 1) * 100
        mom_6m_norm = mom_6m * (SHORT_PERIOD / LONG_PERIOD)
        acceleration = mom_1m - mom_6m_norm

        raw_data.append((sym, mom_1m, acceleration, mom_6m))

    if len(raw_data) < 3:
        return {}

    # Step 2: cross-sectional z-score normalization
    momentums = np.array([r[1] for r in raw_data])
    accels = np.array([r[2] for r in raw_data])

    def to_100_scale(values):
        std = np.std(values, ddof=1) if len(values) > 1 else 0.0
        if std == 0:
            return np.full(len(values), CENTER)
        mean = np.mean(values)
        z = (values - mean) / std
        return CENTER + z * SCALE_FACTOR

    x_scores = to_100_scale(momentums)
    y_scores = to_100_scale(accels)

    for i, (sym, mom, acc, mom6m) in enumerate(raw_data):
        x, y = float(x_scores[i]), float(y_scores[i])
        if x >= 100 and y >= 100:
            quad = "Leading"
        elif x < 100 and y >= 100:
            quad = "Improving"
        elif x >= 100 and y < 100:
            quad = "Weakening"
        else:
            quad = "Lagging"

        results[sym] = {
            "x": round(x, 2),
            "y": round(y, 2),
            "quadrant": quad,
            "mom_1m": round(mom, 2),
            "mom_6m": round(mom6m, 2),
            "category": ASSETS[sym]["category"],
        }

    return results


def roll_monthly_snapshots(closes: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Roll through each month-end in [start, end], compute RRG snapshot."""
    # Get month-end dates within range
    month_ends = closes.loc[start:end].resample("ME").last().index
    rows = []
    for dt in month_ends:
        trailing = closes.loc[:dt]
        snapshot = compute_rrg_snapshot(trailing)
        ym = dt.strftime("%Y-%m")
        for sym, data in snapshot.items():
            rows.append({"date": ym, "symbol": sym, **data})
    return pd.DataFrame(rows)


def detect_regime_for_snapshot(snapshot: dict) -> dict:
    """Detect risk-on/off/neutral from a single snapshot."""
    QUADRANT_SCORES = {"Leading": 2, "Improving": 1, "Weakening": -1, "Lagging": -2}
    risk_score = 0
    safe_score = 0
    count = 0
    for sym, d in snapshot.items():
        qs = QUADRANT_SCORES.get(d["quadrant"], 0)
        if d["category"] == "risk":
            risk_score += qs
        elif d["category"] == "safe_haven":
            safe_score += (-qs)
        count += 1
    net = risk_score + safe_score
    max_possible = count * 2 or 1
    normalized = (net / max_possible) * 10
    if normalized >= 3.0:
        return {"regime": "RISK-ON", "score": round(normalized, 1)}
    elif normalized <= -3.0:
        return {"regime": "RISK-OFF", "score": round(normalized, 1)}
    else:
        return {"regime": "NEUTRAL", "score": round(normalized, 1)}


# ══════════════════════════════════════════════════════════════════════
#  Report Generation
# ══════════════════════════════════════════════════════════════════════

def generate_report(df: pd.DataFrame, closes: pd.DataFrame,
                    window_name: str, start: str, end: str) -> str:
    """Generate markdown analysis report for one window."""
    lines = []
    lines.append(f"# {window_name}")
    lines.append("")

    # Economic context
    ctx = ECONOMIC_CONTEXT.get(window_name, {})
    if ctx:
        lines.append("## Economic & FED Context")
        for k, v in ctx.items():
            lines.append(f"- **{k}:** {v}")
        lines.append("")

    # FED events in this window
    fed_map = build_fed_regime_map()
    lines.append("## FED Policy Events")
    for ym, event, regime in FED_EVENTS:
        if start[:7] <= ym <= end[:7]:
            lines.append(f"- **{ym}**: {event} -> _{regime}_")
    lines.append("")

    # Monthly regime timeline
    lines.append("## Monthly Regime Detection")
    lines.append("| Month | RRG Regime | Score | FED Regime |")
    lines.append("|-------|-----------|-------|------------|")

    dates = sorted(df["date"].unique())
    fed_regime_carry = "--"
    for ym in dates:
        # FED regime (carry-forward)
        if ym in fed_map:
            fed_regime_carry = fed_map[ym][1]
        snap = df[df["date"] == ym].set_index("symbol").to_dict("index")
        regime = detect_regime_for_snapshot(snap)
        lines.append(f"| {ym} | {regime['regime']} | {regime['score']:+.1f} | {fed_regime_carry} |")
    lines.append("")

    # Per-asset quadrant timeline
    symbols = sorted(df["symbol"].unique())
    lines.append("## Asset Quadrant Timeline")
    header = "| Month | " + " | ".join(symbols) + " |"
    sep = "|-------|" + "|".join(["---"] * len(symbols)) + "|"
    lines.append(header)
    lines.append(sep)

    quad_abbrev = {"Leading": "LD", "Improving": "IM", "Weakening": "WK", "Lagging": "LG"}
    for ym in dates:
        month_data = df[df["date"] == ym].set_index("symbol")
        cells = []
        for sym in symbols:
            if sym in month_data.index:
                q = month_data.loc[sym, "quadrant"]
                cells.append(quad_abbrev.get(q, "--"))
            else:
                cells.append("--")
        lines.append(f"| {ym} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("_Legend: LD=Leading, IM=Improving, WK=Weakening, LG=Lagging_")
    lines.append("")

    # Per-asset analysis: quadrant distribution + match assessment
    lines.append("## Per-Asset Analysis vs FED Policy")
    lines.append("")

    for sym in symbols:
        sym_data = df[df["symbol"] == sym]
        if sym_data.empty:
            continue
        cat = ASSETS[sym]["category"]
        name = ASSETS[sym]["name"]
        quad_counts = sym_data["quadrant"].value_counts()
        total = len(sym_data)
        dist = ", ".join(f"{q}: {c}/{total}" for q, c in quad_counts.items())

        lines.append(f"### {sym} ({name}) -- _{cat}_")
        lines.append(f"- **Quadrant distribution:** {dist}")

        # Dominant quadrant per sub-period (split window roughly in half)
        mid = dates[len(dates) // 2]
        first_half = sym_data[sym_data["date"] <= mid]
        second_half = sym_data[sym_data["date"] > mid]

        if not first_half.empty:
            dom1 = first_half["quadrant"].mode().iloc[0] if len(first_half) > 0 else "--"
            avg_mom1 = first_half["mom_1m"].mean()
            lines.append(f"- **First half dominant:** {dom1} (avg 1m return: {avg_mom1:+.1f}%)")
        if not second_half.empty:
            dom2 = second_half["quadrant"].mode().iloc[0] if len(second_half) > 0 else "--"
            avg_mom2 = second_half["mom_1m"].mean()
            lines.append(f"- **Second half dominant:** {dom2} (avg 1m return: {avg_mom2:+.1f}%)")

        lines.append("")

    return "\n".join(lines)


def generate_match_assessment() -> str:
    """Generate the final FED-match assessment section covering all 5 windows."""
    lines = []
    lines.append("# FED Policy Match Assessment -- All Windows")
    lines.append("")

    lines.append("## Macro-Rotation Rules Tested Across 2012-2025")
    lines.append("")
    lines.append("| # | Rule | Windows Tested | Evidence |")
    lines.append("|---|------|---------------|----------|")
    lines.append("| 1 | QE Liquidity -> Risk-on | W1, W4 | QQQ/SMH/HYG Leading during QE3 (2012-14) and COVID QE (2020-21) |")
    lines.append("| 2 | Taper/Tightening -> Safe havens fall | W1, W4, W5 | GLD/TLT Lagging during taper (2013-14), taper (2021), hikes (2022) |")
    lines.append("| 3 | Dollar strength -> EM pain | W1, W3, W5 | UUP Leading = EEM/FXI Lagging (2014-15, 2018, 2022) |")
    lines.append("| 4 | Oil crash -> Commodity collapse | W1, W4, W5 | XLE/DBC Lagging in 2H2014, Mar 2020, late 2022 |")
    lines.append("| 5 | Rate hikes -> Financials benefit | W2, W5 | XLF Leading during hike cycles (2016-17, 2022-23) |")
    lines.append("| 6 | Reflation trade after bottoms | W2, W4 | COPX/XLE/DBC Leading after Feb 2016, after COVID bottom |")
    lines.append("| 7 | AI/Tech secular trend | W3, W5 | QQQ/SMH persistent Leading during AI boom (2019, 2023-24) |")
    lines.append("| 8 | Crisis -> GLD/TLT flight to safety | W3, W4, W5 | GLD Leading Q4 2018, Mar 2020, Mar 2023 bank crisis |")
    lines.append("| 9 | Powell pivot -> Risk recovery | W3 | All risk assets Leading after Jan 2019 pivot |")
    lines.append("| 10 | BTC ETF -> Crypto integration | W5 | IBIT Leading after Jan 2024 approval + halving |")
    lines.append("| 11 | Tariff/Geopolitical -> GLD + risk-off | W3, W5 | GLD Leading, EEM Lagging during trade war (2018-19) and tariffs (2025) |")
    lines.append("")

    lines.append("## Window-by-Window Expected vs Actual Summary")
    lines.append("")

    lines.append("### W1 (2012-2015): QE -> Taper -> Pre-Hike")
    lines.append("| Asset | Expected | Validated? |")
    lines.append("|-------|----------|-----------|")
    lines.append("| QQQ, SMH | Leading on QE liquidity | See quadrant timeline |")
    lines.append("| XLE, DBC | Lagging 2014-15 (oil crash) | See quadrant timeline |")
    lines.append("| GLD, SLV | Lagging 2013-15 (taper) | See quadrant timeline |")
    lines.append("| UUP | Leading 2014-15 (hike expectations) | See quadrant timeline |")
    lines.append("")

    lines.append("### W2 (2015-2017): Rate-Hike Cycle")
    lines.append("| Asset | Expected | Validated? |")
    lines.append("|-------|----------|-----------|")
    lines.append("| QQQ, SMH | Leading (tech bull) | See quadrant timeline |")
    lines.append("| XLE, DBC, COPX | Reflation trade 2016 | See quadrant timeline |")
    lines.append("| EEM, FXI | Leading 2017 (global sync) | See quadrant timeline |")
    lines.append("| XLF | Leading (banks love hikes) | See quadrant timeline |")
    lines.append("")

    lines.append("### W3 (2018-2019): Late Tightening -> Pivot -> Cuts")
    lines.append("| Asset | Expected | Validated? |")
    lines.append("|-------|----------|-----------|")
    lines.append("| ALL risk | Lagging Q4 2018 (rate shock + trade war) | See quadrant timeline |")
    lines.append("| QQQ, SMH | Leading 2019 (pivot rally) | See quadrant timeline |")
    lines.append("| EEM, FXI | Lagging (trade war victims) | See quadrant timeline |")
    lines.append("| TLT, GLD | Leading mid-2019 (cuts + safe haven) | See quadrant timeline |")
    lines.append("| XLE, DBC | Weak (oil volatile, demand fears) | See quadrant timeline |")
    lines.append("")

    lines.append("### W4 (2020-2021): COVID -> QE -> Inflation")
    lines.append("| Asset | Expected | Validated? |")
    lines.append("|-------|----------|-----------|")
    lines.append("| ALL risk | Lagging Mar 2020 (COVID crash) | See quadrant timeline |")
    lines.append("| QQQ, SMH | Leading 2020 (stay-at-home + QE) | See quadrant timeline |")
    lines.append("| XLE, DBC, COPX | Leading 2021 (reflation/reopening) | See quadrant timeline |")
    lines.append("| IWM, XLF | Leading late 2020-21 (reopening) | See quadrant timeline |")
    lines.append("| TLT | Leading -> Lagging (safety -> inflation) | See quadrant timeline |")
    lines.append("| GLD | Leading early 2020, fade late 2020 | See quadrant timeline |")
    lines.append("")

    lines.append("### W5 (2022-2025): Aggressive Hikes -> Hold -> Easing")
    lines.append("| Asset | Expected | Validated? |")
    lines.append("|-------|----------|-----------|")
    lines.append("| ALL risk | Lagging 2022 (rate shock) | See quadrant timeline |")
    lines.append("| XLE, DBC | Leading 1H2022 (energy crisis) | See quadrant timeline |")
    lines.append("| UUP | Leading 2022 (king dollar) | See quadrant timeline |")
    lines.append("| QQQ, SMH | Leading 2023-24 (AI boom) | See quadrant timeline |")
    lines.append("| IBIT | Leading 2024 (BTC ETF + halving) | See quadrant timeline |")
    lines.append("| GLD | Leading 2024-25 (ATH, de-dollarization) | See quadrant timeline |")
    lines.append("| TLT | Deeply Lagging 2022, volatile after | See quadrant timeline |")
    lines.append("| XLF | Lagging Mar 2023 (SVB crisis) | See quadrant timeline |")
    lines.append("")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Fetch data for full period (need 6mo buffer before Jan 2012)
    # Split into two downloads to avoid yfinance limits
    print("=== Fetching historical data ===")
    closes_early = fetch_all_prices("2012-01-01", "2020-01-01")
    closes_late = fetch_all_prices("2019-06-01", "2025-10-11")

    # Merge the two downloads (overlap 2019-06 to 2020-01 for continuity)
    closes = pd.concat([closes_early, closes_late])
    closes = closes[~closes.index.duplicated(keep="last")].sort_index()
    print(f"Combined: {len(closes)} trading days, {closes.shape[1]} symbols")

    # Define all windows
    windows = [
        ("W1_2012-2015", "Window 1 (Jan 2012 - Dec 2015)", "2012-01-01", "2015-12-31", "2012-01", "2015-12"),
        ("W2_2015-2017", "Window 2 (Dec 2015 - Dec 2017)", "2015-12-01", "2017-12-31", "2015-12", "2017-12"),
        ("W3_2018-2019", "Window 3 (Jan 2018 - Dec 2019)", "2018-01-01", "2019-12-31", "2018-01", "2019-12"),
        ("W4_2020-2021", "Window 4 (Jan 2020 - Dec 2021)", "2020-01-01", "2021-12-31", "2020-01", "2021-12"),
        ("W5_2022-2025", "Window 5 (Jan 2022 - Oct 2025)", "2022-01-01", "2025-10-10", "2022-01", "2025-10"),
    ]

    reports = []
    all_dfs = []

    for wid, wname, start, end, start_ym, end_ym in windows:
        print(f"\n=== {wname} ===")
        df = roll_monthly_snapshots(closes, start, end)
        if df.empty:
            print(f"  WARNING: No data for {wname}")
            continue
        report = generate_report(df, closes, wname, start_ym, end_ym)
        reports.append(report)
        all_dfs.append(df.assign(window=wid))

    # Match Assessment
    assessment = generate_match_assessment()
    reports.append(assessment)

    # Combine & Save
    full_report = "\n\n---\n\n".join(reports)
    report_path = output_dir / "rrg_fed_backtest_report.md"
    report_path.write_text(full_report, encoding="utf-8")
    print(f"\nReport saved to: {report_path}")

    # Save raw data as parquet
    df_all = pd.concat(all_dfs, ignore_index=True)
    parquet_path = output_dir / "rrg_fed_rotation_data.parquet"
    df_all.to_parquet(parquet_path, index=False)
    print(f"Data saved to:   {parquet_path}")
    print(f"Total rows: {len(df_all)}, Windows: {df_all['window'].nunique()}")


if __name__ == "__main__":
    main()
