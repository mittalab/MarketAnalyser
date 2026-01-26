import numpy as np
def build_option_buckets(
        option_df,
        spot_price,
        totalStrike=2,
        atr=None,
        max_spread_pct=0.02
):
    """
    option_df columns:
    strike, type (CE/PE), oi, oi_change, bid, ask, volume
    """

    df = option_df.copy()

    # -------------------------
    # 1. Define relevance zone
    # -------------------------
    if atr is not None:
        lower = spot_price - atr
        upper = spot_price + atr
    else:
        # fallback: ATM ±totalStrike strikes
        strikes = sorted(df["strike"].unique())
        atm = min(strikes, key=lambda x: abs(float(x) - spot_price))
        idx = strikes.index(atm)
        relevant = strikes[max(0, idx-totalStrike): idx+totalStrike+1]
        lower, upper = min(relevant), max(relevant)

    df = df[(df["strike"] >= lower) & (df["strike"] <= upper)]
    # -------------------------
    # 2. TODO : Fix Liquidity filter when bid and ask are not present
    # -------------------------
    # mid = (df["bid"] + df["ask"]) / 2
    # spread_pct = (df["ask"] - df["bid"]) / mid
    # df = df[spread_pct <= max_spread_pct]
    # print(df)

    # -------------------------
    # 3. Define ATM
    # -------------------------
    strikes = df["strike"].unique()
    atm_strike = min(strikes, key=lambda x: abs(x - spot_price))

    buckets = {
        "PUT_ITM": [],
        "PUT_ATM": [],
        "PUT_OTM": [],
        "CALL_ITM": [],
        "CALL_ATM": [],
        "CALL_OTM": []
    }

    for _, row in df.iterrows():
        k = row["strike"]
        t = row["type"]

        if t == "PE":
            if k > spot_price:
                buckets["PUT_ITM"].append(row)
            elif k == atm_strike:
                buckets["PUT_ATM"].append(row)
            else:
                buckets["PUT_OTM"].append(row)

        if t == "CE":
            if k < spot_price:
                buckets["CALL_ITM"].append(row)
            elif k == atm_strike:
                buckets["CALL_ATM"].append(row)
            else:
                buckets["CALL_OTM"].append(row)

    return buckets, atm_strike

def test():
    strikes = [np.float64(240.0), np.float64(250.0), np.float64(260.0), np.float64(265.0), np.float64(270.0), np.float64(275.0), np.float64(280.0), np.float64(285.0), np.float64(290.0), np.float64(295.0), np.float64(300.0), np.float64(305.0), np.float64(310.0), np.float64(315.0), np.float64(320.0), np.float64(325.0), np.float64(330.0), np.float64(335.0), np.float64(340.0), np.float64(350.0), np.float64(360.0)]
    spot_price = 292.5
    atm = min(strikes, key=lambda x: abs(x - spot_price))
    print(atm)

# test()