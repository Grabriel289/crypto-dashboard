# Liquidation Heatmap System — Complete Technical Specification

**Document Type:** Development Specification for Kimi  
**Project:** GIGA Mission Control — Liquidation & Fragility Module  
**Version:** 2.0  
**Date:** February 2026  
**Author:** Orbix Invest Quant Team

---

## 1. Overview

### 1.1 Objective

สร้างระบบ **Liquidation Heatmap** ที่แสดง:
1. **Market Fragility Score (Φ)** — วัดความเปราะบางของตลาด
2. **Estimated Liquidation Heatmap** — ประมาณการ liquidation levels จาก OI + leverage
3. **Realized Liquidations** — liquidations ที่เกิดขึ้นจริงจาก WebSocket
4. **Historical Data** — เก็บข้อมูลใน PostgreSQL (Supabase)

### 1.2 Important Labels

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚠️ CRITICAL: DATA LABELING                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ต้อง LABEL ชัดเจนเสมอ:                                              │
│                                                                      │
│  "ESTIMATED" = คำนวณจาก OI + leverage assumptions                   │
│              → ไม่ใช่ actual pending liquidations                   │
│              → Accuracy ~60-70%                                      │
│                                                                      │
│  "REALIZED"  = liquidations ที่เกิดขึ้นจริงแล้ว                      │
│              → จาก Binance WebSocket                                │
│              → 100% accurate (past events)                          │
│                                                                      │
│  ห้าม claim ว่าเป็น exact data เหมือน Coinglass!                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SYSTEM ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   DATA SOURCES (Binance Free API)                                       │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  REST API                    │  WebSocket                        │   │
│   │  ├── Open Interest           │  └── Real-time Liquidations      │   │
│   │  ├── Funding Rate            │      wss://fstream.binance.com   │   │
│   │  ├── Order Book Depth        │      /ws/!forceOrder@arr         │   │
│   │  ├── Spot Price              │                                   │   │
│   │  └── Perp Price              │                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                          │                          │                    │
│                          ▼                          ▼                    │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    CALCULATION LAYER                             │   │
│   │                                                                  │   │
│   │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │   │
│   │  │ FRAGILITY (Φ)    │  │ ESTIMATED        │  │ REALIZED     │   │   │
│   │  │                  │  │ HEATMAP          │  │ HEATMAP      │   │   │
│   │  │ L_d + F_σ + B_z  │  │                  │  │              │   │   │
│   │  │ ─────────────    │  │ OI × Leverage    │  │ WebSocket    │   │   │
│   │  │       3          │  │ Distribution     │  │ Events       │   │   │
│   │  └──────────────────┘  └──────────────────┘  └──────────────┘   │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                          │                                               │
│                          ▼                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    SUPABASE (PostgreSQL)                         │   │
│   │                                                                  │   │
│   │  ├── liquidations          (real-time events)                   │   │
│   │  ├── market_snapshots      (OI, funding, depth every 5min)      │   │
│   │  ├── liquidation_aggregates (pre-calculated stats)              │   │
│   │  └── system_logs           (debugging)                          │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                          │                                               │
│                          ▼                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    OUTPUT / DISPLAY                              │   │
│   │                                                                  │   │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐  │   │
│   │  │ Dashboard  │  │ API (JSON) │  │ Alerts     │  │ Reports   │  │   │
│   │  │ (HTML/React)│  │            │  │ (Telegram) │  │ (6AM)     │  │   │
│   │  └────────────┘  └────────────┘  └────────────┘  └───────────┘  │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Binance Free API Endpoints

### 2.1 REST API Endpoints (No API Key Required)

| Data | Endpoint | Base URL |
|------|----------|----------|
| Open Interest | `/fapi/v1/openInterest` | https://fapi.binance.com |
| Funding Rate (Current) | `/fapi/v1/premiumIndex` | https://fapi.binance.com |
| Funding Rate (History) | `/fapi/v1/fundingRate` | https://fapi.binance.com |
| Order Book | `/fapi/v1/depth` | https://fapi.binance.com |
| Perp Price | `/fapi/v1/ticker/price` | https://fapi.binance.com |
| Spot Price | `/api/v3/ticker/price` | https://api.binance.com |

### 2.2 WebSocket Stream (No API Key Required)

```
URL: wss://fstream.binance.com/ws/!forceOrder@arr

Receives: All liquidation orders across all symbols
```

### 2.3 API Details

#### A) Open Interest

```python
# Request
GET https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT

# Response
{
    "openInterest": "10659.509",    # OI in contracts (not USD!)
    "symbol": "BTCUSDT",
    "time": 1589437530011
}

# Convert to USD
oi_usd = float(openInterest) * current_price
```

#### B) Order Book Depth

