# Update KEY LEVELS & CDC SIGNAL with Order Block Detection

## Overview

Update the KEY LEVELS section to use **Order Block (OB) detection** for Support and Resistance levels instead of static/pivot-based calculations.

**Order Block (Smart Money Concept):**
- **Bullish OB** = Last RED candle before significant UP move → **SUPPORT zone**
- **Bearish OB** = Last GREEN candle before significant DOWN move → **RESISTANCE zone**

---

## Current Problem

The current S/R levels are too close together and don't reflect real price action:

```
Current (Wrong):
BTC $68,097
R1: $68,276  (+0.26%)  ← Too close, not meaningful
R2: $68,455  (+0.52%)
S1: $67,864  (-0.34%)
S2: $67,630  (-0.69%)
```

---

## New Layout with Order Blocks

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📊 KEY LEVELS & CDC SIGNAL                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐       │
│  │  ₿ BTC          $68,097     │  │  Ξ ETH          $1,976      │       │
│  │                             │  │                             │       │
│  │  CDC Signal: 🔴 BEARISH     │  │  CDC Signal: 🔴 BEARISH     │       │
│  │                             │  │                             │       │
│  │  🔴 R2  $72,150             │  │  🔴 R2  $2,180              │       │
│  │  🔴 R1  $70,200             │  │  🔴 R1  $2,050              │       │
│  │  ── ▶ $68,097 ──            │  │  ── ▶ $1,976 ──             │       │
│  │  🟢 S1  $65,400             │  │  🟢 S1  $1,880              │       │
│  │  🟢 S2  $62,800             │  │  🟢 S2  $1,750              │       │
│  │                             │  │                             │       │
│  │  📉 -7.7% from ATH          │  │  📉 -59.5% from ATH         │       │
│  └─────────────────────────────┘  └─────────────────────────────┘       │
│                                                                          │
│  ℹ️ S/R levels based on Order Block detection (Smart Money Concept)     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoint

```javascript
// BTC Daily Candles (60 days for OB detection)
GET https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=60

// ETH Daily Candles
GET https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1d&limit=60
```

**Response format:**
```javascript
[
  [
    1499040000000,      // [0] Open time
    "0.01634000",       // [1] Open
    "0.80000000",       // [2] High
    "0.01575800",       // [3] Low
    "0.01577100",       // [4] Close
    "148976.11427815",  // [5] Volume
    ...
  ]
]
```

---

## Order Block Detection Logic

