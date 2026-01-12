import pandas as pd


def fetch_option_chain(fyers, symbol):
    # data = {"symbol": symbol, "strikecount": 5, "timestamp": ""}
    response = fyers.optionchain({"symbol": symbol})
    records = []

    for item in response["data"]["optionsChain"]:
        # Skip underlying / non-option rows
        if item.get("option_type") not in ("CE", "PE"):
            continue

        records.append({
            "strike": item["strike_price"],
            "type": item["option_type"],  # CE / PE
            "oi": item["oi"],
            "oi_change": item["oich"],
            "oi_change_pct": item["oichp"],
            "bid": item["bid"],
            "ask": item["ask"],
            "ltp": item["ltp"],
            "volume": item["volume"]
        })



    return pd.DataFrame(records)
