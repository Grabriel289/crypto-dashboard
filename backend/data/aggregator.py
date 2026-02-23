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
        
        # Fallback to CoinGecko for coins not on major exchanges
        try:
            from data.fetchers.coingecko import coingecko_fetcher
            result = await coingecko_fetcher.fetch_price(coin)
            if result:
                result["coin"] = coin
                self.price_cache[cache_key] = {
                    "data": result,
                    "timestamp": datetime.now()
                }
                return result
        except Exception as e:
            print(f"Error fetching {coin} from CoinGecko: {e}")
        
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
        """Fetch real 7-day return from klines data. Tries Binance, OKX, then CoinGecko."""
        # Try Binance first
        binance_symbol = SYMBOL_MAPPING.get("binance", {}).get(coin)
        if binance_symbol:
            df = await binance_fetcher.fetch_klines(binance_symbol, interval="1d", limit=8)
            if df is not None and len(df) >= 8:
                try:
                    price_7d_ago = df["close"].iloc[0]
                    current_price = df["close"].iloc[-1]
                    return_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
                    return return_7d
                except Exception as e:
                    print(f"Error calculating 7d return for {coin} from Binance: {e}")
        
        # Fallback to OKX
        okx_symbol = SYMBOL_MAPPING.get("okx", {}).get(coin)
        if okx_symbol:
            from data.fetchers.okx import okx_fetcher
            df = await okx_fetcher.fetch_klines(okx_symbol, interval="1D", limit=8)
            if df is not None and len(df) >= 8:
                try:
                    price_7d_ago = df["close"].iloc[0]
                    current_price = df["close"].iloc[-1]
                    return_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
                    return return_7d
                except Exception as e:
                    print(f"Error calculating 7d return for {coin} from OKX: {e}")
        
        # Fallback to CoinGecko
        try:
            from data.fetchers.coingecko import coingecko_fetcher
            return_7d = await coingecko_fetcher.fetch_7d_change(coin)
            if return_7d is not None:
                return return_7d
        except Exception as e:
            print(f"Error fetching 7d return for {coin} from CoinGecko: {e}")
        
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
