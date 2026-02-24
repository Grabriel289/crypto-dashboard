"""KuCoin data fetcher - fallback for altcoins not on Binance/OKX."""
import aiohttp
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime


KUCOIN_URL = "https://api.kucoin.com"


class KuCoinFetcher:
    """Fetch data from KuCoin API."""
    
    async def fetch_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch 24h ticker data from KuCoin."""
        url = f"{KUCOIN_URL}/api/v1/market/stats"
        params = {"symbol": symbol}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    
                    if data.get("code") != "200000":
                        return None
                    
                    ticker = data.get("data", {})
                    
                    return {
                        "price": float(ticker.get("last", 0)),
                        "change_24h": float(ticker.get("changeRate", 0)) * 100,  # Convert to percentage
                        "volume_24h": float(ticker.get("volValue", 0)),
                        "high_24h": float(ticker.get("high", 0)),
                        "low_24h": float(ticker.get("low", 0)),
                        "source": "kucoin"
                    }
            except Exception as e:
                print(f"KuCoin price fetch error for {symbol}: {e}")
                return None
    
    async def fetch_klines(self, symbol: str, interval: str = "1day", limit: int = 8) -> Optional[pd.DataFrame]:
        """Fetch candlestick data from KuCoin.
        
        Args:
            symbol: Trading pair (e.g., "BTC-USDT")
            interval: 1min, 3min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
            limit: Number of candles (max 1500)
        """
        url = f"{KUCOIN_URL}/api/v1/market/candles"
        
        # KuCoin uses different format: type=1min, startAt, endAt
        # We need to calculate timestamps
        end_at = int(datetime.now().timestamp())
        
        # Rough estimate for 8 candles based on interval
        interval_seconds = {
            "1min": 60, "3min": 180, "5min": 300, "15min": 900,
            "30min": 1800, "1hour": 3600, "2hour": 7200, "4hour": 14400,
            "6hour": 21600, "8hour": 28800, "12hour": 43200, "1day": 86400,
            "1week": 604800
        }
        seconds = interval_seconds.get(interval, 86400)
        start_at = end_at - (seconds * limit * 2)  # Buffer for safety
        
        params = {
            "symbol": symbol,
            "type": interval,
            "startAt": start_at,
            "endAt": end_at
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    
                    if data.get("code") != "200000":
                        return None
                    
                    candles = data.get("data", [])
                    if not candles or len(candles) < 2:
                        return None
                    
                    # KuCoin format: [timestamp, open, close, high, low, volume, turnover]
                    df = pd.DataFrame(candles, columns=[
                        "timestamp", "open", "close", "high", "low", "volume", "turnover"
                    ])
                    df["close"] = df["close"].astype(float)
                    df["volume"] = df["volume"].astype(float)
                    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit='s')
                    
                    # Sort by timestamp ascending (oldest first)
                    df = df.sort_values("timestamp").reset_index(drop=True)
                    
                    # Take last 'limit' rows
                    if len(df) > limit:
                        df = df.tail(limit).reset_index(drop=True)
                    
                    return df
            except Exception as e:
                print(f"KuCoin klines fetch error for {symbol}: {e}")
                return None


# Singleton instance
kucoin_fetcher = KuCoinFetcher()
