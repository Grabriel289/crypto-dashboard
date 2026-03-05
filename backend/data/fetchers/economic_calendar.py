"""Economic Calendar fetcher with auto-generated macro + crypto events."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import calendar


class CalendarFetcher:
    """Generate economic calendar from known schedules — no external API needed."""

    # ──────────────────────────────────────────────────────────────
    # FOMC meeting *statement* dates for 2026 (published by the Fed)
    # Meetings with Summary of Economic Projections marked with SEP
    # Update once per year when Fed publishes the new calendar.
    # ──────────────────────────────────────────────────────────────
    FOMC_DATES_2026 = [
        {"date": "2026-01-28", "sep": False},
        {"date": "2026-03-18", "sep": True},
        {"date": "2026-04-29", "sep": False},
        {"date": "2026-06-17", "sep": True},
        {"date": "2026-07-29", "sep": False},
        {"date": "2026-09-16", "sep": True},
        {"date": "2026-10-28", "sep": False},
        {"date": "2026-12-09", "sep": True},
    ]

    # ──────────────────────────────────────────────────────────────
    # CPI release dates for 2026 (from BLS schedule)
    # CPI is released ~10th-14th of each month for prior month data.
    # Update once per year when BLS publishes the schedule.
    # ──────────────────────────────────────────────────────────────
    CPI_DATES_2026 = [
        "2026-01-13",  # Dec 2025 data
        "2026-02-11",  # Jan 2026 data
        "2026-03-11",  # Feb 2026 data
        "2026-04-14",  # Mar 2026 data
        "2026-05-12",  # Apr 2026 data
        "2026-06-10",  # May 2026 data
        "2026-07-14",  # Jun 2026 data
        "2026-08-12",  # Jul 2026 data
        "2026-09-15",  # Aug 2026 data
        "2026-10-13",  # Sep 2026 data
        "2026-11-12",  # Oct 2026 data
        "2026-12-10",  # Nov 2026 data
    ]

    # ──────────────────────────────────────────────────────────────
    # Helper: nth weekday of a month
    # ──────────────────────────────────────────────────────────────
    @staticmethod
    def _nth_weekday(year: int, month: int, weekday: int, n: int) -> datetime:
        """Return the n-th occurrence of weekday in given month.
        weekday: 0=Mon … 4=Fri.  n: 1-based."""
        first = datetime(year, month, 1)
        offset = (weekday - first.weekday()) % 7
        return first + timedelta(days=offset + 7 * (n - 1))

    @staticmethod
    def _last_weekday(year: int, month: int, weekday: int) -> datetime:
        """Return the last occurrence of weekday in given month."""
        last_day = calendar.monthrange(year, month)[1]
        d = datetime(year, month, last_day)
        offset = (d.weekday() - weekday) % 7
        return d - timedelta(days=offset)

    # ──────────────────────────────────────────────────────────────
    # Generate events for a date range
    # ──────────────────────────────────────────────────────────────
    def _generate_macro_events(self, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Generate macro events (FOMC, CPI, NFP) within the date range."""
        events = []

        # --- FOMC meetings ---
        for fomc in self.FOMC_DATES_2026:
            d = datetime.strptime(fomc["date"], "%Y-%m-%d")
            if from_date <= d <= to_date:
                label = "FOMC Rate Decision + SEP" if fomc["sep"] else "FOMC Rate Decision"
                impact = "🔴 CRITICAL" if fomc["sep"] else "🔴 HIGH"
                event = {
                    "date": fomc["date"],
                    "time": "19:00",
                    "event": label,
                    "flag": "🇺🇸",
                    "impact": impact,
                }
                if fomc["sep"]:
                    event["is_key_event"] = True
                    event["insight"] = "SEP includes dot plot + growth/inflation forecasts. Hawkish shift = risk-off for crypto"
                events.append(event)

        # --- CPI releases ---
        for cpi_date in self.CPI_DATES_2026:
            d = datetime.strptime(cpi_date, "%Y-%m-%d")
            if from_date <= d <= to_date:
                events.append({
                    "date": cpi_date,
                    "time": "13:30",
                    "event": "CPI Inflation",
                    "flag": "🇺🇸",
                    "impact": "🔴 CRITICAL",
                    "is_key_event": True,
                    "insight": "Hot CPI = hawkish Fed = risk-off. Cool CPI = dovish = risk-on for crypto",
                })

        # --- Non-Farm Payrolls (first Friday of each month) ---
        year = from_date.year
        for m in range(1, 13):
            nfp = self._nth_weekday(year, m, 4, 1)  # 4 = Friday, 1st occurrence
            if from_date <= nfp <= to_date:
                events.append({
                    "date": nfp.strftime("%Y-%m-%d"),
                    "time": "13:30",
                    "event": "Non-Farm Payrolls",
                    "flag": "🇺🇸",
                    "impact": "🔴 HIGH",
                })

        # --- PCE Inflation (last Friday of each month, approximate) ---
        for m in range(1, 13):
            pce = self._last_weekday(year, m, 4)  # last Friday
            if from_date <= pce <= to_date:
                events.append({
                    "date": pce.strftime("%Y-%m-%d"),
                    "time": "13:30",
                    "event": "PCE Inflation",
                    "flag": "🇺🇸",
                    "impact": "🔴 HIGH",
                    "insight": "Core PCE is Fed's preferred inflation measure",
                })

        # Sort by date
        events.sort(key=lambda e: e["date"])
        return events

    def _generate_crypto_events(self, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Generate crypto events (options/futures expiry) within the date range."""
        events = []
        year = from_date.year

        # --- BTC/ETH Monthly Options Expiry (last Friday of each month on Deribit/CME) ---
        for m in range(1, 13):
            expiry = self._last_weekday(year, m, 4)  # last Friday
            if from_date <= expiry <= to_date:
                events.append({
                    "date": expiry.strftime("%Y-%m-%d"),
                    "event": "BTC/ETH Monthly Options Expiry",
                    "amount": "",
                    "impact": "🟡 Volatility",
                })

        # --- Quarterly Futures Expiry (last Friday of Mar/Jun/Sep/Dec) ---
        for m in [3, 6, 9, 12]:
            expiry = self._last_weekday(year, m, 4)
            if from_date <= expiry <= to_date:
                # Check if already added as options expiry — upgrade it
                existing = next((e for e in events if e["date"] == expiry.strftime("%Y-%m-%d")), None)
                if existing:
                    existing["event"] = "BTC/ETH Quarterly Options + Futures Expiry"
                    existing["impact"] = "🔴 High Volatility"
                else:
                    events.append({
                        "date": expiry.strftime("%Y-%m-%d"),
                        "event": "BTC/ETH Quarterly Options + Futures Expiry",
                        "amount": "",
                        "impact": "🔴 High Volatility",
                    })

        events.sort(key=lambda e: e["date"])
        return events

    async def get_calendar(self) -> Dict[str, Any]:
        """Get economic calendar for next 7 days."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        next_week = today + timedelta(days=7)

        macro_events = self._generate_macro_events(today, next_week)
        crypto_events = self._generate_crypto_events(today, next_week)
        key_event = self._find_key_event(macro_events)

        return {
            "macro_events": macro_events,
            "crypto_events": crypto_events,
            "key_event": key_event,
            "date_range": {
                "from": today.strftime("%Y-%m-%d"),
                "to": next_week.strftime("%Y-%m-%d"),
            },
        }

    def _find_key_event(self, events: List[Dict]) -> Optional[Dict[str, Any]]:
        """Find the most important upcoming event."""
        for event in events:
            if event.get("is_key_event"):
                return {
                    "date": event["date"],
                    "event": event["event"],
                    "insight": event.get("insight", ""),
                }

        # Fallback to first CRITICAL or HIGH impact event
        for event in events:
            if "CRITICAL" in event.get("impact", "") or "HIGH" in event.get("impact", ""):
                return {
                    "date": event["date"],
                    "event": event["event"],
                    "insight": event.get("insight", ""),
                }

        return None


# Global instance
calendar_fetcher = CalendarFetcher()
