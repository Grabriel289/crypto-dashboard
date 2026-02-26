"""Real BTC ETF flow tracker using Yahoo Finance AUM data."""
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os


class FarsideScraper:
    """
    BTC ETF Flow tracker using Yahoo Finance totalAssets + price data.

    Flow calculation (same method used by professional ETF flow trackers):
        Flow_today = AUM_today - AUM_prev_day * (price_today / price_prev_day)

    This strips out price-driven AUM changes and isolates real share
    creation / redemption flows.

    ETFs tracked: IBIT, FBTC, ARKB, BITB, GBTC
    Data source:  Yahoo Finance quoteSummary API (free, no key required)

    Note: farside.co.uk is blocked by Cloudflare (403) so we use Yahoo
    Finance directly. AUM data is updated each market day by Yahoo Finance.
    """

    CACHE_FILE = ".cache/farside_etf.json"
    CACHE_TTL_HOURS = 6

    ETF_TICKERS = ["IBIT", "FBTC", "ARKB", "BITB", "GBTC"]

    YAHOO_SUMMARY_URL = "https://query1.finance.yahoo.com/v10/finance/quoteSummary"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        try:
            os.makedirs(".cache", exist_ok=True)
        except Exception:
            pass

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _load_cache(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.CACHE_FILE):
                with open(self.CACHE_FILE, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_cache(
        self,
        result_data: Dict,
        current_snap: Dict,
        current_date: str,
        prev_snap: Dict,
        prev_date: str,
    ):
        try:
            cache = {
                "result_timestamp": datetime.utcnow().isoformat(),
                "result_data": result_data,
                "current": {"date": current_date, "etfs": current_snap},
                "previous": {"date": prev_date, "etfs": prev_snap},
            }
            with open(self.CACHE_FILE, "w") as f:
                json.dump(cache, f)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Yahoo Finance fetch
    # ------------------------------------------------------------------

    async def fetch_etf_aum(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch AUM (totalAssets) and current price from Yahoo Finance."""
        url = f"{self.YAHOO_SUMMARY_URL}/{symbol}"
        params = {"modules": "summaryDetail,price"}
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        try:
            session = await self._get_session()
            async with session.get(
                url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status != 200:
                    print(f"[Farside] {symbol}: HTTP {response.status}")
                    return None

                data = await response.json()
                result = data.get("quoteSummary", {}).get("result")
                if not result:
                    return None
                result = result[0]

                summary = result.get("summaryDetail", {})
                price_data = result.get("price", {})

                aum = summary.get("totalAssets", {}).get("raw")
                price = price_data.get("regularMarketPrice", {}).get("raw")
                prev_close = price_data.get("regularMarketPreviousClose", {}).get("raw")

                if aum is None or price is None:
                    print(f"[Farside] {symbol}: missing AUM or price")
                    return None

                change_pct = (
                    (price - prev_close) / prev_close * 100 if prev_close else 0.0
                )

                return {
                    "symbol": symbol,
                    "aum": aum,          # USD
                    "price": price,      # USD per share
                    "prev_close": prev_close,
                    "change_pct": change_pct,
                }

        except Exception as e:
            print(f"[Farside] Error fetching {symbol}: {e}")
            return None

    # ------------------------------------------------------------------
    # Main flow computation
    # ------------------------------------------------------------------

    async def scrape_etf_flows(self) -> Optional[Dict[str, Any]]:
        """
        Return real BTC ETF flow data.

        Flow = AUM_today - AUM_prev_day * (price_today / price_prev_day)

        First run: saves baseline snapshot; flows are None until the next
        calendar day when we have two data points to compare.
        Subsequent runs: returns real flows in USD millions.
        """
        cache = self._load_cache()

        # Return cached result if still fresh
        result_ts = cache.get("result_timestamp")
        if result_ts:
            try:
                age_h = (
                    datetime.utcnow() - datetime.fromisoformat(result_ts)
                ).total_seconds() / 3600
                if age_h < self.CACHE_TTL_HOURS:
                    return cache.get("result_data")
            except Exception:
                pass

        # Fetch current AUM + price for all ETFs (+ GLD for context)
        print("[Farside] Fetching ETF AUM from Yahoo Finance...")
        current: Dict[str, Dict] = {}
        for ticker in self.ETF_TICKERS:
            stats = await self.fetch_etf_aum(ticker)
            if stats:
                current[ticker] = stats

        gld = await self.fetch_etf_aum("GLD")

        if not current:
            return self._get_fallback_data("Yahoo Finance unavailable")

        # Determine today's date (UTC)
        today_date = datetime.utcnow().strftime("%Y-%m-%d")

        # Resolve previous-day snapshot from cache
        cached_current = cache.get("current", {})
        cached_previous = cache.get("previous", {})
        cached_current_date = cached_current.get("date", "")

        if cached_current_date and cached_current_date != today_date:
            # New calendar day: yesterday = old "current"
            prev_snap = cached_current.get("etfs", {})
            prev_date = cached_current_date
        else:
            # Same calendar day or first run: keep stored "previous"
            prev_snap = cached_previous.get("etfs", {})
            prev_date = cached_previous.get("date", "")

        # Build today's snapshot
        today_snap = {
            ticker: {"aum": d["aum"], "price": d["price"]}
            for ticker, d in current.items()
        }

        # Calculate flows
        etf_flows: Dict[str, Optional[float]] = {}
        has_real_flows = False

        if prev_snap and prev_date and prev_date != today_date:
            for ticker, data in current.items():
                prev = prev_snap.get(ticker)
                if prev and prev.get("price") and prev["price"] > 0:
                    price_ratio = data["price"] / prev["price"]
                    # Flow = AUM_today - AUM_prev * price_ratio  (isolates new money)
                    flow_usd = data["aum"] - prev["aum"] * price_ratio
                    etf_flows[ticker] = round(flow_usd / 1_000_000, 1)
                    has_real_flows = True
                else:
                    etf_flows[ticker] = None
        else:
            for ticker in current:
                etf_flows[ticker] = None

        total_flow: Optional[float] = None
        if has_real_flows:
            total_flow = round(
                sum(v for v in etf_flows.values() if v is not None), 1
            )

        # Relative performance context (always available)
        proxy_metrics: Dict[str, float] = {}
        ibit = current.get("IBIT")
        if ibit and gld:
            proxy_metrics = {
                "ibit_change_pct": round(ibit["change_pct"], 2),
                "gld_change_pct": round(gld["change_pct"], 2),
                "relative_performance": round(
                    ibit["change_pct"] - gld["change_pct"], 2
                ),
            }

        if has_real_flows:
            note = f"Real flows: AUM delta adjusted for price ({prev_date} → {today_date})"
            source = "yahoo_aum_real"
        else:
            note = "Collecting baseline — flows will appear on next calendar day refresh"
            source = "yahoo_aum_first_run"

        result = {
            "date": today_date,
            "flow_date": prev_date if has_real_flows else None,
            "total_flow": total_flow,
            "flows": etf_flows,
            "has_real_flows": has_real_flows,
            "source": source,
            "proxy_metrics": proxy_metrics,
            "note": note,
        }

        self._save_cache(result, today_snap, today_date, prev_snap, prev_date)

        if has_real_flows:
            print(f"[Farside] Real ETF flows: ${total_flow:+.1f}M total")
            for t, f in etf_flows.items():
                if f is not None:
                    print(f"  {t}: ${f:+.1f}M")
        else:
            print(f"[Farside] Baseline saved for {today_date}. Flows available next calendar day.")

        return result

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------

    def _get_fallback_data(self, reason: str = "Unknown") -> Dict[str, Any]:
        return {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "flow_date": None,
            "total_flow": None,
            "flows": {t: None for t in self.ETF_TICKERS},
            "has_real_flows": False,
            "source": "fallback",
            "proxy_metrics": {},
            "note": reason,
        }

    # ------------------------------------------------------------------
    # Signal interpretation
    # ------------------------------------------------------------------

    def get_gold_cannibalization_signal(
        self, etf_flows: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Convert ETF flow data to a Gold Cannibalization signal."""
        if not etf_flows:
            return {
                "active": False,
                "status": "⚪",
                "detail": "No ETF data available",
                "flow_24h": None,
                "signal": "neutral",
                "individual_etfs": {},
            }

        flow_24h = etf_flows.get("total_flow")
        flows = etf_flows.get("flows", {})
        has_real_flows = etf_flows.get("has_real_flows", False)
        proxy_metrics = etf_flows.get("proxy_metrics", {})
        source = etf_flows.get("source", "unknown")
        note = etf_flows.get("note", "")
        date = etf_flows.get("date", "")

        # Build per-ETF breakdown
        individual_analysis: Dict[str, Any] = {}
        for ticker, flow in flows.items():
            if flow is None:
                individual_analysis[ticker] = {"flow": None, "status": "pending"}
            elif ticker == "GBTC":
                individual_analysis[ticker] = {
                    "flow": flow,
                    "status": "inflow" if flow > 0 else "outflow",
                    "note": "Legacy conversion vehicle",
                }
            else:
                individual_analysis[ticker] = {
                    "flow": flow,
                    "status": "inflow" if flow > 0 else "outflow" if flow < 0 else "neutral",
                }

        base = {
            "date": date,
            "individual_etfs": individual_analysis,
            "proxy_metrics": proxy_metrics,
            "source": source,
        }

        # ---- First run / no real flows: use relative performance direction ----
        if not has_real_flows:
            ibit_chg = proxy_metrics.get("ibit_change_pct", 0)
            gld_chg = proxy_metrics.get("gld_change_pct", 0)
            rel_perf = proxy_metrics.get("relative_performance", 0)

            if proxy_metrics:
                detail = (
                    f"IBIT {ibit_chg:+.1f}% vs GLD {gld_chg:+.1f}% "
                    f"(collecting baseline)"
                )
            else:
                detail = note or "Initializing…"

            if rel_perf > 1:
                status, signal = "🟡", "light_inflow"
            elif rel_perf < -1:
                status, signal = "🟡", "light_outflow"
            else:
                status, signal = "⚪", "neutral"

            return {
                **base,
                "active": abs(rel_perf) > 0.5 if proxy_metrics else False,
                "status": status,
                "detail": detail,
                "flow_24h": None,
                "signal": signal,
                "is_baseline": True,
            }

        # ---- Real flow data available ----
        sorted_flows = sorted(
            [(t, f) for t, f in flows.items() if f is not None],
            key=lambda x: x[1],
            reverse=True,
        )
        top_inflow = sorted_flows[0] if sorted_flows and sorted_flows[0][1] > 0 else None

        ibit_chg = proxy_metrics.get("ibit_change_pct", 0)
        gld_chg = proxy_metrics.get("gld_change_pct", 0)
        detail_parts = [f"${flow_24h:+.0f}M"]
        if proxy_metrics:
            detail_parts.append(f"IBIT {ibit_chg:+.1f}% vs GLD {gld_chg:+.1f}%")
        if top_inflow:
            detail_parts.append(f"Leader: {top_inflow[0]}")
        detail = " | ".join(detail_parts)

        if flow_24h > 200:
            return {
                **base,
                "active": True,
                "status": "🟢",
                "detail": detail,
                "flow_24h": flow_24h,
                "signal": "strong_inflow",
                "interpretation": "Strong BTC ETF inflows vs Gold",
                "is_real": True,
            }
        elif flow_24h > 80:
            return {
                **base,
                "active": True,
                "status": "🟢",
                "detail": detail,
                "flow_24h": flow_24h,
                "signal": "moderate_inflow",
                "interpretation": "BTC ETF seeing solid inflows",
                "is_real": True,
            }
        elif flow_24h > 20:
            return {
                **base,
                "active": True,
                "status": "🟡",
                "detail": detail,
                "flow_24h": flow_24h,
                "signal": "light_inflow",
                "interpretation": "Modest BTC ETF inflows",
                "is_real": True,
            }
        elif flow_24h < -50:
            return {
                **base,
                "active": True,
                "status": "🔴",
                "detail": detail,
                "flow_24h": flow_24h,
                "signal": "outflow",
                "interpretation": "BTC ETF outflows detected",
                "is_real": True,
            }
        else:
            return {
                **base,
                "active": False,
                "status": "⚪",
                "detail": f"Neutral: ${flow_24h:.0f}M on {date}",
                "flow_24h": flow_24h,
                "signal": "neutral",
                "interpretation": "Flat BTC ETF flows",
                "is_real": True,
            }


# Singleton instance
farside_scraper = FarsideScraper()
