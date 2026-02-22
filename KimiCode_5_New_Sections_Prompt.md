# Add 5 New Sections to Crypto Dashboard

Please add these 5 new sections to the existing dashboard:

---

## SECTION 1: KEY LEVELS & CDC SIGNAL

Add a section showing BTC and ETH with CDC indicator and key levels.

### Layout:
```
┌─────────────────────────────────────────────────────────────────────────┐
│  📊 KEY LEVELS & CDC SIGNAL                                             │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐       │
│  │  ₿ BTC          $68,072     │  │  Ξ ETH          $1,976      │       │
│  │                             │  │                             │       │
│  │  CDC Signal: 🟢 BULLISH     │  │  CDC Signal: 🟢 BULLISH     │       │
│  │                             │  │                             │       │
│  │  🔴 R2  $75,000             │  │  🔴 R2  $2,200              │       │
│  │  🔴 R1  $72,000             │  │  🔴 R1  $2,100              │       │
│  │  ── ▶ $68,072 ──            │  │  ── ▶ $1,976 ──             │       │
│  │  🟢 S1  $65,000             │  │  🟢 S1  $1,900              │       │
│  │  🟢 S2  $60,000             │  │  🟢 S2  $1,800              │       │
│  │                             │  │                             │       │
│  │  📉 -15.2% from ATH         │  │  📉 -59.4% from ATH         │       │
│  └─────────────────────────────┘  └─────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

### CDC Signal Logic (IMPORTANT):

```javascript
function getCDCSignal(currentPrice, closePrices) {
  const ema12 = calculateEMA(closePrices, 12);
  const ema26 = calculateEMA(closePrices, 26);
  
  const currentEMA12 = ema12[ema12.length - 1];
  const currentEMA26 = ema26[ema26.length - 1];
  
  // 🟢 BULLISH: Price > EMA12 AND Price > EMA26 AND EMA12 > EMA26
  if (currentPrice > currentEMA12 && 
      currentPrice > currentEMA26 && 
      currentEMA12 > currentEMA26) {
    return { signal: 'BULLISH', emoji: '🟢', color: 'green' };
  }
  
  // 🔴 BEARISH: Price < EMA12 AND Price < EMA26 AND EMA12 < EMA26
  if (currentPrice < currentEMA12 && 
      currentPrice < currentEMA26 && 
      currentEMA12 < currentEMA26) {
    return { signal: 'BEARISH', emoji: '🔴', color: 'red' };
  }
  
  // 🟡 NEUTRAL: Mixed conditions
  return { signal: 'NEUTRAL', emoji: '🟡', color: 'yellow' };
}

function calculateEMA(prices, period) {
  const multiplier = 2 / (period + 1);
  let ema = [prices[0]];
  for (let i = 1; i < prices.length; i++) {
    ema.push((prices[i] - ema[i-1]) * multiplier + ema[i-1]);
  }
  return ema;
}
```

### API:
```
GET https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=50
GET https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1d&limit=50
GET https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT
GET https://api.binance.com/api/v3/ticker/24hr?symbol=ETHUSDT
```

### Display:
- Only show "CDC Signal: 🟢 BULLISH" or "CDC Signal: 🔴 BEARISH"
- Do NOT show EMA values or spread percentage
- Show key levels (R2, R1, S1, S2) and distance from ATH

---

## SECTION 2: BTC LIQUIDATION HEATMAP

### Layout:
```
┌─────────────────────────────────────────────────────────────────────────┐
│  💥 BTC LIQUIDATION HEATMAP                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ─────────────── SHORT LIQUIDATIONS (Above) ───────────────             │
│                                                                          │
│  $75,000  ██████████████████████████  $1.8B  🔴 Major cluster           │
│  $72,000  ████████████████░░░░░░░░░░  $1.2B                             │
│  $70,000  ██████████░░░░░░░░░░░░░░░░  $650M                             │
│                                                                          │
│  ════════════════ ▶ $68,072 CURRENT ◀ ════════════════                  │
│                                                                          │
│  $66,000  ████████████░░░░░░░░░░░░░░  $720M                             │
│  $65,000  ██████████████████░░░░░░░░  $1.1B                             │
│  $62,000  ██████████████████████████  $2.1B  🔴 Major cluster           │
│  $60,000  ████████████████████████████████  $2.8B  💀 Wall              │
│                                                                          │
│  ─────────────── LONG LIQUIDATIONS (Below) ────────────────             │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────┐            │
│  │  ⚠️ Nearest: $65,000 (LONGS) — $1.1B at risk           │            │
│  │  📊 Longs: $6.7B | Shorts: $3.6B                        │            │
│  └─────────────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Source:
```
CoinGlass API: https://open-api.coinglass.com/public/v2/liquidation_map
Alternative: https://www.coinglass.com/LiquidationData
```

