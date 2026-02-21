"""Detect conflicting signals in market data."""
from typing import Dict, Any, List


def detect_conflicting_signals(
    macro_score: float,
    fear_greed: int,
    fear_greed_signal: str,
    whale_signal: str,
    whale_bias: str,
    funding_bias: str,
    fragility_score: int,
    sector_verdict: str
) -> Dict[str, Any]:
    """
    Detect conflicting signals across different indicators.
    Returns warning if bullish and bearish signals are present simultaneously.
    """
    bullish_signals = []
    bearish_signals = []
    
    # Fear & Greed analysis
    if fear_greed <= 20:
        bullish_signals.append({
            "indicator": "Fear & Greed",
            "value": f"{fear_greed} (Extreme Fear)",
            "signal": "Potential bottom - accumulation zone"
        })
    elif fear_greed >= 80:
        bearish_signals.append({
            "indicator": "Fear & Greed",
            "value": f"{fear_greed} (Extreme Greed)",
            "signal": "Potential top - take profits"
        })
    
    # Whale activity analysis
    if "ACCUMULATION" in whale_signal:
        bullish_signals.append({
            "indicator": "Whale Activity",
            "value": whale_signal,
            "signal": "Smart money accumulating"
        })
    elif "DISTRIBUTION" in whale_signal:
        bearish_signals.append({
            "indicator": "Whale Activity",
            "value": whale_signal,
            "signal": "Smart money distributing"
        })
    
    # Funding rate analysis
    if funding_bias == "bullish":
        bullish_signals.append({
            "indicator": "Funding Rates",
            "value": "Negative/Squeezed",
            "signal": "Shorts paying longs - bullish setup"
        })
    elif funding_bias == "bearish":
        bearish_signals.append({
            "indicator": "Funding Rates",
            "value": "Overleveraged Longs",
            "signal": "Longs paying shorts - caution"
        })
    
    # Macro score analysis
    if macro_score >= 3.0:
        bullish_signals.append({
            "indicator": "Macro Tide",
            "value": f"{macro_score}/5",
            "signal": "Risk-on environment supportive"
        })
    elif macro_score < 2.0:
        bearish_signals.append({
            "indicator": "Macro Tide",
            "value": f"{macro_score}/5",
            "signal": "Risk-off environment - defensive"
        })
    
    # Fragility analysis
    if fragility_score >= 60:
        bearish_signals.append({
            "indicator": "Market Fragility",
            "value": f"{fragility_score}/100",
            "signal": "Elevated fragility - reduce leverage"
        })
    elif fragility_score <= 30:
        bullish_signals.append({
            "indicator": "Market Fragility",
            "value": f"{fragility_score}/100",
            "signal": "Low fragility - favorable conditions"
        })
    
    # Determine if there's a conflict
    has_conflict = len(bullish_signals) > 0 and len(bearish_signals) > 0
    
    # Generate recommendation
    recommendation = ""
    if has_conflict:
        if fear_greed <= 15 and "DISTRIBUTION" in whale_signal:
            recommendation = "Wait for confirmation - extreme fear but whales distributing. Consider DCA strategy."
        elif macro_score >= 3.0 and fragility_score >= 60:
            recommendation = "Good macro but high fragility - wait for pullback before entering."
        elif funding_bias == "bullish" and "DISTRIBUTION" in whale_signal:
            recommendation = "Mixed signals - reduce position sizes and use tight stops."
        else:
            recommendation = "Mixed market signals - stay cautious and reduce leverage."
    
    return {
        "has_conflict": has_conflict,
        "conflict_level": "HIGH" if (len(bullish_signals) >= 2 and len(bearish_signals) >= 2) else "MEDIUM" if has_conflict else "NONE",
        "bullish_signals": bullish_signals,
        "bearish_signals": bearish_signals,
        "recommendation": recommendation,
        "summary": f"{len(bullish_signals)} bullish vs {len(bearish_signals)} bearish signals"
    }
