"""Data aggregator with fallback between exchanges."""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio

from config.sectors import SYMBOL_MAPPING, EXCHANGE_PRIORITY
from data.fetchers.binance import binance_fetcher
from data.fetchers.okx import okx_fetcher


class DataAggregator:
    """Aggregate data from multiple sources with fallback."""
    
    def __init__(self):
        self.price_cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        
    async def fetch_price_with_fallback(self, coin: str) -> Optional[Dict[str, Any]]:
        """Try exchanges in priority order until success."""
        cache_key = f"price_{coin}"
        
        # Check cache
        if cache_key in self.price_cache:
            cached = self.price_cache[cache_key]
            if datetime.now() - cached["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached["data"]
        
        for exchange in EXCHANGE_PRIORITY:
            try:
                symbol_map = SYMBOL_MAPPING.get(exchange, {})
                symbol = symbol_map.get(coin)
                
                if not symbol:
                    continue
                
                # Fetch from appropriate fetcher
                result = None
                if exchange == "binance":
                    result = await binance_fetcher.fetch_price(symbol)
                elif exchange == "okx":
                    result = await okx_fetcher.fetch_price(symbol)
                
                if result:
                    result["coin"] = coin
                    self.price_cache[cache_key] = {
                        "data": result,
                        "timestamp": datetime.now()
                    }
                    return result
                    
            except Exception as e:
                print(f"Error fetching {coin} from {exchange}: {e}")
                continue
        
        return None
    
    async def fetch_multiple_prices(self, coins: List[str]) -> Dict[str, Any]:
        """Fetch prices for multiple coins concurrently."""
        tasks = [self.fetch_price_with_fallback(coin) for coin in coins]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        errors = []
        
        for coin, result in zip(coins, results):
            if isinstance(result, Exception):
                errors.append({"coin": coin, "error": str(result)})
            elif result:
                prices[coin] = result
            else:
                errors.append({"coin": coin, "error": "No data available"})
        
        return {
            "prices": prices,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    async def fetch_funding_rate(self, coin: str) -> Optional[Dict[str, Any]]:
        """Fetch funding rate for a coin."""
        symbol_map = SYMBOL_MAPPING.get("binance", {})
        symbol = symbol_map.get(coin)
        
        if not symbol:
            return None
        
        return await binance_fetcher.fetch_funding_rate(symbol)
    
    async def fetch_open_interest(self, coin: str) -> Optional[Dict[str, Any]]:
        """Fetch open interest for a coin."""
        symbol_map = SYMBOL_MAPPING.get("binance", {})
        symbol = symbol_map.get(coin)
        
        if not symbol:
            return None
        
        return await binance_fetcher.fetch_open_interest(symbol)


# Singleton instance
data_aggregator = DataAggregator()
