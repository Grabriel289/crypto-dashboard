"""Farside BTC ETF flow scraper for Gold Cannibalization indicator."""
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import os


class FarsideScraper:
    """Scrape BTC ETF flow data from farside.co.uk"""
    
    URL = "https://farside.co.uk/btc/"
    CACHE_FILE = ".cache/farside_etf.json"
    CACHE_TTL_HOURS = 6  # Update every 6 hours
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        try:
            os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
        except Exception:
            pass  # Ignore if cannot create cache directory
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached data if fresh."""
        try:
            if os.path.exists(self.CACHE_FILE):
                with open(self.CACHE_FILE, 'r') as f:
                    cache = json.load(f)
                
                # Check if cache is fresh
                cached_time = datetime.fromisoformat(cache.get('timestamp', ''))
                age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                
                if age_hours < self.CACHE_TTL_HOURS:
                    return cache.get('data')
        except Exception as e:
            print(f"[Farside] Cache load error: {e}")
        return None
    
    def _save_cache(self, data: Dict[str, Any]):
        """Save data to cache."""
        try:
            cache = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(self.CACHE_FILE, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            print(f"[Farside] Cache save error: {e}")
    
    async def scrape_etf_flows(self) -> Optional[Dict[str, Any]]:
        """
        Scrape BTC ETF daily flow data from farside.co.uk
        
        Returns:
            {
                'date': '2024-01-15',
                'total_flow': 450.5,  # in millions USD
                'flows': {
                    'IBIT': 250.3,
                    'FBTC': 120.1,
                    'ARKB': 45.2,
                    ...
                },
                'cumulative_since_launch': 5000.2
            }
        """
        # Check cache first
        cached = self._load_cache()
        if cached:
            print("[Farside] Using cached ETF flow data")
            return cached
        
        try:
            session = await self._get_session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            async with session.get(self.URL, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f"[Farside] HTTP {response.status}")
                    return None
                
                html = await response.text()
                
                # Parse the HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the table with ETF data
                # The table typically has class or id related to ETF flows
                tables = soup.find_all('table')
                
                etf_data = {}
                latest_date = None
                total_flow = 0.0
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            # Try to extract ETF ticker and flow
                            text = row.get_text()
                            
                            # Look for ETF tickers (IBIT, FBTC, ARKB, etc.)
                            # and their corresponding flow values
                            # This is a simplified parser - may need adjustment
                            # based on actual HTML structure
                            
                # If scraping fails to find data, return None
                # In production, you'd need to inspect the actual HTML structure
                print("[Farside] Scraping not fully implemented - using fallback")
                return None
                
        except Exception as e:
            print(f"[Farside] Scraping error: {e}")
            return None
    
    def get_gold_cannibalization_signal(self, etf_flows: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert ETF flows to Gold Cannibalization signal.
        
        Logic:
        - Strong inflows (> $200M/day) = Money moving from Gold to BTC = 🟢
        - Moderate inflows ($50-200M) = Some rotation = 🟡
        - Outflows (< 0) = BTC to Gold = 🔴
        - Neutral = ⚪
        """
        if not etf_flows:
            return {
                "active": False,
                "status": "⚪",
                "detail": "No ETF flow data available",
                "flow_24h": None,
                "signal": "neutral"
            }
        
        flow_24h = etf_flows.get('total_flow', 0)
        
        if flow_24h > 200:
            return {
                "active": True,
                "status": "🟢",
                "detail": f"Strong BTC ETF inflows: ${flow_24h:.0f}M (Gold → BTC)",
                "flow_24h": flow_24h,
                "signal": "strong_inflow"
            }
        elif flow_24h > 50:
            return {
                "active": True,
                "status": "🟡",
                "detail": f"Moderate BTC ETF inflows: ${flow_24h:.0f}M",
                "flow_24h": flow_24h,
                "signal": "moderate_inflow"
            }
        elif flow_24h < 0:
            return {
                "active": True,
                "status": "🔴",
                "detail": f"BTC ETF outflows: ${flow_24h:.0f}M (BTC → Gold/stocks)",
                "flow_24h": flow_24h,
                "signal": "outflow"
            }
        else:
            return {
                "active": False,
                "status": "⚪",
                "detail": f"Neutral ETF flows: ${flow_24h:.0f}M",
                "flow_24h": flow_24h,
                "signal": "neutral"
            }


# Singleton instance
farside_scraper = FarsideScraper()
