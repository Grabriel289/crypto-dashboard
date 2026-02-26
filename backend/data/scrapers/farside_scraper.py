"""Farside BTC ETF flow scraper for Gold Cannibalization indicator."""
import aiohttp
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import os
import re


class FarsideScraper:
    """Scrape BTC ETF flow data from farside.co.uk"""
    
    URL = "https://farside.co.uk/btc/"
    CACHE_FILE = ".cache/farside_etf.json"
    CACHE_TTL_HOURS = 6  # Update every 6 hours
    
    # Known ETF tickers and their full names
    ETF_MAPPING = {
        'IBIT': 'iShares Bitcoin Trust',
        'FBTC': 'Fidelity Wise Origin',
        'ARKB': 'ARK 21Shares',
        'BITB': 'Bitwise Bitcoin ETF',
        'BTCO': 'Invesco Galaxy',
        'EZBC': 'Franklin Templeton',
        'BRRR': 'Valkyrie Bitcoin Fund',
        'HODL': 'VanEck Bitcoin Trust',
        'BTCW': 'WisdomTree Bitcoin Fund',
        'GBTC': 'Grayscale Bitcoin Trust',
    }
    
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
                    print(f"[Farside] Using cached data ({age_hours:.1f}h old)")
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
    
    def _parse_flow_value(self, text: str) -> Optional[float]:
        """Parse flow value from text (handles $250.5M or -$50.2M format)."""
        try:
            # Remove $, M, commas and whitespace
            cleaned = text.replace('$', '').replace('M', '').replace(',', '').strip()
            # Handle parentheses for negative numbers
            if '(' in cleaned and ')' in cleaned:
                cleaned = cleaned.replace('(', '-').replace(')', '')
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _extract_date_from_header(self, text: str) -> Optional[str]:
        """Extract date from table header text."""
        # Look for date patterns like "Jan 15, 2025" or "15 Jan 2025"
        date_patterns = [
            r'(\w{3})\s+(\d{1,2}),?\s+(\d{4})',  # Jan 15, 2025 or Jan 15 2025
            r'(\d{1,2})\s+(\w{3})\s+(\d{4})',    # 15 Jan 2025
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if pattern.startswith(r'(\w{3})'):
                        # Format: Mon DD, YYYY
                        date_str = f"{match.group(1)} {match.group(2)}, {match.group(3)}"
                        dt = datetime.strptime(date_str, "%b %d, %Y")
                    else:
                        # Format: DD Mon YYYY
                        date_str = f"{match.group(1)} {match.group(2)} {match.group(3)}"
                        dt = datetime.strptime(date_str, "%d %b %Y")
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        return None
    
    async def scrape_etf_flows(self) -> Optional[Dict[str, Any]]:
        """
        Scrape BTC ETF daily flow data from farside.co.uk
        
        Farside table structure typically has:
        - Header row with dates
        - Rows for each ETF (IBIT, FBTC, etc.)
        - Last row is 'Total' 
        - Values are in $M format
        """
        # Check cache first
        cached = self._load_cache()
        if cached:
            return cached
        
        try:
            session = await self._get_session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with session.get(self.URL, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f"[Farside] HTTP {response.status}")
                    return self._get_fallback_data()
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all tables
                tables = soup.find_all('table')
                
                if not tables:
                    print("[Farside] No tables found")
                    return self._get_fallback_data()
                
                # The main ETF flow table is usually the first or second table
                etf_table = None
                for table in tables:
                    # Check if this looks like the ETF flow table
                    text = table.get_text()
                    if any(ticker in text for ticker in ['IBIT', 'FBTC', 'ARKB', 'Total']):
                        etf_table = table
                        break
                
                if not etf_table:
                    print("[Farside] ETF table not found")
                    return self._get_fallback_data()
                
                # Parse the table
                rows = etf_table.find_all('tr')
                if len(rows) < 3:
                    print("[Farside] Table has insufficient rows")
                    return self._get_fallback_data()
                
                # Get headers (dates) from first row
                header_row = rows[0]
                headers = header_row.find_all(['th', 'td'])
                
                # Find the most recent date column (usually column index 1, after ETF name)
                latest_date = None
                date_column_index = 1  # Default to second column
                
                for i, header in enumerate(headers):
                    header_text = header.get_text(strip=True)
                    if i > 0:  # Skip first column (ETF names)
                        date = self._extract_date_from_header(header_text)
                        if date:
                            latest_date = date
                            date_column_index = i
                            break  # First date column is most recent
                
                # Parse ETF flows
                etf_flows = {}
                total_flow = 0.0
                cumulative_flow = 0.0
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 2:
                        continue
                    
                    # Get ETF name/ticker from first column
                    etf_name = cells[0].get_text(strip=True)
                    
                    # Check if this is the Total row
                    is_total = 'total' in etf_name.lower()
                    
                    # Get flow value from date column
                    if len(cells) > date_column_index:
                        flow_text = cells[date_column_index].get_text(strip=True)
                        flow = self._parse_flow_value(flow_text)
                        
                        if flow is not None:
                            if is_total:
                                total_flow = flow
                            else:
                                # Try to match ETF name to ticker
                                ticker = None
                                for t, full_name in self.ETF_MAPPING.items():
                                    if t in etf_name or full_name.lower() in etf_name.lower():
                                        ticker = t
                                        break
                                
                                if ticker:
                                    etf_flows[ticker] = flow
                                elif etf_name:
                                    # Use name as-is if we can't map it
                                    etf_flows[etf_name] = flow
                
                # If we didn't get a total, calculate it
                if total_flow == 0 and etf_flows:
                    total_flow = sum(etf_flows.values())
                
                # Try to get cumulative flow (usually in a summary section or last column)
                # For now, use a reasonable estimate or search for it
                cumulative_flow = self._estimate_cumulative(soup)
                
                result = {
                    'date': latest_date or datetime.now().strftime("%Y-%m-%d"),
                    'total_flow': round(total_flow, 1),
                    'flows': etf_flows,
                    'cumulative_since_launch': round(cumulative_flow, 1),
                    'source': 'farside_scraped',
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Save to cache
                self._save_cache(result)
                
                print(f"[Farside] Successfully scraped: ${total_flow:.1f}M flow on {result['date']}")
                return result
                
        except Exception as e:
            print(f"[Farside] Scraping error: {e}")
            return self._get_fallback_data()
    
    def _estimate_cumulative(self, soup: BeautifulSoup) -> float:
        """Try to extract cumulative flow from page text."""
        try:
            # Look for text containing cumulative totals
            page_text = soup.get_text()
            
            # Pattern: "cumulative" or "total" followed by a number
            patterns = [
                r'cumulative.*?\$?([\d,]+\.?\d*)\s*[Bb]illion',
                r'cumulative.*?\$?([\d,]+\.?\d*)\s*[Mm]illion',
                r'total inflows.*?\$?([\d,]+\.?\d*)\s*[Bb]illion',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    value = float(match.group(1).replace(',', ''))
                    # Convert to millions
                    if '[Bb]illion' in pattern:
                        value *= 1000
                    return value
        except Exception:
            pass
        
        # Default: return 0 (will be calculated from history if available)
        return 0.0
    
    def _get_fallback_data(self) -> Optional[Dict[str, Any]]:
        """Get fallback data when scraping fails."""
        return {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'total_flow': 0.0,
            'flows': {},
            'cumulative_since_launch': 0.0,
            'source': 'fallback',
            'note': 'Using fallback - scraping failed'
        }
    
    def get_gold_cannibalization_signal(self, etf_flows: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert ETF flows to Gold Cannibalization signal.
        
        Enhanced logic:
        - Strong inflows (> $300M/day) = Heavy Gold → BTC rotation = 🟢🟢
        - Moderate inflows ($100-300M) = Steady rotation = 🟢
        - Small inflows ($20-100M) = Some interest = 🟡
        - Outflows (< 0) = BTC → Gold = 🔴
        - Neutral = ⚪
        
        Also tracks individual ETF performance for deeper insights.
        """
        if not etf_flows or etf_flows.get('source') == 'fallback':
            return {
                "active": False,
                "status": "⚪",
                "detail": "No ETF flow data available - check Farside connection",
                "flow_24h": None,
                "signal": "neutral",
                "individual_etfs": {}
            }
        
        flow_24h = etf_flows.get('total_flow', 0)
        flows = etf_flows.get('flows', {})
        date = etf_flows.get('date', 'Unknown')
        
        # Analyze individual ETFs
        individual_analysis = {}
        top_inflow = None
        top_outflow = None
        
        for ticker, flow in flows.items():
            if ticker == 'GBTC':
                # GBTC outflows are expected (conversion discount arbitrage)
                status = "expected" if flow < 0 else "unusual"
                individual_analysis[ticker] = {"flow": flow, "status": status, "note": "Legacy trust conversion"}
            else:
                if flow > 0:
                    individual_analysis[ticker] = {"flow": flow, "status": "inflow"}
                    if top_inflow is None or flow > top_inflow[1]:
                        top_inflow = (ticker, flow)
                elif flow < 0:
                    individual_analysis[ticker] = {"flow": flow, "status": "outflow"}
                    if top_outflow is None or flow < top_outflow[1]:
                        top_outflow = (ticker, flow)
                else:
                    individual_analysis[ticker] = {"flow": 0, "status": "neutral"}
        
        # Build detail message
        detail_parts = [f"${flow_24h:+.0f}M on {date}"]
        if top_inflow:
            detail_parts.append(f"Leader: {top_inflow[0]} (+${top_inflow[1]:.1f}M)")
        if top_outflow:
            detail_parts.append(f"Weak: {top_outflow[0]} ({top_outflow[1]:.1f}M)")
        
        # Determine signal
        if flow_24h > 300:
            return {
                "active": True,
                "status": "🟢",
                "detail": " | ".join(detail_parts),
                "flow_24h": flow_24h,
                "signal": "strong_inflow",
                "interpretation": "Heavy rotation from Gold to BTC ETFs",
                "individual_etfs": individual_analysis,
                "cumulative": etf_flows.get('cumulative_since_launch')
            }
        elif flow_24h > 100:
            return {
                "active": True,
                "status": "🟢",
                "detail": " | ".join(detail_parts),
                "flow_24h": flow_24h,
                "signal": "moderate_inflow",
                "interpretation": "Steady BTC ETF demand",
                "individual_etfs": individual_analysis,
                "cumulative": etf_flows.get('cumulative_since_launch')
            }
        elif flow_24h > 20:
            return {
                "active": True,
                "status": "🟡",
                "detail": " | ".join(detail_parts),
                "flow_24h": flow_24h,
                "signal": "light_inflow",
                "interpretation": "Modest BTC ETF interest",
                "individual_etfs": individual_analysis,
                "cumulative": etf_flows.get('cumulative_since_launch')
            }
        elif flow_24h < -50:
            return {
                "active": True,
                "status": "🔴",
                "detail": " | ".join(detail_parts),
                "flow_24h": flow_24h,
                "signal": "outflow",
                "interpretation": "BTC ETF outflows - rotation to Gold/stocks",
                "individual_etfs": individual_analysis,
                "cumulative": etf_flows.get('cumulative_since_launch')
            }
        else:
            return {
                "active": False,
                "status": "⚪",
                "detail": f"Neutral flows: ${flow_24h:.0f}M on {date}",
                "flow_24h": flow_24h,
                "signal": "neutral",
                "interpretation": "Balanced ETF flows",
                "individual_etfs": individual_analysis,
                "cumulative": etf_flows.get('cumulative_since_launch')
            }


# Singleton instance
farside_scraper = FarsideScraper()
