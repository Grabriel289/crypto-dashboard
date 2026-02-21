"""Test market prices endpoint."""
import asyncio
from api.routes.dashboard import get_market_prices

async def test():
    print("Testing market prices...")
    result = await get_market_prices()
    print(f"Result: {result}")

asyncio.run(test())
