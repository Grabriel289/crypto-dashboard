"""CDC Signal and Key Levels fetcher."""
import aiohttp
from typing import Dict, Any, List


class CDCFetcher:
    """Fetch CDC signals and key levels for BTC/ETH."""
    
    BINANCE_BASE = "https://api.binance.com"
    
    async def get_klines(self, symbol: str, limit: int = 50) -> List[List]:
        """Fetch klines data from Binance."""
        url = f"{self.BINANCE_BASE}/api/v3/klines"
        params = {"symbol": symbol, "interval": "1d", "limit": limit}
        
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
    
    def calculate_pivot_levels(self, high: float, low: float, close: float) -> Dict[str, float]:
        """Calculate pivot points (R2, R1, S1, S2)."""
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
        return {
            "r2": round(r2, 2),
            "r1": round(r1, 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2)
        }
    
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
            return {"signal": "BULLISH", "emoji": "🟢", "color": "green"}
        
        # BEARISH: Price < EMA12 AND Price < EMA26 AND EMA12 < EMA26
        if (current_price < current_ema12 and 
            current_price < current_ema26 and 
            current_ema12 < current_ema26):
            return {"signal": "BEARISH", "emoji": "🔴", "color": "red"}
        
        # NEUTRAL: Mixed conditions
        return {"signal": "NEUTRAL", "emoji": "🟡", "color": "yellow"}
    
    async def get_cdc_data(self, symbol: str) -> Dict[str, Any]:
        """Get complete CDC data including signal and key levels."""
        # Fetch klines and ticker
        klines, ticker = await asyncio.gather(
            self.get_klines(symbol, 50),
            self.get_ticker(symbol)
        )
        
        if not klines or not ticker:
            return self._get_fallback_data(symbol)
        
        # Extract close prices
        close_prices = [float(k[4]) for k in klines]
        current_price = float(ticker["lastPrice"])
        
        # Get ATH
        ath = await self.get_ath(symbol)
        ath_distance = ((current_price - ath) / ath * 100) if ath else 0
        
        # Calculate CDC signal
        cdc = self.get_cdc_signal(current_price, close_prices)
        
        # Calculate pivot levels using last candle
        last_candle = klines[-1]
        high = float(last_candle[2])
        low = float(last_candle[3])
        close = float(last_candle[4])
        levels = self.calculate_pivot_levels(high, low, close)
        
        return {
            "symbol": symbol.replace("USDT", ""),
            "price": current_price,
            "cdc_signal": cdc,
            "levels": levels,
            "ath": ath,
            "ath_distance": round(ath_distance, 1)
        }
    
    async def get_ath(self, symbol: str) -> float:
        """Get all-time high for a symbol."""
        # For BTC/ETH, use known ATHs (can be fetched from API in production)
        ath_map = {
            "BTCUSDT": 73777,
            "ETHUSDT": 4878
        }
        return ath_map.get(symbol, 0)
    
    def _get_fallback_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback data when API fails."""
        base_price = 68000 if symbol == "BTCUSDT" else 1976
        return {
            "symbol": symbol.replace("USDT", ""),
            "price": base_price,
            "cdc_signal": {"signal": "NEUTRAL", "emoji": "🟡", "color": "yellow"},
            "levels": {
                "r2": round(base_price * 1.1, 2),
                "r1": round(base_price * 1.06, 2),
                "s1": round(base_price * 0.95, 2),
                "s2": round(base_price * 0.88, 2)
            },
            "ath": 73777 if symbol == "BTCUSDT" else 4878,
            "ath_distance": -7.8 if symbol == "BTCUSDT" else -59.4
        }


# Global instance
import asyncio
cdc_fetcher = CDCFetcher()
