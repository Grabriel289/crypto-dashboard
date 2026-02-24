"""Funding rate analysis module."""
from typing import Dict, Any


def interpret_funding(rate: float) -> Dict[str, Any]:
    """
    Interpret funding rate signal.
    rate: 8h funding rate (e.g., -0.0005 = -0.05%)
    """
    rate_pct = rate * 100  # Convert to percentage
    
    if rate_pct < -0.03:
        return {
            "signal": "STRONG SQUEEZE SETUP",
            "emoji": "[G]",
            "bias": "bullish",
            "description": "Shorts paying longs heavily",
            "color": "#00ff88"
        }
    elif rate_pct < 0:
        return {
            "signal": "SQUEEZE SETUP",
            "emoji": "[GREEN]",
            "bias": "bullish",
            "description": "Negative funding; shorts dominant",
            "color": "#00cc6a"
        }
    elif rate_pct < 0.03:
        return {
            "signal": "NEUTRAL",
            "emoji": "[Y]",
            "bias": "neutral",
            "description": "Balanced positioning",
            "color": "#ffaa00"
        }
    elif rate_pct < 0.08:
        return {
            "signal": "OVERLEVERAGED LONGS",
            "emoji": "[O]",
            "bias": "bearish",
            "description": "Pullback risk elevated",
            "color": "#ff6b35"
        }
    else:
        return {
            "signal": "EXTREME EUPHORIA",
            "emoji": "[R]",
            "bias": "bearish",
            "description": "Correction imminent",
            "color": "#ff4444"
        }


def aggregate_funding_signals(funding_data: Dict[str, Dict]) -> Dict[str, Any]:
    """Aggregate funding signals across multiple assets."""
    if not funding_data:
        return {
            "overall_signal": "NEUTRAL",
            "bias": "neutral",
            "emoji": "[YELLOW]"
        }
    
    # Count biases
    bullish_count = sum(1 for d in funding_data.values() if d.get("bias") == "bullish")
    bearish_count = sum(1 for d in funding_data.values() if d.get("bias") == "bearish")
    neutral_count = len(funding_data) - bullish_count - bearish_count
    
    # Determine overall bias
    if bullish_count > bearish_count and bullish_count > neutral_count:
        return {
            "overall_signal": "SQUEEZE SETUP",
            "bias": "bullish",
            "emoji": "[GREEN]",
            "description": "Negative funding dominance"
        }
    elif bearish_count > bullish_count and bearish_count > neutral_count:
        return {
            "overall_signal": "OVERLEVERAGED",
            "bias": "bearish",
            "emoji": "[ORANGE]",
            "description": "Longs paying shorts - caution"
        }
    else:
        return {
            "overall_signal": "NEUTRAL",
            "bias": "neutral",
            "emoji": "[YELLOW]",
            "description": "Mixed funding signals"
        }
