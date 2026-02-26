# RRG Rotation Map — Technical Specification

**Document Type:** Software Development Specification  
**Project:** GIGA Mission Control — RRG Rotation Map Module  
**Version:** 1.0  
**Date:** February 2026  
**Author:** Orbix Invest Engineering Team

---

## 1. Executive Summary

### 1.1 Purpose

สร้าง **RRG (Relative Rotation Graph) Rotation Map** Dashboard ที่แสดง:
- Sector rotation ระหว่าง Risk Assets และ Safe Haven
- Market Regime detection (Risk-On / Risk-Off / Neutral)
- Investment recommendations พร้อม Top Picks

### 1.2 Data Source

```
Yahoo Finance API (Free)
├── Price data: Daily OHLCV
├── Symbols: 9 ETFs
└── Update frequency: Every 15 minutes during market hours
```

### 1.3 Key Deliverables

| Deliverable | Description |
|-------------|-------------|
| Backend API | FastAPI service with RRG calculation engine |
| Frontend UI | React component matching v3 design |
| Database | PostgreSQL (Supabase) for historical data |
| Scheduler | Cron job for periodic data fetching |

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐      ┌─────────────────────────────────────────────┐      │
│   │   Yahoo     │      │              BACKEND (FastAPI)              │      │
│   │   Finance   │─────▶│                                             │      │
│   │    API      │      │  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │      │
│   └─────────────┘      │  │  Data   │  │   RRG   │  │  Regime     │ │      │
│                        │  │ Fetcher │─▶│ Engine  │─▶│  Detector   │ │      │
│                        │  └─────────┘  └─────────┘  └─────────────┘ │      │
│                        │                      │                      │      │
│                        │                      ▼                      │      │
│                        │            ┌─────────────────┐             │      │
│                        │            │  Recommendation │             │      │
│                        │            │     Engine      │             │      │
│                        │            └─────────────────┘             │      │
│                        │                      │                      │      │
│                        └──────────────────────┼──────────────────────┘      │
│                                               │                              │
│                                               ▼                              │
│   ┌─────────────┐                    ┌───────────────┐      ┌───────────┐   │
│   │  Supabase   │◀───────────────────│   REST API    │─────▶│  Frontend │   │
│   │ PostgreSQL  │                    │   Endpoints   │      │   React   │   │
│   └─────────────┘                    └───────────────┘      └───────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Module Responsibilities

| Module | Responsibility | Single Responsibility |
|--------|---------------|----------------------|
| `DataFetcher` | Fetch prices from Yahoo Finance | Data acquisition only |
| `RRGEngine` | Calculate RS-Ratio & RS-Momentum | Math calculations only |
| `RegimeDetector` | Determine market regime | Classification only |
| `RecommendationEngine` | Generate buy/sell signals | Signal generation only |
| `APIRouter` | Handle HTTP requests | Request/Response only |
| `Database` | CRUD operations | Data persistence only |

---

## 3. Technology Stack

### 3.1 Backend

```yaml
Runtime: Python 3.11+
Framework: FastAPI 0.100+
Database: PostgreSQL 15 (Supabase)
ORM: SQLAlchemy 2.0 (async)
Scheduler: APScheduler
HTTP Client: httpx (async)
Validation: Pydantic v2
```

### 3.2 Frontend

```yaml
Framework: React 18
Language: TypeScript 5
Styling: Tailwind CSS
Charts: None (custom CSS visualization)
State: React Query (TanStack Query)
```

### 3.3 Infrastructure

```yaml
Backend Hosting: Render.com (Free tier)
Database: Supabase (Free tier)
Frontend: Vercel or same Render instance
```

---

## 4. Project Structure

### 4.1 Backend Structure

```
rrg-rotation-map/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration management
│   │
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── constants.py           # ETF symbols, thresholds
│   │   ├── enums.py               # Quadrant, Regime enums
│   │   └── exceptions.py          # Custom exceptions
│   │
│   ├── models/                    # Pydantic & SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── database.py            # SQLAlchemy models
│   │   ├── schemas.py             # Pydantic schemas (API)
│   │   └── domain.py              # Domain models (internal)
│   │
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   ├── data_fetcher.py        # Yahoo Finance data fetching
│   │   ├── rrg_engine.py          # RRG calculation engine
│   │   ├── regime_detector.py     # Market regime detection
│   │   └── recommendation.py      # Investment recommendations
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   └── price_repository.py    # Price data CRUD
│   │
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   ├── router.py              # Main router
│   │   ├── dependencies.py        # Dependency injection
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── rrg.py             # RRG endpoints
│   │       └── health.py          # Health check
│   │
│   └── scheduler/                 # Background jobs
│       ├── __init__.py
│       └── jobs.py                # Scheduled tasks
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── unit/
│   │   ├── test_rrg_engine.py
│   │   ├── test_regime_detector.py
│   │   └── test_recommendation.py
│   └── integration/
│       └── test_api.py
│
├── alembic/                       # Database migrations
│   └── versions/
│
├── scripts/                       # Utility scripts
│   ├── seed_data.py
│   └── backfill_history.py
│
├── .env.example                   # Environment template
├── requirements.txt
├── Dockerfile
└── README.md
```

### 4.2 File Naming Conventions

```python
# Files: snake_case
data_fetcher.py
rrg_engine.py

# Classes: PascalCase
class RRGEngine:
class RegimeDetector:

# Functions/Methods: snake_case
def calculate_rs_ratio():
def get_market_regime():

# Constants: SCREAMING_SNAKE_CASE
RS_RATIO_PERIOD = 10
RISK_ON_THRESHOLD = 3.0

# Private: leading underscore
def _normalize_score():
_cache = {}
```

---

## 5. Core Constants & Enums

### 5.1 constants.py

