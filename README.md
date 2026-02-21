# Crypto Market Dashboard v2.0

A beautiful, real-time crypto market monitoring dashboard with macro analysis, sector rotation signals, and actionable trading insights.

![Dashboard Preview](preview.png)

## Features

### 📊 Section 1: Macro Tide (B1 Scoring)
- **NFCI** (Chicago Fed National Financial Conditions Index)
- **HY Spread** (High Yield Credit Spread)
- **MOVE Index** (Rate Volatility)
- **Cu/Au Ratio** (Growth Signal)
- **Net Liquidity** (Fed Balance Sheet - TGA - RRP)
- **Liquidity Leak Monitor** (Fiscal Dominance, Gold Cannibalization, Policy Lag)

### 💓 Section 2: Crypto Pulse
- **Fear & Greed Index** with bottom/top probability signals
- **Market Fragility** Score (BTC, ETH, SOL)
- **Funding Rates** Analysis with squeeze detection
- **Whale Activity** Tracking (OI, Exchange Flows)

### 🔄 Section 3: Sector Rotation
- **8 Sectors**: AI, DeFi, L1, Privacy, L2, RWA, Meme, PERP
- **Momentum Scoring** (0-100) based on absolute + relative performance vs BTC
- **Rotation Signals**: ROTATE IN, WATCH, NEUTRAL, AVOID, ROTATE OUT
- **Recommended Allocation** based on macro conditions

### 🎯 Section 4: Action Items
- Prioritized actions (HIGH, MEDIUM, LOW)
- Context-aware recommendations
- Risk management alerts

## Architecture

```
crypto_dashboard/
├── backend/                    # FastAPI + Python
│   ├── main.py                # API entry point
│   ├── config/                # Settings, sectors
│   ├── data/                  # Data fetching & scheduler
│   │   ├── fetchers/          # Binance, OKX, FRED, Fear&Greed
│   │   ├── aggregator.py      # Multi-source with fallback
│   │   └── scheduler.py       # Periodic updates
│   ├── scoring/               # All scoring modules
│   │   ├── macro_tide.py      # B1 scoring
│   │   ├── momentum.py        # Momentum calculation
│   │   ├── fragility.py       # Fragility score
│   │   ├── funding.py         # Funding analysis
│   │   ├── whale.py           # Whale activity
│   │   └── sector_rotation.py # Sector logic
│   ├── analysis/              # Action generator
│   └── api/routes/            # API endpoints
│
├── frontend/                   # React + Vite + Tailwind
│   ├── src/
│   │   ├── App.jsx            # Main app
│   │   ├── components/        # UI components
│   │   │   ├── macro/         # MacroTide
│   │   │   ├── crypto/        # CryptoPulse components
│   │   │   ├── sectors/       # SectorRotation
│   │   │   ├── actions/       # ActionItems
│   │   │   └── layout/        # Header, Footer
│   │   └── styles/            # Global CSS
│   └── package.json
│
└── requirements.txt
```

## Quick Start

### 1. Install Dependencies

```bash
# Backend
cd crypto_dashboard
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Run the Application

```bash
# Terminal 1: Start Backend
cd backend
python main.py

# Terminal 2: Start Frontend (dev mode)
cd frontend
npm run dev
```

### 3. Access Dashboard

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/api/health

## Data Update Schedule

| Data Type | Update Frequency | Priority |
|-----------|-----------------|----------|
| Macro Tide | Every 6 hours | High |
| Fear & Greed | Every 6 hours | High |
| Funding Rates | Every 8 hours | High |
| Crypto Prices | Every 1 hour | Medium |
| Sector Momentum | Every 1 hour | Medium |
| Fragility Metrics | Every 15 min | Medium |

## API Endpoints

- `GET /api/full` - Complete dashboard data
- `GET /api/macro` - Macro tide data
- `GET /api/crypto-pulse` - Crypto pulse data
- `GET /api/sectors` - Sector rotation data
- `GET /api/actions` - Action items
- `GET /api/health` - Health check

## Design Philosophy

> **"Less is More, but What's There Must Be Actionable"**

- Every metric drives a decision
- No vanity metrics or noise
- Clear visual hierarchy: Macro → Crypto → Sector → Action
- Real-time where it matters, delayed where acceptable

## Tech Stack

**Backend:**
- FastAPI (async Python web framework)
- APScheduler (periodic tasks)
- aiohttp (async HTTP client)
- pandas (data manipulation)

**Frontend:**
- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- Recharts (charts)
- Lucide React (icons)

**Data Sources:**
- Binance (primary crypto data)
- OKX (fallback)
- FRED (macro data)
- Alternative.me (Fear & Greed)

## Color Palette (Cyberpunk Trading Terminal)

```css
--bg-primary: #0a0a0f
--bg-secondary: #12121a
--bg-card: #1a1a2e
--accent-green: #00ff88
--accent-red: #ff4444
--accent-yellow: #ffaa00
--accent-orange: #ff6b35
--accent-cyan: #00d4ff
--accent-purple: #9d4edd
```

## License

MIT License - Not financial advice.
