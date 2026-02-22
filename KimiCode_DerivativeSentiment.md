# Update: Rename "Whale Activity" to "DERIVATIVE SENTIMENT"

## Overview

Replace the current "Whale Activity" section (hardcoded data) with **"DERIVATIVE SENTIMENT"** using real-time data from Binance Futures API.

**Coins covered:** BTC, ETH, SOL (same as Funding Rates section)

---

## Current vs New

| Current (Whale Activity) | New (Derivative Sentiment) |
|--------------------------|----------------------------|
| Hardcoded data | Real-time Binance Futures API |
| BTC only | BTC + ETH + SOL |
| "Exchange Flow" (no source) | Long/Short Ratio (verifiable) |
| Unclear signal | Clear signal logic |

---

## New Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📊 DERIVATIVE SENTIMENT                                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  OPEN INTEREST                                                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐            │
│  │ BTC             │ │ ETH             │ │ SOL             │            │
│  │ $5.58B          │ │ $2.10B          │ │ $0.85B          │            │
│  │ ↓ -3.2% (24h)   │ │ ↓ -1.8% (24h)   │ │ ↑ +2.1% (24h)   │            │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘            │
│                                                                          │
│  POSITIONING                                                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │         │  Retail L/S      │  Top Traders     │  Taker Buy/Sell  │  │
│  │  ───────┼──────────────────┼──────────────────┼─────────────────  │  │
│  │  BTC    │  🟢 52.3% Long   │  🔴 45.9% Long   │  58.2% Buy       │  │
│  │  ETH    │  🟢 55.1% Long   │  🔴 48.8% Long   │  52.1% Buy       │  │
│  │  SOL    │  🟢 61.2% Long   │  🟢 52.3% Long   │  64.5% Buy       │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Signal: 🟡 SQUEEZE SETUP                                         │  │
│  │  Retail heavily long but smart money shorting BTC/ETH             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Binance Futures API Endpoints (FREE)

### 1. Open Interest (Current)

```javascript
// BTC Open Interest
GET https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT

// ETH Open Interest
GET https://fapi.binance.com/fapi/v1/openInterest?symbol=ETHUSDT

// SOL Open Interest
GET https://fapi.binance.com/fapi/v1/openInterest?symbol=SOLUSDT

// Response:
{
  "symbol": "BTCUSDT",
  "openInterest": "82500.123",  // in coin units (BTC)
  "time": 1703980800000
}
```

### 2. Open Interest History (for 24h change)

```javascript
// OI History - use 5m intervals, limit 288 = 24 hours
GET https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=5m&limit=288
GET https://fapi.binance.com/futures/data/openInterestHist?symbol=ETHUSDT&period=5m&limit=288
GET https://fapi.binance.com/futures/data/openInterestHist?symbol=SOLUSDT&period=5m&limit=288

// Response:
[
  {
    "symbol": "BTCUSDT",
    "sumOpenInterest": "82000.50",      // in coin
    "sumOpenInterestValue": "5580000000", // in USD
    "timestamp": 1703894400000
  },
  ...
]
```

### 3. Long/Short Ratio (Retail - All Accounts)

```javascript
// Global Long/Short Account Ratio
GET https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=1
GET https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=ETHUSDT&period=1h&limit=1
GET https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=SOLUSDT&period=1h&limit=1

// Response:
{
  "symbol": "BTCUSDT",
  "longShortRatio": "1.0965",   // > 1 = more accounts long
  "longAccount": "0.5230",      // 52.30% of accounts are long
  "shortAccount": "0.4770",     // 47.70% of accounts are short
  "timestamp": 1703980800000
}
```

### 4. Top Traders Long/Short (Smart Money)

```javascript
// Top Trader Long/Short Ratio (by position value)
GET https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol=BTCUSDT&period=1h&limit=1
GET https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol=ETHUSDT&period=1h&limit=1
GET https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol=SOLUSDT&period=1h&limit=1

// Response:
{
  "symbol": "BTCUSDT",
  "longShortRatio": "0.8475",   // < 1 = top traders shorting
  "longAccount": "0.4590",      // 45.90% long
  "shortAccount": "0.5410",     // 54.10% short
  "timestamp": 1703980800000
}
```

