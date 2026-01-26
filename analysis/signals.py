import logging

logger = logging.getLogger(__name__)

def generate_signal(market_state, price_oi, option_zones):
    logger.debug(f"Generating signal with market_state: {market_state}, price_oi: {price_oi}, option_zones: {option_zones}")
    if not option_zones:
        logger.warning("No option zones found, returning HOLD")
        return "HOLD"

    # LONG
    if (
        market_state in ["ACCUMULATION", "EXPANSION"]
        and price_oi["price_up"]
        and price_oi["oi_up"]
        and option_zones["put_oi_change"] > 0
        and option_zones["call_oi_change"] <= 0
    ):
        signal = "LONG"

    # SHORT
    elif (
        market_state in ["DISTRIBUTION", "RISK_TRANSFER"]
        and price_oi["price_down"]
        and price_oi["oi_up"]
        and option_zones["call_oi_change"] > 0
        and option_zones["put_oi_change"] <= 0
    ):
        signal = "SHORT"

    # EXIT (Risk transfer)
    elif price_oi["price_up"] and price_oi["oi_down"]:
        signal = "EXIT"
    
    else:
        signal = "HOLD"

    logger.info(f"Generated signal: {signal}")
    return signal
