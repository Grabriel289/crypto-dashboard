"""Live market prices API routes."""
from fastapi import APIRouter
from typing import Dict, Any, List
from datetime import datetime

from data.aggregator import data_aggregator

router = APIRouter()


@router.get("/market-prices")
async def get_market_prices() -> Dict[str, Any]:
    """Get live market prices for BTC, ETH, SOL with 24h stats."""
    coins = ["BTC", "ETH", "SOL"]
    result = await data_aggregator.fetch_multiple_prices(coins)
    
    prices = {}
    for coin in coins:
        if coin in result.get("prices", {}):
            data = result["prices"][coin]
            prices[coin] = {
                "symbol": coin,
                "price": data.get("price", 0),
                "change_24h": data.get("change_24h", 0),
                "volume_24h": data.get("volume_24h", 0),
                "high_24h": data.get("high_24h", 0),
                "low_24h": data.get("low_24h", 0),
                "source": data.get("source", "unknown")
            }
    
    return {
        "prices": prices,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/market-prices/{coin}")
async def get_coin_price(coin: str) -> Dict[str, Any]:
    """Get live price for a specific coin."""
    result = await data_aggregator.fetch_price_with_fallback(coin.upper())
    
    if not result:
        return {"error": f"Price data not available for {coin}"}
    
    return {
        "symbol": coin.upper(),
        "price": result.get("price", 0),
        "change_24h": result.get("change_24h", 0),
        "volume_24h": result.get("volume_24h", 0),
        "high_24h": result.get("high_24h", 0),
        "low_24h": result.get("low_24h", 0),
        "source": result.get("source", "unknown"),
        "timestamp": datetime.now().isoformat()
    }
