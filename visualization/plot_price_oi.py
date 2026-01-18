import matplotlib.pyplot as plt

def plot_price_oi_volume(df):
    """
    df columns:
    date, open, high, low, close, volume, oi
    """

    fig, (ax_price, ax_vol, ax_oi) = plt.subplots(
        3, 1, figsize=(16, 10), sharex=True,
        gridspec_kw={"height_ratios": [3, 1, 1]}
    )

    # --- Price (candles simplified to close) ---
    ax_price.plot(df["date"], df["close"])
    ax_price.set_ylabel("Futures Price")
    ax_price.set_title("Futures Price")

    # --- Volume ---
    ax_vol.bar(df["date"], df["volume"])
    ax_vol.set_ylabel("Volume")

    # --- Open Interest ---
    ax_oi.plot(df["date"], df["oi"])
    ax_oi.set_ylabel("Futures OI")

    return fig, ax_price, ax_vol, ax_oi
