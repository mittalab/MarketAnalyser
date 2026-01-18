import pandas as pd
import zipfile
import io
import requests
from datetime import datetime

NSE_BHAV_URL = "https://archives.nseindia.com/content/historical/DERIVATIVES/{year}/{month}/fo{date}bhav.csv.zip"


def fetch_futures_bhavcopy(trade_date):
    """
    Fetch NSE futures bhavcopy for a given date.
    trade_date: datetime.date
    """

    year = trade_date.strftime("%Y")
    month = trade_date.strftime("%b").upper()
    date_str = trade_date.strftime("%d%b%Y").upper()

    url = NSE_BHAV_URL.format(
        year=year,
        month=month,
        date=date_str
    )

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        with z.open(z.namelist()[0]) as f:
            df = pd.read_csv(f)

    # Keep only stock futures
    fut = df[
        (df["INSTRUMENT"] == "FUTSTK")
    ].copy()

    return fut
