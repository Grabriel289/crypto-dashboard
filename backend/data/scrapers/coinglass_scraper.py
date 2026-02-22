"""CoinGlass web scraper for derivative data."""
import requests
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import time


class CoinGlassScraper:
    """Scrape derivative sentiment data from CoinGlass."""
    
    BASE_URL = "https://www.coinglass.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # Cache file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.CACHE_FILE = os.path.join(current_dir, "..", "coinglass_cache.json")
    
    def scrape_open_interest(self, symbol: str) -> Dict[str, Any]:
        """Scrape Open Interest from CoinGlass futures page."""
        try:
            url = f"{self.BASE_URL}/en/pro/futures/{symbol}"
            print(f"Fetching {url}...")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for Open Interest data in the page
            oi_data = {
                "open_interest": 0,
                "oi_change_24h": 0,
                "long_short_ratio": 1.0,
                "long_percent": 50.0
            }
            
            # Try to find OI value in page scripts (CoinGlass stores data in JS)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    text = script.string
                    
                    # Look for openInterest patterns
                    oi_match = re.search(r'openInterest["\']?\s*[:=]\s*([\d.]+)', text, re.IGNORECASE)
                    if oi_match:
                        oi_data["open_interest"] = float(oi_match.group(1))
                    
                    # Look for OI change
                    oi_change_match = re.search(r'oiChange(?:24h)?["\']?\s*[:=]\s*([-\d.]+)', text, re.IGNORECASE)
                    if oi_change_match:
                        oi_data["oi_change_24h"] = float(oi_change_match.group(1))
                    
                    # Look for long/short ratio
                    ls_match = re.search(r'longShortRatio["\']?\s*[:=]\s*([\d.]+)', text, re.IGNORECASE)
                    if ls_match:
                        ratio = float(ls_match.group(1))
                        oi_data["long_short_ratio"] = ratio
                        oi_data["long_percent"] = (ratio / (ratio + 1)) * 100
            
            # If no data in scripts, try to find visible elements
            if oi_data["open_interest"] == 0:
                # Look for OI display on page
                text_content = soup.get_text()
                
                # Pattern: $X.XXB or $XXXM for Open Interest
                oi_patterns = [
                    r'Open Interest\s*[:$]?\s*([\d.]+)\s*B',
                    r'OI\s*[:$]?\s*([\d.]+)\s*B',
                    r'\$([\d.]+)\s*B\s*Open Interest',
                ]
                
                for pattern in oi_patterns:
                    match = re.search(pattern, text_content, re.IGNORECASE)
                    if match:
                        oi_data["open_interest"] = float(match.group(1)) * 1e9
                        break
            
            print(f"  Found OI: ${oi_data['open_interest']/1e9:.2f}B")
            return oi_data
            
        except Exception as e:
            print(f"  [ERROR] scraping {symbol}: {e}")
            return None
    
    def scrape_long_short_data(self, symbol: str) -> Dict[str, Any]:
        """Scrape Long/Short ratio data."""
        try:
            # CoinGlass has separate pages for L/S ratios
            url = f"{self.BASE_URL}/en/pro/futures/LongShortRatio/{symbol}"
            print(f"Fetching L/S data for {symbol}...")
            
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            ls_data = {
                "retail_long": 50.0,
                "top_trader_long": 50.0
            }
            
            # Try to extract from page
            text = soup.get_text()
            
            # Look for long percentage patterns
            patterns = [
                r'Long\s*[:$]?\s*(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s*Long',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    ls_data["retail_long"] = float(matches[0])
                    break
            
            return ls_data
            
        except Exception as e:
            print(f"  Error scraping L/S for {symbol}: {e}")
            return None
    
    def scrape_all_data(self) -> Dict[str, Any]:
        """Scrape data for all coins."""
        symbols = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum", 
            "SOL": "Solana"
        }
        
        results = {}
        
        for symbol, name in symbols.items():
            print(f"\nScraping {name} ({symbol})...")
            
            # Scrape OI data
            oi_data = self.scrape_open_interest(symbol)
            
            # Scrape L/S data
            ls_data = self.scrape_long_short_data(symbol)
            
            if oi_data:
                results[f"{symbol}USDT"] = {
                    "symbol": symbol,
                    "open_interest": oi_data.get("open_interest", 0),
                    "oi_change_24h": oi_data.get("oi_change_24h", 0),
                    "retail_long_percent": oi_data.get("long_percent", 50) if oi_data.get("long_percent") else (ls_data.get("retail_long", 50) if ls_data else 50),
                    "top_trader_long_percent": ls_data.get("top_trader_long", 50) if ls_data else 50,
                    "taker_buy_percent": 50,  # Default, hard to scrape
                    "scraped_at": datetime.now().isoformat(),
                    "is_scraped": True
                }
            else:
                # Use fallback if scraping failed
                results[f"{symbol}USDT"] = self._get_fallback_data(symbol)
                results[f"{symbol}USDT"]["scraped_at"] = datetime.now().isoformat()
                results[f"{symbol}USDT"]["is_scraped"] = False
            
            # Wait between requests to be nice
            time.sleep(3)
        
        # Save results
        output = {
            "coins": results,
            "scraped_at": datetime.now().isoformat(),
            "next_scrape": (datetime.now() + timedelta(hours=24)).isoformat(),
            "source": "coinglass_scraper"
        }
        
        self.save_cache(output)
        return output
    
    def _get_fallback_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback data when scraping fails."""
        fallbacks = {
            "BTC": {
                "symbol": "BTC",
                "open_interest": 5362792767.0,
                "oi_change_24h": -3.9,
                "retail_long_percent": 65.3,
                "top_trader_long_percent": 55.7,
                "taker_buy_percent": 58.2,
                "is_fallback": True
            },
            "ETH": {
                "symbol": "ETH",
                "open_interest": 3472657347.0,
                "oi_change_24h": -2.8,
                "retail_long_percent": 72.3,
                "top_trader_long_percent": 60.2,
                "taker_buy_percent": 52.1,
                "is_fallback": True
            },
            "SOL": {
                "symbol": "SOL",
                "open_interest": 812269184.0,
                "oi_change_24h": -4.8,
                "retail_long_percent": 71.8,
                "top_trader_long_percent": 55.2,
                "taker_buy_percent": 64.5,
                "is_fallback": True
            }
        }
        return fallbacks.get(symbol, fallbacks["BTC"])
    
    def save_cache(self, data: Dict[str, Any]):
        """Save scraped data to cache file."""
        try:
            # Ensure directory exists
            cache_dir = os.path.dirname(self.CACHE_FILE)
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
            
            with open(self.CACHE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\n[SAVED] Cache to {self.CACHE_FILE}")
            
        except Exception as e:
            print(f"[ERROR] Saving cache: {e}")
    
    def load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached data if it exists and is fresh (< 24h)."""
        try:
            if not os.path.exists(self.CACHE_FILE):
                print("No cache file found")
                return None
            
            with open(self.CACHE_FILE, 'r') as f:
                cache = json.load(f)
            
            # Check if cache is fresh
            scraped_at = datetime.fromisoformat(cache.get("scraped_at", "2000-01-01"))
            age = datetime.now() - scraped_at
            
            if age < timedelta(hours=24):
                print(f"[OK] Using cached data from {scraped_at.strftime('%Y-%m-%d %H:%M')}")
                return cache
            else:
                print(f"[EXPIRED] Cache ({age.total_seconds()/3600:.1f} hours old)")
                return None
                
        except Exception as e:
            print(f"[ERROR] Loading cache: {e}")
            return None
    
    def get_data(self) -> Dict[str, Any]:
        """Get data - either from cache or by scraping."""
        # Try cache first
        cache = self.load_cache()
        if cache:
            return cache
        
        # Scrape new data
        print("\n🔍 No fresh cache. Scraping CoinGlass...")
        return self.scrape_all_data()


# Easy import function
def get_coinglass_data() -> Dict[str, Any]:
    """Get derivative data from CoinGlass (cached or scraped)."""
    scraper = CoinGlassScraper()
    return scraper.get_data()


# Test if run directly
if __name__ == "__main__":
    print("="*60)
    print("CoinGlass Scraper Test")
    print("="*60)
    
    scraper = CoinGlassScraper()
    data = scraper.get_data()
    
    print("\n" + "="*60)
    print("RESULT:")
    print("="*60)
    print(json.dumps(data, indent=2))