```javascript
async function getOrderBlockLevels(symbol) {
  // ═══════════════════════════════════════════════════════════════
  // STEP 1: Fetch Daily Candles
  // ═══════════════════════════════════════════════════════════════
  
  const response = await fetch(
    `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1d&limit=60`
  );
  const data = await response.json();
  
  // Parse candles
  const candles = data.map(k => ({
    timestamp: k[0],
    open: parseFloat(k[1]),
    high: parseFloat(k[2]),
    low: parseFloat(k[3]),
    close: parseFloat(k[4]),
    volume: parseFloat(k[5])
  }));
  
  // ═══════════════════════════════════════════════════════════════
  // STEP 2: Calculate Average Volume (for filtering)
  // ═══════════════════════════════════════════════════════════════
  
  const avgVolume = candles.reduce((sum, c) => sum + c.volume, 0) / candles.length;
  
  // ═══════════════════════════════════════════════════════════════
  // STEP 3: Detect Order Blocks
  // ═══════════════════════════════════════════════════════════════
  
  const threshold = 0.03;  // 3% move required to qualify
  const volumeMultiplier = 1.2;  // Volume must be 1.2x average
  const lookforward = 3;  // Check next 3 candles for the move
  const maxAge = 30;  // Only consider OBs from last 30 days
  
  const bullishOBs = [];  // Will become SUPPORT
  const bearishOBs = [];  // Will become RESISTANCE
  
  for (let i = 1; i < candles.length - lookforward; i++) {
    const current = candles[i];
    const nextCandles = candles.slice(i + 1, i + 1 + lookforward);
    
    // Calculate max move after this candle
    const maxHigh = Math.max(...nextCandles.map(c => c.high));
    const minLow = Math.min(...nextCandles.map(c => c.low));
    
    const moveUp = (maxHigh - current.close) / current.close;
    const moveDown = (current.close - minLow) / current.close;
    
    // Candle characteristics
    const isBearishCandle = current.close < current.open;  // Red candle
    const isBullishCandle = current.close > current.open;  // Green candle
    const hasSignificantVolume = current.volume >= avgVolume * volumeMultiplier;
    
    // ─────────────────────────────────────────────────────────────
    // BULLISH ORDER BLOCK
    // Definition: Last RED candle before significant UP move
    // This zone becomes SUPPORT
    // ─────────────────────────────────────────────────────────────
    if (isBearishCandle && moveUp >= threshold && hasSignificantVolume) {
      bullishOBs.push({
        type: 'BULLISH_OB',
        top: current.high,
        bottom: current.low,
        mid: (current.high + current.low) / 2,
        strength: moveUp,
        volumeRatio: current.volume / avgVolume,
        timestamp: current.timestamp,
        age: candles.length - i
      });
    }
    
    // ─────────────────────────────────────────────────────────────
    // BEARISH ORDER BLOCK
    // Definition: Last GREEN candle before significant DOWN move
    // This zone becomes RESISTANCE
    // ─────────────────────────────────────────────────────────────
    if (isBullishCandle && moveDown >= threshold && hasSignificantVolume) {
      bearishOBs.push({
        type: 'BEARISH_OB',
        top: current.high,
        bottom: current.low,
        mid: (current.high + current.low) / 2,
        strength: moveDown,
        volumeRatio: current.volume / avgVolume,
        timestamp: current.timestamp,
        age: candles.length - i
      });
    }
  }
  
  // ═══════════════════════════════════════════════════════════════
  // STEP 4: Filter & Sort to Get Nearest Levels
  // ═══════════════════════════════════════════════════════════════
  
  const currentPrice = candles[candles.length - 1].close;
  
  // SUPPORT: Bullish OBs BELOW current price (unmitigated)
  // Use the TOP of the OB zone as the support level
  const supports = bullishOBs
    .filter(ob => ob.top < currentPrice && ob.age <= maxAge)
    .sort((a, b) => b.top - a.top)  // Highest first (nearest to price)
    .slice(0, 2);
  
  // RESISTANCE: Bearish OBs ABOVE current price (unmitigated)
  // Use the BOTTOM of the OB zone as the resistance level
  const resistances = bearishOBs
    .filter(ob => ob.bottom > currentPrice && ob.age <= maxAge)
    .sort((a, b) => a.bottom - b.bottom)  // Lowest first (nearest to price)
    .slice(0, 2);
  
  // ═══════════════════════════════════════════════════════════════
  // STEP 5: Return Formatted Levels
  // ═══════════════════════════════════════════════════════════════
  
  return {
    currentPrice,
    
    // Resistance levels (above price)
    R1: resistances[0] ? {
      price: resistances[0].bottom,
      zone: { top: resistances[0].top, bottom: resistances[0].bottom },
      strength: resistances[0].strength,
      age: resistances[0].age
    } : null,
    
    R2: resistances[1] ? {
      price: resistances[1].bottom,
      zone: { top: resistances[1].top, bottom: resistances[1].bottom },
      strength: resistances[1].strength,
      age: resistances[1].age
    } : null,
    
    // Support levels (below price)
    S1: supports[0] ? {
      price: supports[0].top,
      zone: { top: supports[0].top, bottom: supports[0].bottom },
      strength: supports[0].strength,
      age: supports[0].age
    } : null,
    
    S2: supports[1] ? {
      price: supports[1].top,
      zone: { top: supports[1].top, bottom: supports[1].bottom },
      strength: supports[1].strength,
      age: supports[1].age
    } : null
  };
}
```

---

## Fallback: If No Order Blocks Found

If no valid Order Blocks are detected within the criteria, fall back to psychological levels:

```javascript
function getFallbackLevels(currentPrice, symbol) {
  // Round to appropriate base
  let roundBase;
  if (symbol === 'BTCUSDT') {
    roundBase = 5000;  // Round to nearest $5,000 for BTC
  } else if (symbol === 'ETHUSDT') {
    roundBase = 100;   // Round to nearest $100 for ETH
  } else {
    roundBase = currentPrice > 100 ? 10 : 1;
  }
  
  const nearest = Math.round(currentPrice / roundBase) * roundBase;
  
  return {
    R1: { price: nearest + roundBase, zone: null },
    R2: { price: nearest + roundBase * 2, zone: null },
    S1: { price: nearest - roundBase, zone: null },
    S2: { price: nearest - roundBase * 2, zone: null },
    isFallback: true
  };
}
```

---

## Complete Function

```javascript
async function getKeyLevels(symbol) {
  try {
    const obLevels = await getOrderBlockLevels(symbol);
    
    // Check if we found valid levels
    const hasResistance = obLevels.R1 !== null;
    const hasSupport = obLevels.S1 !== null;
    
    if (!hasResistance || !hasSupport) {
      // Merge OB levels with fallback
      const fallback = getFallbackLevels(obLevels.currentPrice, symbol);
      
      return {
        currentPrice: obLevels.currentPrice,
        R1: obLevels.R1 || fallback.R1,
        R2: obLevels.R2 || fallback.R2,
        S1: obLevels.S1 || fallback.S1,
        S2: obLevels.S2 || fallback.S2,
        source: 'mixed'
      };
    }
    
    return {
      ...obLevels,
      source: 'orderblock'
    };
    
  } catch (error) {
    console.error('Error fetching Order Block levels:', error);
    
    // Full fallback
    const currentPrice = await getCurrentPrice(symbol);
    return {
      ...getFallbackLevels(currentPrice, symbol),
      currentPrice,
      source: 'fallback'
    };
  }
}
```

---

## React Component Update

