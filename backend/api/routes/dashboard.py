"""Main dashboard API routes."""
from fastapi import APIRouter
from typing import Dict, Any, List
import asyncio
from datetime import datetime

from scoring.macro_tide import macro_tide_scorer
from scoring.momentum import calculate_momentum_from_prices, calculate_momentum_score, MomentumMetrics
from scoring.fragility import calculate_fragility
from scoring.funding import interpret_funding, aggregate_funding_signals
from scoring.whale import WhaleActivity
from scoring.sector_rotation import calculate_sector_momentum, generate_sector_verdict
from analysis.action_generator import generate_action_items
from analysis.conflict_detector import detect_conflicting_signals
from analysis.final_verdict import generate_final_verdict
from data.fetchers.fear_greed import fear_greed_fetcher
from data.fetchers.binance import binance_fetcher
from data.fetchers.cdc_levels import cdc_fetcher
from data.fetchers.liquidation import liquidation_fetcher
from data.fetchers.stablecoin import stablecoin_fetcher
from data.fetchers.economic_calendar import calendar_fetcher
from data.fetchers.correlation import correlation_fetcher
from data.fetchers.derivative_sentiment import derivative_sentiment_fetcher
from data.aggregator import data_aggregator
from config.sectors import SECTORS

router = APIRouter()


@router.get("/macro")
async def get_macro_data() -> Dict[str, Any]:
    """Get macro tide data."""
    return await macro_tide_scorer.calculate_full_score()


@router.get("/market-prices")
async def get_market_prices() -> Dict[str, Any]:
    """Get live market prices for BTC, ETH, SOL."""
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


