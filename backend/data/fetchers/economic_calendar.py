"""Economic Calendar fetcher."""
from typing import Dict, Any, List
from datetime import datetime, timedelta


class CalendarFetcher:
    """Fetch economic calendar data."""
    
    # Static macro events (update weekly in production)
    MACRO_EVENTS = [
        {"date": "2026-02-23", "time": "19:00", "event": "Fed Minutes Release", "flag": "[US]", "impact": "[R] HIGH"},
        {"date": "2026-02-25", "time": "15:00", "event": "Consumer Confidence", "flag": "[US]", "impact": "[Y] MEDIUM"},
        {"date": "2026-02-27", "time": "13:30", "event": "GDP Q4 (2nd Est.)", "flag": "[US]", "impact": "[R] HIGH"},
        {"date": "2026-02-28", "time": "13:30", "event": "PCE Inflation", "flag": "[US]", "impact": "[R] CRITICAL", "is_key_event": True, "insight": "Core PCE is Fed's preferred measure. Hot print = hawkish Fed = risk-off for crypto"},
        {"date": "2026-03-07", "time": "13:30", "event": "Non-Farm Payrolls", "flag": "[US]", "impact": "[R] HIGH"},
        {"date": "2026-03-12", "time": "13:30", "event": "CPI Inflation", "flag": "[US]", "impact": "[R] CRITICAL"},
    ]
    
    # Static crypto events (can be updated via API)
    CRYPTO_EVENTS = [
        {"date": "2026-02-24", "event": "ARB Token Unlock", "amount": "$45M", "impact": "[R] Bearish ARB"},
        {"date": "2026-02-26", "event": "APT Token Unlock", "amount": "$82M", "impact": "[R] Bearish APT"},
        {"date": "2026-02-28", "event": "BTC Monthly Options Expiry", "amount": "", "impact": "[Y] Volatility"},
        {"date": "2026-03-15", "event": "ETH Dencun Upgrade", "amount": "", "impact": "[G] Bullish ETH"},
    ]
    
    async def get_calendar(self) -> Dict[str, Any]:
        """Get economic calendar for next 7 days."""
        today = datetime.now()
        next_week = today + timedelta(days=7)
        
        # Filter events for next 7 days
        macro_events = self._filter_events(self.MACRO_EVENTS, today, next_week)
        crypto_events = self._filter_crypto_events(self.CRYPTO_EVENTS, today, next_week)
        
        # Find key event
        key_event = self._find_key_event(macro_events)
        
        return {
            "macro_events": macro_events,
            "crypto_events": crypto_events,
            "key_event": key_event,
            "date_range": {
                "from": today.strftime("%Y-%m-%d"),
                "to": next_week.strftime("%Y-%m-%d")
            }
        }
    
    def _filter_events(self, events: List[Dict], from_date: datetime, to_date: datetime) -> List[Dict]:
        """Filter macro events by date range."""
        filtered = []
        for event in events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            if from_date <= event_date <= to_date:
                filtered.append(event)
        return filtered
    
    def _filter_crypto_events(self, events: List[Dict], from_date: datetime, to_date: datetime) -> List[Dict]:
        """Filter crypto events by date range."""
        filtered = []
        for event in events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            if from_date <= event_date <= to_date:
                filtered.append(event)
        return filtered
    
    def _find_key_event(self, events: List[Dict]) -> Dict[str, Any]:
        """Find the most important upcoming event."""
        for event in events:
            if event.get("is_key_event"):
                return {
                    "date": event["date"],
                    "event": event["event"],
                    "insight": event.get("insight", "")
                }
        
        # Return first critical or high impact event
        for event in events:
            if "CRITICAL" in event.get("impact", "") or "HIGH" in event.get("impact", ""):
                return {
                    "date": event["date"],
                    "event": event["event"],
                    "insight": ""
                }
        
        return None


# Global instance
calendar_fetcher = CalendarFetcher()
