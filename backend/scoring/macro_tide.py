"""Macro Tide scoring (B1 + Leak Monitor)."""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from data.fetchers.fred import fred_fetcher
from data.fetchers.yahoo_finance import yahoo_finance_fetcher


@dataclass
class MacroIndicators:
    """Raw macro indicator data."""
    nfci: Optional[Dict] = None
    hy_spread: Optional[Dict] = None
    move_index: Optional[Dict] = None  # Will need Yahoo Finance
    cu_au_ratio: Optional[Dict] = None  # Will need Yahoo Finance
    net_liquidity: Optional[Dict] = None
    fed_funds: Optional[Dict] = None
    treasury_10y: Optional[Dict] = None


class MacroTideScorer:
    """Calculate B1 score and leak penalties."""
    
    async def fetch_all_indicators(self) -> MacroIndicators:
        """Fetch all macro indicators."""
        indicators = MacroIndicators()
        
        # Fetch from FRED
        indicators.nfci = await fred_fetcher.fetch_nfci()
        indicators.hy_spread = await fred_fetcher.fetch_hy_spread()
        indicators.net_liquidity = await fred_fetcher.calculate_net_liquidity()
        indicators.fed_funds = await fred_fetcher.fetch_fed_funds()
        indicators.treasury_10y = await fred_fetcher.fetch_treasury_10y()
        
        # Fetch MOVE index and Cu/Au ratio from Yahoo Finance (real-time)
        indicators.move_index = await yahoo_finance_fetcher.fetch_move_index()
        indicators.cu_au_ratio = await yahoo_finance_fetcher.fetch_cu_au_ratio()
        
        return indicators
    
    def calculate_b1_score(self, indicators: MacroIndicators) -> Dict[str, Any]:
        """Calculate raw B1 score."""
        scores = {
            "NFCI": indicators.nfci.get("score", 0) if indicators.nfci else 0,
            "HY_Spread": indicators.hy_spread.get("score", 0) if indicators.hy_spread else 0,
            "MOVE": indicators.move_index.get("score", 0.5) if indicators.move_index else 0.5,
            "CuAu_Ratio": indicators.cu_au_ratio.get("score", 0.5) if indicators.cu_au_ratio else 0.5,
            "Net_Liquidity": indicators.net_liquidity.get("score", 0.5) if indicators.net_liquidity else 0.5,
        }
        
        raw_score = sum(scores.values())
        
        return {
            "raw_score": round(raw_score, 1),
            "max_score": 5.0,
            "components": scores,
            "details": {
                "NFCI": {
                    "value": indicators.nfci.get("value") if indicators.nfci else None,
                    "status": indicators.nfci.get("status", "⚪") if indicators.nfci else "⚪"
                },
                "HY_Spread": {
                    "value": indicators.hy_spread.get("value_pct") if indicators.hy_spread else None,
                    "status": indicators.hy_spread.get("status", "⚪") if indicators.hy_spread else "⚪"
                },
                "MOVE": {
                    "value": indicators.move_index.get("value") if indicators.move_index else None,
                    "status": indicators.move_index.get("status", "⚪") if indicators.move_index else "⚪"
                },
                "CuAu_Ratio": {
                    "value": indicators.cu_au_ratio.get("value") if indicators.cu_au_ratio else None,
                    "status": indicators.cu_au_ratio.get("status", "⚪") if indicators.cu_au_ratio else "⚪"
                },
                "Net_Liquidity": {
                    "value": f"${indicators.net_liquidity.get('value_trillion', 0)}T" if indicators.net_liquidity else None,
                    "status": indicators.net_liquidity.get("status", "⚪") if indicators.net_liquidity else "⚪"
                }
            }
        }
    
    def check_liquidity_leaks(self, indicators: MacroIndicators) -> Dict[str, Any]:
        """Check for liquidity leak conditions."""
        leaks = {
            "fiscal_dominance": {"active": False, "penalty": 0.0, "detail": ""},
            "gold_cannibalization": {"active": False, "penalty": 0.0, "detail": ""},
            "policy_lag": {"active": False, "penalty": 0.0, "detail": ""}
        }
        
        # Check Fiscal Dominance: 10Y - Fed Funds > 25bp
        if indicators.treasury_10y and indicators.fed_funds:
            spread = indicators.treasury_10y.get("value", 0) - indicators.fed_funds.get("value", 0)
            if spread > 0.25:
                leaks["fiscal_dominance"] = {
                    "active": True,
                    "penalty": -0.5,
                    "detail": f"+{spread:.0f}bp gap",
                    "status": "[RED] ACTIVE"
                }
            else:
                leaks["fiscal_dominance"]["status"] = "🟢 OK"
        
        # Gold Cannibalization - simplified (would need BTC ETF flow data)
        leaks["gold_cannibalization"]["status"] = "🟢 OK"
        leaks["gold_cannibalization"]["detail"] = "Monitoring BTC ETF flows"
        
        # Policy Lag - simplified
        leaks["policy_lag"]["status"] = "🟡 PARTIAL"
        leaks["policy_lag"]["detail"] = "Seized only / CLARITY Act pending"
        
        total_penalty = sum(l["penalty"] for l in leaks.values())
        
        return {
            "leaks": leaks,
            "total_penalty": total_penalty
        }
    
    def classify_regime(self, adjusted_score: float) -> Dict[str, str]:
        """Classify market regime based on adjusted score."""
        if adjusted_score >= 4.0:
            return {
                "regime": "[GREEN] HIGH TIDE / RISK-ON",
                "stance": "Aggressive",
                "emoji": "🟢"
            }
        elif adjusted_score >= 3.0:
            return {
                "regime": "[YELLOW] NEUTRAL",
                "stance": "Balanced",
                "emoji": "🟡"
            }
        elif adjusted_score >= 2.0:
            return {
                "regime": "[ORANGE] CAUTION / BLOCKED FLOW",
                "stance": "Defensive",
                "emoji": "🟠"
            }
        else:
            return {
                "regime": "[RED] LOW TIDE / RISK-OFF",
                "stance": "Defensive",
                "emoji": "🔴"
            }
    
    async def calculate_full_score(self) -> Dict[str, Any]:
        """Calculate complete macro tide score."""
        indicators = await self.fetch_all_indicators()
        
        b1 = self.calculate_b1_score(indicators)
        leaks = self.check_liquidity_leaks(indicators)
        
        adjusted_score = max(0, b1["raw_score"] + leaks["total_penalty"])
        regime = self.classify_regime(adjusted_score)
        
        return {
            "b1_raw_score": b1["raw_score"],
            "b1_max_score": b1["max_score"],
            "b1_components": b1["components"],
            "b1_details": b1["details"],
            "leak_penalty": leaks["total_penalty"],
            "leak_details": leaks["leaks"],
            "adjusted_score": round(adjusted_score, 1),
            "max_adjusted_score": 5.0,
            "regime": regime["regime"],
            "stance": regime["stance"],
            "regime_emoji": regime["emoji"]
        }


# Singleton instance
macro_tide_scorer = MacroTideScorer()
