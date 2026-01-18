def overlay_state_and_signal(ax, df, state_series, signal_series):
    """
    state_series: dict(date -> market_state)
    signal_series: dict(date -> signal)
    """

    for i, row in df.iterrows():
        date = row["date"]

        # --- Market State Background ---
        state = state_series.get(date)

        if state == "ACCUMULATION":
            ax.axvspan(date, date, alpha=0.1)
        elif state == "RISK_TRANSFER":
            ax.axvspan(date, date, alpha=0.2)
        elif state == "EXPANSION":
            ax.axvspan(date, date, alpha=0.15)

        # --- Signals ---
        signal = signal_series.get(date)

        if signal == "LONG":
            ax.scatter(date, row["close"], marker="^")
        elif signal == "SHORT":
            ax.scatter(date, row["close"], marker="v")
