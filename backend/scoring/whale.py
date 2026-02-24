"""Whale activity analysis module."""
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class WhaleActivity:
    """Whale activity metrics."""
    total_oi_usd: float = 0.0
    oi_change_24h_pct: float = 0.0
    exchange_inflow_pct: float = 0.0
    
    def get_positioning_signal(self) -> Dict[str, Any]:
        """Generate positioning signal based on whale activity."""
        # OI rising + inflows = distribution (bearish)
        if self.oi_change_24h_pct > 5 and self.exchange_inflow_pct > 5:
            return {
                "signal": "DISTRIBUTION / NET SHORT",
                "emoji": "🔴",
                "description": "OI rising + exchange inflows = distribution",
                "bias": "bearish"
            }
        # OI falling + outflows = accumulation (bullish)
        elif self.oi_change_24h_pct < -5 and self.exchange_inflow_pct < -5:
            return {
                "signal": "ACCUMULATION / NET LONG",
                "emoji": "🟢",
                "description": "OI falling + exchange outflows = accumulation",
                "bias": "bullish"
            }
        elif self.exchange_inflow_pct > 10:
            return {
                "signal": "DISTRIBUTION DETECTED",
                "emoji": "🟠",
                "description": "Heavy exchange inflows",
                "bias": "bearish"
            }
        elif self.exchange_inflow_pct < -10:
            return {
                "signal": "ACCUMULATION DETECTED",
                "emoji": "🟢",
                "description": "Heavy exchange outflows",
                "bias": "bullish"
            }
        else:
            return {
                "signal": "NEUTRAL",
                "emoji": "🟡",
                "description": "No clear whale signal",
                "bias": "neutral"
            }


def analyze_whale_activity(
    oi_current: float,
    oi_previous: float,
    exchange_inflow_24h: float,
    exchange_outflow_24h: float
) -> WhaleActivity:
    """Analyze whale activity from raw data."""
    # Calculate OI change
    oi_change_pct = ((oi_current - oi_previous) / oi_previous * 100) if oi_previous > 0 else 0
    
    # Calculate net exchange flow
    net_flow = exchange_inflow_24h - exchange_outflow_24h
    total_flow = exchange_inflow_24h + exchange_outflow_24h
    
    # Calculate flow percentage
    flow_pct = (net_flow / total_flow * 100) if total_flow > 0 else 0
    
    return WhaleActivity(
        total_oi_usd=oi_current,
        oi_change_24h_pct=oi_change_pct,
        exchange_inflow_pct=flow_pct
    )
