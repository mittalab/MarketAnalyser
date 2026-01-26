from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

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
    
    logger.info(f"Fetching OHLC data for {symbol} from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")

    response = fyers.history(data)

    if "candles" in response:
        logger.debug("Successfully fetched candles.")
        return response["candles"]
    else:
        logger.warning(f"Could not fetch candles for {symbol}. Response: {response}")
        return []
