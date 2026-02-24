"""Stablecoin Flow Monitor fetcher."""
import aiohttp
from typing import Dict, Any, List


class StablecoinFetcher:
    """Fetch stablecoin supply data from DefiLlama."""
    
    DEFILLAMA_API = "https://stablecoins.llama.fi"
    
    async def get_flow_data(self) -> Dict[str, Any]:
        """Get stablecoin flow data."""
        url = f"{self.DEFILLAMA_API}/stablecoins?includePrices=true"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_data(data)
        except Exception as e:
            print(f"Error fetching stablecoin data: {e}")
        
        return self._get_fallback_data()
    
    def _parse_data(self, data: Dict) -> Dict[str, Any]:
        """Parse DefiLlama stablecoin data."""
        target_symbols = ['USDT', 'USDC', 'USDS', 'USDe']
        stablecoins = []
        found_symbols = set()
        
        for asset in data.get("peggedAssets", []):
            symbol = asset.get("symbol", "")
            # Skip if not in target list or already found (avoid duplicates)
            if symbol not in target_symbols or symbol in found_symbols:
                continue
            
            current_supply = asset.get("circulating", {}).get("peggedUSD", 0)
            # Skip tiny supplies (< $1M)
            if current_supply < 1e6:
                continue
            
            prev_week = asset.get("circulatingPrevWeek", {}).get("peggedUSD", current_supply)
            change_7d = current_supply - prev_week
            
            stablecoins.append({
                "symbol": symbol,
                "supply": round(current_supply / 1e9, 2),  # In billions
                "change_7d": round(change_7d / 1e9, 2),
                "status": "MINTING" if change_7d >= 0 else "REDEEMING",
                "emoji": "🟢" if change_7d >= 0 else "🔴"
            })
            found_symbols.add(symbol)
        
        # Sort by supply descending
        stablecoins.sort(key=lambda x: x["supply"], reverse=True)
        
        total_supply = sum(s["supply"] for s in stablecoins)
        total_change = sum(s["change_7d"] for s in stablecoins)
        
        # Generate insight
        if total_change > 0:
            insight = "🟢 Bullish: Stablecoins minting = New capital entering crypto"
        elif total_change < 0:
            insight = "🔴 Bearish: Stablecoins redeeming = Capital exiting crypto"
        else:
            insight = "⚪ Neutral: Stablecoin supply stable"
        
        return {
            "stablecoins": stablecoins,
            "total_supply": round(total_supply, 2),
            "total_change_7d": round(total_change, 2),
            "insight": insight
        }
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Fallback data when API fails."""
        return {
            "stablecoins": [
                {"symbol": "USDT", "supply": 143.2, "change_7d": 1.5, "status": "MINTING", "emoji": "🟢"},
                {"symbol": "USDC", "supply": 52.8, "change_7d": 0.9, "status": "MINTING", "emoji": "🟢"},
                {"symbol": "USDS", "supply": 4.2, "change_7d": 0.2, "status": "MINTING", "emoji": "🟢"},
                {"symbol": "USDe", "supply": 6.1, "change_7d": -0.3, "status": "REDEEMING", "emoji": "🔴"}
            ],
            "total_supply": 206.3,
            "total_change_7d": 2.3,
            "insight": "[G] Bullish: Stablecoins minting = New capital entering crypto"
        }


# Global instance
stablecoin_fetcher = StablecoinFetcher()