```python
# Request
GET https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=1000

# Response
{
    "lastUpdateId": 1027024,
    "bids": [
        ["95000.00", "4.00000"],   # [price, quantity]
        ["94999.00", "2.50000"],
        ...
    ],
    "asks": [
        ["95001.00", "3.00000"],
        ["95002.00", "1.80000"],
        ...
    ]
}
```

#### C) Funding Rate

```python
# Current Funding
GET https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT

# Response
{
    "symbol": "BTCUSDT",
    "markPrice": "95000.00",
    "lastFundingRate": "0.00010000",   # 0.01% = 0.0001
    "nextFundingTime": 1577836800000,
    "time": 1577836800000
}

# Funding History (for 7-day average)
GET https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=21

# Returns last 21 funding periods (7 days × 3 per day)
```

#### D) WebSocket Liquidation Stream

```python
# Connect
ws = websocket.connect("wss://fstream.binance.com/ws/!forceOrder@arr")

# Message format
{
    "e": "forceOrder",
    "E": 1568014460893,
    "o": {
        "s": "BTCUSDT",           # Symbol
        "S": "SELL",              # Side: SELL = Long liquidated, BUY = Short liquidated
        "o": "LIMIT",
        "f": "IOC",
        "q": "0.014",             # Quantity
        "p": "9910",              # Price
        "ap": "9910",             # Average Price
        "X": "FILLED",
        "l": "0.014",
        "z": "0.014",
        "T": 1568014460893        # Timestamp
    }
}

# Interpretation
if order['S'] == 'SELL':
    # LONG position was liquidated (forced to sell)
    side = 'LONG'
else:
    # SHORT position was liquidated (forced to buy)
    side = 'SHORT'
```

---

## 3. Market Fragility Score (Φ)

### 3.1 Formula

$$\Phi = \frac{L_d + F_\sigma + B_z}{3}$$

### 3.2 Component Calculations

#### L_d — Liquidation Density (Slippage Risk)

```python
def calculate_L_d(open_interest_usd: float, depth_2pct_usd: float) -> float:
    """
    L_d = min(100, OI / (Depth_2% × 10))
    
    Measures: How much OI vs available liquidity
    High L_d = Small trades cause cascades
    """
    if depth_2pct_usd <= 0:
        return 100.0
    
    L_d = open_interest_usd / (depth_2pct_usd * 10)
    return min(100.0, L_d)
```

#### F_σ — Funding Deviation (Position Crowding)

```python
def calculate_F_sigma(current_funding: float, funding_7d: list) -> float:
    """
    F_σ = min(100, |F_i - SMA_7d| / StdDev × 20)
    
    Measures: How far current funding is from average
    High F_σ = Extreme position crowding
    """
    import numpy as np
    
    if len(funding_7d) < 3:
        return 50.0  # Not enough data
    
    sma_7d = np.mean(funding_7d)
    std_7d = np.std(funding_7d)
    
    if std_7d == 0:
        return 50.0  # No variance
    
    z_score = abs(current_funding - sma_7d) / std_7d
    F_sigma = z_score * 20
    
    return min(100.0, F_sigma)
```

#### B_z — Basis Tension (Market Dislocation)

```python
def calculate_B_z(spot_price: float, perp_price: float) -> float:
    """
    B_z = min(100, |Spot - Perp| / Spot × 1000)
    
    Measures: Gap between spot and perpetual
    High B_z = Market dislocation, likely to snap back
    """
    if spot_price <= 0:
        return 50.0
    
    basis_pct = abs(spot_price - perp_price) / spot_price
    B_z = basis_pct * 1000
    
    return min(100.0, B_z)
```

### 3.3 Depth Calculation (within 2%)

```python
def calculate_depth_2pct(bids: list, asks: list, mid_price: float) -> float:
    """
    Calculate total liquidity within 2% of mid price.
    
    Args:
        bids: List of [price, quantity] from order book
        asks: List of [price, quantity] from order book
        mid_price: Current mid price
    
    Returns:
        Total USD liquidity within ±2%
    """
    upper_bound = mid_price * 1.02
    lower_bound = mid_price * 0.98
    
    # Sum bid liquidity within range
    bid_depth = sum(
        float(price) * float(qty)
        for price, qty in bids
        if float(price) >= lower_bound
    )
    
    # Sum ask liquidity within range
    ask_depth = sum(
        float(price) * float(qty)
        for price, qty in asks
        if float(price) <= upper_bound
    )
    
    return bid_depth + ask_depth
```

### 3.4 Fragility Level Interpretation

| Φ Score | Level | Emoji | Interpretation |
|---------|-------|-------|----------------|
| 0-25 | Stable | 🟢 | Safe to use large positions |
| 26-50 | Caution | 🟡 | Standard market conditions |
| 51-75 | Fragile | 🟠 | Expect wicky price action |
| 76-100 | Critical | 🔴 | High probability of flash crash/squeeze |

---

