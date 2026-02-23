"""OKX data fetcher."""
import aiohttp
import pandas as pd
from typing import Optional, Dict, Any


OKX_URL = "https://www.okx.com"


class OKXFetcher:
    """Fetch data from OKX API."""
    
    async def fetch_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch price data from OKX."""
        url = f"{OKX_URL}/api/v5/market/ticker?instId={symbol}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    if data.get("code") != "0":
                        return None
                    ticker = data["data"][0]
                    return {
                        "price": float(ticker.get("last", 0)),
                        "change_24h": float(ticker.get("chg24h", 0)) * 100,
                        "volume_24h": float(ticker.get("vol24h", 0)),
                        "high_24h": float(ticker.get("high24h", 0)),
                        "low_24h": float(ticker.get("low24h", 0)),
                        "source": "okx"
                    }
            except Exception as e:
                print(f"OKX price fetch error for {symbol}: {e}")
                return None
    
    async def fetch_klines(self, symbol: str, interval: str = "1D", limit: int = 8) -> Optional[pd.DataFrame]:
        """Fetch candlestick data from OKX.
        
        Args:
            symbol: Trading pair (e.g., "BTC-USDT")
            interval: Bar interval (1D, 1H, etc.)
            limit: Number of candles
        """
        url = f"{OKX_URL}/api/v5/market/history-candles"
        params = {
            "instId": symbol,
            "bar": interval,
            "limit": limit
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    if data.get("code") != "0":
                        return None
                    
                    candles = data.get("data", [])
                    if not candles:
                        return None
                    
                    # OKX format: [ts, o, h, l, c, vol, volCcy]
                    df = pd.DataFrame(candles, columns=[
                        "timestamp", "open", "high", "low", "close", "volume", "vol_ccy"
                    ])
                    df["close"] = df["close"].astype(float)
                    df["volume"] = df["volume"].astype(float)
                    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit='ms')
                    
                    # Reverse to get chronological order (oldest first)
                    df = df.iloc[::-1].reset_index(drop=True)
                    
                    return df
            except Exception as e:
                print(f"OKX klines fetch error for {symbol}: {e}")
                return None


# Singleton instance
okx_fetcher = OKXFetcher()
