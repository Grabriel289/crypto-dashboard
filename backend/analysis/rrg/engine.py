"""Accelerating Momentum Rotation Map Engine."""
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .constants import (
    ETF_SYMBOLS, SHORT_PERIOD, LONG_PERIOD, SCALE_FACTOR,
    CENTER_VALUE, QUADRANT_SCORES, RISK_ON_THRESHOLD, RISK_OFF_THRESHOLD,
    V6_SAFE_HAVEN_KEYS, V6_WEIGHTS, V6_ENTER_THRESHOLD, V6_EXIT_THRESHOLD,
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
    return_6m: float      # 6-month (LONG_PERIOD) return % — used for Take Profit check
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
    ) -> Optional[Tuple[float, float, float]]:
        """
        Compute raw momentum, acceleration, and 6-month return for one asset.

        Args:
            closes: Daily closing prices, oldest first (need ≥ 127)

        Returns:
            (momentum_1m_pct, acceleration_pct, momentum_6m_pct) or None
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
        return momentum_1m, acceleration, momentum_6m

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
        symbols_raw: List[Tuple[str, float, float, float]] = []  # (symbol, mom_1m, acc, mom_6m)

        for symbol in ETF_SYMBOLS:
            if ETF_SYMBOLS[symbol]["category"] == "benchmark":
                continue
            if symbol not in price_data:
                continue
            raw = self._compute_raw(price_data[symbol])
            if raw is not None:
                symbols_raw.append((symbol, raw[0], raw[1], raw[2]))

        if not symbols_raw:
            return []

        # Step 2 — cross-sectional normalisation
        momentums = np.array([r[1] for r in symbols_raw])
        accels = np.array([r[2] for r in symbols_raw])

        x_scores = self._to_100_scale(momentums)
        y_scores = self._to_100_scale(accels)

        # Step 3 — build results
        results: List[RRGResult] = []
        for i, (symbol, mom, acc, mom_6m) in enumerate(symbols_raw):
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
                rs_ratio=round(x, 2),         # Momentum Score  → x-axis
                rs_momentum=round(y, 2),      # Acceleration Score → y-axis
                quadrant=quadrant,
                period_return=round(mom, 2),  # 1-month return %
                return_6m=round(mom_6m, 2),   # 6-month return % — Take Profit check
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
        risk_count = sum(risk_counts.values())
        safe_count = sum(safe_counts.values())
        max_possible = (risk_count + safe_count) * 2 or 1
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
    # V6 Composite Regime Filter
    # ------------------------------------------------------------------

    # Class-level state for hysteresis (persists across calls within process)
    _v6_prev_regime: str = "neutral"
    _v6_prev_score: Optional[float] = None

    def detect_regime_v6(
        self, results: List[RRGResult], regime: RegimeResult
    ) -> Dict:
        """
        V6 multi-factor composite regime filter with hysteresis.

        Combines 5 factors:
          1. Raw score level (from detect_regime)
          2. Score trend vs previous call
          3. Safe-haven rotation (GLD+TLT+UUP positions)
          4. BTC/IBIT quadrant
          5. Risk breadth (% risk assets in Leading/Improving)

        Returns dict with: regime, composite_score, factors breakdown
        """
        W = V6_WEIGHTS
        composite = 0.0
        factors = {}

        # ── Factor 1: Raw score level ──
        raw = regime.score
        if raw <= W["score_strong_bear"]["threshold"]:
            composite += W["score_strong_bear"]["value"]
        elif raw <= W["score_bear"]["threshold"]:
            composite += W["score_bear"]["value"]
        elif raw >= W["score_strong_bull"]["threshold"]:
            composite += W["score_strong_bull"]["value"]
        elif raw >= W["score_bull"]["threshold"]:
            composite += W["score_bull"]["value"]
        factors["raw_score"] = raw

        # ── Factor 2: Score trend (change vs previous snapshot) ──
        trend = 0.0
        if self._v6_prev_score is not None:
            trend = raw - self._v6_prev_score
            if trend <= W["trend_strong_down"]["threshold"]:
                composite += W["trend_strong_down"]["value"]
            elif trend <= W["trend_down"]["threshold"]:
                composite += W["trend_down"]["value"]
            elif trend >= W["trend_strong_up"]["threshold"]:
                composite += W["trend_strong_up"]["value"]
            elif trend >= W["trend_up"]["threshold"]:
                composite += W["trend_up"]["value"]
        factors["score_trend"] = round(trend, 1)

        # ── Factor 3: Safe-haven rotation ──
        sh_count = 0
        sh_detail = {}
        for r in results:
            if r.symbol in V6_SAFE_HAVEN_KEYS:
                bullish = r.quadrant in ("leading", "improving")
                if bullish:
                    sh_count += 1
                sh_detail[r.symbol] = r.quadrant

        if sh_count >= W["sh_full"]["count"]:
            composite += W["sh_full"]["value"]
        elif sh_count >= W["sh_partial"]["count"]:
            composite += W["sh_partial"]["value"]
        elif sh_count == W["sh_none"]["count"]:
            composite += W["sh_none"]["value"]
        factors["safe_haven"] = {"count": sh_count, "detail": sh_detail}

        # ── Factor 4: BTC / IBIT quadrant ──
        btc_quad = None
        for r in results:
            if r.symbol in ("IBIT", "ETHA"):
                btc_quad = r.quadrant
                break  # prefer IBIT (first crypto found)
        if btc_quad == "leading":
            composite += W["btc_leading"]["value"]
        elif btc_quad == "improving":
            composite += W["btc_improving"]["value"]
        elif btc_quad == "weakening":
            composite += W["btc_weakening"]["value"]
        elif btc_quad == "lagging":
            composite += W["btc_lagging"]["value"]
        factors["crypto_quad"] = btc_quad

        # ── Factor 5: Risk breadth ──
        risk_total = 0
        risk_bullish = 0
        for r in results:
            if r.category == "risk":
                risk_total += 1
                if r.quadrant in ("leading", "improving"):
                    risk_bullish += 1
        breadth = risk_bullish / risk_total * 100 if risk_total > 0 else 50

        if breadth <= W["breadth_very_low"]["threshold"]:
            composite += W["breadth_very_low"]["value"]
        elif breadth <= W["breadth_low"]["threshold"]:
            composite += W["breadth_low"]["value"]
        elif breadth >= W["breadth_very_high"]["threshold"]:
            composite += W["breadth_very_high"]["value"]
        elif breadth >= W["breadth_high"]["threshold"]:
            composite += W["breadth_high"]["value"]
        factors["risk_breadth"] = round(breadth, 1)

        composite = round(composite, 1)
        factors["composite"] = composite

        # ── Hysteresis ──
        prev = self._v6_prev_regime
        if prev == "neutral":
            if composite >= V6_ENTER_THRESHOLD:
                new_regime = "risk_on"
            elif composite <= -V6_ENTER_THRESHOLD:
                new_regime = "risk_off"
            else:
                new_regime = "neutral"
        elif prev == "risk_on":
            if composite <= -V6_ENTER_THRESHOLD:
                new_regime = "risk_off"
            elif composite < V6_EXIT_THRESHOLD:
                new_regime = "neutral"
            else:
                new_regime = "risk_on"
        elif prev == "risk_off":
            if composite >= V6_ENTER_THRESHOLD:
                new_regime = "risk_on"
            elif composite > -V6_EXIT_THRESHOLD:
                new_regime = "neutral"
            else:
                new_regime = "risk_off"
        else:
            new_regime = "neutral"

        # Update state for next call
        self._v6_prev_regime = new_regime
        self._v6_prev_score = raw

        # Color and emoji
        if new_regime == "risk_on":
            emoji, color = "🟢", "#3fb950"
        elif new_regime == "risk_off":
            emoji, color = "🔴", "#f85149"
        else:
            emoji, color = "🟡", "#d29922"

        return {
            "regime": new_regime,
            "composite_score": composite,
            "emoji": emoji,
            "color": color,
            "factors": factors,
        }

    # ------------------------------------------------------------------
    # Recommendations (unchanged logic)
    # ------------------------------------------------------------------

    def get_top_picks(self, results: List[RRGResult], count: int = 3) -> List[Dict]:
        """
        Top picks = top 3 assets ranked by acceleration (Y-score) descending.
        Matches the backtest portfolio: always hold the fastest-accelerating assets.
        """
        sorted_by_accel = sorted(results, key=lambda r: r.rs_momentum, reverse=True)
        rank_reasons = {
            1: "Fastest acceleration — highest conviction",
            2: "Strong acceleration — high conviction entry",
            3: "Accelerating — momentum building",
        }
        picks = []
        for i, result in enumerate(sorted_by_accel[:count], start=1):
            picks.append({
                "rank": i,
                "symbol": result.symbol,
                "name": result.name,
                "reason": rank_reasons.get(i, f"Acceleration rank #{i}"),
                "period_return": result.period_return,
                "color": result.color,
            })
        return picks

    def get_action_groups(self, results: List[RRGResult]) -> List[Dict]:
        """
        Rank all assets by Y-score (acceleration) descending, then assign buckets:

          Rank 1-3                           → Buy / Add
          Rank 4-6  AND  Y ≥ 100            → Watch / Entry
          Y < 100   AND  not bottom-3       → Take Profit  (decelerating, not worst)
          Bottom 3  AND  6m return > 0      → Take Profit  (profits exist — exit signal)
          Bottom 3  AND  6m return ≤ 0      → Avoid        (already underwater)

        Override: lagging quadrant assets are always Avoid (never Buy/Take Profit).
        """
        sorted_by_accel = sorted(results, key=lambda r: r.rs_momentum, reverse=True)
        n = len(sorted_by_accel)

        actions: Dict[str, List] = {"buy": [], "watch": [], "reduce": [], "avoid": []}

        for rank, result in enumerate(sorted_by_accel, start=1):
            # Lagging quadrant: Take Profit if 6m return positive (rotated down
            # from leading/weakening), otherwise Avoid
            if result.quadrant == "lagging":
                if result.return_6m > 0:
                    actions["reduce"].append(result.symbol)
                else:
                    actions["avoid"].append(result.symbol)
            elif rank <= 3:
                actions["buy"].append(result.symbol)
            elif rank <= 6 and result.rs_momentum >= 100:
                actions["watch"].append(result.symbol)
            elif result.rs_momentum < 100 and rank <= n - 3:
                actions["reduce"].append(result.symbol)
            elif result.return_6m > 0:
                actions["reduce"].append(result.symbol)
            else:
                actions["avoid"].append(result.symbol)

        action_labels = {
            "buy":    {"label": "Buy / Add",     "emoji": "✅"},
            "watch":  {"label": "Watch / Entry", "emoji": "📌"},
            "reduce": {"label": "Take Profit",   "emoji": "⚠️"},
            "avoid":  {"label": "Avoid",         "emoji": "🚫"},
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
        """
        Generate up to 3 key insights based on Top-3 acceleration composition,
        crypto status, watch-list rotation, and take-profit warnings.
        """
        sorted_by_accel = sorted(results, key=lambda r: r.rs_momentum, reverse=True)
        n = len(sorted_by_accel)
        top3 = sorted_by_accel[:3]
        insights = []

        # Insight 1: Top-3 composition — risk vs safe-haven dominance
        risk_in_top3 = [r for r in top3 if r.category == "risk"]
        safe_in_top3 = [r for r in top3 if r.category == "safe_haven"]

        if len(risk_in_top3) >= 2:
            names = " & ".join(r.name for r in risk_in_top3[:2])
            insights.append({
                "emoji": "🚀",
                "text": f"{names} accelerating — Risk appetite is HIGH",
                "highlight": names,
            })
        elif len(safe_in_top3) >= 2:
            names = " & ".join(r.name for r in safe_in_top3[:2])
            insights.append({
                "emoji": "🛡️",
                "text": f"{names} leading — Flight to safety detected",
                "highlight": names,
            })

        # Insight 2: Crypto (IBIT / ETHA) status
        crypto = [r for r in results if r.symbol in ("IBIT", "ETHA")]
        crypto_accel = [r for r in crypto if r.rs_momentum >= 100]
        crypto_decel = [r for r in crypto if r.rs_momentum < 100]

        if crypto_accel:
            names = " & ".join(r.symbol for r in crypto_accel)
            insights.append({
                "emoji": "📈",
                "text": f"{names} accelerating — Crypto recovery signal",
                "highlight": names,
            })
        elif crypto_decel:
            names = " & ".join(r.symbol for r in crypto_decel)
            insights.append({
                "emoji": "📉",
                "text": f"{names} decelerating — Stay cautious on crypto",
                "highlight": names,
            })

        # Insight 3: Watch-list (rank 4-6, still accelerating) — rotation candidates
        watch_candidates = [
            r for rank, r in enumerate(sorted_by_accel, start=1)
            if 4 <= rank <= 6 and r.rs_momentum >= 100
        ]
        if watch_candidates:
            names = ", ".join(r.symbol for r in watch_candidates[:2])
            insights.append({
                "emoji": "👀",
                "text": f"{names} approaching top — Watch for rotation",
                "highlight": names,
            })

        # Insight 4: Take-profit warning (decelerating, not bottom-3)
        take_profit = [
            r for rank, r in enumerate(sorted_by_accel, start=1)
            if r.rs_momentum < 100 and rank <= n - 3
        ]
        if take_profit:
            names = ", ".join(r.symbol for r in take_profit[:2])
            insights.append({
                "emoji": "⚠️",
                "text": f"{names} losing momentum — Consider taking profit",
                "highlight": names,
            })

        return insights[:3]

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