```python
"""
Core constants for RRG Rotation Map.
All magic numbers should be defined here.
"""
from typing import Final

# =============================================================================
# ETF SYMBOLS
# =============================================================================

class ETFSymbols:
    """ETF ticker symbols organized by category."""
    
    # Benchmark
    BENCHMARK: Final[str] = "SPY"
    
    # Risk Assets (高風險資産)
    RISK_ASSETS: Final[tuple[str, ...]] = (
        "IBIT",   # iShares Bitcoin Trust
        "ETHA",   # iShares Ethereum Trust
        "BOTZ",   # Global X Robotics & AI
        "QQQ",    # Invesco Nasdaq 100
        "IWM",    # iShares Russell 2000 (Small Cap)
    )
    
    # Safe Haven Assets (避險資産)
    SAFE_HAVEN: Final[tuple[str, ...]] = (
        "GLD",    # SPDR Gold Shares
        "TLT",    # iShares 20+ Year Treasury Bond
        "SHY",    # iShares 1-3 Year Treasury Bond
        "UUP",    # Invesco DB US Dollar Index
    )
    
    @classmethod
    def all_symbols(cls) -> list[str]:
        """Return all symbols including benchmark."""
        return [cls.BENCHMARK] + list(cls.RISK_ASSETS) + list(cls.SAFE_HAVEN)
    
    @classmethod
    def tracked_symbols(cls) -> list[str]:
        """Return symbols to track (excluding benchmark)."""
        return list(cls.RISK_ASSETS) + list(cls.SAFE_HAVEN)


# =============================================================================
# ETF METADATA
# =============================================================================

ETF_METADATA: Final[dict[str, dict]] = {
    "SPY":  {"name": "S&P 500",           "category": "benchmark",   "color": "#6b7280"},
    "IBIT": {"name": "Bitcoin",           "category": "risk",        "color": "#f7931a"},
    "ETHA": {"name": "Ethereum",          "category": "risk",        "color": "#627eea"},
    "BOTZ": {"name": "AI/Robotics",       "category": "risk",        "color": "#8b5cf6"},
    "QQQ":  {"name": "Nasdaq 100",        "category": "risk",        "color": "#00d4aa"},
    "IWM":  {"name": "Small Cap",         "category": "risk",        "color": "#f85149"},
    "GLD":  {"name": "Gold",              "category": "safe_haven",  "color": "#ffd700"},
    "TLT":  {"name": "Long-Term Bonds",   "category": "safe_haven",  "color": "#4ade80"},
    "SHY":  {"name": "Short-Term Bonds",  "category": "safe_haven",  "color": "#22d3ee"},
    "UUP":  {"name": "US Dollar",         "category": "safe_haven",  "color": "#a3e635"},
}


# =============================================================================
# RRG PARAMETERS
# =============================================================================

class RRGParams:
    """RRG calculation parameters."""
    
    # Standard RRG periods (Bloomberg/StockCharts convention)
    RS_RATIO_PERIOD: Final[int] = 10      # SMA period for RS-Ratio
    RS_MOMENTUM_PERIOD: Final[int] = 6    # SMA period for RS-Momentum
    
    # Normalization center
    CENTER_VALUE: Final[float] = 100.0
    
    # Quadrant thresholds
    QUADRANT_THRESHOLD: Final[float] = 100.0
    
    # Minimum data points required
    MIN_DATA_POINTS: Final[int] = 20


# =============================================================================
# REGIME DETECTION
# =============================================================================

class RegimeParams:
    """Market regime detection parameters."""
    
    # Quadrant scores for regime calculation
    QUADRANT_SCORES: Final[dict[str, int]] = {
        "leading": 2,
        "improving": 1,
        "weakening": -1,
        "lagging": -2,
    }
    
    # Thresholds for regime classification
    RISK_ON_THRESHOLD: Final[float] = 3.0
    RISK_OFF_THRESHOLD: Final[float] = -3.0
    
    # Score normalization range
    MAX_SCORE: Final[float] = 10.0


# =============================================================================
# RECOMMENDATION
# =============================================================================

class RecommendationParams:
    """Recommendation engine parameters."""
    
    # Minimum return for "positive" classification
    POSITIVE_RETURN_THRESHOLD: Final[float] = 0.0
    
    # Major cluster threshold (% of total)
    MAJOR_CLUSTER_PCT: Final[float] = 0.25
    
    # Top picks count
    TOP_PICKS_COUNT: Final[int] = 3


# =============================================================================
# DATA FETCHING
# =============================================================================

class DataFetchParams:
    """Yahoo Finance data fetching parameters."""
    
    # Historical data period
    HISTORY_DAYS: Final[int] = 60
    
    # Cache TTL in seconds (15 minutes)
    CACHE_TTL: Final[int] = 900
    
    # Request timeout
    REQUEST_TIMEOUT: Final[int] = 30
    
    # Retry attempts
    MAX_RETRIES: Final[int] = 3
    RETRY_DELAY: Final[float] = 1.0
```

### 5.2 enums.py

```python
"""
Enumerations for RRG Rotation Map.
Use enums instead of string literals for type safety.
"""
from enum import Enum, auto


class Quadrant(str, Enum):
    """RRG Quadrant classification."""
    
    LEADING = "leading"
    WEAKENING = "weakening"
    LAGGING = "lagging"
    IMPROVING = "improving"
    
    @property
    def emoji(self) -> str:
        """Return emoji for quadrant."""
        return {
            self.LEADING: "🚀",
            self.WEAKENING: "⚠️",
            self.LAGGING: "📉",
            self.IMPROVING: "📈",
        }[self]
    
    @property
    def display_name(self) -> str:
        """Return display name."""
        return self.value.capitalize()


class MarketRegime(str, Enum):
    """Market regime classification."""
    
    RISK_ON = "risk_on"
    RISK_OFF = "risk_off"
    NEUTRAL = "neutral"
    
    @property
    def emoji(self) -> str:
        return {
            self.RISK_ON: "📈",
            self.RISK_OFF: "📉",
            self.NEUTRAL: "⚖️",
        }[self]
    
    @property
    def display_name(self) -> str:
        return self.value.upper().replace("_", "-")
    
    @property
    def color(self) -> str:
        return {
            self.RISK_ON: "#3fb950",
            self.RISK_OFF: "#f85149",
            self.NEUTRAL: "#d29922",
        }[self]


class AssetCategory(str, Enum):
    """Asset category classification."""
    
    RISK = "risk"
    SAFE_HAVEN = "safe_haven"
    BENCHMARK = "benchmark"


class ActionSignal(str, Enum):
    """Trading action signals."""
    
    BUY = "buy"
    WATCH = "watch"
    REDUCE = "reduce"
    AVOID = "avoid"
    
    @property
    def emoji(self) -> str:
        return {
            self.BUY: "✅",
            self.WATCH: "📌",
            self.REDUCE: "⚠️",
            self.AVOID: "🚫",
        }[self]
    
    @property
    def label(self) -> str:
        return {
            self.BUY: "Buy / Add",
            self.WATCH: "Watch / Entry",
            self.REDUCE: "Take Profit",
            self.AVOID: "Avoid",
        }[self]
```

### 5.3 exceptions.py

```python
"""
Custom exceptions for RRG Rotation Map.
Explicit exceptions make debugging easier.
"""


class RRGError(Exception):
    """Base exception for RRG module."""
    pass


class DataFetchError(RRGError):
    """Raised when data fetching fails."""
    
    def __init__(self, symbol: str, reason: str):
        self.symbol = symbol
        self.reason = reason
        super().__init__(f"Failed to fetch data for {symbol}: {reason}")


class InsufficientDataError(RRGError):
    """Raised when there's not enough data for calculation."""
    
    def __init__(self, symbol: str, required: int, actual: int):
        self.symbol = symbol
        self.required = required
        self.actual = actual
        super().__init__(
            f"Insufficient data for {symbol}: need {required}, got {actual}"
        )


class CalculationError(RRGError):
    """Raised when RRG calculation fails."""
    
    def __init__(self, symbol: str, step: str, reason: str):
        self.symbol = symbol
        self.step = step
        self.reason = reason
        super().__init__(f"Calculation failed for {symbol} at {step}: {reason}")


class ConfigurationError(RRGError):
    """Raised when configuration is invalid."""
    pass
```

---

## 6. Domain Models

### 6.1 domain.py (Internal Models)

