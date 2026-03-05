"""FRED (Federal Reserve Economic Data) fetcher."""
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os

from config.settings import settings


FRED_URL = "https://api.stlouisfed.org/fred"


class FREDFetcher:
    """Fetch macro data from FRED API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FRED_API_KEY or os.getenv("FRED_API_KEY", "")
    
    async def fetch_series(self, series_id: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """Fetch a FRED series."""
        url = f"{FRED_URL}/series/observations"
        params = {
            "series_id": series_id,
            "sort_order": "desc",
            "limit": limit,
            "file_type": "json"
        }
        if self.api_key:
            params["api_key"] = self.api_key
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        print(f"FRED API error for {series_id}: HTTP {response.status}")
                        text = await response.text()
                        print(f"Response: {text[:200]}")
                        return None
                    data = await response.json()
                    if "observations" in data and data["observations"]:
                        return {
                            "series_id": series_id,
                            "observations": data["observations"],
                            "last_value": float(data["observations"][0]["value"]) if data["observations"][0]["value"] != "." else None,
                            "last_date": data["observations"][0]["date"]
                        }
                    elif "error_code" in data:
                        print(f"FRED API error for {series_id}: {data.get('error_message', 'Unknown error')}")
                        return None
                    else:
                        print(f"FRED: No observations for {series_id}")
                        return None
            except Exception as e:
                print(f"FRED fetch error for {series_id}: {e}")
                return None
    
    @staticmethod
    def _linear_score(value: float, best: float, worst: float) -> float:
        """Linear score 0.0-1.0 between best and worst thresholds.
        If best < worst: lower value = better (e.g., NFCI, HY Spread).
        If best > worst: higher value = better (e.g., Cu/Au ratio)."""
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

    async def fetch_nfci(self) -> Optional[Dict[str, Any]]:
        """Fetch NFCI (Chicago Fed National Financial Conditions Index)."""
        data = await self.fetch_series("NFCI", limit=10)
        if data and data["last_value"] is not None:
            value = data["last_value"]
            # Linear: -0.5 (loose) = 1.0, +0.5 (tight) = 0.0
            score = self._linear_score(value, best=-0.5, worst=0.5)
            return {
                "value": value,
                "score": score,
                "status": self._score_status(score),
                "date": data["last_date"],
                "description": "Financial Conditions Index"
            }
        return None

    async def fetch_hy_spread(self) -> Optional[Dict[str, Any]]:
        """Fetch High Yield Spread."""
        data = await self.fetch_series("BAMLH0A0HYM2", limit=10)
        if data and data["last_value"] is not None:
            value = data["last_value"]
            # Linear: 2.5% (tight) = 1.0, 6.0% (wide) = 0.0
            score = self._linear_score(value, best=2.5, worst=6.0)
            return {
                "value": value,
                "value_pct": f"{value}%",
                "score": score,
                "status": self._score_status(score),
                "date": data["last_date"],
                "description": "High Yield Spread"
            }
        return None

    async def fetch_treasury_2y(self) -> Optional[Dict[str, Any]]:
        """Fetch 2-Year Treasury Rate."""
        data = await self.fetch_series("DGS2", limit=10)
        if data and data["last_value"] is not None:
            return {
                "value": data["last_value"],
                "value_pct": f"{data['last_value']}%",
                "date": data["last_date"],
                "description": "2-Year Treasury"
            }
        return None
    
    async def fetch_fed_balance(self) -> Optional[Dict[str, Any]]:
        """Fetch Fed Balance Sheet (WALCL)."""
        data = await self.fetch_series("WALCL", limit=20)
        if data and data["last_value"] is not None:
            value = data["last_value"]
            return {
                "value": value,
                "value_trillion": round(value / 1000, 2),
                "date": data["last_date"],
                "description": "Fed Balance Sheet"
            }
        return None
    
    async def fetch_treasury_general(self) -> Optional[Dict[str, Any]]:
        """Fetch Treasury General Account (WTREGEN)."""
        data = await self.fetch_series("WTREGEN", limit=20)
        if data and data["last_value"] is not None:
            value = data["last_value"]
            return {
                "value": value,
                "value_billion": round(value, 2),
                "date": data["last_date"],
                "description": "Treasury General Account"
            }
        return None
    
    async def fetch_rrp(self) -> Optional[Dict[str, Any]]:
        """Fetch Reverse Repo (RRPONTSYD)."""
        data = await self.fetch_series("RRPONTSYD", limit=20)
        if data and data["last_value"] is not None:
            value = data["last_value"]
            return {
                "value": value,
                "value_billion": round(value, 2),
                "date": data["last_date"],
                "description": "Reverse Repo"
            }
        return None
    
    async def fetch_fed_funds(self) -> Optional[Dict[str, Any]]:
        """Fetch Fed Funds Rate."""
        data = await self.fetch_series("DFF", limit=10)
        if data and data["last_value"] is not None:
            value = data["last_value"]
            return {
                "value": value,
                "value_pct": f"{value}%",
                "date": data["last_date"],
                "description": "Fed Funds Rate"
            }
        return None
    
    async def fetch_treasury_10y(self) -> Optional[Dict[str, Any]]:
        """Fetch 10-Year Treasury Rate."""
        data = await self.fetch_series("DGS10", limit=10)
        if data and data["last_value"] is not None:
            value = data["last_value"]
            return {
                "value": value,
                "value_pct": f"{value}%",
                "date": data["last_date"],
                "description": "10-Year Treasury"
            }
        return None
    
    async def calculate_net_liquidity(self) -> Optional[Dict[str, Any]]:
        """Calculate Net Liquidity: WALCL - WTREGEN - RRPONTSYD."""
        walcl = await self.fetch_fed_balance()
        wtregen = await self.fetch_treasury_general()
        rrp = await self.fetch_rrp()
        
        if walcl and wtregen and rrp:
            # Convert to same units (billions)
            walcl_b = walcl["value"]  # Already in billions
            wtregen_b = wtregen["value"]
            rrp_b = rrp["value"]
            
            net_liq = walcl_b - wtregen_b - rrp_b
            
            # Score based on absolute level as proxy
            # $6T+ = abundant = 1.0, $4T = tight = 0.0
            score = self._linear_score(net_liq, best=6000, worst=4000)
            status = self._score_status(score)
            
            return {
                "value": net_liq,
                "value_trillion": round(net_liq / 1000, 2),
                "score": score,
                "status": status,
                "components": {
                    "walcl": walcl_b,
                    "wtregen": wtregen_b,
                    "rrp": rrp_b
                },
                "description": "Net Liquidity"
            }
        return None


# Singleton instance
fred_fetcher = FREDFetcher()
