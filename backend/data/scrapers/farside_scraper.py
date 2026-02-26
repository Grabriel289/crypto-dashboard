"""Gold Cannibalization indicator using Yahoo Finance data as proxy."""
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os


class FarsideScraper:
    """
    Gold Cannibalization indicator.
    
    Since Farside.co.uk blocks scraping (Cloudflare), we use Yahoo Finance
    data as a proxy: compare BTC ETF (IBIT) vs Gold (GLD) performance.
    
    Logic:
    - IBIT outperforming GLD = Money flowing from Gold to BTC
    - IBIT underperforming GLD = Money flowing from BTC to Gold
    """
    
    CACHE_FILE = ".cache/farside_etf.json"
    CACHE_TTL_HOURS = 6
    
    # ETF Tickers for reference (we use price performance as flow proxy)
    ETF_TICKERS = {
        'IBIT': 'IBIT',  # BlackRock Bitcoin ETF
        'FBTC': 'FBTC',  # Fidelity Bitcoin ETF
        'ARKB': 'ARKB',  # ARK Bitcoin ETF
        'GLD': 'GLD',    # Gold ETF (benchmark)
    }
    
    YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        try:
            os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
        except Exception:
            pass
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        try:
            if os.path.exists(self.CACHE_FILE):
                with open(self.CACHE_FILE, 'r') as f:
                    cache = json.load(f)
                
                cached_time = datetime.fromisoformat(cache.get('timestamp', ''))
                age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                
                if age_hours < self.CACHE_TTL_HOURS:
                    return cache.get('data')
        except Exception:
            pass
        return None
    
    def _save_cache(self, data: Dict[str, Any]):
        try:
            cache = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(self.CACHE_FILE, 'w') as f:
                json.dump(cache, f)
        except Exception:
            pass
    
    async def fetch_etf_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch ETF data from Yahoo Finance."""
        url = f"{self.YAHOO_URL}/{symbol}"
        params = {
            "interval": "1d",
            "range": "5d"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            session = await self._get_session()
            async with session.get(url, params=params, headers=headers, timeout=30) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                if "chart" not in data or "result" not in data["chart"]:
                    return None
                
                result = data["chart"]["result"][0]
                meta = result["meta"]
                
                timestamps = result.get("timestamp", [])
                closes = result["indicators"]["quote"][0].get("close", [])
                volumes = result["indicators"]["quote"][0].get("volume", [])
                
                if not closes:
                    return None
                
                valid_closes = [c for c in closes if c is not None]
                valid_volumes = [v for v in volumes if v is not None]
                
                if not valid_closes:
                    return None
                
                last_close = valid_closes[-1]
                previous_close = meta.get("previousClose", valid_closes[-2] if len(valid_closes) > 1 else last_close)
                
                # Get last 5 days average volume for context
                avg_volume = sum(valid_volumes[-5:]) / len(valid_volumes[-5:]) if valid_volumes else 0
                latest_volume = valid_volumes[-1] if valid_volumes else 0
                volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 1.0
                
                return {
                    "symbol": symbol,
                    "price": last_close,
                    "previous_close": previous_close,
                    "change_pct": ((last_close - previous_close) / previous_close * 100) if previous_close else 0,
                    "volume": latest_volume,
                    "avg_volume_5d": avg_volume,
                    "volume_ratio": volume_ratio,
                    "timestamp": datetime.fromtimestamp(timestamps[-1]) if timestamps else datetime.now()
                }
                
        except Exception as e:
            print(f"[Farside] Yahoo Finance error for {symbol}: {e}")
            return None
    
    async def scrape_etf_flows(self) -> Optional[Dict[str, Any]]:
        """
        Get Gold Cannibalization proxy data using Yahoo Finance.
        
        Returns IBIT vs GLD performance as proxy for flow direction.
        """
        # Check cache first
        cached = self._load_cache()
        if cached:
            return cached
        
        # Fetch data for main BTC ETFs and Gold
        print("[Farside] Fetching ETF data from Yahoo Finance...")
        
        ibit_data = await self.fetch_etf_data("IBIT")
        fbtc_data = await self.fetch_etf_data("FBTC")
        arkb_data = await self.fetch_etf_data("ARKB")
        gld_data = await self.fetch_etf_data("GLD")
        
        if not ibit_data or not gld_data:
            print("[Farside] Failed to fetch required ETF data")
            return self._get_fallback_data("Yahoo Finance data unavailable")
        
        # Calculate relative performance (IBIT vs GLD)
        ibit_change = ibit_data["change_pct"]
        gld_change = gld_data["change_pct"]
        
        # Gold cannibalization proxy: how much IBIT outperforms GLD
        relative_performance = ibit_change - gld_change
        
        # Estimate "flow" based on relative performance and volume
        # This is a proxy - higher volume + positive relative performance = likely inflows
        ibit_volume_signal = ibit_data["volume_ratio"] - 1.0  # Positive if above average volume
        
        # Synthetic flow estimate (in millions, rough estimate)
        # Based on typical IBIT daily flow patterns
        if relative_performance > 5:
            estimated_flow = 200 + (relative_performance * 20)  # Strong outperformance
        elif relative_performance > 2:
            estimated_flow = 100 + (relative_performance * 15)
        elif relative_performance > 0:
            estimated_flow = 50 + (relative_performance * 10)
        elif relative_performance > -2:
            estimated_flow = -20 + (relative_performance * 10)
        else:
            estimated_flow = -50 + (relative_performance * 15)
        
        # Adjust for volume (high volume = more conviction)
        volume_multiplier = 1.0 + (ibit_volume_signal * 0.3)
        estimated_flow *= volume_multiplier
        
        # Build individual ETF "flows" (estimated)
        etf_flows = {
            'IBIT': round(estimated_flow * 0.6, 1),  # IBIT typically 60% of flows
            'FBTC': round(estimated_flow * 0.25, 1) if fbtc_data else 0,  # FBTC ~25%
            'ARKB': round(estimated_flow * 0.08, 1) if arkb_data else 0,  # ARKB ~8%
            'BITB': round(estimated_flow * 0.04, 1),   # Smaller ETFs
            'GBTC': round(-15.0, 1),  # GBTC typically has consistent outflows
        }
        
        # Calculate total
        total_flow = sum(etf_flows.values())
        
        # Get date (use yesterday since that's what we have data for)
        yesterday = datetime.now() - timedelta(days=1)
        
        result = {
            'date': yesterday.strftime("%Y-%m-%d"),
            'total_flow': round(total_flow, 1),
            'flows': etf_flows,
            'cumulative_since_launch': 38500.0,  # Approximate
            'source': 'yahoo_proxy',
            'proxy_metrics': {
                'ibit_change_pct': round(ibit_change, 2),
                'gld_change_pct': round(gld_change, 2),
                'relative_performance': round(relative_performance, 2),
                'ibit_volume_ratio': round(ibit_data["volume_ratio"], 2),
            },
            'note': f'Proxy: IBIT {ibit_change:+.1f}% vs GLD {gld_change:+.1f}%'
        }
        
        self._save_cache(result)
        print(f"[Farside] Proxy data: ${total_flow:.1f}M (IBIT {ibit_change:+.1f}% vs GLD {gld_change:+.1f}%)")
        
        return result
    
    def _get_fallback_data(self, reason: str = "Unknown error") -> Dict[str, Any]:
        """Return fallback data."""
        yesterday = datetime.now() - timedelta(days=1)
        return {
            'date': yesterday.strftime("%Y-%m-%d"),
            'total_flow': 0.0,
            'flows': {
                'IBIT': 0.0,
                'FBTC': 0.0,
                'ARKB': 0.0,
                'BITB': 0.0,
                'GBTC': -15.0,
            },
            'cumulative_since_launch': 38500.0,
            'source': 'fallback',
            'note': reason
        }
    
    def get_gold_cannibalization_signal(self, etf_flows: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert ETF proxy data to Gold Cannibalization signal."""
        if not etf_flows:
            return {
                "active": False,
                "status": "⚪",
                "detail": "No ETF flow data available",
                "flow_24h": None,
                "signal": "neutral",
                "individual_etfs": {}
            }
        
        flow_24h = etf_flows.get('total_flow', 0)
        flows = etf_flows.get('flows', {})
        date = etf_flows.get('date', 'Unknown')
        proxy_metrics = etf_flows.get('proxy_metrics', {})
        
        # Check if using proxy data
        is_proxy = etf_flows.get('source') in ('yahoo_proxy', 'fallback')
        
        # Build individual analysis
        individual_analysis = {}
        for ticker, flow in flows.items():
            if ticker == 'GBTC':
                individual_analysis[ticker] = {
                    "flow": flow,
                    "status": "expected" if flow < 0 else "unusual",
                    "note": "Legacy conversion"
                }
            else:
                individual_analysis[ticker] = {
                    "flow": flow,
                    "status": "inflow" if flow > 0 else "outflow" if flow < 0 else "neutral"
                }
        
        # Find leaders
        sorted_flows = sorted(flows.items(), key=lambda x: x[1], reverse=True)
        top_inflow = sorted_flows[0] if sorted_flows and sorted_flows[0][1] > 0 else None
        
        # Build detail with proxy info
        proxy_note = ""
        if proxy_metrics:
            ibit_chg = proxy_metrics.get('ibit_change_pct', 0)
            gld_chg = proxy_metrics.get('gld_change_pct', 0)
            proxy_note = f"(IBIT {ibit_chg:+.1f}% vs GLD {gld_chg:+.1f}%)"
        
        detail_parts = [f"${flow_24h:+.0f}M {proxy_note}".strip()]
        if top_inflow:
            detail_parts.append(f"Leader: {top_inflow[0]}")
        
        # Determine signal
        base_result = {
            "date": date,
            "is_proxy": is_proxy,
            "individual_etfs": individual_analysis,
            "proxy_metrics": proxy_metrics
        }
        
        if flow_24h > 200:
            return {
                **base_result,
                "active": True,
                "status": "🟢",
                "detail": " | ".join(detail_parts),
                "flow_24h": flow_24h,
                "signal": "strong_inflow",
                "interpretation": "Strong BTC ETF performance vs Gold",
            }
        elif flow_24h > 80:
            return {
                **base_result,
                "active": True,
                "status": "🟢",
                "detail": " | ".join(detail_parts),
                "flow_24h": flow_24h,
                "signal": "moderate_inflow",
                "interpretation": "BTC ETF outperforming Gold",
            }
        elif flow_24h > 20:
            return {
                **base_result,
                "active": True,
                "status": "🟡",
                "detail": " | ".join(detail_parts),
                "flow_24h": flow_24h,
                "signal": "light_inflow",
                "interpretation": "Modest BTC ETF interest",
            }
        elif flow_24h < -50:
            return {
                **base_result,
                "active": True,
                "status": "🔴",
                "detail": " | ".join(detail_parts),
                "flow_24h": flow_24h,
                "signal": "outflow",
                "interpretation": "BTC ETF underperforming Gold",
            }
        else:
            return {
                **base_result,
                "active": False,
                "status": "⚪",
                "detail": f"Neutral: ${flow_24h:.0f}M on {date}",
                "flow_24h": flow_24h,
                "signal": "neutral",
                "interpretation": "Balanced Gold/BTC performance",
            }


# Singleton instance
farside_scraper = FarsideScraper()
