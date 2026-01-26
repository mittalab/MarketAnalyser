import logging

logger = logging.getLogger(__name__)

def define_levels(spot_price, option_zones):
    support_zone = min(option_zones["put_support"], spot_price)
    resistance_zone = max(option_zones["call_resistance"], spot_price)

    logger.info(f"Support zone: {support_zone}, Resistance zone: {resistance_zone}")

    return {
        "support_zone": support_zone,
        "resistance_zone": resistance_zone
    }