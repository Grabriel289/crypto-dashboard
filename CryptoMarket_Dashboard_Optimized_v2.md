# Crypto Market Condition Dashboard — Optimized Specification
## For AI Code Assistant Implementation (OpenClaw / Kimi Code / Claude Code)

**Version:** 2.0 (Optimized)  
**Author:** Orbix Invest — Quant Research Team  
**Date:** February 2026  
**Purpose:** Production-ready Crypto Market Dashboard with Sector Rotation

---

## 1. Dashboard Overview

### 1.1 Design Philosophy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PRINCIPLE: "Less is More, but What's There Must Be Actionable"             │
│                                                                              │
│  • Every metric must drive a decision                                       │
│  • No vanity metrics or noise                                               │
│  • Clear visual hierarchy: Macro → Crypto → Sector → Action                 │
│  • Real-time where it matters, delayed where acceptable                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Final Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HEADER: Date | Last Updated | Overall Regime Badge                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ═══════════════════════ SECTION 1: MACRO TIDE ═══════════════════════     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🌊 MACRO TIDE (B1 SCORING)                                          │   │
│  │                                                                      │   │
│  │  B1 RAW SCORE: 3.0 / 5.0                                            │   │
│  │  ┌────────┬────────┬────────┬────────┬────────┐                     │   │
│  │  │  NFCI  │HY Spread│  MOVE  │ Cu/Au  │Net Liq │                     │   │
│  │  │ -0.57  │ 2.86%  │   68   │0.00115 │ $5.88T │                     │   │
│  │  │ 🟢 1.0 │ 🟢 1.0 │ 🟢 1.0 │ 🟡 0.0 │ 🟡 0.0 │                     │   │
│  │  └────────┴────────┴────────┴────────┴────────┘                     │   │
│  │                                                                      │   │
│  │  🚰 LIQUIDITY LEAK MONITOR                     LEAK PENALTY: -1.0   │   │
│  │  ┌─────────────────┬─────────────────┬─────────────────┐            │   │
│  │  │ Fiscal Dominance│Gold Cannibalize │  Policy Lag     │            │   │
│  │  │   🔴 ACTIVE     │   🔴 ACTIVE     │   🟡 PARTIAL    │            │   │
│  │  │   +45bp gap     │  ETF -$8.5B     │  Seized only    │            │   │
│  │  └─────────────────┴─────────────────┴─────────────────┘            │   │
│  │                                                                      │   │
│  │  ══════════════════════════════════════════════════════════════     │   │
│  │  ADJUSTED SCORE: 2.0 / 5.0  →  🔴 RISK-OFF / BLOCKED FLOW           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ═══════════════════════ SECTION 2: CRYPTO PULSE ═══════════════════════   │
│                                                                              │
│  ┌───────────────────────┐  ┌───────────────────────┐                      │
│  │  📊 MARKET FRAGILITY  │  │  😱 FEAR & GREED      │                      │
│  │                       │  │                       │                      │
│  │  BTC: 45/100 🟡       │  │      8 / 100          │                      │
│  │  ETH: 48/100 🟡       │  │   EXTREME FEAR        │                      │
│  │  SOL: 58/100 🟠       │  │                       │                      │
│  │  ─────────────────    │  │  Historical: 70%      │                      │
│  │  Composite: 50 🟡     │  │  probability bottom   │                      │
│  └───────────────────────┘  └───────────────────────┘                      │
│                                                                              │
│  ┌───────────────────────┐  ┌───────────────────────┐                      │
│  │  🐋 WHALE ACTIVITY    │  │  ⚖️ FUNDING RATES     │                      │
│  │                       │  │                       │                      │
│  │  Total OI: $5.50B     │  │  BTC: -0.05% 🟢       │                      │
│  │  OI 24h: -3.2%        │  │  ETH: -0.02% 🟢       │                      │
│  │  Exchange Flow: +15%  │  │  SOL: +0.08% 🟡       │                      │
│  │  ─────────────────    │  │  ─────────────────    │                      │
│  │  Signal: DISTRIBUTION │  │  Signal: SQUEEZE      │                      │
│  │          NET SHORT    │  │          SETUP        │                      │
│  └───────────────────────┘  └───────────────────────┘                      │
│                                                                              │
│  ═══════════════════════ SECTION 3: SECTOR ROTATION ════════════════════   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🔄 SECTOR MOMENTUM RANKING (7D vs BTC)                              │   │
│  │                                                                      │   │
│  │  VERDICT: ❌ STAY IN BTC — No sector outperforming consistently     │   │
│  │                                                                      │   │
│  │  Rank │ Sector   │ 7D Return │ vs BTC  │ Mom Score │ Signal         │   │
│  │  ─────┼──────────┼───────────┼─────────┼───────────┼────────────    │   │
│  │   1   │ RWA      │  +2.3%    │ +4.4%   │  72/100   │ 🟢 ROTATE IN  │   │
│  │   2   │ AI       │  -0.8%    │ +1.3%   │  58/100   │ 🟡 WATCH      │   │
│  │   3   │ L1       │  -1.5%    │ +0.6%   │  52/100   │ 🟡 NEUTRAL    │   │
│  │   4   │ DeFi     │  -2.1%    │  0.0%   │  48/100   │ ⚪ NEUTRAL    │   │
│  │   5   │ L2       │  -3.2%    │ -1.1%   │  42/100   │ 🟠 AVOID      │   │
│  │   6   │ PERP     │  -4.5%    │ -2.4%   │  35/100   │ 🔴 ROTATE OUT │   │
│  │   7   │ Meme     │  -8.2%    │ -6.1%   │  22/100   │ 🔴 CAPITULATE │   │
│  │   8   │ Privacy  │  -9.1%    │ -7.0%   │  18/100   │ 🔴 AVOID      │   │
│  │                                                                      │   │
│  │  ═══ TOP PICKS BY SECTOR ═══                                        │   │
│  │  RWA:  PAXG (+5.2%) | ONDO (-2.1%)                                  │   │
│  │  AI:   TAO (+3.1%)  | RENDER (-1.2%) | FET (-2.8%)                  │   │
│  │  L1:   BTC (-2.1%)  | SOL (-3.4%)    | SUI (-4.2%)                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ═══════════════════════ SECTION 4: ACTION ITEMS ═══════════════════════   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🎯 PRIORITIZED ACTIONS                                              │   │
│  │                                                                      │   │
│  │  🔴 HIGH   │ Do NOT panic sell — F&G at 8 = 70% bottom probability  │   │
│  │  🔴 HIGH   │ Accumulate BTC at $66,500-$68,000 if Macro ≥ 2.5       │   │
│  │  🟡 MEDIUM │ Avoid Meme/Privacy sectors — capitulation ongoing      │   │
│  │  🟡 MEDIUM │ Watch RWA sector for rotation if Macro improves        │   │
│  │  ⚪ LOW    │ Scale into ETH at $1,900-$2,000 support                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  FOOTER: 🎯 REGIME: RISK-OFF | STANCE: Defensive | STABLE ALLOCATION: 20%+ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Module Specifications