### Labels:
| Amount | Label |
|--------|-------|
| > $2.5B | 💀 Liquidation wall |
| $1.5B - $2.5B | 🔴 Major cluster |
| < $1.5B | (no label) |

---

## SECTION 3: STABLECOIN FLOW MONITOR

### Layout:
```
┌─────────────────────────────────────────────────────────────────────────┐
│  💵 STABLECOIN FLOW MONITOR                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  USDT    $143.2B    ↑ +$1.5B (7d)    🟢 MINTING                        │
│  ██████████████████████████████████████████████░░░░░░░░░░              │
│                                                                          │
│  USDC    $52.8B     ↑ +$0.9B (7d)    🟢 MINTING                        │
│  █████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░              │
│                                                                          │
│  DAI     $5.2B      ↓ -$0.1B (7d)    🔴 REDEEMING                      │
│  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░              │
│                                                                          │
│  Total:  $201.2B    ↑ +$2.3B (7d)                                       │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │  📊 🟢 Bullish: Stablecoins minting = New capital        │           │
│  │     entering crypto                                       │           │
│  └──────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

### API (DefiLlama only):
```
GET https://stablecoins.llama.fi/stablecoins?includePrices=true
```

### Code:
```javascript
async function fetchStablecoinData() {
  const response = await fetch('https://stablecoins.llama.fi/stablecoins?includePrices=true');
  const data = await response.json();
  
  const targetSymbols = ['USDT', 'USDC', 'DAI'];
  
  const stablecoins = data.peggedAssets
    .filter(s => targetSymbols.includes(s.symbol))
    .map(s => {
      const currentSupply = s.circulating?.peggedUSD || 0;
      const prevWeekSupply = s.circulatingPrevWeek?.peggedUSD || currentSupply;
      const change7d = currentSupply - prevWeekSupply;
      
      return {
        symbol: s.symbol,
        supply: currentSupply,
        change7d: change7d,
        status: change7d >= 0 ? 'MINTING' : 'REDEEMING',
        emoji: change7d >= 0 ? '🟢' : '🔴'
      };
    })
    .sort((a, b) => b.supply - a.supply);
  
  const totalSupply = stablecoins.reduce((sum, s) => sum + s.supply, 0);
  const totalChange7d = stablecoins.reduce((sum, s) => sum + s.change7d, 0);
  
  return { stablecoins, totalSupply, totalChange7d };
}
```

### Insight Logic:
- totalChange7d > 0 → 🟢 "Stablecoins minting = New capital entering crypto"
- totalChange7d < 0 → 🔴 "Stablecoins redeeming = Capital exiting crypto"

---

## SECTION 4: ECONOMIC CALENDAR

### Layout:
```
┌─────────────────────────────────────────────────────────────────────────┐
│  📅 ECONOMIC CALENDAR (Next 7 Days)                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  🏛️ MACRO EVENTS                                                        │
│  ────────────────────────────────────────────────────────────────────   │
│  Feb 23 Sun │ 19:00 │ 🇺🇸 Fed Minutes Release       │ 🔴 HIGH          │
│  Feb 25 Tue │ 15:00 │ 🇺🇸 Consumer Confidence       │ 🟡 MEDIUM        │
│  Feb 27 Thu │ 13:30 │ 🇺🇸 GDP Q4 (2nd Est.)         │ 🔴 HIGH          │
│  Feb 28 Fri │ 13:30 │ 🇺🇸 PCE Inflation             │ 🔴 CRITICAL      │
│                                                                          │
│  🪙 CRYPTO EVENTS                                                        │
│  ────────────────────────────────────────────────────────────────────   │
│  Feb 24 Mon │ 🔓 ARB Token Unlock ($45M)            │ 🔴 Bearish ARB   │
│  Feb 26 Wed │ 🔓 APT Token Unlock ($82M)            │ 🔴 Bearish APT   │
│  Feb 28 Fri │ 📊 BTC Monthly Options Expiry         │ 🟡 Volatility    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │  ⚠️ KEY EVENT: Feb 28 — PCE Inflation                    │           │
│  │  Core PCE is Fed's preferred measure.                    │           │
│  │  Hot print = hawkish Fed = risk-off for crypto           │           │
│  └──────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data:
- Macro events: Use static JSON (update weekly)
- Crypto events: TokenUnlocks API `https://token.unlocks.app/api/v1/unlocks`

