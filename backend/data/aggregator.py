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
    
    async def fetch_7d_return(self, coin: str) -> Optional[float]:
        """Fetch real 7-day return from klines data."""
        symbol_map = SYMBOL_MAPPING.get("binance", {})
        symbol = symbol_map.get(coin)
        
        if not symbol:
            return None
        
        # Fetch 8 days of daily data (to calculate 7-day change)
        df = await binance_fetcher.fetch_klines(symbol, interval="1d", limit=8)
        
        if df is None or len(df) < 8:
            return None
        
        try:
            # Calculate 7-day return: (current - 7_days_ago) / 7_days_ago * 100
            price_7d_ago = df["close"].iloc[0]  # First candle (8 days ago)
            current_price = df["close"].iloc[-1]  # Last candle (today)
            
            return_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
            return return_7d
        except Exception as e:
            print(f"Error calculating 7d return for {coin}: {e}")
            return None
    
    async def fetch_multiple_7d_returns(self, coins: List[str]) -> Dict[str, float]:
        """Fetch 7-day returns for multiple coins concurrently."""
        tasks = [self.fetch_7d_return(coin) for coin in coins]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        returns = {}
        for coin, result in zip(coins, results):
            if isinstance(result, Exception):
                print(f"Error fetching 7d return for {coin}: {result}")
            elif result is not None:
                returns[coin] = result
        
        return returns


# Singleton instance
data_aggregator = DataAggregator()
