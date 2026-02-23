"""BTC Liquidation Heatmap fetcher - Real-time from Binance."""
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class LiquidationFetcher:
    """Fetch liquidation heatmap data from Binance Futures."""
    
    BINANCE_FUTURES = "https://fapi.binance.com"
    BINANCE_SPOT = "https://api.binance.com"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _fetch_price(self, symbol: str = "BTCUSDT", futures: bool = True) -> Optional[float]:
        """Fetch current price from Binance."""
        try:
            session = await self._get_session()
            if futures:
                url = f"{self.BINANCE_FUTURES}/fapi/v1/ticker/price"
            else:
                url = f"{self.BINANCE_SPOT}/api/v3/ticker/price"
            
            async with session.get(url, params={"symbol": symbol}, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return float(data["price"])
                return None
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def fetch_open_interest(self, symbol: str = "BTCUSDT") -> Optional[Dict[str, Any]]:
        """Fetch open interest from Binance Futures."""
        try:
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
                return None
        except Exception as e:
            print(f"Error fetching OI for {symbol}: {e}")
            return None
    
    async def fetch_funding_rate(self, symbol: str = "BTCUSDT") -> Optional[Dict[str, Any]]:
        """Fetch current funding rate."""
        try:
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
                return None
        except Exception as e:
            print(f"Error fetching funding for {symbol}: {e}")
            return None
    
    async def fetch_funding_history(self, symbol: str = "BTCUSDT", limit: int = 21) -> List[float]:
        """Fetch funding rate history for 7 days (21 periods)."""
        try:
            session = await self._get_session()
            url = f"{self.BINANCE_FUTURES}/fapi/v1/fundingRate"
            
            async with session.get(url, params={"symbol": symbol, "limit": limit}, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [float(r["fundingRate"]) for r in data]
                return []
        except Exception as e:
            print(f"Error fetching funding history for {symbol}: {e}")
            return []
    
    async def fetch_prices(self, symbol: str = "BTCUSDT") -> Optional[Dict[str, float]]:
        """Fetch both spot and perpetual prices."""
        try:
            session = await self._get_session()
            
            # Perp price
            perp_url = f"{self.BINANCE_FUTURES}/fapi/v1/ticker/price"
            async with session.get(perp_url, params={"symbol": symbol}, timeout=10) as resp:
                if resp.status != 200:
                    return None
                perp_data = await resp.json()
                perp_price = float(perp_data["price"])
            
            # Spot price
            spot_url = f"{self.BINANCE_SPOT}/api/v3/ticker/price"
            async with session.get(spot_url, params={"symbol": symbol}, timeout=10) as resp:
                if resp.status != 200:
                    return None
                spot_data = await resp.json()
                spot_price = float(spot_data["price"])
            
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
        """Fetch order book depth."""
        try:
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
                return None
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
            # Fetch all required data concurrently
            oi_data, funding_data, prices, depth = await asyncio.gather(
                self.fetch_open_interest(symbol),
                self.fetch_funding_rate(symbol),
                self.fetch_prices(symbol),
                self.fetch_orderbook_depth(symbol)
            )
            
            # Fetch funding history (needed for F_sigma)
            funding_history = await self.fetch_funding_history(symbol)
            
            # Check if we have all required data
            if not all([oi_data, funding_data, prices, depth]):
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
        """Get heatmap for multiple symbols."""
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        results = {}
        for symbol in symbols:
            results[symbol] = await self.get_heatmap(symbol)
        
        return {
            "symbols": results,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
liquidation_fetcher = LiquidationFetcher()
