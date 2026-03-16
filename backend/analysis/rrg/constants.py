"""Accelerating Momentum Rotation Map constants."""
from typing import Final, Dict, Any

# ETF Symbols for Rotation Analysis
ETF_SYMBOLS = {
    # Benchmark (fetched for reference; excluded from rotation output)
    "SPY": {"name": "S&P 500", "category": "benchmark", "color": "#6b7280"},

    # Risk Assets — Crypto
    "IBIT": {"name": "Bitcoin", "category": "risk", "color": "#f7931a"},
    "ETHA": {"name": "Ethereum", "category": "risk", "color": "#627eea"},

    # Risk Assets — Equity / Sector
    "QQQ": {"name": "Nasdaq 100", "category": "risk", "color": "#00d4aa"},
    "IWM": {"name": "Small Cap", "category": "risk", "color": "#f85149"},
    "SMH": {"name": "Semiconductors", "category": "risk", "color": "#06b6d4"},
    "BOTZ": {"name": "AI/Robotics", "category": "risk", "color": "#8b5cf6"},
    "XLF": {"name": "Financials", "category": "risk", "color": "#2563eb"},
    "XLE": {"name": "Energy", "category": "risk", "color": "#ef4444"},

    # Risk Assets — Regional
    "EEM": {"name": "Emerging Mkts", "category": "risk", "color": "#fb923c"},
    "EWJ": {"name": "Japan", "category": "risk", "color": "#e11d48"},
    "FXI": {"name": "China", "category": "risk", "color": "#dc2626"},

    # Risk Assets — Credit / Commodity
    "HYG": {"name": "High Yield", "category": "risk", "color": "#f472b6"},
    "DBC": {"name": "Commodities", "category": "risk", "color": "#a16207"},
    "COPX": {"name": "Copper Miners", "category": "risk", "color": "#b45309"},

    # Safe Haven Assets
    "GLD": {"name": "Gold", "category": "safe_haven", "color": "#ffd700"},
    "SLV": {"name": "Silver", "category": "safe_haven", "color": "#94a3b8"},
    "TLT": {"name": "Long-Term Bonds", "category": "safe_haven", "color": "#4ade80"},
    "TIP": {"name": "TIPS (Inflation)", "category": "safe_haven", "color": "#22d3ee"},
    "UUP": {"name": "US Dollar", "category": "safe_haven", "color": "#a3e635"},
}

# Accelerating Momentum Parameters (trading days)
SHORT_PERIOD: Final[int] = 21     # 1-month momentum window
LONG_PERIOD: Final[int] = 126     # 6-month momentum window (for acceleration)
SCALE_FACTOR: Final[int] = 5      # 1 std dev = 5 points from center (100)
CENTER_VALUE: Final[float] = 100.0

# Regime Detection
QUADRANT_SCORES: Final[Dict[str, int]] = {
    "leading": 2,
    "improving": 1,
    "weakening": -1,
    "lagging": -2,
}

RISK_ON_THRESHOLD: Final[float] = 3.0
RISK_OFF_THRESHOLD: Final[float] = -3.0

# ── V6 Composite Regime Filter ──────────────────────────────────────
# Multi-factor weighted composite with hysteresis (backtested 2012-2025)
# Reduces whipsaws by 50% vs raw threshold while keeping 85% crash recall

V6_SAFE_HAVEN_KEYS: Final[list] = ["GLD", "TLT", "UUP"]

# Weighted composite factor scores
V6_WEIGHTS: Final[Dict[str, Any]] = {
    # Factor 1: Raw regime score level
    "score_strong_bear": {"threshold": -5, "value": -2.0},
    "score_bear":        {"threshold": -2, "value": -1.0},
    "score_strong_bull": {"threshold":  5, "value":  2.0},
    "score_bull":        {"threshold":  2, "value":  1.0},
    # Factor 2: Score trend (2-period direction)
    "trend_strong_down": {"threshold": -4, "value": -1.5},
    "trend_down":        {"threshold": -2, "value": -0.75},
    "trend_strong_up":   {"threshold":  4, "value":  1.5},
    "trend_up":          {"threshold":  2, "value":  0.75},
    # Factor 3: Safe-haven rotation (GLD+TLT+UUP in Leading/Improving)
    "sh_full":           {"count": 3, "value": -2.0},    # 3/3 = very bearish
    "sh_partial":        {"count": 2, "value": -1.0},    # 2/3
    "sh_none":           {"count": 0, "value":  1.5},    # 0/3 = bullish
    # Factor 4: BTC/crypto quadrant
    "btc_leading":       {"value":  1.0},
    "btc_improving":     {"value":  0.5},
    "btc_weakening":     {"value": -0.5},
    "btc_lagging":       {"value": -1.0},
    # Factor 5: Risk breadth (% risk assets in Leading/Improving)
    "breadth_very_low":  {"threshold": 20, "value": -1.5},
    "breadth_low":       {"threshold": 35, "value": -0.75},
    "breadth_high":      {"threshold": 50, "value":  0.75},
    "breadth_very_high": {"threshold": 65, "value":  1.5},
}

# Hysteresis thresholds — require stronger signal to enter, weaker to exit
V6_ENTER_THRESHOLD: Final[float] = 3.5   # composite must hit +/-3.5 to flip
V6_EXIT_THRESHOLD: Final[float] = 1.0    # composite must cross +/-1.0 to revert

# Yahoo Finance API Settings
YAHOO_BASE_URL: Final[str] = "https://query1.finance.yahoo.com/v8/finance/chart"
# Need 127+ trading days → fetch ~300 calendar days to be safe on Render
HISTORY_DAYS: Final[int] = 300