### 5. Taker Buy/Sell Volume

```javascript
// Taker Buy/Sell Volume Ratio
GET https://fapi.binance.com/futures/data/takerlongshortRatio?symbol=BTCUSDT&period=1h&limit=1
GET https://fapi.binance.com/futures/data/takerlongshortRatio?symbol=ETHUSDT&period=1h&limit=1
GET https://fapi.binance.com/futures/data/takerlongshortRatio?symbol=SOLUSDT&period=1h&limit=1

// Response:
{
  "buySellRatio": "1.3920",     // > 1 = more aggressive buying
  "buyVol": "12500.50",         // taker buy volume
  "sellVol": "8980.23",         // taker sell volume
  "timestamp": 1703980800000
}
```

---

## Implementation

### Data Fetching

```javascript
const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'];
const SYMBOL_DISPLAY = {
  'BTCUSDT': 'BTC',
  'ETHUSDT': 'ETH',
  'SOLUSDT': 'SOL'
};

async function fetchDerivativeSentiment() {
  const results = {};
  
  for (const symbol of SYMBOLS) {
    const [oi, oiHistory, retailLS, topTraderLS, takerVolume, price] = await Promise.all([
      fetchOpenInterest(symbol),
      fetchOIHistory(symbol),
      fetchRetailLongShort(symbol),
      fetchTopTraderLongShort(symbol),
      fetchTakerBuySell(symbol),
      fetchCurrentPrice(symbol)
    ]);
    
    // Calculate OI in USD
    const oiUSD = parseFloat(oi.openInterest) * price;
    
    // Calculate 24h OI change
    const oiNow = parseFloat(oiHistory[oiHistory.length - 1].sumOpenInterestValue);
    const oi24hAgo = parseFloat(oiHistory[0].sumOpenInterestValue);
    const oiChange24h = ((oiNow - oi24hAgo) / oi24hAgo) * 100;
    
    // Parse Long/Short ratios
    const retailLong = parseFloat(retailLS.longAccount) * 100;
    const topTraderLong = parseFloat(topTraderLS.longAccount) * 100;
    
    // Parse Taker Buy percentage
    const takerBuyRatio = parseFloat(takerVolume.buySellRatio);
    const takerBuyPercent = (takerBuyRatio / (takerBuyRatio + 1)) * 100;
    
    results[symbol] = {
      symbol: SYMBOL_DISPLAY[symbol],
      openInterest: oiUSD,
      oiChange24h: oiChange24h,
      retailLongPercent: retailLong,
      topTraderLongPercent: topTraderLong,
      takerBuyPercent: takerBuyPercent
    };
  }
  
  // Generate overall signal
  const signal = generateSignal(results);
  
  return {
    data: results,
    signal: signal,
    timestamp: Date.now()
  };
}

// Individual fetch functions
async function fetchOpenInterest(symbol) {
  const res = await fetch(`https://fapi.binance.com/fapi/v1/openInterest?symbol=${symbol}`);
  return res.json();
}

async function fetchOIHistory(symbol) {
  const res = await fetch(`https://fapi.binance.com/futures/data/openInterestHist?symbol=${symbol}&period=5m&limit=288`);
  return res.json();
}

async function fetchRetailLongShort(symbol) {
  const res = await fetch(`https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=${symbol}&period=1h&limit=1`);
  const data = await res.json();
  return data[0];
}

async function fetchTopTraderLongShort(symbol) {
  const res = await fetch(`https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol=${symbol}&period=1h&limit=1`);
  const data = await res.json();
  return data[0];
}

async function fetchTakerBuySell(symbol) {
  const res = await fetch(`https://fapi.binance.com/futures/data/takerlongshortRatio?symbol=${symbol}&period=1h&limit=1`);
  const data = await res.json();
  return data[0];
}

