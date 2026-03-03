"""ABM Backtest — All parameters in one place."""
import os

# ---------------------------------------------------------------------------
# Paths (relative to this file)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")

for d in (DATA_DIR, OUTPUT_DIR, CHARTS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------
BACKTEST_START = "2019-01-01"
BACKTEST_END = "2024-12-31"
EXCHANGE = "binance"
TIMEFRAME = "1d"

CORE_ASSETS = ["BTCUSDT", "ETHUSDT"]

UNIVERSE_BINANCE = [
    # Tier A
    "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT", "TRXUSDT",
    "DOGEUSDT", "ADAUSDT", "LINKUSDT", "LTCUSDT", "ZECUSDT", "VETUSDT",
    # Tier B
    "AVAXUSDT", "SUIUSDT", "SHIBUSDT", "TONUSDT",
    "UNIUSDT", "AAVEUSDT", "NEARUSDT",
    # Tier C
    "MNTUSDT", "TAOUSDT", "PEPEUSDT",
    "ONDOUSDT", "WLDUSDT", "ENAUSDT", "KASUSDT", "APTUSDT",
    "RENDERUSDT", "JUPUSDT", "ARBUSDT", "BONKUSDT", "SEIUSDT",
    "FETUSDT", "INJUSDT", "TIAUSDT", "PENDLEUSDT",
    # Tier D (newer — will have shorter history)
    "PENGUUSDT", "ETHFIUSDT",
    "IPUSDT", "MONUSDT",
]

# OKX fallback for coins not on Binance
UNIVERSE_OKX = [
    "XMR-USDT",
]

# Symbols that may not exist on Binance — skip gracefully
# (HYPEUSDT, CROUSDT, ASTERUSDT, SKYUSDT, WLFIUSDT, PUMPUSDT,
#  VIRTUALUSDT, LITUSDT, AEROUSDT, SPXUSDT are excluded if they fail)

# ---------------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------------
MAX_CONSECUTIVE_MISSING = 7
FILL_METHOD = "ffill"
MIN_COVERAGE_PCT = 0.80
MAX_SINGLE_DAY_RETURN = 5.0      # +500%
MIN_SINGLE_DAY_RETURN = -0.99    # -99%
MIN_DAILY_VOLUME_USD = 1_000_000
MIN_VALID_COUNT = 10

# ---------------------------------------------------------------------------
# Ground truth — altcoin season definition
# ---------------------------------------------------------------------------
SEASON_THRESHOLD = 10.0       # % outperformance vs BTC
SEASON_MIN_DURATION = 7       # days
SEASON_COOLDOWN = 14          # days
PEAK_DRAWDOWN = 15.0          # % from peak to confirm
BREADTH_LOOKBACK = 30         # 30-day return window

# ---------------------------------------------------------------------------
# BM signal methods
# ---------------------------------------------------------------------------
BM14_LOOKBACK = 14
BM14_ENTRY = 5.0
BM14_EXIT = -5.0

BM30_LOOKBACK = 30
BM30_ENTRY = 5.0
BM30_EXIT = -5.0

EMA_FAST = 7
EMA_SLOW = 21

# ---------------------------------------------------------------------------
# ETH/BTC ROC methods
# ---------------------------------------------------------------------------
ROC7_PERIOD = 7
ROC14_PERIOD = 14
ROC7C_PERIOD = 7
ROC7C_CONFIRM = 3

# ---------------------------------------------------------------------------
# Scoring weights (Test E)
# ---------------------------------------------------------------------------
WEIGHT_BM_LEAD = 0.25
WEIGHT_BM_FALSE = 0.25
WEIGHT_BM_NOISE = 0.10
WEIGHT_ROC_LEAD = 0.20
WEIGHT_ROC_FALSE = 0.15
WEIGHT_ROC_NOISE = 0.05

# ---------------------------------------------------------------------------
# Chart style
# ---------------------------------------------------------------------------
CHART_THEME = "dark_background"
CHART_FIGSIZE = (14, 8)
CHART_DPI = 150
