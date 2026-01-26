import logging

logger = logging.getLogger(__name__)

class Order:
    def __init__(self, symbol, side, quantity, price, order_type):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price
        self.order_type = order_type
        self.status = "PLANNED"
        logger.info(f"Created new order: {self}")

    def __repr__(self):
        return f"{self.side} {self.quantity} @ {self.price} ({self.order_type})"
