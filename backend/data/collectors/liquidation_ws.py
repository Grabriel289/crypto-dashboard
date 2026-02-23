"""WebSocket Liquidation Collector - Real-time from Binance Futures."""
import json
import asyncio
import websockets
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Optional, List
import threading


class LiquidationWebSocketCollector:
    """
    Collect real-time liquidations from Binance WebSocket.
    
    WebSocket URL: wss://fstream.binance.com/ws/!forceOrder@arr
    
    This collects ALL liquidation orders across ALL symbols on Binance Futures.
    """
    
    WEBSOCKET_URL = "wss://fstream.binance.com/ws/!forceOrder@arr"
    
    def __init__(self, symbols: List[str] = None, on_liquidation: Callable = None):
        """
        Args:
            symbols: List of symbols to track (None = all)
            on_liquidation: Callback function when liquidation received
        """
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.on_liquidation = on_liquidation
        self.running = False
        self.ws = None
        self._buffer: List[Dict[str, Any]] = []
        self._buffer_lock = threading.Lock()
        self._last_flush = datetime.now()
        self.BUFFER_SIZE = 50
        self.FLUSH_INTERVAL = 10  # seconds
        self._stats = {
            "total_received": 0,
            "long_liquidations": 0,
            "short_liquidations": 0,
            "total_usd": 0.0
        }
    
    def _parse_liquidation(self, data: Dict) -> Optional[Dict[str, Any]]:
        """Parse WebSocket liquidation message."""
        try:
            if 'o' not in data:
                return None
            
            order = data['o']
            symbol = order['s']
            
            # Filter by symbols
            if self.symbols and symbol not in self.symbols:
                return None
            
            # Parse liquidation
            price = float(order['p'])
            quantity = float(order['q'])
            timestamp = datetime.fromtimestamp(order['T'] / 1000)
            
            # Determine side
            # SELL = Long was liquidated (forced to sell)
            # BUY = Short was liquidated (forced to buy)
            side = 'LONG' if order['S'] == 'SELL' else 'SHORT'
            
            usd_value = price * quantity
            
            return {
                'timestamp': timestamp,
                'symbol': symbol,
                'side': side,
                'price': price,
                'quantity': quantity,
                'usd_value': usd_value,
                'price_level': round(price / 1000) * 1000,
                'hour_bucket': timestamp.replace(minute=0, second=0, microsecond=0),
                'raw_data': order
            }
            
        except Exception as e:
            print(f"Error parsing liquidation: {e}")
            return None
    
    async def _process_message(self, message: str):
        """Process incoming WebSocket message."""
        try:
            data = json.loads(message)
            liquidation = self._parse_liquidation(data)
            
            if not liquidation:
                return
            
            # Update stats
            self._stats["total_received"] += 1
            self._stats["total_usd"] += liquidation["usd_value"]
            if liquidation["side"] == "LONG":
                self._stats["long_liquidations"] += 1
            else:
                self._stats["short_liquidations"] += 1
            
            # Add to buffer
            with self._buffer_lock:
                self._buffer.append(liquidation)
            
            # Print for monitoring
            emoji = '🔴' if liquidation["side"] == "LONG" else '🟢'
            print(f"{emoji} {liquidation['side']} LIQ: {liquidation['symbol']} "
                  f"${liquidation['usd_value']:,.0f} @ ${liquidation['price']:,.0f}")
            
            # Call callback if provided
            if self.on_liquidation:
                try:
                    self.on_liquidation(liquidation)
                except Exception as e:
                    print(f"Error in liquidation callback: {e}")
            
            # Check if should flush
            await self._check_flush()
            
        except Exception as e:
            print(f"Error processing message: {e}")
    
    async def _check_flush(self):
        """Check if buffer should be flushed."""
        should_flush = False
        
        with self._buffer_lock:
            if len(self._buffer) >= self.BUFFER_SIZE:
                should_flush = True
            elif (datetime.now() - self._last_flush).seconds > self.FLUSH_INTERVAL:
                should_flush = True
        
        if should_flush:
            await self._flush_buffer()
    
    async def _flush_buffer(self):
        """Flush buffer (override for database storage)."""
        with self._buffer_lock:
            if not self._buffer:
                return
            
            buffer_copy = self._buffer.copy()
            self._buffer = []
            self._last_flush = datetime.now()
        
        # For now, just log - in production this would insert to database
        print(f"💾 Buffer flush: {len(buffer_copy)} liquidations")
        
        # TODO: Insert to database
        # for liq in buffer_copy:
        #     await db.insert_liquidation(liq)
    
    async def _connect(self):
        """Connect to WebSocket and listen for liquidations."""
        while self.running:
            try:
                print(f"🔌 Connecting to Binance Liquidation Stream...")
                
                async with websockets.connect(self.WEBSOCKET_URL) as ws:
                    self.ws = ws
                    print("✅ Connected to Binance Liquidation Stream")
                    
                    async for message in ws:
                        if not self.running:
                            break
                        await self._process_message(message)
                        
            except websockets.exceptions.ConnectionClosed:
                print("⚠️ WebSocket closed, reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"❌ WebSocket error: {e}, reconnecting in 5 seconds...")
                await asyncio.sleep(5)
    
    async def start(self):
        """Start collecting liquidations."""
        self.running = True
        await self._connect()
    
    def start_sync(self):
        """Start in synchronous context (for threading)."""
        self.running = True
        asyncio.run(self._connect())
    
    def start_background(self):
        """Start in background thread."""
        self.running = True
        thread = threading.Thread(target=self.start_sync, daemon=True)
        thread.start()
        print("🚀 Started liquidation collector in background")
        return thread
    
    async def stop(self):
        """Stop collecting."""
        self.running = False
        if self.ws:
            await self.ws.close()
        await self._flush_buffer()
        print("🛑 Liquidation collector stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            **self._stats,
            "buffer_size": len(self._buffer),
            "running": self.running
        }
    
    def get_buffer(self) -> List[Dict[str, Any]]:
        """Get current buffer contents."""
        with self._buffer_lock:
            return self._buffer.copy()


# Simple in-memory storage for liquidations (until database is implemented)
class LiquidationMemoryStore:
    """In-memory storage for recent liquidations."""
    
    def __init__(self, max_size: int = 1000):
        self.liquidations: List[Dict[str, Any]] = []
        self.max_size = max_size
        self._lock = threading.Lock()
    
    def add(self, liquidation: Dict[str, Any]):
        """Add liquidation to store."""
        with self._lock:
            self.liquidations.append(liquidation)
            # Keep only recent liquidations
            if len(self.liquidations) > self.max_size:
                self.liquidations = self.liquidations[-self.max_size:]
    
    def get_recent(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get liquidations from last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self._lock:
            return [liq for liq in self.liquidations if liq['timestamp'] > cutoff]
    
    def get_by_symbol(self, symbol: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get liquidations for specific symbol."""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self._lock:
            return [
                liq for liq in self.liquidations 
                if liq['symbol'] == symbol and liq['timestamp'] > cutoff
            ]
    
    def get_aggregated(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
        """Get aggregated liquidation data for heatmap."""
        liquidations = self.get_by_symbol(symbol, hours)
        
        long_liqs = {}
        short_liqs = {}
        
        for liq in liquidations:
            level = liq['price_level']
            if liq['side'] == 'LONG':
                long_liqs[level] = long_liqs.get(level, 0) + liq['usd_value']
            else:
                short_liqs[level] = short_liqs.get(level, 0) + liq['usd_value']
        
        return {
            'long_liquidations': long_liqs,
            'short_liquidations': short_liqs,
            'data_type': 'REALIZED',
            'period_hours': hours,
            'count': len(liquidations),
            'total_usd': sum(liq['usd_value'] for liq in liquidations)
        }


# Global instances
liquidation_collector = LiquidationWebSocketCollector()
liquidation_store = LiquidationMemoryStore()


def start_liquidation_collector():
    """Start the liquidation collector with memory store."""
    # Set up callback to store liquidations
    liquidation_collector.on_liquidation = liquidation_store.add
    liquidation_collector.start_background()
