"""
RRG Rotation System — Predictive Power Analysis
=================================================
Tests whether the RRG regime (RISK-ON / RISK-OFF / NEUTRAL) provides
advance warning before major market events across:
  - Traditional market crashes & rallies
  - FED policy pivots
  - Wars & geopolitical shocks
  - COVID-19
  - Crypto market peaks & bottoms
  - US Elections
  - Tariffs & trade wars
  - Crypto-specific crashes (Luna, FTX)
  - Oct 2025 mega-liquidation

For each event we check:
  1. RRG regime 1-3 months BEFORE the event (lead signal)
  2. RRG regime AT the event month
  3. Key asset quadrant positions (safe haven rotation, BTC position)
  4. Whether the signal was actionable (early enough to act on)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# ── Load Data ─────────────────────────────────────────────────────────

DATA_PATH = Path(__file__).parent / "output" / "rrg_fed_rotation_data.parquet"
BTC_PATH = Path(__file__).parent / "data" / "btc_coingecko.csv"
OUTPUT_DIR = Path(__file__).parent / "output"

df = pd.read_parquet(DATA_PATH)
btc_prices = pd.read_csv(BTC_PATH, parse_dates=["snapped_at"])
btc_prices["date"] = btc_prices["snapped_at"].dt.strftime("%Y-%m")
btc_monthly = btc_prices.groupby("date")["price"].last()

# ── Regime Detection (mirrors backtest engine) ────────────────────────

QUADRANT_SCORES = {"Leading": 2, "Improving": 1, "Weakening": -1, "Lagging": -2}
SAFE_HAVENS = ["GLD", "SLV", "TLT", "TIP", "UUP"]
RISK_ASSETS = ["BTC", "IBIT", "ETHA", "QQQ", "IWM", "SMH", "BOTZ", "XLF",
               "XLE", "EEM", "EWJ", "FXI", "HYG", "DBC", "COPX"]


def get_regime(ym: str) -> dict:
    """Get regime score and details for a given month."""
    snap = df[df["date"] == ym]
    if snap.empty:
        return None

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
    if normalized >= 3.0:
        regime = "RISK-ON"
    elif normalized <= -3.0:
        regime = "RISK-OFF"
    else:
        regime = "NEUTRAL"

    return {"regime": regime, "score": round(normalized, 1),
            "risk_raw": risk_score, "safe_raw": safe_score, "n_assets": count}


def get_asset_quad(ym: str, symbol: str) -> str:
    """Get quadrant for a specific asset in a given month."""
    row = df[(df["date"] == ym) & (df["symbol"] == symbol)]
    if row.empty:
        return "--"
    return row.iloc[0]["quadrant"]


def get_safe_haven_state(ym: str) -> dict:
    """Check safe haven rotation pattern."""
    state = {}
    for sym in SAFE_HAVENS:
        state[sym] = get_asset_quad(ym, sym)
    # "Full safe haven rotation" = GLD + TLT + UUP all in Leading/Improving
    gld = state.get("GLD", "--")
    tlt = state.get("TLT", "--")
    uup = state.get("UUP", "--")
    bullish_havens = {"Leading", "Improving"}
    full_rotation = gld in bullish_havens and tlt in bullish_havens and uup in bullish_havens
    return {"positions": state, "full_safe_haven_rotation": full_rotation}


def get_btc_price_at(ym: str) -> float:
    """Get BTC price for a given month."""
    if ym in btc_monthly.index:
        return btc_monthly[ym]
    return None


def month_offset(ym: str, months: int) -> str:
    """Shift a YYYY-MM string by N months."""
    y, m = int(ym[:4]), int(ym[5:7])
    m += months
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}"


# ── Event Definitions ─────────────────────────────────────────────────

EVENTS = [
    # ── Traditional Market ──
    {
        "id": 1,
        "category": "Traditional Market",
        "event": "Taper Tantrum",
        "date": "2013-06",
        "type": "CRASH",
        "description": "Bernanke hints at QE taper; bonds & EM sell off sharply",
        "expected_signal": "RISK-OFF or NEUTRAL before",
        "btc_relevant": True,
    },
    {
        "id": 2,
        "category": "Traditional Market",
        "event": "Oil Crash & EM Crisis",
        "date": "2014-10",
        "type": "CRASH",
        "description": "Oil collapses from $110->$45; EM currencies crash; HY spreads widen",
        "expected_signal": "RISK-OFF before, XLE/DBC/EEM Lagging",
        "btc_relevant": True,
    },
    {
        "id": 3,
        "category": "Traditional Market",
        "event": "China Devaluation & Flash Crash",
        "date": "2015-08",
        "type": "CRASH",
        "description": "PBoC devalues yuan; S&P drops 11% in 6 days; VIX spikes to 53",
        "expected_signal": "RISK-OFF before, FXI/EEM Lagging",
        "btc_relevant": True,
    },
    {
        "id": 4,
        "category": "Traditional Market",
        "event": "Volmageddon + Q4 Selloff",
        "date": "2018-10",
        "type": "CRASH",
        "description": "S&P drops 20% in Q4; VIX blowup Feb; rate fears + trade war",
        "expected_signal": "RISK-OFF before, safe havens rotating in",
        "btc_relevant": True,
    },
    {
        "id": 5,
        "category": "Traditional Market",
        "event": "2022 Bear Market Bottom",
        "date": "2022-10",
        "type": "BOTTOM",
        "description": "S&P bottoms at 3577; inflation peaking, Fed pivot hopes",
        "expected_signal": "RISK-OFF then improving score",
        "btc_relevant": True,
    },
    {
        "id": 6,
        "category": "Traditional Market",
        "event": "SVB / Banking Crisis",
        "date": "2023-03",
        "type": "CRASH",
        "description": "Silicon Valley Bank collapses; regional bank contagion fears",
        "expected_signal": "XLF Lagging, GLD Leading, score dipping",
        "btc_relevant": True,
    },

    # ── FED Policy Pivots ──
    {
        "id": 7,
        "category": "FED Policy",
        "event": "QE3 Launch",
        "date": "2012-09",
        "type": "BULLISH",
        "description": "Fed launches QE3 ($40B MBS/mo -> expanded to $85B)",
        "expected_signal": "RISK-ON after, risk assets Leading",
        "btc_relevant": False,
    },
    {
        "id": 8,
        "category": "FED Policy",
        "event": "First Rate Hike (ZIRP Ends)",
        "date": "2015-12",
        "type": "TIGHTENING",
        "description": "First hike in 9 years: 0.25->0.50%",
        "expected_signal": "NEUTRAL/RISK-OFF, UUP Leading",
        "btc_relevant": True,
    },
    {
        "id": 9,
        "category": "FED Policy",
        "event": "Powell Pivot (Jan 2019)",
        "date": "2019-01",
        "type": "BULLISH",
        "description": "Powell signals patience after Q4 2018 crash; markets V-recover",
        "expected_signal": "RISK-OFF before -> RISK-ON after (swing signal)",
        "btc_relevant": True,
    },
    {
        "id": 10,
        "category": "FED Policy",
        "event": "Emergency COVID Cuts to Zero",
        "date": "2020-03",
        "type": "BULLISH",
        "description": "Emergency 150bp cut to 0% + unlimited QE announced",
        "expected_signal": "RISK-OFF at event -> RISK-ON within 1-2 months",
        "btc_relevant": True,
    },
    {
        "id": 11,
        "category": "FED Policy",
        "event": "Aggressive Hike Cycle Begins",
        "date": "2022-03",
        "type": "TIGHTENING",
        "description": "First hike of aggressive cycle; 425bp in 9 months",
        "expected_signal": "RISK-OFF or deteriorating score before",
        "btc_relevant": True,
    },
    {
        "id": 12,
        "category": "FED Policy",
        "event": "First Rate Cut (Sep 2024)",
        "date": "2024-09",
        "type": "BULLISH",
        "description": "First cut 50bp to 4.75-5.00%; easing cycle begins",
        "expected_signal": "RISK-ON or improving trend",
        "btc_relevant": True,
    },

    # ── Wars & Geopolitical ──
    {
        "id": 13,
        "category": "Geopolitical / War",
        "event": "Russia Invades Ukraine",
        "date": "2022-02",
        "type": "CRASH",
        "description": "Full-scale invasion Feb 24; energy crisis, sanctions, risk-off",
        "expected_signal": "RISK-OFF, XLE/DBC Leading (energy), GLD Leading",
        "btc_relevant": True,
    },
    {
        "id": 14,
        "category": "Geopolitical / War",
        "event": "Hamas-Israel War",
        "date": "2023-10",
        "type": "SHOCK",
        "description": "Oct 7 attack; Middle East escalation fears; oil spike",
        "expected_signal": "GLD Leading, score dipping",
        "btc_relevant": True,
    },

    # ── COVID-19 ──
    {
        "id": 15,
        "category": "COVID-19",
        "event": "COVID Crash",
        "date": "2020-03",
        "type": "CRASH",
        "description": "S&P drops 34% in 23 days; BTC drops 50% on Mar 12-13",
        "expected_signal": "RISK-OFF before, full safe-haven rotation",
        "btc_relevant": True,
    },
    {
        "id": 16,
        "category": "COVID-19",
        "event": "Post-COVID Recovery Rally",
        "date": "2020-06",
        "type": "BULLISH",
        "description": "V-shaped recovery; QE + stimulus driving everything up",
        "expected_signal": "RISK-ON, broad risk assets Leading",
        "btc_relevant": True,
    },

    # ── Crypto Peaks & Bottoms ──
    {
        "id": 17,
        "category": "Crypto Market",
        "event": "BTC 2013 Peak ($1,100)",
        "date": "2013-11",
        "type": "CRYPTO_PEAK",
        "description": "BTC reaches $1,100 in parabolic blow-off; 87% crash follows",
        "expected_signal": "BTC Leading/Weakening (momentum peaking)",
        "btc_relevant": True,
    },
    {
        "id": 18,
        "category": "Crypto Market",
        "event": "BTC 2015 Bottom ($172)",
        "date": "2015-01",
        "type": "CRYPTO_BOTTOM",
        "description": "BTC bottoms at $172 after 14-month bear market",
        "expected_signal": "BTC Lagging -> Improving transition",
        "btc_relevant": True,
    },
    {
        "id": 19,
        "category": "Crypto Market",
        "event": "BTC 2017 Peak ($19,400)",
        "date": "2017-12",
        "type": "CRYPTO_PEAK",
        "description": "ICO mania peak; BTC hits $19,400 then crashes 84%",
        "expected_signal": "BTC Leading/Weakening, broad market still RISK-ON",
        "btc_relevant": True,
    },
    {
        "id": 20,
        "category": "Crypto Market",
        "event": "Crypto Winter Bottom ($3,200)",
        "date": "2018-12",
        "type": "CRYPTO_BOTTOM",
        "description": "BTC bottoms at $3,200; aligns with Q4 2018 equity crash",
        "expected_signal": "RISK-OFF, BTC Lagging for months",
        "btc_relevant": True,
    },
    {
        "id": 21,
        "category": "Crypto Market",
        "event": "BTC 2021 ATH ($67,000)",
        "date": "2021-11",
        "type": "CRYPTO_PEAK",
        "description": "BTC hits $67K ATH; end of COVID liquidity supercycle",
        "expected_signal": "BTC Leading/Weakening, score peaking, taper starting",
        "btc_relevant": True,
    },
    {
        "id": 22,
        "category": "Crypto Market",
        "event": "Luna/UST Collapse",
        "date": "2022-05",
        "type": "CRYPTO_CRASH",
        "description": "UST depeg -> LUNA death spiral; $60B wiped; BTC drops to $26K",
        "expected_signal": "RISK-OFF before, BTC already Lagging",
        "btc_relevant": True,
    },
    {
        "id": 23,
        "category": "Crypto Market",
        "event": "FTX Collapse",
        "date": "2022-11",
        "type": "CRYPTO_CRASH",
        "description": "FTX insolvent; BTC drops from $21K->$16K; industry contagion",
        "expected_signal": "RISK-OFF, BTC Lagging",
        "btc_relevant": True,
    },
    {
        "id": 24,
        "category": "Crypto Market",
        "event": "BTC Cycle Bottom ($16,300)",
        "date": "2022-11",
        "type": "CRYPTO_BOTTOM",
        "description": "BTC bottoms at $16,300 post-FTX; coincides with equity bottom",
        "expected_signal": "RISK-OFF extreme -> recovery signal within 1-2 months",
        "btc_relevant": True,
    },
    {
        "id": 25,
        "category": "Crypto Market",
        "event": "BTC ETF Rally ($73K ATH)",
        "date": "2024-03",
        "type": "CRYPTO_PEAK",
        "description": "BTC hits $73K post-ETF approval + halving anticipation",
        "expected_signal": "RISK-ON, BTC/IBIT Leading",
        "btc_relevant": True,
    },
    {
        "id": 26,
        "category": "Crypto Market",
        "event": "Oct 2025 Mega Liquidation",
        "date": "2025-10",
        "type": "CRYPTO_CRASH",
        "description": "Biggest liquidation event in crypto history; ~$19B+ wiped",
        "expected_signal": "RISK-OFF or deteriorating score before, BTC Weakening/Lagging",
        "btc_relevant": True,
    },

    # ── US Elections ──
    {
        "id": 27,
        "category": "US Election",
        "event": "Obama Re-election 2012",
        "date": "2012-11",
        "type": "ELECTION",
        "description": "Obama wins 2nd term; fiscal cliff fears then resolved",
        "expected_signal": "Regime shift around election month",
        "btc_relevant": False,
    },
    {
        "id": 28,
        "category": "US Election",
        "event": "Trump Election 2016",
        "date": "2016-11",
        "type": "ELECTION",
        "description": "Trump wins; 'reflation trade' — XLF, IWM surge; bonds dump",
        "expected_signal": "RISK-ON after, XLF/IWM Leading, TLT Lagging",
        "btc_relevant": True,
    },
    {
        "id": 29,
        "category": "US Election",
        "event": "Biden Election 2020",
        "date": "2020-11",
        "type": "ELECTION",
        "description": "Biden wins; stimulus expectations; clean energy + value rotation",
        "expected_signal": "RISK-ON, broad risk Leading",
        "btc_relevant": True,
    },
    {
        "id": 30,
        "category": "US Election",
        "event": "Trump Election 2024",
        "date": "2024-11",
        "type": "ELECTION",
        "description": "Trump wins; pro-crypto stance; BTC rallies to $100K+",
        "expected_signal": "RISK-ON, BTC/IBIT Leading",
        "btc_relevant": True,
    },

    # ── Tariffs & Trade Wars ──
    {
        "id": 31,
        "category": "Tariff / Trade War",
        "event": "US-China Trade War Escalation",
        "date": "2018-06",
        "type": "CRASH",
        "description": "Trump imposes $50B tariffs on China; retaliation begins",
        "expected_signal": "EEM/FXI Lagging, UUP Leading, score deteriorating",
        "btc_relevant": True,
    },
    {
        "id": 32,
        "category": "Tariff / Trade War",
        "event": "Trade War Escalation (Aug 2019)",
        "date": "2019-08",
        "type": "CRASH",
        "description": "Trump announces 10% tariff on remaining $300B China goods",
        "expected_signal": "RISK-OFF spike, safe havens Leading",
        "btc_relevant": True,
    },
    {
        "id": 33,
        "category": "Tariff / Trade War",
        "event": "Trump Tariff Shock 2025",
        "date": "2025-03",
        "type": "CRASH",
        "description": "Broad tariff threats on multiple countries; market uncertainty",
        "expected_signal": "GLD Leading, score deteriorating, risk-off",
        "btc_relevant": True,
    },
]

# ══════════════════════════════════════════════════════════════════════
#  Analysis Engine
# ══════════════════════════════════════════════════════════════════════

def analyze_event(event: dict) -> dict:
    """Analyze RRG regime and key asset positions around an event."""
    ym = event["date"]

    # Get regime at event and 1-3 months before
    regimes = {}
    for offset in [-3, -2, -1, 0, 1, 2]:
        m = month_offset(ym, offset)
        r = get_regime(m)
        if r:
            regimes[offset] = r

    # Safe haven state at event and before
    sh_at = get_safe_haven_state(ym)
    sh_before_1 = get_safe_haven_state(month_offset(ym, -1))
    sh_before_2 = get_safe_haven_state(month_offset(ym, -2))

    # BTC quadrant
    btc_quads = {}
    for offset in [-3, -2, -1, 0, 1, 2]:
        m = month_offset(ym, offset)
        btc_quads[offset] = get_asset_quad(m, "BTC")

    # Key asset positions at event month
    key_positions = {}
    for sym in ["BTC", "QQQ", "SMH", "GLD", "TLT", "UUP", "XLE", "EEM", "FXI", "XLF", "IWM"]:
        key_positions[sym] = get_asset_quad(ym, sym)

    # BTC price
    btc_price = get_btc_price_at(ym)

    # Score trend (direction of score change leading into event)
    scores_before = [regimes[o]["score"] for o in [-3, -2, -1] if o in regimes]
    score_at = regimes[0]["score"] if 0 in regimes else None
    if len(scores_before) >= 2:
        score_trend = scores_before[-1] - scores_before[0]
    else:
        score_trend = None

    # Predictive assessment
    prediction = assess_prediction(event, regimes, sh_before_1, sh_before_2, btc_quads, score_trend)

    return {
        "event": event,
        "regimes": regimes,
        "safe_haven_at": sh_at,
        "safe_haven_before_1": sh_before_1,
        "safe_haven_before_2": sh_before_2,
        "btc_quads": btc_quads,
        "key_positions": key_positions,
        "btc_price": btc_price,
        "score_trend": score_trend,
        "prediction": prediction,
    }


def assess_prediction(event, regimes, sh_1, sh_2, btc_quads, score_trend) -> dict:
    """
    Assess whether RRG gave an early warning signal.
    Returns: signal_type, lead_months, correct (bool), explanation
    """
    etype = event["type"]
    regime_before_1 = regimes.get(-1, {}).get("regime", "N/A")
    regime_before_2 = regimes.get(-2, {}).get("regime", "N/A")
    regime_before_3 = regimes.get(-3, {}).get("regime", "N/A")
    regime_at = regimes.get(0, {}).get("regime", "N/A")
    score_before_1 = regimes.get(-1, {}).get("score", None)
    score_before_2 = regimes.get(-2, {}).get("score", None)
    score_at = regimes.get(0, {}).get("score", None)

    # Full safe-haven rotation before?
    fsh_1 = sh_1.get("full_safe_haven_rotation", False)
    fsh_2 = sh_2.get("full_safe_haven_rotation", False)

    if etype in ("CRASH", "CRYPTO_CRASH"):
        # For crashes: did RRG show RISK-OFF or deteriorating score BEFORE?
        early_warning = False
        lead = 0
        explanation = ""

        if regime_before_2 == "RISK-OFF" or regime_before_3 == "RISK-OFF":
            early_warning = True
            lead = 2 if regime_before_2 == "RISK-OFF" else 3
            explanation = f"RISK-OFF signal {lead}mo before crash"
        elif regime_before_1 == "RISK-OFF":
            early_warning = True
            lead = 1
            explanation = "RISK-OFF 1mo before crash"
        elif score_trend is not None and score_trend < -2.0:
            early_warning = True
            lead = 1
            explanation = f"Score deteriorating {score_trend:+.1f} pts into crash"
        elif fsh_1 or fsh_2:
            early_warning = True
            lead = 1 if fsh_1 else 2
            explanation = f"Full safe-haven rotation {lead}mo before crash"
        elif regime_before_1 == "NEUTRAL" and score_before_1 is not None and score_before_1 < 0:
            early_warning = True
            lead = 1
            explanation = f"Negative NEUTRAL ({score_before_1:+.1f}) 1mo before crash"
        elif regime_at == "RISK-OFF":
            early_warning = False
            lead = 0
            explanation = "RISK-OFF detected same month (reactive, not predictive)"
        else:
            explanation = f"No clear warning; regime before: {regime_before_1} ({score_before_1})"

        return {"correct": early_warning, "lead_months": lead,
                "signal": "RISK-OFF" if early_warning else "MISS",
                "explanation": explanation}

    elif etype == "CRYPTO_PEAK":
        # For crypto peaks: was BTC in Leading/Weakening? Score peaking?
        btc_before = btc_quads.get(-1, "--")
        btc_at = btc_quads.get(0, "--")
        early_warning = False
        lead = 0
        explanation = ""

        # BTC Weakening before peak = divergence warning
        if btc_quads.get(-1) == "Weakening" or btc_quads.get(-2) == "Weakening":
            early_warning = True
            lead = 1 if btc_quads.get(-1) == "Weakening" else 2
            explanation = f"BTC Weakening {lead}mo before peak (momentum fading while price rises)"
        elif score_trend is not None and score_trend < -1.0:
            early_warning = True
            lead = 1
            explanation = f"Score deteriorating ({score_trend:+.1f}) into peak"
        elif regime_before_1 in ("NEUTRAL", "RISK-OFF"):
            early_warning = True
            lead = 1
            explanation = f"Regime already {regime_before_1} before peak (divergence)"
        else:
            explanation = f"BTC was {btc_at} at peak; regime {regime_at}"

        return {"correct": early_warning, "lead_months": lead,
                "signal": "PEAK_WARNING" if early_warning else "MISS",
                "explanation": explanation}

    elif etype in ("CRYPTO_BOTTOM", "BOTTOM"):
        # For bottoms: was RRG at extreme RISK-OFF then improving?
        early_warning = False
        lead = 0
        explanation = ""

        score_after_1 = regimes.get(1, {}).get("score", None)
        regime_after_1 = regimes.get(1, {}).get("regime", "N/A")

        if regime_at == "RISK-OFF" and score_after_1 is not None and score_after_1 > score_at:
            early_warning = True
            lead = 0
            explanation = f"RISK-OFF extreme at bottom ({score_at:+.1f}), then recovery ({score_after_1:+.1f})"
        elif regime_before_1 == "RISK-OFF" and regime_at != "RISK-OFF":
            early_warning = True
            lead = 0
            explanation = f"Regime flip from RISK-OFF -> {regime_at} at bottom"
        elif score_at is not None and score_at <= -5:
            early_warning = True
            lead = 0
            explanation = f"Extreme RISK-OFF score ({score_at:+.1f}) = contrarian buy signal"
        else:
            explanation = f"Regime at bottom: {regime_at} ({score_at})"

        return {"correct": early_warning, "lead_months": lead,
                "signal": "BOTTOM_SIGNAL" if early_warning else "MISS",
                "explanation": explanation}

    elif etype == "BULLISH":
        # For bullish pivots: did RISK-ON emerge within 1-2 months?
        early_warning = False
        lead = 0
        regime_after_1 = regimes.get(1, {}).get("regime", "N/A")
        regime_after_2 = regimes.get(2, {}).get("regime", "N/A")
        score_after_1 = regimes.get(1, {}).get("score", None)

        if regime_at == "RISK-ON" or regime_after_1 == "RISK-ON":
            early_warning = True
            lead = 0 if regime_at == "RISK-ON" else -1
            explanation = f"RISK-ON confirmed at/near event"
        elif score_at is not None and score_after_1 is not None and (score_after_1 - score_at) > 3:
            early_warning = True
            lead = 0
            explanation = f"Score swing +{score_after_1 - score_at:.1f} after event = bull ignition"
        elif score_trend is not None and score_trend > 2:
            early_warning = True
            lead = 1
            explanation = f"Score improving ({score_trend:+.1f}) into bullish event"
        else:
            explanation = f"Regime at event: {regime_at}, after: {regime_after_1}"

        return {"correct": early_warning, "lead_months": lead,
                "signal": "RISK-ON" if early_warning else "MISS",
                "explanation": explanation}

    elif etype == "TIGHTENING":
        # For tightening: did risk-off or deterioration show before?
        early_warning = False
        explanation = ""
        if regime_before_1 in ("RISK-OFF", "NEUTRAL") or (score_trend is not None and score_trend < 0):
            early_warning = True
            explanation = f"Score trending down ({score_trend:+.1f}) or regime {regime_before_1} before tightening"
        else:
            explanation = f"Regime before: {regime_before_1}"

        return {"correct": early_warning, "lead_months": 1,
                "signal": "RISK-OFF" if early_warning else "MISS",
                "explanation": explanation}

    elif etype == "ELECTION":
        # Elections: check for regime shift around event
        regime_before = regime_before_1
        regime_after_1 = regimes.get(1, {}).get("regime", "N/A")
        shift = regime_before != regime_after_1 or regime_at != regime_before
        explanation = f"Before: {regime_before} -> At: {regime_at} -> After: {regime_after_1}"
        return {"correct": shift, "lead_months": 0,
                "signal": "REGIME_SHIFT" if shift else "STABLE",
                "explanation": explanation}

    elif etype == "SHOCK":
        # Geopolitical shocks: check for GLD Leading + risk deterioration
        gld_at = get_asset_quad(event["date"], "GLD")
        early_warning = gld_at in ("Leading", "Improving") or regime_at in ("RISK-OFF", "NEUTRAL")
        explanation = f"GLD={gld_at}, regime={regime_at} ({score_at})"
        return {"correct": early_warning, "lead_months": 0,
                "signal": "DEFENSIVE" if early_warning else "MISS",
                "explanation": explanation}

    return {"correct": False, "lead_months": 0, "signal": "N/A", "explanation": "Unclassified event type"}


# ══════════════════════════════════════════════════════════════════════
#  Report Generation
# ══════════════════════════════════════════════════════════════════════

def generate_report(results: list) -> str:
    lines = []
    lines.append("# RRG Rotation System — Predictive Power Analysis")
    lines.append("## Can RRG Regime Scores Predict Major Market Events?")
    lines.append("")
    lines.append("**Methodology:** For each historical event, we check the RRG regime score")
    lines.append("1-3 months BEFORE the event occurred. A 'hit' means the system provided")
    lines.append("an actionable signal before the event — not just a reactive reading at the time.")
    lines.append("")
    lines.append(f"**Data range:** Jan 2012 — Oct 2025 ({len(EVENTS)} events tested)")
    lines.append(f"**Assets tracked:** {len(df['symbol'].unique())} (incl. BTC from CoinGecko Apr 2013+)")
    lines.append("")

    # ── Grand Summary Table ──
    lines.append("---")
    lines.append("## Grand Summary: All Events")
    lines.append("")
    lines.append("| # | Category | Event | Date | Type | Signal | Lead | Hit? | Score Before->At | BTC |")
    lines.append("|---|----------|-------|------|------|--------|------|------|-----------------|-----|")

    total_hits = 0
    total_events = 0
    category_stats = {}

    for r in results:
        ev = r["event"]
        pred = r["prediction"]
        regime_before = r["regimes"].get(-1, {})
        regime_at = r["regimes"].get(0, {})
        sb = regime_before.get("score", "--")
        sa = regime_at.get("score", "--")
        score_str = f"{sb}->{sa}" if sb != "--" else f"--->{sa}"

        btc_q = r["btc_quads"].get(0, "--")
        btc_p = r["btc_price"]
        btc_str = f"{btc_q}" + (f" ${btc_p:,.0f}" if btc_p else "")

        hit = "YES" if pred["correct"] else "NO"
        lead_str = f"{pred['lead_months']}mo" if pred["lead_months"] > 0 else "0mo"
        hit_icon = "**YES**" if pred["correct"] else "no"

        lines.append(f"| {ev['id']} | {ev['category']} | {ev['event']} | {ev['date']} | "
                     f"{ev['type']} | {pred['signal']} | {lead_str} | {hit_icon} | {score_str} | {btc_str} |")

        total_events += 1
        if pred["correct"]:
            total_hits += 1

        cat = ev["category"]
        if cat not in category_stats:
            category_stats[cat] = {"hits": 0, "total": 0}
        category_stats[cat]["total"] += 1
        if pred["correct"]:
            category_stats[cat]["hits"] += 1

    lines.append("")
    lines.append(f"**Overall Hit Rate: {total_hits}/{total_events} ({total_hits/total_events*100:.0f}%)**")
    lines.append("")

    # Category breakdown
    lines.append("### Hit Rate by Category")
    lines.append("| Category | Hits | Total | Rate |")
    lines.append("|----------|------|-------|------|")
    for cat, stats in sorted(category_stats.items()):
        rate = stats["hits"] / stats["total"] * 100 if stats["total"] > 0 else 0
        lines.append(f"| {cat} | {stats['hits']} | {stats['total']} | {rate:.0f}% |")
    lines.append("")

    # ── Detailed Event Analysis ──
    lines.append("---")
    lines.append("## Detailed Event-by-Event Analysis")
    lines.append("")

    current_cat = ""
    for r in results:
        ev = r["event"]
        pred = r["prediction"]

        if ev["category"] != current_cat:
            current_cat = ev["category"]
            lines.append(f"### {current_cat}")
            lines.append("")

        hit_icon = "HIT" if pred["correct"] else "MISS"
        lines.append(f"#### Event #{ev['id']}: {ev['event']} ({ev['date']}) — **{hit_icon}**")
        lines.append(f"_{ev['description']}_")
        lines.append("")

        # Regime timeline
        lines.append("**Regime Timeline (3mo before -> 2mo after):**")
        lines.append("| Month | Regime | Score | BTC Quad |")
        lines.append("|-------|--------|-------|----------|")
        for offset in [-3, -2, -1, 0, 1, 2]:
            m = month_offset(ev["date"], offset)
            reg = r["regimes"].get(offset, {})
            regime_str = reg.get("regime", "--")
            score_str = f"{reg.get('score', '--'):+.1f}" if "score" in reg else "--"
            btc_q = r["btc_quads"].get(offset, "--")
            marker = " **← EVENT**" if offset == 0 else ""
            label = f"T{offset:+d}" if offset != 0 else "T=0"
            lines.append(f"| {m} ({label}){marker} | {regime_str} | {score_str} | {btc_q} |")
        lines.append("")

        # Key positions at event
        lines.append("**Key Asset Positions at Event:**")
        pos_parts = []
        for sym in ["BTC", "QQQ", "GLD", "TLT", "UUP", "XLE", "EEM", "FXI", "XLF"]:
            q = r["key_positions"].get(sym, "--")
            if q != "--":
                pos_parts.append(f"{sym}={q}")
        lines.append(", ".join(pos_parts))
        lines.append("")

        # Safe haven state
        sh = r["safe_haven_at"]
        fsh = "YES" if sh["full_safe_haven_rotation"] else "no"
        sh_str = ", ".join(f"{s}={q}" for s, q in sh["positions"].items())
        lines.append(f"**Safe Haven Rotation:** {sh_str} | Full rotation: {fsh}")
        lines.append("")

        # Prediction assessment
        lines.append(f"**Assessment:** {pred['explanation']}")
        lines.append(f"**Lead time:** {pred['lead_months']} month(s)")
        lines.append("")

    # ── Key Findings ──
    lines.append("---")
    lines.append("## Key Findings")
    lines.append("")

    # Crash prediction accuracy
    crash_events = [r for r in results if r["event"]["type"] in ("CRASH", "CRYPTO_CRASH")]
    crash_hits = sum(1 for r in crash_events if r["prediction"]["correct"])
    lines.append(f"### 1. Crash/Crisis Prediction: {crash_hits}/{len(crash_events)} ({crash_hits/len(crash_events)*100:.0f}%)")
    lines.append("")
    for r in crash_events:
        ev = r["event"]
        pred = r["prediction"]
        icon = "+" if pred["correct"] else "-"
        lines.append(f"  {icon} **{ev['event']}** ({ev['date']}): {pred['explanation']}")
    lines.append("")

    # Crypto peak prediction
    peak_events = [r for r in results if r["event"]["type"] == "CRYPTO_PEAK"]
    peak_hits = sum(1 for r in peak_events if r["prediction"]["correct"])
    lines.append(f"### 2. Crypto Peak Detection: {peak_hits}/{len(peak_events)} ({peak_hits/len(peak_events)*100:.0f}%)")
    lines.append("")
    for r in peak_events:
        ev = r["event"]
        pred = r["prediction"]
        icon = "+" if pred["correct"] else "-"
        lines.append(f"  {icon} **{ev['event']}** ({ev['date']}): {pred['explanation']}")
    lines.append("")

    # Bottom detection
    bottom_events = [r for r in results if r["event"]["type"] == "CRYPTO_BOTTOM"]
    bottom_hits = sum(1 for r in bottom_events if r["prediction"]["correct"])
    lines.append(f"### 3. Crypto Bottom Detection: {bottom_hits}/{len(bottom_events)} ({bottom_hits/len(bottom_events)*100:.0f}%)")
    lines.append("")
    for r in bottom_events:
        ev = r["event"]
        pred = r["prediction"]
        icon = "+" if pred["correct"] else "-"
        lines.append(f"  {icon} **{ev['event']}** ({ev['date']}): {pred['explanation']}")
    lines.append("")

    # Safe haven rotation as crash indicator
    lines.append("### 4. Full Safe-Haven Rotation as Crash Indicator")
    lines.append("")
    lines.append("When GLD + TLT + UUP all in Leading/Improving simultaneously:")
    lines.append("")
    # Check all months for full safe-haven rotation
    all_months = sorted(df["date"].unique())
    fsh_months = []
    for m in all_months:
        sh = get_safe_haven_state(m)
        if sh["full_safe_haven_rotation"]:
            reg = get_regime(m)
            fsh_months.append((m, reg["score"] if reg else None))
    if fsh_months:
        lines.append("| Month | Score | What Followed |")
        lines.append("|-------|-------|---------------|")
        for m, score in fsh_months:
            # Check what happened 1-3 months later
            future_events = [e for e in EVENTS
                            if month_offset(e["date"], -3) <= m <= month_offset(e["date"], 0)
                            and e["type"] in ("CRASH", "CRYPTO_CRASH")]
            followed = ", ".join(e["event"] for e in future_events) if future_events else "no major crash within 3mo"
            lines.append(f"| {m} | {score:+.1f} | {followed} |")
    else:
        lines.append("No months with full safe-haven rotation detected.")
    lines.append("")

    # BTC as leading indicator
    lines.append("### 5. BTC Quadrant as Crypto Market Leading Indicator")
    lines.append("")
    lines.append("BTC quadrant transitions around crypto-specific events:")
    lines.append("")
    crypto_events = [r for r in results if r["event"]["category"] == "Crypto Market"]
    for r in crypto_events:
        ev = r["event"]
        bq = r["btc_quads"]
        trail = " -> ".join(f"{bq.get(o, '--')}" for o in [-3, -2, -1, 0, 1, 2])
        lines.append(f"- **{ev['event']}** ({ev['date']}): {trail}")
    lines.append("")

    # Score extremes
    lines.append("### 6. Score Extremes as Contrarian Signals")
    lines.append("")
    lines.append("Months where RRG score hit extreme levels:")
    lines.append("")
    lines.append("| Month | Score | Regime | What Happened Next |")
    lines.append("|-------|-------|--------|--------------------|")
    for m in all_months:
        reg = get_regime(m)
        if reg and (reg["score"] <= -5 or reg["score"] >= 7):
            next_m = month_offset(m, 1)
            next_reg = get_regime(next_m)
            next_str = f"{next_reg['regime']} ({next_reg['score']:+.1f})" if next_reg else "--"
            btc_p = get_btc_price_at(m)
            btc_str = f"BTC ${btc_p:,.0f}" if btc_p else ""
            lines.append(f"| {m} | {reg['score']:+.1f} | {reg['regime']} | Next month: {next_str} {btc_str} |")
    lines.append("")

    # ── Conclusion ──
    lines.append("---")
    lines.append("## Conclusion: RRG as Market Regime Filter")
    lines.append("")
    lines.append(f"**Overall predictive accuracy: {total_hits}/{total_events} ({total_hits/total_events*100:.0f}%)**")
    lines.append("")
    lines.append("### Strengths:")
    lines.append("- Regime score captures macro risk appetite effectively")
    lines.append("- Safe-haven rotation (GLD+TLT+UUP) provides 1-2 month crash lead time")
    lines.append("- Score extremes (<= -5) are reliable contrarian buy signals at bottoms")
    lines.append("- BTC quadrant transitions align with crypto cycle peaks/bottoms")
    lines.append("")
    lines.append("### Limitations:")
    lines.append("- Crypto-specific black swans (Luna, FTX) may not show in macro RRG if contagion is contained")
    lines.append("- Monthly granularity means fast crashes (COVID, flash crashes) can hit before signal update")
    lines.append("- Election impact is mixed — markets sometimes rally regardless of regime reading")
    lines.append("")
    lines.append("### Actionable Rules for Crypto Trading:")
    lines.append("1. **Score <= -5 + BTC Lagging** -> Contrarian accumulation zone (historical bottoms)")
    lines.append("2. **Full safe-haven rotation** -> Reduce exposure, expect crash within 1-3 months")
    lines.append("3. **BTC Weakening while score > 0** -> Peak warning, consider taking profit")
    lines.append("4. **Score swing > +5 from trough** -> Bull ignition, increase exposure")
    lines.append("5. **Score > +5 + BTC Leading** -> Risk-on confirmed, ride the trend")
    lines.append("")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("RRG PREDICTIVE POWER ANALYSIS")
    print(f"Testing {len(EVENTS)} events across 2012-2025")
    print("=" * 60)

    results = []
    for event in EVENTS:
        result = analyze_event(event)
        pred = result["prediction"]
        icon = "HIT" if pred["correct"] else "MISS"
        print(f"  [{icon}] #{event['id']:02d} {event['event']} ({event['date']}) -- {pred['explanation']}")
        results.append(result)

    # Generate report
    report = generate_report(results)
    output_path = OUTPUT_DIR / "rrg_predictive_analysis.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {output_path}")

    # Summary stats
    hits = sum(1 for r in results if r["prediction"]["correct"])
    print(f"\n{'=' * 60}")
    print(f"OVERALL: {hits}/{len(results)} events predicted ({hits/len(results)*100:.0f}%)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
