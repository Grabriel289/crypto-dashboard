"""Altcoin Breadth Momentum (ABM) calculation engine.

Produces two signals:
  1. BM (Breadth Momentum 14D) — entry/exit timing
  2. ETH/BTC ROC (7D) — peak warning

See AltcoinBreadthMomentum_Spec_v2.md for full specification.
"""
from typing import Dict, List, Any, Optional

from .constants import (
    ABM_UNIVERSE,
    BREADTH_LOOKBACK,
    BM_LOOKBACK,
    ETH_ROC_LOOKBACK,
    BM_ENTRY_THRESHOLD,
    BM_EXIT_THRESHOLD,
    ETH_ROC_WARN,
    ETH_ROC_BEAR,
    MIN_VALID_COUNT,
)


class ABMEngine:
    """Calculate Altcoin Breadth Momentum signals from daily close prices."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _align_by_date(
        price_data: Dict[str, List[Dict]],
    ) -> tuple:
        """
        Build a date-aligned matrix of closes.

        Returns:
            (dates, btc_closes, alt_closes_dict)
            where alt_closes_dict maps coin → list of closes aligned to dates.
            Missing values are None.
        """
        # Collect all unique dates that BTC has data for (BTC is required)
        btc_raw = price_data.get("BTC", [])
        if not btc_raw:
            return [], [], {}

        btc_map = {d["date"]: d["close"] for d in btc_raw}
        dates = sorted(btc_map.keys())

        btc_closes = [btc_map[d] for d in dates]

        # Build per-coin close maps
        alt_coins = [c for c in price_data if c != "BTC"]
        alt_maps = {}
        for coin in alt_coins:
            cmap = {d["date"]: d["close"] for d in price_data[coin]}
            alt_maps[coin] = cmap

        # Align alts to BTC date grid
        alt_closes: Dict[str, List[Optional[float]]] = {}
        for coin in alt_coins:
            alt_closes[coin] = [alt_maps[coin].get(d) for d in dates]

        return dates, btc_closes, alt_closes

    # ------------------------------------------------------------------
    # Breadth time series
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_breadth_series(
        dates: List[str],
        btc_closes: List[float],
        alt_closes: Dict[str, List[Optional[float]]],
    ) -> List[Dict]:
        """
        For each day t (where t >= BREADTH_LOOKBACK), compute:
          breadth_t = (# altcoins with 30D return > BTC 30D return) / valid_count * 100

        Returns list of {date, breadth, valid_count, outperform_count}.
        """
        n = len(dates)
        lb = BREADTH_LOOKBACK
        series = []

        for t in range(lb, n):
            btc_now = btc_closes[t]
            btc_ago = btc_closes[t - lb]
            if btc_ago == 0:
                continue
            btc_ret = (btc_now / btc_ago - 1) * 100

            valid = 0
            outperform = 0

            for coin, closes in alt_closes.items():
                close_now = closes[t]
                close_ago = closes[t - lb]
                if close_now is None or close_ago is None or close_ago == 0:
                    continue
                valid += 1
                alt_ret = (close_now / close_ago - 1) * 100
                if alt_ret > btc_ret:
                    outperform += 1

            if valid < MIN_VALID_COUNT:
                continue

            breadth = (outperform / valid) * 100
            series.append({
                "date": dates[t],
                "breadth": round(breadth, 2),
                "valid_count": valid,
                "outperform_count": outperform,
            })

        return series

    # ------------------------------------------------------------------
    # BM signal series
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_bm_series(breadth_series: List[Dict]) -> List[Dict]:
        """
        BM_t = breadth_t - breadth_{t-14}

        Returns list of {date, bm}.
        """
        lb = BM_LOOKBACK
        if len(breadth_series) <= lb:
            return []

        bm_series = []
        for i in range(lb, len(breadth_series)):
            bm = breadth_series[i]["breadth"] - breadth_series[i - lb]["breadth"]
            bm_series.append({
                "date": breadth_series[i]["date"],
                "bm": round(bm, 2),
            })
        return bm_series

    # ------------------------------------------------------------------
    # ETH/BTC ROC series
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_eth_roc_series(
        dates: List[str],
        btc_closes: List[float],
        eth_closes: List[Optional[float]],
    ) -> List[Dict]:
        """
        eth_btc_ratio_t = eth_close_t / btc_close_t
        eth_roc_t = (ratio_t / ratio_{t-7} - 1) * 100

        Returns list of {date, roc}.
        """
        lb = ETH_ROC_LOOKBACK
        n = len(dates)

        # Build ratio series
        ratios: List[Optional[float]] = []
        for i in range(n):
            eth = eth_closes[i] if i < len(eth_closes) else None
            btc = btc_closes[i]
            if eth is not None and btc > 0:
                ratios.append(eth / btc)
            else:
                ratios.append(None)

        series = []
        for t in range(lb, n):
            r_now = ratios[t]
            r_ago = ratios[t - lb]
            if r_now is None or r_ago is None or r_ago == 0:
                continue
            roc = (r_now / r_ago - 1) * 100
            series.append({
                "date": dates[t],
                "roc": round(roc, 4),
            })
        return series

    # ------------------------------------------------------------------
    # Signal derivation
    # ------------------------------------------------------------------

    @staticmethod
    def _get_bm_signal(bm: float) -> str:
        if bm >= BM_ENTRY_THRESHOLD:
            return "ENTRY"
        if bm <= BM_EXIT_THRESHOLD:
            return "EXIT"
        if bm > 0:
            return "RISING"
        if bm < 0:
            return "FALLING"
        return "NEUTRAL"

    @staticmethod
    def _get_eth_roc_signal(roc: float) -> str:
        if roc > 3:
            return "STRONG"
        if roc > ETH_ROC_WARN:
            return "POSITIVE"
        if roc > ETH_ROC_BEAR:
            return "WARNING"
        return "BEARISH"

    @staticmethod
    def _get_combined_state(bm: float, eth_roc: float) -> str:
        """Derive combined state per spec section 0.4."""
        if bm > BM_ENTRY_THRESHOLD and eth_roc > 0:
            return "ENTRY"
        if bm > 0 and eth_roc <= ETH_ROC_WARN:
            return "PEAK_WARNING"
        if bm <= BM_EXIT_THRESHOLD:
            return "EXIT"
        if bm > 0:
            return "RISING"
        return "NEUTRAL"

    # ------------------------------------------------------------------
    # Main calculation
    # ------------------------------------------------------------------

    def calculate(self, price_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Run the full ABM calculation pipeline.

        Args:
            price_data: coin → list of {date, close} dicts (oldest first).
                        Must include "BTC" and "ETH" keys.

        Returns:
            Dict with bm_series, eth_roc_series, current values, signals, etc.
        """
        if "BTC" not in price_data:
            return {"error": "BTC data missing"}

        dates, btc_closes, alt_closes = self._align_by_date(price_data)

        if len(dates) < BREADTH_LOOKBACK + BM_LOOKBACK:
            return {"error": f"Not enough data ({len(dates)} days, need {BREADTH_LOOKBACK + BM_LOOKBACK})"}

        # --- Breadth ---
        breadth_series = self._compute_breadth_series(dates, btc_closes, alt_closes)
        if not breadth_series:
            return {"error": "Could not compute breadth series"}

        # --- BM ---
        bm_series = self._compute_bm_series(breadth_series)
        if not bm_series:
            return {"error": "Could not compute BM series"}

        bm_current = bm_series[-1]["bm"]

        # --- ETH/BTC ROC ---
        eth_closes = alt_closes.get("ETH", [])
        eth_roc_series = self._compute_eth_roc_series(dates, btc_closes, eth_closes)
        eth_roc_current = eth_roc_series[-1]["roc"] if eth_roc_series else 0.0

        # --- Latest breadth snapshot ---
        latest_breadth = breadth_series[-1]

        # --- BTC gate ---
        btc_ret_30d = 0.0
        if len(btc_closes) > BREADTH_LOOKBACK:
            btc_now = btc_closes[-1]
            btc_ago = btc_closes[-1 - BREADTH_LOOKBACK]
            if btc_ago > 0:
                btc_ret_30d = (btc_now / btc_ago - 1) * 100
        btc_gate = "PASS" if btc_ret_30d > 0 else "FAIL"

        # --- Signals ---
        bm_signal = self._get_bm_signal(bm_current)
        eth_roc_signal = self._get_eth_roc_signal(eth_roc_current)
        combined_state = self._get_combined_state(bm_current, eth_roc_current)

        return {
            "bm_series": bm_series,
            "bm_current": bm_current,
            "eth_roc_series": eth_roc_series,
            "eth_roc_current": round(eth_roc_current, 4),
            "breadth_30d": latest_breadth["breadth"],
            "valid_count": latest_breadth["valid_count"],
            "outperform_count": latest_breadth["outperform_count"],
            "btc_gate": btc_gate,
            "btc_return_30d": round(btc_ret_30d, 2),
            "bm_signal": bm_signal,
            "eth_roc_signal": eth_roc_signal,
            "combined_state": combined_state,
        }
