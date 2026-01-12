def generate_signal(market_state, price_oi, option_zones):
    if not option_zones:
        return "HOLD"

    # LONG
    if (
        market_state in ["ACCUMULATION", "EXPANSION"]
        and price_oi["price_up"]
        and price_oi["oi_up"]
        and option_zones["put_oi_change"] > 0
        and option_zones["call_oi_change"] <= 0
    ):
        return "LONG"

    # SHORT
    if (
        market_state in ["DISTRIBUTION", "RISK_TRANSFER"]
        and price_oi["price_down"]
        and price_oi["oi_up"]
        and option_zones["call_oi_change"] > 0
        and option_zones["put_oi_change"] <= 0
    ):
        return "SHORT"

    # EXIT (Risk transfer)
    if price_oi["price_up"] and price_oi["oi_down"]:
        return "EXIT"

    return "HOLD"
