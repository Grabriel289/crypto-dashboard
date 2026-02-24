"""CDC Signal and Order Block Level fetcher."""
import aiohttp
from typing import Dict, Any, List, Optional
import asyncio


class CDCFetcher:
    """Fetch CDC signals and Order Block levels for BTC/ETH."""
    
    BINANCE_BASE = "https://api.binance.com"
    
    async def get_klines(self, symbol: str, interval: str = "1d", limit: int = 60) -> List[List]:
        """Fetch klines data from Binance."""
        url = f"{self.BINANCE_BASE}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch 24hr ticker data."""
        url = f"{self.BINANCE_BASE}/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {}
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate EMA for a list of prices."""
        multiplier = 2 / (period + 1)
        ema = [prices[0]]
        for i in range(1, len(prices)):
            ema.append((prices[i] - ema[i-1]) * multiplier + ema[i-1])
        return ema
    
    def get_cdc_signal(self, current_price: float, close_prices: List[float]) -> Dict[str, Any]:
        """Calculate CDC signal based on EMA crossover."""
        ema12 = self.calculate_ema(close_prices, 12)
        ema26 = self.calculate_ema(close_prices, 26)
        
        current_ema12 = ema12[-1]
        current_ema26 = ema26[-1]
        
        # BULLISH: Price > EMA12 AND Price > EMA26 AND EMA12 > EMA26
        if (current_price > current_ema12 and 
            current_price > current_ema26 and 
            current_ema12 > current_ema26):
            return {"signal": "BULLISH", "emoji": "[G]", "color": "green"}
        
        # BEARISH: Price < EMA12 AND Price < EMA26 AND EMA12 < EMA26
        if (current_price < current_ema12 and 
            current_price < current_ema26 and 
            current_ema12 < current_ema26):
            return {"signal": "BEARISH", "emoji": "[R]", "color": "red"}
        
        # NEUTRAL: Mixed conditions
        return {"signal": "NEUTRAL", "emoji": "[Y]", "color": "yellow"}
    
    def detect_order_blocks(self, candles: List[Dict]) -> Dict[str, Any]:
        """
        Detect Order Blocks (Smart Money Concept):
        - Bullish OB = Last RED candle before significant UP move -> SUPPORT
        - Bearish OB = Last GREEN candle before significant DOWN move -> RESISTANCE
        """
        if len(candles) < 10:
            return {"supports": [], "resistances": []}
        
        # Calculate average volume
        avg_volume = sum(c["volume"] for c in candles) / len(candles)
        
        # Parameters
        threshold = 0.03  # 3% move required
        volume_multiplier = 1.2  # Volume must be 1.2x average
        lookforward = 3  # Check next 3 candles
        max_age = 30  # Only last 30 days
        
        bullish_obs = []  # Support zones
        bearish_obs = []  # Resistance zones
        
        for i in range(1, len(candles) - lookforward):
            current = candles[i]
            next_candles = candles[i + 1:i + 1 + lookforward]
            
            # Calculate max move after this candle
            max_high = max(c["high"] for c in next_candles)
            min_low = min(c["low"] for c in next_candles)
            
            move_up = (max_high - current["close"]) / current["close"]
            move_down = (current["close"] - min_low) / current["close"]
            
            # Candle characteristics
            is_bearish = current["close"] < current["open"]  # Red candle
            is_bullish = current["close"] > current["open"]  # Green candle
            has_volume = current["volume"] >= avg_volume * volume_multiplier
            
            # Bullish Order Block: Red candle before UP move
            if is_bearish and move_up >= threshold and has_volume:
                bullish_obs.append({
                    "top": current["high"],
                    "bottom": current["low"],
                    "mid": (current["high"] + current["low"]) / 2,
                    "strength": move_up,
                    "age": len(candles) - i
                })
            
            # Bearish Order Block: Green candle before DOWN move
            if is_bullish and move_down >= threshold and has_volume:
                bearish_obs.append({
                    "top": current["high"],
                    "bottom": current["low"],
                    "mid": (current["high"] + current["low"]) / 2,
                    "strength": move_down,
                    "age": len(candles) - i
                })
        
        return {"supports": bullish_obs, "resistances": bearish_obs}
    
    def get_fallback_levels(self, current_price: float, symbol: str) -> Dict[str, Any]:
        """Fallback to psychological levels if no OBs found."""
        if "BTC" in symbol:
            round_base = 5000
        elif "ETH" in symbol:
            round_base = 100
        else:
            round_base = 500 if current_price > 100 else 10
        
        nearest = round(current_price / round_base) * round_base
        
        return {
            "R1": {"price": nearest + round_base, "zone": None},
            "R2": {"price": nearest + round_base * 2, "zone": None},
            "S1": {"price": nearest - round_base, "zone": None},
            "S2": {"price": nearest - round_base * 2, "zone": None},
            "isFallback": True
        }
    
    def calculate_ob_levels(self, obs: Dict[str, Any], current_price: float, symbol: str) -> Dict[str, Any]:
        """Calculate S/R levels from Order Blocks."""
        supports = obs.get("supports", [])
        resistances = obs.get("resistances", [])
        
        # Filter OBs below/above current price and sort by distance
        valid_supports = [ob for ob in supports if ob["top"] < current_price and ob["age"] <= 30]
        valid_resistances = [ob for ob in resistances if ob["bottom"] > current_price and ob["age"] <= 30]
        
        # Sort by proximity to current price
        valid_supports.sort(key=lambda x: x["top"], reverse=True)  # Highest first (closest)
        valid_resistances.sort(key=lambda x: x["bottom"])  # Lowest first (closest)
        
        # Take top 2 of each
        top_supports = valid_supports[:2]
        top_resistances = valid_resistances[:2]
        
        # If not enough OBs, use fallback
        has_resistance = len(top_resistances) >= 1
        has_support = len(top_supports) >= 1
        
        if not has_resistance or not has_support:
            fallback = self.get_fallback_levels(current_price, symbol)
        else:
            fallback = {"R1": None, "R2": None, "S1": None, "S2": None, "isFallback": False}
        
        return {
            "R1": top_resistances[0] if len(top_resistances) > 0 else fallback["R1"],
            "R2": top_resistances[1] if len(top_resistances) > 1 else (fallback["R2"] if not top_resistances else {"price": int(top_resistances[0]["bottom"] * 1.03), "zone": None}),
            "S1": top_supports[0] if len(top_supports) > 0 else fallback["S1"],
            "S2": top_supports[1] if len(top_supports) > 1 else (fallback["S2"] if not top_supports else {"price": int(top_supports[0]["top"] * 0.97), "zone": None}),
            "isFallback": fallback.get("isFallback", False)
        }
    
    async def get_ath(self, symbol: str) -> float:
        """Get all-time high for a symbol."""
        ath_map = {
            "BTCUSDT": 73800,
            "ETHUSDT": 4878
        }
        return ath_map.get(symbol, 0)
    
    async def get_cdc_data(self, symbol: str) -> Dict[str, Any]:
        """Get complete CDC data with Order Block levels."""
        # Fetch klines and ticker
        klines, ticker = await asyncio.gather(
            self.get_klines(symbol, "1d", 60),
            self.get_ticker(symbol)
        )
        
        if not klines or not ticker:
            return self._get_fallback_data(symbol)
        
        # Parse candles
        candles = []
        for k in klines:
            candles.append({
                "timestamp": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            })
        
        current_price = float(ticker["lastPrice"])
        close_prices = [c["close"] for c in candles]
        
        # Get ATH
        ath = await self.get_ath(symbol)
        ath_distance = ((current_price - ath) / ath * 100) if ath else 0
        
        # Calculate CDC signal
        cdc = self.get_cdc_signal(current_price, close_prices)
        
        # Detect Order Blocks
        obs = self.detect_order_blocks(candles)
        
        # Calculate levels from OBs
        levels_data = self.calculate_ob_levels(obs, current_price, symbol)
        
        # Format levels for display - safely access price
        def get_price(level_data, fallback_price):
            if level_data is None:
                return fallback_price
            if isinstance(level_data, dict):
                return int(level_data.get("price", fallback_price))
            return int(fallback_price)
        
        levels = {
            "r2": get_price(levels_data.get("R2"), int(current_price * 1.06)),
            "r1": get_price(levels_data.get("R1"), int(current_price * 1.03)),
            "s1": get_price(levels_data.get("S1"), int(current_price * 0.97)),
            "s2": get_price(levels_data.get("S2"), int(current_price * 0.94)),
            "source": "orderblock" if not levels_data.get("isFallback", False) else "fallback"
        }
        
        return {
            "symbol": symbol.replace("USDT", ""),
            "price": current_price,
            "cdc_signal": cdc,
            "levels": levels,
            "ath": ath,
            "ath_distance": round(ath_distance, 1)
        }
    
    def _get_fallback_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback data when API fails."""
        base_price = 68000 if symbol == "BTCUSDT" else 1976
        return {
            "symbol": symbol.replace("USDT", ""),
            "price": base_price,
            "cdc_signal": {"signal": "NEUTRAL", "emoji": "[Y]", "color": "yellow"},
            "levels": {
                "r2": int(base_price * 1.06),
                "r1": int(base_price * 1.03),
                "s1": int(base_price * 0.97),
                "s2": int(base_price * 0.94),
                "source": "fallback"
            },
            "ath": 73800 if symbol == "BTCUSDT" else 4878,
            "ath_distance": -7.8 if symbol == "BTCUSDT" else -59.4
        }


# Global instance
cdc_fetcher = CDCFetcher()
