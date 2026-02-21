"""Crypto data API routes."""
from fastapi import APIRouter
from typing import Dict, Any, List

from data.fetchers.fear_greed import fear_greed_fetcher
from data.aggregator import data_aggregator
from scoring.fragility import calculate_fragility
from scoring.funding import interpret_funding
from scoring.whale import WhaleActivity

router = APIRouter()


@router.get("/fear-greed")
async def get_fear_greed() -> Dict[str, Any]:
    """Get Fear & Greed index."""
    return await fear_greed_fetcher.fetch()


@router.get("/funding")
async def get_funding_rates(coins: str = "BTC,ETH,SOL") -> Dict[str, Any]:
    """Get funding rates for specified coins."""
    coin_list = [c.strip() for c in coins.split(",")]
    funding_data = {}
    
    for coin in coin_list:
        funding = await data_aggregator.fetch_funding_rate(coin)
        if funding:
            funding_data[coin] = {
                **funding,
                "interpretation": interpret_funding(funding["funding_rate"])
            }
    
    return {
        "funding_rates": funding_data,
        "count": len(funding_data)
    }


@router.get("/fragility")
async def get_fragility() -> Dict[str, Any]:
    """Get market fragility score."""
    # Simplified fragility calculation
    return calculate_fragility(
        vol_percentile=45,
        drawdown_pct=-15,
        funding_rate=0.01,
        exchange_flow_pct=0
    )


@router.get("/whale")
async def get_whale_activity() -> Dict[str, Any]:
    """Get whale activity data."""
    whale = WhaleActivity(total_oi_usd=5.5e9, oi_change_24h_pct=-3.2, exchange_inflow_pct=15)
    signal = whale.get_positioning_signal()
    
    return {
        "total_oi_usd": whale.total_oi_usd,
        "oi_change_24h_pct": whale.oi_change_24h_pct,
        "exchange_inflow_pct": whale.exchange_inflow_pct,
        **signal
    }


@router.get("/prices")
async def get_prices(coins: str = "BTC,ETH,SOL") -> Dict[str, Any]:
    """Get current prices for specified coins."""
    coin_list = [c.strip() for c in coins.split(",")]
    return await data_aggregator.fetch_multiple_prices(coin_list)
