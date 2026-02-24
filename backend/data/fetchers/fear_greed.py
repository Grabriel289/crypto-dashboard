"""Fear & Greed Index fetcher."""
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime


FEAR_GREED_URL = "https://api.alternative.me/fng/"


class FearGreedFetcher:
    """Fetch Fear & Greed Index."""
    
    async def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch current Fear & Greed data."""
        url = f"{FEAR_GREED_URL}?limit=1"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    if data and "data" in data and len(data["data"]) > 0:
                        item = data["data"][0]
                        value = int(item["value"])
                        return {
                            "value": value,
                            "value_classification": item["value_classification"],
                            "timestamp": datetime.fromtimestamp(int(item["timestamp"])),
                            **self._interpret(value)
                        }
                    return None
            except Exception as e:
                print(f"Fear & Greed fetch error: {e}")
                return None
    
    def _interpret(self, value: int) -> Dict[str, Any]:
        """Interpret fear & greed value."""
        if value <= 10:
            return {
                "label": "EXTREME FEAR",
                "signal": "BOTTOM_SIGNAL",
                "probability": "70% local bottom",
                "action": "Accumulate",
                "emoji": "🔴"
            }
        elif value <= 25:
            return {
                "label": "FEAR",
                "signal": "CAUTIOUS_BULLISH",
                "probability": "50% bottom forming",
                "action": "Selective buying",
                "emoji": "🟡"
            }
        elif value <= 45:
            return {
                "label": "NEUTRAL_FEAR",
                "signal": "NEUTRAL",
                "probability": "Normal range",
                "action": "Hold",
                "emoji": "⚪"
            }
        elif value <= 55:
            return {
                "label": "NEUTRAL",
                "signal": "NEUTRAL",
                "probability": "Normal range",
                "action": "Hold",
                "emoji": "[N]"
            }
        elif value <= 75:
            return {
                "label": "GREED",
                "signal": "CAUTIOUS_BEARISH",
                "probability": "Pullback risk",
                "action": "Take some profits",
                "emoji": "🟢"
            }
        else:
            return {
                "label": "EXTREME GREED",
                "signal": "TOP_SIGNAL",
                "probability": "65% local top",
                "action": "Take profits",
                "emoji": "🚀"
            }


# Singleton instance
fear_greed_fetcher = FearGreedFetcher()
