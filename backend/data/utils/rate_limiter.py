"""Rate limiter for Binance API to avoid hitting limits."""
import asyncio
import time
from typing import Optional
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    # Binance Futures API limits (per minute)
    max_weight_per_minute: int = 1200  # Default IP limit
    # Conservative: use 80% of limit
    safe_weight_limit: int = 960
    # Minimum delay between requests (ms)
    min_delay_ms: float = 50
    # Retry configuration
    max_retries: int = 3
    retry_delay_base: float = 1.0  # seconds


class BinanceRateLimiter:
    """
    Rate limiter for Binance API.
    
    Tracks request weight and enforces delays to stay within limits.
    Binance uses a weight system where different endpoints cost different amounts.
    """
    
    # Endpoint weights (approximate)
    WEIGHTS = {
        "ticker/price": 1,
        "openInterest": 1,
        "premiumIndex": 1,
        "fundingRate": 1,
        "depth": 10,  # Order book is heavier
        "klines": 2,
    }
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.current_minute_weight = 0
        self.last_request_time = 0
        self.minute_start = time.time()
        self._lock = asyncio.Lock()
    
    def _get_endpoint_weight(self, endpoint: str) -> int:
        """Get weight for an endpoint."""
        for key, weight in self.WEIGHTS.items():
            if key in endpoint:
                return weight
        return 1  # Default weight
    
    def _reset_minute_if_needed(self):
        """Reset minute counter if a minute has passed."""
        now = time.time()
        if now - self.minute_start >= 60:
            self.current_minute_weight = 0
            self.minute_start = now
    
    async def acquire(self, endpoint: str = ""):
        """
        Acquire permission to make a request.
        
        Args:
            endpoint: The API endpoint being called (for weight calculation)
        """
        async with self._lock:
            self._reset_minute_if_needed()
            
            weight = self._get_endpoint_weight(endpoint)
            now = time.time()
            
            # Calculate minimum delay since last request
            time_since_last = (now - self.last_request_time) * 1000  # ms
            if time_since_last < self.config.min_delay_ms:
                delay_ms = self.config.min_delay_ms - time_since_last
                await asyncio.sleep(delay_ms / 1000)
            
            # Check if we're approaching the limit
            if self.current_minute_weight + weight > self.config.safe_weight_limit:
                # Wait until next minute
                wait_time = 60 - (now - self.minute_start) + 1  # +1s buffer
                print(f"[RateLimiter] Approaching limit ({self.current_minute_weight}/{self.config.safe_weight_limit}), waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                self._reset_minute_if_needed()
            
            self.current_minute_weight += weight
            self.last_request_time = time.time()
    
    async def execute_with_retry(self, func, endpoint: str = "", *args, **kwargs):
        """
        Execute a function with rate limiting and retry logic.
        
        Args:
            func: The async function to execute
            endpoint: The API endpoint (for weight tracking)
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            The result of func
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                # Acquire rate limit permission
                await self.acquire(endpoint)
                
                # Execute the request
                result = await func(*args, **kwargs)
                return result
                
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                
                # Check if it's a rate limit error
                if "429" in str(e) or "rate limit" in error_str or "too many requests" in error_str:
                    wait_time = self.config.retry_delay_base * (2 ** attempt)  # Exponential backoff
                    print(f"[RateLimiter] Rate limited on {endpoint}, waiting {wait_time}s (attempt {attempt + 1}/{self.config.max_retries})...")
                    await asyncio.sleep(wait_time)
                    # Reset weight counter to be safe
                    self.current_minute_weight = 0
                elif attempt < self.config.max_retries - 1:
                    # Other error, retry with shorter delay
                    wait_time = self.config.retry_delay_base * (1.5 ** attempt)
                    print(f"[RateLimiter] Error on {endpoint}: {e}, retrying in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                else:
                    break  # No more retries
        
        # All retries exhausted
        raise last_exception if last_exception else Exception("Request failed after retries")


# Global rate limiter instance
binance_rate_limiter = BinanceRateLimiter()
