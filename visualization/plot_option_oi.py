import matplotlib.pyplot as plt

def plot_option_oi_by_strike(option_df, spot_price):
    """
    option_df columns:
    strike, type (CE/PE), oi_change
    """

    ce = option_df[option_df["type"] == "CE"]
    pe = option_df[option_df["type"] == "PE"]

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.barh(pe["strike"], pe["oi_change"], alpha=0.6, label="PUT OI Change")
    ax.barh(ce["strike"], -ce["oi_change"], alpha=0.6, label="CALL OI Change")

    ax.axhline(spot_price)
    ax.set_xlabel("OI Change")
    ax.set_ylabel("Strike")
    ax.set_title("Option Chain OI Change (PUT vs CALL)")

    ax.legend()

    return fig, ax
