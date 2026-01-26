import logging

logger = logging.getLogger(__name__)

def size_futures_position(capital, risk_pct, entry, stop):
    logger.debug(f"Sizing futures position with capital: {capital}, risk_pct: {risk_pct}, entry: {entry}, stop: {stop}")
    risk_amount = capital * risk_pct
    risk_per_unit = abs(entry - stop)

    if risk_per_unit == 0:
        logger.warning("Risk per unit is 0, returning quantity of 0")
        return 0

    quantity = risk_amount // risk_per_unit
    logger.info(f"Calculated futures position size: {quantity}")
    return int(quantity)

def size_option_position(capital, risk_pct, premium):
    logger.debug(f"Sizing option position with capital: {capital}, risk_pct: {risk_pct}, premium: {premium}")
    max_loss = capital * risk_pct
    lots = max_loss // premium
    logger.info(f"Calculated option position size: {lots}")
    return int(lots)
