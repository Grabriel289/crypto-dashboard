"""RRG Rotation Map constants."""
from typing import Final, Dict, Any

# ETF Symbols for RRG Analysis
ETF_SYMBOLS = {
    # Benchmark
    "SPY": {"name": "S&P 500", "category": "benchmark", "color": "#6b7280"},
    
    # Risk Assets
    "IBIT": {"name": "Bitcoin", "category": "risk", "color": "#f7931a"},
    "ETHA": {"name": "Ethereum", "category": "risk", "color": "#627eea"},
    "BOTZ": {"name": "AI/Robotics", "category": "risk", "color": "#8b5cf6"},
    "QQQ": {"name": "Nasdaq 100", "category": "risk", "color": "#00d4aa"},
    "IWM": {"name": "Small Cap", "category": "risk", "color": "#f85149"},
    
    # Safe Haven Assets
    "GLD": {"name": "Gold", "category": "safe_haven", "color": "#ffd700"},
    "TLT": {"name": "Long-Term Bonds", "category": "safe_haven", "color": "#4ade80"},
    "SHY": {"name": "Short-Term Bonds", "category": "safe_haven", "color": "#22d3ee"},
    "UUP": {"name": "US Dollar", "category": "safe_haven", "color": "#a3e635"},
}

# RRG Calculation Parameters
RS_RATIO_PERIOD: Final[int] = 10      # SMA period for RS-Ratio
RS_MOMENTUM_PERIOD: Final[int] = 6    # SMA period for RS-Momentum
CENTER_VALUE: Final[float] = 100.0    # Normalization center

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
HISTORY_DAYS: Final[int] = 60
