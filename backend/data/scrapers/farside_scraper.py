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
            pass
    
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
        """Parse flow value from text."""
        try:
            if not text or text.strip() == '-' or text.strip() == '':
                return None
            
            cleaned = text.replace('$', '').replace('M', '').replace(',', '').strip()
            
            # Handle parentheses for negative numbers: (50.5) -> -50.5
            if '(' in cleaned and ')' in cleaned:
                cleaned = cleaned.replace('(', '-').replace(')', '')
            
            # Handle color-coded cells (might have span tags stripped)
            cleaned = cleaned.replace('−', '-')  # Unicode minus
            
            return float(cleaned)
        except (ValueError, AttributeError) as e:
            print(f"[Farside] Parse error for '{text}': {e}")
            return None
    
    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """Extract date from any text."""
        # Try various date patterns
        patterns = [
            r'(\w{3,})\s+(\d{1,2}),?\s+(\d{4})',  # January 15, 2025 or Jan 15 2025
            r'(\d{1,2})\s+(\w{3,})\s+(\d{4})',    # 15 Jan 2025
            r'(\d{4})-(\d{2})-(\d{2})',            # 2025-01-15
            r'(\d{2})/(\d{2})/(\d{4})',            # 01/15/2025
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if pattern.startswith(r'(\w{3,})'):
                        month_str = match.group(1)[:3]  # Take first 3 chars
                        date_str = f"{month_str} {match.group(2)}, {match.group(3)}"
                        dt = datetime.strptime(date_str, "%b %d, %Y")
                    elif pattern.startswith(r'(\d{1,2})'):
                        date_str = f"{match.group(1)} {match.group(2)[:3]} {match.group(3)}"
                        dt = datetime.strptime(date_str, "%d %b %Y")
                    elif pattern.startswith(r'(\d{4})-'):
                        dt = datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", "%Y-%m-%d")
                    else:
                        dt = datetime.strptime(f"{match.group(1)}/{match.group(2)}/{match.group(3)}", "%m/%d/%Y")
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        return None
    
    async def scrape_etf_flows(self) -> Optional[Dict[str, Any]]:
        """
        Scrape BTC ETF daily flow data from farside.co.uk
        """
        # Check cache first
        cached = self._load_cache()
        if cached:
            return cached
        
        try:
            session = await self._get_session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
            
            print(f"[Farside] Fetching from {self.URL}...")
            
            async with session.get(self.URL, headers=headers, timeout=30, ssl=False) as response:
                print(f"[Farside] Response status: {response.status}")
                
                if response.status != 200:
                    print(f"[Farside] HTTP error {response.status}")
                    return self._get_fallback_data()
                
                html = await response.text()
                print(f"[Farside] Received {len(html)} bytes")
                
                # Debug: Save HTML for inspection
                try:
                    with open('.cache/farside_debug.html', 'w', encoding='utf-8') as f:
                        f.write(html)
                except:
                    pass
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all tables
                tables = soup.find_all('table')
                print(f"[Farside] Found {len(tables)} tables")
                
                if not tables:
                    print("[Farside] No tables found in HTML")
                    return self._get_fallback_data()
                
                # Look for the table with ETF data
                etf_table = None
                for i, table in enumerate(tables):
                    text = table.get_text()
                    # Check for ETF tickers or typical table headers
                    if any(ticker in text for ticker in ['IBIT', 'FBTC', 'ARKB', 'BITB']):
                        etf_table = table
                        print(f"[Farside] Found ETF table at index {i}")
                        break
                    elif 'Total' in text and ('$' in text or 'M' in text):
                        # Might be the right table
                        etf_table = table
                        print(f"[Farside] Found potential table at index {i}")
                        break
                
                if not etf_table:
                    print("[Farside] No ETF table found")
                    # Debug: print first 500 chars of page
                    print(f"[Farside] Page preview: {soup.get_text()[:500]}")
                    return self._get_fallback_data()
                
                # Parse the table
                rows = etf_table.find_all('tr')
                print(f"[Farside] Table has {len(rows)} rows")
                
                if len(rows) < 2:
                    print("[Farside] Table has insufficient rows")
                    return self._get_fallback_data()
                
                # Get headers from first row
                header_row = rows[0]
                headers = header_row.find_all(['th', 'td'])
                print(f"[Farside] Headers: {[h.get_text(strip=True) for h in headers]}")
                
                # Find the most recent date column (usually second column, first is ETF name)
                latest_date = None
                date_column_index = 1
                
                for i, header in enumerate(headers):
                    header_text = header.get_text(strip=True)
                    if i > 0:  # Skip first column (ETF names)
                        date = self._extract_date_from_text(header_text)
                        if date:
                            latest_date = date
                            date_column_index = i
                            print(f"[Farside] Found date: {date} at column {i}")
                            break
                
                # If no date found in headers, try to find it in page title or elsewhere
                if not latest_date:
                    title = soup.find('title')
                    if title:
                        latest_date = self._extract_date_from_text(title.get_text())
                    if not latest_date:
                        latest_date = datetime.now().strftime("%Y-%m-%d")
                        print(f"[Farside] Using today's date: {latest_date}")
                
                # Parse ETF flows
                etf_flows = {}
                total_flow = None
                
                for row_idx, row in enumerate(rows[1:], 1):  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 2:
                        continue
                    
                    # Get ETF name from first column
                    etf_cell = cells[0]
                    etf_name = etf_cell.get_text(strip=True)
                    
                    # Skip empty rows
                    if not etf_name:
                        continue
                    
                    # Check if this is the Total row
                    is_total = 'total' in etf_name.lower()
                    
                    # Get flow value from date column
                    if len(cells) > date_column_index:
                        flow_cell = cells[date_column_index]
                        flow_text = flow_cell.get_text(strip=True)
                        
                        # Debug
                        print(f"[Farside] Row {row_idx}: {etf_name} = '{flow_text}'")
                        
                        flow = self._parse_flow_value(flow_text)
                        
                        if flow is not None:
                            if is_total:
                                total_flow = flow
                                print(f"[Farside] Total flow: ${total_flow:.1f}M")
                            else:
                                # Match to known ticker
                                ticker = None
                                for t in self.ETF_MAPPING.keys():
                                    if t in etf_name.upper():
                                        ticker = t
                                        break
                                
                                if ticker:
                                    etf_flows[ticker] = flow
                                    print(f"[Farside] {ticker}: ${flow:.1f}M")
                                elif etf_name:
                                    # Use name as-is
                                    etf_flows[etf_name] = flow
                
                # If no total found but we have individual flows, calculate it
                if total_flow is None and etf_flows:
                    total_flow = sum(etf_flows.values())
                    print(f"[Farside] Calculated total: ${total_flow:.1f}M")
                
                # Check if we got any data
                if not etf_flows and total_flow is None:
                    print("[Farside] No data extracted from table")
                    return self._get_fallback_data()
                
                result = {
                    'date': latest_date,
                    'total_flow': round(total_flow, 1) if total_flow else 0.0,
                    'flows': etf_flows,
                    'cumulative_since_launch': 0.0,  # Would need separate calculation
                    'source': 'farside_scraped',
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Save to cache
                self._save_cache(result)
                
                print(f"[Farside] Success: ${result['total_flow']:.1f}M on {result['date']}")
                return result
                
        except Exception as e:
            print(f"[Farside] Scraping error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> Optional[Dict[str, Any]]:
        """Get fallback data when scraping fails."""
        print("[Farside] Returning fallback data")
        return {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'total_flow': 0.0,
            'flows': {},
            'cumulative_since_launch': 0.0,
            'source': 'fallback',
            'note': 'Scraping failed - check connection or site structure'
        }
    
    def get_gold_cannibalization_signal(self, etf_flows: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert ETF flows to Gold Cannibalization signal.
        """
        if not etf_flows:
            return {
                "active": False,
                "status": "⚪",
                "detail": "No ETF flow data available",
                "flow_24h": None,
                "signal": "neutral",
                "individual_etfs": {}
            }
        
        # Check if we have real data or fallback
        if etf_flows.get('source') == 'fallback':
            return {
                "active": False,
                "status": "⚪",
                "detail": f"No live data: {etf_flows.get('note', 'Scraping unavailable')}",
                "flow_24h": None,
                "signal": "neutral",
                "individual_etfs": {},
                "is_fallback": True
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
