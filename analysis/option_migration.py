def get_weighted_strike(rows):
    """
    rows: list of option rows in a bucket
    """
    if not rows:
        return None

    total_oi = sum(r["oi"] for r in rows)
    if total_oi == 0:
        return None

    return sum(r["strike"] * r["oi"] for r in rows) / total_oi

def compute_daily_migration(buckets):
    """
    buckets: output of build_option_buckets()
    """

    put_atm_strike = get_weighted_strike(buckets["PUT_ATM"])
    call_atm_strike = get_weighted_strike(buckets["CALL_ATM"])

    return {
        "put_atm_strike": put_atm_strike,
        "call_atm_strike": call_atm_strike
    }

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