### 2.1 SECTION 1: Macro Tide (B1 Scoring)

> **Source:** ตาม Macro Weekly Report doc

#### B1 Indicators (5 ตัว)

| # | Indicator | Source | API | Scoring Logic |
|---|-----------|--------|-----|---------------|
| 1 | **NFCI** | FRED | `NFCI` | < 0 = 1.0pt, 0-0.5 = 0.5pt, > 0.5 = 0pt |
| 2 | **HY Spread** | FRED | `BAMLH0A0HYM2` | < 3.5% = 1.0pt, 3.5-5.5% = 0.5pt, > 5.5% = 0pt |
| 3 | **MOVE Index** | Yahoo | `^MOVE` | < 80 = 1.0pt, 80-110 = 0.5pt, > 110 = 0pt |
| 4 | **Cu/Au Ratio** | Yahoo | `HG=F / GC=F` | Rising = 1.0pt, Flat = 0.5pt, Falling = 0pt |
| 5 | **Net Liquidity** | FRED | `WALCL - WTREGEN - RRPONTSYD` | YoY > 5% = 1.0pt, 0-5% = 0.5pt, < 0 = 0pt |

#### Liquidity Leak Monitor (3 ตัว)

| # | Leak | Trigger Condition | Penalty |
|---|------|-------------------|---------|
| 1 | **Fiscal Dominance** | 10Y - Fed Funds > 25bp | -0.5 |
| 2 | **Gold Cannibalization** | BTC ETF cumulative outflow > $3B | -0.5 |
| 3 | **Policy Lag** | BTC Reserve = seized only / CLARITY Act blocked | -0.25 to -0.5 |

#### Final Calculation

```python
B1_RAW_SCORE = NFCI_score + HY_score + MOVE_score + CuAu_score + NetLiq_score  # 0-5
LEAK_PENALTY = sum(active_leak_penalties)  # 0 to -1.5
ADJUSTED_SCORE = max(0, B1_RAW_SCORE + LEAK_PENALTY)  # 0-5

# Regime Classification
if ADJUSTED_SCORE >= 4.0: regime = "🟢 HIGH TIDE / RISK-ON"
elif ADJUSTED_SCORE >= 3.0: regime = "🟡 NEUTRAL"  
elif ADJUSTED_SCORE >= 2.0: regime = "🟠 CAUTION / BLOCKED FLOW"
else: regime = "🔴 LOW TIDE / RISK-OFF"
```

---

### 2.2 SECTION 2: Crypto Pulse

#### 2.2.1 Fear & Greed Index

| Source | API | Update |
|--------|-----|--------|
| Alternative.me | `https://api.alternative.me/fng/` | Daily |

