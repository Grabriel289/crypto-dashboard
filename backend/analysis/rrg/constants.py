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

# Yahoo Finance API Settings
YAHOO_BASE_URL: Final[str] = "https://query1.finance.yahoo.com/v8/finance/chart"
# Need 127+ trading days → fetch ~300 calendar days to be safe on Render
HISTORY_DAYS: Final[int] = 300
