def apply_option_rules(
        futures_state,
        futures_signal,
        option_metrics,
        orb_threshold=0
):
    """
    futures_signal: LONG / SHORT / HOLD
    """

    DPI = option_metrics["DPI"]
    USI = option_metrics["USI"]
    ORB = option_metrics["ORB"]

    # -------------------------
    # ACCUMULATION regime
    # -------------------------
    if futures_state == "ACCUMULATION":
        if ORB > orb_threshold:
            return futures_signal  # confirmed
        else:
            return "HOLD"

    # -------------------------
    # EXPANSION regime
    # -------------------------
    if futures_state == "EXPANSION":
        if USI < 0:
            return futures_signal
        else:
            return "HOLD"

    # -------------------------
    # DISTRIBUTION / RISK TRANSFER
    # -------------------------
    if futures_state in ["DISTRIBUTION", "RISK_TRANSFER"]:
        if ORB < 0:
            return futures_signal
        else:
            return "HOLD"

    return futures_signal

def apply_migration_rules(
        futures_state,
        current_signal,
        migration_trend
):
    """
    Modifies signal based on bucket migration trends.
    """

    put_trend = migration_trend.get("put_trend", 0)
    call_trend = migration_trend.get("call_trend", 0)

    # -----------------------------------
    # ACCUMULATION regime
    # -----------------------------------
    if futures_state == "ACCUMULATION":
        # Support not rising → no confidence
        if put_trend <= 0:
            return "HOLD"
        return current_signal

    # -----------------------------------
    # EXPANSION regime
    # -----------------------------------
    if futures_state == "EXPANSION":
        # Resistance tightening → caution
        if call_trend < 0:
            return "HOLD"
        return current_signal

    # -----------------------------------
    # DISTRIBUTION / RISK TRANSFER
    # -----------------------------------
    if futures_state in ["DISTRIBUTION", "RISK_TRANSFER"]:
        # Supply tightening confirms exit / short
        if call_trend < 0:
            return current_signal
        return "HOLD"

    return current_signal

def compute_migration_trend(migration_history, lookback=5):
    """
    migration_history: list of daily migration dicts (ordered by date)
    """

    if len(migration_history) < lookback:
        return {
            "put_trend": 0,
            "call_trend": 0
        }

    recent = migration_history[-lookback:]

    put_values = [m["put_atm_strike"] for m in recent if m["put_atm_strike"]]
    call_values = [m["call_atm_strike"] for m in recent if m["call_atm_strike"]]

    put_trend = put_values[-1] - put_values[0] if len(put_values) >= 2 else 0
    call_trend = call_values[-1] - call_values[0] if len(call_values) >= 2 else 0

    return {
        "put_trend": put_trend,
        "call_trend": call_trend
    }
