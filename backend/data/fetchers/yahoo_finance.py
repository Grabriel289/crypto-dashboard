"""Yahoo Finance data fetcher for macro indicators."""
import aiohttp
from data.utils.http_session import create_session
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
        
        async with create_session() as session:
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
    
    @staticmethod
    def _linear_score(value: float, best: float, worst: float) -> float:
        """Linear score 0.0-1.0. best < worst means lower is better."""
        if best < worst:
            if value <= best:
                return 1.0
            if value >= worst:
                return 0.0
            return round(1.0 - (value - best) / (worst - best), 2)
        else:
            if value >= best:
                return 1.0
            if value <= worst:
                return 0.0
            return round((value - worst) / (best - worst), 2)

    @staticmethod
    def _score_status(score: float) -> str:
        if score >= 0.7:
            return "🟢"
        if score >= 0.3:
            return "🟡"
        return "🔴"

    async def fetch_move_index(self) -> Optional[Dict[str, Any]]:
        """Fetch MOVE Index (bond volatility). Low = calm = risk-on."""
        data = await self.fetch_ticker("^MOVE")
        if data:
            value = data["price"]
            # Linear: 70 (calm) = 1.0, 120 (stressed) = 0.0
            score = self._linear_score(value, best=70, worst=120)
            return {
                "value": value,
                "change_pct": round(data["change_pct"], 2),
                "score": score,
                "status": self._score_status(score),
                "date": data["timestamp"].strftime("%Y-%m-%d"),
                "description": "MOVE Index (Bond Volatility)",
                "source": "yahoo_finance"
            }
        return None

    async def fetch_cu_au_ratio(self) -> Optional[Dict[str, Any]]:
        """Fetch Copper/Gold ratio. High = growth = risk-on."""
        copper = await self.fetch_ticker("HG=F")
        gold = await self.fetch_ticker("GC=F")
        if copper and gold and gold["price"] > 0:
            ratio = copper["price"] / gold["price"]
            # Linear: 0.0028 (strong growth) = 1.0, 0.0016 (recession) = 0.0
            score = self._linear_score(ratio, best=0.0028, worst=0.0016)
            return {
                "value": round(ratio, 6),
                "copper_price": copper["price"],
                "gold_price": gold["price"],
                "score": score,
                "status": self._score_status(score),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "description": "Copper/Gold Ratio (Growth Signal)",
                "source": "yahoo_finance"
            }
        return None

    async def fetch_dxy(self) -> Optional[Dict[str, Any]]:
        """Fetch DXY (US Dollar Index). Strong dollar = risk-off for crypto."""
        data = await self.fetch_ticker("DX-Y.NYB")
        if data:
            value = data["price"]
            # Linear: 95 (weak dollar) = 1.0, 110 (strong dollar) = 0.0
            score = self._linear_score(value, best=95, worst=110)
            return {
                "value": round(value, 2),
                "change_pct": round(data["change_pct"], 2),
                "score": score,
                "status": self._score_status(score),
                "date": data["timestamp"].strftime("%Y-%m-%d"),
                "description": "US Dollar Index",
                "source": "yahoo_finance"
            }
        return None


# Singleton instance
yahoo_finance_fetcher = YahooFinanceFetcher()