```python
"""
Domain models for internal use.
These are NOT exposed via API - use schemas.py for API models.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from app.core.enums import Quadrant, MarketRegime, AssetCategory, ActionSignal


@dataclass(frozen=True)
class PricePoint:
    """Immutable price data point."""
    
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    @property
    def typical_price(self) -> float:
        """Calculate typical price (HLC average)."""
        return (self.high + self.low + self.close) / 3


@dataclass
class RRGCoordinate:
    """RRG position for a single ETF."""
    
    symbol: str
    rs_ratio: float
    rs_momentum: float
    quadrant: Quadrant
    raw_rs: float
    period_return: float  # Return over RS_RATIO_PERIOD
    
    @property
    def x(self) -> float:
        """X coordinate (RS-Ratio)."""
        return self.rs_ratio
    
    @property
    def y(self) -> float:
        """Y coordinate (RS-Momentum)."""
        return self.rs_momentum
    
    @classmethod
    def determine_quadrant(cls, rs_ratio: float, rs_momentum: float) -> Quadrant:
        """Determine quadrant from coordinates."""
        if rs_ratio > 100 and rs_momentum > 100:
            return Quadrant.LEADING
        elif rs_ratio > 100 and rs_momentum <= 100:
            return Quadrant.WEAKENING
        elif rs_ratio <= 100 and rs_momentum <= 100:
            return Quadrant.LAGGING
        else:
            return Quadrant.IMPROVING


@dataclass
class ETFPosition:
    """Complete position data for an ETF."""
    
    symbol: str
    name: str
    category: AssetCategory
    color: str
    coordinate: RRGCoordinate
    current_price: float
    period_return: float
    action: ActionSignal
    
    @property
    def quadrant(self) -> Quadrant:
        return self.coordinate.quadrant


@dataclass
class RegimeScore:
    """Market regime calculation result."""
    
    regime: MarketRegime
    score: float  # -10 to +10
    risk_score: float
    safe_haven_score: float
    risk_leading_count: int
    risk_improving_count: int
    safe_leading_count: int
    safe_weakening_count: int


@dataclass
class TopPick:
    """Top investment pick."""
    
    rank: int
    symbol: str
    name: str
    reason: str
    period_return: float
    color: str


@dataclass
class ActionGroup:
    """Group of ETFs by action signal."""
    
    action: ActionSignal
    symbols: list[str]


@dataclass
class KeyInsight:
    """Single key insight."""
    
    emoji: str
    text: str
    highlight: Optional[str] = None


@dataclass
class RRGDashboard:
    """Complete RRG Dashboard data."""
    
    timestamp: datetime
    benchmark: str
    positions: list[ETFPosition]
    regime: RegimeScore
    top_picks: list[TopPick]
    action_groups: list[ActionGroup]
    insights: list[KeyInsight]
    
    @property
    def risk_assets(self) -> list[ETFPosition]:
        return [p for p in self.positions if p.category == AssetCategory.RISK]
    
    @property
    def safe_haven_assets(self) -> list[ETFPosition]:
        return [p for p in self.positions if p.category == AssetCategory.SAFE_HAVEN]
```

### 6.2 schemas.py (API Models)

```python
"""
Pydantic schemas for API request/response.
These are the contracts with the frontend.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.core.enums import Quadrant, MarketRegime, AssetCategory, ActionSignal


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class CoordinateResponse(BaseModel):
    """RRG coordinate for a single ETF."""
    
    model_config = ConfigDict(from_attributes=True)
    
    rs_ratio: float = Field(..., description="RS-Ratio (X-axis), centered at 100")
    rs_momentum: float = Field(..., description="RS-Momentum (Y-axis), centered at 100")
    quadrant: Quadrant = Field(..., description="Current quadrant")


class ETFPositionResponse(BaseModel):
    """Complete ETF position data for frontend."""
    
    model_config = ConfigDict(from_attributes=True)
    
    symbol: str = Field(..., description="ETF ticker symbol")
    name: str = Field(..., description="Display name")
    category: AssetCategory = Field(..., description="Asset category")
    color: str = Field(..., description="Hex color for chart")
    coordinate: CoordinateResponse
    current_price: float = Field(..., description="Latest closing price")
    period_return: float = Field(..., description="Return over calculation period (%)")
    action: ActionSignal = Field(..., description="Recommended action")
    quadrant_emoji: str = Field(..., description="Emoji for quadrant")
    
    @classmethod
    def from_domain(cls, position) -> "ETFPositionResponse":
        """Create from domain model."""
        return cls(
            symbol=position.symbol,
            name=position.name,
            category=position.category,
            color=position.color,
            coordinate=CoordinateResponse(
                rs_ratio=position.coordinate.rs_ratio,
                rs_momentum=position.coordinate.rs_momentum,
                quadrant=position.coordinate.quadrant,
            ),
            current_price=position.current_price,
            period_return=position.period_return,
            action=position.action,
            quadrant_emoji=position.quadrant.emoji,
        )


class RegimeResponse(BaseModel):
    """Market regime data."""
    
    regime: MarketRegime
    score: float = Field(..., ge=-10, le=10, description="Regime score")
    emoji: str
    display_name: str
    color: str
    risk_summary: str = Field(..., description="e.g., '2 Leading, 1 Improving'")
    safe_summary: str = Field(..., description="e.g., '1 Leading, 2 Weakening'")


class TopPickResponse(BaseModel):
    """Top investment pick."""
    
    rank: int = Field(..., ge=1, le=3)
    symbol: str
    name: str
    reason: str
    period_return: float
    color: str


class ActionGroupResponse(BaseModel):
    """Action group with ETF symbols."""
    
    action: ActionSignal
    label: str
    emoji: str
    symbols: list[str]


class InsightResponse(BaseModel):
    """Key insight item."""
    
    emoji: str
    text: str
    highlight: Optional[str] = None


class RRGDashboardResponse(BaseModel):
    """Complete RRG Dashboard response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    timestamp: datetime
    benchmark: str
    
    # Positions separated by category
    risk_assets: list[ETFPositionResponse]
    safe_haven_assets: list[ETFPositionResponse]
    
    # Regime
    regime: RegimeResponse
    
    # Recommendations
    top_picks: list[TopPickResponse]
    action_groups: list[ActionGroupResponse]
    insights: list[InsightResponse]
    
    # Metadata
    calculation_period: int = Field(..., description="RS-Ratio period in days")
    data_freshness: str = Field(..., description="e.g., 'Live' or '15 min delay'")


# =============================================================================
# ERROR RESPONSES
# =============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: str = "connected"
    yahoo_finance: str = "reachable"
```

---

## 7. Service Layer

### 7.1 data_fetcher.py

```python
"""
Yahoo Finance data fetcher service.

Responsibilities:
- Fetch price data from Yahoo Finance
- Handle retries and errors
- Cache management
"""
import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import Optional

import httpx
import yfinance as yf
from cachetools import TTLCache

from app.core.constants import ETFSymbols, DataFetchParams, ETF_METADATA
from app.core.exceptions import DataFetchError
from app.models.domain import PricePoint

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Fetches price data from Yahoo Finance.
    
    Thread-safe with async support and built-in caching.
    """
    
    def __init__(self):
        self._cache: TTLCache = TTLCache(
            maxsize=100,
            ttl=DataFetchParams.CACHE_TTL
        )
        self._lock = asyncio.Lock()
    
    async def fetch_prices(
        self,
        symbol: str,
        days: int = DataFetchParams.HISTORY_DAYS
    ) -> list[PricePoint]:
        """
        Fetch historical prices for a symbol.
        
        Args:
            symbol: ETF ticker symbol
            days: Number of days of history
            
        Returns:
            List of PricePoint objects, sorted by date ascending
            
        Raises:
            DataFetchError: If fetching fails after retries
        """
        cache_key = f"{symbol}_{days}"
        
        # Check cache first
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {symbol}")
            return self._cache[cache_key]
        
        async with self._lock:
            # Double-check after acquiring lock
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Fetch from Yahoo Finance
            prices = await self._fetch_with_retry(symbol, days)
            
            # Cache result
            self._cache[cache_key] = prices
            
            return prices
    
    async def _fetch_with_retry(
        self,
        symbol: str,
        days: int
    ) -> list[PricePoint]:
        """Fetch with exponential backoff retry."""
        
        last_error: Optional[Exception] = None
        
        for attempt in range(DataFetchParams.MAX_RETRIES):
            try:
                return await self._do_fetch(symbol, days)
                
            except Exception as e:
                last_error = e
                wait_time = DataFetchParams.RETRY_DELAY * (2 ** attempt)
                
                logger.warning(
                    f"Fetch attempt {attempt + 1} failed for {symbol}: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                
                await asyncio.sleep(wait_time)
        
        raise DataFetchError(symbol, str(last_error))
    
    async def _do_fetch(self, symbol: str, days: int) -> list[PricePoint]:
        """Actual fetch implementation."""
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Use yfinance (runs in thread pool for async)
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(
            None,
            lambda: yf.download(
                symbol,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                progress=False,
            )
        )
        
        if df.empty:
            raise DataFetchError(symbol, "No data returned")
        
        # Convert to PricePoint objects
        prices = []
        for idx, row in df.iterrows():
            prices.append(PricePoint(
                date=idx.date(),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]),
            ))
        
        logger.info(f"Fetched {len(prices)} price points for {symbol}")
        
        return sorted(prices, key=lambda p: p.date)
    
    async def fetch_all_symbols(self) -> dict[str, list[PricePoint]]:
        """
        Fetch prices for all tracked symbols.
        
        Returns:
            Dict mapping symbol to price history
        """
        symbols = ETFSymbols.all_symbols()
        
        # Fetch concurrently
        tasks = [self.fetch_prices(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build result dict, log errors
        data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch {symbol}: {result}")
            else:
                data[symbol] = result
        
        return data
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        logger.info("Cache cleared")
```

