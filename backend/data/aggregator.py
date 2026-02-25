"""Data aggregator with fallback between exchanges."""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio

from config.sectors import SYMBOL_MAPPING, EXCHANGE_PRIORITY
from data.fetchers.binance import binance_fetcher
from data.fetchers.okx import okx_fetcher
from data.fetchers.kucoin import kucoin_fetcher


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
        
        # Fallback to KuCoin
        kucoin_symbol = SYMBOL_MAPPING.get("kucoin", {}).get(coin)
        if kucoin_symbol:
            try:
                result = await kucoin_fetcher.fetch_price(kucoin_symbol)
                if result:
                    result["coin"] = coin
                    self.price_cache[cache_key] = {
                        "data": result,
                        "timestamp": datetime.now()
                    }
                    return result
            except Exception as e:
                print(f"Error fetching {coin} from KuCoin: {e}")
        
        # Final fallback to CoinGecko
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
    
    async def fetch_multiple_prices_with_fallbacks(self, coins: List[str]) -> Dict[str, Any]:
        """Fetch prices for multiple coins, using KuCoin and CoinGecko as fallbacks for altcoins."""
        # First try Binance/OKX exchanges
        result = await self.fetch_multiple_prices(coins)
        prices = result.get("prices", {})
        
        # Find coins that weren't found
        missing_coins = [c for c in coins if c not in prices]
        
        # Try KuCoin for missing coins
        kucoin_results = {}
        for coin in missing_coins[:]:
            kucoin_symbol = SYMBOL_MAPPING.get("kucoin", {}).get(coin)
            if kucoin_symbol:
                try:
                    price_data = await kucoin_fetcher.fetch_price(kucoin_symbol)
                    if price_data:
                        price_data["coin"] = coin
                        kucoin_results[coin] = price_data
                        prices[coin] = price_data
                        self.price_cache[f"price_{coin}"] = {
                            "data": price_data,
                            "timestamp": datetime.now()
                        }
                        missing_coins.remove(coin)
                except Exception as e:
                    print(f"KuCoin fetch error for {coin}: {e}")
        
        # Final fallback to CoinGecko for remaining coins
        if missing_coins:
            try:
                from data.fetchers.coingecko import coingecko_fetcher
                cg_prices = await coingecko_fetcher.fetch_prices_batch(missing_coins)
                
                for coin, price_data in cg_prices.items():
                    price_data["coin"] = coin
                    prices[coin] = price_data
                    self.price_cache[f"price_{coin}"] = {
                        "data": price_data,
                        "timestamp": datetime.now()
                    }
            except Exception as e:
                print(f"CoinGecko batch fetch error: {e}")
        
        return {
            "prices": prices,
            "errors": result.get("errors", []),
            "timestamp": datetime.now().isoformat()
        }
    
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
        """
        Fetch actual 7-day return from historical price data.
        Tries Binance, OKX, KuCoin, then CoinGecko.
        Uses current price vs price from exactly 7 days ago.
        """
        # Try Binance first - uses actual current price vs 7-day historical
        binance_symbol = SYMBOL_MAPPING.get("binance", {}).get(coin)
        if binance_symbol:
            return_7d = await binance_fetcher.fetch_7d_return(binance_symbol)
            if return_7d is not None:
                return return_7d
        
        # Fallback to OKX
        okx_symbol = SYMBOL_MAPPING.get("okx", {}).get(coin)
        if okx_symbol:
            from data.fetchers.okx import okx_fetcher
            return_7d = await okx_fetcher.fetch_7d_return(okx_symbol)
            if return_7d is not None:
                return return_7d
        
        # Fallback to KuCoin
        kucoin_symbol = SYMBOL_MAPPING.get("kucoin", {}).get(coin)
        if kucoin_symbol:
            return_7d = await kucoin_fetcher.fetch_7d_return(kucoin_symbol)
            if return_7d is not None:
                return return_7d
        
        # Final fallback to CoinGecko
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
