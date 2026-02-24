"""Generate Final Verdict based on all dashboard data."""
from typing import Dict, Any, List


def generate_final_verdict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Final Verdict with stance, DO/DON'T lists, and WAIT FOR triggers.
    
    Args:
        data: Full dashboard data including macro, cdc, fear_greed, whale, etc.
    
    Returns:
        Dict with stance, doList, dontList, waitFor
    """
    # Extract data
    macro = data.get("macro", {})
    key_levels = data.get("key_levels", {})
    crypto_pulse = data.get("crypto_pulse", {})
    sectors = data.get("sectors", {})
    calendar = data.get("calendar", {})
    
    # Get individual values
    macro_score = macro.get("adjusted_score", 2.5)
    
    # Get CDC signal
    btc_data = key_levels.get("btc", {})
    cdc_signal = btc_data.get("cdc_signal", {}).get("signal", "NEUTRAL")
    btc_s1 = btc_data.get("levels", {}).get("s1", 65000)
    
    # Get Fear & Greed
    fear_greed = crypto_pulse.get("fear_greed", {}).get("value", 50)
    
    # Get Whale signal
    whale = crypto_pulse.get("whale", {})
    whale_signal = whale.get("signal", "NEUTRAL")
    
    # Get best sector
    sector_list = sectors.get("sectors", [])
    best_sector = None
    if sector_list:
        best_sector = max(sector_list, key=lambda s: s.get("avg_return_7d", 0))
    
    # Get key event
    key_event = calendar.get("key_event")
    
    # Count capitulating sectors
    capitulating_count = sum(1 for s in sector_list if s.get("avg_return_7d", 0) < -10)
    
    # ═══════════════════════════════════════════════════════════════
    # DETERMINE STANCE
    # ═══════════════════════════════════════════════════════════════
    
    stance = None
    
    # AGGRESSIVE: All green lights
    if macro_score >= 4 and cdc_signal == "BULLISH" and fear_greed < 30:
        stance = {
            "text": "AGGRESSIVE",
            "color": "green",
            "emoji": "🟢",
            "bgColor": "rgba(0, 255, 136, 0.1)",
            "borderColor": "#00ff88"
        }
    # RISK-OFF: Macro very weak
    elif macro_score < 2:
        stance = {
            "text": "RISK-OFF / WAIT",
            "color": "red",
            "emoji": "🔴",
            "bgColor": "rgba(255, 68, 68, 0.1)",
            "borderColor": "#ff4444"
        }
    # DEFENSIVE ACCUMULATION: Bearish but extreme fear = opportunity
    elif cdc_signal == "BEARISH" and fear_greed <= 15:
        stance = {
            "text": "DEFENSIVE ACCUMULATION",
            "color": "orange",
            "emoji": "🟠",
            "bgColor": "rgba(255, 165, 0, 0.1)",
            "borderColor": "#ffa500"
        }
    # BALANCED: Default
    else:
        stance = {
            "text": "BALANCED",
            "color": "yellow",
            "emoji": "🟡",
            "bgColor": "rgba(255, 170, 0, 0.1)",
            "borderColor": "#ffaa00"
        }
    
    # ═══════════════════════════════════════════════════════════════
    # GENERATE "DO" LIST
    # ═══════════════════════════════════════════════════════════════
    
    do_list = []
    
    # Extreme fear = DCA opportunity
    if fear_greed <= 15:
        do_list.append("DCA 5-10% at current levels")
    
    # Bearish = set limit orders at support
    if cdc_signal == "BEARISH" and btc_s1:
        do_list.append(f"Set limit orders at S1 (${btc_s1:,.0f})")
    
    # Best sector outperforming
    if best_sector and best_sector.get("avg_vs_btc_7d", 0) > 0:
        do_list.append(f"Focus: BTC > {best_sector.get('sector', 'Best')}")
    
    # Bullish = scale in
    if cdc_signal == "BULLISH" and macro_score >= 3:
        do_list.append("Scale into positions")
    
    # Default if empty
    if not do_list:
        do_list.append("Monitor and wait for clarity")
    
    # ═══════════════════════════════════════════════════════════════
    # GENERATE "DON'T" LIST
    # ═══════════════════════════════════════════════════════════════
    
    dont_list = []
    
    # Extreme fear = don't panic sell
    if fear_greed <= 15:
        dont_list.append("Panic sell")
    
    # Distribution = don't go all-in
    if whale_signal == "DISTRIBUTION":
        dont_list.append("Go all-in")
    
    # Many sectors capitulating = don't chase alts
    if capitulating_count >= 3:
        dont_list.append("Chase weak sectors")
    
    # Extreme greed = don't FOMO
    if fear_greed >= 80:
        dont_list.append("FOMO into pumps")
    
    # Default if empty
    if not dont_list:
        dont_list.append("Overleverage")
    
    # ═══════════════════════════════════════════════════════════════
    # GENERATE "WAIT FOR" LIST
    # ═══════════════════════════════════════════════════════════════
    
    wait_for = []
    
    # CDC bearish = wait for flip
    if cdc_signal == "BEARISH":
        wait_for.append("CDC → BULLISH")
    
    # Distribution = wait for accumulation
    if whale_signal == "DISTRIBUTION":
        wait_for.append("Whale → ACCUMULATION")
    
    # Key event coming
    if key_event:
        date_str = key_event.get("date", "")
        name_str = key_event.get("event", "")
        if date_str and name_str:
            wait_for.append(f"{date_str} {name_str}")
    
    # CDC bullish but neutral = wait for confirmation
    if cdc_signal == "NEUTRAL":
        wait_for.append("CDC Signal confirmation")
    
    # ═══════════════════════════════════════════════════════════════
    # RETURN RESULT
    # ═══════════════════════════════════════════════════════════════
    
    return {
        "stance": stance,
        "do_list": do_list,
        "dont_list": dont_list,
        "wait_for": wait_for
    }
