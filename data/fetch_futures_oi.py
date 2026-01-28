import logging
from data.fyers_client import get_fyers_client
from data.CandleResolution import CandleResolution
import time
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

def price_with_highest_volume(bids):
    logger.debug("Calculating price with highest volume")
    if not bids:
        logger.warning("Bids list is empty, cannot calculate price with highest volume")
        return None

    highest_volume_bid = max(bids, key=lambda x: x.get("volume", 0))
    return highest_volume_bid.get("price")

def fetch_futures_spot_oi(fyers, exchg, symbol, date):
    logger.info(f"Fetching futures and spot OI for {exchg}:{symbol} on {date}")
    curr_time = int(time.time())
    """
    Fetches latest Futures OI using FYERS quotes API.
    """
    futures_symbol = exchg + ":" + symbol + date + "FUT"
    fut_response = fyers.depth({"symbol": futures_symbol, "ohlcv_flag": "1"})
    if fut_response["s"] != "ok":
        logger.error(f"Failed to fetch futures OI for {futures_symbol}")
        raise Exception(f"Failed to fetch futures OI for {futures_symbol}")
    fut_quote = fut_response["d"][futures_symbol]

    spot_symbol = exchg + ":" + symbol + "-EQ"
    spot_response = fyers.depth({"symbol": spot_symbol, "ohlcv_flag": "1"})
    if spot_response["s"] != "ok":
        logger.error(f"Failed to fetch spot OI for {spot_symbol}")
        raise Exception(f"Failed to fetch spotures OI for {spot_symbol}")
    spot_quote = spot_response["d"][spot_symbol]
    
    logger.debug("Successfully fetched futures and spot OI")

    return {
        "time": curr_time,
        "fut_ltp": fut_quote.get("ltp"),
        "spot_ltp": spot_quote.get("ltp"),
        "bias": round(fut_quote.get("ltp") - spot_quote.get("ltp"), 2),
        "oi": fut_quote.get("oi"),
        "volume": fut_quote.get("v"),
        "bid": price_with_highest_volume(fut_quote.get("bids")), # TODO: It is possible that highest volumes is not giving true picture
        "ask": price_with_highest_volume(fut_quote.get("ask")),
        "oiperct_from_last_day": fut_quote.get("oipercent"),
        "oiperct_from_last_candle": fut_quote.get("oipercent"),
    }

def get_epoch_time (epoch_time: int, resolution: CandleResolution):
    if resolution == CandleResolution.DAY_1 or resolution == CandleResolution.DAY:
        return epoch_time + 10 * 60 * 60
    return epoch_time


def is_330pm_ist(epoch_ts: int) -> bool:
    IST = ZoneInfo("Asia/Kolkata")
    dt = datetime.fromtimestamp(epoch_ts, tz=IST)
    return dt.hour == 15 and dt.minute == 30

def get_hitorical_futures_oi(fyers, exchg, symbol, exp_date, range_from, range_to, resolution: CandleResolution, lastoi, lastclose):
    """
    Fetches latest Futures OI using FYERS quotes API.
    Response is an array with value order epochtime, open, high , low, close, volume, oi
    """
    logger.info(f"Fetching historical futures OI for {exchg}:{symbol} ({exp_date}) from {range_from} to {range_to} with {resolution} resolution")
    futures_symbol = exchg + ":" + symbol + exp_date + "FUT"
    fut_data = {
        "symbol":futures_symbol,
        "resolution":resolution.value,
        "date_format":"1",
        "range_from":range_from,
        "range_to":range_to,
        "cont_flag":"1",
        "oi_flag":"1"
    }
    fut_response = fyers.history(fut_data)

    if fut_response["s"] == "no_data":
        logger.warning(f"No historical futures OI data found for {futures_symbol}")
        return []

    if fut_response["s"] != "ok":
        logger.error(f"Failed to fetch historical futures OI for {futures_symbol}: {fut_response}")
        raise Exception(f"Failed to fetch historical futures OI for {futures_symbol}: {fut_response}")

    fut_data = fut_response["candles"]

    spot_symbol = exchg + ":" + symbol + "-EQ"
    spot_data = {
        "symbol":spot_symbol,
        "resolution":resolution.value,
        "date_format":"1",
        "range_from":range_from,
        "range_to":range_to,
        "cont_flag":"1"
    }
    spot_response = fyers.history(spot_data)
    if spot_response["s"] != "ok":
        logger.error(f"Failed to fetch historical spot data for {spot_symbol}: {spot_response}")
        raise Exception(f"Failed to fetch historical spot data for {spot_symbol}: {spot_response}")

    spot_data = spot_response["candles"]

    results = []

    last_candle_oi = fut_data[0][6]
    if int(lastoi) != 0:
        last_candle_oi = int(lastoi)
    last_day_oi = int(lastoi)

    for fut, spot in zip(fut_data, spot_data):
        epoch_time = get_epoch_time(fut[0], resolution)
        oi_change = fut[6] - last_candle_oi
        oiperct_from_last_candle = (fut[6] - last_candle_oi) / last_candle_oi * 100
        oiperct_from_last_day = 0
        if last_day_oi != 0:
            oiperct_from_last_day = (fut[6] - last_day_oi) / last_day_oi * 100

        last_price_change = fut[4] - lastclose
        result = {
            "time": epoch_time,
            "spot_close": spot[4],
            "fut_open": fut[1],
            "fut_high": fut[2],
            "fut_low": fut[3],
            "fut_close": fut[4],
            "bias": round(fut[4] - spot[4], 2),
            "oi": fut[6],
            "fut_volume": fut[5],
            "bid": 0,
            "ask": 0,
            "oiperct_from_last_day": round(oiperct_from_last_day, 2),
            "oiperct_from_last_candle": round(oiperct_from_last_candle, 2),
            "oi_change": oi_change,
            "last_price_change": last_price_change,
        }

        lastclose = fut[4]
        last_candle_oi = fut[6]
        if is_330pm_ist(epoch_time):
            last_day_oi = fut[6]

        results.append(result)
        
    logger.debug(f"Returning {len(results)} historical OI records")
    return results

def test():
    fyers = get_fyers_client()
    # futures_oi = fetch_futures_spot_oi(fyers, "NSE", "M&M", "26JAN")
    # logger.info(futures_oi)
    # get_hitorical_futures_oi(fyers, "NSE", "M&M", "26JAN", "2025-12-29", "2026-01-14", CandleResolution.MIN_15)
    # logger.info(get_hitorical_futures_oi(fyers, "NSE", "M&M", "26JAN", "2026-01-13", "2026-01-15", CandleResolution.MIN_15))
    # get_hitorical_futures_oi(fyers, "NSE", "M&M", "26JAN", "2026-01-13", "2026-01-15", CandleResolution.MIN_1)
    logger.info(get_hitorical_futures_oi(fyers, "NSE", "M&M", "26JAN", "2026-01-16", "2026-01-16", CandleResolution.DAY_1, 0.0))

    #1768348800, 3675.4, 3683, 3637.6, 3652.2, 953000, 17685800

# test()