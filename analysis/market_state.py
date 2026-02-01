import logging
import numpy as np

logger = logging.getLogger(__name__)

def classify_market_state_futures(
        futures_df,
        lookback=7,
        dominance_threshold=0.5
):
    """
    futures_df must contain:
    date, close, oi
    """

    which_day = "UNWIND"
    last = futures_df.tail(1).copy()
    # print(last)
    p = float(last["last_price_change"])
    o = float(last["oi_change"])
    if p > 0.0 and o > 0.0:
        which_day = "ACCUMULATE"
    elif p > 0 and o < 0:
        which_day = "RISK TRANSFER"
    elif p < 0 and o > 0:
        which_day = "SHORT BUILD"

    if len(futures_df) < lookback + 1:
        logger.warning("Not enough data to classify market state, returning NEUTRAL")
        data = {
            "market_state": "NEUTRAL",
            "acc_days": 0,
            "short_build_days": 0,
            "risk_transfer_days": 0,
            "unwind_days": 0,
            "which_day": which_day,
        }
        return data

    recent = futures_df.tail(lookback + 1).copy()

    price_diff = recent["close"].diff().iloc[1:]
    oi_diff = recent["oi"].diff().iloc[1:]

    acc_days = 0
    risk_transfer_days = 0
    short_build_days = 0
    unwind_days = 0

    # TODO : thresholds for increase and decrease in OI / price
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

    logger.debug(
        f"Accumulation days: {acc_days}, "
        f"Distribution days: {short_build_days}, "
        f"Risk transfer days: {risk_transfer_days}, "
        f"Unwind days: {unwind_days}"
    )

    if acc_days / total >= dominance_threshold:
        market_state = "ACCUMULATION"
    elif short_build_days / total >= dominance_threshold:
        market_state = "DISTRIBUTION"
    elif risk_transfer_days / total >= dominance_threshold:
        market_state = "RISK_TRANSFER"
    else:
        market_state = "NEUTRAL"
    
    logger.info(f"Market state classified as: {market_state}")
    data = {
        "market_state": market_state,
        "acc_days": acc_days,
        "short_build_days": short_build_days,
        "risk_transfer_days": risk_transfer_days,
        "unwind_days": unwind_days,
        "which_day": which_day,
    }
    return data
