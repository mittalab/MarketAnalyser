import os
import re
import csv
import json
from datetime import datetime
from collections import defaultdict

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
BHAVCOPY_DIR = "bhavcopies"


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
    return datetime.strptime(f"{dd}{mm}{yy}", "%d%m%y").date()


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
def build_option_history(EXPIRY_MMM, start_date: datetime):
    # Sort files by date
    files = sorted(
        [f for f in os.listdir(BHAVCOPY_DIR) if f.startswith("op")],
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

        filepath = os.path.join(BHAVCOPY_DIR, fname)

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
            symbol_day_data[symbol].append([
                call_oi_sum[symbol],
                "",
                "",
                daily_rows[symbol],
                put_oi_sum[symbol],
                trade_date.isoformat()
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

        # Ensure rows are sorted by date
        rows.sort(key=lambda r: r[-1])

        # start_date = rows[0][-1]
        # end_date = rows[-1][-1]

       # fname = f"{symbol}_{format_ddmm(start_date)}_{format_ddmm(end_date)}.csv"
        fname = f"NSE_{symbol}_{final_dir}_OPTIONS.csv"

        outputDir = f"{OUTPUT_DIR}\\{final_dir}"
        os.makedirs(outputDir, exist_ok=True)
        fpath = os.path.join(outputDir, fname)

        with open(fpath, "w", newline="") as f:
            writer = csv.writer(f)

            # Header (optional but recommended)
            writer.writerow([
                "callOi",
                "expiryData",
                "indiavixData",
                "optionsChain",
                "putOi",
                "fetched_datetime"
            ])

            for row in rows:
                calloi, c2, c3, options, putoi, date = row

                writer.writerow([
                    calloi,
                    "",
                    "",
                    json.dumps(options),   # serialize nested structure
                    putoi,
                    date
                ])

        print(f"Written: {fpath}")

def test():
    symbol_day_data = build_option_history(EXPIRY_MMM = "JAN", start_date=None)
    write_symbol_csv_files(symbol_day_data, final_dir="26JAN")

test()