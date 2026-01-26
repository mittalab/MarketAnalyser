import logging
from visualization.plot_price_oi import plot_price_oi_volume
from visualization.plot_option_oi import plot_option_oi_by_strike
from visualization.plot_state_signal import overlay_state_and_signal
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def show_dashboard(
        futures_df,
        option_df,
        state_series,
        signal_series
):
    logger.info("Showing dashboard...")
    # --- Price / Volume / OI ---
    fig, ax_price, ax_vol, ax_oi = plot_price_oi_volume(futures_df)

    # --- Overlay state + signal on price ---
    overlay_state_and_signal(
        ax_price,
        futures_df,
        state_series,
        signal_series
    )

    plt.show()

    # --- Option chain OI ---
    spot_price = futures_df["close"].iloc[-1]
    plot_option_oi_by_strike(option_df, spot_price)
    plt.show()
    logger.debug("Dashboard displayed.")
