def aggregate_bucket(rows):
    if not rows:
        return {"oi": 0, "oi_change": 0}

    oi = sum(r["oi"] for r in rows)
    oi_chg = sum(r["oi_change"] for r in rows)

    return {
        "oi": oi,
        "oi_change": oi_chg
    }


def compute_option_metrics(buckets):
    put_atm = aggregate_bucket(buckets["PUT_ATM"])
    put_itm = aggregate_bucket(buckets["PUT_ITM"])
    call_atm = aggregate_bucket(buckets["CALL_ATM"])
    call_otm = aggregate_bucket(buckets["CALL_OTM"])

    DPI = put_atm["oi_change"] + put_itm["oi_change"]
    USI = call_atm["oi_change"] + call_otm["oi_change"]
    ORB = DPI - USI

    return {
        "DPI": DPI,
        "USI": USI,
        "ORB": ORB
    }
