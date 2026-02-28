"""Accelerating Momentum Rotation Map Engine."""
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .constants import (
    ETF_SYMBOLS, SHORT_PERIOD, LONG_PERIOD, SCALE_FACTOR,
    CENTER_VALUE, QUADRANT_SCORES, RISK_ON_THRESHOLD, RISK_OFF_THRESHOLD,
)


@dataclass
class RRGResult:
    """Result of Accelerating Momentum calculation for a single ETF."""
    symbol: str
    name: str
    category: str
    color: str
    rs_ratio: float      # X-axis: Momentum Score  (100-centered)
    rs_momentum: float   # Y-axis: Acceleration Score (100-centered)
    quadrant: str
    period_return: float  # 1-month (SHORT_PERIOD) return %
    current_price: float


@dataclass
class RegimeResult:
    """Market regime detection result."""
    regime: str   # "risk_on" | "risk_off" | "neutral"
    score: float
    risk_summary: str
    safe_summary: str
    emoji: str
    color: str


class RRGEngine:
    """
    Accelerating Momentum Rotation Map Engine.

    Replaces the old RS-Ratio / RS-Momentum formula with:

      X-Axis (Momentum Score):
          momentum_1m = (price_now / price[-21]) - 1   ×100

      Y-Axis (Acceleration Score):
          momentum_6m_norm = ((price_now / price[-126]) - 1) ×100
                             × (21 / 126)
          acceleration = momentum_1m - momentum_6m_norm

    Both axes are cross-sectionally z-score-normalised across all tracked
    assets, then mapped to a 100-centred scale where 1 std = SCALE_FACTOR
    points.  The output field names (rs_ratio, rs_momentum) are kept
    unchanged so the API and frontend require no modification.
    """

    def __init__(self):
        self.min_points = LONG_PERIOD + 1   # 127 daily prices required

    # ------------------------------------------------------------------
    # Raw computation (single asset)
    # ------------------------------------------------------------------

    def _compute_raw(
        self, closes: List[float]
    ) -> Optional[Tuple[float, float]]:
        """
        Compute raw momentum and acceleration for one asset.

        Args:
            closes: Daily closing prices, oldest first (need ≥ 127)

        Returns:
            (momentum_1m_pct, acceleration_pct) or None if insufficient data
        """
        if len(closes) < self.min_points:
            return None

        price_now = closes[-1]
        price_short = closes[-(SHORT_PERIOD + 1)]   # 21 trading days ago
        price_long = closes[-(LONG_PERIOD + 1)]     # 126 trading days ago

        momentum_1m = (price_now / price_short - 1) * 100
        momentum_6m = (price_now / price_long - 1) * 100
        momentum_6m_norm = momentum_6m * (SHORT_PERIOD / LONG_PERIOD)

        acceleration = momentum_1m - momentum_6m_norm
        return momentum_1m, acceleration

    # ------------------------------------------------------------------
    # Cross-sectional normalisation
    # ------------------------------------------------------------------

    @staticmethod
    def _to_100_scale(values: np.ndarray) -> np.ndarray:
        """
        Z-score normalise an array, then shift to 100-centred scale.
        1 std dev = SCALE_FACTOR points from 100.
        If std == 0, all assets score exactly 100.
        """
        std = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        if std == 0:
            return np.full(len(values), CENTER_VALUE)
        mean = float(np.mean(values))
        z = (values - mean) / std
        return CENTER_VALUE + z * SCALE_FACTOR

    # ------------------------------------------------------------------
    # Main calculation
    # ------------------------------------------------------------------

    def calculate_all(
        self, price_data: Dict[str, List[float]]
    ) -> List[RRGResult]:
        """
        Calculate Accelerating Momentum scores for all tracked ETFs.

        Steps:
        1. Compute raw momentum & acceleration for every non-benchmark asset.
        2. Normalise cross-sectionally (z-score → 100-centred).
        3. Return RRGResult list with rs_ratio=x_score, rs_momentum=y_score.

        Args:
            price_data: symbol → list of daily closing prices (oldest first)
        """
        # Step 1 — raw values
        symbols_raw: List[Tuple[str, float, float]] = []  # (symbol, mom, acc)

        for symbol in ETF_SYMBOLS:
            if ETF_SYMBOLS[symbol]["category"] == "benchmark":
                continue
            if symbol not in price_data:
                continue
            raw = self._compute_raw(price_data[symbol])
            if raw is not None:
                symbols_raw.append((symbol, raw[0], raw[1]))

        if not symbols_raw:
            return []

        # Step 2 — cross-sectional normalisation
        momentums = np.array([r[1] for r in symbols_raw])
        accels = np.array([r[2] for r in symbols_raw])

        x_scores = self._to_100_scale(momentums)
        y_scores = self._to_100_scale(accels)

        # Step 3 — build results
        results: List[RRGResult] = []
        for i, (symbol, mom, acc) in enumerate(symbols_raw):
            x = float(x_scores[i])
            y = float(y_scores[i])
            quadrant = self._determine_quadrant(x, y)
            metadata = ETF_SYMBOLS[symbol]
            closes = price_data[symbol]

            results.append(RRGResult(
                symbol=symbol,
                name=metadata["name"],
                category=metadata["category"],
                color=metadata["color"],
                rs_ratio=round(x, 2),        # Momentum Score  → x-axis
                rs_momentum=round(y, 2),     # Acceleration Score → y-axis
                quadrant=quadrant,
                period_return=round(mom, 2), # 1-month return %
                current_price=closes[-1],
            ))

        return results

    # ------------------------------------------------------------------
    # Regime detection (unchanged logic)
    # ------------------------------------------------------------------

    def detect_regime(self, results: List[RRGResult]) -> RegimeResult:
        risk_score = 0
        safe_score = 0

        risk_counts: Dict[str, int] = {"leading": 0, "improving": 0, "weakening": 0, "lagging": 0}
        safe_counts: Dict[str, int] = {"leading": 0, "improving": 0, "weakening": 0, "lagging": 0}

        for result in results:
            quadrant_score = QUADRANT_SCORES.get(result.quadrant, 0)
            if result.category == "risk":
                risk_score += quadrant_score
                risk_counts[result.quadrant] = risk_counts.get(result.quadrant, 0) + 1
            elif result.category == "safe_haven":
                safe_score += (-quadrant_score)
                safe_counts[result.quadrant] = safe_counts.get(result.quadrant, 0) + 1

        net_score = risk_score + safe_score
        max_possible = 18
        normalized_score = (net_score / max_possible) * 10

        if normalized_score >= RISK_ON_THRESHOLD:
            regime, emoji, color = "risk_on", "📈", "#3fb950"
        elif normalized_score <= RISK_OFF_THRESHOLD:
            regime, emoji, color = "risk_off", "📉", "#f85149"
        else:
            regime, emoji, color = "neutral", "⚖️", "#d29922"

        return RegimeResult(
            regime=regime,
            score=round(normalized_score, 1),
            risk_summary=self._format_summary(risk_counts),
            safe_summary=self._format_summary(safe_counts),
            emoji=emoji,
            color=color,
        )

    # ------------------------------------------------------------------
    # Recommendations (unchanged logic)
    # ------------------------------------------------------------------

    def get_top_picks(self, results: List[RRGResult], count: int = 3) -> List[Dict]:
        candidates = [r for r in results if r.quadrant in ("leading", "improving")]

        def sort_key(r: RRGResult):
            return ({"leading": 0, "improving": 1}.get(r.quadrant, 99), -r.period_return)

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
                "color": result.color,
            })
        return picks

    def get_action_groups(self, results: List[RRGResult]) -> List[Dict]:
        actions: Dict[str, List] = {"buy": [], "watch": [], "reduce": [], "avoid": []}
        for result in results:
            action = self._determine_action(result.quadrant, result.category)
            actions[action].append(result.symbol)

        action_labels = {
            "buy":    {"label": "Buy / Add",      "emoji": "✅"},
            "watch":  {"label": "Watch / Entry",  "emoji": "📌"},
            "reduce": {"label": "Take Profit",    "emoji": "⚠️"},
            "avoid":  {"label": "Avoid",          "emoji": "🚫"},
        }
        return [
            {
                "action": action,
                "label": action_labels[action]["label"],
                "emoji": action_labels[action]["emoji"],
                "symbols": actions[action],
            }
            for action in ["buy", "watch", "reduce", "avoid"]
            if actions[action]
        ]

    def generate_insights(
        self, results: List[RRGResult], regime: RegimeResult
    ) -> List[Dict]:
        insights = []

        leading = [r for r in results if r.quadrant == "leading"]
        if leading:
            names = " & ".join(r.name for r in leading[:2])
            insights.append({
                "emoji": "🚀",
                "text": f"{names} leading — Risk appetite is HIGH",
                "highlight": names,
            })

        safe_weakening = [
            r for r in results
            if r.category == "safe_haven" and r.quadrant in ("weakening", "lagging")
        ]
        if safe_weakening:
            names = " & ".join(r.name for r in safe_weakening[:2])
            insights.append({
                "emoji": "⚠️",
                "text": (
                    f"{names} weakening — Safe haven outflow confirms "
                    f"{regime.regime.replace('_', '-').upper()}"
                ),
                "highlight": names,
            })

        usd = next((r for r in results if r.symbol == "UUP"), None)
        if usd and usd.quadrant == "leading":
            insights.append({
                "emoji": "💵",
                "text": "USD strong — Dollar strength (watch for divergence)",
                "highlight": "USD",
            })

        improving = [
            r for r in results
            if r.quadrant == "improving" and r.category == "risk"
        ]
        if improving:
            names = " & ".join(r.name for r in improving[:2])
            insights.append({
                "emoji": "📈",
                "text": f"{names} improving — Rally broadening signal",
                "highlight": names,
            })

        return insights[:5]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _determine_quadrant(self, x: float, y: float) -> str:
        if x >= 100 and y >= 100:
            return "leading"
        elif x < 100 and y >= 100:
            return "improving"
        elif x >= 100 and y < 100:
            return "weakening"
        else:
            return "lagging"

    def _determine_action(self, quadrant: str, category: str) -> str:
        # Recommendation is quadrant-only; category is for display grouping only
        return {"leading": "buy", "improving": "watch",
                "weakening": "reduce", "lagging": "avoid"}[quadrant]

    def _format_summary(self, counts: Dict[str, int]) -> str:
        parts = []
        for q in ("leading", "improving", "weakening", "lagging"):
            if counts.get(q, 0) > 0:
                parts.append(f"{counts[q]} {q.capitalize()}")
        return ", ".join(parts) if parts else "None"
