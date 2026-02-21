"""Sector data API routes."""
from fastapi import APIRouter
from typing import Dict, Any, List

from config.sectors import SECTORS
from data.aggregator import data_aggregator
from scoring.momentum import calculate_momentum_from_prices
from scoring.sector_rotation import calculate_sector_momentum, generate_sector_verdict
from scoring.macro_tide import macro_tide_scorer

router = APIRouter()


@router.get("/sectors")
async def get_sectors() -> Dict[str, Any]:
    """Get all sector data with momentum scores and top coins."""
    # Fetch prices for all coins
    all_coins = []
    for sector_coins in SECTORS.values():
        all_coins.extend(sector_coins["coins"])
    all_coins = list(set(all_coins))
    
    prices_result = await data_aggregator.fetch_multiple_prices(all_coins)
    prices = prices_result.get("prices", {})
    
    # Calculate sector data
    sector_data = []
    btc_price_data = prices.get("BTC", {})
    btc_change_7d = btc_price_data.get("change_24h", 0) * 7
    
    for sector_name, sector_info in SECTORS.items():
        sector_coins = sector_info["coins"]
        scores = []
        returns_7d = []
        returns_vs_btc = []
        coin_details = []
        
        for coin in sector_coins:
            if coin in prices:
                price_info = prices[coin]
                change_24h = price_info.get("change_24h", 0)
                change_7d = change_24h * 7
                vs_btc = change_7d - btc_change_7d
                
                score = 50 + (change_7d * 2)
                score = max(0, min(100, score))
                
                scores.append(score)
                returns_7d.append(change_7d)
                returns_vs_btc.append(vs_btc)
                
                coin_details.append({
                    "symbol": coin,
                    "return_7d": round(change_7d, 2),
                    "vs_btc": round(vs_btc, 2),
                    "price": price_info.get("price", 0),
                    "momentum_score": score
                })
        
        # Sort coins by 7d return to get top 3
        coin_details_sorted = sorted(coin_details, key=lambda x: x["return_7d"], reverse=True)
        top_3_coins = coin_details_sorted[:3]
        
        if scores:
            sector_data.append({
                "sector": sector_name,
                "momentum_score": int(sum(scores) / len(scores)),
                "avg_return_7d": round(sum(returns_7d) / len(returns_7d), 2),
                "avg_vs_btc_7d": round(sum(returns_vs_btc) / len(returns_vs_btc), 2),
                "coin_count": len(scores),
                "top_performer": top_3_coins[0]["symbol"] if top_3_coins else None,
                "top_3_coins": top_3_coins,
                "description": sector_info["description"]
            })
    
    # Get BTC momentum and macro score
    btc_momentum = next((s["momentum_score"] for s in sector_data if s["sector"] == "L1"), 50)
    macro = await macro_tide_scorer.calculate_full_score()
    macro_score = macro.get("adjusted_score", 2.5)
    
    # Generate verdict
    verdict = generate_sector_verdict(sector_data, btc_momentum, macro_score)
    
    return {
        "sectors": sector_data,
        "verdict": verdict,
        "btc_momentum": btc_momentum,
        "macro_score": macro_score
    }


@router.get("/sectors/{sector_name}")
async def get_sector_detail(sector_name: str) -> Dict[str, Any]:
    """Get detailed data for a specific sector."""
    if sector_name.upper() not in SECTORS:
        return {"error": f"Sector {sector_name} not found"}
    
    sector_key = sector_name.upper()
    sector_info = SECTORS[sector_key]
    
    # Fetch prices for sector coins
    prices_result = await data_aggregator.fetch_multiple_prices(sector_info["coins"])
    
    return {
        "sector": sector_key,
        "description": sector_info["description"],
        "coins": sector_info["coins"],
        "prices": prices_result
    }