### 7.2 rrg_engine.py

```python
"""
RRG (Relative Rotation Graph) calculation engine.

Responsibilities:
- Calculate RS-Ratio (X-axis)
- Calculate RS-Momentum (Y-axis)
- Determine quadrant classification
"""
import logging
from typing import Optional

import numpy as np

from app.core.constants import RRGParams, ETFSymbols, ETF_METADATA
from app.core.enums import Quadrant, AssetCategory
from app.core.exceptions import InsufficientDataError, CalculationError
from app.models.domain import PricePoint, RRGCoordinate

logger = logging.getLogger(__name__)


class RRGEngine:
    """
    Calculates RRG coordinates for ETFs.
    
    Formula:
    1. Raw RS = ETF_Price / Benchmark_Price
    2. RS-Ratio = (Raw_RS / SMA(Raw_RS, 10)) × 100
    3. RS-Momentum = (RS_Ratio / SMA(RS_Ratio, 6)) × 100
    """
    
    def __init__(
        self,
        rs_ratio_period: int = RRGParams.RS_RATIO_PERIOD,
        rs_momentum_period: int = RRGParams.RS_MOMENTUM_PERIOD,
    ):
        self._rs_ratio_period = rs_ratio_period
        self._rs_momentum_period = rs_momentum_period
        self._min_points = rs_ratio_period + rs_momentum_period + 5
    
    def calculate(
        self,
        symbol: str,
        etf_prices: list[PricePoint],
        benchmark_prices: list[PricePoint],
    ) -> RRGCoordinate:
        """
        Calculate RRG coordinates for a single ETF.
        
        Args:
            symbol: ETF ticker symbol
            etf_prices: ETF price history (sorted by date)
            benchmark_prices: Benchmark price history (sorted by date)
            
        Returns:
            RRGCoordinate with current position
            
        Raises:
            InsufficientDataError: Not enough data points
            CalculationError: Calculation failed
        """
        # Validate data
        self._validate_inputs(symbol, etf_prices, benchmark_prices)
        
        # Align dates
        etf_closes, bench_closes = self._align_prices(etf_prices, benchmark_prices)
        
        if len(etf_closes) < self._min_points:
            raise InsufficientDataError(symbol, self._min_points, len(etf_closes))
        
        try:
            # Step 1: Calculate Raw RS
            raw_rs = np.array(etf_closes) / np.array(bench_closes)
            
            # Step 2: Calculate RS-Ratio
            rs_ratio_series = self._calculate_rs_ratio(raw_rs)
            
            # Step 3: Calculate RS-Momentum
            rs_momentum = self._calculate_rs_momentum(rs_ratio_series)
            
            # Get latest values
            current_rs_ratio = rs_ratio_series[-1]
            current_rs_momentum = rs_momentum
            current_raw_rs = raw_rs[-1]
            
            # Calculate period return
            period_return = self._calculate_return(etf_closes)
            
            # Determine quadrant
            quadrant = RRGCoordinate.determine_quadrant(
                current_rs_ratio,
                current_rs_momentum
            )
            
            logger.debug(
                f"{symbol}: RS-Ratio={current_rs_ratio:.2f}, "
                f"RS-Momentum={current_rs_momentum:.2f}, "
                f"Quadrant={quadrant.value}"
            )
            
            return RRGCoordinate(
                symbol=symbol,
                rs_ratio=round(current_rs_ratio, 2),
                rs_momentum=round(current_rs_momentum, 2),
                quadrant=quadrant,
                raw_rs=round(current_raw_rs, 6),
                period_return=round(period_return, 2),
            )
            
        except Exception as e:
            raise CalculationError(symbol, "RRG calculation", str(e))
    
    def _validate_inputs(
        self,
        symbol: str,
        etf_prices: list[PricePoint],
        benchmark_prices: list[PricePoint],
    ) -> None:
        """Validate input data."""
        if not etf_prices:
            raise InsufficientDataError(symbol, self._min_points, 0)
        
        if not benchmark_prices:
            raise InsufficientDataError("benchmark", self._min_points, 0)
    
    def _align_prices(
        self,
        etf_prices: list[PricePoint],
        benchmark_prices: list[PricePoint],
    ) -> tuple[list[float], list[float]]:
        """Align prices by date, return closing prices."""
        
        # Build date -> close mapping
        etf_dict = {p.date: p.close for p in etf_prices}
        bench_dict = {p.date: p.close for p in benchmark_prices}
        
        # Find common dates
        common_dates = sorted(set(etf_dict.keys()) & set(bench_dict.keys()))
        
        etf_closes = [etf_dict[d] for d in common_dates]
        bench_closes = [bench_dict[d] for d in common_dates]
        
        return etf_closes, bench_closes
    
    def _calculate_rs_ratio(self, raw_rs: np.ndarray) -> np.ndarray:
        """Calculate RS-Ratio series."""
        
        # Simple Moving Average of Raw RS
        sma = self._sma(raw_rs, self._rs_ratio_period)
        
        # RS-Ratio = (Raw_RS / SMA) × 100
        rs_ratio = (raw_rs / sma) * RRGParams.CENTER_VALUE
        
        return rs_ratio
    
    def _calculate_rs_momentum(self, rs_ratio: np.ndarray) -> float:
        """Calculate RS-Momentum (latest value only)."""
        
        # We need at least rs_momentum_period points
        if len(rs_ratio) < self._rs_momentum_period:
            return RRGParams.CENTER_VALUE
        
        # SMA of RS-Ratio
        sma = self._sma(rs_ratio, self._rs_momentum_period)
        
        # RS-Momentum = (RS_Ratio / SMA) × 100
        rs_momentum = (rs_ratio[-1] / sma[-1]) * RRGParams.CENTER_VALUE
        
        return rs_momentum
    
    def _sma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average."""
        
        if len(data) < period:
            # Return array filled with first value if not enough data
            return np.full_like(data, data[0])
        
        # Cumulative sum method for efficiency
        cumsum = np.cumsum(np.insert(data, 0, 0))
        sma = (cumsum[period:] - cumsum[:-period]) / period
        
        # Pad beginning with first valid SMA
        padding = np.full(period - 1, sma[0])
        
        return np.concatenate([padding, sma])
    
    def _calculate_return(self, closes: list[float]) -> float:
        """Calculate return over RS-Ratio period."""
        
        if len(closes) < self._rs_ratio_period:
            return 0.0
        
        start_price = closes[-self._rs_ratio_period]
        end_price = closes[-1]
        
        if start_price == 0:
            return 0.0
        
        return ((end_price / start_price) - 1) * 100
    
    def calculate_all(
        self,
        price_data: dict[str, list[PricePoint]],
    ) -> dict[str, RRGCoordinate]:
        """
        Calculate RRG for all ETFs.
        
        Args:
            price_data: Dict mapping symbol to price history
            
        Returns:
            Dict mapping symbol to RRGCoordinate
        """
        benchmark_symbol = ETFSymbols.BENCHMARK
        
        if benchmark_symbol not in price_data:
            raise CalculationError(
                benchmark_symbol,
                "data validation",
                "Benchmark data not found"
            )
        
        benchmark_prices = price_data[benchmark_symbol]
        results = {}
        
        for symbol in ETFSymbols.tracked_symbols():
            if symbol not in price_data:
                logger.warning(f"No data for {symbol}, skipping")
                continue
            
            try:
                coordinate = self.calculate(
                    symbol,
                    price_data[symbol],
                    benchmark_prices,
                )
                results[symbol] = coordinate
                
            except Exception as e:
                logger.error(f"Failed to calculate RRG for {symbol}: {e}")
        
        return results
```