```python
def interpret_fear_greed(value: int) -> dict:
    if value <= 10:
        return {
            "label": "EXTREME FEAR",
            "signal": "BOTTOM_SIGNAL",
            "probability": "70% local bottom",
            "action": "Accumulate"
        }
    elif value <= 25:
        return {"label": "FEAR", "signal": "CAUTIOUS_BULLISH", ...}
    elif value <= 45:
        return {"label": "NEUTRAL_FEAR", "signal": "NEUTRAL", ...}
    elif value <= 55:
        return {"label": "NEUTRAL", "signal": "NEUTRAL", ...}
    elif value <= 75:
        return {"label": "GREED", "signal": "CAUTIOUS_BEARISH", ...}
    else:
        return {
            "label": "EXTREME GREED",
            "signal": "TOP_SIGNAL", 
            "probability": "65% local top",
            "action": "Take profits"
        }
```

#### 2.2.2 Market Fragility (0-100)

**Assets to Track:** BTC, ETH, SOL

| Component | Weight | Data Source | Logic |
|-----------|--------|-------------|-------|
| Volatility Percentile | 25% | Binance | Current 7d vol vs 1Y range |
| Drawdown from ATH | 25% | Binance | Deeper = more fragile |
| Funding Rate | 25% | Binance Futures | Extreme = more fragile |
| Exchange Net Flow | 25% | Glassnode/CryptoQuant | Inflows = distribution = fragile |

```python
def calculate_fragility(
    vol_percentile: float,    # 0-100
    drawdown_pct: float,      # negative number
    funding_rate: float,      # 8h rate
    exchange_flow_pct: float  # positive = inflow
) -> int:
    score = 0
    
    # Volatility (0-25)
    score += min(25, vol_percentile * 0.25)
    
    # Drawdown (0-25)
    dd_score = min(25, abs(drawdown_pct) * 0.5)
    score += dd_score
    
    # Funding (0-25) - extreme funding = fragile
    if funding_rate > 0.05:
        score += 25  # Overleveraged longs
    elif funding_rate > 0.02:
        score += 15
    elif funding_rate < -0.03:
        score += 5   # Squeeze setup = less fragile
    else:
        score += 10
    
    # Exchange Flow (0-25)
    if exchange_flow_pct > 10:
        score += 25  # Heavy inflows = distribution
    elif exchange_flow_pct > 0:
        score += 15
    else:
        score += 5   # Outflows = accumulation
    
    return min(100, int(score))

def get_fragility_label(score: int) -> tuple[str, str]:
    if score >= 75: return "CRITICAL", "🔴"
    if score >= 50: return "ELEVATED", "🟠"
    if score >= 25: return "MODERATE", "🟡"
    return "LOW", "🟢"
```

#### 2.2.3 Whale Activity

| Metric | Source | API |
|--------|--------|-----|
| Total Open Interest | Binance | `/fapi/v1/openInterest` |
| OI Change 24h | Calculated | Compare snapshots |
| Exchange Net Flow | Glassnode | Premium API (or CryptoQuant) |

```python
@dataclass
class WhaleActivity:
    total_oi_usd: float
    oi_change_24h_pct: float
    exchange_inflow_pct: float
    
    @property
    def positioning_signal(self) -> str:
        # OI rising + inflows = distribution (bearish)
        if self.oi_change_24h_pct > 5 and self.exchange_inflow_pct > 5:
            return "DISTRIBUTION / NET SHORT"
        # OI falling + outflows = accumulation (bullish)
        elif self.oi_change_24h_pct < -5 and self.exchange_inflow_pct < -5:
            return "ACCUMULATION / NET LONG"
        elif self.exchange_inflow_pct > 10:
            return "DISTRIBUTION DETECTED"
        elif self.exchange_inflow_pct < -10:
            return "ACCUMULATION DETECTED"
        else:
            return "NEUTRAL"
```

#### 2.2.4 Funding Rates (เลือกแทน Spot-Futures Spread)

> **เหตุผลที่เลือก Funding Rate:**
> - Update บ่อยกว่า (8h vs daily settle)
> - บอก positioning ชัดเจนกว่า
> - Data เข้าถึงง่ายกว่า (Binance public API)
> - Spot-Futures spread ซ้ำซ้อนกับ funding rate ในการตีความ

| Asset | Source | API Endpoint |
|-------|--------|--------------|
| BTC | Binance | `/fapi/v1/fundingRate?symbol=BTCUSDT` |
| ETH | Binance | `/fapi/v1/fundingRate?symbol=ETHUSDT` |
| SOL | Binance | `/fapi/v1/fundingRate?symbol=SOLUSDT` |

