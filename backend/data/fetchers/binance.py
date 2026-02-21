"""Binance data fetcher."""
import aiohttp
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime


BINANCE_SPOT_URL = "https://api.binance.com"
BINANCE_FUTURES_URL = "https://fapi.binance.com"


class BinanceFetcher:
    """Fetch data from Binance API."""
    
    async def fetch_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch 24h price data from Binance spot."""
        url = f"{BINANCE_SPOT_URL}/api/v3/ticker/24hr?symbol={symbol}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    return {
                        "price": float(data["lastPrice"]),
                        "change_24h": float(data["priceChangePercent"]),
                        "volume_24h": float(data["quoteVolume"]),
                        "high_24h": float(data["highPrice"]),
                        "low_24h": float(data["lowPrice"]),
                        "source": "binance"
                    }
            except Exception as e:
                print(f"Binance price fetch error for {symbol}: {e}")
                return None
    
    async def fetch_klines(self, symbol: str, interval: str = "1d", limit: int = 30) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data."""
        url = f"{BINANCE_SPOT_URL}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    df = pd.DataFrame(data, columns=[
                        "open_time", "open", "high", "low", "close", "volume",
                        "close_time", "quote_volume", "trades", "taker_buy_base",
                        "taker_buy_quote", "ignore"
                    ])
                    df["close"] = df["close"].astype(float)
                    df["volume"] = df["volume"].astype(float)
                    df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
                    return df
            except Exception as e:
                print(f"Binance klines fetch error for {symbol}: {e}")
                return None
    
    async def fetch_funding_rate(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current funding rate."""
        url = f"{BINANCE_FUTURES_URL}/fapi/v1/fundingRate?symbol={symbol}&limit=1"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    if data:
                        return {
                            "symbol": symbol,
                            "funding_rate": float(data[0]["fundingRate"]),
                            "funding_time": datetime.fromtimestamp(data[0]["fundingTime"] / 1000),
                            "source": "binance"
                        }
                    return None
            except Exception as e:
                print(f"Binance funding fetch error for {symbol}: {e}")
                return None
    
    async def fetch_open_interest(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch open interest."""
        url = f"{BINANCE_FUTURES_URL}/fapi/v1/openInterest?symbol={symbol}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    return {
                        "symbol": symbol,
                        "open_interest": float(data["openInterest"]),
                        "source": "binance"
                    }
            except Exception as e:
                print(f"Binance OI fetch error for {symbol}: {e}")
                return None


# Singleton instance
binance_fetcher = BinanceFetcher()
