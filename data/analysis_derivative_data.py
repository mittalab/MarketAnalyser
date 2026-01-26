import calendar
import datetime
# from typing import List, Dict, Optional
from data.fyers_client import get_fyers_client
from data.storage import save_csv
from data.storage import load_csv
from main import logger
from utils.expiry import get_first_day_of_this_expiry
from utils.expiry import get_expiry_YYMMM
from utils.util import datetime_to_YYYY_MM_DD
from data.fetch_futures_oi import get_hitorical_futures_oi
from data.fetch_options import fetch_option_chain
from data.CandleResolution import CandleResolution
import pandas as pd

FUTURES_PATH_BASE = "C:/Users/Abhishek/Trading_Projects/MarketAnalyser/storage/storage/futures"
OPTIONS_PATH_BASE = "C:/Users/Abhishek/Trading_Projects/MarketAnalyser/storage/storage/options"
Exchange = "NSE"


def populate_options_data(SYMBOL: str, ExpDate: str):

    OPTIONS_PATH = OPTIONS_PATH_BASE + "/" + ExpDate
    fyers = get_fyers_client()
    options_file = f"{Exchange}_{SYMBOL}_{ExpDate}_OPTIONS.csv"
    data_from_file = load_csv(OPTIONS_PATH, options_file)

    new_data = fetch_option_chain(fyers, Exchange, SYMBOL)

    # File doesn't exist; fetching all historical data
    if data_from_file is None:
        data_from_file = new_data
    else:
        # last_date_fetched = data_from_file[-1]
        data_from_file.append(new_data)

    save_csv(data_from_file, OPTIONS_PATH, options_file)

def populate_futures_data(SYMBOL: str, ExpDate: str):

    today_datetime = datetime.datetime.now()
    to_date = datetime_to_YYYY_MM_DD(today_datetime)

    FUTURES_PATH = FUTURES_PATH_BASE + "/" + ExpDate
    fyers = get_fyers_client()
    futures_file = f"{Exchange}_{SYMBOL}_{ExpDate}_FUT.csv"
    data_from_file = load_csv(FUTURES_PATH, futures_file)

    # File doesn't exist; fetching all historical data
    if data_from_file is None:
        historical_date = get_first_day_of_this_expiry(ExpDate, calendar.MONDAY)
        from_date = datetime_to_YYYY_MM_DD(historical_date)
        logger.debug(f"Futures file not found for {SYMBOL}, fetching historical data from {from_date} to {to_date}")
        data_from_file = get_hitorical_futures_oi(fyers, Exchange, SYMBOL, ExpDate, from_date, to_date, CandleResolution.DAY_1, 0.0)
    else:
        last_date_str = data_from_file[-1]['time']
        last_date = datetime.datetime.fromtimestamp(int(last_date_str))
        logger.info(f"Last date found in futures file for {SYMBOL}: {last_date.date()}")
        from_date = datetime_to_YYYY_MM_DD(last_date + datetime.timedelta(days=1))
        logger.debug(f"Futures file found for {SYMBOL}, fetching new data from {from_date} to {to_date}")
        new_data = get_hitorical_futures_oi(fyers, Exchange, SYMBOL, ExpDate, from_date, to_date, CandleResolution.DAY_1, data_from_file[-1]['oi'])
        for data in new_data:
            data_from_file.append(data)

    # TODO: ASSUMPTION : data_from_file is sorted from time
    save_csv(data_from_file, FUTURES_PATH, futures_file)

    futures_df = pd.DataFrame(
        data_from_file,
        columns=["time", "fut_open", "fut_high", "fut_low", "fut_close", "fut_volume", "oi", "spot_close"]
    )

    futures_df = futures_df.sort_values(by="time", ascending=True)
    futures_df["date"] = pd.to_datetime(
        futures_df["time"], unit="s"
    ).dt.strftime("%Y-%m-%d")
    futures_df.drop(columns=["time"], inplace=True)

    futures_df.columns = ["open", "high", "low", "close", "volume", "oi", "spot_close", "date"]

    futures_df = futures_df.astype({
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "int64",
        "oi": "int64",
        "spot_close": "float64",
    })

    return futures_df


def populate_derivatives_data(SYMBOL: str, ExpDate: str):
    futures_df = populate_futures_data(SYMBOL, ExpDate)
    options_df = populate_options_data(SYMBOL, ExpDate)
    return futures_df, options_df

def test():
    today_datetime = datetime.datetime.now()
    ExpDate = get_expiry_YYMMM(today_datetime)
    populate_futures_data("M&M", ExpDate)


test()