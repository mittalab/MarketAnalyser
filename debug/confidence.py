def compute_confidence(snapshot):
    score = 0
    max_score = 6

    if snapshot["market_state"] in ["ACCUMULATION", "EXPANSION"]:
        score += 1

    if snapshot["ORB"] > 0:
        score += 1

    if snapshot["ORB_momentum"] > 0:
        score += 1

    if snapshot["put_trend"] > 0:
        score += 1

    if snapshot["final_signal"] != "HOLD":
        score += 1

    if snapshot["raw_signal"] == snapshot["final_signal"]:
        score += 1

    return round(score / max_score, 2)