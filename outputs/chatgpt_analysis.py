import json
import numpy as np
from utils.nse_holiday import count_trading_days
from utils.expiry import datetime_to_YYYY_MM_DD, get_expiry, get_expiry_YYMMM
from data.analysis_derivative_data import retrieve_derivatives_data
from datetime import datetime, timedelta

def export_stock_analysis_file(
        stock_name,
        expiry,
        futures_df,
        options_df,
        output_file
):
    """
    Convert futures and options dataframe into structured JSON
    suitable for deep derivatives analysis.
    """

    futures_df = futures_df.sort_values("date")
    options_df = options_df.sort_values(["date", "strike"])

    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()

    sorted_dates = sorted(futures_df["date"].unique())

    result = {
        "stock": stock_name,
        "expiry": expiry,
        "data": {}
    }

    for session_idx, d in enumerate(sorted_dates):

        fut_row = futures_df[futures_df["date"] == d]

        if fut_row.empty:
            continue

        fut = fut_row.iloc[0]

        date_obj = datetime.strptime(d, "%Y-%m-%d").date()

        spot_price = float(fut["spot_close"])

        opt_day = options_df[options_df["date"] == d]

        if opt_day.empty:
            continue

        strikes = np.sort(opt_day["strike"].unique())

        # Determine ATM strike
        atm_strike = float(strikes[np.argmin(np.abs(strikes - spot_price))])

        # Determine strike step automatically
        if len(strikes) > 1:
            strike_step = float(np.min(np.diff(strikes)))
        else:
            strike_step = 1.0

        # Separate calls and puts
        call_df = opt_day[opt_day["type"] == "CE"]
        put_df = opt_day[opt_day["type"] == "PE"]

        total_call_oi = int(call_df["oi"].sum())
        total_put_oi = int(put_df["oi"].sum())

        total_call_oi_change = float(call_df["oi_change"].sum())
        total_put_oi_change = float(put_df["oi_change"].sum())

        # Time calculations
        days_to_expiry = (expiry_date - date_obj).days

        trading_days_to_expiry = count_trading_days(
            date_obj + timedelta(days=1),
            expiry_date
        )

        session_number = session_idx + 1

        futures_block = {
            "open": float(fut["open"]),
            "high": float(fut["high"]),
            "low": float(fut["low"]),
            "close": float(fut["close"]),
            "volume": int(fut["volume"]),
            "oi": int(fut["oi"]),
            "oi_change": float(fut["oi_change"]),
            "spot_close": float(fut["spot_close"]),
            "last_price_change": float(fut["last_price_change"])
        }

        options_block = []

        for _, row in opt_day.iterrows():

            strike = float(row["strike"])

            distance_from_atm = int(round((strike - atm_strike) / strike_step))

            options_block.append({
                "strike": strike,
                "type": row["type"],
                "bid": float(row["bid"]),
                "ask": float(row["ask"]),
                "oi": int(row["oi"]),
                "oi_change": float(row["oi_change"]),
                "distance_from_atm": distance_from_atm
            })

        result["data"][d] = {
            "session_number": session_number,
            "days_to_expiry": days_to_expiry,
            "trading_days_to_expiry": trading_days_to_expiry,
            "atm_strike": atm_strike,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "total_call_oi_change": total_call_oi_change,
            "total_put_oi_change": total_put_oi_change,
            "futures": futures_block,
            "options": options_block
        }

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Analysis file written to: {output_file}")

def get_data(SYMBOL_EQ):
    today_datetime = datetime.now()
    ExpDate = get_expiry_YYMMM(today_datetime)
    expiryDate = datetime_to_YYYY_MM_DD(get_expiry(today_datetime))
    futures_df, options_df = retrieve_derivatives_data(SYMBOL_EQ, ExpDate)
    export_stock_analysis_file(stock_name=SYMBOL_EQ,
                               expiry=expiryDate,
                               futures_df=futures_df,
                               options_df=options_df,
                               output_file=f"{SYMBOL_EQ}_analysis.json")

# SYMBOL_EQ = "IOC"
SYMBOL_EQ = "ETERNAL"
get_data(SYMBOL_EQ)