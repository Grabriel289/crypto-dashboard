"""Yahoo Finance data fetcher for RRG."""
import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .constants import ETF_SYMBOLS, YAHOO_BASE_URL, HISTORY_DAYS


class RRGDataFetcher:
    """Fetches price data from Yahoo Finance for RRG calculations."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache = {}
        self._cache_ttl = 900  # 15 minutes
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch_prices(self, symbol: str, days: int = HISTORY_DAYS) -> Optional[List[float]]:
        """
        Fetch historical closing prices for a symbol.
        
        Args:
            symbol: ETF ticker symbol
            days: Number of days of history
            
        Returns:
            List of closing prices (oldest first)
        """
        cache_key = f"{symbol}_{days}"
        
        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if (datetime.now() - cached_time).seconds < self._cache_ttl:
                return cached_data
        
        try:
            session = await self._get_session()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Build URL
            period1 = int(start_date.timestamp())
            period2 = int(end_date.timestamp())
            
            url = f"{YAHOO_BASE_URL}/{symbol}"
            params = {
                "period1": period1,
                "period2": period2,
                "interval": "1d",
                "events": "history"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with session.get(url, params=params, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f"Yahoo Finance error for {symbol}: {response.status}")
                    return None
                
                data = await response.json()
                
                # Extract closing prices
                result = data.get("chart", {}).get("result", [{}])[0]
                timestamps = result.get("timestamp", [])
                prices = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
                
                if not prices or len(prices) < 20:
                    return None
                
                # Filter out None values
                valid_prices = [p for p in prices if p is not None]
                
                # Cache result
                self._cache[cache_key] = (datetime.now(), valid_prices)
                
                return valid_prices
                
        except Exception as e:
            print(f"Error fetching prices for {symbol}: {e}")
            return None
    
    async def fetch_all_symbols(self) -> Dict[str, List[float]]:
        """
        Fetch prices for all tracked symbols.
        
        Returns:
            Dict mapping symbol to closing prices
        """
        symbols = list(ETF_SYMBOLS.keys())
        
        # Fetch concurrently with rate limiting
        results = {}
        for symbol in symbols:
            prices = await self.fetch_prices(symbol)
            if prices:
                results[symbol] = prices
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        return results


# Global instance
rrg_fetcher = RRGDataFetcher()
