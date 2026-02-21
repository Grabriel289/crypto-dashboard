"""Test FRED data - simple version."""
import asyncio
from data.fetchers.fred import fred_fetcher

async def test():
    print("Testing FRED...")
    
    nfci = await fred_fetcher.fetch_nfci()
    if nfci:
        print(f"NFCI: {nfci.get('value')} (score: {nfci.get('score')})")
    else:
        print("NFCI: None")
    
    hy = await fred_fetcher.fetch_hy_spread()
    if hy:
        print(f"HY Spread: {hy.get('value')}% (score: {hy.get('score')})")
    else:
        print("HY Spread: None")
    
    net = await fred_fetcher.calculate_net_liquidity()
    if net:
        print(f"Net Liquidity: ${net.get('value_trillion')}T")
    else:
        print("Net Liquidity: None")

asyncio.run(test())
