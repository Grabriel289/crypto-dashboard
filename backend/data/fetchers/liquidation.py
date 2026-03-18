"""BTC Liquidation Heatmap fetcher - Real-time from Binance with rate limiting."""
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from data.utils.rate_limiter import binance_rate_limiter
from data.utils.http_session import create_session


class LiquidationFetcher:
    """Fetch liquidation heatmap data from Binance Futures with rate limiting and caching."""
    
    BINANCE_FUTURES = "https://fapi.binance.com"
    BINANCE_SPOT = "https://api.binance.com"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()
        # Cache for fragility data (5 minute TTL to reduce API calls)
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if not expired."""
        if key in self._cache:
            cached_time, ttl, data = self._cache[key]
            if (datetime.utcnow() - cached_time).seconds < ttl:
                print(f"[Heatmap] Using cached data ({(datetime.utcnow() - cached_time).seconds}s old, ttl={ttl}s)")
                return data
        return None

    def _set_cached(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None):
        """Cache data with timestamp. Uses data['_cache_ttl'] if set, else default TTL."""
        effective_ttl = ttl or data.pop('_cache_ttl', None) or self._cache_ttl
        self._cache[key] = (datetime.utcnow(), effective_ttl, data)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            async with self._session_lock:
                if self.session is None or self.session.closed:
                    self.session = create_session()
        return self.session
    
    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _fetch_price(self, symbol: str = "BTCUSDT", futures: bool = True) -> Optional[float]:
        """Fetch current price from Binance with rate limiting."""
        async def _do_fetch():
            try:
                session = await self._get_session()
                if futures:
                    url = f"{self.BINANCE_FUTURES}/fapi/v1/ticker/price"
                    endpoint = "fapi/v1/ticker/price"
                else:
                    url = f"{self.BINANCE_SPOT}/api/v3/ticker/price"
                    endpoint = "api/v3/ticker/price"
                
                async with session.get(url, params={"symbol": symbol}, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return float(data["price"])
                    elif resp.status == 429:
                        raise Exception(f"429 Too Many Requests for {endpoint}")
                    return None
            except Exception as e:
                raise e
        
        try:
            return await binance_rate_limiter.execute_with_retry(
                _do_fetch, 
                endpoint="ticker/price"
            )
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def fetch_open_interest(self, symbol: str = "BTCUSDT") -> Optional[Dict[str, Any]]:
        """Fetch open interest from Binance Futures with rate limiting."""
        async def _do_fetch():
            session = await self._get_session()
            url = f"{self.BINANCE_FUTURES}/fapi/v1/openInterest"
            
            async with session.get(url, params={"symbol": symbol}, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "symbol": data["symbol"],
                        "openInterest": float(data["openInterest"]),
                        "time": data["time"]
                    }
                elif resp.status == 429:
                    raise Exception("429 Too Many Requests for openInterest")
                return None
        
        try:
            return await binance_rate_limiter.execute_with_retry(
                _do_fetch,
                endpoint="openInterest"
            )
        except Exception as e:
            print(f"Error fetching OI for {symbol}: {e}")
            return None
    
    async def fetch_funding_rate(self, symbol: str = "BTCUSDT") -> Optional[Dict[str, Any]]:
        """Fetch current funding rate with rate limiting."""
        async def _do_fetch():
            session = await self._get_session()
            url = f"{self.BINANCE_FUTURES}/fapi/v1/premiumIndex"
            
            async with session.get(url, params={"symbol": symbol}, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "symbol": data["symbol"],
                        "markPrice": float(data["markPrice"]),
                        "lastFundingRate": float(data["lastFundingRate"]),
                        "nextFundingTime": data["nextFundingTime"]
                    }
                elif resp.status == 429:
                    raise Exception("429 Too Many Requests for premiumIndex")
                return None
        
        try:
            return await binance_rate_limiter.execute_with_retry(
                _do_fetch,
                endpoint="premiumIndex"
            )
        except Exception as e:
            print(f"Error fetching funding for {symbol}: {e}")
            return None
    
    async def fetch_funding_history(self, symbol: str = "BTCUSDT", limit: int = 21) -> List[float]:
        """Fetch funding rate history for 7 days with rate limiting."""
        async def _do_fetch():
            session = await self._get_session()
            url = f"{self.BINANCE_FUTURES}/fapi/v1/fundingRate"
            
            async with session.get(url, params={"symbol": symbol, "limit": limit}, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [float(r["fundingRate"]) for r in data]
                elif resp.status == 429:
                    raise Exception("429 Too Many Requests for fundingRate")
                return []
        
        try:
            return await binance_rate_limiter.execute_with_retry(
                _do_fetch,
                endpoint="fundingRate"
            )
        except Exception as e:
            print(f"Error fetching funding history for {symbol}: {e}")
            return []
    
    async def fetch_prices(self, symbol: str = "BTCUSDT") -> Optional[Dict[str, float]]:
        """Fetch both spot and perpetual prices with rate limiting."""
        try:
            # Use gather with semaphore to prevent too many concurrent requests
            sem = asyncio.Semaphore(2)
            
            async def fetch_perp():
                async with sem:
                    return await self._fetch_price(symbol, futures=True)
            
            async def fetch_spot():
                async with sem:
                    return await self._fetch_price(symbol, futures=False)
            
            perp_price, spot_price = await asyncio.gather(
                fetch_perp(),
                fetch_spot(),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(perp_price, Exception) or perp_price is None:
                return None
            if isinstance(spot_price, Exception) or spot_price is None:
                return None
            
            return {
                "spot": spot_price,
                "perp": perp_price,
                "basis": perp_price - spot_price,
                "basis_pct": (perp_price - spot_price) / spot_price * 100
            }
        except Exception as e:
            print(f"Error fetching prices for {symbol}: {e}")
            return None
    
    async def fetch_orderbook_depth(self, symbol: str = "BTCUSDT", limit: int = 1000) -> Optional[Dict[str, Any]]:
        """Fetch order book depth with rate limiting."""
        async def _do_fetch():
            session = await self._get_session()
            url = f"{self.BINANCE_FUTURES}/fapi/v1/depth"
            
            async with session.get(url, params={"symbol": symbol, "limit": limit}, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "bids": [[float(p), float(q)] for p, q in data["bids"]],
                        "asks": [[float(p), float(q)] for p, q in data["asks"]],
                        "lastUpdateId": data["lastUpdateId"]
                    }
                elif resp.status == 429:
                    raise Exception("429 Too Many Requests for depth")
                return None
        
        try:
            return await binance_rate_limiter.execute_with_retry(
                _do_fetch,
                endpoint="depth"
            )
        except Exception as e:
            print(f"Error fetching depth for {symbol}: {e}")
            return None
    
    async def get_heatmap(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """
        Get complete liquidation heatmap with fragility score.

        Resilient: fetches all data in parallel, calculates each fragility
        component independently.  Partial data still produces a live score
        (missing components get neutral defaults instead of full fallback).
        """
        from scoring.fragility import (
            calculate_L_d, calculate_F_sigma, calculate_B_z,
            calculate_depth_2pct
        )
        from analysis.liquidation_heatmap import (
            estimate_liquidation_heatmap, get_major_liquidation_zones,
            generate_heatmap_insight
        )

        # Check cache first
        cache_key = f"heatmap_{symbol}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        print(f"[Heatmap] Starting parallel fetch for {symbol}...")

        # Fetch all 5 data sources in parallel (no sequential waits)
        oi_data, funding_data, prices, depth, funding_history = await asyncio.gather(
            self.fetch_open_interest(symbol),
            self.fetch_funding_rate(symbol),
            self.fetch_prices(symbol),
            self.fetch_orderbook_depth(symbol, limit=500),  # 500 instead of 1000 = weight 5 vs 10
            self.fetch_funding_history(symbol),
            return_exceptions=True
        )

        # Treat exceptions as None
        if isinstance(oi_data, Exception):
            print(f"[Heatmap] OI exception: {oi_data}")
            oi_data = None
        if isinstance(funding_data, Exception):
            print(f"[Heatmap] Funding exception: {funding_data}")
            funding_data = None
        if isinstance(prices, Exception):
            print(f"[Heatmap] Prices exception: {prices}")
            prices = None
        if isinstance(depth, Exception):
            print(f"[Heatmap] Depth exception: {depth}")
            depth = None
        if isinstance(funding_history, Exception):
            print(f"[Heatmap] Funding history exception: {funding_history}")
            funding_history = []

        ok = [k for k, v in {"OI": oi_data, "funding": funding_data, "prices": prices, "depth": depth}.items() if v]
        fail = [k for k, v in {"OI": oi_data, "funding": funding_data, "prices": prices, "depth": depth}.items() if not v]
        print(f"[Heatmap] OK: {ok}  FAILED: {fail}")

        # We need at least prices OR funding to do anything useful
        has_price = prices is not None
        has_funding = funding_data is not None

        if not has_price and not has_funding:
            print(f"[Heatmap] No price or funding data — full fallback")
            fallback = self._get_fallback_data(symbol)
            fallback["_cache_ttl"] = 60
            self._set_cached(cache_key, fallback)
            return fallback

        # Derive current price from whatever we have
        if has_price:
            current_price = prices["perp"]
            spot_price = prices["spot"]
        else:
            current_price = funding_data.get("markPrice", 0)
            spot_price = current_price  # approximate

        # --- Calculate each fragility component independently ---
        live_components = []

        # L_d: needs OI + depth + price
        if oi_data and depth and current_price > 0:
            oi_usd = oi_data["openInterest"] * current_price
            mid_price = (spot_price + current_price) / 2
            depth_2pct = calculate_depth_2pct(depth["bids"], depth["asks"], mid_price)
            L_d = calculate_L_d(oi_usd, depth_2pct)
            live_components.append("L_d")
            print(f"[Heatmap] L_d={L_d:.1f} (OI=${oi_usd/1e9:.2f}B, depth=${depth_2pct/1e6:.1f}M)")
        elif oi_data and current_price > 0:
            # Have OI but no depth — estimate L_d from OI alone (moderate assumption)
            oi_usd = oi_data["openInterest"] * current_price
            L_d = min(100.0, oi_usd / (200e6 * 10))  # assume ~$200M depth
            live_components.append("L_d~")
            print(f"[Heatmap] L_d={L_d:.1f} (estimated, no depth)")
        else:
            oi_usd = 0
            depth_2pct = 0
            L_d = 50.0  # neutral default

        # F_sigma: needs funding + history
        if has_funding:
            funding_rate = funding_data["lastFundingRate"]
            hist = funding_history if funding_history else [funding_rate] * 7
            F_sigma = calculate_F_sigma(funding_rate, hist)
            live_components.append("F_sigma")
            print(f"[Heatmap] F_sigma={F_sigma:.1f} (rate={funding_rate:.6f})")
        else:
            funding_rate = 0.0
            F_sigma = 50.0  # neutral default

        # B_z: needs spot + perp prices
        if has_price:
            B_z = calculate_B_z(spot_price, current_price)
            live_components.append("B_z")
            print(f"[Heatmap] B_z={B_z:.1f} (basis={prices.get('basis_pct', 0):.4f}%)")
        else:
            B_z = 50.0  # neutral default

        # --- Composite fragility score ---
        phi = (L_d + F_sigma + B_z) / 3

        if phi <= 25:
            level, emoji, color = "Stable", "🟢", "#00ff88"
        elif phi <= 50:
            level, emoji, color = "Caution", "🟡", "#ffaa00"
        elif phi <= 75:
            level, emoji, color = "Fragile", "🟠", "#ff6b35"
        else:
            level, emoji, color = "Critical", "🔴", "#ff4444"

        fragility = {
            "score": round(phi, 1),
            "level": level,
            "emoji": emoji,
            "color": color,
            "components": {
                "L_d": {"value": round(L_d, 1), "label": "Liquidation Density"},
                "F_sigma": {"value": round(F_sigma, 1), "label": "Funding Deviation"},
                "B_z": {"value": round(B_z, 1), "label": "Basis Tension"}
            },
            "live_components": live_components,
            "formula": "Phi = (L_d + F_sigma + B_z) / 3"
        }

        # --- Liquidation heatmap (needs OI + funding + price) ---
        if oi_usd > 0 and current_price > 0:
            heatmap = estimate_liquidation_heatmap(current_price, oi_usd, funding_rate)
            major_zones = get_major_liquidation_zones(heatmap, current_price)
        else:
            heatmap = {"long_liquidations": {}, "short_liquidations": {},
                       "total_long_at_risk": 0, "total_short_at_risk": 0,
                       "data_type": "PARTIAL", "disclaimer": "Insufficient data for liquidation estimates"}
            major_zones = []

        # --- Insight ---
        insight = generate_heatmap_insight(phi, heatmap, current_price) if current_price > 0 else {
            "emoji": emoji, "summary": f"{level}: Partial data", "details": [], "recommendation": "Check API connectivity"
        }

        # Mark source based on how many components are live
        source = "binance_live" if len(live_components) >= 2 else "binance_partial"

        result = {
            "symbol": symbol,
            "current_price": current_price,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "fragility": fragility,
            "estimated_liquidations": heatmap,
            "major_zones": major_zones[:5],
            "insight": insight
        }

        print(f"[Heatmap] Done! score={phi:.1f} ({level}), source={source}, live={live_components}")

        # Cache: 5min for live, 2min for partial
        ttl = 300 if source == "binance_live" else 120
        self._set_cached(cache_key, result, ttl=ttl)
        return result
    
    def _get_fallback_data(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Get estimated data when live data fails."""
        current_price = 95000  # Approximate current BTC price
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "estimated_fallback",
            "fragility": {
                "score": 45.0,
                "level": "Caution",
                "emoji": "🟡",
                "color": "#ffaa00",
                "components": {
                    "L_d": {"value": 40.0, "label": "Liquidation Density"},
                    "F_sigma": {"value": 50.0, "label": "Funding Deviation"},
                    "B_z": {"value": 45.0, "label": "Basis Tension"}
                }
            },
            "estimated_liquidations": {
                "long_liquidations": {
                    90000: 1.5e9,
                    85000: 2.8e9,
                    80000: 3.2e9,
                    75000: 2.1e9
                },
                "short_liquidations": {
                    100000: 1.2e9,
                    105000: 2.1e9,
                    110000: 1.8e9,
                    115000: 0.9e9
                },
                "total_long_at_risk": 9.6e9,
                "total_short_at_risk": 6.0e9,
                "data_type": "ESTIMATED_FALLBACK",
                "disclaimer": "Using fallback estimates - live data temporarily unavailable"
            },
            "major_zones": [
                {"price": 80000, "usd_value": 3.2e9, "side": "LONG", "distance_pct": 15.8},
                {"price": 85000, "usd_value": 2.8e9, "side": "LONG", "distance_pct": 10.5}
            ],
            "insight": {
                "emoji": "🟡",
                "summary": "CAUTION: Using estimated data",
                "details": ["Live data temporarily unavailable"],
                "recommendation": "Check connection to Binance API"
            }
        }
    
    async def get_multi_heatmap(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Get heatmap for multiple symbols with rate limiting between calls."""
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        results = {}
        for i, symbol in enumerate(symbols):
            results[symbol] = await self.get_heatmap(symbol)
            # Add delay between symbols to avoid rate limits
            if i < len(symbols) - 1:
                await asyncio.sleep(1.0)
        
        return {
            "symbols": results,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
liquidation_fetcher = LiquidationFetcher()
