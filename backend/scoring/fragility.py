"""Market fragility scoring module."""
from typing import Dict, Any
import numpy as np


def calculate_fragility(
    vol_percentile: float = 50.0,
    drawdown_pct: float = -10.0,
    funding_rate: float = 0.0,
    exchange_flow_pct: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate market fragility score (0-100).
    Higher = More fragile/risky
    """
    score = 0
    components = {}
    
    # Volatility (0-25)
    vol_score = min(25, vol_percentile * 0.25)
    score += vol_score
    components["volatility"] = round(vol_score, 1)
    
    # Drawdown (0-25) - deeper drawdown = more fragile
    dd_score = min(25, abs(drawdown_pct) * 0.5)
    score += dd_score
    components["drawdown"] = round(dd_score, 1)
    
    # Funding (0-25) - extreme funding = fragile
    if funding_rate > 0.05:
        funding_score = 25  # Overleveraged longs
    elif funding_rate > 0.02:
        funding_score = 15
    elif funding_rate < -0.03:
        funding_score = 5   # Squeeze setup = less fragile
    else:
        funding_score = 10
    score += funding_score
    components["funding"] = funding_score
    
    # Exchange Flow (0-25)
    if exchange_flow_pct > 10:
        flow_score = 25  # Heavy inflows = distribution
    elif exchange_flow_pct > 0:
        flow_score = 15
    else:
        flow_score = 5   # Outflows = accumulation
    score += flow_score
    components["exchange_flow"] = flow_score
    
    total_score = min(100, int(score))
    
    # Get label
    if total_score >= 75:
        label = "CRITICAL"
        emoji = "🔴"
        color = "#ff4444"
    elif total_score >= 50:
        label = "ELEVATED"
        emoji = "🟠"
        color = "#ff6b35"
    elif total_score >= 25:
        label = "MODERATE"
        emoji = "🟡"
        color = "#ffaa00"
    else:
        label = "LOW"
        emoji = "🟢"
        color = "#00ff88"
    
    return {
        "score": total_score,
        "label": label,
        "emoji": emoji,
        "color": color,
        "components": components,
        "description": f"{label} fragility level"
    }


def get_fragility_from_market_data(
    current_price: float,
    ath_price: float,
    funding_rate: float,
    volume_24h: float,
    avg_volume_7d: float
) -> Dict[str, Any]:
    """Calculate fragility from market data."""
    drawdown = ((current_price / ath_price) - 1) * 100 if ath_price > 0 else 0
    
    # Estimate volatility percentile (simplified)
    vol_change = abs((volume_24h / avg_volume_7d) - 1) * 100 if avg_volume_7d > 0 else 50
    vol_percentile = min(100, vol_change * 2)
    
    return calculate_fragility(
        vol_percentile=vol_percentile,
        drawdown_pct=drawdown,
        funding_rate=funding_rate,
        exchange_flow_pct=0  # Would need on-chain data
    )
