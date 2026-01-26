import datetime
from data.fyers_client import get_fyers_client
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_option_chain(fyers, exchg, symbol_eq):
    symbol = exchg + ":" + symbol_eq + "-EQ"
    logger.info(f"Fetching option chain for {symbol}")
    data = {"symbol": symbol, "strikecount": 50, "timestamp": ""}
    response = fyers.optionchain(data=data)
    records = []

    if "data" not in response or "optionsChain" not in response["data"]:
        logger.warning(f"Could not parse option chain for {symbol}, returning empty dataframe. Response: {response}")
        return pd.DataFrame()

    data = response["data"]
    data["fetched_datetime"] = datetime.datetime.now()

    results = []
    results.append(data)
    return results
    # for item in response["data"]["optionsChain"]:
    #     # Skip underlying / non-option rows
    #     if item.get("option_type") not in ("CE", "PE"):
    #         continue
    #
    #     records.append({
    #         "strike": item["strike_price"],
    #         "type": item["option_type"],  # CE / PE
    #         "oi": item["oi"],
    #         "oi_change": item["oich"],
    #         "oi_change_pct": item["oichp"],
    #         "bid": item["bid"],
    #         "ask": item["ask"],
    #         "ltp": item["ltp"],
    #         "volume": item["volume"]
    #     })
    #
    # logger.debug(f"Parsed {len(records)} option records for {symbol}")
    # return pd.DataFrame(records)

def test():
    fyers = get_fyers_client()
    print(fetch_option_chain(fyers, "NSE", "JIOFIN"))

    #1768348800, 3675.4, 3683, 3637.6, 3652.2, 953000, 17685800

# test()