### 7.3 regime_detector.py

```python
"""
Market regime detection service.

Responsibilities:
- Classify market regime (Risk-On / Risk-Off / Neutral)
- Calculate regime score
- Generate regime summary
"""
import logging
from typing import Optional

from app.core.constants import ETFSymbols, RegimeParams, ETF_METADATA
from app.core.enums import Quadrant, MarketRegime, AssetCategory
from app.models.domain import RRGCoordinate, RegimeScore

logger = logging.getLogger(__name__)


class RegimeDetector:
    """
    Detects market regime from RRG positions.
    
    Algorithm:
    1. Score each ETF based on quadrant
    2. Aggregate scores for Risk vs Safe Haven
    3. Classify regime based on net score
    """
    
    def detect(
        self,
        coordinates: dict[str, RRGCoordinate],
    ) -> RegimeScore:
        """
        Detect current market regime.
        
        Args:
            coordinates: Dict mapping symbol to RRG coordinate
            
        Returns:
            RegimeScore with classification and details
        """
        # Calculate scores
        risk_score = self._calculate_category_score(
            coordinates,
            ETFSymbols.RISK_ASSETS,
        )
        
        safe_score = self._calculate_category_score(
            coordinates,
            ETFSymbols.SAFE_HAVEN,
        )
        
        # Net score: positive = risk-on, negative = risk-off
        # Safe haven uses inverted logic
        net_score = risk_score - safe_score
        
        # Normalize to -10 to +10
        max_possible = (
            len(ETFSymbols.RISK_ASSETS) * 2 +
            len(ETFSymbols.SAFE_HAVEN) * 2
        )
        normalized_score = (net_score / max_possible) * RegimeParams.MAX_SCORE
        
        # Classify regime
        regime = self._classify_regime(normalized_score)
        
        # Count positions
        risk_counts = self._count_quadrants(coordinates, ETFSymbols.RISK_ASSETS)
        safe_counts = self._count_quadrants(coordinates, ETFSymbols.SAFE_HAVEN)
        
        logger.info(
            f"Regime detected: {regime.value} (score: {normalized_score:.1f})"
        )
        
        return RegimeScore(
            regime=regime,
            score=round(normalized_score, 1),
            risk_score=risk_score,
            safe_haven_score=safe_score,
            risk_leading_count=risk_counts.get(Quadrant.LEADING, 0),
            risk_improving_count=risk_counts.get(Quadrant.IMPROVING, 0),
            safe_leading_count=safe_counts.get(Quadrant.LEADING, 0),
            safe_weakening_count=safe_counts.get(Quadrant.WEAKENING, 0),
        )
    
    def _calculate_category_score(
        self,
        coordinates: dict[str, RRGCoordinate],
        symbols: tuple[str, ...],
    ) -> float:
        """Calculate aggregate score for a category."""
        
        total_score = 0.0
        
        for symbol in symbols:
            if symbol not in coordinates:
                continue
            
            quadrant = coordinates[symbol].quadrant
            score = RegimeParams.QUADRANT_SCORES.get(quadrant.value, 0)
            total_score += score
        
        return total_score
    
    def _count_quadrants(
        self,
        coordinates: dict[str, RRGCoordinate],
        symbols: tuple[str, ...],
    ) -> dict[Quadrant, int]:
        """Count positions in each quadrant."""
        
        counts: dict[Quadrant, int] = {}
        
        for symbol in symbols:
            if symbol not in coordinates:
                continue
            
            quadrant = coordinates[symbol].quadrant
            counts[quadrant] = counts.get(quadrant, 0) + 1
        
        return counts
    
    def _classify_regime(self, score: float) -> MarketRegime:
        """Classify regime from normalized score."""
        
        if score >= RegimeParams.RISK_ON_THRESHOLD:
            return MarketRegime.RISK_ON
        elif score <= RegimeParams.RISK_OFF_THRESHOLD:
            return MarketRegime.RISK_OFF
        else:
            return MarketRegime.NEUTRAL
    
    def format_summary(
        self,
        counts: dict[Quadrant, int],
        category: str,
    ) -> str:
        """Format quadrant counts as summary string."""
        
        parts = []
        
        if counts.get(Quadrant.LEADING, 0) > 0:
            parts.append(f"{counts[Quadrant.LEADING]} Leading")
        
        if counts.get(Quadrant.IMPROVING, 0) > 0:
            parts.append(f"{counts[Quadrant.IMPROVING]} Improving")
        
        if counts.get(Quadrant.WEAKENING, 0) > 0:
            parts.append(f"{counts[Quadrant.WEAKENING]} Weakening")
        
        if counts.get(Quadrant.LAGGING, 0) > 0:
            parts.append(f"{counts[Quadrant.LAGGING]} Lagging")
        
        return ", ".join(parts) if parts else "No data"
```

### 7.4 recommendation.py

