import os
import re
import csv
import json
from datetime import datetime
from collections import defaultdict
from data.storage import load_csv
from data.storage import save_csv
from typing import List, Callable, Any, Set

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
BHAVCOPY_DIR = "bhavcopies"
BHAVCOPY_DIR_TMP = "bhavcopy_temp"

DIR_TO_USE = BHAVCOPY_DIR_TMP

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def parse_date_from_filename(filename):
    """
    opDDMMYY.csv → YYYY-MM-DD
    """
    m = re.search(r"op(\d{2})(\d{2})(\d{2})\.csv", filename)
    if not m:
        return None

    dd, mm, yy = m.groups()
    return datetime.strptime(f"{dd}{mm}{yy}", "%d%m%y")


def parse_option_symbol(col1):
    """
    OPTSTKRELIANCE25-JAN-24CE1500
    → SYMBOL, MMM, TYPE, STRIKE
    """
    m = re.match(
        r"OPTSTK([A-Z0-9a-z-&]+)\d{2}-([A-Z]{3})-\d{4}(CE|PE)(\d+)",
        col1
    )
    if not m:
        return None

    symbol, mmm, opt_type, strike = m.groups()
    return symbol, mmm, opt_type, int(strike)


# ------------------------------------------------------------
# MAIN PROCESSOR
# ------------------------------------------------------------
def build_option_history(EXPIRY_MMM: str, start_date: datetime | None):
    # Sort files by date
    files = sorted(
        [f for f in os.listdir(DIR_TO_USE) if f.startswith("op")],
        key=parse_date_from_filename
    )

    # OI memory for OI_CHANGE
    prev_oi = {}  # (symbol, type, strike) → oi

    # Final output
    symbol_day_data = defaultdict(list)

    for fname in files:
        trade_date = parse_date_from_filename(fname)
        if not trade_date:
            continue
        if start_date and trade_date < start_date:
            continue

        filepath = os.path.join(DIR_TO_USE, fname)

        daily_rows = defaultdict(list)
        call_oi_sum = defaultdict(int)
        put_oi_sum = defaultdict(int)

        with open(filepath, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    col1 = row[0]
                    oi = int(float(row[8])) * 1000
                except (IndexError, ValueError):
                    continue

                parsed = parse_option_symbol(col1)
                if not parsed:
                    continue

                symbol, mmm, opt_type, strike = parsed

                # Filter expiry month
                if mmm != EXPIRY_MMM:
                    continue

                key = (symbol, opt_type, strike)
                prev = prev_oi.get(key, 0)
                oi_change = oi - prev
                prev_oi[key] = oi

                option_entry = {
                    "ask": 0,
                    "bid": 0,
                    "oi": oi,
                    "option_type": opt_type,
                    "strike_price": strike,
                    "oich": oi_change
                }

                daily_rows[symbol].append(option_entry)

                if opt_type == "CE":
                    call_oi_sum[symbol] += oi
                else:
                    put_oi_sum[symbol] += oi

        # Build daily output rows
        for symbol in daily_rows:
            dt_330 = trade_date.date().strftime("%Y-%m-%d")
            symbol_day_data[symbol].append([
                call_oi_sum[symbol],
                "",
                "",
                daily_rows[symbol],
                put_oi_sum[symbol],
                dt_330
            ])

    return symbol_day_data

OUTPUT_DIR = "C:\\Users\\Abhishek\\Trading_Projects\\MarketAnalyser\\storage\\options"

def format_ddmm(date_str):
    """
    YYYY-MM-DD → DDMM
    """
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return d.strftime("%d%m")


def write_symbol_csv_files(symbol_day_data, final_dir: str):
    """
    symbol_day_data:
        {
          SYMBOL: [
              [calloi, "", "", option_list, putoi, date],
              ...
          ]
        }
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for symbol, rows in symbol_day_data.items():
        if not rows:
            continue

        print(f"Populating for symbol {symbol}")
        # Ensure rows are sorted by date
        rows.sort(key=lambda r: r[-1])

        fname = f"NSE_{symbol}_{final_dir}_OPTIONS.csv"

        outputDir = f"{OUTPUT_DIR}\\{final_dir}"
        os.makedirs(outputDir, exist_ok=True)
        fpath = os.path.join(outputDir, fname)

        with open(fpath, "r", newline="", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            header = next(reader)

            sort_idx = header.index("fetched_datetime")

            #  Read existing rows
            all_rows = list(reader)

        # Track keys from file (file has priority)
        existing_keys: Set[Any] = set()
        for row in all_rows:
            existing_keys.add(row[sort_idx])

        # Validate & append new rows
        for row in rows:
            calloi, c2, c3, options, putoi, date = row
            if date in existing_keys:
                print(f"Date already exists {date}")
                continue

            all_rows.append([
                    calloi,
                    "",
                    "",
                    json.dumps(options),   # serialize nested structure
                    putoi,
                    date
                ])

        # Sort rows
        all_rows.sort(
            key=lambda r: r[sort_idx],
            reverse=False
        )

        # Write merged & sorted CSV
        with open(fpath, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            writer.writerows(all_rows)

        print(f"Written: {fpath}")

def test():
    symbol_day_data = build_option_history(EXPIRY_MMM = "FEB", start_date=None)
    write_symbol_csv_files(symbol_day_data, final_dir="26FEB")

# test()