## 4. Estimated Liquidation Heatmap

### 4.1 Concept

```
┌─────────────────────────────────────────────────────────────────────┐
│  ESTIMATED vs ACTUAL PENDING LIQUIDATIONS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Coinglass รู้ "actual pending" เพราะมี partnership กับ exchanges   │
│  → เราไม่มีข้อมูลนั้น (ต้องจ่าย $200+/month)                        │
│                                                                      │
│  เราทำ "ESTIMATED" จาก:                                              │
│  1. Total Open Interest (OI)                                        │
│  2. Typical leverage distribution (5x, 10x, 20x, 50x, 100x)        │
│  3. Liquidation price formula                                       │
│                                                                      │
│  ⚠️ Accuracy ~60-70% — ต้อง label ว่า "ESTIMATED" เสมอ               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Leverage Distribution Assumption

```python
# Based on industry research
LEVERAGE_DISTRIBUTION = {
    5: 0.10,    # 10% of traders use 5x
    10: 0.25,   # 25% use 10x
    20: 0.30,   # 30% use 20x
    50: 0.25,   # 25% use 50x
    100: 0.10   # 10% use 100x
}
```

### 4.3 Liquidation Price Formula

```python
def calculate_liquidation_price(entry_price: float, leverage: int, is_long: bool) -> float:
    """
    Calculate liquidation price.
    
    For LONG:  Liq = Entry × (1 - 0.9/Leverage)
    For SHORT: Liq = Entry × (1 + 0.9/Leverage)
    
    0.9 factor accounts for maintenance margin (~10%)
    """
    margin_factor = 0.9 / leverage
    
    if is_long:
        return entry_price * (1 - margin_factor)
    else:
        return entry_price * (1 + margin_factor)
```

### 4.4 Long/Short Ratio Estimation

```python
def estimate_long_short_ratio(funding_rate: float) -> tuple:
    """
    Estimate long/short ratio from funding rate.
    
    Positive funding = more longs (longs pay shorts)
    Negative funding = more shorts (shorts pay longs)
    
    Returns:
        (long_ratio, short_ratio)
    """
    if funding_rate > 0.0005:
        return (0.60, 0.40)  # 60% longs
    elif funding_rate > 0.0002:
        return (0.55, 0.45)
    elif funding_rate < -0.0005:
        return (0.40, 0.60)  # 60% shorts
    elif funding_rate < -0.0002:
        return (0.45, 0.55)
    else:
        return (0.50, 0.50)  # Balanced
```

### 4.5 Complete Estimation Algorithm

```python
def estimate_liquidation_heatmap(
    current_price: float,
    oi_usd: float,
    funding_rate: float,
    price_range_pct: float = 0.20  # ±20% from current
) -> dict:
    """
    Estimate liquidation levels.
    
    Returns:
        {
            'long_liquidations': {price_level: usd_value},
            'short_liquidations': {price_level: usd_value}
        }
    """
    # Estimate long/short split
    long_ratio, short_ratio = estimate_long_short_ratio(funding_rate)
    long_oi = oi_usd * long_ratio
    short_oi = oi_usd * short_ratio
    
    # Price bounds
    min_price = current_price * (1 - price_range_pct)
    max_price = current_price * (1 + price_range_pct)
    
    long_liqs = {}   # Below current price
    short_liqs = {}  # Above current price
    
    for leverage, weight in LEVERAGE_DISTRIBUTION.items():
        # LONG liquidations (below current)
        long_liq_price = calculate_liquidation_price(current_price, leverage, is_long=True)
        
        if min_price <= long_liq_price < current_price:
            level = round(long_liq_price / 1000) * 1000  # Round to $1000
            estimated_usd = long_oi * weight
            long_liqs[level] = long_liqs.get(level, 0) + estimated_usd
        
        # SHORT liquidations (above current)
        short_liq_price = calculate_liquidation_price(current_price, leverage, is_long=False)
        
        if current_price < short_liq_price <= max_price:
            level = round(short_liq_price / 1000) * 1000
            estimated_usd = short_oi * weight
            short_liqs[level] = short_liqs.get(level, 0) + estimated_usd
    
    return {
        'long_liquidations': long_liqs,
        'short_liquidations': short_liqs,
        'total_long_at_risk': sum(long_liqs.values()),
        'total_short_at_risk': sum(short_liqs.values()),
        'data_type': 'ESTIMATED',
        'disclaimer': 'Calculated from OI + leverage assumptions. Not actual pending liquidations.'
    }
```

---

## 5. Database Schema (Supabase PostgreSQL)

### 5.1 Connection Details

```python
# Environment Variable
DATABASE_URL = "postgresql://postgres.qmvaypguppkusxfngrxa:[PASSWORD]@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

