"""Derivative Sentiment fetcher using CoinGlass scraper + Binance Futures API with rate limiting."""
import aiohttp
from typing import Dict, Any, List
import asyncio
import os
import json
from datetime import datetime, timedelta


class DerivativeSentimentFetcher:
    """Fetch derivative sentiment data from Binance Futures with rate limiting."""
    
    BYBIT_BASE_URL = "https://api.bybit.com"
    BINANCE_API = "https://api.binance.com"  # spot price (no geo-restriction)
    
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    
    def __init__(self):
        self._session: aiohttp.ClientSession = None
        self._session_lock = asyncio.Lock()
        # In-memory cache: (cached_at: datetime, data: dict)
        self._cache: tuple = None
        self._cache_ttl = 300        # 5 minutes for live data
        self._fallback_cache_ttl = 60  # 1 minute when fallback — retry sooner
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            async with self._session_lock:
                if self._session is None or self._session.closed:
                    self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def fetch_open_interest(self, symbol: str) -> Dict[str, Any]:
        """Fetch current open interest from Bybit (globally accessible)."""
        try:
            session = await self._get_session()
            url = f"{self.BYBIT_BASE_URL}/v5/market/open-interest"
            params = {"category": "linear", "symbol": symbol, "intervalTime": "1h", "limit": "1"}
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("result", {}).get("list", [])
                    if items:
                        return {"openInterest": items[0]["openInterest"], "symbol": symbol}
            return {"openInterest": "0", "symbol": symbol}
        except Exception as e:
            print(f"Error fetching OI for {symbol} from Bybit: {e}")
            return {"openInterest": "0", "symbol": symbol}
    
    async def fetch_oi_history(self, symbol: str) -> List[Dict]:
        """Fetch OI history (24h) from Bybit — returns ASC order (oldest first)."""
        try:
            session = await self._get_session()
            url = f"{self.BYBIT_BASE_URL}/v5/market/open-interest"
            params = {"category": "linear", "symbol": symbol, "intervalTime": "1h", "limit": "25"}
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("result", {}).get("list", [])
                    # Bybit returns DESC (newest first) — reverse to ASC for change calc
                    return list(reversed(items))
            return []
        except Exception as e:
            print(f"Error fetching OI history for {symbol}: {e}")
            return []
    
    async def fetch_retail_long_short(self, symbol: str) -> Dict[str, Any]:
        """Fetch global long/short ratio from Bybit account-ratio."""
        try:
            session = await self._get_session()
            url = f"{self.BYBIT_BASE_URL}/v5/market/account-ratio"
            params = {"category": "linear", "symbol": symbol, "period": "1h", "limit": "1"}
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("result", {}).get("list", [])
                    if items:
                        return {
                            "longAccount": items[0].get("buyRatio", "0.5"),
                            "shortAccount": items[0].get("sellRatio", "0.5"),
                        }
            return {}
        except Exception as e:
            print(f"Error fetching retail L/S for {symbol}: {e}")
            return {}
    
    async def fetch_top_trader_long_short(self, symbol: str) -> Dict[str, Any]:
        """Bybit has no separate top-trader endpoint — reuse global account-ratio."""
        return await self.fetch_retail_long_short(symbol)
    
    async def fetch_taker_buy_sell(self, symbol: str) -> Dict[str, Any]:
        """Fetch taker buy/sell volume ratio from Bybit."""
        try:
            session = await self._get_session()
            url = f"{self.BYBIT_BASE_URL}/v5/market/taker-buy-sell-vol"
            params = {"category": "linear", "symbol": symbol, "period": "1h", "limit": "1"}
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("result", {}).get("list", [])
                    if items:
                        buy_vol = float(items[0].get("buyVolume", 0))
                        sell_vol = float(items[0].get("sellVolume", 0))
                        if sell_vol > 0:
                            return {"buySellRatio": buy_vol / sell_vol}
            return {"buySellRatio": 1.0}
        except Exception as e:
            print(f"Error fetching taker ratio for {symbol}: {e}")
            return {"buySellRatio": 1.0}
    
    async def fetch_price(self, symbol: str) -> float:
        """Fetch current price from Binance spot (no geo-restriction)."""
        try:
            session = await self._get_session()
            url = f"{self.BINANCE_API}/api/v3/ticker/price"
            params = {"symbol": symbol}
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return float(data.get("price", 0))
            return 0.0
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
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
                "emoji": "⚖️",
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
                print(f"📅 CoinGlass cache expired ({age.total_seconds()/3600:.1f}h old)")
                return {}
                
        except Exception as e:
            print(f"❌ Error loading CoinGlass cache: {e}")
            return {}
    
    async def get_sentiment(self) -> Dict[str, Any]:
        """Get derivative sentiment - tries CoinGlass cache first, then Binance API with rate limiting."""
        # Return in-memory cache if still fresh
        if self._cache is not None:
            cached_at, cached_data = self._cache
            age = (datetime.utcnow() - cached_at).total_seconds()
            is_fallback_result = any(
                c.get("is_fallback") for c in cached_data.get("coins", {}).values()
            )
            ttl = self._fallback_cache_ttl if is_fallback_result else self._cache_ttl
            if age < ttl:
                print(f"[DerivativeSentiment] Using cache ({age:.0f}s old, ttl={ttl}s)")
                return cached_data

        results = {}
        
        # First, try to load from CoinGlass scraper cache
        coinglass_data = self.load_coinglass_cache()
        
        if coinglass_data:
            print("[DATA] Using scraped data")
            results = coinglass_data
        else:
            print("[DATA] No CoinGlass cache. Trying Binance API...")
            
            # Process symbols sequentially with delays to avoid rate limits
            for i, symbol in enumerate(self.SYMBOLS):
                try:
                    # Add delay between symbols (increased to avoid rate limits)
                    if i > 0:
                        await asyncio.sleep(1.0)
                    
                    # Fetch all data for this symbol with staggered timing
                    oi = await self.fetch_open_interest(symbol)
                    await asyncio.sleep(0.2)
                    
                    oi_history = await self.fetch_oi_history(symbol)
                    await asyncio.sleep(0.2)
                    
                    retail_ls = await self.fetch_retail_long_short(symbol)
                    await asyncio.sleep(0.2)
                    
                    top_ls = await self.fetch_top_trader_long_short(symbol)
                    await asyncio.sleep(0.2)
                    
                    taker = await self.fetch_taker_buy_sell(symbol)
                    await asyncio.sleep(0.2)
                    
                    # Fetch price for OI calculation
                    price = await self.fetch_price(symbol)
                    
                    # Calculate OI in USD
                    oi_value_usd = float(oi.get("openInterest", 0)) * price
                    
                    # Check if we got valid data
                    has_valid_oi = oi_value_usd > 0 and price > 0
                    has_valid_ls = retail_ls.get("longAccount") is not None
                    
                    if not has_valid_oi or not has_valid_ls:
                        print(f"Using fallback for {symbol} (valid_oi={has_valid_oi}, valid_ls={has_valid_ls})")
                        results[symbol] = self._get_fallback_data(symbol)
                        continue
                    
                    # Calculate 24h OI change (Bybit: openInterest in coins, ASC order)
                    oi_change_24h = 0
                    if len(oi_history) >= 2:
                        oi_now = float(oi_history[-1].get("openInterest", 0))
                        oi_24h_ago = float(oi_history[0].get("openInterest", 0))
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

        result = {
            "coins": results,
            "signal": signal,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Store in cache
        self._cache = (datetime.utcnow(), result)
        return result
    
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
