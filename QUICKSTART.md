# 🚀 Crypto Dashboard - Quick Start Guide

## Project Overview

A **beautiful, production-ready** Crypto Market Dashboard featuring:
- **Cyberpunk Trading Terminal** UI design
- **Macro Tide** analysis with B1 scoring
- **Crypto Pulse** monitoring (Fear & Greed, Funding, Whale Activity)
- **Sector Rotation** signals for 8 crypto sectors
- **Action Items** generator with prioritized recommendations

## 📁 Project Structure

```
crypto_dashboard/
├── backend/              # FastAPI Python backend
│   ├── main.py          # API entry point
│   ├── config/          # Settings & sector definitions
│   ├── data/            # Data fetchers & scheduler
│   ├── scoring/         # All scoring modules
│   ├── analysis/        # Action generator
│   └── api/routes/      # API endpoints
├── frontend/            # React + Vite + Tailwind
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/  # UI components
│   │   └── styles/      # Global CSS
│   └── package.json
├── requirements.txt     # Python dependencies
├── start.py            # Launch script
└── README.md
```

## 🏃 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd frontend
npm install
cd ..

# Start both backend and frontend
python start.py
```

### Option 2: Manual Startup

Terminal 1 - Backend:
```bash
cd backend
python main.py
# API runs on http://localhost:8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
# Dashboard runs on http://localhost:3000
```

## 🌐 Access URLs

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |

## 📊 Data Update Schedule

| Module | Frequency | Priority |
|--------|-----------|----------|
| Macro Tide | Every 6 hours | High |
| Fear & Greed | Every 6 hours | High |
| Funding Rates | Every 8 hours | High |
| Crypto Prices | Every 1 hour | Medium |
| Sector Momentum | Every 1 hour | Medium |
| Fragility Metrics | Every 15 min | Medium |

## 🎨 Design Features

- **Dark Cyberpunk Theme** with neon accents
- **Real-time Updates** every 60 seconds
- **Responsive Layout** (Desktop, Tablet, Mobile)
- **Animated Components** with smooth transitions
- **Color-coded Signals** (🟢 Bullish, 🔴 Bearish, 🟡 Neutral)

## 🔧 Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Optional: Get a free FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html

## 📝 Key API Endpoints

- `GET /api/full` - Complete dashboard data
- `GET /api/macro` - Macro tide (B1 scoring)
- `GET /api/crypto-pulse` - Fear & Greed, Funding, etc.
- `GET /api/sectors` - Sector rotation data
- `GET /api/actions` - Prioritized action items

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python 3.9+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start:**
- Check Node.js 18+ is installed: `node --version`
- Install dependencies: `cd frontend && npm install`

**No data showing:**
- Check internet connection
- Verify API is running: http://localhost:8000/api/health
- Check browser console for errors

## 📦 What's Included

### Backend Modules
- ✅ FRED macro data fetcher (NFCI, HY Spread, etc.)
- ✅ Binance/OKX crypto data with fallback
- ✅ B1 Scoring system with liquidity leak detection
- ✅ Momentum scoring (absolute + relative vs BTC)
- ✅ Fragility calculation
- ✅ Funding rate analysis
- ✅ Whale activity tracking
- ✅ Sector rotation logic
- ✅ Action item generator
- ✅ APScheduler for periodic updates

### Frontend Components
- ✅ Cyberpunk trading terminal UI
- ✅ Macro Tide visualization
- ✅ Fear & Greed gauge
- ✅ Market fragility scores
- ✅ Funding rates display
- ✅ Whale activity monitor
- ✅ Sector rotation table
- ✅ Action items list

## ⚠️ Disclaimer

This dashboard is for **informational purposes only**. Not financial advice. Always do your own research before making investment decisions.

---

Built with ❤️ using FastAPI + React + Tailwind CSS
