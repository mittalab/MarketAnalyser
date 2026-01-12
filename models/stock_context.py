class StockContext:
    def __init__(self, symbol):
        self.symbol = symbol
        self.market_state = None
        self.price_oi = None
        self.option_zones = None
        self.levels = None
        self.signal = None

    def update(self, market_state, price_oi, option_zones, levels, signal):
        self.market_state = market_state
        self.price_oi = price_oi
        self.option_zones = option_zones
        self.levels = levels
        self.signal = signal
