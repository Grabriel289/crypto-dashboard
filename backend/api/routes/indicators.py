"""New indicator API routes for 5 additional sections."""
from fastapi import APIRouter
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio

from data.fetchers.cdc_levels import cdc_fetcher
from data.fetchers.liquidation import liquidation_fetcher
from data.fetchers.stablecoin import stablecoin_fetcher
from data.fetchers.economic_calendar import calendar_fetcher
from data.fetchers.correlation import correlation_fetcher

router = APIRouter()


@router.get("/key-levels")
async def get_key_levels() -> Dict[str, Any]:
    """Get Key Levels & CDC Signal for BTC and ETH."""
    btc_data = await cdc_fetcher.get_cdc_data("BTCUSDT")
    eth_data = await cdc_fetcher.get_cdc_data("ETHUSDT")
    
    return {
        "btc": btc_data,
        "eth": eth_data,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/liquidation-heatmap")
async def get_liquidation_heatmap() -> Dict[str, Any]:
    """Get BTC Liquidation Heatmap."""
    heatmap = await liquidation_fetcher.get_heatmap()
    
    return {
        "heatmap": heatmap,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/stablecoin-flow")
async def get_stablecoin_flow() -> Dict[str, Any]:
    """Get Stablecoin Flow Monitor data."""
    data = await stablecoin_fetcher.get_flow_data()
    
    return {
        **data,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/economic-calendar")
async def get_economic_calendar() -> Dict[str, Any]:
    """Get Economic Calendar (next 7 days)."""
    data = await calendar_fetcher.get_calendar()
    
    return {
        **data,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/correlation-matrix")
async def get_correlation_matrix() -> Dict[str, Any]:
    """Get Correlation Matrix & PAXG/BTC data."""
    correlations = await correlation_fetcher.get_correlations()
    paxg_btc = await correlation_fetcher.get_paxg_btc()
    
    return {
        "correlations": correlations,
        "paxg_btc": paxg_btc,
        "timestamp": datetime.now().isoformat()
    }
