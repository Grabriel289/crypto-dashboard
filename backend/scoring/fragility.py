"""Market fragility scoring module - Fixed implementation per specification."""
from typing import Dict, Any, List, Optional
import numpy as np


def calculate_depth_2pct(bids: List[List], asks: List[List], mid_price: float) -> float:
    """
    Calculate total liquidity within 2% of mid price.
    
    Args:
        bids: List of [price, quantity] from order book
        asks: List of [price, quantity] from order book
        mid_price: Current mid price
    
    Returns:
        Total USD liquidity within ±2%
    """
    upper_bound = mid_price * 1.02
    lower_bound = mid_price * 0.98
    
    # Sum bid liquidity within range
    bid_depth = sum(
        float(price) * float(qty)
        for price, qty in bids
        if float(price) >= lower_bound
    )
    
    # Sum ask liquidity within range
    ask_depth = sum(
        float(price) * float(qty)
        for price, qty in asks
        if float(price) <= upper_bound
    )
    
    return bid_depth + ask_depth


def calculate_L_d(open_interest_usd: float, depth_2pct_usd: float) -> float:
    """
    L_d — Liquidation Density (Slippage Risk)
    
    Formula: L_d = min(100, OI / (Depth_2% × 10))
    
    Measures: How much OI vs available liquidity
    High L_d = Small trades cause cascades
    """
    if depth_2pct_usd <= 0:
        return 100.0
    
    L_d = open_interest_usd / (depth_2pct_usd * 10)
    return min(100.0, L_d)


def calculate_F_sigma(current_funding: float, funding_7d: List[float]) -> float:
    """
    F_σ — Funding Deviation (Position Crowding)
    
    Formula: F_σ = min(100, |F_i - SMA_7d| / StdDev × 20)
    
    Measures: How far current funding is from average
    High F_σ = Extreme position crowding
    """
    if len(funding_7d) < 3:
        return 50.0  # Not enough data
    
    sma_7d = np.mean(funding_7d)
    std_7d = np.std(funding_7d)
    
    if std_7d == 0:
        return 50.0  # No variance
    
    z_score = abs(current_funding - sma_7d) / std_7d
    F_sigma = z_score * 20
    
    return min(100.0, F_sigma)


def calculate_B_z(spot_price: float, perp_price: float) -> float:
    """
    B_z — Basis Tension (Market Dislocation)
    
    Formula: B_z = min(100, |Spot - Perp| / Spot × 1000)
    
    Measures: Gap between spot and perpetual
    High B_z = Market dislocation, likely to snap back
    """
    if spot_price <= 0:
        return 50.0
    
    basis_pct = abs(spot_price - perp_price) / spot_price
    B_z = basis_pct * 1000
    
    return min(100.0, B_z)


def calculate_fragility_score(
    open_interest_usd: float,
    depth_2pct_usd: float,
    current_funding: float,
    funding_7d: List[float],
    spot_price: float,
    perp_price: float
) -> Dict[str, Any]:
    """
    Calculate Market Fragility Score (Φ).
    
    Formula: Φ = (L_d + F_σ + B_z) / 3
    
    Returns score 0-100 with components breakdown.
    """
    # Calculate components
    L_d = calculate_L_d(open_interest_usd, depth_2pct_usd)
    F_sigma = calculate_F_sigma(current_funding, funding_7d)
    B_z = calculate_B_z(spot_price, perp_price)
    
    # Calculate final fragility score
    phi = (L_d + F_sigma + B_z) / 3
    
    # Determine level
    if phi <= 25:
        level = "Stable"
        emoji = "🟢"
        color = "#00ff88"
    elif phi <= 50:
        level = "Caution"
        emoji = "🟡"
        color = "#ffaa00"
    elif phi <= 75:
        level = "Fragile"
        emoji = "🟠"
        color = "#ff6b35"
    else:
        level = "Critical"
        emoji = "🔴"
        color = "#ff4444"
    
    return {
        "score": round(phi, 1),
        "level": level,
        "emoji": emoji,
        "color": color,
        "components": {
            "L_d": {
                "value": round(L_d, 1),
                "label": "Liquidation Density",
                "description": "OI vs liquidity depth"
            },
            "F_sigma": {
                "value": round(F_sigma, 1),
                "label": "Funding Deviation",
                "description": "Position crowding"
            },
            "B_z": {
                "value": round(B_z, 1),
                "label": "Basis Tension",
                "description": "Spot-perp dislocation"
            }
        },
        "formula": "Φ = (L_d + F_σ + B_z) / 3"
    }


# Legacy function for backward compatibility
def calculate_fragility(
    vol_percentile: float = 50.0,
    drawdown_pct: float = -10.0,
    funding_rate: float = 0.0,
    exchange_flow_pct: float = 0.0
) -> Dict[str, Any]:
    """
    LEGACY: Calculate market fragility score (0-100).
    Higher = More fragile/risky
    
    This is the old simplified version for backward compatibility.
    Use calculate_fragility_score() for the proper implementation.
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
        emoji = "[RED]"
        color = "#ff4444"
    elif total_score >= 50:
        label = "ELEVATED"
        emoji = "[ORANGE]"
        color = "#ff6b35"
    elif total_score >= 25:
        label = "MODERATE"
        emoji = "[YELLOW]"
        color = "#ffaa00"
    else:
        label = "LOW"
        emoji = "[GREEN]"
        color = "#00ff88"
    
    return {
        "score": total_score,
        "label": label,
        "emoji": emoji,
        "color": color,
        "components": components,
        "description": f"{label} fragility level",
        "note": "Using legacy calculation. Use calculate_fragility_score() for Φ formula."
    }


def get_fragility_from_market_data(
    current_price: float,
    ath_price: float,
    funding_rate: float,
    volume_24h: float,
    avg_volume_7d: float
) -> Dict[str, Any]:
    """Calculate fragility from market data (legacy method)."""
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
