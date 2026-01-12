from datetime import datetime, timedelta

def fetch_ohlc(fyers, symbol, days=20):
    end = datetime.now()
    start = end - timedelta(days=days)

    data = {
        "symbol": symbol,
        "resolution": "D",
        "date_format": "1",
        "range_from": start.strftime("%Y-%m-%d"),
        "range_to": end.strftime("%Y-%m-%d"),
        "cont_flag": "1"
    }

    response = fyers.history(data)
    return response["candles"]