```jsx
function KeyLevelsCard({ symbol, name, icon }) {
  const [data, setData] = useState(null);
  const [cdcSignal, setCdcSignal] = useState(null);
  
  useEffect(() => {
    async function fetchData() {
      const levels = await getKeyLevels(symbol);
      const cdc = await getCDCSignal(symbol);
      setData(levels);
      setCdcSignal(cdc);
    }
    fetchData();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [symbol]);
  
  if (!data) return <LoadingSpinner />;
  
  const athPrice = symbol === 'BTCUSDT' ? 73800 : 4878;  // Historical ATH
  const athDistance = ((data.currentPrice - athPrice) / athPrice * 100).toFixed(1);
  
  return (
    <div className="key-levels-card">
      {/* Header */}
      <div className="card-header">
        <span className="icon">{icon}</span>
        <span className="symbol">{name}</span>
        <span className="price">${data.currentPrice.toLocaleString()}</span>
      </div>
      
      {/* CDC Signal */}
      <div className={`cdc-signal ${cdcSignal.signal.toLowerCase()}`}>
        <span>CDC Signal:</span>
        <span className="signal-badge">
          {cdcSignal.emoji} {cdcSignal.signal}
        </span>
      </div>
      
      {/* Levels */}
      <div className="levels-list">
        {/* Resistances */}
        {data.R2 && (
          <div className="level resistance r2">
            <span className="dot">🔴</span>
            <span className="label">R2</span>
            <span className="price">${data.R2.price.toLocaleString()}</span>
          </div>
        )}
        {data.R1 && (
          <div className="level resistance r1">
            <span className="dot">🔴</span>
            <span className="label">R1</span>
            <span className="price">${data.R1.price.toLocaleString()}</span>
          </div>
        )}
        
        {/* Current Price Marker */}
        <div className="current-price-marker">
          <span>▶</span>
          <span>${data.currentPrice.toLocaleString()}</span>
          <span>◀</span>
        </div>
        
        {/* Supports */}
        {data.S1 && (
          <div className="level support s1">
            <span className="dot">🟢</span>
            <span className="label">S1</span>
            <span className="price">${data.S1.price.toLocaleString()}</span>
          </div>
        )}
        {data.S2 && (
          <div className="level support s2">
            <span className="dot">🟢</span>
            <span className="label">S2</span>
            <span className="price">${data.S2.price.toLocaleString()}</span>
          </div>
        )}
      </div>
      
      {/* ATH Distance */}
      <div className="ath-distance">
        <span>📉</span>
        <span>{athDistance}% from ATH</span>
      </div>
    </div>
  );
}
```

---

## CSS Styling

```css
.key-levels-card {
  background: #1a1a2e;
  border: 1px solid #2a2a3e;
  border-radius: 12px;
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.card-header .symbol {
  font-weight: 600;
  color: #ffffff;
}

.card-header .price {
  margin-left: auto;
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  font-family: 'JetBrains Mono', monospace;
}

/* CDC Signal */
.cdc-signal {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  color: #888888;
}

.signal-badge {
  font-weight: 600;
}

.cdc-signal.bullish .signal-badge {
  color: #00ff88;
}

.cdc-signal.bearish .signal-badge {
  color: #ff4444;
}

.cdc-signal.neutral .signal-badge {
  color: #ffaa00;
}

/* Levels List */
.levels-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.level {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
}

.level .dot {
  font-size: 0.8rem;
}

.level .label {
  width: 30px;
  font-weight: 600;
  font-size: 0.85rem;
}

.level.resistance .label {
  color: #ff4444;
}

.level.support .label {
  color: #00ff88;
}

.level .price {
  margin-left: auto;
  font-family: 'JetBrains Mono', monospace;
  color: #cccccc;
}

/* Current Price Marker */
.current-price-marker {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  color: #00d4ff;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  border-top: 1px dashed #2a2a3e;
  border-bottom: 1px dashed #2a2a3e;
  margin: 8px 0;
}

/* ATH Distance */
.ath-distance {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #ff6b6b;
}
```

---

## Footnote

Add a small footnote below the two cards explaining the methodology:

```jsx
<div className="levels-footnote">
  ℹ️ S/R levels based on Order Block detection (Smart Money Concept)
</div>
```

```css
.levels-footnote {
  text-align: center;
  font-size: 0.75rem;
  color: #666666;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #2a2a3e;
}
```

---

## Summary

| Before | After |
|--------|-------|
| S/R from unknown formula | S/R from Order Block detection |
| Levels too close (~$200 apart) | Meaningful levels (~$2,000+ apart) |
| Not actionable | Real Smart Money zones |
| No explanation | Footnote explaining methodology |

---

## Update Frequency

- Refresh every **5 minutes** (daily candles don't change often)
- Or refresh when user manually clicks refresh button

---

## Testing Checklist

- [ ] Order Blocks detected correctly on BTC
- [ ] Order Blocks detected correctly on ETH
- [ ] Fallback works when no OBs found
- [ ] Levels are displayed in correct order (R2 > R1 > Current > S1 > S2)
- [ ] CDC Signal still works correctly
- [ ] ATH distance calculated correctly
- [ ] Footnote displayed
