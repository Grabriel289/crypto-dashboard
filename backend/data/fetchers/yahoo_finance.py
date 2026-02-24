"""Yahoo Finance data fetcher for macro indicators."""
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"


class YahooFinanceFetcher:
    """Fetch market data from Yahoo Finance."""
    
    async def fetch_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current data for a ticker symbol."""
        url = f"{YAHOO_FINANCE_URL}/{symbol}"
        params = {
            "interval": "1d",
            "range": "5d"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        print(f"Yahoo Finance error for {symbol}: HTTP {response.status}")
                        return None
                    
                    data = await response.json()
                    
                    if "chart" not in data or "result" not in data["chart"]:
                        print(f"Yahoo Finance: No data for {symbol}")
                        return None
                    
                    result = data["chart"]["result"][0]
                    meta = result["meta"]
                    
                    # Get last close price
                    timestamps = result.get("timestamp", [])
                    closes = result["indicators"]["quote"][0].get("close", [])
                    
                    if not closes:
                        return None
                    
                    # Filter out None values and get last valid close
                    valid_closes = [c for c in closes if c is not None]
                    if not valid_closes:
                        return None
                    
                    last_close = valid_closes[-1]
                    previous_close = meta.get("previousClose", valid_closes[-2] if len(valid_closes) > 1 else last_close)
                    
                    return {
                        "symbol": symbol,
                        "price": last_close,
                        "previous_close": previous_close,
                        "change": last_close - previous_close,
                        "change_pct": ((last_close - previous_close) / previous_close * 100) if previous_close else 0,
                        "currency": meta.get("currency", "USD"),
                        "timestamp": datetime.fromtimestamp(timestamps[-1]) if timestamps else datetime.now()
                    }
                    
            except Exception as e:
                print(f"Yahoo Finance fetch error for {symbol}: {e}")
                return None
    
    async def fetch_move_index(self) -> Optional[Dict[str, Any]]:
        """
        Fetch MOVE Index (Merrill Lynch Option Volatility Estimate).
        
        Ticker: ^MOVE
        The MOVE index measures implied volatility of US Treasury bonds.
        High MOVE = bond market stress = risk-off for crypto.
        """
        data = await self.fetch_ticker("^MOVE")
        if data:
            value = data["price"]
            
            # Scoring for MOVE Index:
            # < 80 = calm bond market = 1.0pt (risk-on for crypto)
            # 80-100 = elevated = 0.5pt
            # > 100 = stressed = 0pt (risk-off)
            if value < 80:
                score = 1.0
                status = "[GREEN]"
            elif value < 100:
                score = 0.5
                status = "[YELLOW]"
            else:
                score = 0.0
                status = "[RED]"
            
            return {
                "value": value,
                "change_pct": round(data["change_pct"], 2),
                "score": score,
                "status": status,
                "date": data["timestamp"].strftime("%Y-%m-%d"),
                "description": "MOVE Index (Bond Volatility)",
                "source": "yahoo_finance"
            }
        return None
    
    async def fetch_cu_au_ratio(self) -> Optional[Dict[str, Any]]:
        """
        Fetch Copper/Gold ratio as economic health indicator.
        
        Copper = Economic growth (industrial demand)
        Gold = Safe haven / recession hedge
        
        High Cu/Au = growth optimism = risk-on
        Low Cu/Au = recession fear = risk-off
        """
        # Fetch both copper and gold
        copper = await self.fetch_ticker("HG=F")  # Copper futures
        gold = await self.fetch_ticker("GC=F")    # Gold futures
        
        if copper and gold and gold["price"] > 0:
            # Calculate ratio: Copper price / Gold price
            ratio = copper["price"] / gold["price"]
            
            # Historical context:
            # Ratio > 0.0025 = strong growth signal = 1.0pt
            # Ratio 0.0020-0.0025 = moderate = 0.5pt
            # Ratio < 0.0020 = weak = 0pt
            if ratio > 0.0025:
                score = 1.0
                status = "[GREEN]"
            elif ratio > 0.0020:
                score = 0.5
                status = "[YELLOW]"
            else:
                score = 0.0
                status = "[RED]"
            
            return {
                "value": round(ratio, 6),
                "copper_price": copper["price"],
                "gold_price": gold["price"],
                "score": score,
                "status": status,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "description": "Copper/Gold Ratio (Growth Signal)",
                "source": "yahoo_finance"
            }
        return None


# Singleton instance
yahoo_finance_fetcher = YahooFinanceFetcher()