```python
"""
Investment recommendation engine.

Responsibilities:
- Generate top picks
- Assign action signals
- Create key insights
"""
import logging
from typing import Optional

from app.core.constants import (
    ETFSymbols, ETF_METADATA, 
    RecommendationParams, RRGParams
)
from app.core.enums import (
    Quadrant, MarketRegime, AssetCategory, ActionSignal
)
from app.models.domain import (
    RRGCoordinate, RegimeScore, ETFPosition,
    TopPick, ActionGroup, KeyInsight
)

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Generates investment recommendations from RRG data.
    """
    
    def build_positions(
        self,
        coordinates: dict[str, RRGCoordinate],
        price_data: dict,
    ) -> list[ETFPosition]:
        """
        Build complete ETF positions with actions.
        
        Args:
            coordinates: RRG coordinates for each ETF
            price_data: Price data for current prices
            
        Returns:
            List of ETFPosition objects
        """
        positions = []
        
        for symbol, coord in coordinates.items():
            metadata = ETF_METADATA.get(symbol, {})
            
            # Determine category
            if symbol in ETFSymbols.RISK_ASSETS:
                category = AssetCategory.RISK
            elif symbol in ETFSymbols.SAFE_HAVEN:
                category = AssetCategory.SAFE_HAVEN
            else:
                category = AssetCategory.BENCHMARK
            
            # Determine action
            action = self._determine_action(coord.quadrant, category)
            
            # Get current price
            prices = price_data.get(symbol, [])
            current_price = prices[-1].close if prices else 0.0
            
            positions.append(ETFPosition(
                symbol=symbol,
                name=metadata.get("name", symbol),
                category=category,
                color=metadata.get("color", "#6b7280"),
                coordinate=coord,
                current_price=current_price,
                period_return=coord.period_return,
                action=action,
            ))
        
        return positions
    
    def _determine_action(
        self,
        quadrant: Quadrant,
        category: AssetCategory,
    ) -> ActionSignal:
        """Determine action signal based on quadrant and category."""
        
        # Risk assets: follow quadrant directly
        if category == AssetCategory.RISK:
            return {
                Quadrant.LEADING: ActionSignal.BUY,
                Quadrant.IMPROVING: ActionSignal.WATCH,
                Quadrant.WEAKENING: ActionSignal.REDUCE,
                Quadrant.LAGGING: ActionSignal.AVOID,
            }[quadrant]
        
        # Safe haven: inverse logic for risk-on environment
        # (We want to reduce safe haven when risk is on)
        else:
            return {
                Quadrant.LEADING: ActionSignal.WATCH,  # Strong but defensive
                Quadrant.IMPROVING: ActionSignal.WATCH,
                Quadrant.WEAKENING: ActionSignal.REDUCE,
                Quadrant.LAGGING: ActionSignal.AVOID,
            }[quadrant]
    
    def generate_top_picks(
        self,
        positions: list[ETFPosition],
        count: int = RecommendationParams.TOP_PICKS_COUNT,
    ) -> list[TopPick]:
        """
        Generate top investment picks.
        
        Criteria:
        1. Leading quadrant first
        2. Improving quadrant second
        3. Sort by period return within each group
        """
        # Filter to BUY or WATCH actions
        candidates = [
            p for p in positions
            if p.action in (ActionSignal.BUY, ActionSignal.WATCH)
        ]
        
        # Sort: Leading first, then Improving, then by return
        def sort_key(p: ETFPosition) -> tuple:
            quadrant_order = {
                Quadrant.LEADING: 0,
                Quadrant.IMPROVING: 1,
            }
            return (
                quadrant_order.get(p.quadrant, 99),
                -p.period_return,  # Descending return
            )
        
        candidates.sort(key=sort_key)
        
        # Build top picks
        picks = []
        for i, pos in enumerate(candidates[:count], start=1):
            reason = self._generate_reason(pos)
            
            picks.append(TopPick(
                rank=i,
                symbol=pos.symbol,
                name=pos.name,
                reason=reason,
                period_return=pos.period_return,
                color=pos.color,
            ))
        
        return picks
    
    def _generate_reason(self, position: ETFPosition) -> str:
        """Generate human-readable reason for pick."""
        
        quadrant = position.quadrant
        
        if quadrant == Quadrant.LEADING:
            return "Strongest momentum, leading rotation"
        elif quadrant == Quadrant.IMPROVING:
            return "Improving momentum, early entry"
        elif quadrant == Quadrant.WEAKENING:
            return "Strong but losing momentum"
        else:
            return "Underperforming"
    
    def generate_action_groups(
        self,
        positions: list[ETFPosition],
    ) -> list[ActionGroup]:
        """Group positions by action signal."""
        
        groups = {}
        
        for pos in positions:
            if pos.action not in groups:
                groups[pos.action] = []
            groups[pos.action].append(pos.symbol)
        
        # Order: BUY, WATCH, REDUCE, AVOID
        action_order = [
            ActionSignal.BUY,
            ActionSignal.WATCH,
            ActionSignal.REDUCE,
            ActionSignal.AVOID,
        ]
        
        result = []
        for action in action_order:
            if action in groups:
                result.append(ActionGroup(
                    action=action,
                    symbols=groups[action],
                ))
        
        return result
    
    def generate_insights(
        self,
        positions: list[ETFPosition],
        regime: RegimeScore,
    ) -> list[KeyInsight]:
        """Generate key insights based on current state."""
        
        insights = []
        
        # Insight 1: Leading assets
        leading = [p for p in positions if p.quadrant == Quadrant.LEADING]
        if leading:
            names = " & ".join([p.name for p in leading[:2]])
            insights.append(KeyInsight(
                emoji="🚀",
                text=f"{names} leading — Risk appetite is HIGH",
                highlight=names,
            ))
        
        # Insight 2: Weakening safe haven
        safe_weakening = [
            p for p in positions
            if p.category == AssetCategory.SAFE_HAVEN
            and p.quadrant in (Quadrant.WEAKENING, Quadrant.LAGGING)
        ]
        if safe_weakening:
            names = " & ".join([p.name for p in safe_weakening[:2]])
            insights.append(KeyInsight(
                emoji="⚠️",
                text=f"{names} weakening — Safe haven outflow confirms {regime.regime.display_name}",
                highlight=names,
            ))
        
        # Insight 3: USD status
        usd_pos = next((p for p in positions if p.symbol == "UUP"), None)
        if usd_pos:
            if usd_pos.quadrant == Quadrant.LEADING:
                insights.append(KeyInsight(
                    emoji="💵",
                    text="USD strong — Dollar strength (watch for divergence)",
                    highlight="USD",
                ))
        
        # Insight 4: Improving assets
        improving = [
            p for p in positions
            if p.quadrant == Quadrant.IMPROVING
            and p.category == AssetCategory.RISK
        ]
        if improving:
            names = " & ".join([p.name for p in improving[:2]])
            insights.append(KeyInsight(
                emoji="📈",
                text=f"{names} improving — Rally broadening signal",
                highlight=names,
            ))
        
        # Insight 5: Lagging risk assets
        lagging_risk = [
            p for p in positions
            if p.quadrant == Quadrant.LAGGING
            and p.category == AssetCategory.RISK
        ]
        if lagging_risk:
            names = " & ".join([p.name for p in lagging_risk[:2]])
            insights.append(KeyInsight(
                emoji="📉",
                text=f"{names} lagging — Wait for rotation confirmation",
                highlight=names,
            ))
        
        return insights[:5]  # Max 5 insights
```

---

## 8. API Layer

### 8.1 endpoints/rrg.py

