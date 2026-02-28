"""Yahoo Finance data fetcher for Accelerating Momentum Rotation Map."""
import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .constants import ETF_SYMBOLS, YAHOO_BASE_URL, HISTORY_DAYS, LONG_PERIOD


class RRGDataFetcher:
    """Fetches daily price data from Yahoo Finance for momentum calculations."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache = {}
        self._cache_ttl = 900  # 15 minutes

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch_prices(self, symbol: str, days: int = HISTORY_DAYS) -> Optional[List[float]]:
        """
        Fetch historical daily closing prices from Yahoo Finance.

        Args:
            symbol: ETF ticker symbol
            days:   Calendar days of history to request

        Returns:
            List of daily closing prices (oldest first), or None on failure.
            Need at least LONG_PERIOD + 1 = 127 data points.
        """
        cache_key = f"{symbol}_daily_{days}"

        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if (datetime.now() - cached_time).seconds < self._cache_ttl:
                return cached_data

        try:
            session = await self._get_session()

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            url = f"{YAHOO_BASE_URL}/{symbol}"
            params = {
                "period1": int(start_date.timestamp()),
                "period2": int(end_date.timestamp()),
                "interval": "1d",
                "events": "history",
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with session.get(url, params=params, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f"Yahoo Finance error for {symbol}: {response.status}")
                    return None

                data = await response.json()

                result = data.get("chart", {}).get("result", [{}])[0]
                raw_prices = (
                    result.get("indicators", {})
                    .get("quote", [{}])[0]
                    .get("close", [])
                )

                # Strip None values (holidays / gaps)
                prices = [p for p in raw_prices if p is not None]

                # Need LONG_PERIOD + 1 points for acceleration calculation
                min_required = LONG_PERIOD + 1
                if len(prices) < min_required:
                    print(
                        f"Not enough daily data for {symbol}: "
                        f"{len(prices)} days (need {min_required})"
                    )
                    return None

                self._cache[cache_key] = (datetime.now(), prices)
                return prices

        except Exception as e:
            print(f"Error fetching prices for {symbol}: {e}")
            return None

    async def fetch_all_symbols(self) -> Dict[str, List[float]]:
        """
        Fetch daily prices for all tracked symbols.

        Returns:
            Dict mapping symbol → list of daily closing prices
        """
        results = {}
        for symbol in ETF_SYMBOLS:
            prices = await self.fetch_prices(symbol)
            if prices:
                results[symbol] = prices
            await asyncio.sleep(0.1)  # gentle rate limit

        return results


# Global instance
rrg_fetcher = RRGDataFetcher()