```python
def interpret_funding(rate: float) -> dict:
    """
    rate: 8h funding rate (e.g., -0.0005 = -0.05%)
    """
    rate_pct = rate * 100  # Convert to percentage
    
    if rate_pct < -0.03:
        return {
            "signal": "STRONG SQUEEZE SETUP",
            "emoji": "🟢",
            "bias": "bullish",
            "description": "Shorts paying longs heavily"
        }
    elif rate_pct < 0:
        return {
            "signal": "SQUEEZE SETUP",
            "emoji": "🟢", 
            "bias": "bullish",
            "description": "Negative funding; shorts dominant"
        }
    elif rate_pct < 0.03:
        return {
            "signal": "NEUTRAL",
            "emoji": "🟡",
            "bias": "neutral",
            "description": "Balanced positioning"
        }
    elif rate_pct < 0.08:
        return {
            "signal": "OVERLEVERAGED LONGS",
            "emoji": "🟠",
            "bias": "bearish",
            "description": "Pullback risk elevated"
        }
    else:
        return {
            "signal": "EXTREME EUPHORIA",
            "emoji": "🔴",
            "bias": "bearish",
            "description": "Correction imminent"
        }
```

---

### 2.3 SECTION 3: Sector Rotation

#### 2.3.1 Sector Definitions

```python
SECTORS = {
    "AI": {
        "coins": ["RENDER", "TAO", "FET", "VIRTUAL", "WLD", "ZORA"],
        "description": "AI & Compute tokens"
    },
    "DeFi": {
        "coins": ["UNI", "AAVE", "SKY", "AERO", "JUP", "SYRUP", "PENDLE", "ENA", "ETHFI", "WLFI"],
        "description": "Decentralized Finance"
    },
    "L1": {
        "coins": ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "NEAR", "SEI", "APT", "SUI", "TON", "TRX", "MON"],
        "description": "Layer 1 Blockchains"
    },
    "Privacy": {
        "coins": ["ZEC", "XMR"],
        "description": "Privacy coins"
    },
    "L2": {
        "coins": ["ARB", "OP", "STK"],
        "description": "Layer 2 Scaling"
    },
    "RWA": {
        "coins": ["PAXG", "ONDO"],
        "description": "Real World Assets"
    },
    "Meme": {
        "coins": ["DOGE", "PEPE", "SHIB", "PENGU", "BONK", "PUMP"],
        "description": "Meme coins"
    },
    "PERP": {
        "coins": ["HYPE", "LIT", "ASTER"],
        "description": "Perpetual DEX tokens"
    }
}
```

#### 2.3.2 API Priority & Symbol Mapping

```python
EXCHANGE_PRIORITY = ["binance", "okx", "kucoin", "coinbase"]

# Symbol mapping per exchange
SYMBOL_MAPPING = {
    "binance": {
        "BTC": "BTCUSDT",
        "ETH": "ETHUSDT",
        "SOL": "SOLUSDT",
        "RENDER": "RENDERUSDT",
        "TAO": "TAOUSDT",
        "FET": "FETUSDT",
        # ... etc
    },
    "okx": {
        "BTC": "BTC-USDT",
        "ETH": "ETH-USDT",
        # ...
    },
    "kucoin": {
        "BTC": "BTC-USDT",
        # ...
    },
    "coinbase": {
        "BTC": "BTC-USD",
        # ...
    }
}

async def fetch_price_with_fallback(coin: str) -> dict:
    """
    Try exchanges in priority order until success
    """
    for exchange in EXCHANGE_PRIORITY:
        try:
            symbol = SYMBOL_MAPPING[exchange].get(coin)
            if not symbol:
                continue
            
            price_data = await fetch_from_exchange(exchange, symbol)
            if price_data:
                return {
                    "coin": coin,
                    "price": price_data["price"],
                    "change_24h": price_data["change_24h"],
                    "change_7d": price_data["change_7d"],
                    "source": exchange
                }
        except Exception as e:
            continue
    
    return {"coin": coin, "error": "No data available"}
```

#### 2.3.3 Momentum Score Calculation

> **Core Logic: Sector Momentum Score (0-100)**

