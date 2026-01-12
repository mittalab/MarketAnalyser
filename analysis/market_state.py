def classify_market_state(price_oi):
    """
    price_oi: output from analyze_futures_oi
    """

    if price_oi["price_up"] and price_oi["oi_up"]:
        return "ACCUMULATION"

    if price_oi["price_up"] and price_oi["oi_down"]:
        return "RISK_TRANSFER"

    if price_oi["price_down"] and price_oi["oi_up"]:
        return "DISTRIBUTION"

    if price_oi["price_down"] and price_oi["oi_down"]:
        return "UNWINDING"

    return "NEUTRAL"