@router.get("/crypto-pulse")
async def get_crypto_pulse() -> Dict[str, Any]:
    """Get crypto pulse data (Fear & Greed, Fragility, Funding, Derivative Sentiment)."""
    # Fetch Fear & Greed
    fear_greed = await fear_greed_fetcher.fetch()
    
    # Fetch funding rates for BTC, ETH, SOL
    funding_data = {}
    for coin in ["BTC", "ETH", "SOL"]:
        funding = await data_aggregator.fetch_funding_rate(coin)
        if funding:
            funding_data[coin] = interpret_funding(funding["funding_rate"])
            funding_data[coin]["rate"] = funding["funding_rate"]
    
    funding_aggregate = aggregate_funding_signals(funding_data)
    
    # Calculate fragility (simplified)
    fragility = calculate_fragility(
        vol_percentile=45,
        drawdown_pct=-15,
        funding_rate=funding_data.get("BTC", {}).get("rate", 0),
        exchange_flow_pct=0
    )
    
    # Fetch Derivative Sentiment (real data from Binance Futures)
    derivative_sentiment = await derivative_sentiment_fetcher.get_sentiment()
    
    return {
        "fear_greed": fear_greed,
        "fragility": fragility,
        "funding": {
            "rates": funding_data,
            "aggregate": funding_aggregate
        },
        "derivative_sentiment": derivative_sentiment,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/sectors")
async def get_sector_data() -> Dict[str, Any]:
    """Get sector rotation data with top 3 coins per sector."""
    # Fetch prices for all coins
    all_coins = []
    for sector_coins in SECTORS.values():
        all_coins.extend(sector_coins["coins"])
    all_coins = list(set(all_coins))
    
    # Fetch prices with fallback
    prices_result = await data_aggregator.fetch_multiple_prices(all_coins)
    prices = prices_result.get("prices", {})
    
    # For each sector, calculate momentum and top 3 coins
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
                # Use 24h change as proxy for 7d (in production, fetch klines)
                change_24h = price_info.get("change_24h", 0)
                change_7d = change_24h * 7  # Rough approximation
                vs_btc = change_7d - btc_change_7d
                
                # Simple momentum score
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
        
        # Always include sector even if no data (for PERP and others)
        sector_data.append({
            "sector": sector_name,
            "momentum_score": int(sum(scores) / len(scores)) if scores else 0,
            "avg_return_7d": round(sum(returns_7d) / len(returns_7d), 2) if returns_7d else 0,
            "avg_vs_btc_7d": round(sum(returns_vs_btc) / len(returns_vs_btc), 2) if returns_vs_btc else 0,
            "coin_count": len(scores),
            "top_performer": top_3_coins[0]["symbol"] if top_3_coins else None,
            "top_3_coins": top_3_coins,
            "description": sector_info["description"],
            "has_data": len(scores) > 0
        })
    
    # Get BTC momentum
    btc_momentum = next((s["momentum_score"] for s in sector_data if s["sector"] == "L1"), 50)
    
    # Get macro score
    macro = await macro_tide_scorer.calculate_full_score()
    macro_score = macro.get("adjusted_score", 2.5)
    
    # Generate verdict
    verdict = generate_sector_verdict(sector_data, btc_momentum, macro_score)
    
    return {
        "sectors": sector_data,
        "verdict": verdict,
        "btc_momentum": btc_momentum,
        "macro_score": macro_score,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/actions")
async def get_action_items() -> Dict[str, Any]:
    """Get prioritized action items."""
    # Fetch all data
    macro = await macro_tide_scorer.calculate_full_score()
    pulse = await get_crypto_pulse()
    sectors = await get_sector_data()
    
    actions = generate_action_items(
        macro_score=macro.get("adjusted_score", 2.5),
        macro_regime=macro.get("regime", ""),
        fear_greed=pulse.get("fear_greed", {}).get("value", 50),
        fragility_composite=pulse.get("fragility", {}).get("score", 50),
        funding_signals=pulse.get("funding", {}).get("rates", {}),
        whale_signal=pulse.get("whale", {}).get("signal", "NEUTRAL"),
        sector_verdict=sectors.get("verdict", {}),
        sectors=sectors.get("sectors", [])
    )
    
    # Detect conflicting signals
    conflicts = detect_conflicting_signals(
        macro_score=macro.get("adjusted_score", 2.5),
        fear_greed=pulse.get("fear_greed", {}).get("value", 50),
        fear_greed_signal=pulse.get("fear_greed", {}).get("signal", ""),
        whale_signal=pulse.get("whale", {}).get("signal", "NEUTRAL"),
        whale_bias=pulse.get("whale", {}).get("bias", "neutral"),
        funding_bias=pulse.get("funding", {}).get("aggregate", {}).get("bias", "neutral"),
        fragility_score=pulse.get("fragility", {}).get("score", 50),
        sector_verdict=sectors.get("verdict", {}).get("verdict", "")
    )
    
    # Generate final verdict
    final_verdict = generate_final_verdict({
        "macro": macro,
        "key_levels": key_levels,
        "crypto_pulse": pulse,
        "sectors": sectors,
        "calendar": calendar
    })
    
    return {
        "actions": actions,
        "conflicts": conflicts,
        "summary": {
            "macro_regime": macro.get("regime", ""),
            "fear_greed": pulse.get("fear_greed", {}).get("label", ""),
            "sector_verdict": sectors.get("verdict", {}).get("verdict", "")
        },
        "timestamp": datetime.now().isoformat()
    }


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


@router.get("/full")
async def get_full_dashboard() -> Dict[str, Any]:
    """Get complete dashboard data including new indicators."""
    # Fetch all data concurrently
    macro, prices, pulse, sectors, key_levels, liquidation, stablecoin, calendar, correlation = await asyncio.gather(
        macro_tide_scorer.calculate_full_score(),
        get_market_prices(),
        get_crypto_pulse(),
        get_sector_data(),
        get_key_levels(),
        get_liquidation_heatmap(),
        get_stablecoin_flow(),
        get_economic_calendar(),
        get_correlation_matrix()
    )
    
    # Generate actions
    actions = generate_action_items(
        macro_score=macro.get("adjusted_score", 2.5),
        macro_regime=macro.get("regime", ""),
        fear_greed=pulse.get("fear_greed", {}).get("value", 50),
        fragility_composite=pulse.get("fragility", {}).get("score", 50),
        funding_signals=pulse.get("funding", {}).get("rates", {}),
        whale_signal=pulse.get("whale", {}).get("signal", "NEUTRAL"),
        sector_verdict=sectors.get("verdict", {}),
        sectors=sectors.get("sectors", [])
    )
    
    # Detect conflicting signals
    conflicts = detect_conflicting_signals(
        macro_score=macro.get("adjusted_score", 2.5),
        fear_greed=pulse.get("fear_greed", {}).get("value", 50),
        fear_greed_signal=pulse.get("fear_greed", {}).get("signal", ""),
        whale_signal=pulse.get("whale", {}).get("signal", "NEUTRAL"),
        whale_bias=pulse.get("whale", {}).get("bias", "neutral"),
        funding_bias=pulse.get("funding", {}).get("aggregate", {}).get("bias", "neutral"),
        fragility_score=pulse.get("fragility", {}).get("score", 50),
        sector_verdict=sectors.get("verdict", {}).get("verdict", "")
    )
    
    # Generate final verdict
    final_verdict = generate_final_verdict({
        "macro": macro,
        "key_levels": key_levels,
        "crypto_pulse": pulse,
        "sectors": sectors,
        "calendar": calendar
    })
    
    return {
        "macro": macro,
        "market_prices": prices,
        "crypto_pulse": pulse,
        "sectors": sectors,
        "actions": actions,
        "conflicts": conflicts,
        "key_levels": key_levels,
        "liquidation": liquidation,
        "stablecoin": stablecoin,
        "calendar": calendar,
        "correlation": correlation,
        "final_verdict": final_verdict,
        "last_updated": datetime.now().isoformat()
    }
