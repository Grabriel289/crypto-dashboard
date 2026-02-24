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
    
    async def fetch_nfci(self) -> Optional[Dict[str, Any]]:
        """Fetch NFCI (Chicago Fed National Financial Conditions Index)."""
        data = await self.fetch_series("NFCI", limit=10)
        if data and data["last_value"] is not None:
            value = data["last_value"]
            # Scoring: < 0 = 1.0pt, 0-0.5 = 0.5pt, > 0.5 = 0pt
            if value < 0:
                score = 1.0
                status = "🟢"
            elif value < 0.5:
                score = 0.5
                status = "🟡"
            else:
                score = 0.0
                status = "🔴"
            
            return {
                "value": value,
                "score": score,
                "status": status,
                "date": data["last_date"],
                "description": "Financial Conditions Index"
            }
        return None
    
    async def fetch_hy_spread(self) -> Optional[Dict[str, Any]]:
        """Fetch High Yield Spread."""
        data = await self.fetch_series("BAMLH0A0HYM2", limit=10)
        if data and data["last_value"] is not None:
            value = data["last_value"]
            # Scoring: < 3.5% = 1.0pt, 3.5-5.5% = 0.5pt, > 5.5% = 0pt
            if value < 3.5:
                score = 1.0
                status = "[GREEN]"
            elif value < 5.5:
                score = 0.5
                status = "[YELLOW]"
            else:
                score = 0.0
                status = "[RED]"
            
            return {
                "value": value,
                "value_pct": f"{value}%",
                "score": score,
                "status": status,
                "date": data["last_date"],
                "description": "High Yield Spread"
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
            
            # Calculate YoY change (simplified - using last year's value estimate)
            # For proper YoY, would need historical data
            # Scoring: YoY > 5% = 1.0pt, 0-5% = 0.5pt, < 0 = 0pt
            # Simplified: assume neutral for now
            score = 0.5
            status = "[YELLOW]"
            
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
