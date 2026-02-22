#!/usr/bin/env python3
"""
Run the CoinGlass scraper to update derivative data.
This should be scheduled to run once per day.
"""
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.scrapers.coinglass_scraper import CoinGlassScraper

def main():
    print("="*60)
    print("CoinGlass Scraper - Daily Data Update")
    print("="*60)
    
    scraper = CoinGlassScraper()
    data = scraper.scrape_all_data()
    
    if data and data.get("coins"):
        print("\n[SUCCESS] Scraping completed!")
        print(f"📅 Next scrape: {data.get('next_scrape', '24 hours')}")
        
        # Show summary
        for symbol, coin_data in data["coins"].items():
            oi = coin_data.get("open_interest", 0)
            change = coin_data.get("oi_change_24h", 0)
            is_scraped = coin_data.get("is_scraped", False)
            source = "Scraped" if is_scraped else "Fallback"
            print(f"  {symbol}: OI=${oi/1e9:.2f}B ({change:+.1f}%) [{source}]")
        
        return 0
    else:
        print("\n[FAILED] Scraping - using fallback data")
        return 1

if __name__ == "__main__":
    exit(main())
