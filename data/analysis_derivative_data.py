
import datetime

from data.fyers_client import get_fyers_client
from data.storage import save_csv
from data.storage import load_csv
from utils.expiry import get_last_month_Monday
from utils.expiry import get_expiry_YYMMM
from utils.util import datetime_to_YYYY_MM_DD
from data.fetch_futures_oi import get_hitorical_futures_oi
from data.CandleResolution import CandleResolution

FUTURES_PATH = "storage/futures"

import pandas as pd

def populate_futures_data(SYMBOL: str):

    today_datetime = datetime.datetime.now()
    ExpDate = get_expiry_YYMMM(today_datetime)
    to_date = datetime_to_YYYY_MM_DD(today_datetime)
    Exchange = "NSE"

    fyers = get_fyers_client()
    futures_file = f"{Exchange}_{SYMBOL}_{ExpDate}_FUT.csv"
    data_from_file = load_csv(FUTURES_PATH, futures_file)

    # File doesn't exist; fetching all historical data
    if data_from_file is None:
        historical_date = get_last_month_Monday(datetime.datetime.now())
        from_date = datetime_to_YYYY_MM_DD(historical_date)
        data_from_file = get_hitorical_futures_oi(fyers, Exchange, SYMBOL, ExpDate, from_date, to_date, CandleResolution.DAY_1)
    else:
        new_data = get_hitorical_futures_oi(fyers, Exchange, SYMBOL, ExpDate, to_date, to_date, CandleResolution.DAY_1)
        if(len(new_data) == 1):
            data_from_file.append(new_data[0])

    save_csv(data_from_file, FUTURES_PATH, futures_file)

    futures_df = pd.DataFrame(
        data_from_file,
        columns=["time", "fut_open", "fut_high", "fut_low", "fut_close", "fut_volume", "oi", "spot_close"]
    )

    futures_df["date"] = pd.to_datetime(
        futures_df["time"], unit="s"
    )
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


def populate_derivatives_data(SYMBOL: str):
    futures_df = populate_futures_data(SYMBOL)
    options_df = futures_df #TODO
    return futures_df, options_df

# print(populate_futures_data("M&M"))