### Static JSON Example:
```javascript
const MACRO_EVENTS = [
  { date: '2026-02-23', time: '19:00', event: 'Fed Minutes Release', flag: '🇺🇸', impact: '🔴 HIGH' },
  { date: '2026-02-25', time: '15:00', event: 'Consumer Confidence', flag: '🇺🇸', impact: '🟡 MEDIUM' },
  { date: '2026-02-27', time: '13:30', event: 'GDP Q4 (2nd Est.)', flag: '🇺🇸', impact: '🔴 HIGH' },
  { date: '2026-02-28', time: '13:30', event: 'PCE Inflation', flag: '🇺🇸', impact: '🔴 CRITICAL', isKeyEvent: true }
];
```

---

## SECTION 5: CORRELATION MATRIX & PAXG/BTC

### Layout:
```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔗 CORRELATION MATRIX & PAXG/BTC                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  BTC CORRELATION (30D Rolling)                                          │
│  ────────────────────────────────────────────────────────────────────   │
│  vs S&P 500    +0.72  ████████████████████░░░░░  High Positive         │
│  vs NASDAQ     +0.78  █████████████████████░░░░  Very High             │
│  vs Gold       -0.15  ██████████░░░░░░░░░░░░░░░  Diverging             │
│  vs DXY        -0.45  ███████░░░░░░░░░░░░░░░░░░  Inverse               │
│                                                                          │
│  📊 Insight: BTC trading as high-beta tech/risk asset                   │
│                                                                          │
│  ────────────────────────────────────────────────────────────────────   │
│                                                                          │
│  🪙 PAXG/BTC RATIO                                                      │
│  ────────────────────────────────────────────────────────────────────   │
│  Current:    0.07234                                                    │
│  24h:        ↑ +1.25%                                                   │
│  7d:         ↑ +3.42%                                                   │
│  30d:        ↑ +8.15%                                                   │
│                                                                          │
│  Trend: 🟡 GOLD OUTPERFORMING BTC                                       │
│                                                                          │
│  [═══════════════════════════════════════════] Mini 30d Chart           │
│                                                                          │
│  🛡️ BitGold Signal: Consider defensive allocation                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### API:

**PAXG/BTC from Binance:**
```
GET https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGBTC
GET https://api.binance.com/api/v3/klines?symbol=PAXGBTC&interval=1d&limit=30
```

**Traditional Assets (Yahoo Finance via backend proxy):**
```javascript
// Create backend endpoint to avoid CORS
app.get('/api/yahoo-proxy', async (req, res) => {
  const { symbol } = req.query;
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?range=1mo&interval=1d`;
  const response = await fetch(url);
  const data = await response.json();
  res.json({ closes: data.chart.result[0].indicators.quote[0].close });
});

// Symbols:
// S&P 500: ^GSPC
// NASDAQ: ^IXIC
// Gold: GC=F
// DXY: DX-Y.NYB
```

### PAXG/BTC Code:
```javascript
async function fetchPAXGBTC() {
  const tickerRes = await fetch('https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGBTC');
  const ticker = await tickerRes.json();
  
  const klinesRes = await fetch('https://api.binance.com/api/v3/klines?symbol=PAXGBTC&interval=1d&limit=30');
  const klines = await klinesRes.json();
  
  const closes = klines.map(k => parseFloat(k[4]));
  const current = closes[closes.length - 1];
  const week = closes[closes.length - 7];
  const month = closes[0];
  
  const change7d = ((current - week) / week) * 100;
  const change30d = ((current - month) / month) * 100;
  
  // Trend logic
  let trend;
  if (change7d > 2 && change30d > 5) {
    trend = { signal: 'GOLD OUTPERFORMING BTC', emoji: '🟡', bitgold: '🛡️ Consider defensive allocation' };
  } else if (change7d < -2 && change30d < -5) {
    trend = { signal: 'BTC OUTPERFORMING GOLD', emoji: '🟢', bitgold: '🚀 Maintain BTC allocation' };
  } else {
    trend = { signal: 'NEUTRAL', emoji: '⚪', bitgold: '⚖️ Follow CDC signal' };
  }
  
  return {
    currentRatio: current,
    change24h: parseFloat(ticker.priceChangePercent),
    change7d,
    change30d,
    chartData: closes,
    trend
  };
}
```

### Correlation Code:
```javascript
function calculateCorrelation(x, y) {
  const n = Math.min(x.length, y.length);
  const xSlice = x.slice(-n);
  const ySlice = y.slice(-n);
  
  const meanX = xSlice.reduce((a, b) => a + b, 0) / n;
  const meanY = ySlice.reduce((a, b) => a + b, 0) / n;
  
  let num = 0, denomX = 0, denomY = 0;
  for (let i = 0; i < n; i++) {
    const dx = xSlice[i] - meanX;
    const dy = ySlice[i] - meanY;
    num += dx * dy;
    denomX += dx * dx;
    denomY += dy * dy;
  }
  
  return num / Math.sqrt(denomX * denomY);
}

function getCorrelationLabel(corr) {
  if (corr >= 0.7) return 'Very High';
  if (corr >= 0.5) return 'High Positive';
  if (corr >= 0.3) return 'Moderate';
  if (corr >= -0.3) return 'Weak';
  if (corr >= -0.5) return 'Inverse';
  return 'Strong Inverse';
}
```

### Insight Logic:
```javascript
function generateInsight(correlations) {
  if (correlations.nasdaq > 0.6) return '📊 BTC trading as high-beta tech/risk asset';
  if (correlations.dxy < -0.4) return '💵 BTC inversely correlated with USD';
  if (correlations.gold > 0.4) return '🥇 BTC moving with Gold as store-of-value';
  return '📈 Mixed correlations — monitor for regime shift';
}
```

---

## API SUMMARY

| Section | Source | Endpoint |
|---------|--------|----------|
| CDC Signal | Binance | `/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=50` |
| CDC Signal | Binance | `/api/v3/klines?symbol=ETHUSDT&interval=1d&limit=50` |
| PAXG/BTC | Binance | `/api/v3/ticker/24hr?symbol=PAXGBTC` |
| PAXG/BTC Klines | Binance | `/api/v3/klines?symbol=PAXGBTC&interval=1d&limit=30` |
| Stablecoins | DefiLlama | `https://stablecoins.llama.fi/stablecoins?includePrices=true` |
| Liquidation | CoinGlass | `https://open-api.coinglass.com/public/v2/liquidation_map` |
| Token Unlocks | TokenUnlocks | `https://token.unlocks.app/api/v1/unlocks` |
| Traditional Assets | Yahoo | Via backend proxy |

---

## UPDATE FREQUENCY

| Section | Frequency |
|---------|-----------|
| CDC Signal | Every 5 min |
| Liquidation | Every 5 min |
| PAXG/BTC | Every 5 min |
| Stablecoin | Every 1 hour |
| Correlations | Every 1 hour |
| Calendar | Daily |
