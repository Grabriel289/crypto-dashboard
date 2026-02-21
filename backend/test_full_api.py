"""Test the full dashboard API response."""
import asyncio
import json
from api.routes.dashboard import get_full_dashboard

async def test():
    print("Testing /api/full endpoint...")
    print("=" * 60)
    
    result = await get_full_dashboard()
    
    # Check market_prices
    print("\n1. MARKET PRICES:")
    print(f"   Has market_prices: {'market_prices' in result}")
    if 'market_prices' in result:
        prices = result['market_prices']
        print(f"   Prices data: {prices}")
    else:
        print("   ERROR: market_prices missing!")
    
    # Check sectors
    print("\n2. SECTORS:")
    print(f"   Has sectors: {'sectors' in result}")
    if 'sectors' in result:
        sectors_data = result['sectors']
        sectors = sectors_data.get('sectors', [])
        print(f"   Number of sectors: {len(sectors)}")
        for s in sectors:
            top3_count = len(s.get('top_3_coins', []))
            print(f"   - {s['sector']}: {s.get('coin_count', 0)} coins, top_3_coins: {top3_count}")
    
    # Check PERP specifically
    print("\n3. PERP SECTOR:")
    if 'sectors' in result:
        sectors = result['sectors'].get('sectors', [])
        perp = [s for s in sectors if s['sector'] == 'PERP']
        print(f"   Found: {len(perp) > 0}")
        if perp:
            print(f"   Data: {perp[0]}")
        else:
            print("   ERROR: PERP sector not found!")
            print(f"   Available sectors: {[s['sector'] for s in sectors]}")
    
    # Check conflicts
    print("\n4. CONFLICTING SIGNALS:")
    print(f"   Has conflicts: {'conflicts' in result}")
    if 'conflicts' in result:
        print(f"   Data: {result['conflicts']}")
    
    print("\n" + "=" * 60)

asyncio.run(test())
