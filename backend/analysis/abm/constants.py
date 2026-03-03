"""Altcoin Breadth Momentum (ABM) constants and universe definition."""

# ---------------------------------------------------------------------------
# Signal thresholds — Breadth 90D (Panel 2: peak warning)
# ---------------------------------------------------------------------------
BREADTH_PEAK_THRESHOLD = 70  # Breadth 90D > 70% → alt season peak
BREADTH_HIGH = 50            # Breadth 90D > 50% → strong alt season
BREADTH_LOW = 30             # Breadth 90D <= 30% → BTC dominant

# ---------------------------------------------------------------------------
# BM method: EMA crossover (validated via backtest — best noise/lead ratio)
# ---------------------------------------------------------------------------
EMA_FAST = 7                 # Fast EMA span on breadth series
EMA_SLOW = 21                # Slow EMA span on breadth series

# ---------------------------------------------------------------------------
# Lookback periods (calendar days)
# ---------------------------------------------------------------------------
BREADTH_LOOKBACK = 30        # 30-day return window for Panel 1 breadth
BREADTH_LONG_LOOKBACK = 90   # 90-day return window for Panel 2 breadth

# Need 90D lookback + enough history for EMA convergence + chart buffer.
KLINE_LIMIT = 200            # ~200 calendar days of daily klines

# ---------------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------------
MIN_VALID_COUNT = 10         # Skip day if fewer than 10 coins have data

# ---------------------------------------------------------------------------
# 50-Altcoin Universe (ex-BTC, ex-stablecoins, ex-wrapped)
#
# Each entry: coin → { "binance": ticker | None, "okx": ticker | None, "bybit": ticker | None }
# None (or absent) means the coin is not available on that exchange.
# Fallback order: Binance → OKX → Bybit
# ---------------------------------------------------------------------------
ABM_UNIVERSE = {
    # Tier A — long history (2017+)
    "ETH":   {"binance": "ETHUSDT",   "okx": "ETH-USDT"},
    "BNB":   {"binance": "BNBUSDT",   "okx": "BNB-USDT"},
    "XRP":   {"binance": "XRPUSDT",   "okx": "XRP-USDT"},
    "SOL":   {"binance": "SOLUSDT",   "okx": "SOL-USDT"},
    "TRX":   {"binance": "TRXUSDT",   "okx": "TRX-USDT"},
    "DOGE":  {"binance": "DOGEUSDT",  "okx": "DOGE-USDT"},
    "ADA":   {"binance": "ADAUSDT",   "okx": "ADA-USDT"},
    "XMR":   {"binance": None,        "okx": "XMR-USDT"},      # Delisted from Binance
    "LINK":  {"binance": "LINKUSDT",  "okx": "LINK-USDT"},
    "LTC":   {"binance": "LTCUSDT",   "okx": "LTC-USDT"},
    "ZEC":   {"binance": "ZECUSDT",   "okx": "ZEC-USDT"},
    "VET":   {"binance": "VETUSDT",   "okx": "VET-USDT"},

    # Tier B — 2020-2021
    "HYPE":  {"binance": None,        "okx": "HYPE-USDT"},
    "AVAX":  {"binance": "AVAXUSDT",  "okx": "AVAX-USDT"},
    "SUI":   {"binance": "SUIUSDT",   "okx": "SUI-USDT"},
    "SHIB":  {"binance": "SHIBUSDT",  "okx": "SHIB-USDT"},
    "TON":   {"binance": "TONUSDT",   "okx": "TON-USDT"},
    "CRO":   {"binance": None,        "okx": "CRO-USDT"},
    "UNI":   {"binance": "UNIUSDT",   "okx": "UNI-USDT"},
    "AAVE":  {"binance": "AAVEUSDT",  "okx": "AAVE-USDT"},
    "NEAR":  {"binance": "NEARUSDT",  "okx": "NEAR-USDT"},

    # Tier C — 2022-2023
    "MNT":   {"binance": "MNTUSDT",   "okx": "MNT-USDT"},
    "TAO":   {"binance": "TAOUSDT",   "okx": "TAO-USDT"},
    "ASTER": {"binance": "ASTERUSDT", "okx": None},             # Ticker is ASTER not ASTR
    "SKY":   {"binance": None,        "okx": "SKY-USDT"},
    "PEPE":  {"binance": "PEPEUSDT",  "okx": "PEPE-USDT"},
    "ONDO":  {"binance": "ONDOUSDT",  "okx": "ONDO-USDT"},
    "WLD":   {"binance": "WLDUSDT",   "okx": "WLD-USDT"},
    "ENA":   {"binance": "ENAUSDT",   "okx": "ENA-USDT"},
    "KAS":   {"binance": "KASUSDT",   "okx": "KAS-USDT"},
    "APT":   {"binance": "APTUSDT",   "okx": "APT-USDT"},
    "RENDER": {"binance": "RENDERUSDT", "okx": "RENDER-USDT"},
    "JUP":   {"binance": "JUPUSDT",   "okx": "JUP-USDT"},
    "ARB":   {"binance": "ARBUSDT",   "okx": "ARB-USDT"},
    "BONK":  {"binance": "BONKUSDT",  "okx": "BONK-USDT"},
    "SEI":   {"binance": "SEIUSDT",   "okx": "SEI-USDT"},
    "FET":   {"binance": "FETUSDT",   "okx": "FET-USDT"},
    "INJ":   {"binance": "INJUSDT",   "okx": "INJ-USDT"},
    "TIA":   {"binance": "TIAUSDT",   "okx": "TIA-USDT"},
    "PENDLE": {"binance": "PENDLEUSDT", "okx": "PENDLE-USDT"},

    # Tier D — 2024+ (limited history)
    "WLFI":  {"binance": None,        "okx": None},             # Very new, may fail
    "PUMP":  {"binance": None,        "okx": "PUMP-USDT"},
    "VIRTUAL": {"binance": "VIRTUALUSDT", "okx": "VIRTUAL-USDT"},
    "PENGU": {"binance": "PENGUUSDT", "okx": "PENGU-USDT"},
    "ETHFI": {"binance": "ETHFIUSDT", "okx": "ETHFI-USDT"},
    "LIT":   {"binance": None,        "okx": "LIT-USDT"},
    "AERO":  {"binance": "AEROUSDT",  "okx": None},
    "SPX":   {"binance": None,        "okx": None},             # Very new, may fail
    "IP":    {"binance": "IPUSDT",    "okx": "IP-USDT"},
    "MON":   {"binance": None,        "okx": None, "bybit": "MONUSDT"},  # Bybit API
}

# BTC is the benchmark — fetched separately
BTC_SYMBOL = {"binance": "BTCUSDT", "okx": "BTC-USDT"}

# Binance / OKX / Bybit base URLs
BINANCE_SPOT_URL = "https://api.binance.com"
OKX_URL = "https://www.okx.com"
BYBIT_URL = "https://api.bybit.com"

# Cache TTL in seconds (30 minutes — daily data, no need for frequent refresh)
CACHE_TTL = 1800
