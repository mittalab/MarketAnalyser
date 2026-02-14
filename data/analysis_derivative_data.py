import calendar
import datetime
import time
import json
from typing import Callable, Any

# from typing import List, Dict, Optional
from data.fyers_client import get_fyers_client
from config.settings import HISTORICAL_DAYS
from data.storage import save_csv
from data.storage import load_csv
from config.logging_config import logger
from utils.expiry import is_trading_ongoing
from utils.expiry import get_expiry_YYMMM
from utils.expiry import get_first_day_of_this_expiry
from utils.expiry import get_historical_trade_date
from utils.expiry import get_last_trading_day
from utils.util import datetime_to_YYYY_MM_DD
from data.fetch_futures_oi import get_hitorical_futures_oi
from data.fetch_options import fetch_option_chain
from data.CandleResolution import CandleResolution
import pandas as pd
import ast

FUTURES_PATH_BASE = "C:\\Users\\Abhishek\\Trading_Projects\\MarketAnalyser\\storage\\futures"
OPTIONS_PATH_BASE = "C:\\Users\\Abhishek\\Trading_Projects\\MarketAnalyser\\storage\\options"
Exchange = "NSE"

def _retry(
        func: Callable[..., Any],
        *args,
        max_retries: int = 2,
        retry_delay: float = 1.0,
        **kwargs,
):
    """
    Retries a function call based on return status_code or exception.

    func: function to execute
    max_retries: maximum retry attempts
    retry_delay: delay (seconds) between retries
    retry_on_status: HTTP-like status codes to retry on
    retry_on_exception: exceptions that trigger retry
    """

    retry_on_status = (500, 502, 503, 504)
    attempt = 0

    while True:
        try:
            result = func(*args, **kwargs)

            # If response has status_code, evaluate it
            status_code = getattr(result, "status_code", None)

            if status_code is not None and status_code in retry_on_status:
                raise RuntimeError(f"Retryable status code: {status_code}")

            return result

        except RuntimeError as e:
            attempt += 1

            if attempt > max_retries:
                raise RuntimeError(
                    f"Retry failed after {max_retries} attempts"
                ) from e

            time.sleep(retry_delay)

def _safe_parse_option_chain(raw):
    """
    Parses optionChain string into Python list safely.
    Handles:
    - Python-style dict strings
    - JSON-style escaped strings
    """
    if raw is None or raw == "":
        return []

    try:
        return ast.literal_eval(raw)
    except Exception:
        # Fallback: try to normalize double-quoted JSON
        try:
            cleaned = raw.replace('""', '"')
            return ast.literal_eval(cleaned)
        except Exception:
            return []


def _flatten_option_chain_row(row):
    """
    Flattens ONE CSV row (any supported optionChain format)
    into list of normalized option rows.
    """
    flattened = []

    option_chain = _safe_parse_option_chain(row["optionsChain"])

    if not isinstance(option_chain, list):
        return flattened

    row_date = pd.to_datetime(row["fetched_datetime"]).date()

    for opt in option_chain:
        # Skip non-option or malformed rows
        opt_type = opt.get("option_type")
        if opt_type not in ("CE", "PE"):
            continue

        flattened.append({
            # Core identity
            "date": row_date,
            "strike": opt.get("strike_price"),
            "type": opt_type,

            # OI metrics
            "oi": opt.get("oi", 0),
            "oi_change": opt.get("oich", 0),

            "bid": opt.get("bid"),
            "ask": opt.get("ask"),
            # "ltp": opt.get("ltp"),
            #
            # # Volume & symbol (optional)
            # "volume": opt.get("volume", 0),
            # "symbol": opt.get("symbol"),
            #
            # # Snapshot context
            # "callOi_total": row.get("callOi"),
            # "putOi_total": row.get("putOi"),
        })

    return flattened

def populate_options_data(SYMBOL: str, ExpDate: str):

    trading_date = get_last_trading_day(datetime.datetime.now(), include_ongoingDay=False)
    OPTIONS_PATH = OPTIONS_PATH_BASE + "\\" + ExpDate
    options_file = f"{Exchange}_{SYMBOL}_{ExpDate}_OPTIONS.csv"
    data_from_file = load_csv(OPTIONS_PATH, options_file)

    fyers = get_fyers_client()
    # Fyers API provide the last data only
    new_data = _retry(lambda: fetch_option_chain(fyers, Exchange, SYMBOL))
    new_data[0]["fetched_datetime"] = pd.to_datetime(trading_date).strftime("%Y-%m-%d")

    if data_from_file is None:
        data_from_file = new_data
    else:
        date = new_data[0]["fetched_datetime"]
        if data_from_file[-1]["fetched_datetime"] != new_data[0]["fetched_datetime"]:
            data_from_file.append(new_data[0])
            save_csv(data_from_file, OPTIONS_PATH, options_file)
        else:
            print(f"Options data already exists for date {date} for symbol {SYMBOL}")

    options_df = pd.DataFrame(
        data_from_file,
        columns=["callOi", "expiryData", "indiavixData" , "optionsChain" , "putOi" , "fetched_datetime"]
       )

    options_df = options_df.sort_values(by="fetched_datetime", ascending=True)
    all_rows = []
    for _, row in options_df.iterrows():
        all_rows.extend(_flatten_option_chain_row(row))

    final_df = pd.DataFrame(all_rows)
    final_df = final_df.astype({
        "strike": "float64",
        "type": "str",
        "bid": "float64",
        "ask": "float64",
        "oi": "int64",
        "oi_change": "float64",
        "date": "str",
    })
    return final_df


