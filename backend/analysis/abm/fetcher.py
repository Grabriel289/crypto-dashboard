"""Binance / OKX kline fetcher for Altcoin Breadth Momentum universe."""
import aiohttp
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .constants import (
    ABM_UNIVERSE, BTC_SYMBOL, KLINE_LIMIT,
    BINANCE_SPOT_URL, OKX_URL, CACHE_TTL,
)


class ABMDataFetcher:
    """
    Fetches daily close prices for the 50-altcoin ABM universe + BTC.

    Exchange priority: Binance first, OKX fallback.
    Results are cached for CACHE_TTL seconds (30 min).
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Tuple[datetime, List[Dict]]] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    # ------------------------------------------------------------------
    # Low-level kline fetch
    # ------------------------------------------------------------------

    async def _fetch_binance_klines(
        self, symbol: str, limit: int = KLINE_LIMIT
    ) -> Optional[List[Dict]]:
        """Fetch daily klines from Binance. Returns list of {date, close}."""
        session = await self._get_session()
        url = f"{BINANCE_SPOT_URL}/api/v3/klines"
        params = {"symbol": symbol, "interval": "1d", "limit": limit}

        try:
            async with session.get(url, params=params, timeout=15) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return [
                    {
                        "date": datetime.utcfromtimestamp(c[0] / 1000).strftime("%Y-%m-%d"),
                        "close": float(c[4]),
                    }
                    for c in data
                ]
        except Exception as e:
            print(f"[ABM] Binance kline error {symbol}: {e}")
            return None

    async def _fetch_okx_klines(
        self, symbol: str, limit: int = KLINE_LIMIT
    ) -> Optional[List[Dict]]:
        """Fetch daily klines from OKX. Returns list of {date, close} oldest-first."""
        session = await self._get_session()
        url = f"{OKX_URL}/api/v5/market/history-candles"
        params = {"instId": symbol, "bar": "1D", "limit": str(limit)}

        try:
            async with session.get(url, params=params, timeout=15) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != "0":
                    return None
                candles = data.get("data", [])
                if not candles:
                    return None
                # OKX returns newest first — reverse to oldest-first
                candles.reverse()
                return [
                    {
                        "date": datetime.utcfromtimestamp(int(c[0]) / 1000).strftime("%Y-%m-%d"),
                        "close": float(c[4]),
                    }
                    for c in candles
                ]
        except Exception as e:
            print(f"[ABM] OKX kline error {symbol}: {e}")
            return None

    # ------------------------------------------------------------------
    # Single-coin fetch with exchange fallback
    # ------------------------------------------------------------------

    async def _fetch_coin(self, coin: str, mapping: Dict) -> Optional[List[Dict]]:
        """Fetch klines for one coin, trying Binance then OKX."""
        cache_key = coin
        if cache_key in self._cache:
            ts, cached = self._cache[cache_key]
            if (datetime.now() - ts).total_seconds() < CACHE_TTL:
                return cached

        # Try Binance
        binance_sym = mapping.get("binance")
        if binance_sym:
            result = await self._fetch_binance_klines(binance_sym)
            if result and len(result) >= 30:
                self._cache[cache_key] = (datetime.now(), result)
                return result

        # Fallback to OKX
        okx_sym = mapping.get("okx")
        if okx_sym:
            result = await self._fetch_okx_klines(okx_sym)
            if result and len(result) >= 30:
                self._cache[cache_key] = (datetime.now(), result)
                return result

        return None

    # ------------------------------------------------------------------
    # Fetch all coins
    # ------------------------------------------------------------------

    async def fetch_all(self) -> Dict[str, List[Dict]]:
        """
        Fetch daily klines for all 50 altcoins + BTC.

        Returns:
            Dict mapping coin ticker → list of {date, close} dicts (oldest first).
        """
        results: Dict[str, List[Dict]] = {}

        # Fetch BTC first (always needed as benchmark)
        btc_data = await self._fetch_coin("BTC", BTC_SYMBOL)
        if btc_data:
            results["BTC"] = btc_data

        # Fetch altcoins with staggered requests
        for coin, mapping in ABM_UNIVERSE.items():
            data = await self._fetch_coin(coin, mapping)
            if data:
                results[coin] = data
            await asyncio.sleep(0.05)  # 50ms stagger to respect rate limits

        fetched = len(results) - (1 if "BTC" in results else 0)
        print(f"[ABM] Fetched {fetched}/50 altcoins + BTC")
        return results
