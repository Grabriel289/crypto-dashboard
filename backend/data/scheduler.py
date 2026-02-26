"""Data scheduler for periodic updates with different frequencies."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

from scoring.macro_tide import macro_tide_scorer
from data.fetchers.fear_greed import fear_greed_fetcher
from data.aggregator import data_aggregator
from data.fetchers.liquidation import liquidation_fetcher
from config.sectors import SECTORS


class DataCache:
    """Simple in-memory cache with timestamps."""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def set(self, key: str, value: Any):
        """Set cache value with timestamp."""
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        return self._cache.get(key)
    
    def get_timestamp(self, key: str) -> Optional[datetime]:
        """Get cache timestamp."""
        return self._timestamps.get(key)
    
    def is_stale(self, key: str, max_age_minutes: int) -> bool:
        """Check if cache entry is stale."""
        timestamp = self._timestamps.get(key)
        if not timestamp:
            return True
        age = (datetime.now() - timestamp).total_seconds() / 60
        return age > max_age_minutes


# Global cache instance
data_cache = DataCache()


class DataScheduler:
    """Schedule periodic data updates."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs with different frequencies."""
        
        # Macro data - every 6 hours (daily is too long for dashboard freshness)
        self.scheduler.add_job(
            self._update_macro,
            IntervalTrigger(hours=6),
            id='macro_update',
            replace_existing=True
        )
        
        # Fear & Greed - every 6 hours (API updates daily)
        self.scheduler.add_job(
            self._update_fear_greed,
            IntervalTrigger(hours=6),
            id='fear_greed_update',
            replace_existing=True
        )
        
        # Funding rates - every 8 hours (funding happens every 8h)
        self.scheduler.add_job(
            self._update_funding,
            IntervalTrigger(hours=8),
            id='funding_update',
            replace_existing=True
        )
        
        # Crypto prices - every 1 hour
        self.scheduler.add_job(
            self._update_crypto_prices,
            IntervalTrigger(hours=1),
            id='crypto_update',
            replace_existing=True
        )
        
        # Sector data - every 1 hour
        self.scheduler.add_job(
            self._update_sectors,
            IntervalTrigger(hours=1),
            id='sector_update',
            replace_existing=True
        )
        
        # Market Fragility (OI, Funding, Depth) - every 1 hour (to avoid rate limits)
        self.scheduler.add_job(
            self._update_fragility,
            IntervalTrigger(hours=1),
            id='fragility_update',
            replace_existing=True
        )
    
    async def _update_macro(self):
        """Update macro data."""
        try:
            print(f"[{datetime.now()}] Updating macro data...")
            data = await macro_tide_scorer.calculate_full_score()
            data_cache.set('macro', data)
            print(f"[{datetime.now()}] Macro data updated: {data.get('adjusted_score')}/5")
        except Exception as e:
            print(f"Error updating macro data: {e}")
    
    async def _update_fear_greed(self):
        """Update Fear & Greed index."""
        try:
            print(f"[{datetime.now()}] Updating Fear & Greed...")
            data = await fear_greed_fetcher.fetch()
            data_cache.set('fear_greed', data)
            print(f"[{datetime.now()}] F&G updated: {data.get('value')}/100")
        except Exception as e:
            print(f"Error updating Fear & Greed: {e}")
    
    async def _update_funding(self):
        """Update funding rates."""
        try:
            print(f"[{datetime.now()}] Updating funding rates...")
            funding_data = {}
            for coin in ["BTC", "ETH", "SOL"]:
                funding = await data_aggregator.fetch_funding_rate(coin)
                if funding:
                    funding_data[coin] = funding
            data_cache.set('funding', funding_data)
            print(f"[{datetime.now()}] Funding rates updated for {len(funding_data)} coins")
        except Exception as e:
            print(f"Error updating funding rates: {e}")
    
    async def _update_crypto_prices(self):
        """Update crypto prices."""
        try:
            print(f"[{datetime.now()}] Updating crypto prices...")
            # Get all coins from sectors
            all_coins = []
            for sector_coins in SECTORS.values():
                all_coins.extend(sector_coins["coins"])
            all_coins = list(set(all_coins))
            
            prices = await data_aggregator.fetch_multiple_prices(all_coins)
            data_cache.set('prices', prices)
            print(f"[{datetime.now()}] Prices updated for {len(prices.get('prices', {}))} coins")
        except Exception as e:
            print(f"Error updating crypto prices: {e}")
    
    async def _update_sectors(self):
        """Update sector data."""
        try:
            print(f"[{datetime.now()}] Updating sector data...")
            # Trigger crypto price update first
            await self._update_crypto_prices()
            print(f"[{datetime.now()}] Sector data updated")
        except Exception as e:
            print(f"Error updating sector data: {e}")
    
    async def _update_fragility(self):
        """Update fragility metrics - runs hourly to avoid rate limits."""
        try:
            print(f"[{datetime.now()}] Updating fragility metrics...")
            # Fetch full heatmap data from Binance (rate limited endpoint)
            heatmap = await liquidation_fetcher.get_heatmap("BTCUSDT")
            if heatmap:
                data_cache.set('fragility', heatmap)
                frag_score = heatmap.get('fragility', {}).get('score', 'N/A')
                source = heatmap.get('source', 'unknown')
                print(f"[{datetime.now()}] Fragility updated: score={frag_score}, source={source}")
            else:
                print(f"[{datetime.now()}] Failed to fetch fragility data")
        except Exception as e:
            print(f"[{datetime.now()}] Error updating fragility: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        print(">>> Data scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        print(">>> Data scheduler stopped")
    
    async def run_initial_fetch(self):
        """Run initial data fetch on startup."""
        print(">>> Running initial data fetch...")
        await asyncio.gather(
            self._update_macro(),
            self._update_fear_greed(),
            self._update_funding(),
            self._update_crypto_prices(),
            self._update_fragility()  # Fetch fragility on startup
        )
        print(">>> Initial data fetch complete")


# Singleton instance
data_scheduler = DataScheduler()
