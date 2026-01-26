import logging

logger = logging.getLogger(__name__)

def select_instrument(
        futures_spread_pct,
        event_risk=False,
        volatility_expected=False
):
    """
    Rule-based switch: Futures first, Options only if risk demands.
    """
    logger.debug(f"Selecting instrument with futures_spread_pct: {futures_spread_pct}, event_risk: {event_risk}, volatility_expected: {volatility_expected}")

    if futures_spread_pct <= 0.0005 and not event_risk:
        decision = {
            "instrument": "FUTURES",
            "reason": "Clean delta, tight spread"
        }
    else:
        decision = {
            "instrument": "OPTIONS",
            "reason": "Risk control / volatility / spread"
        }
    logger.info(f"Selected instrument: {decision['instrument']}, reason: {decision['reason']}")
    return decision

def is_spread_acceptable(bid, ask, max_pct=0.02):
    logger.debug(f"Checking if spread is acceptable with bid: {bid}, ask: {ask}, max_pct: {max_pct}")
    mid = (bid + ask) / 2
    spread_pct = (ask - bid) / mid
    result = spread_pct <= max_pct
    logger.debug(f"Spread percentage: {spread_pct}, acceptable: {result}")
    return result
