"""Derivative Sentiment fetcher using CoinGlass scraper + Binance Futures API."""
import aiohttp
from typing import Dict, Any, List
import asyncio
import os
import json
from datetime import datetime, timedelta


class DerivativeSentimentFetcher:
    """Fetch derivative sentiment data from Binance Futures."""
    
    BINANCE_FAPI = "https://fapi.binance.com"
    BINANCE_API = "https://api.binance.com"
    
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    
    async def fetch_open_interest(self, symbol: str) -> Dict[str, Any]:
        """Fetch current open interest."""
        url = f"{self.BINANCE_FAPI}/fapi/v1/openInterest"
        params = {"symbol": symbol}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"openInterest": "0", "symbol": symbol}
    
    async def fetch_oi_history(self, symbol: str) -> List[Dict]:
        """Fetch open interest history (24h)."""
        url = f"{self.BINANCE_FAPI}/futures/data/openInterestHist"
        params = {"symbol": symbol, "period": "5m", "limit": 288}  # 24 hours
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
    
    async def fetch_retail_long_short(self, symbol: str) -> Dict[str, Any]:
        """Fetch retail (global) long/short ratio."""
        url = f"{self.BINANCE_FAPI}/futures/data/globalLongShortAccountRatio"
        params = {"symbol": symbol, "period": "1h", "limit": 1}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data[0] if data else {}
                return {}
    
    async def fetch_top_trader_long_short(self, symbol: str) -> Dict[str, Any]:
        """Fetch top trader long/short ratio."""
        url = f"{self.BINANCE_FAPI}/futures/data/topLongShortPositionRatio"
        params = {"symbol": symbol, "period": "1h", "limit": 1}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data[0] if data else {}
                return {}
    
    async def fetch_taker_buy_sell(self, symbol: str) -> Dict[str, Any]:
        """Fetch taker buy/sell volume ratio."""
        url = f"{self.BINANCE_FAPI}/futures/data/takerlongshortRatio"
        params = {"symbol": symbol, "period": "1h", "limit": 1}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data[0] if data else {}
                return {}
    
    async def fetch_price(self, symbol: str) -> float:
        """Fetch current price."""
        url = f"{self.BINANCE_API}/api/v3/ticker/price"
        params = {"symbol": symbol}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return float(data.get("price", 0))
                return 0.0
    
    def generate_signal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate derivative sentiment signal."""
        coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        # Analyze each coin
        analysis = {}
        for coin in coins:
            if coin not in data:
                continue
            coin_data = data[coin]
            
            retail_long = coin_data.get("retail_long_percent", 50)
            top_trader_long = coin_data.get("top_trader_long_percent", 50)
            
            retail_bias = "LONG" if retail_long > 52 else "SHORT" if retail_long < 48 else "NEUTRAL"
            whale_bias = "LONG" if top_trader_long > 52 else "SHORT" if top_trader_long < 48 else "NEUTRAL"
            divergence = (retail_bias == "LONG" and whale_bias == "SHORT") or (retail_bias == "SHORT" and whale_bias == "LONG")
            
            analysis[coin] = {
                "retail_bias": retail_bias,
                "whale_bias": whale_bias,
                "divergence": divergence
            }
        
        # Calculate average OI change
        oi_changes = [data[c].get("oi_change_24h", 0) for c in coins if c in data]
        avg_oi_change = sum(oi_changes) / len(oi_changes) if oi_changes else 0
        oi_increasing = avg_oi_change > 1
        oi_decreasing = avg_oi_change < -1
        
        # Get biases for BTC and ETH (primary signals)
        btc_whale = analysis.get("BTCUSDT", {}).get("whale_bias", "NEUTRAL")
        eth_whale = analysis.get("ETHUSDT", {}).get("whale_bias", "NEUTRAL")
        btc_divergence = analysis.get("BTCUSDT", {}).get("divergence", False)
        eth_divergence = analysis.get("ETHUSDT", {}).get("divergence", False)
        
        # Extreme retail positioning
        btc_retail = data.get("BTCUSDT", {}).get("retail_long_percent", 50)
        eth_retail = data.get("ETHUSDT", {}).get("retail_long_percent", 50)
        extreme_retail_long = btc_retail > 60 or eth_retail > 60
        extreme_retail_short = btc_retail < 40 or eth_retail < 40
        
        # Generate signal
        if btc_whale == "LONG" and eth_whale == "LONG" and oi_increasing:
            return {
                "signal": "ACCUMULATION",
                "emoji": "🟢",
                "color": "green",
                "description": "Smart money accumulating — OI rising with long bias"
            }
        elif btc_whale == "SHORT" and eth_whale == "SHORT" and oi_decreasing:
            return {
                "signal": "DISTRIBUTION",
                "emoji": "🔴",
                "color": "red",
                "description": "Smart money distributing — OI falling with short bias"
            }
        elif btc_divergence or eth_divergence:
            squeeze_type = "SHORT SQUEEZE" if analysis.get("BTCUSDT", {}).get("retail_bias") == "LONG" else "LONG SQUEEZE"
            return {
                "signal": "SQUEEZE SETUP",
                "emoji": "🟡",
                "color": "yellow",
                "description": f"Retail vs Smart Money divergence — potential {squeeze_type}"
            }
        elif (extreme_retail_long or extreme_retail_short) and oi_decreasing:
            return {
                "signal": "LEVERAGE FLUSH",
                "emoji": "🔵",
                "color": "blue",
                "description": "Extreme positioning + falling OI — liquidations likely"
            }
        else:
            return {
                "signal": "NEUTRAL",
                "emoji": "⚪",
                "color": "gray",
                "description": "No clear derivative sentiment bias"
            }
    
    def load_coinglass_cache(self) -> Dict[str, Any]:
        """Load data from CoinGlass scraper cache."""
        try:
            # Try to load from coinglass cache
            current_dir = os.path.dirname(os.path.abspath(__file__))
            cache_file = os.path.join(current_dir, "..", "coinglass_cache.json")
            
            if not os.path.exists(cache_file):
                return {}
            
            with open(cache_file, 'r') as f:
                cache = json.load(f)
            
            # Check if cache is fresh (< 24h)
            scraped_at = datetime.fromisoformat(cache.get("scraped_at", "2000-01-01"))
            age = datetime.now() - scraped_at
            
            if age < timedelta(hours=24):
                print(f"✅ Using CoinGlass cache from {scraped_at.strftime('%Y-%m-%d %H:%M')}")
                return cache.get("coins", {})
            else:
                print(f"⏰ CoinGlass cache expired ({age.total_seconds()/3600:.1f}h old)")
                return {}
                
        except Exception as e:
            print(f"❌ Error loading CoinGlass cache: {e}")
            return {}
    
    async def get_sentiment(self) -> Dict[str, Any]:
        """Get derivative sentiment - tries CoinGlass cache first, then Binance API."""
        results = {}
        
        # First, try to load from CoinGlass scraper cache
        coinglass_data = self.load_coinglass_cache()
        
        if coinglass_data:
            print("[DATA] Using scraped data")
            results = coinglass_data
        else:
            print("[CoinGlass] No cache. Trying Binance API...")
            
            for symbol in self.SYMBOLS:
                try:
                    # Fetch all data concurrently
                    oi, oi_history, retail_ls, top_ls, taker = await asyncio.gather(
                        self.fetch_open_interest(symbol),
                        self.fetch_oi_history(symbol),
                        self.fetch_retail_long_short(symbol),
                        self.fetch_top_trader_long_short(symbol),
                        self.fetch_taker_buy_sell(symbol)
                    )
                    
                    # Fetch price for OI calculation
                    price = await self.fetch_price(symbol)
                    
                    # Calculate OI in USD
                    oi_value_usd = float(oi.get("openInterest", 0)) * price
                    
                    # Check if we got valid data
                    has_valid_oi = oi_value_usd > 0 and price > 0
                    has_valid_ls = retail_ls.get("longAccount") is not None
                    
                    if not has_valid_oi or not has_valid_ls:
                        print(f"Using fallback for {symbol}")
                        results[symbol] = self._get_fallback_data(symbol)
                        continue
                    
                    # Calculate 24h OI change
                    oi_change_24h = 0
                    if len(oi_history) >= 2:
                        oi_now = float(oi_history[-1].get("sumOpenInterestValue", 0))
                        oi_24h_ago = float(oi_history[0].get("sumOpenInterestValue", 0))
                        if oi_24h_ago > 0:
                            oi_change_24h = ((oi_now - oi_24h_ago) / oi_24h_ago) * 100
                    
                    # Parse Long/Short ratios
                    retail_long = float(retail_ls.get("longAccount", 0.5)) * 100
                    top_trader_long = float(top_ls.get("longAccount", 0.5)) * 100
                    
                    # Parse Taker Buy/Sell
                    taker_ratio = float(taker.get("buySellRatio", 1.0))
                    taker_buy_percent = (taker_ratio / (taker_ratio + 1)) * 100
                    
                    results[symbol] = {
                        "symbol": symbol.replace("USDT", ""),
                        "open_interest": oi_value_usd,
                        "oi_change_24h": oi_change_24h,
                        "retail_long_percent": retail_long,
                        "top_trader_long_percent": top_trader_long,
                        "taker_buy_percent": taker_buy_percent,
                        "price": price,
                        "source": "binance_api"
                    }
                    
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
                    results[symbol] = self._get_fallback_data(symbol)
        
        # Generate signal
        signal = self.generate_signal(results)
        
        return {
            "coins": results,
            "signal": signal,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def _get_fallback_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback data when API fails - uses realistic market data."""
        fallbacks = {
            "BTCUSDT": {
                "symbol": "BTC",
                "open_interest": 5362792767.0,  # $5.36B
                "oi_change_24h": -3.9,
                "retail_long_percent": 65.3,
                "top_trader_long_percent": 55.7,
                "taker_buy_percent": 58.2,
                "price": 68000,
                "is_fallback": True
            },
            "ETHUSDT": {
                "symbol": "ETH",
                "open_interest": 3472657347.0,  # $3.47B
                "oi_change_24h": -2.8,
                "retail_long_percent": 72.3,
                "top_trader_long_percent": 60.2,
                "taker_buy_percent": 52.1,
                "price": 1976,
                "is_fallback": True
            },
            "SOLUSDT": {
                "symbol": "SOL",
                "open_interest": 812269184.0,  # $812M
                "oi_change_24h": -4.8,
                "retail_long_percent": 71.8,
                "top_trader_long_percent": 55.2,
                "taker_buy_percent": 64.5,
                "price": 140,
                "is_fallback": True
            }
        }
        return fallbacks.get(symbol, fallbacks["BTCUSDT"])


# Global instance
derivative_sentiment_fetcher = DerivativeSentimentFetcher()
