"""Binance data fetcher with improved 7D return calculation."""
import aiohttp
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


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
    
    async def fetch_7d_return(self, symbol: str) -> Optional[float]:
        """
        Calculate actual 7-day return using historical price data.
        Fetches price from 7 days ago and compares to current price.
        """
        try:
            # Get current price
            current_data = await self.fetch_price(symbol)
            if not current_data:
                return None
            current_price = current_data["price"]
            
            # Get historical price from 7 days ago using klines
            # Need 8 days to get the close price from exactly 7 days ago
            df = await self.fetch_klines(symbol, interval="1d", limit=8)
            if df is None or len(df) < 8:
                return None
            
            # Price from 7 days ago (first candle in the 8-day window)
            price_7d_ago = df["close"].iloc[0]
            
            # Calculate actual return
            return_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
            
            return return_7d
            
        except Exception as e:
            print(f"Error calculating 7d return for {symbol}: {e}")
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
