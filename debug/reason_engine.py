def build_reason(snapshot):
    reasons = []

    # Regime
    reasons.append(f"Market state = {snapshot['market_state']}")

    # Futures vs signal
    if snapshot["market_state"] == "ACCUMULATION" and snapshot["raw_signal"] == "SHORT":
        reasons.append("Price pullback inside accumulation")

    # Option flow
    if snapshot["ORB"] > 0:
        reasons.append("Risk absorbed (ORB positive)")
    else:
        reasons.append("Risk transferred (ORB negative)")

    # Momentum
    if snapshot["ORB_momentum"] > 0:
        reasons.append("Absorption strengthening")
    elif snapshot["ORB_momentum"] < 0:
        reasons.append("Absorption weakening")

    # Migration
    if snapshot["put_trend"] > 0:
        reasons.append("Support rising")
    if snapshot["call_trend"] < 0:
        reasons.append("Resistance tightening")

    # Final
    reasons.append(f"Final signal = {snapshot['final_signal']}")

    return "; ".join(reasons)