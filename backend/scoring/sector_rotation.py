"""Sector rotation analysis module."""
from typing import Dict, Any, List
from config.sectors import SECTORS
from scoring.momentum import MomentumMetrics, calculate_momentum_score


def calculate_sector_momentum(sector_name: str, coin_data: Dict[str, MomentumMetrics]) -> Dict[str, Any]:
    """Calculate sector-level momentum from individual coins."""
    coins = SECTORS[sector_name]["coins"]
    scores = []
    returns_7d = []
    returns_vs_btc = []
    
    for coin in coins:
        if coin in coin_data:
            metrics = coin_data[coin]
            coin_score = calculate_momentum_score(metrics)
            scores.append(coin_score)
            returns_7d.append(metrics.return_7d)
            returns_vs_btc.append(metrics.return_7d_vs_btc)
    
    if not scores:
        return {"sector": sector_name, "error": "No data"}
    
    # Find top performer
    coin_scores = {coin: coin_data[coin] for coin in coins if coin in coin_data}
    top_performer = max(coin_scores.items(), key=lambda x: x[1].return_7d)[0] if coin_scores else None
    
    return {
        "sector": sector_name,
        "momentum_score": int(sum(scores) / len(scores)),
        "avg_return_7d": round(sum(returns_7d) / len(returns_7d), 2),
        "avg_vs_btc_7d": round(sum(returns_vs_btc) / len(returns_vs_btc), 2),
        "coin_count": len(scores),
        "top_performer": top_performer,
        "description": SECTORS[sector_name]["description"]
    }


def should_rotate_to_sector(
    sector_momentum: Dict[str, Any],
    btc_momentum_score: int,
    macro_adjusted_score: float
) -> Dict[str, Any]:
    """Determine if should rotate from BTC to sector."""
    sector_score = sector_momentum.get("momentum_score", 0)
    score_diff = sector_score - btc_momentum_score
    vs_btc_return = sector_momentum.get("avg_vs_btc_7d", 0)
    sector_name = sector_momentum.get("sector", "Unknown")
    
    # Rule 1: Macro Risk-Off = Stay defensive (BTC or stables)
    if macro_adjusted_score < 2.0:
        if score_diff > 15 and vs_btc_return > 5:
            return {
                "signal": "🟡 WATCH",
                "action": "Strong momentum but macro weak; wait for improvement",
                "rotate": False
            }
        else:
            return {
                "signal": "🔴 AVOID",
                "action": "Risk-off environment; stay in BTC or stables",
                "rotate": False
            }
    
    # Rule 2: Sector significantly outperforming BTC
    if score_diff > 10 and vs_btc_return > 5:
        if macro_adjusted_score >= 3.0:
            return {
                "signal": "🟢 ROTATE IN",
                "action": f"Strong momentum + supportive macro; consider {sector_momentum.get('top_performer', 'top coin')}",
                "rotate": True
            }
        else:
            return {
                "signal": "🟡 WATCH",
                "action": "Good momentum but macro not fully supportive; small position OK",
                "rotate": False
            }
    
    # Rule 3: Sector slightly outperforming
    if score_diff > 0 and vs_btc_return > 0:
        return {
            "signal": "🟡 NEUTRAL",
            "action": "Slight outperformance; not enough edge to rotate",
            "rotate": False
        }
    
    # Rule 4: Sector underperforming BTC
    if vs_btc_return < -5:
        return {
            "signal": "🔴 ROTATE OUT",
            "action": "Sector underperforming; exit positions",
            "rotate": False
        }
    
    return {
        "signal": "⚪ NEUTRAL",
        "action": "No clear signal; maintain current allocation",
        "rotate": False
    }


def generate_sector_verdict(
    all_sectors: List[Dict[str, Any]],
    btc_momentum: int,
    macro_score: float,
    btc_return_7d: float = 0
) -> Dict[str, Any]:
    """Generate overall sector rotation verdict based on actual vs BTC performance."""
    # Sort sectors by avg_vs_btc_7d (actual outperformance)
    sorted_sectors = sorted(all_sectors, key=lambda x: x.get("avg_vs_btc_7d", 0), reverse=True)
    
    # Count sectors with meaningful outperformance vs BTC (>5%)
    strongly_outperforming = [s for s in all_sectors if s.get("avg_vs_btc_7d", 0) > 5]
    moderately_outperforming = [s for s in all_sectors if s.get("avg_vs_btc_7d", 0) > 0]
    
    # Find best sector by vs BTC performance
    best_sector = max(all_sectors, key=lambda x: x.get("avg_vs_btc_7d", 0)) if all_sectors else None
    
    # No sectors outperforming BTC
    if len(moderately_outperforming) == 0:
        return {
            "verdict": "❌ STAY IN BTC",
            "reason": "No sector outperforming BTC",
            "recommended_allocation": {
                "BTC": "70-80%",
                "Stables": "20-30%"
            },
            "sorted_sectors": sorted_sectors
        }
    
    # Macro Risk-Off: Be defensive even if sectors look good
    if macro_score < 2.0:
        if best_sector and best_sector.get("avg_vs_btc_7d", 0) > 5:
            return {
                "verdict": "⚠️ DEFENSIVE MODE",
                "reason": f"{best_sector['sector']} outperforming BTC by {best_sector['avg_vs_btc_7d']:.1f}% but macro unfavorable",
                "recommended_allocation": {
                    "BTC": "50%",
                    "Stables": "40%",
                    best_sector["sector"]: "10% max"
                },
                "best_sector": best_sector,
                "sorted_sectors": sorted_sectors
            }
        else:
            return {
                "verdict": "⚠️ DEFENSIVE MODE",
                "reason": "Macro unfavorable; stay defensive",
                "recommended_allocation": {
                    "BTC": "50%",
                    "Stables": "50%"
                },
                "sorted_sectors": sorted_sectors
            }
    
    # Strong rotation signal: Best sector outperforming BTC by >5%
    if best_sector and best_sector.get("avg_vs_btc_7d", 0) > 5:
        return {
            "verdict": f"🟢 ROTATE TO {best_sector['sector'].upper()}",
            "reason": f"{best_sector['sector']} outperforming BTC by {best_sector['avg_vs_btc_7d']:.1f}% (7D)",
            "recommended_allocation": {
                "BTC": "40%",
                best_sector["sector"]: "30%",
                "Stables": "30%"
            },
            "best_sector": best_sector,
            "sorted_sectors": sorted_sectors
        }
    
    # Moderate rotation: Some sectors slightly outperforming
    if best_sector and best_sector.get("avg_vs_btc_7d", 0) > 0:
        return {
            "verdict": "🟡 SELECTIVE ROTATION",
            "reason": f"{best_sector['sector']} slightly outperforming BTC by {best_sector['avg_vs_btc_7d']:.1f}% (7D)",
            "recommended_allocation": {
                "BTC": "60%",
                best_sector["sector"]: "20%",
                "Stables": "20%"
            },
            "best_sector": best_sector,
            "sorted_sectors": sorted_sectors
        }
    
    # Default: Stay with BTC
    return {
        "verdict": "🟡 STAY IN BTC",
        "reason": "No clear sector advantage vs BTC",
        "recommended_allocation": {
            "BTC": "70%",
            "Stables": "30%"
        },
        "sorted_sectors": sorted_sectors
    }