```python
"""
RRG API endpoints.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.constants import RRGParams
from app.models.schemas import (
    RRGDashboardResponse,
    ETFPositionResponse,
    RegimeResponse,
    TopPickResponse,
    ActionGroupResponse,
    InsightResponse,
    ErrorResponse,
)
from app.services.data_fetcher import DataFetcher
from app.services.rrg_engine import RRGEngine
from app.services.regime_detector import RegimeDetector
from app.services.recommendation import RecommendationEngine
from app.api.dependencies import (
    get_data_fetcher,
    get_rrg_engine,
    get_regime_detector,
    get_recommendation_engine,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rrg", tags=["RRG"])


@router.get(
    "/dashboard",
    response_model=RRGDashboardResponse,
    responses={
        500: {"model": ErrorResponse},
    },
    summary="Get RRG Dashboard",
    description="Returns complete RRG dashboard with positions, regime, and recommendations",
)
async def get_dashboard(
    data_fetcher: DataFetcher = Depends(get_data_fetcher),
    rrg_engine: RRGEngine = Depends(get_rrg_engine),
    regime_detector: RegimeDetector = Depends(get_regime_detector),
    rec_engine: RecommendationEngine = Depends(get_recommendation_engine),
) -> RRGDashboardResponse:
    """
    Get complete RRG dashboard data.
    
    This endpoint:
    1. Fetches latest prices from Yahoo Finance
    2. Calculates RRG coordinates for all ETFs
    3. Detects market regime
    4. Generates investment recommendations
    """
    try:
        # Step 1: Fetch prices
        logger.info("Fetching price data...")
        price_data = await data_fetcher.fetch_all_symbols()
        
        if not price_data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch price data",
            )
        
        # Step 2: Calculate RRG
        logger.info("Calculating RRG coordinates...")
        coordinates = rrg_engine.calculate_all(price_data)
        
        # Step 3: Detect regime
        logger.info("Detecting market regime...")
        regime = regime_detector.detect(coordinates)
        
        # Step 4: Build positions
        logger.info("Building positions and recommendations...")
        positions = rec_engine.build_positions(coordinates, price_data)
        
        # Step 5: Generate recommendations
        top_picks = rec_engine.generate_top_picks(positions)
        action_groups = rec_engine.generate_action_groups(positions)
        insights = rec_engine.generate_insights(positions, regime)
        
        # Separate by category
        risk_assets = [
            ETFPositionResponse.from_domain(p)
            for p in positions
            if p.category.value == "risk"
        ]
        safe_haven = [
            ETFPositionResponse.from_domain(p)
            for p in positions
            if p.category.value == "safe_haven"
        ]
        
        # Build regime response
        regime_response = RegimeResponse(
            regime=regime.regime,
            score=regime.score,
            emoji=regime.regime.emoji,
            display_name=regime.regime.display_name,
            color=regime.regime.color,
            risk_summary=_format_summary(regime, "risk"),
            safe_summary=_format_summary(regime, "safe"),
        )
        
        return RRGDashboardResponse(
            timestamp=datetime.utcnow(),
            benchmark="SPY",
            risk_assets=risk_assets,
            safe_haven_assets=safe_haven,
            regime=regime_response,
            top_picks=[
                TopPickResponse(
                    rank=p.rank,
                    symbol=p.symbol,
                    name=p.name,
                    reason=p.reason,
                    period_return=p.period_return,
                    color=p.color,
                )
                for p in top_picks
            ],
            action_groups=[
                ActionGroupResponse(
                    action=g.action,
                    label=g.action.label,
                    emoji=g.action.emoji,
                    symbols=g.symbols,
                )
                for g in action_groups
            ],
            insights=[
                InsightResponse(
                    emoji=i.emoji,
                    text=i.text,
                    highlight=i.highlight,
                )
                for i in insights
            ],
            calculation_period=RRGParams.RS_RATIO_PERIOD,
            data_freshness="15 min delay",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Dashboard generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def _format_summary(regime, category: str) -> str:
    """Format regime counts as summary string."""
    if category == "risk":
        leading = regime.risk_leading_count
        improving = regime.risk_improving_count
    else:
        leading = regime.safe_leading_count
        improving = 0  # Not tracked for safe haven
    
    parts = []
    if leading > 0:
        parts.append(f"{leading} Leading")
    if improving > 0:
        parts.append(f"{improving} Improving")
    
    return ", ".join(parts) if parts else "None"
```

### 8.2 dependencies.py

```python
"""
Dependency injection for FastAPI.
"""
from functools import lru_cache

from app.services.data_fetcher import DataFetcher
from app.services.rrg_engine import RRGEngine
from app.services.regime_detector import RegimeDetector
from app.services.recommendation import RecommendationEngine


@lru_cache()
def get_data_fetcher() -> DataFetcher:
    """Get singleton DataFetcher instance."""
    return DataFetcher()


@lru_cache()
def get_rrg_engine() -> RRGEngine:
    """Get singleton RRGEngine instance."""
    return RRGEngine()


@lru_cache()
def get_regime_detector() -> RegimeDetector:
    """Get singleton RegimeDetector instance."""
    return RegimeDetector()


@lru_cache()
def get_recommendation_engine() -> RecommendationEngine:
    """Get singleton RecommendationEngine instance."""
    return RecommendationEngine()
```

---

## 9. Database Schema

### 9.1 SQL Schema (Supabase)

```sql
-- =====================================================
-- RRG ROTATION MAP DATABASE SCHEMA
-- Run in Supabase SQL Editor
-- =====================================================

-- Table: Price history cache
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(symbol, date)
);

-- Table: RRG snapshots (for historical tracking)
CREATE TABLE IF NOT EXISTS rrg_snapshots (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    rs_ratio DECIMAL(10, 4) NOT NULL,
    rs_momentum DECIMAL(10, 4) NOT NULL,
    quadrant VARCHAR(20) NOT NULL,
    period_return DECIMAL(10, 4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(symbol, timestamp)
);

-- Table: Regime history
CREATE TABLE IF NOT EXISTS regime_history (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    regime VARCHAR(20) NOT NULL,
    score DECIMAL(5, 2) NOT NULL,
    risk_score DECIMAL(5, 2),
    safe_score DECIMAL(5, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_price_symbol_date 
    ON price_history(symbol, date DESC);

CREATE INDEX IF NOT EXISTS idx_rrg_symbol_ts 
    ON rrg_snapshots(symbol, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_regime_ts 
    ON regime_history(timestamp DESC);

-- Cleanup function
CREATE OR REPLACE FUNCTION cleanup_old_data(retention_days INTEGER DEFAULT 90)
RETURNS void AS $$
BEGIN
    DELETE FROM price_history 
    WHERE date < CURRENT_DATE - retention_days;
    
    DELETE FROM rrg_snapshots 
    WHERE timestamp < NOW() - (retention_days || ' days')::INTERVAL;
    
    DELETE FROM regime_history 
    WHERE timestamp < NOW() - (retention_days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;
```

---

## 10. Frontend Specification

### 10.1 Component Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── RRGDashboard/
│   │   │   ├── index.tsx           # Main container
│   │   │   ├── RRGChart.tsx        # Rotation map chart
│   │   │   ├── RegimeIndicator.tsx # Regime badge + scale
│   │   │   ├── ETFLegend.tsx       # ETF list with status
│   │   │   ├── Recommendation.tsx  # Top picks + actions
│   │   │   └── Insights.tsx        # Key insights
│   │   │
│   │   └── ui/                     # Reusable UI components
│   │       ├── Badge.tsx
│   │       ├── Card.tsx
│   │       └── Dot.tsx
│   │
│   ├── hooks/
│   │   └── useRRGData.ts           # React Query hook
│   │
│   ├── types/
│   │   └── rrg.ts                  # TypeScript types
│   │
│   └── styles/
│       └── rrg.css                 # Custom styles
```

### 10.2 TypeScript Types

```typescript
// types/rrg.ts

export type Quadrant = 'leading' | 'weakening' | 'lagging' | 'improving';
export type MarketRegime = 'risk_on' | 'risk_off' | 'neutral';
export type AssetCategory = 'risk' | 'safe_haven' | 'benchmark';
export type ActionSignal = 'buy' | 'watch' | 'reduce' | 'avoid';

export interface Coordinate {
  rs_ratio: number;
  rs_momentum: number;
  quadrant: Quadrant;
}

export interface ETFPosition {
  symbol: string;
  name: string;
  category: AssetCategory;
  color: string;
  coordinate: Coordinate;
  current_price: number;
  period_return: number;
  action: ActionSignal;
  quadrant_emoji: string;
}

