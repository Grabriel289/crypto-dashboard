"""Momentum scoring module."""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from config.sectors import SECTORS
import pandas as pd
import numpy as np


@dataclass
class MomentumMetrics:
    """Raw momentum data for a single asset."""
    return_1d: float = 0.0
    return_7d: float = 0.0
    return_30d: float = 0.0
    return_1d_vs_btc: float = 0.0
    return_7d_vs_btc: float = 0.0
    return_30d_vs_btc: float = 0.0
    volume_change_7d: float = 0.0


def calculate_momentum_score(metrics: MomentumMetrics) -> int:
    """
    Calculate momentum score (0-100).
    Components: Absolute Momentum (40%) + Relative vs BTC (40%) + Volume Confirmation (20%)
    """
    score = 0
    
    # ═══════════════════════════════════════════════════════════════
    # COMPONENT 1: ABSOLUTE MOMENTUM (40 points max)
    # ═══════════════════════════════════════════════════════════════
    
    # 1D Return (10 points)
    if metrics.return_1d > 5:
        score += 10
    elif metrics.return_1d > 2:
        score += 8
    elif metrics.return_1d > 0:
        score += 5
    elif metrics.return_1d > -2:
        score += 3
    
    # 7D Return (15 points) - Most important timeframe
    if metrics.return_7d > 15:
        score += 15
    elif metrics.return_7d > 8:
        score += 12
    elif metrics.return_7d > 3:
        score += 9
    elif metrics.return_7d > 0:
        score += 6
    elif metrics.return_7d > -5:
        score += 3
    
    # 30D Return (15 points) - Trend confirmation
    if metrics.return_30d > 30:
        score += 15
    elif metrics.return_30d > 15:
        score += 12
    elif metrics.return_30d > 5:
        score += 9
    elif metrics.return_30d > 0:
        score += 6
    elif metrics.return_30d > -10:
        score += 3
    
    # ═══════════════════════════════════════════════════════════════
    # COMPONENT 2: RELATIVE MOMENTUM vs BTC (40 points max)
    # ═══════════════════════════════════════════════════════════════
    
    # 7D vs BTC (25 points) - Key metric for rotation decision
    if metrics.return_7d_vs_btc > 10:
        score += 25
    elif metrics.return_7d_vs_btc > 5:
        score += 20
    elif metrics.return_7d_vs_btc > 2:
        score += 15
    elif metrics.return_7d_vs_btc > 0:
        score += 10
    elif metrics.return_7d_vs_btc > -2:
        score += 5
    
    # 30D vs BTC (15 points) - Trend confirmation
    if metrics.return_30d_vs_btc > 15:
        score += 15
    elif metrics.return_30d_vs_btc > 5:
        score += 10
    elif metrics.return_30d_vs_btc > 0:
        score += 7
    elif metrics.return_30d_vs_btc > -5:
        score += 3
    
    # ═══════════════════════════════════════════════════════════════
    # COMPONENT 3: VOLUME CONFIRMATION (20 points max)
    # ═══════════════════════════════════════════════════════════════
    
    if metrics.volume_change_7d > 50 and metrics.return_7d > 0:
        score += 20
    elif metrics.volume_change_7d > 20 and metrics.return_7d > 0:
        score += 15
    elif metrics.volume_change_7d > 0:
        score += 10
    elif metrics.volume_change_7d > -20:
        score += 5
    
    return min(100, score)


def calculate_momentum_from_prices(price_data: pd.DataFrame, btc_data: Optional[pd.DataFrame] = None) -> MomentumMetrics:
    """Calculate momentum metrics from price dataframe."""
    if price_data is None or len(price_data) < 30:
        return MomentumMetrics()
    
    # Calculate returns
    current_price = price_data["close"].iloc[-1]
    price_1d = price_data["close"].iloc[-2] if len(price_data) >= 2 else current_price
    price_7d = price_data["close"].iloc[-8] if len(price_data) >= 8 else price_data["close"].iloc[0]
    price_30d = price_data["close"].iloc[0]
    
    return_1d = ((current_price / price_1d) - 1) * 100
    return_7d = ((current_price / price_7d) - 1) * 100
    return_30d = ((current_price / price_30d) - 1) * 100
    
    # Volume change
    current_vol = price_data["volume"].iloc[-7:].mean() if len(price_data) >= 7 else price_data["volume"].mean()
    prev_vol = price_data["volume"].iloc[-14:-7].mean() if len(price_data) >= 14 else price_data["volume"].iloc[:7].mean()
    volume_change_7d = ((current_vol / prev_vol) - 1) * 100 if prev_vol > 0 else 0
    
    # Relative to BTC
    return_1d_vs_btc = return_1d
    return_7d_vs_btc = return_7d
    return_30d_vs_btc = return_30d
    
    if btc_data is not None and len(btc_data) >= 30:
        btc_current = btc_data["close"].iloc[-1]
        btc_1d = btc_data["close"].iloc[-2] if len(btc_data) >= 2 else btc_current
        btc_7d = btc_data["close"].iloc[-8] if len(btc_data) >= 8 else btc_data["close"].iloc[0]
        btc_30d = btc_data["close"].iloc[0]
        
        btc_return_1d = ((btc_current / btc_1d) - 1) * 100
        btc_return_7d = ((btc_current / btc_7d) - 1) * 100
        btc_return_30d = ((btc_current / btc_30d) - 1) * 100
        
        return_1d_vs_btc = return_1d - btc_return_1d
        return_7d_vs_btc = return_7d - btc_return_7d
        return_30d_vs_btc = return_30d - btc_return_30d
    
    return MomentumMetrics(
        return_1d=return_1d,
        return_7d=return_7d,
        return_30d=return_30d,
        return_1d_vs_btc=return_1d_vs_btc,
        return_7d_vs_btc=return_7d_vs_btc,
        return_30d_vs_btc=return_30d_vs_btc,
        volume_change_7d=volume_change_7d
    )
