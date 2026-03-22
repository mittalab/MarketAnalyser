import csv
import os
import re
from datetime import datetime, time, timedelta, timezone
from collections import defaultdict
from data.fyers_client import get_fyers_client
from typing import Callable, Any

IST = timezone(timedelta(hours=5, minutes=30))

INPUT_DATE_FMT = "%d%m%y"
EXPIRY_DATE_FMT = "%d-%b-%Y"

OI_MULTIPLIER = 1000

OUTPUT_HEADERS = [
    "time",
    "spot_close",
    "fut_open",
    "fut_high",
    "fut_low",
    "fut_close",
    "bias",
    "oi",
    "fut_volume",
    "bid",
    "ask",
    "oiperct_from_last_day",
    "oiperct_from_last_candle",
    "oi_change",
    "last_price_change",
]

BHAVCOPY_DIR = "bhavcopies"
BHAVCOPY_DIR_TMP = "bhavcopy_temp"

DIR_TO_USE = BHAVCOPY_DIR_TMP

OUTPUT_DIR = "C:\\Users\\Abhishek\\Trading_Projects\\MarketAnalyser\\storage\\futures"
OUTPUT_DIR_TMP = "C:\\Users\\Abhishek\\Trading_Projects\\MarketAnalyser\\backfill\\futures\\output"

OUTPUT_DIR_TO_USE = OUTPUT_DIR

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

def r2(x):
    """round to max 2 decimals safely"""
    return round(float(x), 2)


def epoch_330pm_ist(date_obj: datetime) -> int:
    dt = datetime.combine(date_obj.date(), time(15, 30), tzinfo=IST)
    return int(dt.timestamp())


def parse_contract_d(contract_d: str):
    m = re.match(r"FUTSTK([A-Z0-9&-]+)(\d{2}-[A-Z]{3}-\d{4})", contract_d)
    if not m:
        return None, None
    return m.group(1), datetime.strptime(m.group(2), EXPIRY_DATE_FMT)


def read_existing_data(filepath):
    rows = {}
    if not os.path.exists(filepath):
        return rows

    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows[int(r["time"])] = normalize_existing_row(r)

    print(f"Loaded existing file {filepath}, rows={len(rows)}")
    return rows

def normalize_existing_row(r):
    return {
        "epoch": int(r["time"]),
        "open": r2(r["fut_open"]),
        "high": r2(r["fut_high"]),
        "low": r2(r["fut_low"]),
        "close": r2(r["fut_close"]),
        "oi": r2(int(r["oi"]) / OI_MULTIPLIER),
        "volume": r2(int(r["fut_volume"]) / OI_MULTIPLIER),
    }

def get_spot_data(symbol : str, range_from: str, range_to: str, fyers):
    spot_symbol = "NSE:" + symbol + "-EQ"
    spot_data = {
        "symbol":spot_symbol,
        "resolution":'D',
        "date_format":"1",
        "range_from":range_from,
        "range_to":range_to,
        "cont_flag":"1"
    }
    spot_response = fyers.history(spot_data)
    if spot_response["s"] != "ok":
        print(f"Failed to fetch historical spot data for {spot_symbol}: {spot_response}")
        raise Exception(f"Failed to fetch historical spot data for {spot_symbol}: {spot_response}")

    spot_data = {}
    candles = spot_response['candles']
    for candle in candles:
        # candle[0] = Epoch Time, [1]=O, [2]=H, [3]=L, [4]=Close
        print(f"Date: {candle[0] + (10 * 60 * 60)}, Closing Price: {candle[4]}")
        spot_data[candle[0]  + (10 * 60 * 60)] = candle[4]

    return spot_data


def process_fo_folder():
    print("Starting FO data processing")
    fyers = get_fyers_client()
    grouped = defaultdict(list)

    for fname in sorted(os.listdir(DIR_TO_USE)):
        if not fname.startswith("fo") or not fname.endswith(".csv"):
            continue

        try:
            file_date = datetime.strptime(fname[2:8], INPUT_DATE_FMT)
        except Exception:
            print(f"Skipping invalid filename {fname}")
            continue

        epoch_time = epoch_330pm_ist(file_date)
        full_path = os.path.join(DIR_TO_USE, fname)

        print(f"Reading {fname}")

        with open(full_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    symbol, expiry = parse_contract_d(row["CONTRACT_D"])
                    if not symbol:
                        continue

                    grouped[(symbol, expiry)].append({
                        "epoch": epoch_time,
                        "open": r2(row["OPEN_PRICE"]),
                        "high": r2(row["HIGH_PRICE"]),
                        "low": r2(row["LOW_PRICE"]),
                        "close": r2(row["CLOSE_PRIC"]),
                        "oi": r2(row["OI_NO_CON"]),
                        "volume": r2(row["TRD_NO_CON"]),
                    })
                except Exception as e:
                    print(f"Bad row skipped: {e}")

    for (symbol, expiry), rows in grouped.items():
        rows.sort(key=lambda x: x["epoch"])

        yymmm = expiry.strftime("%y%b").upper()
        out_dir = os.path.join(OUTPUT_DIR_TO_USE, yymmm)
        os.makedirs(out_dir, exist_ok=True)

        out_file = os.path.join(
            out_dir, f"NSE_{symbol}_{yymmm}_FUT.csv"
        )

        existing_rows = read_existing_data(out_file)

        # merge existing + new rows by epoch
        merged = {}

        for epoch, r in existing_rows.items():
            merged[epoch] = r

        for r in rows:
            merged[r["epoch"]] = r  # overwrite if newly found

        write_rows = []
        all_rows = sorted(merged.values(), key=lambda x: x["epoch"])

        prev_oi = None
        prev_close = None

        range_from = all_rows[0]["epoch"]
        range_to = all_rows[-1]["epoch"]
        date_from = datetime.fromtimestamp(range_from).strftime("%Y-%m-%d")
        date_to = datetime.fromtimestamp(range_to).strftime("%Y-%m-%d")

        print(f'date_from {date_from} , date_to : {date_to}')
        spot_data = _retry(lambda: get_spot_data(symbol, date_from, date_to, fyers))
        print(spot_data)
        for r in all_rows:
            oi_change = 0.0
            oi_pct = 0.0
            price_change = 0.0

            if prev_oi is not None:
                oi_change = r2(r["oi"] - prev_oi)
                oi_pct = r2((oi_change / prev_oi) * 100) if prev_oi != 0 else 0.0
                price_change = r2(r["close"] - prev_close)

            print(r["epoch"])
            write_rows.append({
                "time": r["epoch"],
                "spot_close": spot_data[r["epoch"]],
                "fut_open": r["open"],
                "fut_high": r["high"],
                "fut_low": r["low"],
                "fut_close": r["close"],
                "bias": r2(r["close"] - spot_data[r["epoch"]]),
                "oi": int(r["oi"] * OI_MULTIPLIER),
                "fut_volume": int(r["volume"] * OI_MULTIPLIER),
                "bid": 0.00,
                "ask": 0.00,
                "oiperct_from_last_day": oi_pct,
                "oiperct_from_last_candle": oi_pct,
                "oi_change": int(oi_change),
                "last_price_change": price_change,
            })

            prev_oi = r["oi"]
            prev_close = r["close"]

        with open(out_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_HEADERS)
            writer.writeheader()
            for row in write_rows:
                writer.writerow(row)

        print(f"Rebuilt file with {len(write_rows)} rows → {out_file}")

    print("FO data processing completed")

def test():
    process_fo_folder()

test()