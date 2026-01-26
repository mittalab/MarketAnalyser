def compute_orb_momentum(orb_history, lookback=3):
    """
    orb_history: list of dicts [{"date": ..., "ORB": ...}]
    lookback: window size

    returns float ORB_momentum
    """

    if len(orb_history) < lookback * 2:
        return 0.0  # not enough data → neutral

    recent = orb_history[-lookback:]
    prior = orb_history[-lookback*2:-lookback]

    recent_avg = sum(d["ORB"] for d in recent) / lookback
    prior_avg = sum(d["ORB"] for d in prior) / lookback

    return round(recent_avg - prior_avg, 2)

def apply_orb_momentum(
        market_state: str,
        current_signal: str,
        orb: float,
        orb_momentum: float
) -> str:
    """
    Applies ORB momentum as a confirmation filter.

    Rules:
    - Never flips direction
    - Only degrades to HOLD
    """

    # HOLD stays HOLD
    if current_signal == "HOLD":
        return "HOLD"

    # ACCUMULATION regime
    if market_state == "ACCUMULATION":
        if current_signal == "LONG":
            # Absorption slowing down
            if orb > 0 and orb_momentum < 0:
                return "HOLD"

    # DISTRIBUTION regime
    if market_state == "DISTRIBUTION":
        if current_signal == "SHORT":
            # Distribution losing force
            if orb < 0 and orb_momentum > 0:
                return "HOLD"

    return current_signal