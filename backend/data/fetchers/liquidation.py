"""BTC Liquidation Heatmap fetcher - Real-time from Binance with rate limiting."""
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from data.utils.rate_limiter import binance_rate_limiter


class LiquidationFetcher:
    """Fetch liquidation heatmap data from Binance Futures with rate limiting."""
    
    BINANCE_FUTURES = "https://fapi.binance.com"
    BINANCE_SPOT = "https://api.binance.com"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            async with self._session_lock:
                if self.session is None or self.session.closed:
                    self.session = aiohttp.ClientSession()
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
        
        This fetches all required data and calculates:
        1. Market Fragility Score (Φ)
        2. Estimated Liquidation Heatmap
        3. Major liquidation zones
        """
        from analysis.liquidation_heatmap import calculate_complete_heatmap
        from scoring.fragility import calculate_depth_2pct
        
        try:
            # Fetch all required data with staggered timing to avoid rate limits
            oi_data = await self.fetch_open_interest(symbol)
            await asyncio.sleep(0.2)  # Small delay between requests
            
            funding_data = await self.fetch_funding_rate(symbol)
            await asyncio.sleep(0.2)
            
            prices = await self.fetch_prices(symbol)
            await asyncio.sleep(0.2)
            
            depth = await self.fetch_orderbook_depth(symbol)
            await asyncio.sleep(0.2)
            
            # Fetch funding history (needed for F_sigma)
            funding_history = await self.fetch_funding_history(symbol)
            
            # Check if we have all required data
            if not all([oi_data, funding_data, prices, depth]):
                missing = []
                if not oi_data: missing.append("OI")
                if not funding_data: missing.append("funding")
                if not prices: missing.append("prices")
                if not depth: missing.append("depth")
                print(f"[Heatmap] Missing data for {symbol}: {missing}, using fallback")
                return self._get_fallback_data(symbol)
            
            # Calculate OI in USD
            oi_usd = oi_data["openInterest"] * prices["perp"]
            
            # Calculate depth within 2%
            mid_price = (prices["spot"] + prices["perp"]) / 2
            depth_2pct = calculate_depth_2pct(depth["bids"], depth["asks"], mid_price)
            
            # Calculate complete heatmap
            result = calculate_complete_heatmap(
                current_price=prices["perp"],
                oi_usd=oi_usd,
                funding_rate=funding_data["lastFundingRate"],
                depth_2pct=depth_2pct,
                funding_7d=funding_history if funding_history else [funding_data["lastFundingRate"]] * 7,
                spot_price=prices["spot"],
                perp_price=prices["perp"]
            )
            
            result["timestamp"] = datetime.utcnow().isoformat()
            result["source"] = "binance_live"
            
            return result
            
        except Exception as e:
            print(f"Error calculating heatmap for {symbol}: {e}")
            return self._get_fallback_data(symbol)
    
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