def populate_futures_data(SYMBOL: str, ExpDate: str):

    today_datetime = datetime.datetime.now()
    market_close = datetime.datetime.combine(today_datetime.date(), datetime.time(15, 30))

    datetime_to_fetch_date = today_datetime
    if today_datetime < market_close:
        datetime_to_fetch_date = datetime_to_fetch_date - datetime.timedelta(days=1)

    to_date = datetime_to_YYYY_MM_DD(datetime_to_fetch_date)
    FUTURES_PATH = FUTURES_PATH_BASE + "/" + ExpDate
    fyers = get_fyers_client()
    futures_file = f"{Exchange}_{SYMBOL}_{ExpDate}_FUT.csv"
    data_from_file = load_csv(FUTURES_PATH, futures_file)
    # File doesn't exist; fetching all historical data
    if data_from_file is None:
        historical_date = get_first_day_of_this_expiry(ExpDate, calendar.TUESDAY)
        pull_back_historical_date = get_historical_trade_date(historical_date, HISTORICAL_DAYS)
        from_date = datetime_to_YYYY_MM_DD(pull_back_historical_date)
        logger.debug(f"Futures file not found for {SYMBOL}, fetching historical data from {from_date} to {to_date}")
        data_from_file = _retry(lambda: get_hitorical_futures_oi(fyers, Exchange, SYMBOL, ExpDate, from_date, to_date, CandleResolution.DAY_1, 0.0, 0.0))
    else:
        last_date_str = data_from_file[-1]['time']
        last_date = datetime.datetime.fromtimestamp(int(last_date_str))
        logger.info(f"Last date found in futures file for {SYMBOL}: {last_date.date()}")
        from_date = datetime_to_YYYY_MM_DD(last_date + datetime.timedelta(days=1))
        logger.debug(f"Futures file found for {SYMBOL}, fetching new data from {from_date} to {to_date}")
        if from_date <= to_date:
            new_data = _retry(lambda: get_hitorical_futures_oi(fyers, Exchange, SYMBOL, ExpDate, from_date, to_date, CandleResolution.DAY_1, data_from_file[-1]['oi'], data_from_file[-1]['fut_close']))
            for data in new_data:
                data_from_file.append(data)
        else:
            print("Latest futures data exists")

    # TODO: ASSUMPTION : data_from_file is sorted from time
    save_csv(data_from_file, FUTURES_PATH, futures_file)

    futures_df = pd.DataFrame(
        data_from_file,
        columns=["time", "fut_open", "fut_high", "fut_low", "fut_close", "fut_volume", "oi", "spot_close", "oi_change", "last_price_change"]
    )

    futures_df["date"] = pd.to_datetime(
        futures_df["time"], unit="s"
    ).dt.strftime("%Y-%m-%d")
    futures_df.drop(columns=["time"], inplace=True)
    futures_df = futures_df.sort_values(by="date", ascending=True)

    futures_df.columns = ["open", "high", "low", "close", "volume", "oi", "spot_close", "oi_change", "last_price_change", "date"]

    futures_df = futures_df.astype({
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "int64",
        "oi": "int64",
        "oi_change": "float64",
        "spot_close": "float64",
        "date": "str",
        "last_price_change": "float64",
    })

    return futures_df


def populate_derivatives_data(SYMBOL: str, ExpDate: str):
    if is_trading_ongoing():
        print(f"Trading is ongoing as per the time: {datetime.datetime.now()}. Can't populate data in ingoing trading session.")
        return

    futures_df = populate_futures_data(SYMBOL, ExpDate)
    options_df = populate_options_data(SYMBOL, ExpDate)
    return futures_df, options_df

def test():
    today_datetime = datetime.datetime.now()
    ExpDate = get_expiry_YYMMM(today_datetime)
    populate_derivatives_data("JIOFIN", ExpDate)
    # print(get_last_trading_day(datetime.datetime.now(), include_ongoingDay=False))
    # populate_futures_data("M&M", ExpDate)
    # print(populate_options_data("360ONE", "26FEB"))

# test()