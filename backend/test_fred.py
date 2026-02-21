"""Test FRED data fetching."""
import asyncio
from data.fetchers.fred import fred_fetcher

async def test_fred():
    print("Testing FRED data fetching...")
    print("=" * 50)
    
    # Test NFCI
    print("\n1. NFCI (Chicago Fed National Financial Conditions Index)")
    try:
        nfci = await fred_fetcher.fetch_nfci()
        print(f"   Result: {nfci}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test HY Spread
    print("\n2. High Yield Spread (BAMLH0A0HYM2)")
    try:
        hy = await fred_fetcher.fetch_hy_spread()
        print(f"   Result: {hy}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test Net Liquidity
    print("\n3. Net Liquidity (WALCL - WTREGEN - RRPONTSYD)")
    try:
        net_liq = await fred_fetcher.calculate_net_liquidity()
        print(f"   Result: {net_liq}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test_fred())
