import logging

logger = logging.getLogger(__name__)

class StockContext:
    def __init__(self, symbol):
        self.symbol = symbol
        self.market_state = None
        self.price_oi = None
        self.option_zones = None
        self.levels = None
        self.signal = None
        logger.info(f"Created new stock context for {self.symbol}")

    def update(self, market_state, price_oi, option_zones, levels, signal):
        logger.debug(f"Updating stock context for {self.symbol} with: "
                     f"market_state={market_state}, price_oi={price_oi}, "
                     f"option_zones={option_zones}, levels={levels}, signal={signal}")
        self.market_state = market_state
        self.price_oi = price_oi
        self.option_zones = option_zones
        self.levels = levels
        self.signal = signal