async function fetchCurrentPrice(symbol) {
  const res = await fetch(`https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`);
  const data = await res.json();
  return parseFloat(data.price);
}
```

---

## Signal Logic

```javascript
function generateSignal(data) {
  const btc = data['BTCUSDT'];
  const eth = data['ETHUSDT'];
  const sol = data['SOLUSDT'];
  
  // ═══════════════════════════════════════════════════════════════
  // Analyze divergence between Retail and Top Traders
  // ═══════════════════════════════════════════════════════════════
  
  // BTC Analysis
  const btcRetailBias = btc.retailLongPercent > 52 ? 'LONG' : btc.retailLongPercent < 48 ? 'SHORT' : 'NEUTRAL';
  const btcWhaleBias = btc.topTraderLongPercent > 52 ? 'LONG' : btc.topTraderLongPercent < 48 ? 'SHORT' : 'NEUTRAL';
  const btcDivergence = (btcRetailBias === 'LONG' && btcWhaleBias === 'SHORT') || 
                        (btcRetailBias === 'SHORT' && btcWhaleBias === 'LONG');
  
  // ETH Analysis
  const ethRetailBias = eth.retailLongPercent > 52 ? 'LONG' : eth.retailLongPercent < 48 ? 'SHORT' : 'NEUTRAL';
  const ethWhaleBias = eth.topTraderLongPercent > 52 ? 'LONG' : eth.topTraderLongPercent < 48 ? 'SHORT' : 'NEUTRAL';
  const ethDivergence = (ethRetailBias === 'LONG' && ethWhaleBias === 'SHORT') || 
                        (ethRetailBias === 'SHORT' && ethWhaleBias === 'LONG');
  
  // SOL Analysis
  const solRetailBias = sol.retailLongPercent > 52 ? 'LONG' : sol.retailLongPercent < 48 ? 'SHORT' : 'NEUTRAL';
  const solWhaleBias = sol.topTraderLongPercent > 52 ? 'LONG' : sol.topTraderLongPercent < 48 ? 'SHORT' : 'NEUTRAL';
  const solDivergence = (solRetailBias === 'LONG' && solWhaleBias === 'SHORT') || 
                        (solRetailBias === 'SHORT' && solWhaleBias === 'LONG');
  
  // ═══════════════════════════════════════════════════════════════
  // Overall OI trend
  // ═══════════════════════════════════════════════════════════════
  
  const avgOIChange = (btc.oiChange24h + eth.oiChange24h + sol.oiChange24h) / 3;
  const oiIncreasing = avgOIChange > 1;
  const oiDecreasing = avgOIChange < -1;
  
  // ═══════════════════════════════════════════════════════════════
  // Determine Signal
  // ═══════════════════════════════════════════════════════════════
  
  // 🟢 BULLISH ACCUMULATION
  // Whales long + OI increasing + Buyers aggressive
  if (btcWhaleBias === 'LONG' && ethWhaleBias === 'LONG' && oiIncreasing) {
    return {
      signal: 'ACCUMULATION',
      emoji: '🟢',
      color: 'green',
      description: 'Smart money accumulating — OI rising with long bias'
    };
  }
  
  // 🔴 DISTRIBUTION
  // Whales short + OI decreasing
  if (btcWhaleBias === 'SHORT' && ethWhaleBias === 'SHORT' && oiDecreasing) {
    return {
      signal: 'DISTRIBUTION',
      emoji: '🔴',
      color: 'red',
      description: 'Smart money distributing — OI falling with short bias'
    };
  }
  
  // 🟡 SQUEEZE SETUP
  // Major divergence between retail and whales
  if (btcDivergence || ethDivergence) {
    const squeezeType = btcRetailBias === 'LONG' ? 'SHORT SQUEEZE' : 'LONG SQUEEZE';
    return {
      signal: 'SQUEEZE SETUP',
      emoji: '🟡',
      color: 'yellow',
      description: `Retail vs Smart Money divergence — potential ${squeezeType}`
    };
  }
  
  // 🔵 LEVERAGE FLUSH
  // Extreme retail positioning (>60% one side) + OI dropping
  const extremeRetailLong = btc.retailLongPercent > 60 || eth.retailLongPercent > 60;
  const extremeRetailShort = btc.retailLongPercent < 40 || eth.retailLongPercent < 40;
  if ((extremeRetailLong || extremeRetailShort) && oiDecreasing) {
    return {
      signal: 'LEVERAGE FLUSH',
      emoji: '🔵',
      color: 'blue',
      description: 'Extreme positioning + falling OI — liquidations likely'
    };
  }
  
  // ⚪ NEUTRAL
  return {
    signal: 'NEUTRAL',
    emoji: '⚪',
    color: 'gray',
    description: 'No clear derivative sentiment bias'
  };
}
```

---

## React Component

```jsx
function DerivativeSentiment() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadData() {
      try {
        const result = await fetchDerivativeSentiment();
        setData(result);
      } catch (error) {
        console.error('Error fetching derivative sentiment:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
    
    // Refresh every 5 minutes
    const interval = setInterval(loadData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);
  
  if (loading) return <LoadingSpinner />;
  if (!data) return <ErrorMessage message="Failed to load data" />;
  
  const { data: sentimentData, signal } = data;
  const coins = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'];
  
  return (
    <div className="derivative-sentiment-card">
      {/* Header */}
      <div className="card-header">
        <span className="icon">📊</span>
        <span className="title">DERIVATIVE SENTIMENT</span>
      </div>
      
      {/* Open Interest Row */}
      <div className="section-label">Open Interest</div>
      <div className="oi-grid">
        {coins.map(symbol => {
          const coin = sentimentData[symbol];
          const isPositive = coin.oiChange24h >= 0;
          return (
            <div key={symbol} className="oi-card">
              <div className="coin-name">{coin.symbol}</div>
              <div className="oi-value">${formatBillions(coin.openInterest)}</div>
              <div className={`oi-change ${isPositive ? 'positive' : 'negative'}`}>
                {isPositive ? '↑' : '↓'} {Math.abs(coin.oiChange24h).toFixed(1)}% (24h)
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Positioning Table */}
      <div className="section-label">Positioning</div>
      <div className="positioning-table">
        <div className="table-header">
          <div className="col-coin"></div>
          <div className="col-retail">Retail L/S</div>
          <div className="col-whales">Top Traders</div>
          <div className="col-taker">Taker Buy/Sell</div>
        </div>
        
        {coins.map(symbol => {
          const coin = sentimentData[symbol];
          const retailBullish = coin.retailLongPercent >= 50;
          const whalesBullish = coin.topTraderLongPercent >= 50;
          
          return (
            <div key={symbol} className="table-row">
              <div className="col-coin">{coin.symbol}</div>
              <div className={`col-retail ${retailBullish ? 'bullish' : 'bearish'}`}>
                {retailBullish ? '🟢' : '🔴'} {coin.retailLongPercent.toFixed(1)}% Long
              </div>
              <div className={`col-whales ${whalesBullish ? 'bullish' : 'bearish'}`}>
                {whalesBullish ? '🟢' : '🔴'} {coin.topTraderLongPercent.toFixed(1)}% Long
              </div>
              <div className="col-taker">
                {coin.takerBuyPercent.toFixed(1)}% Buy
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Signal Box */}
      <div 
        className="signal-box"
        style={{ 
          borderColor: getSignalColor(signal.color),
          backgroundColor: getSignalBgColor(signal.color)
        }}
      >
        <div className="signal-header">
          <span className="signal-label">Signal:</span>
          <span className="signal-value">{signal.emoji} {signal.signal}</span>
        </div>
        <div className="signal-description">{signal.description}</div>
      </div>
    </div>
  );
}

// Helper functions
function formatBillions(value) {
  if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B';
  if (value >= 1e6) return (value / 1e6).toFixed(0) + 'M';
  return value.toFixed(0);
}

function getSignalColor(color) {
  const colors = {
    green: '#00ff88',
    red: '#ff4444',
    yellow: '#ffaa00',
    blue: '#00d4ff',
    gray: '#666666'
  };
  return colors[color] || colors.gray;
}

function getSignalBgColor(color) {
  const colors = {
    green: 'rgba(0, 255, 136, 0.1)',
    red: 'rgba(255, 68, 68, 0.1)',
    yellow: 'rgba(255, 170, 0, 0.1)',
    blue: 'rgba(0, 212, 255, 0.1)',
    gray: 'rgba(102, 102, 102, 0.1)'
  };
  return colors[color] || colors.gray;
}
```

---

## CSS Styling

```css
.derivative-sentiment-card {
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

.card-header .icon {
  font-size: 1.2rem;
}

.card-header .title {
  font-weight: 600;
  font-size: 1rem;
  color: #ffffff;
}

/* Section Label */
.section-label {
  font-size: 0.75rem;
  color: #666666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  margin-top: 16px;
}

.section-label:first-of-type {
  margin-top: 0;
}

/* Open Interest Grid */
.oi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.oi-card {
  background: #12121a;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.oi-card .coin-name {
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 4px;
}

.oi-card .oi-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
  font-family: 'JetBrains Mono', monospace;
}

.oi-card .oi-change {
  font-size: 0.8rem;
  margin-top: 4px;
}

.oi-card .oi-change.positive {
  color: #00ff88;
}

.oi-card .oi-change.negative {
  color: #ff4444;
}

/* Positioning Table */
.positioning-table {
  background: #12121a;
  border-radius: 8px;
  overflow: hidden;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 60px 1fr 1fr 1fr;
  padding: 10px 12px;
  align-items: center;
}

.table-header {
  background: #0a0a0f;
  font-size: 0.75rem;
  color: #666666;
  text-transform: uppercase;
}

.table-row {
  border-top: 1px solid #2a2a3e;
  font-size: 0.85rem;
}

.col-coin {
  font-weight: 600;
  color: #ffffff;
}

.col-retail,
.col-whales,
.col-taker {
  color: #cccccc;
}

.col-retail.bullish,
.col-whales.bullish {
  color: #00ff88;
}

.col-retail.bearish,
.col-whales.bearish {
  color: #ff4444;
}

/* Signal Box */
.signal-box {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid;
}

.signal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.signal-label {
  color: #888888;
  font-size: 0.85rem;
}

.signal-value {
  font-weight: 700;
  color: #ffffff;
}

.signal-description {
  font-size: 0.8rem;
  color: #aaaaaa;
}

/* Responsive */
@media (max-width: 600px) {
  .oi-grid {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 50px 1fr 1fr;
  }
  
  .col-taker {
    display: none;
  }
}
```

---

## Signal Reference

| Signal | Emoji | Condition | Meaning |
|--------|-------|-----------|---------|
| **ACCUMULATION** | 🟢 | Whales long + OI rising | Smart money buying |
| **DISTRIBUTION** | 🔴 | Whales short + OI falling | Smart money selling |
| **SQUEEZE SETUP** | 🟡 | Retail vs Whale divergence | Potential squeeze incoming |
| **LEVERAGE FLUSH** | 🔵 | Extreme retail + OI falling | Liquidation cascade likely |
| **NEUTRAL** | ⚪ | No clear pattern | Wait and monitor |

---

## Update Frequency

| Data | Endpoint | Refresh |
|------|----------|---------|
| Open Interest | `/fapi/v1/openInterest` | Every 5 min |
| OI History | `/futures/data/openInterestHist` | Every 5 min |
| Retail L/S | `/futures/data/globalLongShortAccountRatio` | Every 5 min |
| Top Traders L/S | `/futures/data/topLongShortPositionRatio` | Every 5 min |
| Taker Buy/Sell | `/futures/data/takerlongshortRatio` | Every 5 min |

---

## Testing Checklist

- [ ] OI displays correctly for BTC, ETH, SOL
- [ ] 24h OI change calculated correctly
- [ ] Retail Long/Short % displays correctly
- [ ] Top Traders Long/Short % displays correctly
- [ ] Taker Buy/Sell % displays correctly
- [ ] Signal logic generates correct signals
- [ ] Colors match signal type
- [ ] Responsive design works on mobile
- [ ] Data refreshes every 5 minutes