```python
@dataclass
class MomentumMetrics:
    """Raw momentum data for a single asset"""
    return_1d: float
    return_7d: float
    return_30d: float
    return_1d_vs_btc: float  # Relative to BTC
    return_7d_vs_btc: float
    return_30d_vs_btc: float
    volume_change_7d: float  # Volume trend
    
def calculate_momentum_score(metrics: MomentumMetrics) -> int:
    """
    Momentum Score: 0-100
    Higher = Stronger momentum, better rotation candidate
    
    Components:
    1. Absolute Momentum (40%): Is it going up?
    2. Relative Momentum vs BTC (40%): Is it beating BTC?
    3. Volume Confirmation (20%): Is volume supporting the move?
    """
    score = 0
    
    # ═══════════════════════════════════════════════════════════════
    # COMPONENT 1: ABSOLUTE MOMENTUM (40 points max)
    # ═══════════════════════════════════════════════════════════════
    
    # 1D Return (10 points)
    if metrics.return_1d > 5:
        score += 10
    elif metrics.return_1d > 2:
        score += 8
    elif metrics.return_1d > 0:
        score += 5
    elif metrics.return_1d > -2:
        score += 3
    else:
        score += 0
    
    # 7D Return (15 points) - Most important timeframe
    if metrics.return_7d > 15:
        score += 15
    elif metrics.return_7d > 8:
        score += 12
    elif metrics.return_7d > 3:
        score += 9
    elif metrics.return_7d > 0:
        score += 6
    elif metrics.return_7d > -5:
        score += 3
    else:
        score += 0
    
    # 30D Return (15 points) - Trend confirmation
    if metrics.return_30d > 30:
        score += 15
    elif metrics.return_30d > 15:
        score += 12
    elif metrics.return_30d > 5:
        score += 9
    elif metrics.return_30d > 0:
        score += 6
    elif metrics.return_30d > -10:
        score += 3
    else:
        score += 0
    
    # ═══════════════════════════════════════════════════════════════
    # COMPONENT 2: RELATIVE MOMENTUM vs BTC (40 points max)
    # ═══════════════════════════════════════════════════════════════
    
    # 7D vs BTC (25 points) - Key metric for rotation decision
    if metrics.return_7d_vs_btc > 10:
        score += 25  # Strong outperformance
    elif metrics.return_7d_vs_btc > 5:
        score += 20
    elif metrics.return_7d_vs_btc > 2:
        score += 15
    elif metrics.return_7d_vs_btc > 0:
        score += 10  # Slight outperformance
    elif metrics.return_7d_vs_btc > -2:
        score += 5   # Slight underperformance
    else:
        score += 0   # Significant underperformance
    
    # 30D vs BTC (15 points) - Trend confirmation
    if metrics.return_30d_vs_btc > 15:
        score += 15
    elif metrics.return_30d_vs_btc > 5:
        score += 10
    elif metrics.return_30d_vs_btc > 0:
        score += 7
    elif metrics.return_30d_vs_btc > -5:
        score += 3
    else:
        score += 0
    
    # ═══════════════════════════════════════════════════════════════
    # COMPONENT 3: VOLUME CONFIRMATION (20 points max)
    # ═══════════════════════════════════════════════════════════════
    
    # Volume trend should confirm price trend
    if metrics.volume_change_7d > 50 and metrics.return_7d > 0:
        score += 20  # Strong volume + price up = confirmed
    elif metrics.volume_change_7d > 20 and metrics.return_7d > 0:
        score += 15
    elif metrics.volume_change_7d > 0:
        score += 10
    elif metrics.volume_change_7d > -20:
        score += 5
    else:
        score += 0   # Volume declining
    
    return min(100, score)
```

#### 2.3.4 Sector Aggregation

```python
def calculate_sector_momentum(sector_name: str, coin_data: dict[str, MomentumMetrics]) -> dict:
    """
    Calculate sector-level momentum from individual coins
    
    Aggregation method: Market-cap weighted average (simplified to equal weight if no mcap)
    """
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
    
    return {
        "sector": sector_name,
        "momentum_score": int(sum(scores) / len(scores)),
        "avg_return_7d": sum(returns_7d) / len(returns_7d),
        "avg_vs_btc_7d": sum(returns_vs_btc) / len(returns_vs_btc),
        "coin_count": len(scores),
        "top_performer": max(coin_data.items(), key=lambda x: x[1].return_7d if x[0] in coins else -999)[0],
    }
```

#### 2.3.5 Rotation Decision Logic

