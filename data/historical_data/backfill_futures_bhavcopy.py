import pandas as pd

def backfill_futures_from_bhavcopy(
        futures_df,
        symbol,
        start_date,
        end_date
):
    """
    Backfills missing OI rows using bhavcopy.
    """

    from utils.fetch_fo_bhavcopy import fetch_futures_bhavcopy

    date_range = pd.date_range(start_date, end_date, freq="B")

    for d in date_range:
        if d not in futures_df["date"].values:
            continue

        row = futures_df[futures_df["date"] == d]

        if not row["oi"].isna().iloc[0]:
            continue

        bhav = fetch_futures_bhavcopy(d.date())

        fut = bhav[
            (bhav["SYMBOL"] == symbol)
        ]

        if fut.empty:
            continue

        fut = fut.iloc[0]

        futures_df.loc[futures_df["date"] == d, "oi"] = fut["OPEN_INT"]
        futures_df.loc[futures_df["date"] == d, "volume"] = fut["CONTRACTS"]

    return futures_df
