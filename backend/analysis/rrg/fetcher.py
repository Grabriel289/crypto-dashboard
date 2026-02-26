"""Yahoo Finance data fetcher for RRG."""
import aiohttp
import asyncio
from typing import Dict, List, Optional, Tuple
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
    
    def _resample_to_weekly(self, timestamps: List[int], prices: List[float]) -> List[float]:
        """
        Resample daily data to weekly closing prices.
        Takes the last available price of each week (typically Friday).
        
        Args:
            timestamps: List of Unix timestamps
            prices: List of prices corresponding to timestamps
            
        Returns:
            List of weekly closing prices (oldest first)
        """
        if not timestamps or not prices or len(timestamps) != len(prices):
            return []
        
        weekly_prices = []
        current_week = None
        current_week_price = None
        
        for ts, price in zip(timestamps, prices):
            if price is None:
                continue
            
            # Convert timestamp to datetime
            dt = datetime.fromtimestamp(ts)
            # Get ISO calendar week (year, week number, weekday)
            week_key = dt.isocalendar()[:2]  # (year, week number)
            
            if week_key != current_week:
                # New week - save previous week's close
                if current_week_price is not None:
                    weekly_prices.append(current_week_price)
                current_week = week_key
            
            # Update current week's latest price
            current_week_price = price
        
        # Don't forget the last week
        if current_week_price is not None:
            weekly_prices.append(current_week_price)
        
        return weekly_prices
    
    async def fetch_prices(self, symbol: str, days: int = HISTORY_DAYS) -> Optional[List[float]]:
        """
        Fetch historical daily prices and resample to weekly.
        
        Args:
            symbol: ETF ticker symbol
            days: Number of days of history (fetches more to ensure enough weeks)
            
        Returns:
            List of weekly closing prices (oldest first)
        """
        cache_key = f"{symbol}_weekly_{days}"
        
        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if (datetime.now() - cached_time).seconds < self._cache_ttl:
                return cached_data
        
        try:
            session = await self._get_session()
            
            # Calculate date range - fetch extra days to ensure enough weeks
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days * 2)  # 2x to ensure enough trading days
            
            # Build URL
            period1 = int(start_date.timestamp())
            period2 = int(end_date.timestamp())
            
            url = f"{YAHOO_BASE_URL}/{symbol}"
            params = {
                "period1": period1,
                "period2": period2,
                "interval": "1d",  # Fetch daily
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
                
                # Extract data
                result = data.get("chart", {}).get("result", [{}])[0]
                timestamps = result.get("timestamp", [])
                prices = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
                
                if not prices or len(prices) < 20:
                    return None
                
                # Resample to weekly
                weekly_prices = self._resample_to_weekly(timestamps, prices)
                
                # Need at least 16 weeks for RRG calculation (10 + 6)
                if len(weekly_prices) < 16:
                    print(f"Not enough weekly data for {symbol}: {len(weekly_prices)} weeks")
                    return None
                
                # Cache result
                self._cache[cache_key] = (datetime.now(), weekly_prices)
                
                return weekly_prices
                
        except Exception as e:
            print(f"Error fetching prices for {symbol}: {e}")
            return None
    
    async def fetch_all_symbols(self) -> Dict[str, List[float]]:
        """
        Fetch weekly prices for all tracked symbols.
        
        Returns:
            Dict mapping symbol to weekly closing prices
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