```python
def should_rotate_to_sector(
    sector_momentum: dict,
    btc_momentum_score: int,
    macro_adjusted_score: float
) -> dict:
    """
    Determine if should rotate from BTC to sector
    
    Decision Matrix:
    ┌─────────────────┬───────────────┬───────────────┬───────────────┐
    │                 │ Macro ≥ 3.0   │ Macro 2.0-3.0 │ Macro < 2.0   │
    │                 │ (RISK-ON)     │ (NEUTRAL)     │ (RISK-OFF)    │
    ├─────────────────┼───────────────┼───────────────┼───────────────┤
    │ Sector > BTC    │ 🟢 ROTATE IN  │ 🟡 WATCH      │ 🟠 STAY BTC   │
    │ by > 10 pts     │               │               │               │
    ├─────────────────┼───────────────┼───────────────┼───────────────┤
    │ Sector > BTC    │ 🟡 WATCH      │ 🟡 NEUTRAL    │ 🟠 STAY BTC   │
    │ by 0-10 pts     │               │               │               │
    ├─────────────────┼───────────────┼───────────────┼───────────────┤
    │ Sector < BTC    │ 🟠 STAY BTC   │ 🔴 AVOID      │ 🔴 AVOID      │
    │                 │               │               │               │
    └─────────────────┴───────────────┴───────────────┴───────────────┘
    """
    sector_score = sector_momentum["momentum_score"]
    score_diff = sector_score - btc_momentum_score
    vs_btc_return = sector_momentum["avg_vs_btc_7d"]
    
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
                "action": f"Strong momentum + supportive macro; consider {sector_momentum['top_performer']}",
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
    all_sectors: list[dict],
    btc_momentum: int,
    macro_score: float
) -> dict:
    """
    Generate overall sector rotation verdict
    """
    # Count sectors outperforming BTC
    outperforming = [s for s in all_sectors if s["momentum_score"] > btc_momentum]
    
    if len(outperforming) == 0:
        return {
            "verdict": "❌ STAY IN BTC",
            "reason": "No sector consistently outperforming BTC",
            "recommended_allocation": {
                "BTC": "70-80%",
                "Stables": "20-30%"
            }
        }
    
    if macro_score < 2.0:
        return {
            "verdict": "⚠️ DEFENSIVE MODE",
            "reason": f"{len(outperforming)} sectors showing momentum but macro unfavorable",
            "recommended_allocation": {
                "BTC": "50%",
                "Stables": "40%",
                "Best Sector": "10% max"
            }
        }
    
    best_sector = max(all_sectors, key=lambda x: x["momentum_score"])
    if best_sector["momentum_score"] > btc_momentum + 15:
        return {
            "verdict": f"🟢 ROTATE TO {best_sector['sector'].upper()}",
            "reason": f"{best_sector['sector']} score {best_sector['momentum_score']} vs BTC {btc_momentum}",
            "recommended_allocation": {
                "BTC": "40%",
                best_sector["sector"]: "30%",
                "Stables": "30%"
            }
        }
    
    return {
        "verdict": "🟡 SELECTIVE ROTATION",
        "reason": "Some sectors showing strength; partial rotation OK",
        "recommended_allocation": {
            "BTC": "60%",
            "Best Sectors": "25%",
            "Stables": "15%"
        }
    }
```

---

### 2.4 SECTION 4: Action Items Generator

```python
def generate_action_items(
    macro_score: float,
    macro_regime: str,
    fear_greed: int,
    fragility_composite: int,
    funding_signals: dict,
    whale_signal: str,
    sector_verdict: dict
) -> list[dict]:
    """
    Generate prioritized action items based on all inputs
    """
    actions = []
    
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
    if fear_greed <= 15 and funding_signals.get("BTC", {}).get("bias") == "bullish":
        if macro_score >= 2.0:
            actions.append({
                "priority": "HIGH",
                "emoji": "🔴",
                "action": "Selective accumulation of BTC",
                "reason": "Extreme fear + negative funding + acceptable macro",
                "condition": f"Entry zone: current price ± 3%"
            })
        else:
            actions.append({
                "priority": "MEDIUM",
                "emoji": "🟡",
                "action": "Prepare for accumulation",
                "reason": "Fear + squeeze setup BUT macro weak",
                "condition": f"Wait for Macro ≥ 2.5"
            })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 3: Sector Rotation Actions
    # ═══════════════════════════════════════════════════════════════
    if "ROTATE TO" in sector_verdict.get("verdict", ""):
        sector = sector_verdict["verdict"].replace("🟢 ROTATE TO ", "")
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": f"Consider rotation to {sector}",
            "reason": sector_verdict["reason"],
            "condition": "Scale in gradually; 5-10% per day"
        })
    
    if sector_verdict.get("verdict", "").startswith("❌"):
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": "Avoid altcoin rotation",
            "reason": "No sector outperforming BTC consistently",
            "condition": "Stay in BTC or stables"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 4: Risk Management
    # ═══════════════════════════════════════════════════════════════
    if fragility_composite >= 60:
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": "Avoid high-leverage longs",
            "reason": f"Market fragility elevated ({fragility_composite}/100)",
            "condition": "Max 2x leverage"
        })
    
    if whale_signal == "DISTRIBUTION / NET SHORT":
        actions.append({
            "priority": "MEDIUM",
            "emoji": "🟡",
            "action": "Tighten stop losses",
            "reason": "Whale distribution detected",
            "condition": "Trail stops at -5%"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 5: Macro-driven Actions
    # ═══════════════════════════════════════════════════════════════
    if macro_score < 2.0:
        actions.append({
            "priority": "HIGH",
            "emoji": "🔴",
            "action": "Defensive allocation",
            "reason": f"Macro score {macro_score}/5 = Risk-Off",
            "condition": "Stables 30%+, reduce alt exposure"
        })
    
    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    actions.sort(key=lambda x: priority_order.get(x["priority"], 2))
    
    return actions[:5]  # Return top 5 actions
```

---

## 3. Data Pipeline

### 3.1 API Endpoints

#### Binance (Primary)

