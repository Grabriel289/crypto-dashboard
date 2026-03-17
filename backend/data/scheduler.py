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
        
        # Market Fragility (OI, Funding, Depth) - every 30 min (parallel fetch reduces rate limit impact)
        self.scheduler.add_job(
            self._update_fragility,
            IntervalTrigger(minutes=30),
            id='fragility_update',
            replace_existing=True
        )

        # Altcoin Breadth Momentum - every 1 hour (daily data, hourly refresh)
        self.scheduler.add_job(
            self._update_abm,
            IntervalTrigger(hours=1),
            id='abm_update',
            replace_existing=True
        )

        # RRG Rotation Map - every 1 hour (daily ETF data from Yahoo Finance)
        self.scheduler.add_job(
            self._update_rrg,
            IntervalTrigger(hours=1),
            id='rrg_update',
            replace_existing=True
        )
    
    async def _update_macro(self):
        """Update macro data."""
        try:
            print(f"[{datetime.now()}] Updating macro data...")
            data = await macro_tide_scorer.calculate_full_score()
            data_cache.set('macro', data)
            print(f"[{datetime.now()}] Macro data updated: {data.get('adjusted_score')}/7")
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
            heatmap = await liquidation_fetcher.get_heatmap("BTCUSDT")
            source = heatmap.get('source', 'unknown') if heatmap else 'none'
            frag_score = heatmap.get('fragility', {}).get('score', 'N/A') if heatmap else 'N/A'

            if heatmap and source in ('binance_live', 'binance_partial'):
                # Cache live or partial data (partial is still better than hardcoded fallback)
                data_cache.set('fragility', heatmap)
                print(f"[{datetime.now()}] Fragility cached: score={frag_score}, source={source}")
            else:
                # Full fallback — do NOT cache so API endpoint retries on next request
                print(f"[{datetime.now()}] Fragility got fallback (source={source}), skipping cache")
        except Exception as e:
            print(f"[{datetime.now()}] Error updating fragility: {e}")
            import traceback
            traceback.print_exc()
    
    async def _update_abm(self):
        """Update Altcoin Breadth Momentum data."""
        try:
            print(f"[{datetime.now()}] Updating ABM data...")
            from analysis.abm import ABMEngine, ABMDataFetcher

            fetcher = ABMDataFetcher()
            engine = ABMEngine()
            price_data = await fetcher.fetch_all()
            await fetcher.close()

            if price_data and "BTC" in price_data:
                result = engine.calculate(price_data)
                if "error" not in result:
                    data_cache.set('abm', result)
                    print(f"[{datetime.now()}] ABM updated: BM={result.get('bm_current')}, state={result.get('combined_state')}")
                else:
                    print(f"[{datetime.now()}] ABM calc error: {result.get('error')}")
            else:
                print(f"[{datetime.now()}] ABM: no price data available")
        except Exception as e:
            print(f"[{datetime.now()}] Error updating ABM: {e}")
            import traceback
            traceback.print_exc()

    async def _update_rrg(self):
        """Update RRG Rotation Map data — runs hourly (daily ETF data)."""
        try:
            print(f"[{datetime.now()}] Updating RRG data...")
            from analysis.rrg import RRGEngine, RRGDataFetcher

            fetcher = RRGDataFetcher()
            engine = RRGEngine()
            price_data = await fetcher.fetch_all_symbols()
            await fetcher.close()

            if price_data:
                results = engine.calculate_all(price_data)
                regime = engine.detect_regime(results)
                regime_filter = engine.detect_regime_v6(results, regime)
                top_picks = engine.get_top_picks(results)
                action_groups = engine.get_action_groups(results)
                insights = engine.generate_insights(results, regime)

                def _asset_dict(r):
                    return {
                        "symbol": r.symbol, "name": r.name,
                        "category": r.category, "color": r.color,
                        "coordinate": {
                            "rs_ratio": r.rs_ratio,
                            "rs_momentum": r.rs_momentum,
                            "quadrant": r.quadrant
                        },
                        "current_price": r.current_price,
                        "period_return": r.period_return,
                        "return_6m": r.return_6m,
                    }

                rrg_data = {
                    "benchmark": "SPY",
                    "risk_assets": [_asset_dict(r) for r in results if r.category == "risk"],
                    "safe_haven_assets": [_asset_dict(r) for r in results if r.category == "safe_haven"],
                    "regime": {
                        "regime": regime.regime, "score": regime.score,
                        "emoji": regime.emoji, "color": regime.color,
                        "risk_summary": regime.risk_summary,
                        "safe_summary": regime.safe_summary
                    },
                    "regime_filter": regime_filter,
                    "top_picks": top_picks,
                    "action_groups": action_groups,
                    "insights": insights,
                    "calculation_period": 21,
                }
                data_cache.set('rrg', rrg_data)
                print(f"[{datetime.now()}] RRG updated: regime={regime.regime}, {len(results)} assets")
            else:
                print(f"[{datetime.now()}] RRG: no price data available")
        except Exception as e:
            print(f"[{datetime.now()}] Error updating RRG: {e}")
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
        """Run initial data fetch on startup.

        Fragility is fetched separately after other Binance-dependent fetchers
        to avoid rate limiting (fragility requires 5 concurrent Binance API calls).
        """
        print(">>> Running initial data fetch...")
        await asyncio.gather(
            self._update_macro(),
            self._update_fear_greed(),
            self._update_funding(),
            self._update_crypto_prices(),
        )
        # Run fragility separately after a longer pause — the price fetch for ~43 sector
        # coins fires many Binance requests; we need to let the rate limiter settle first.
        print(">>> Running fragility fetch (staggered 15s)...")
        await asyncio.sleep(15)
        await self._update_fragility()
        # ABM fetches 52 klines from Binance — stagger after fragility
        print(">>> Running ABM fetch (staggered 20s)...")
        await asyncio.sleep(20)
        await self._update_abm()
        # RRG fetches from Yahoo Finance — stagger after ABM (Binance)
        print(">>> Running RRG fetch (staggered 10s)...")
        await asyncio.sleep(10)
        await self._update_rrg()
        print(">>> Initial data fetch complete")


# Singleton instance
data_scheduler = DataScheduler()
