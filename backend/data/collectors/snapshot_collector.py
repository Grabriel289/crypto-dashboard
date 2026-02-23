"""Snapshot Collector - Periodic market data collection."""
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading
import time


class SnapshotCollector:
    """
    Collect market snapshots (OI, funding, depth) periodically.
    Calculate and store fragility score.
    """
    
    BINANCE_FUTURES = "https://fapi.binance.com"
    BINANCE_SPOT = "https://api.binance.com"
    
    def __init__(self, symbols: List[str] = None, interval_minutes: int = 5):
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.interval = interval_minutes * 60
        self.running = False
        self._latest_snapshots: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    async def _fetch_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch all data for a symbol from Binance."""
        try:
            async with aiohttp.ClientSession() as session:
                # Open Interest
                oi_resp = await session.get(
                    f"{self.BINANCE_FUTURES}/fapi/v1/openInterest",
                    params={"symbol": symbol},
                    timeout=10
                )
                oi_data = await oi_resp.json()
                oi_contracts = float(oi_data["openInterest"])
                
                # Perp Price
                perp_resp = await session.get(
                    f"{self.BINANCE_FUTURES}/fapi/v1/ticker/price",
                    params={"symbol": symbol},
                    timeout=10
                )
                perp_data = await perp_resp.json()
                perp_price = float(perp_data["price"])
                
                # Spot Price
                spot_resp = await session.get(
                    f"{self.BINANCE_SPOT}/api/v3/ticker/price",
                    params={"symbol": symbol},
                    timeout=10
                )
                spot_data = await spot_resp.json()
                spot_price = float(spot_data["price"])
                
                # Funding Rate
                funding_resp = await session.get(
                    f"{self.BINANCE_FUTURES}/fapi/v1/premiumIndex",
                    params={"symbol": symbol},
                    timeout=10
                )
                funding_data = await funding_resp.json()
                funding_rate = float(funding_data["lastFundingRate"])
                
                # Funding History
                funding_hist_resp = await session.get(
                    f"{self.BINANCE_FUTURES}/fapi/v1/fundingRate",
                    params={"symbol": symbol, "limit": 21},
                    timeout=10
                )
                funding_history = [float(r["fundingRate"]) for r in await funding_hist_resp.json()]
                
                # Order Book Depth
                depth_resp = await session.get(
                    f"{self.BINANCE_FUTURES}/fapi/v1/depth",
                    params={"symbol": symbol, "limit": 1000},
                    timeout=10
                )
                depth_data = await depth_resp.json()
                
                # Calculate metrics
                from scoring.fragility import calculate_depth_2pct, calculate_fragility_score
                
                oi_usd = oi_contracts * perp_price
                mid_price = (spot_price + perp_price) / 2
                depth_2pct = calculate_depth_2pct(
                    [[float(p), float(q)] for p, q in depth_data["bids"]],
                    [[float(p), float(q)] for p, q in depth_data["asks"]],
                    mid_price
                )
                
                # Calculate Fragility Score
                fragility = calculate_fragility_score(
                    open_interest_usd=oi_usd,
                    depth_2pct_usd=depth_2pct,
                    current_funding=funding_rate,
                    funding_7d=funding_history if funding_history else [funding_rate] * 7,
                    spot_price=spot_price,
                    perp_price=perp_price
                )
                
                return {
                    "timestamp": datetime.utcnow().isoformat(),
                    "symbol": symbol,
                    "open_interest_usd": oi_usd,
                    "spot_price": spot_price,
                    "perp_price": perp_price,
                    "funding_rate": funding_rate,
                    "total_depth_usd": depth_2pct,
                    "fragility_score": fragility["score"],
                    "fragility_components": fragility["components"]
                }
                
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    async def _collect_once(self):
        """Collect one round of snapshots."""
        for symbol in self.symbols:
            snapshot = await self._fetch_data(symbol)
            
            if snapshot:
                with self._lock:
                    self._latest_snapshots[symbol] = snapshot
                
                # Print status
                phi = snapshot["fragility_score"]
                level = "🟢" if phi <= 25 else "🟡" if phi <= 50 else "🟠" if phi <= 75 else "🔴"
                print(f"📊 {symbol} Φ={phi:.1f} {level} | OI=${snapshot['open_interest_usd']/1e9:.1f}B")
            
            await asyncio.sleep(1)  # Small delay between symbols
    
    async def _collect_loop(self):
        """Main collection loop."""
        while self.running:
            await self._collect_once()
            
            # Wait for next interval
            await asyncio.sleep(self.interval)
    
    async def start(self):
        """Start snapshot collection."""
        self.running = True
        await self._collect_loop()
    
    def start_sync(self):
        """Start in synchronous context."""
        self.running = True
        asyncio.run(self._collect_loop())
    
    def start_background(self):
        """Start in background thread."""
        self.running = True
        thread = threading.Thread(target=self.start_sync, daemon=True)
        thread.start()
        print(f"🚀 Started snapshot collector (every {self.interval//60} min)")
        return thread
    
    def stop(self):
        """Stop collection."""
        self.running = False
        print("🛑 Snapshot collector stopped")
    
    def get_latest(self, symbol: str = None) -> Optional[Dict[str, Any]]:
        """Get most recent snapshot."""
        with self._lock:
            if symbol:
                return self._latest_snapshots.get(symbol)
            return self._latest_snapshots.copy()


# Global instance
snapshot_collector = SnapshotCollector()


def start_snapshot_collector():
    """Start the snapshot collector in background."""
    snapshot_collector.start_background()
