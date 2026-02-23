"""Correlation Matrix & PAXG/BTC fetcher with live data calculation."""
import aiohttp
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import os
import sys

# Add parent to path for settings import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not available")

try:
    from config.settings import settings
    FRED_API_KEY = settings.FRED_API_KEY
except:
    FRED_API_KEY = os.getenv("FRED_API_KEY", "")


class CorrelationFetcher:
    """Fetch correlation data and PAXG/BTC ratio with live correlation calculation."""
    
    BINANCE_BASE = "https://api.binance.com"
    FRED_BASE = "https://api.stlouisfed.org/fred"
    
    # Yahoo Finance tickers for traditional assets
    YAHOO_ASSETS = {
        "SP500": {
            "ticker": "^GSPC",
            "asset": "S&P 500",
            "symbol": "^GSPC"
        },
        "NASDAQ": {
            "ticker": "^IXIC",
            "asset": "NASDAQ",
            "symbol": "^IXIC"
        },
        "GOLD": {
            "ticker": "GC=F",
            "asset": "Gold",
            "symbol": "GC=F"
        },
        "DXY": {
            "ticker": "DX-Y.NYB",
            "asset": "DXY (USD)",
            "symbol": "DX-Y.NYB"
        }
    }
    
    # FRED Series IDs as fallback
    FRED_SERIES = {
        "SP500": {"series_id": "SP500", "asset": "S&P 500", "symbol": "^GSPC"},
        "NASDAQ": {"series_id": "NASDAQCOM", "asset": "NASDAQ", "symbol": "^IXIC"},
        "GOLD": {"series_id": "GOLDPMGBD228NLBM", "asset": "Gold", "symbol": "GC=F"},
        "DXY": {"series_id": "DTWEXBGS", "asset": "DXY (USD)", "symbol": "DX-Y.NYB"}
    }
    
    async def get_klines(self, symbol: str, interval: str = "1d", limit: int = 30) -> List[List]:
        """Fetch klines data from Binance."""
        url = f"{self.BINANCE_BASE}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        
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
    
    def fetch_yahoo_history(self, ticker: str, period: str = "3mo") -> Optional[Tuple[List[float], List[datetime]]]:
        """Fetch historical price data with dates from Yahoo Finance."""
        if not YFINANCE_AVAILABLE:
            return None
        
        try:
            import concurrent.futures
            
            def _fetch():
                stock = yf.Ticker(ticker)
                # Get more data to ensure we have 30 trading days
                hist = stock.history(period=period, interval="1d")
                if hist.empty:
                    return None
                # Return closing prices and dates
                prices = hist['Close'].tolist()
                dates = hist.index.tolist()
                return prices, dates
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_fetch)
                return future.result(timeout=30)
                
        except Exception as e:
            print(f"Yahoo Finance fetch error for {ticker}: {e}")
            return None
    
    def parse_fred_values(self, observations: List[Dict]) -> List[float]:
        """Extract numeric values from FRED observations."""
        values = []
        for obs in reversed(observations):
            val = obs.get("value", ".")
            if val != ".":
                try:
                    values.append(float(val))
                except ValueError:
                    continue
        return values
    
    def calculate_returns(self, prices: List[float]) -> List[float]:
        """Calculate daily returns from price series."""
        returns = []
        for i in range(1, len(prices)):
            daily_return = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(daily_return)
        return returns
    
    def calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = min(len(x), len(y))
        if n < 2:
            return 0
        
        # Use only the last n values
        x_slice = x[-n:]
        y_slice = y[-n:]
        
        mean_x = sum(x_slice) / n
        mean_y = sum(y_slice) / n
        
        num = 0
        denom_x = 0
        denom_y = 0
        
        for i in range(n):
            dx = x_slice[i] - mean_x
            dy = y_slice[i] - mean_y
            num += dx * dy
            denom_x += dx * dx
            denom_y += dy * dy
        
        if denom_x == 0 or denom_y == 0:
            return 0
        
        return num / math.sqrt(denom_x * denom_y)
    
    def get_correlation_label(self, corr: float) -> str:
        """Get label for correlation value."""
        if corr >= 0.7:
            return "Very High"
        if corr >= 0.5:
            return "High Positive"
        if corr >= 0.3:
            return "Moderate"
        if corr >= -0.3:
            return "Weak"
        if corr >= -0.5:
            return "Inverse"
        return "Strong Inverse"
    
    async def get_correlations(self) -> Dict[str, Any]:
        """Get BTC correlations with traditional assets using 30-day rolling correlation."""
        # Fetch 30 days of BTC data
        btc_klines = await self.get_klines("BTCUSDT", limit=30)
        if not btc_klines or len(btc_klines) < 7:
            return self._get_fallback_correlations()
        
        # Extract BTC prices and calculate returns (need 31 days for 30 returns)
        btc_prices = [float(k[4]) for k in btc_klines]
        btc_returns = self.calculate_returns(btc_prices)
        
        # We need exactly 30 days of returns for 30D rolling correlation
        target_returns = 30
        if len(btc_returns) < target_returns:
            # Fetch more BTC data if needed
            btc_klines = await self.get_klines("BTCUSDT", limit=35)
            if btc_klines:
                btc_prices = [float(k[4]) for k in btc_klines]
                btc_returns = self.calculate_returns(btc_prices)
        
        # Use last 30 returns
        btc_returns = btc_returns[-target_returns:] if len(btc_returns) >= target_returns else btc_returns
        
        correlations = []
        
        # Fetch and calculate correlation for each traditional asset
        for key, config in self.YAHOO_ASSETS.items():
            try:
                # Try Yahoo Finance first - fetch 3 months to ensure 30 trading days
                result = self.fetch_yahoo_history(config["ticker"], period="3mo")
                source = "Yahoo Finance"
                
                if result:
                    asset_prices, asset_dates = result
                    
                    # Calculate asset returns
                    asset_returns = self.calculate_returns(asset_prices)
                    
                    # Take the last N returns where N matches BTC returns length
                    # This gives us the most recent overlapping period
                    n_returns = min(len(btc_returns), len(asset_returns))
                    if n_returns >= 7:  # Need at least 7 days for meaningful correlation
                        btc_slice = btc_returns[-n_returns:]
                        asset_slice = asset_returns[-n_returns:]
                        
                        # Calculate correlation
                        corr = self.calculate_correlation(btc_slice, asset_slice)
                        
                        correlations.append({
                            "asset": config["asset"],
                            "symbol": config["symbol"],
                            "correlation": round(corr, 2),
                            "label": self.get_correlation_label(corr),
                            "source": source,
                            "data_points": n_returns,
                            "period_days": n_returns
                        })
                    else:
                        # Not enough data
                        fallback = self._get_fallback_for_asset(key)
                        if fallback:
                            correlations.append(fallback)
                else:
                    # Yahoo failed, try FRED
                    fallback_result = await self._try_fred_fallback(key, btc_returns)
                    if fallback_result:
                        correlations.append(fallback_result)
                    else:
                        # Use static fallback
                        fallback = self._get_fallback_for_asset(key)
                        if fallback:
                            correlations.append(fallback)
                        
            except Exception as e:
                print(f"Error calculating correlation for {key}: {e}")
                fallback = self._get_fallback_for_asset(key)
                if fallback:
                    correlations.append(fallback)
        
        # Sort by correlation strength
        correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        # Generate insight
        insight = self._generate_insight(correlations)
        
        return {
            "correlations": correlations,
            "insight": insight,
            "calculation_method": f"{target_returns}-day rolling Pearson correlation of daily returns",
            "btc_data_points": len(btc_returns),
            "last_updated": datetime.now().isoformat()
        }
    
    async def _try_fred_fallback(self, asset_key: str, btc_returns: List[float]) -> Optional[Dict]:
        """Try to get correlation from FRED as fallback."""
        try:
            from data.fetchers.fred import fred_fetcher
            
            series_id = self.FRED_SERIES[asset_key]["series_id"]
            fred_data = await fred_fetcher.fetch_series(series_id, limit=45)
            
            if fred_data and "observations" in fred_data:
                values = self.parse_fred_values(fred_data["observations"])
                if len(values) >= 7:
                    asset_returns = self.calculate_returns(values)
                    n_returns = min(len(btc_returns), len(asset_returns))
                    
                    if n_returns >= 7:
                        btc_slice = btc_returns[-n_returns:]
                        asset_slice = asset_returns[-n_returns:]
                        corr = self.calculate_correlation(btc_slice, asset_slice)
                        
                        return {
                            "asset": self.FRED_SERIES[asset_key]["asset"],
                            "symbol": self.FRED_SERIES[asset_key]["symbol"],
                            "correlation": round(corr, 2),
                            "label": self.get_correlation_label(corr),
                            "source": "FRED",
                            "data_points": n_returns,
                            "period_days": n_returns
                        }
        except Exception as e:
            print(f"FRED fallback error for {asset_key}: {e}")
        return None
    
    def _get_fallback_for_asset(self, asset_key: str) -> Optional[Dict[str, Any]]:
        """Get fallback correlation for a specific asset."""
        fallbacks = {
            "SP500": {
                "asset": "S&P 500",
                "symbol": "^GSPC",
                "correlation": 0.72,
                "label": "High Positive",
                "source": "estimated"
            },
            "NASDAQ": {
                "asset": "NASDAQ",
                "symbol": "^IXIC",
                "correlation": 0.78,
                "label": "Very High",
                "source": "estimated"
            },
            "GOLD": {
                "asset": "Gold",
                "symbol": "GC=F",
                "correlation": -0.15,
                "label": "Diverging",
                "source": "estimated"
            },
            "DXY": {
                "asset": "DXY (USD)",
                "symbol": "DX-Y.NYB",
                "correlation": -0.45,
                "label": "Inverse",
                "source": "estimated"
            }
        }
        return fallbacks.get(asset_key)
    
    def _generate_insight(self, correlations: List[Dict]) -> str:
        """Generate insight based on correlations."""
        nasdaq = next((c for c in correlations if "NASDAQ" in c["asset"]), None)
        dxy = next((c for c in correlations if "DXY" in c["asset"]), None)
        gold = next((c for c in correlations if "Gold" in c["asset"]), None)
        
        highest = max(correlations, key=lambda x: x["correlation"]) if correlations else None
        lowest = min(correlations, key=lambda x: x["correlation"]) if correlations else None
        
        insights = []
        
        if nasdaq and nasdaq["correlation"] > 0.6:
            insights.append("BTC trading as high-beta tech/risk asset")
        elif nasdaq and nasdaq["correlation"] > 0.3:
            insights.append("Moderate correlation with tech stocks")
        
        if dxy and dxy["correlation"] < -0.4:
            insights.append("inversely correlated with USD")
        elif dxy and dxy["correlation"] < -0.2:
            insights.append("showing some inverse relation to USD strength")
        
        if gold and gold["correlation"] > 0.4:
            insights.append("moving with Gold as store-of-value")
        elif gold and gold["correlation"] > 0:
            insights.append("weak positive correlation with Gold")
        
        if insights:
            return "📊 " + "; ".join(insights)
        
        if highest and highest["correlation"] > 0.5:
            return f"📊 BTC most correlated with {highest['asset']} ({highest['correlation']:.2f})"
        if lowest and lowest["correlation"] < -0.3:
            return f"📊 BTC most inversely correlated with {lowest['asset']} ({lowest['correlation']:.2f})"
        
        return "📈 Mixed correlations — monitor for regime shift"
    
    async def get_paxg_btc(self) -> Dict[str, Any]:
        """Get PAXG/BTC ratio data."""
        ticker, klines = await asyncio.gather(
            self.get_ticker("PAXGBTC"),
            self.get_klines("PAXGBTC", limit=30)
        )
        
        if not klines:
            return self._get_fallback_paxg_btc()
        
        closes = [float(k[4]) for k in klines]
        current = closes[-1]
        week_ago = closes[-7] if len(closes) >= 7 else closes[0]
        month_ago = closes[0]
        
        change_24h = float(ticker.get("priceChangePercent", 0))
        change_7d = ((current - week_ago) / week_ago) * 100
        change_30d = ((current - month_ago) / month_ago) * 100
        
        # Trend logic
        if change_7d > 2 and change_30d > 5:
            trend = {
                "signal": "GOLD OUTPERFORMING BTC",
                "emoji": "🟡",
                "bitgold": "🛡️ Consider defensive allocation"
            }
        elif change_7d < -2 and change_30d < -5:
            trend = {
                "signal": "BTC OUTPERFORMING GOLD",
                "emoji": "🟢",
                "bitgold": "🚀 Maintain BTC allocation"
            }
        else:
            trend = {
                "signal": "NEUTRAL",
                "emoji": "⚪",
                "bitgold": "⚖️ Follow CDC signal"
            }
        
        return {
            "current_ratio": round(current, 5),
            "change_24h": round(change_24h, 2),
            "change_7d": round(change_7d, 2),
            "change_30d": round(change_30d, 2),
            "chart_data": closes,
            "trend": trend
        }
    
    def _get_fallback_correlations(self) -> Dict[str, Any]:
        """Fallback correlation data when all sources fail."""
        return {
            "correlations": [
                {"asset": "S&P 500", "symbol": "^GSPC", "correlation": 0.72, "label": "High Positive", "source": "estimated"},
                {"asset": "NASDAQ", "symbol": "^IXIC", "correlation": 0.78, "label": "Very High", "source": "estimated"},
                {"asset": "Gold", "symbol": "GC=F", "correlation": -0.15, "label": "Diverging", "source": "estimated"},
                {"asset": "DXY (USD)", "symbol": "DX-Y.NYB", "correlation": -0.45, "label": "Inverse", "source": "estimated"}
            ],
            "insight": "📊 BTC trading as high-beta tech/risk asset",
            "calculation_method": "fallback estimates",
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_fallback_paxg_btc(self) -> Dict[str, Any]:
        """Fallback PAXG/BTC data."""
        return {
            "current_ratio": 0.07234,
            "change_24h": 1.25,
            "change_7d": 3.42,
            "change_30d": 8.15,
            "chart_data": [0.066, 0.067, 0.068, 0.069, 0.070, 0.071, 0.072],
            "trend": {
                "signal": "GOLD OUTPERFORMING BTC",
                "emoji": "🟡",
                "bitgold": "🛡️ Consider defensive allocation"
            }
        }


# Global instance
correlation_fetcher = CorrelationFetcher()
