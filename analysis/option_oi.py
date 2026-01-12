def analyze_option_oi(df):
    """
    Aggregates CE/PE by strike and finds institutional zones.
    """

    if df.empty:
        return None

    ce = df[df["type"] == "CE"]
    pe = df[df["type"] == "PE"]

    ce_group = ce.groupby("strike").agg({
        "oi": "sum",
        "oi_change": "sum",
        "bid": "mean",
        "ask": "mean"
    }).reset_index()

    pe_group = pe.groupby("strike").agg({
        "oi": "sum",
        "oi_change": "sum",
        "bid": "mean",
        "ask": "mean"
    }).reset_index()

    call_wall = ce_group.loc[ce_group["oi"].idxmax()]
    put_floor = pe_group.loc[pe_group["oi"].idxmax()]

    return {
        "call_resistance": call_wall["strike"],
        "call_oi": call_wall["oi"],
        "call_oi_change": call_wall["oi_change"],
        "put_support": put_floor["strike"],
        "put_oi": put_floor["oi"],
        "put_oi_change": put_floor["oi_change"],
    }
