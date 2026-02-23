"""CoinGecko data fetcher - for coins not on major exchanges."""
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


COINGECKO_URL = "https://api.coingecko.com/api/v3"


class CoinGeckoFetcher:
    """Fetch data from CoinGecko API (free tier) with caching and rate limiting."""
    
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_request = None
        self._min_interval = 1.2  # Minimum seconds between requests (rate limit)
    
    # CoinGecko IDs for mapping
    COIN_IDS = {
        "HYPE": "hyperliquid",
        "VIRTUAL": "virtual-protocol",
        "ZORA": "zora",
        "SKY": "sky-mavis",
        "SYRUP": "syrup",
        "ETHFI": "ether-fi",
        "WLFI": "world-liberty-financial",
        "PUMP": "pump",
        "LIT": "litentry",
        "ASTER": "aster",
    }
    
    async def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        if self._last_request:
            elapsed = (datetime.now() - self._last_request).total_seconds()
            if elapsed < self._min_interval:
                await asyncio.sleep(self._min_interval - elapsed)
        self._last_request = datetime.now()
    
    async def fetch_price(self, coin: str) -> Optional[Dict[str, Any]]:
        """Fetch price data from CoinGecko with caching."""
        # Check cache
        cache_key = f"price_{coin}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if datetime.now() - cached["time"] < timedelta(seconds=self._cache_ttl):
                return cached["data"]
        
        coin_id = self.COIN_IDS.get(coin)
        if not coin_id:
            return None
        
        await self._rate_limit()
        
        url = f"{COINGECKO_URL}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 429:
                        print(f"CoinGecko rate limit hit for {coin}")
                        return None
                    if response.status != 200:
                        return None
                    data = await response.json()
                    coin_data = data.get(coin_id, {})
                    
                    if not coin_data:
                        return None
                    
                    result = {
                        "price": float(coin_data.get("usd", 0)),
                        "change_24h": float(coin_data.get("usd_24h_change", 0)),
                        "volume_24h": float(coin_data.get("usd_24h_vol", 0)),
                        "source": "coingecko"
                    }
                    
                    # Cache result
                    self._cache[cache_key] = {"data": result, "time": datetime.now()}
                    return result
            except Exception as e:
                print(f"CoinGecko price fetch error for {coin}: {e}")
                return None
    
    async def fetch_7d_change(self, coin: str) -> Optional[float]:
        """Fetch 7-day price change percentage with caching."""
        # Check cache
        cache_key = f"7d_{coin}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if datetime.now() - cached["time"] < timedelta(seconds=self._cache_ttl):
                return cached["data"]
        
        coin_id = self.COIN_IDS.get(coin)
        if not coin_id:
            return None
        
        await self._rate_limit()
        
        url = f"{COINGECKO_URL}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "7",
            "interval": "daily"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 429:
                        print(f"CoinGecko rate limit hit for {coin} 7d")
                        return None
                    if response.status != 200:
                        return None
                    data = await response.json()
                    prices = data.get("prices", [])
                    
                    if len(prices) < 2:
                        return None
                    
                    price_7d_ago = prices[0][1]
                    current_price = prices[-1][1]
                    
                    change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
                    
                    # Cache result
                    self._cache[cache_key] = {"data": change_7d, "time": datetime.now()}
                    return change_7d
            except Exception as e:
                print(f"CoinGecko 7d fetch error for {coin}: {e}")
                return None


# Singleton instance
coingecko_fetcher = CoinGeckoFetcher()
