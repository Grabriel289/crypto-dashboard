"""Macro data API routes."""
from fastapi import APIRouter
from typing import Dict, Any

from scoring.macro_tide import macro_tide_scorer

router = APIRouter()


@router.get("/macro")
async def get_macro() -> Dict[str, Any]:
    """Get macro tide data."""
    return await macro_tide_scorer.calculate_full_score()


@router.get("/macro/b1")
async def get_b1_score() -> Dict[str, Any]:
    """Get B1 raw score only."""
    full = await macro_tide_scorer.calculate_full_score()
    return {
        "b1_raw_score": full.get("b1_raw_score"),
        "adjusted_score": full.get("adjusted_score"),
        "regime": full.get("regime")
    }


@router.get("/macro/leaks")
async def get_liquidity_leaks() -> Dict[str, Any]:
    """Get liquidity leak monitor data."""
    full = await macro_tide_scorer.calculate_full_score()
    return {
        "leak_penalty": full.get("leak_penalty"),
        "leak_details": full.get("leak_details")
    }
