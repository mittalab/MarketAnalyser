import logging

logger = logging.getLogger(__name__)

def analyze_option_oi(df):
    """
    Aggregates CE/PE by strike and finds institutional zones.
    """
    logger.info("Analyzing option OI...")
    if df.empty:
        logger.warning("Option OI dataframe is empty, cannot analyze.")
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

    logger.debug(f"Call wall at {call_wall['strike']} with OI {call_wall['oi']}")
    logger.debug(f"Put floor at {put_floor['strike']} with OI {put_floor['oi']}")

    return {
        "call_resistance": call_wall["strike"],
        "call_oi": call_wall["oi"],
        "call_oi_change": call_wall["oi_change"],
        "put_support": put_floor["strike"],
        "put_oi": put_floor["oi"],
        "put_oi_change": put_floor["oi_change"],
    }
