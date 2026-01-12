import numpy as np

def analyze_futures_oi(candles, oi_series):
    """
    candles: list of OHLCV
    oi_series: list of daily OI values
    """

    closes = np.array([c[4] for c in candles])
    oi = np.array(oi_series)

    price_change = (closes[-1] - closes[-2]) / closes[-2]
    oi_change = (oi[-1] - oi[-2]) / oi[-2]

    return {
        "price_up": price_change > 0,
        "price_down": price_change < 0,
        "oi_up": oi_change > 0,
        "oi_down": oi_change < 0,
        "price_change": price_change,
        "oi_change": oi_change
    }