# Use Transaction Pooler (Port 6543) for IPv4 compatibility
```

### 5.2 Tables (Already Created)

```sql
-- Table 1: liquidations
-- Stores real-time liquidation events from WebSocket
CREATE TABLE liquidations (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,          -- 'LONG' or 'SHORT'
    price DECIMAL(20, 8) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    usd_value DECIMAL(20, 2) NOT NULL,
    price_level INTEGER NOT NULL,        -- Rounded to nearest $1000
    hour_bucket TIMESTAMPTZ NOT NULL,    -- Rounded to hour
    exchange VARCHAR(20) DEFAULT 'binance',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table 2: market_snapshots
-- Stores periodic OI/funding/depth data every 5 minutes
CREATE TABLE market_snapshots (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open_interest_usd DECIMAL(20, 2),
    spot_price DECIMAL(20, 8),
    perp_price DECIMAL(20, 8),
    funding_rate DECIMAL(20, 8),
    total_depth_usd DECIMAL(20, 2),
    fragility_score DECIMAL(5, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(symbol, timestamp)
);

-- Table 3: liquidation_aggregates
-- Pre-calculated aggregates for fast queries
CREATE TABLE liquidation_aggregates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price_level INTEGER NOT NULL,
    period_type VARCHAR(10) NOT NULL,    -- '1h', '4h', '24h', '7d'
    period_start TIMESTAMPTZ NOT NULL,
    long_liq_count INTEGER DEFAULT 0,
    long_liq_usd DECIMAL(20, 2) DEFAULT 0,
    short_liq_count INTEGER DEFAULT 0,
    short_liq_usd DECIMAL(20, 2) DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(symbol, price_level, period_type, period_start)
);

-- Table 4: system_logs
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level VARCHAR(10) NOT NULL,
    component VARCHAR(50) NOT NULL,
    message TEXT
);
```

### 5.3 Database Operations

```python
import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta


class LiquidationDatabase:
    """PostgreSQL database manager for Supabase."""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.pool = psycopg2.pool.ThreadedConnectionPool(1, 10, self.database_url)
    
    def insert_liquidation(self, liq: dict):
        """Insert a liquidation event."""
        with self.pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO liquidations 
                    (timestamp, symbol, side, price, quantity, usd_value, price_level, hour_bucket)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    liq['timestamp'],
                    liq['symbol'],
                    liq['side'],
                    liq['price'],
                    liq['quantity'],
                    liq['usd_value'],
                    liq['price_level'],
                    liq['hour_bucket']
                ))
            conn.commit()
            self.pool.putconn(conn)
    
    def insert_snapshot(self, snapshot: dict):
        """Insert market snapshot."""
        with self.pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO market_snapshots 
                    (timestamp, symbol, open_interest_usd, spot_price, perp_price, 
                     funding_rate, total_depth_usd, fragility_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timestamp) DO UPDATE SET
                        open_interest_usd = EXCLUDED.open_interest_usd,
                        fragility_score = EXCLUDED.fragility_score
                """, (
                    snapshot['timestamp'],
                    snapshot['symbol'],
                    snapshot['open_interest_usd'],
                    snapshot['spot_price'],
                    snapshot['perp_price'],
                    snapshot['funding_rate'],
                    snapshot['total_depth_usd'],
                    snapshot['fragility_score']
                ))
            conn.commit()
            self.pool.putconn(conn)
    
    def get_liquidation_heatmap(self, symbol: str, hours: int = 24) -> dict:
        """Get realized liquidations aggregated by price level."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Long liquidations
                cur.execute("""
                    SELECT price_level, SUM(usd_value) as total_usd, COUNT(*) as count
                    FROM liquidations
                    WHERE symbol = %s AND side = 'LONG' AND timestamp >= %s
                    GROUP BY price_level
                    ORDER BY price_level DESC
                """, (symbol, since))
                long_rows = cur.fetchall()
                
                # Short liquidations
                cur.execute("""
                    SELECT price_level, SUM(usd_value) as total_usd, COUNT(*) as count
                    FROM liquidations
                    WHERE symbol = %s AND side = 'SHORT' AND timestamp >= %s
                    GROUP BY price_level
                    ORDER BY price_level DESC
                """, (symbol, since))
                short_rows = cur.fetchall()
            
            self.pool.putconn(conn)
        
        return {
            'long_liquidations': {row['price_level']: float(row['total_usd']) for row in long_rows},
            'short_liquidations': {row['price_level']: float(row['total_usd']) for row in short_rows},
            'data_type': 'REALIZED',
            'period_hours': hours
        }
    
    def get_latest_snapshot(self, symbol: str) -> dict:
        """Get most recent market snapshot."""
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM market_snapshots
                    WHERE symbol = %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (symbol,))
                row = cur.fetchone()
            self.pool.putconn(conn)
        
        return dict(row) if row else None
