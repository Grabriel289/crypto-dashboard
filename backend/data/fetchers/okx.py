"""OKX data fetcher."""
import aiohttp
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


# Singleton instance
okx_fetcher = OKXFetcher()
