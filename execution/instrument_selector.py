def select_instrument(
        futures_spread_pct,
        event_risk=False,
        volatility_expected=False
):
    """
    Rule-based switch: Futures first, Options only if risk demands.
    """

    if futures_spread_pct <= 0.0005 and not event_risk:
        return {
            "instrument": "FUTURES",
            "reason": "Clean delta, tight spread"
        }

    return {
        "instrument": "OPTIONS",
        "reason": "Risk control / volatility / spread"
    }

def is_spread_acceptable(bid, ask, max_pct=0.02):
    mid = (bid + ask) / 2
    spread_pct = (ask - bid) / mid
    return spread_pct <= max_pct