```

---

## 6. WebSocket Liquidation Collector

### 6.1 Implementation

```python
import json
import threading
import websocket
from datetime import datetime
import time


class LiquidationCollector:
    """
    Collect real-time liquidations from Binance WebSocket.
    Store in PostgreSQL database.
    """
    
    WEBSOCKET_URL = "wss://fstream.binance.com/ws/!forceOrder@arr"
    
    def __init__(self, database, symbols=None):
        """
        Args:
            database: LiquidationDatabase instance
            symbols: List of symbols to track (None = all)
        """
        self.db = database
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        self.running = False
        self.ws = None
        
        # Buffer for batch inserts
        self._buffer = []
        self._buffer_lock = threading.Lock()
        self._last_flush = time.time()
        self.BUFFER_SIZE = 50
        self.FLUSH_INTERVAL = 10  # seconds
    
    def _process_message(self, ws, message):
        """Process incoming WebSocket message."""
        try:
            data = json.loads(message)
            
            if 'o' not in data:
                return
            
            order = data['o']
            symbol = order['s']
            
            # Filter by symbols
            if symbol not in self.symbols:
                return
            
            # Parse liquidation
            price = float(order['p'])
            quantity = float(order['q'])
            timestamp = datetime.fromtimestamp(order['T'] / 1000)
            
            # Determine side
            # SELL = Long was liquidated (forced to sell)
            # BUY = Short was liquidated (forced to buy)
            side = 'LONG' if order['S'] == 'SELL' else 'SHORT'
            
            liq = {
                'timestamp': timestamp,
                'symbol': symbol,
                'side': side,
                'price': price,
                'quantity': quantity,
                'usd_value': price * quantity,
                'price_level': round(price / 1000) * 1000,
                'hour_bucket': timestamp.replace(minute=0, second=0, microsecond=0)
            }
            
            # Add to buffer
            with self._buffer_lock:
                self._buffer.append(liq)
            
            # Print for monitoring
            emoji = '🔴' if side == 'LONG' else '🟢'
            print(f"{emoji} {side} LIQ: {symbol} ${liq['usd_value']:,.0f} @ ${price:,.0f}")
            
            # Check if should flush
            self._check_flush()
            
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def _check_flush(self):
        """Check if buffer should be flushed to database."""
        should_flush = False
        
        with self._buffer_lock:
            if len(self._buffer) >= self.BUFFER_SIZE:
                should_flush = True
            elif time.time() - self._last_flush > self.FLUSH_INTERVAL:
                should_flush = True
        
        if should_flush:
            self._flush_buffer()
    
    def _flush_buffer(self):
        """Flush buffer to database."""
        with self._buffer_lock:
            if not self._buffer:
                return
            
            buffer_copy = self._buffer.copy()
            self._buffer = []
            self._last_flush = time.time()
        
        # Insert to database
        for liq in buffer_copy:
            try:
                self.db.insert_liquidation(liq)
            except Exception as e:
                print(f"Error inserting liquidation: {e}")
        
        print(f"💾 Flushed {len(buffer_copy)} liquidations to database")
    
    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status, close_msg):
        print(f"WebSocket closed: {close_status}")
        
        # Auto-reconnect
        if self.running:
            print("Reconnecting in 5 seconds...")
            time.sleep(5)
            self._connect()
    
    def _on_open(self, ws):
        print("✅ Connected to Binance Liquidation Stream")
    
    def _connect(self):
        """Create and connect WebSocket."""
        self.ws = websocket.WebSocketApp(
            self.WEBSOCKET_URL,
            on_message=self._process_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        self.ws.run_forever()
    
    def start(self, background=True):
        """Start collecting liquidations."""
        self.running = True
        
        if background:
            thread = threading.Thread(target=self._connect, daemon=True)
            thread.start()
            print("🚀 Started liquidation collector in background")
        else:
            self._connect()
    
    def stop(self):
        """Stop collecting."""
        self.running = False
        if self.ws:
            self.ws.close()
        self._flush_buffer()  # Final flush
        print("🛑 Liquidation collector stopped")
```

---

## 7. Snapshot Collector (Periodic Data)

### 7.1 Implementation

```python
import requests
import threading
import time
from datetime import datetime


class SnapshotCollector:
    """
    Collect market snapshots (OI, funding, depth) periodically.
    Calculate and store fragility score.
    """
    
    BINANCE_FUTURES = "https://fapi.binance.com"
    BINANCE_SPOT = "https://api.binance.com"
    
    def __init__(self, database, symbols=None, interval_minutes=5):
        self.db = database
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        self.interval = interval_minutes * 60
        self.running = False
    
    def _fetch_data(self, symbol: str) -> dict:
        """Fetch all data for a symbol from Binance."""
        try:
            # Open Interest
            oi_resp = requests.get(
                f"{self.BINANCE_FUTURES}/fapi/v1/openInterest",
                params={"symbol": symbol}, timeout=10
            )
            oi_contracts = float(oi_resp.json()['openInterest'])
            
            # Prices
            perp_resp = requests.get(
                f"{self.BINANCE_FUTURES}/fapi/v1/ticker/price",
                params={"symbol": symbol}, timeout=10
            )
            perp_price = float(perp_resp.json()['price'])
            
            spot_resp = requests.get(
                f"{self.BINANCE_SPOT}/api/v3/ticker/price",
                params={"symbol": symbol}, timeout=10
            )
            spot_price = float(spot_resp.json()['price'])
            
            # Funding Rate
            funding_resp = requests.get(
                f"{self.BINANCE_FUTURES}/fapi/v1/premiumIndex",
                params={"symbol": symbol}, timeout=10
            )
            funding_rate = float(funding_resp.json()['lastFundingRate'])
            
            # Funding History (for F_sigma calculation)
            funding_hist_resp = requests.get(
                f"{self.BINANCE_FUTURES}/fapi/v1/fundingRate",
                params={"symbol": symbol, "limit": 21}, timeout=10
            )
            funding_history = [float(r['fundingRate']) for r in funding_hist_resp.json()]
            
            # Order Book Depth
            depth_resp = requests.get(
                f"{self.BINANCE_FUTURES}/fapi/v1/depth",
                params={"symbol": symbol, "limit": 1000}, timeout=10
            )
            depth_data = depth_resp.json()
            
            # Calculate metrics
            oi_usd = oi_contracts * perp_price
            mid_price = (spot_price + perp_price) / 2
            depth_2pct = calculate_depth_2pct(depth_data['bids'], depth_data['asks'], mid_price)
            
            # Calculate Fragility Score
            L_d = calculate_L_d(oi_usd, depth_2pct)
            F_sigma = calculate_F_sigma(funding_rate, funding_history)
            B_z = calculate_B_z(spot_price, perp_price)
            fragility_score = (L_d + F_sigma + B_z) / 3
            
            return {
                'timestamp': datetime.utcnow(),
                'symbol': symbol,
                'open_interest_usd': oi_usd,
                'spot_price': spot_price,
                'perp_price': perp_price,
                'funding_rate': funding_rate,
                'total_depth_usd': depth_2pct,
                'fragility_score': fragility_score
            }
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def _collect_loop(self):
        """Main collection loop."""
        while self.running:
            for symbol in self.symbols:
                snapshot = self._fetch_data(symbol)
                
                if snapshot:
                    self.db.insert_snapshot(snapshot)
                    
                    # Print status
                    phi = snapshot['fragility_score']
                    level = '🟢' if phi <= 25 else '🟡' if phi <= 50 else '🟠' if phi <= 75 else '🔴'
                    print(f"📊 {symbol} Φ={phi:.1f} {level} | OI=${snapshot['open_interest_usd']/1e9:.1f}B")
                
                time.sleep(1)  # Small delay between symbols
            
            # Wait for next interval
            time.sleep(self.interval)
    
    def start(self, background=True):
        """Start snapshot collection."""
        self.running = True
        
        if background:
            thread = threading.Thread(target=self._collect_loop, daemon=True)
            thread.start()
            print(f"🚀 Started snapshot collector (every {self.interval//60} min)")
        else:
            self._collect_loop()
    
    def stop(self):
        """Stop collection."""
        self.running = False
        print("🛑 Snapshot collector stopped")
```

---

## 8. Combined Output Format

### 8.1 Heatmap Display

```python
def format_heatmap_display(
    symbol: str,
    current_price: float,
    estimated: dict,
    realized: dict,
    fragility: float
) -> str:
    """Format combined heatmap for display."""
    
    # Fragility level
    if fragility <= 25:
        frag_emoji, frag_level = '🟢', 'Stable'
    elif fragility <= 50:
        frag_emoji, frag_level = '🟡', 'Caution'
    elif fragility <= 75:
        frag_emoji, frag_level = '🟠', 'Fragile'
    else:
        frag_emoji, frag_level = '🔴', 'Critical'
    
    output = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║  💥 {symbol} LIQUIDATION HEATMAP                                          ║
║  📊 Fragility (Φ): {fragility:.1f}/100 {frag_emoji} {frag_level:<10}                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ═══════════════ ESTIMATED SHORT LIQUIDATIONS (Above) ═══════════════   ║
║  ⚠️ Calculated from OI + leverage assumptions                            ║
║                                                                           ║
"""
    
    # Short liquidations (above current)
    shorts = sorted(estimated['short_liquidations'].items(), reverse=True)[:5]
    max_val = max([v for k, v in shorts]) if shorts else 1
    
    for price, usd in shorts:
        bar_len = int(usd / max_val * 30)
        bar = '█' * bar_len
        major = " 🔴 Major" if usd > estimated['total_short_at_risk'] * 0.25 else ""
        output += f"║  ${price/1000:>3.0f}k │ {bar:<30} │ ${usd/1e9:.2f}B{major:<10} ║\n"
    
    output += f"""║                                                                           ║
║              ─────────────▶ ${current_price:,.0f} CURRENT ◀─────────────             ║
║                                                                           ║
║  ═══════════════ ESTIMATED LONG LIQUIDATIONS (Below) ════════════════   ║
║                                                                           ║
"""
    
    # Long liquidations (below current)
    longs = sorted(estimated['long_liquidations'].items(), reverse=True)[:5]
    max_val = max([v for k, v in longs]) if longs else 1
    
    for price, usd in longs:
        bar_len = int(usd / max_val * 30)
        bar = '▓' * bar_len
        major = " 🔴 Major" if usd > estimated['total_long_at_risk'] * 0.25 else ""
        output += f"║  ${price/1000:>3.0f}k │ {bar:<30} │ ${usd/1e9:.2f}B{major:<10} ║\n"
    
    # Summary
    r_long = sum(realized.get('long_liquidations', {}).values())
    r_short = sum(realized.get('short_liquidations', {}).values())
    
    output += f"""║                                                                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║  📊 SUMMARY                                                               ║
║  ─────────────────────────────────────────────────────────────────────   ║
║  Estimated at Risk:  Longs ${estimated['total_long_at_risk']/1e9:.1f}B │ Shorts ${estimated['total_short_at_risk']/1e9:.1f}B            ║
║  Realized (24h):     Longs ${r_long/1e6:.0f}M │ Shorts ${r_short/1e6:.0f}M                ║
║                                                                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ⚠️  DISCLAIMER                                                           ║
║  "Estimated" = Calculated from OI + leverage assumptions                 ║
║  "Realized" = Actual liquidations from Binance WebSocket                 ║
║  This is NOT actual pending liquidation data like Coinglass              ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
    
    return output
```

### 8.2 JSON API Response

```python
def format_json_response(symbol: str, data: dict) -> dict:
    """Format data for API response."""
    return {
        'symbol': symbol,
        'timestamp': datetime.utcnow().isoformat(),
        'current_price': data['current_price'],
        
        'fragility': {
            'score': data['fragility_score'],
            'level': data['fragility_level'],
            'components': {
                'L_d': data['L_d'],
                'F_sigma': data['F_sigma'],
                'B_z': data['B_z']
            }
        },
        
        'estimated_liquidations': {
            'warning': 'ESTIMATED - Not actual pending liquidations',
            'short_above': [
                {'price': p, 'usd_value': v}
                for p, v in sorted(data['estimated']['short_liquidations'].items(), reverse=True)[:10]
            ],
            'long_below': [
                {'price': p, 'usd_value': v}
                for p, v in sorted(data['estimated']['long_liquidations'].items(), reverse=True)[:10]
            ],
            'total_long_at_risk': data['estimated']['total_long_at_risk'],
            'total_short_at_risk': data['estimated']['total_short_at_risk']
        },
        
        'realized_24h': {
            'long_liquidations': data['realized']['long_liquidations'],
            'short_liquidations': data['realized']['short_liquidations']
        },
        
        'data_sources': {
            'estimated': 'Calculated from OI + leverage distribution assumptions',
            'realized': 'Binance forceOrder WebSocket stream',
            'fragility': 'Calculated from OI, Funding Rate, and Basis'
        }
    }
```

---

## 9. Main Application

### 9.1 Entry Point

```python
"""
Liquidation Heatmap System
==========================
Main entry point for the application.

Usage:
    python main.py                  # Start full system
    python main.py --heatmap        # Show heatmap once
    python main.py --fragility      # Show fragility only
"""

import os
import time
import argparse
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description='Liquidation Heatmap System')
    parser.add_argument('--symbols', nargs='+', default=['BTCUSDT', 'ETHUSDT', 'SOLUSDT'])
    parser.add_argument('--heatmap', action='store_true', help='Show heatmap once')
    parser.add_argument('--fragility', action='store_true', help='Show fragility only')
    
    args = parser.parse_args()
    
    # Check DATABASE_URL
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL not set!")
        print("Set it with: export DATABASE_URL='postgresql://...'")
        return
    
    # Initialize
    db = LiquidationDatabase()
    
    if args.heatmap:
        # One-time heatmap display
        for symbol in args.symbols:
            snapshot = db.get_latest_snapshot(symbol)
            if snapshot:
                estimated = estimate_liquidation_heatmap(
                    snapshot['perp_price'],
                    snapshot['open_interest_usd'],
                    snapshot['funding_rate']
                )
                realized = db.get_liquidation_heatmap(symbol, hours=24)
                
                print(format_heatmap_display(
                    symbol,
                    snapshot['perp_price'],
                    estimated,
                    realized,
                    snapshot['fragility_score']
                ))
    
    elif args.fragility:
        # Fragility only
        for symbol in args.symbols:
            snapshot = db.get_latest_snapshot(symbol)
            if snapshot:
                phi = snapshot['fragility_score']
                level = '🟢' if phi <= 25 else '🟡' if phi <= 50 else '🟠' if phi <= 75 else '🔴'
                print(f"{symbol}: Φ = {phi:.1f}/100 {level}")
    
    else:
        # Full system
        print("🚀 Starting Liquidation Heatmap System...")
        print(f"   Symbols: {args.symbols}")
        
        # Start collectors
        liq_collector = LiquidationCollector(db, args.symbols)
        snap_collector = SnapshotCollector(db, args.symbols, interval_minutes=5)
        
        liq_collector.start(background=True)
        snap_collector.start(background=True)
        
        print("✅ System started. Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(60)
                
                # Periodic status
                print(f"\n📊 Status Update — {datetime.utcnow().strftime('%H:%M:%S UTC')}")
                for symbol in args.symbols:
                    snapshot = db.get_latest_snapshot(symbol)
                    if snapshot:
                        phi = snapshot['fragility_score']
                        level = '🟢' if phi <= 25 else '🟡' if phi <= 50 else '🟠' if phi <= 75 else '🔴'
                        print(f"   {symbol}: Φ={phi:.1f} {level}")
        
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            liq_collector.stop()
            snap_collector.stop()
            print("✅ System stopped.")


if __name__ == '__main__':
    main()
```

---

## 10. Requirements

### 10.1 Python Packages

```txt
# requirements.txt

# Database
psycopg2-binary>=2.9.0

# WebSocket
websocket-client>=1.4.0

# HTTP
requests>=2.28.0

# Numeric
numpy>=1.21.0

# Scheduling (optional)
schedule>=1.1.0
```

### 10.2 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://postgres.xxx:[PASSWORD]@xxx.pooler.supabase.com:6543/postgres

# Optional
SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT
SNAPSHOT_INTERVAL=300  # seconds
```

---

## 11. Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION CHECKLIST                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  COMPONENTS TO BUILD:                                                │
│                                                                      │
│  ☐ 1. Market Fragility Calculator (Φ)                               │
│       ├── calculate_L_d()                                           │
│       ├── calculate_F_sigma()                                       │
│       ├── calculate_B_z()                                           │
│       └── calculate_depth_2pct()                                    │
│                                                                      │
│  ☐ 2. Estimated Heatmap Calculator                                  │
│       ├── estimate_long_short_ratio()                               │
│       ├── calculate_liquidation_price()                             │
│       └── estimate_liquidation_heatmap()                            │
│                                                                      │
│  ☐ 3. Database Manager (PostgreSQL/Supabase)                        │
│       ├── insert_liquidation()                                      │
│       ├── insert_snapshot()                                         │
│       ├── get_liquidation_heatmap()                                 │
│       └── get_latest_snapshot()                                     │
│                                                                      │
│  ☐ 4. WebSocket Liquidation Collector                               │
│       ├── Connect to wss://fstream.binance.com                      │
│       ├── Parse liquidation messages                                │
│       ├── Buffer and batch insert                                   │
│       └── Auto-reconnect on disconnect                              │
│                                                                      │
│  ☐ 5. Snapshot Collector (every 5 min)                              │
│       ├── Fetch OI, Funding, Depth from Binance                     │
│       ├── Calculate Fragility Score                                 │
│       └── Store in database                                         │
│                                                                      │
│  ☐ 6. Output Formatters                                             │
│       ├── ASCII heatmap display                                     │
│       └── JSON API response                                         │
│                                                                      │
│  ☐ 7. Main Application                                              │
│       ├── CLI interface                                             │
│       ├── Start/stop collectors                                     │
│       └── Periodic status updates                                   │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  DATA FLOW:                                                          │
│                                                                      │
│  Binance REST API ──▶ Snapshot Collector ──▶ market_snapshots      │
│                           │                                          │
│                           ├──▶ Fragility Score (Φ)                  │
│                           └──▶ Estimated Heatmap                    │
│                                                                      │
│  Binance WebSocket ──▶ Liquidation Collector ──▶ liquidations      │
│                           │                                          │
│                           └──▶ Realized Heatmap                     │
│                                                                      │
│                                    │                                 │
│                                    ▼                                 │
│                           Combined Display                           │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  DEPLOYMENT:                                                         │
│  ├── Render.com (Free tier)                                         │
│  ├── Supabase PostgreSQL (Free tier, already setup)                │
│  └── DATABASE_URL in environment variables                          │
│                                                                      │
│  COST: $0/month                                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

**End of Specification**

*Document prepared for Kimi Development Team*  
*Orbix Invest — February 2026*
