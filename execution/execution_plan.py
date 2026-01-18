def build_execution_plan(
        signal,
        levels,
        today_close,
        instrument
):
    if signal not in ["LONG", "SHORT"]:
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

    return plan
