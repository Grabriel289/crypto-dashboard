"""Sector definitions and coin mappings."""

# Sector definitions with coins
SECTORS = {
    "AI": {
        "coins": ["RENDER", "TAO", "FET", "VIRTUAL", "WLD", "ZORA"],
        "description": "AI & Compute tokens"
    },
    "DeFi": {
        "coins": ["UNI", "AAVE", "SKY", "AERO", "JUP", "SYRUP", "PENDLE", "ENA", "ETHFI", "WLFI"],
        "description": "Decentralized Finance"
    },
    "L1": {
        "coins": ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "NEAR", "SEI", "APT", "SUI", "TON", "TRX", "MON"],
        "description": "Layer 1 Blockchains"
    },
    "Privacy": {
        "coins": ["ZEC", "XMR"],
        "description": "Privacy coins"
    },
    "L2": {
        "coins": ["ARB", "OP", "STK"],
        "description": "Layer 2 Scaling"
    },
    "RWA": {
        "coins": ["PAXG", "ONDO"],
        "description": "Real World Assets"
    },
    "Meme": {
        "coins": ["DOGE", "PEPE", "SHIB", "PENGU", "BONK", "PUMP"],
        "description": "Meme coins"
    },
    "PERP": {
        "coins": ["HYPE", "LIT", "ASTER"],
        "description": "Perpetual DEX tokens"
    }
}

# Symbol mapping per exchange
SYMBOL_MAPPING = {
    "binance": {
        "BTC": "BTCUSDT",
        "ETH": "ETHUSDT",
        "SOL": "SOLUSDT",
        "BNB": "BNBUSDT",
        "XRP": "XRPUSDT",
        "ADA": "ADAUSDT",
        "DOGE": "DOGEUSDT",
        "RENDER": "RENDERUSDT",
        "TAO": "TAOUSDT",
        "FET": "FETUSDT",
        "WLD": "WLDUSDT",
        "UNI": "UNIUSDT",
        "AAVE": "AAVEUSDT",
        "PENDLE": "PENDLEUSDT",
        "NEAR": "NEARUSDT",
        "APT": "APTUSDT",
        "SUI": "SUIUSDT",
        "ARB": "ARBUSDT",
        "OP": "OPUSDT",
        "PEPE": "PEPEUSDT",
        "SHIB": "SHIBUSDT",
        "BONK": "BONKUSDT",
        "ZEC": "ZECUSDT",
        "XMR": "XMRUSDT",
        "TRX": "TRXUSDT",
        "TON": "TONUSDT",
        "ONDO": "ONDOUSDT",
        "PAXG": "PAXGUSDT",
        "JUP": "JUPUSDT",
        "ENA": "ENAUSDT",
    },
    "okx": {
        "BTC": "BTC-USDT",
        "ETH": "ETH-USDT",
        "SOL": "SOL-USDT",
        "BNB": "BNB-USDT",
        "XRP": "XRP-USDT",
        "ADA": "ADA-USDT",
        "DOGE": "DOGE-USDT",
        "RENDER": "RENDER-USDT",
        "TAO": "TAO-USDT",
        "FET": "FET-USDT",
        "VIRTUAL": "VIRTUAL-USDT",
        "WLD": "WLD-USDT",
        "UNI": "UNI-USDT",
        "AAVE": "AAVE-USDT",
        "NEAR": "NEAR-USDT",
        "APT": "APT-USDT",
        "SUI": "SUI-USDT",
        "ARB": "ARB-USDT",
        "OP": "OP-USDT",
        "PEPE": "PEPE-USDT",
        "SHIB": "SHIB-USDT",
        "BONK": "BONK-USDT",
        "ZEC": "ZEC-USDT",
        "TRX": "TRX-USDT",
        "TON": "TON-USDT",
        "ONDO": "ONDO-USDT",
        "PAXG": "PAXG-USDT",
        "JUP": "JUP-USDT",
        "HYPE": "HYPE-USDT",
    },
    "kucoin": {
        "BTC": "BTC-USDT",
        "ETH": "ETH-USDT",
        "SOL": "SOL-USDT",
        "XRP": "XRP-USDT",
        "ADA": "ADA-USDT",
        "DOGE": "DOGE-USDT",
        "RENDER": "RENDER-USDT",
        "FET": "FET-USDT",
        "WLD": "WLD-USDT",
        "UNI": "UNI-USDT",
        "AAVE": "AAVE-USDT",
        "NEAR": "NEAR-USDT",
        "APT": "APT-USDT",
        "SUI": "SUI-USDT",
        "ARB": "ARB-USDT",
        "OP": "OP-USDT",
        "PEPE": "PEPE-USDT",
        "SHIB": "SHIB-USDT",
        "ZEC": "ZEC-USDT",
        "XMR": "XMR-USDT",
        "TRX": "TRX-USDT",
        "HYPE": "HYPE-USDT",
    },
    "coinbase": {
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "SOL": "SOL-USD",
        "XRP": "XRP-USD",
        "ADA": "ADA-USD",
        "DOGE": "DOGE-USD",
    }
}

# Priority order for exchanges
EXCHANGE_PRIORITY = ["binance", "okx", "kucoin", "coinbase"]
