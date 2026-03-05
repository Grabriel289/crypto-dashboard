"""Action items generator."""
from typing import Dict, Any, List


def generate_action_items(
    macro_score: float,
    macro_regime: str,
    fear_greed: int,
    fragility_composite: int,
    funding_signals: Dict[str, Dict],
    whale_signal: str,
    sector_verdict: Dict[str, Any],
    sectors: List[Dict] = None,
    abm_data: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """Generate prioritized action items based on all inputs."""
    actions = []

    # Get funding bias
    funding_aggregate = funding_signals.get("aggregate", {})
    funding_bias = funding_aggregate.get("bias", "neutral")

    # Get ABM signals
    abm = abm_data or {}
    abm_combined = abm.get("combined_state", "NEUTRAL")
    breadth_90d = abm.get("breadth_90d_current", 0)
    breadth_90d_signal = abm.get("breadth_90d_signal", "LOW")
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 1: Extreme Fear = Potential Bottom
    # ═══════════════════════════════════════════════════════════════
    if fear_greed <= 10:
        actions.append({
            "priority": "HIGH",
            "emoji": "🔴",
            "action": "Do NOT panic sell",
            "reason": f"Fear & Greed at {fear_greed} = 70% probability of local bottom",
            "condition": "Always"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 2: Accumulation Zone
    # ═══════════════════════════════════════════════════════════════
    btc_funding = funding_signals.get("BTC", {})
    if fear_greed <= 15 and btc_funding.get("bias") == "bullish":
        if macro_score >= 2.5:
            actions.append({
                "priority": "HIGH",
                "emoji": "🔴",
                "action": "Selective accumulation of BTC",
                "reason": "Extreme fear + negative funding + acceptable macro",
                "condition": "Entry zone: current price ± 3%"
            })
        else:
            actions.append({
                "priority": "MEDIUM",
                "emoji": "🟡",
                "action": "Prepare for accumulation",
                "reason": "Fear + squeeze setup BUT macro weak",
                "condition": "Wait for Macro ≥ 3.0"
            })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 3: Conflicting Signals Warning
    # ═══════════════════════════════════════════════════════════════
    if fear_greed <= 20 and "DISTRIBUTION" in whale_signal:
        actions.append({
            "priority": "HIGH",
            "emoji": "🔴",
            "action": "Caution - conflicting signals",
            "reason": "Extreme fear (bullish) but whale distribution (bearish)",
            "condition": "Wait for confirmation before heavy accumulation"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 4: Sector Rotation Actions
    # ═══════════════════════════════════════════════════════════════
    verdict = sector_verdict.get("verdict", "")
    if "ROTATE TO" in verdict:
        sector = verdict.replace("🟢 ROTATE TO ", "")
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": f"Consider rotation to {sector}",
            "reason": sector_verdict.get("reason", ""),
            "condition": "Scale in gradually; 5-10% per day"
        })
    
    if verdict.startswith("❌"):
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": "Avoid altcoin rotation",
            "reason": "No sector outperforming BTC consistently",
            "condition": "Stay in BTC or stables"
        })
    
    # Check for outperforming sectors
    if sectors:
        best_sectors = [s for s in sectors if s.get("avg_vs_btc_14d", 0) > 5]
        for sector in best_sectors[:2]:  # Top 2 sectors
            sector_name = sector.get("sector", "")
            vs_btc = sector.get("avg_vs_btc_14d", 0)
            top_coin = sector.get("top_performer", "")
            
            if macro_score >= 3.5:
                actions.append({
                    "priority": "MEDIUM",
                    "emoji": "🟡",
                    "action": f"Watch {sector_name} sector rotation",
                    "reason": f"{sector_name} up {vs_btc:+.2f}% vs BTC with supportive macro",
                    "condition": f"Consider {top_coin} on dips"
                })
            else:
                actions.append({
                    "priority": "LOW",
                    "emoji": "⚪",
                    "action": f"Monitor {sector_name} sector",
                    "reason": f"Strong momentum ({vs_btc:+.2f}% vs BTC) but macro unfavorable",
                    "condition": "Wait for macro improvement"
                })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 5: Risk Management
    # ═══════════════════════════════════════════════════════════════
    if fragility_composite >= 60:
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": "Reduce leverage",
            "reason": f"Market fragility elevated ({fragility_composite}/100)",
            "condition": "Max 2x leverage until fragility drops below 50"
        })
    
    if whale_signal == "DISTRIBUTION / NET SHORT":
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": "Tighten stop losses",
            "reason": "Whale distribution detected - smart money selling",
            "condition": "Trail stops at -5% to -7%"
        })
    elif whale_signal == "ACCUMULATION / NET LONG":
        actions.append({
            "priority": "LOW",
            "emoji": "⚪",
            "action": "Consider adding to positions",
            "reason": "Whale accumulation detected - smart money buying",
            "condition": "Scale in on 2-3% dips"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 6: Macro-driven Actions
    # ═══════════════════════════════════════════════════════════════
    if macro_score < 2.5:
        actions.append({
            "priority": "HIGH",
            "emoji": "🔴",
            "action": "Defensive allocation",
            "reason": f"Macro score {macro_score}/7 = Risk-Off environment",
            "condition": "Increase stables to 30%+, reduce alt exposure"
        })
    elif macro_score >= 5.5:
        actions.append({
            "priority": "LOW",
            "emoji": "⚪",
            "action": "Aggressive allocation OK",
            "reason": f"Macro score {macro_score}/7 = Risk-On environment",
            "condition": "Can increase alt exposure to 40-50%"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 7: Funding-based Actions
    # ═══════════════════════════════════════════════════════════════
    if funding_bias == "bullish":
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": "Squeeze setup active",
            "reason": "Negative funding rates - shorts paying longs",
            "condition": "Watch for short squeeze opportunities"
        })
    elif funding_bias == "bearish":
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": "Avoid high leverage longs",
            "reason": "Overleveraged longs - potential for long squeeze",
            "condition": "Use max 3x leverage"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 8: Altcoin Season Index Actions
    # ═══════════════════════════════════════════════════════════════
    if abm_combined == "ENTRY":
        actions.append({
            "priority": "HIGH",
            "emoji": "🔴",
            "action": "Alt season entry - rotate into alts",
            "reason": f"Breadth momentum crossed up, 90D breadth {breadth_90d:.0f}%",
            "condition": "Focus on sectors outperforming BTC"
        })
    elif abm_combined == "PEAK_WARNING":
        actions.append({
            "priority": "HIGH",
            "emoji": "🔴",
            "action": "Alt season peak - take profits on alts",
            "reason": f"90D breadth at {breadth_90d:.0f}% (>70% = overheated)",
            "condition": "Scale out of alts, rotate to BTC/stables"
        })
    elif abm_combined == "EXIT":
        actions.append({
            "priority": "HIGH",
            "emoji": "🔴",
            "action": "Alt season exit - reduce alt exposure",
            "reason": "Breadth momentum crossed down - alt season ending",
            "condition": "Move to BTC or stables"
        })

    if breadth_90d_signal == "PEAK" and abm_combined != "PEAK_WARNING":
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": "Monitor alt overheating",
            "reason": f"90D breadth elevated at {breadth_90d:.0f}%",
            "condition": "Prepare to take alt profits if BM turns negative"
        })

    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    actions.sort(key=lambda x: priority_order.get(x["priority"], 2))

    return actions[:8]  # Return top 8 actions
