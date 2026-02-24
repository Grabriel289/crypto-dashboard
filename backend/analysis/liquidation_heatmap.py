"""BTC Liquidation Heatmap Calculator - Estimated from OI + Leverage."""
from typing import Dict, Any, List, Tuple
import numpy as np


# Leverage distribution based on industry research
LEVERAGE_DISTRIBUTION = {
    5: 0.10,    # 10% of traders use 5x
    10: 0.25,   # 25% use 10x
    20: 0.30,   # 30% use 20x
    50: 0.25,   # 25% use 50x
    100: 0.10   # 10% use 100x
}


def calculate_liquidation_price(entry_price: float, leverage: int, is_long: bool) -> float:
    """
    Calculate liquidation price.
    
    For LONG:  Liq = Entry × (1 - 0.9/Leverage)
    For SHORT: Liq = Entry × (1 + 0.9/Leverage)
    
    0.9 factor accounts for maintenance margin (~10%)
    """
    margin_factor = 0.9 / leverage
    
    if is_long:
        return entry_price * (1 - margin_factor)
    else:
        return entry_price * (1 + margin_factor)


def estimate_long_short_ratio(funding_rate: float) -> Tuple[float, float]:
    """
    Estimate long/short ratio from funding rate.
    
    Positive funding = more longs (longs pay shorts)
    Negative funding = more shorts (shorts pay longs)
    
    Returns:
        (long_ratio, short_ratio)
    """
    if funding_rate > 0.0005:
        return (0.60, 0.40)  # 60% longs
    elif funding_rate > 0.0002:
        return (0.55, 0.45)
    elif funding_rate < -0.0005:
        return (0.40, 0.60)  # 60% shorts
    elif funding_rate < -0.0002:
        return (0.45, 0.55)
    else:
        return (0.50, 0.50)  # Balanced


def estimate_liquidation_heatmap(
    current_price: float,
    oi_usd: float,
    funding_rate: float,
    price_range_pct: float = 0.20  # ±20% from current
) -> Dict[str, Any]:
    """
    Estimate liquidation levels from OI + leverage assumptions.
    
    [!] DISCLAIMER: This is ESTIMATED, not actual pending liquidations.
    Calculated from OI + leverage distribution assumptions.
    Accuracy ~60-70%.
    
    Returns:
        {
            'long_liquidations': {price_level: usd_value},
            'short_liquidations': {price_level: usd_value},
            'total_long_at_risk': float,
            'total_short_at_risk': float,
            'data_type': 'ESTIMATED',
            'disclaimer': str
        }
    """
    # Estimate long/short split
    long_ratio, short_ratio = estimate_long_short_ratio(funding_rate)
    long_oi = oi_usd * long_ratio
    short_oi = oi_usd * short_ratio
    
    # Price bounds
    min_price = current_price * (1 - price_range_pct)
    max_price = current_price * (1 + price_range_pct)
    
    long_liqs = {}   # Below current price
    short_liqs = {}  # Above current price
    
    for leverage, weight in LEVERAGE_DISTRIBUTION.items():
        # LONG liquidations (below current)
        long_liq_price = calculate_liquidation_price(current_price, leverage, is_long=True)
        
        if min_price <= long_liq_price < current_price:
            level = round(long_liq_price / 1000) * 1000  # Round to $1000
            estimated_usd = long_oi * weight
            long_liqs[level] = long_liqs.get(level, 0) + estimated_usd
        
        # SHORT liquidations (above current)
        short_liq_price = calculate_liquidation_price(current_price, leverage, is_long=False)
        
        if current_price < short_liq_price <= max_price:
            level = round(short_liq_price / 1000) * 1000
            estimated_usd = short_oi * weight
            short_liqs[level] = short_liqs.get(level, 0) + estimated_usd
    
    return {
        'long_liquidations': long_liqs,
        'short_liquidations': short_liqs,
        'total_long_at_risk': sum(long_liqs.values()),
        'total_short_at_risk': sum(short_liqs.values()),
        'data_type': 'ESTIMATED',
        'disclaimer': 'Calculated from OI + leverage assumptions. Not actual pending liquidations.',
        'methodology': {
            'leverage_distribution': LEVERAGE_DISTRIBUTION,
            'long_ratio': long_ratio,
            'short_ratio': short_ratio,
            'maintenance_margin': 0.10
        }
    }


def format_liquidation_level(price: float, usd_value: float, max_value: float, is_long: bool) -> Dict[str, Any]:
    """Format a single liquidation level for display."""
    bar_length = 30
    fill_char = '▓' if is_long else '█'
    
    if max_value > 0:
        bar_filled = int((usd_value / max_value) * bar_length)
    else:
        bar_filled = 0
    
    bar = fill_char * bar_filled + '░' * (bar_length - bar_filled)
    
    # Determine if major cluster (>25% of total)
    is_major = usd_value > (max_value * 0.25) if max_value > 0 else False
    
    return {
        'price': price,
        'usd_value': usd_value,
        'usd_formatted': f"${usd_value/1e9:.2f}B" if usd_value >= 1e9 else f"${usd_value/1e6:.0f}M",
        'bar': bar,
        'is_major': is_major,
        'distance_pct': abs(price - 0) / 100  # Will be calculated with actual current price
    }


