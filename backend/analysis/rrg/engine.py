"""RRG (Relative Rotation Graph) Calculation Engine."""
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .constants import (
    ETF_SYMBOLS, RS_RATIO_PERIOD, RS_MOMENTUM_PERIOD, 
    CENTER_VALUE, QUADRANT_SCORES, RISK_ON_THRESHOLD, RISK_OFF_THRESHOLD
)


@dataclass
class RRGResult:
    """Result of RRG calculation for a single ETF."""
    symbol: str
    name: str
    category: str
    color: str
    rs_ratio: float
    rs_momentum: float
    quadrant: str
    period_return: float
    current_price: float


@dataclass
class RegimeResult:
    """Market regime detection result."""
    regime: str  # "risk_on", "risk_off", "neutral"
    score: float
    risk_summary: str
    safe_summary: str
    emoji: str
    color: str


class RRGEngine:
    """
    RRG Calculation Engine.
    
    Calculates RS-Ratio (X-axis) and RS-Momentum (Y-axis) for ETFs.
    
    Data Process:
    1. Fetch daily prices from Yahoo Finance
    2. Resample to weekly closing prices (Friday close)
    3. Calculate RS using weekly data (filters daily noise)
    
    Formula:
    1. Raw RS = ETF_Weekly_Close / Benchmark_Weekly_Close
    2. RS-Ratio = (Raw_RS / SMA(Raw_RS, 10_weeks)) × 100
    3. RS-Momentum = (RS_Ratio / SMA(RS_Ratio, 6_weeks)) × 100
    """
    
    def __init__(self):
        self.rs_ratio_period = RS_RATIO_PERIOD
        self.rs_momentum_period = RS_MOMENTUM_PERIOD
        self.min_points = RS_RATIO_PERIOD + RS_MOMENTUM_PERIOD + 5
    
    def calculate(
        self, 
        symbol: str, 
        etf_closes: List[float], 
        benchmark_closes: List[float]
    ) -> Optional[RRGResult]:
        """
        Calculate RRG coordinates for a single ETF.
        
        Args:
            symbol: ETF symbol
            etf_closes: List of ETF closing prices
            benchmark_closes: List of benchmark closing prices
            
        Returns:
            RRGResult with coordinates and metadata
        """
        if len(etf_closes) < self.min_points or len(benchmark_closes) < self.min_points:
            return None
        
        try:
            # Step 1: Calculate Raw RS
            raw_rs = np.array(etf_closes) / np.array(benchmark_closes)
            
            # Step 2: Calculate RS-Ratio
            rs_ratio_series = self._calculate_rs_ratio(raw_rs)
            
            # Step 3: Calculate RS-Momentum
            rs_momentum = self._calculate_rs_momentum(rs_ratio_series)
            
            # Get current values
            current_rs_ratio = rs_ratio_series[-1]
            current_raw_rs = raw_rs[-1]
            
            # Calculate period return (over RS_RATIO_PERIOD weeks)
            period_return = ((etf_closes[-1] / etf_closes[-RS_RATIO_PERIOD]) - 1) * 100
            
            # Determine quadrant
            quadrant = self._determine_quadrant(current_rs_ratio, rs_momentum)
            
            # Get metadata
            metadata = ETF_SYMBOLS.get(symbol, {})
            
            return RRGResult(
                symbol=symbol,
                name=metadata.get("name", symbol),
                category=metadata.get("category", "unknown"),
                color=metadata.get("color", "#6b7280"),
                rs_ratio=round(current_rs_ratio, 2),
                rs_momentum=round(rs_momentum, 2),
                quadrant=quadrant,
                period_return=round(period_return, 2),
                current_price=etf_closes[-1]
            )
            
        except Exception as e:
            print(f"RRG calculation error for {symbol}: {e}")
            return None
    
    def calculate_all(
        self, 
        price_data: Dict[str, List[float]]
    ) -> List[RRGResult]:
        """
        Calculate RRG for all tracked ETFs.
        
        Args:
            price_data: Dict mapping symbol to list of closing prices
            
        Returns:
            List of RRGResult objects
        """
        if "SPY" not in price_data:
            return []
        
        benchmark_closes = price_data["SPY"]
        results = []
        
        for symbol in ETF_SYMBOLS:
            if symbol == "SPY":
                continue
            if symbol not in price_data:
                continue
            
            result = self.calculate(symbol, price_data[symbol], benchmark_closes)
            if result:
                results.append(result)
        
        return results
    
    def detect_regime(self, results: List[RRGResult]) -> RegimeResult:
        """
        Detect market regime from RRG positions.
        
        Args:
            results: List of RRG results
            
        Returns:
            RegimeResult with classification
        """
        risk_score = 0
        safe_score = 0
        
        risk_counts = {"leading": 0, "improving": 0, "weakening": 0, "lagging": 0}
        safe_counts = {"leading": 0, "improving": 0, "weakening": 0, "lagging": 0}
        
        for result in results:
            quadrant_score = QUADRANT_SCORES.get(result.quadrant, 0)
            
            if result.category == "risk":
                risk_score += quadrant_score
                risk_counts[result.quadrant] = risk_counts.get(result.quadrant, 0) + 1
            elif result.category == "safe_haven":
                # Invert safe haven scores
                safe_score += (-quadrant_score)
                safe_counts[result.quadrant] = safe_counts.get(result.quadrant, 0) + 1
        
        # Calculate net score
        net_score = risk_score + safe_score
        max_possible = 18  # (5 risk + 4 safe) * 2
        normalized_score = (net_score / max_possible) * 10
        
        # Classify regime
        if normalized_score >= RISK_ON_THRESHOLD:
            regime = "risk_on"
            emoji = "📈"
            color = "#3fb950"
        elif normalized_score <= RISK_OFF_THRESHOLD:
            regime = "risk_off"
            emoji = "📉"
            color = "#f85149"
        else:
            regime = "neutral"
            emoji = "⚖️"
            color = "#d29922"
        
        # Format summaries
        risk_summary = self._format_summary(risk_counts)
        safe_summary = self._format_summary(safe_counts)
        
        return RegimeResult(
            regime=regime,
            score=round(normalized_score, 1),
            risk_summary=risk_summary,
            safe_summary=safe_summary,
            emoji=emoji,
            color=color
        )
    
    def get_top_picks(self, results: List[RRGResult], count: int = 3) -> List[Dict]:
        """
        Generate top investment picks from RRG results.
        
        Criteria:
        1. Leading quadrant first
        2. Improving quadrant second
        3. Sort by period return within each group
        """
        # Filter to leading and improving
        candidates = [r for r in results if r.quadrant in ("leading", "improving")]
        
        # Sort by quadrant priority then return
        def sort_key(r: RRGResult):
            quadrant_order = {"leading": 0, "improving": 1}
            return (quadrant_order.get(r.quadrant, 99), -r.period_return)
        
        candidates.sort(key=sort_key)
        
        picks = []
        for i, result in enumerate(candidates[:count], start=1):
            reason = {
                "leading": "Strongest momentum, leading rotation",
                "improving": "Improving momentum, early entry",
            }.get(result.quadrant, "")
            
            picks.append({
                "rank": i,
                "symbol": result.symbol,
                "name": result.name,
                "reason": reason,
                "period_return": result.period_return,
                "color": result.color
            })
        
        return picks
    
    def get_action_groups(self, results: List[RRGResult]) -> List[Dict]:
        """Group ETFs by recommended action."""
        actions = {
            "buy": [],
            "watch": [],
            "reduce": [],
            "avoid": []
        }
        
        for result in results:
            action = self._determine_action(result.quadrant, result.category)
            actions[action].append(result.symbol)
        
        action_order = ["buy", "watch", "reduce", "avoid"]
        action_labels = {
            "buy": {"label": "Buy / Add", "emoji": "✅"},
            "watch": {"label": "Watch / Entry", "emoji": "📌"},
            "reduce": {"label": "Take Profit", "emoji": "⚠️"},
            "avoid": {"label": "Avoid", "emoji": "🚫"},
        }
        
        return [
            {
                "action": action,
                "label": action_labels[action]["label"],
                "emoji": action_labels[action]["emoji"],
                "symbols": actions[action]
            }
            for action in action_order
            if actions[action]
        ]
    
    def generate_insights(
        self, 
        results: List[RRGResult], 
        regime: RegimeResult
    ) -> List[Dict]:
        """Generate key insights based on current state."""
        insights = []
        
        # Leading assets
        leading = [r for r in results if r.quadrant == "leading"]
        if leading:
            names = " & ".join([r.name for r in leading[:2]])
            insights.append({
                "emoji": "🚀",
                "text": f"{names} leading — Risk appetite is HIGH",
                "highlight": names
            })
        
        # Weakening safe haven
        safe_weakening = [
            r for r in results
            if r.category == "safe_haven" and r.quadrant in ("weakening", "lagging")
        ]
        if safe_weakening:
            names = " & ".join([r.name for r in safe_weakening[:2]])
            insights.append({
                "emoji": "⚠️",
                "text": f"{names} weakening — Safe haven outflow confirms {regime.regime.replace('_', '-').upper()}",
                "highlight": names
            })
        
        # USD status
        usd = next((r for r in results if r.symbol == "UUP"), None)
        if usd and usd.quadrant == "leading":
            insights.append({
                "emoji": "💵",
                "text": "USD strong — Dollar strength (watch for divergence)",
                "highlight": "USD"
            })
        
        # Improving risk assets
        improving = [
            r for r in results
            if r.quadrant == "improving" and r.category == "risk"
        ]
        if improving:
            names = " & ".join([r.name for r in improving[:2]])
            insights.append({
                "emoji": "📈",
                "text": f"{names} improving — Rally broadening signal",
                "highlight": names
            })
        
        return insights[:5]  # Max 5 insights
    
    def _calculate_rs_ratio(self, raw_rs: np.ndarray) -> np.ndarray:
        """Calculate RS-Ratio series."""
        sma = self._sma(raw_rs, self.rs_ratio_period)
        rs_ratio = (raw_rs / sma) * CENTER_VALUE
        return rs_ratio
    
    def _calculate_rs_momentum(self, rs_ratio: np.ndarray) -> float:
        """Calculate RS-Momentum (latest value only)."""
        if len(rs_ratio) < self.rs_momentum_period:
            return CENTER_VALUE
        
        sma = self._sma(rs_ratio, self.rs_momentum_period)
        rs_momentum = (rs_ratio[-1] / sma[-1]) * CENTER_VALUE
        return rs_momentum
    
    def _sma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average."""
        if len(data) < period:
            return np.full_like(data, data[0])
        
        cumsum = np.cumsum(np.insert(data, 0, 0))
        sma = (cumsum[period:] - cumsum[:-period]) / period
        padding = np.full(period - 1, sma[0])
        return np.concatenate([padding, sma])
    
    def _determine_quadrant(self, rs_ratio: float, rs_momentum: float) -> str:
        """Determine quadrant from coordinates."""
        if rs_ratio > 100 and rs_momentum > 100:
            return "leading"
        elif rs_ratio > 100 and rs_momentum <= 100:
            return "weakening"
        elif rs_ratio <= 100 and rs_momentum <= 100:
            return "lagging"
        else:
            return "improving"
    
    def _determine_action(self, quadrant: str, category: str) -> str:
        """Determine action signal based on quadrant and category."""
        if category == "risk":
            return {
                "leading": "buy",
                "improving": "watch",
                "weakening": "reduce",
                "lagging": "avoid"
            }[quadrant]
        else:  # safe_haven
            return {
                "leading": "watch",
                "improving": "watch",
                "weakening": "reduce",
                "lagging": "avoid"
            }[quadrant]
    
    def _format_summary(self, counts: Dict[str, int]) -> str:
        """Format quadrant counts as summary string."""
        parts = []
        if counts.get("leading", 0) > 0:
            parts.append(f"{counts['leading']} Leading")
        if counts.get("improving", 0) > 0:
            parts.append(f"{counts['improving']} Improving")
        if counts.get("weakening", 0) > 0:
            parts.append(f"{counts['weakening']} Weakening")
        if counts.get("lagging", 0) > 0:
            parts.append(f"{counts['lagging']} Lagging")
        return ", ".join(parts) if parts else "None"
