import logging

logger = logging.getLogger(__name__)

def build_execution_plan(
        signal,
        levels,
        today_close,
        instrument
):
    logger.debug(f"Building execution plan with signal: {signal}, levels: {levels}, today_close: {today_close}, instrument: {instrument}")
    if signal not in ["LONG", "SHORT"]:
        logger.warning(f"Invalid signal: {signal}. No execution plan will be built.")
        return None

    plan = {
        "signal": signal,
        "instrument": instrument,
        "open_entry": None,
        "pullback_entry": None,
        "no_trade_after": "12:00"
    }

    if signal == "LONG":
        plan["open_entry"] = {
            "type": "LIMIT",
            "price": today_close * 1.002  # small continuation
        }
        plan["pullback_entry"] = {
            "type": "LIMIT",
            "price": levels["support_zone"]
        }

    if signal == "SHORT":
        plan["open_entry"] = {
            "type": "LIMIT",
            "price": today_close * 0.998
        }
        plan["pullback_entry"] = {
            "type": "LIMIT",
            "price": levels["resistance_zone"]
        }

    logger.info(f"Execution plan built: {plan}")
    return plan
