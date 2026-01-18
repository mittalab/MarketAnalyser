import numpy as np

def classify_market_state_futures(
        futures_df,
        lookback=7,
        dominance_threshold=0.5
):
    """
    futures_df must contain:
    date, close, oi
    """

    if len(futures_df) < lookback + 1:
        return "NEUTRAL"

    recent = futures_df.tail(lookback + 1).copy()

    price_diff = recent["close"].diff().iloc[1:]
    oi_diff = recent["oi"].diff().iloc[1:]

    acc_days = 0
    risk_transfer_days = 0
    short_build_days = 0
    unwind_days = 0

    for p, o in zip(price_diff, oi_diff):
        if p > 0 and o > 0:
            acc_days += 1
        elif p > 0 and o < 0:
            risk_transfer_days += 1
        elif p < 0 and o > 0:
            short_build_days += 1
        elif p < 0 and o < 0:
            unwind_days += 1

    total = lookback

    if acc_days / total >= dominance_threshold:
        return "ACCUMULATION"

    if short_build_days / total >= dominance_threshold:
        return "DISTRIBUTION"

    if risk_transfer_days / total >= dominance_threshold:
        return "RISK_TRANSFER"

    return "NEUTRAL"