export interface RegimeData {
  regime: MarketRegime;
  score: number;
  emoji: string;
  display_name: string;
  color: string;
  risk_summary: string;
  safe_summary: string;
}

export interface TopPick {
  rank: number;
  symbol: string;
  name: string;
  reason: string;
  period_return: number;
  color: string;
}

export interface ActionGroup {
  action: ActionSignal;
  label: string;
  emoji: string;
  symbols: string[];
}

export interface Insight {
  emoji: string;
  text: string;
  highlight?: string;
}

export interface RRGDashboardData {
  timestamp: string;
  benchmark: string;
  risk_assets: ETFPosition[];
  safe_haven_assets: ETFPosition[];
  regime: RegimeData;
  top_picks: TopPick[];
  action_groups: ActionGroup[];
  insights: Insight[];
  calculation_period: number;
  data_freshness: string;
}
```

### 10.3 Color Palette

```typescript
// constants/colors.ts

export const COLORS = {
  // Background
  background: '#0d1117',
  cardBg: '#161b22',
  border: '#30363d',
  
  // Quadrant backgrounds
  quadrant: {
    leading: 'rgba(63, 185, 80, 0.08)',
    weakening: 'rgba(210, 153, 34, 0.08)',
    lagging: 'rgba(248, 81, 73, 0.08)',
    improving: 'rgba(88, 166, 255, 0.08)',
  },
  
  // Quadrant labels
  quadrantLabel: {
    leading: '#3fb950',
    weakening: '#d29922',
    lagging: '#f85149',
    improving: '#58a6ff',
  },
  
  // Regime
  regime: {
    risk_on: '#3fb950',
    risk_off: '#f85149',
    neutral: '#d29922',
  },
  
  // Text
  textPrimary: '#f0f6fc',
  textSecondary: '#8b949e',
  textMuted: '#6e7681',
  
  // Safe haven border
  safeHavenBorder: '#ffd700',
} as const;
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

```python
# tests/unit/test_rrg_engine.py

import pytest
from datetime import date

from app.core.enums import Quadrant
from app.models.domain import PricePoint
from app.services.rrg_engine import RRGEngine


@pytest.fixture
def rrg_engine():
    return RRGEngine(rs_ratio_period=10, rs_momentum_period=6)


@pytest.fixture
def sample_prices():
    """Generate sample price data."""
    return [
        PricePoint(
            date=date(2026, 1, i),
            open=100 + i,
            high=101 + i,
            low=99 + i,
            close=100 + i,
            volume=1000000,
        )
        for i in range(1, 31)
    ]


class TestRRGEngine:
    """Test RRG calculation engine."""
    
    def test_calculate_returns_coordinate(self, rrg_engine, sample_prices):
        """Should return valid RRG coordinate."""
        coord = rrg_engine.calculate(
            symbol="IBIT",
            etf_prices=sample_prices,
            benchmark_prices=sample_prices,
        )
        
        assert coord.symbol == "IBIT"
        assert 50 < coord.rs_ratio < 150  # Reasonable range
        assert 50 < coord.rs_momentum < 150
        assert isinstance(coord.quadrant, Quadrant)
    
    def test_quadrant_classification(self, rrg_engine):
        """Should classify quadrants correctly."""
        from app.models.domain import RRGCoordinate
        
        assert RRGCoordinate.determine_quadrant(105, 105) == Quadrant.LEADING
        assert RRGCoordinate.determine_quadrant(105, 95) == Quadrant.WEAKENING
        assert RRGCoordinate.determine_quadrant(95, 95) == Quadrant.LAGGING
        assert RRGCoordinate.determine_quadrant(95, 105) == Quadrant.IMPROVING
    
    def test_insufficient_data_raises_error(self, rrg_engine):
        """Should raise error for insufficient data."""
        from app.core.exceptions import InsufficientDataError
        
        short_data = [
            PricePoint(
                date=date(2026, 1, i),
                open=100, high=101, low=99, close=100, volume=1000000,
            )
            for i in range(1, 5)
        ]
        
        with pytest.raises(InsufficientDataError):
            rrg_engine.calculate("TEST", short_data, short_data)
```

### 11.2 Integration Tests

```python
# tests/integration/test_api.py

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestRRGEndpoints:
    """Test RRG API endpoints."""
    
    def test_health_check(self, client):
        """Health endpoint should return 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_dashboard_returns_data(self, client):
        """Dashboard endpoint should return valid data."""
        response = client.get("/api/v1/rrg/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "risk_assets" in data
        assert "safe_haven_assets" in data
        assert "regime" in data
        assert "top_picks" in data
        assert "action_groups" in data
        assert "insights" in data
        
        # Verify regime
        assert data["regime"]["regime"] in ["risk_on", "risk_off", "neutral"]
        assert -10 <= data["regime"]["score"] <= 10
```

---

## 12. Deployment

### 12.1 Environment Variables

```bash
# .env.example

# Database
DATABASE_URL=postgresql://postgres.xxx:[PASSWORD]@xxx.pooler.supabase.com:6543/postgres

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Cache
CACHE_TTL=900

# Logging
LOG_LEVEL=INFO
```

### 12.2 requirements.txt

```txt
# Core
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0

# Database
sqlalchemy>=2.0.0
asyncpg>=0.28.0
psycopg2-binary>=2.9.0

# Data
yfinance>=0.2.28
pandas>=2.0.0
numpy>=1.24.0
httpx>=0.24.0

# Caching
cachetools>=5.3.0

# Scheduler
apscheduler>=3.10.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# Utilities
python-dotenv>=1.0.0
```

### 12.3 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 13. Summary Checklist

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION CHECKLIST                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  BACKEND:                                                                    │
│  ☐ Project structure setup                                                  │
│  ☐ Constants & Enums (constants.py, enums.py)                              │
│  ☐ Custom exceptions (exceptions.py)                                       │
│  ☐ Domain models (domain.py)                                               │
│  ☐ API schemas (schemas.py)                                                │
│  ☐ DataFetcher service (Yahoo Finance)                                     │
│  ☐ RRGEngine service (calculation)                                         │
│  ☐ RegimeDetector service                                                  │
│  ☐ RecommendationEngine service                                            │
│  ☐ API endpoints                                                           │
│  ☐ Dependency injection                                                    │
│  ☐ Database schema (Supabase)                                              │
│  ☐ Unit tests                                                              │
│  ☐ Integration tests                                                       │
│                                                                              │
│  FRONTEND:                                                                   │
│  ☐ TypeScript types                                                        │
│  ☐ React Query hook                                                        │
│  ☐ RRGChart component                                                      │
│  ☐ RegimeIndicator component                                               │
│  ☐ ETFLegend component                                                     │
│  ☐ Recommendation component                                                │
│  ☐ Insights component                                                      │
│  ☐ Styling (match v3 design)                                               │
│                                                                              │
│  DEPLOYMENT:                                                                 │
│  ☐ Environment setup                                                       │
│  ☐ Docker configuration                                                    │
│  ☐ Render.com deployment                                                   │
│  ☐ Supabase connection                                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. Reference Files

| File | Location |
|------|----------|
| UI Design (HTML) | `rrg_rotation_map_v3.html` |
| Database Setup | `Supabase_Setup_Guide.md` |
| Database Manager | `database_postgresql.py` |

---

**End of Specification**

*Document prepared for Kimi Development Team*  
*Orbix Invest — February 2026*
