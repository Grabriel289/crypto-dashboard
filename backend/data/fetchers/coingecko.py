"""CoinGecko data fetcher - for coins not on major exchanges."""
import aiohttp
from typing import Optional, Dict, Any


COINGECKO_URL = "https://api.coingecko.com/api/v3"


class CoinGeckoFetcher:
    """Fetch data from CoinGecko API (free tier)."""
    
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
    
    async def fetch_price(self, coin: str) -> Optional[Dict[str, Any]]:
        """Fetch price data from CoinGecko."""
        coin_id = self.COIN_IDS.get(coin)
        if not coin_id:
            return None
        
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
                    if response.status != 200:
                        return None
                    data = await response.json()
                    coin_data = data.get(coin_id, {})
                    
                    if not coin_data:
                        return None
                    
                    return {
                        "price": float(coin_data.get("usd", 0)),
                        "change_24h": float(coin_data.get("usd_24h_change", 0)),
                        "volume_24h": float(coin_data.get("usd_24h_vol", 0)),
                        "source": "coingecko"
                    }
            except Exception as e:
                print(f"CoinGecko price fetch error for {coin}: {e}")
                return None
    
    async def fetch_7d_change(self, coin: str) -> Optional[float]:
        """Fetch 7-day price change percentage."""
        coin_id = self.COIN_IDS.get(coin)
        if not coin_id:
            return None
        
        url = f"{COINGECKO_URL}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "7",
            "interval": "daily"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    prices = data.get("prices", [])
                    
                    if len(prices) < 2:
                        return None
                    
                    # prices format: [[timestamp, price], ...]
                    price_7d_ago = prices[0][1]
                    current_price = prices[-1][1]
                    
                    change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
                    return change_7d
            except Exception as e:
                print(f"CoinGecko 7d fetch error for {coin}: {e}")
                return None


# Singleton instance
coingecko_fetcher = CoinGeckoFetcher()