```python
BINANCE_ENDPOINTS = {
    "spot_price": "https://api.binance.com/api/v3/ticker/24hr",
    "klines": "https://api.binance.com/api/v3/klines",
    "funding_rate": "https://fapi.binance.com/fapi/v1/fundingRate",
    "open_interest": "https://fapi.binance.com/fapi/v1/openInterest",
}

async def fetch_binance_price(symbol: str) -> dict:
    """Fetch 24h price data from Binance"""
    url = f"{BINANCE_ENDPOINTS['spot_price']}?symbol={symbol}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return {
                "price": float(data["lastPrice"]),
                "change_24h": float(data["priceChangePercent"]),
                "volume_24h": float(data["quoteVolume"]),
                "high_24h": float(data["highPrice"]),
                "low_24h": float(data["lowPrice"]),
            }

async def fetch_binance_klines(symbol: str, interval: str = "1d", limit: int = 30) -> pd.DataFrame:
    """Fetch OHLCV data for momentum calculation"""
    url = f"{BINANCE_ENDPOINTS['klines']}?symbol={symbol}&interval={interval}&limit={limit}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "trades", "taker_buy_base",
                "taker_buy_quote", "ignore"
            ])
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            return df
```

#### Fallback Exchanges

```python
async def fetch_okx_price(symbol: str) -> dict:
    """OKX fallback"""
    url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}"
    # Implementation

async def fetch_kucoin_price(symbol: str) -> dict:
    """KuCoin fallback"""
    url = f"https://api.kucoin.com/api/v1/market/stats?symbol={symbol}"
    # Implementation

async def fetch_coinbase_price(symbol: str) -> dict:
    """Coinbase fallback"""
    url = f"https://api.coinbase.com/v2/prices/{symbol}/spot"
    # Implementation
```

### 3.2 Update Schedule

| Module | Update Frequency | Priority |
|--------|------------------|----------|
| Macro Tide (B1) | Daily 6:00 AM | High |
| Fear & Greed | Daily 6:00 AM | High |
| Funding Rates | Every 8 hours | High |
| Market Fragility | Every 15 min | Medium |
| Whale Activity | Every 1 hour | Medium |
| Sector Momentum | Every 1 hour | Medium |
| Action Items | On data update | High |

---

## 4. UI Design Guidelines

### 4.1 Color Palette (Cyberpunk Trading Terminal)

```css
:root {
  /* Backgrounds */
  --bg-primary: #0a0a0f;
  --bg-secondary: #12121a;
  --bg-card: #1a1a2e;
  --bg-card-hover: #242438;
  
  /* Accents */
  --accent-green: #00ff88;
  --accent-green-dim: #00cc6a;
  --accent-red: #ff4444;
  --accent-red-dim: #cc3333;
  --accent-yellow: #ffaa00;
  --accent-orange: #ff6b35;
  --accent-cyan: #00d4ff;
  --accent-purple: #9d4edd;
  
  /* Text */
  --text-primary: #ffffff;
  --text-secondary: #888888;
  --text-muted: #555555;
  
  /* Borders */
  --border-subtle: #2a2a3e;
  --border-accent: #3a3a5e;
  
  /* Gradients */
  --gradient-danger: linear-gradient(90deg, #ff4444, #ff6b35);
  --gradient-success: linear-gradient(90deg, #00ff88, #00d4ff);
  --gradient-warning: linear-gradient(90deg, #ffaa00, #ff6b35);
}
```

### 4.2 Component Styling

```css
/* Card Component */
.dashboard-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.dashboard-card:hover {
  border-color: var(--border-accent);
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.1);
}

/* Score Display */
.score-display {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 0 0 10px currentColor;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.risk-on {
  background: rgba(0, 255, 136, 0.15);
  color: var(--accent-green);
  border: 1px solid var(--accent-green);
}

.status-badge.risk-off {
  background: rgba(255, 68, 68, 0.15);
  color: var(--accent-red);
  border: 1px solid var(--accent-red);
}

/* Progress Bar (Arthur Panic Zone style) */
.panic-bar {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.panic-bar-fill {
  height: 100%;
  background: var(--gradient-danger);
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* Table Styling */
.sector-table {
  width: 100%;
  border-collapse: collapse;
}

.sector-table th {
  text-align: left;
  padding: 12px;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 1px solid var(--border-subtle);
}

.sector-table td {
  padding: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.sector-table tr:hover {
  background: var(--bg-card-hover);
}
```

### 4.3 Responsive Breakpoints

