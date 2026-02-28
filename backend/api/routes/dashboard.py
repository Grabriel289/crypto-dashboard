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
from analysis.rrg import RRGEngine, RRGDataFetcher
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
    
    # Get fragility from scheduler cache (updated hourly to avoid rate limits)
    from data.scheduler import data_cache
    cached_fragility = data_cache.get('fragility')
    
    cache_is_live = (
        cached_fragility is not None and
        cached_fragility.get('source') == 'binance_live' and
        cached_fragility.get('fragility', {}).get('score') is not None
    )

    if cache_is_live:
        # Use cached live data (scheduler updates this hourly)
        fragility = cached_fragility.get('fragility', {})
        fragility['cached_at'] = data_cache.get_timestamp('fragility').isoformat() if data_cache.get_timestamp('fragility') else None
        fragility['note'] = 'Hourly cached data (rate limit protection)'
        print(f"[Fragility] Using cached live data: score={fragility.get('score')}")
    else:
        # Cache is empty or has fallback data (e.g. cold-start network issue) — fetch live now
        src = cached_fragility.get('source', 'none') if cached_fragility else 'none'
        print(f"[Fragility] Cache not live (source={src}), fetching live from Binance...")
        try:
            heatmap = await liquidation_fetcher.get_heatmap("BTCUSDT")
            if heatmap and heatmap.get('fragility', {}).get('score') is not None:
                fragility = heatmap.get('fragility', {})
                fragility['source'] = heatmap.get('source', 'unknown')
                fragility['note'] = 'Live fetch (scheduler cache not yet populated)'
                # Only warm the scheduler cache with confirmed live data
                if heatmap.get('source') == 'binance_live':
                    data_cache.set('fragility', heatmap)
                print(f"[Fragility] Live fetch: score={fragility.get('score')}, source={heatmap.get('source')}")
            else:
                raise ValueError("Heatmap returned no fragility score")
        except Exception as e:
            print(f"[Fragility] Live fetch failed ({e}), using legacy fallback")
            fragility = calculate_fragility(
                vol_percentile=45,
                drawdown_pct=-15,
                funding_rate=funding_data.get("BTC", {}).get("rate", 0),
                exchange_flow_pct=0
            )
            fragility["source"] = "legacy_fallback"
            fragility["note"] = "Live fetch failed; scheduler will retry hourly"
    
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
    """Get sector rotation data with real 7-day performance."""
    # Fetch prices for all coins
    all_coins = []
    for sector_coins in SECTORS.values():
        all_coins.extend(sector_coins["coins"])
    all_coins = list(set(all_coins))
    
    # Fetch prices (with KuCoin and CoinGecko fallbacks) and real 7-day returns concurrently
    prices_result, returns_7d_data = await asyncio.gather(
        data_aggregator.fetch_multiple_prices_with_fallbacks(all_coins),
        data_aggregator.fetch_multiple_7d_returns(all_coins)
    )
    prices = prices_result.get("prices", {})
    
    # Get BTC 7-day return for comparison
    btc_return_7d = returns_7d_data.get("BTC", 0)
    
    # For each sector, calculate momentum and top 3 coins
    sector_data = []
    
    for sector_name, sector_info in SECTORS.items():
        sector_coins = sector_info["coins"]
        scores = []
        returns_7d = []
        returns_vs_btc = []
        coin_details = []
        
        for coin in sector_coins:
            # Use real 7-day return if available, fallback to price data approximation
            change_7d = returns_7d_data.get(coin)
            
            if change_7d is None and coin in prices:
                # Fallback: use 24h change × 7 if 7d klines not available
                change_7d = prices[coin].get("change_24h", 0) * 7
            elif change_7d is None:
                continue  # Skip if no data at all
            
            price_info = prices.get(coin, {})
            vs_btc = change_7d - btc_return_7d
            
            # Simple momentum score (0-100)
            score = 50 + (change_7d * 2)
            score = max(0, min(100, score))
            
            scores.append(score)
            returns_7d.append(change_7d)
            returns_vs_btc.append(vs_btc)
            
            # Determine data source
            if coin in returns_7d_data:
                data_source = "7d_klines"
            elif price_info.get("source") == "kucoin":
                data_source = "kucoin"
            elif price_info.get("source") == "coingecko":
                data_source = "coingecko"
            else:
                data_source = "24h_approx"
            
            coin_details.append({
                "symbol": coin,
                "return_7d": round(change_7d, 2),
                "vs_btc": round(vs_btc, 2),
                "price": price_info.get("price", 0),
                "momentum_score": score,
                "data_source": data_source
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
    
    # Get BTC's actual momentum (not L1 sector average)
    btc_momentum = 50  # default
    l1_sector = next((s for s in sector_data if s["sector"] == "L1"), None)
    if l1_sector:
        # Find BTC specifically in L1 sector's top_3_coins or coin details
        btc_coin = next((c for c in l1_sector.get("top_3_coins", []) if c["symbol"] == "BTC"), None)
        if btc_coin:
            btc_momentum = btc_coin.get("momentum_score", 50)
        else:
            # Fallback: calculate from returns_7d_data
            btc_return = returns_7d_data.get("BTC", 0)
            btc_momentum = max(0, min(100, 50 + (btc_return * 2)))
    
    # Get macro score
    macro = await macro_tide_scorer.calculate_full_score()
    macro_score = macro.get("adjusted_score", 2.5)
    
    # Generate verdict (pass btc_return_7d for better comparison)
    verdict = generate_sector_verdict(sector_data, btc_momentum, macro_score, btc_return_7d)
    
    return {
        "sectors": sector_data,
        "verdict": verdict,
        "btc_momentum": btc_momentum,
        "macro_score": macro_score,
        "data_source": "Real 7-day klines from Binance",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/actions")
async def get_action_items() -> Dict[str, Any]:
    """Get prioritized action items."""
    # Fetch all data
    macro = await macro_tide_scorer.calculate_full_score()
    pulse = await get_crypto_pulse()
    sectors = await get_sector_data()
    key_levels = await get_key_levels()
    calendar = await get_economic_calendar()
    
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
        "final_verdict": final_verdict,
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
async def get_liquidation_heatmap(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    """
    Get Liquidation Heatmap with Fragility Score.
    Uses hourly cached data to avoid rate limits.
    
    Returns:
        - Market Fragility Score (Φ) = (L_d + F_σ + B_z) / 3
        - Estimated liquidation levels from OI + leverage
        - Realized liquidations (if WebSocket collector is running)
    """
    from data.scheduler import data_cache
    
    # Try to get cached fragility data first (updated hourly)
    cached = data_cache.get('fragility')
    
    if cached and cached.get('source') == 'binance_live':
        # Use hourly cached data
        heatmap = cached
        source = 'hourly_cached'
    else:
        # No fresh cache - try to fetch live (but this may hit rate limits)
        heatmap = await liquidation_fetcher.get_heatmap(symbol)
        source = heatmap.get('source', 'unknown')
    
    # Get realized liquidations from memory store
    from data.collectors.liquidation_ws import liquidation_store
    realized = liquidation_store.get_aggregated(symbol, hours=24)
    
    return {
        "symbol": symbol,
        "current_price": heatmap.get("current_price"),
        "source": source,
        "fragility": heatmap.get("fragility"),
        "estimated": heatmap.get("estimated_liquidations"),
        "realized_24h": realized,
        "major_zones": heatmap.get("major_zones"),
        "insight": heatmap.get("insight"),
        "update_schedule": "Updated hourly (rate limit protection)",
        "data_sources": {
            "fragility": "Calculated from OI, Funding Rate, Order Book Depth, and Spot-Perp Basis",
            "estimated": "Calculated from OI + leverage distribution assumptions (~60-70% accuracy)",
            "realized": "Actual liquidations from Binance forceOrder WebSocket stream"
        },
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
    macro, prices, pulse, sectors, key_levels, liquidation, stablecoin, calendar, correlation, rrg_rotation = await asyncio.gather(
        macro_tide_scorer.calculate_full_score(),
        get_market_prices(),
        get_crypto_pulse(),
        get_sector_data(),
        get_key_levels(),
        get_liquidation_heatmap(),
        get_stablecoin_flow(),
        get_economic_calendar(),
        get_correlation_matrix(),
        get_rrg_rotation()
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
        "rrg_rotation": rrg_rotation,
        "final_verdict": final_verdict,
        "last_updated": datetime.now().isoformat()
    }


@router.get("/rrg-rotation")
async def get_rrg_rotation() -> Dict[str, Any]:
    """
    Get Accelerating Momentum Rotation Map data.

    Returns:
        - ETF positions with Momentum Score (x) and Acceleration Score (y)
        - Market regime (Risk-On/Risk-Off/Neutral)
        - Top investment picks
        - Action groups (Buy/Watch/Reduce/Avoid)
        - Key insights
    """
    try:
        # Initialize components
        fetcher = RRGDataFetcher()
        engine = RRGEngine()
        
        # Fetch price data
        price_data = await fetcher.fetch_all_symbols()

        if not price_data:
            return {
                "error": "Unable to fetch price data",
                "timestamp": datetime.now().isoformat()
            }

        # Calculate Accelerating Momentum scores for all ETFs
        results = engine.calculate_all(price_data)
        
        # Detect market regime
        regime = engine.detect_regime(results)
        
        # Generate recommendations
        top_picks = engine.get_top_picks(results)
        action_groups = engine.get_action_groups(results)
        insights = engine.generate_insights(results, regime)
        
        # Separate by category
        risk_assets = [
            {
                "symbol": r.symbol,
                "name": r.name,
                "category": r.category,
                "color": r.color,
                "coordinate": {
                    "rs_ratio": r.rs_ratio,
                    "rs_momentum": r.rs_momentum,
                    "quadrant": r.quadrant
                },
                "current_price": r.current_price,
                "period_return": r.period_return
            }
            for r in results if r.category == "risk"
        ]
        
        safe_haven_assets = [
            {
                "symbol": r.symbol,
                "name": r.name,
                "category": r.category,
                "color": r.color,
                "coordinate": {
                    "rs_ratio": r.rs_ratio,
                    "rs_momentum": r.rs_momentum,
                    "quadrant": r.quadrant
                },
                "current_price": r.current_price,
                "period_return": r.period_return
            }
            for r in results if r.category == "safe_haven"
        ]
        
        await fetcher.close()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "benchmark": "SPY",
            "risk_assets": risk_assets,
            "safe_haven_assets": safe_haven_assets,
            "regime": {
                "regime": regime.regime,
                "score": regime.score,
                "emoji": regime.emoji,
                "color": regime.color,
                "risk_summary": regime.risk_summary,
                "safe_summary": regime.safe_summary
            },
            "top_picks": top_picks,
            "action_groups": action_groups,
            "insights": insights,
            "calculation_period": 21,
            "data_freshness": "Live"
        }
        
    except Exception as e:
        print(f"Error in RRG rotation endpoint: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