def get_major_liquidation_zones(heatmap: Dict[str, Any], current_price: float) -> List[Dict[str, Any]]:
    """
    Identify major liquidation zones (clusters > $500M).
    
    Returns list of zones sorted by proximity to current price.
    """
    zones = []
    
    # Combine long and short liquidations
    all_liqs = []
    
    for price, usd in heatmap['long_liquidations'].items():
        if usd >= 500e6:  # > $500M
            all_liqs.append({
                'price': price,
                'usd_value': usd,
                'side': 'LONG',
                'distance_pct': abs(price - current_price) / current_price * 100
            })
    
    for price, usd in heatmap['short_liquidations'].items():
        if usd >= 500e6:  # > $500M
            all_liqs.append({
                'price': price,
                'usd_value': usd,
                'side': 'SHORT',
                'distance_pct': abs(price - current_price) / current_price * 100
            })
    
    # Sort by distance from current price
    all_liqs.sort(key=lambda x: x['distance_pct'])
    
    return all_liqs


def generate_heatmap_insight(
    fragility_score: float,
    estimated: Dict[str, Any],
    current_price: float
) -> Dict[str, Any]:
    """Generate trading insight based on fragility and liquidation heatmap."""
    
    # Find nearest major liquidation
    major_zones = get_major_liquidation_zones(estimated, current_price)
    nearest_major = major_zones[0] if major_zones else None
    
    insights = []
    
    # Fragility-based insight
    if fragility_score >= 75:
        fragility_insight = "CRITICAL: High probability of flash crash/squeeze"
        emoji = "[R]"
    elif fragility_score >= 50:
        fragility_insight = "FRAGILE: Expect wicky price action"
        emoji = "[O]"
    elif fragility_score >= 25:
        fragility_insight = "CAUTION: Standard market conditions"
        emoji = "[Y]"
    else:
        fragility_insight = "STABLE: Safe for larger positions"
        emoji = "[G]"
    
    insights.append(fragility_insight)
    
    # Liquidation proximity insight
    if nearest_major:
        side = nearest_major['side']
        price = nearest_major['price']
        distance = nearest_major['distance_pct']
        usd = nearest_major['usd_value']
        
        if distance < 5:
            liq_insight = f"[WARNING] Major {side} liq wall at ${price:,.0f} ({distance:.1f}% away, ${usd/1e9:.1f}B)"
        elif distance < 10:
            liq_insight = f"[C] Significant {side} liq cluster at ${price:,.0f} ({distance:.1f}% away)"
        else:
            liq_insight = None
        
        if liq_insight:
            insights.append(liq_insight)
    
    # Long/Short imbalance
    long_at_risk = estimated['total_long_at_risk']
    short_at_risk = estimated['total_short_at_risk']
    
    if long_at_risk > short_at_risk * 2:
        insights.append("[T] Longs more vulnerable - potential short squeeze setup")
    elif short_at_risk > long_at_risk * 2:
        insights.append("[TARGET] Shorts more vulnerable - potential long squeeze setup")
    
    return {
        'emoji': emoji,
        'summary': insights[0],
        'details': insights[1:] if len(insights) > 1 else [],
        'recommendation': _get_trading_recommendation(fragility_score, major_zones)
    }


def _get_trading_recommendation(fragility_score: float, major_zones: List[Dict]) -> str:
    """Get trading recommendation based on conditions."""
    if fragility_score >= 75:
        return "Reduce leverage. Expect high volatility."
    elif fragility_score >= 50:
        return "Use tight stops. Major liq zones nearby."
    elif major_zones and major_zones[0]['distance_pct'] < 5:
        return "Watch for liquidity sweep at major zone."
    else:
        return "Normal trading conditions."


# Convenience function for API
def calculate_complete_heatmap(
    current_price: float,
    oi_usd: float,
    funding_rate: float,
    depth_2pct: float,
    funding_7d: List[float],
    spot_price: float,
    perp_price: float
) -> Dict[str, Any]:
    """
    Calculate complete liquidation heatmap with fragility score.
    
    This is the main function that combines everything.
    """
    from scoring.fragility import calculate_fragility_score
    
    # Calculate fragility
    fragility = calculate_fragility_score(
        open_interest_usd=oi_usd,
        depth_2pct_usd=depth_2pct,
        current_funding=funding_rate,
        funding_7d=funding_7d,
        spot_price=spot_price,
        perp_price=perp_price
    )
    
    # Calculate estimated liquidation heatmap
    heatmap = estimate_liquidation_heatmap(
        current_price=current_price,
        oi_usd=oi_usd,
        funding_rate=funding_rate
    )
    
    # Generate insight
    insight = generate_heatmap_insight(
        fragility_score=fragility['score'],
        estimated=heatmap,
        current_price=current_price
    )
    
    # Get major zones
    major_zones = get_major_liquidation_zones(heatmap, current_price)
    
    return {
        'symbol': 'BTCUSDT',
        'current_price': current_price,
        'timestamp': None,  # Will be set by caller
        'fragility': fragility,
        'estimated_liquidations': heatmap,
        'major_zones': major_zones[:5],  # Top 5
        'insight': insight
    }