```css
/* Mobile First */
.dashboard-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr;
}

/* Tablet */
@media (min-width: 768px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Wide Desktop */
@media (min-width: 1440px) {
  .dashboard-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

---

## 5. Project Structure

```
crypto_dashboard_v2/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
│
├── backend/
│   ├── main.py                      # FastAPI entry
│   ├── config/
│   │   ├── settings.py
│   │   ├── sectors.py               # Sector definitions
│   │   └── thresholds.py
│   │
│   ├── data/
│   │   ├── fetchers/
│   │   │   ├── base.py              # Abstract fetcher
│   │   │   ├── binance.py           # Primary
│   │   │   ├── okx.py               # Fallback 1
│   │   │   ├── kucoin.py            # Fallback 2
│   │   │   ├── coinbase.py          # Fallback 3
│   │   │   ├── fred.py              # Macro data
│   │   │   └── fear_greed.py
│   │   └── aggregator.py            # Multi-source with fallback
│   │
│   ├── scoring/
│   │   ├── macro_tide.py            # B1 + Leak scoring
│   │   ├── fragility.py
│   │   ├── funding.py
│   │   ├── whale.py
│   │   ├── momentum.py              # Momentum score calc
│   │   └── sector_rotation.py       # Sector aggregation + verdict
│   │
│   ├── analysis/
│   │   ├── action_generator.py
│   │   └── conclusion.py
│   │
│   └── api/
│       ├── routes/
│       │   ├── dashboard.py
│       │   ├── macro.py
│       │   ├── crypto.py
│       │   └── sectors.py
│       └── websocket.py
│
├── frontend/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   └── DashboardGrid.jsx
│   │   │   ├── macro/
│   │   │   │   ├── MacroTide.jsx
│   │   │   │   └── LeakMonitor.jsx
│   │   │   ├── crypto/
│   │   │   │   ├── FearGreed.jsx
│   │   │   │   ├── Fragility.jsx
│   │   │   │   ├── WhaleActivity.jsx
│   │   │   │   └── FundingRates.jsx
│   │   │   ├── sectors/
│   │   │   │   ├── SectorTable.jsx
│   │   │   │   ├── SectorVerdict.jsx
│   │   │   │   └── TopPicks.jsx
│   │   │   └── actions/
│   │   │       └── ActionItems.jsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   └── useDashboardData.js
│   │   └── styles/
│   │       └── globals.css
│   └── public/
│
└── tests/
    ├── test_momentum.py
    ├── test_sector_rotation.py
    └── test_integration.py
```

---

## 6. Quick Reference

### 6.1 Key Formulas

| Metric | Formula |
|--------|---------|
| **B1 Raw Score** | NFCI_score + HY_score + MOVE_score + CuAu_score + NetLiq_score (0-5) |
| **Adjusted Score** | B1_Raw + Leak_Penalty (0-5) |
| **Momentum Score** | Absolute_Mom(40) + Relative_vs_BTC(40) + Volume_Confirm(20) (0-100) |
| **Fragility Score** | Vol(25) + DD(25) + Funding(25) + Flow(25) (0-100) |
| **Sector Score** | Average(all coin momentum scores in sector) |

### 6.2 Decision Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Macro Adjusted | ≥ 3.0 | Risk-On OK |
| Macro Adjusted | < 2.0 | Defensive mode |
| Fear & Greed | ≤ 10 | Accumulation signal |
| Fear & Greed | ≥ 90 | Take profit signal |
| Sector vs BTC | > 10 pts + > 5% return | Rotate in |
| Sector vs BTC | < BTC - 5% return | Rotate out |
| Fragility | ≥ 60 | Reduce leverage |
| Funding | < -0.03% | Squeeze setup |
| Funding | > 0.08% | Correction risk |

---

## Appendix A: Full Coin List by Exchange Availability

```python
COIN_AVAILABILITY = {
    # AI Sector
    "RENDER": {"binance": "RENDERUSDT", "okx": "RENDER-USDT", "kucoin": "RENDER-USDT"},
    "TAO": {"binance": "TAOUSDT", "okx": "TAO-USDT", "kucoin": None},
    "FET": {"binance": "FETUSDT", "okx": "FET-USDT", "kucoin": "FET-USDT"},
    "VIRTUAL": {"binance": None, "okx": "VIRTUAL-USDT", "kucoin": None},
    "WLD": {"binance": "WLDUSDT", "okx": "WLD-USDT", "kucoin": "WLD-USDT"},
    "ZORA": {"binance": None, "okx": None, "kucoin": None},  # New listing
    
    # DeFi Sector
    "UNI": {"binance": "UNIUSDT", "okx": "UNI-USDT", "kucoin": "UNI-USDT"},
    "AAVE": {"binance": "AAVEUSDT", "okx": "AAVE-USDT", "kucoin": "AAVE-USDT"},
    # ... etc
    
    # L1 Sector
    "BTC": {"binance": "BTCUSDT", "okx": "BTC-USDT", "kucoin": "BTC-USDT", "coinbase": "BTC-USD"},
    "ETH": {"binance": "ETHUSDT", "okx": "ETH-USDT", "kucoin": "ETH-USDT", "coinbase": "ETH-USD"},
    "SOL": {"binance": "SOLUSDT", "okx": "SOL-USDT", "kucoin": "SOL-USDT", "coinbase": "SOL-USD"},
    # ... etc
}
```

---

*End of Optimized Specification v2.0*
