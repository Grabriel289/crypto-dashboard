import asyncio
from data.fetchers.derivative_sentiment import derivative_sentiment_fetcher

async def test():
    result = await derivative_sentiment_fetcher.get_sentiment()
    print("Derivative Sentiment Test:")
    for symbol, data in result['coins'].items():
        print(f"  {symbol}: OI=${data['open_interest']:.2f}, Change={data['oi_change_24h']:.1f}%")
        print(f"    Retail Long: {data['retail_long_percent']:.1f}%")
        print(f"    Top Trader Long: {data['top_trader_long_percent']:.1f}%")
    print(f"\nSignal: {result['signal']}")

asyncio.run(test())
