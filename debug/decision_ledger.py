import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generate_decision_ledger(decisions, output_path):
    df = pd.DataFrame(decisions)

    # -----------------------------
    # 1. Build Price + OI + State plot
    # -----------------------------
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        row_heights=[0.65, 0.35],
        subplot_titles=("Futures Price & Signals", "Futures OI")
    )

    # Price
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["futures_close"],
            mode="lines",
            name="Futures Close",
            line=dict(color="black")
        ),
        row=1, col=1
    )

    # Signals
    for signal, color in [("LONG", "green"), ("SHORT", "red"), ("HOLD", "grey")]:
        mask = df["final_signal"] == signal
        fig.add_trace(
            go.Scatter(
                x=df[mask]["date"],
                y=df[mask]["futures_close"],
                mode="markers",
                marker=dict(color=color, size=9),
                name=signal
            ),
            row=1, col=1
        )

    # Futures OI
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["futures_oi"],
            mode="lines",
            name="Futures OI",
            line=dict(color="blue")
        ),
        row=2, col=1
    )

    for signal, color in [("", "green"), ("SHORT", "red"), ("HOLD", "grey")]:
        mask = df["final_signal"] == signal
        fig.add_trace(
        go.Scatter(
            x=df[mask]["date"],
            y=df[mask]["futures_close"],
            mode="markers",
            marker=dict(color=color, size=9),
            name=signal
        ),
        row=2, col=1
    )
    # -----------------------------
    # 2. Market State Background
    # -----------------------------
    state_colors = {
        "ACCUMULATION": "rgba(0, 200, 0, 0.12)",
        "DISTRIBUTION": "rgba(200, 0, 0, 0.12)",
        "EXPANSION": "rgba(0, 0, 200, 0.12)",
        "CONSOLIDATION": "rgba(150, 150, 150, 0.12)",
        "NEUTRAL": "rgba(100, 100, 100, 1)",
    }

    for i in range(len(df) - 1):
        state = df.iloc[i]["market_state"]
        print(state)
        fig.add_vrect(
            x0=df.iloc[i]["date"],
            x1=df.iloc[i + 1]["date"],
            fillcolor=state_colors.get(state, "rgba(240,240,240,0)"),
            opacity=0.7,
            layer="below",
            line_width=0
        )

    fig.update_layout(
        height=700,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=40, t=100, b=40),
        title="Decision Ledger — Price, OI & Market State"
    )

    # -----------------------------
    # 3. Build Decision Table
    # -----------------------------
    table = go.Figure(
        data=[go.Table(
            header=dict(
                values=[
                    "Date", "Close", "OI", "OI_CHG", "State",
                    "Raw", "Final", "Confidence",
                    "ORB", "ORB Mom", "Reason"
                ],
                fill_color="#f2f2f2",
                align="left"
            ),
            cells=dict(
                values=[
                    [
                        f"<a href='day/{d['date']}.html'>{d['date']}</a>"
                        for d in decisions
                    ],
                    df["futures_close"],
                    df["futures_oi"],
                    df["futures_oi_chg"],
                    df["market_state"],
                    df["raw_signal"],
                    df["final_signal"],
                    df["confidence"],
                    df["ORB"],
                    df["ORB_momentum"],
                    df["reason"]
                ],
                align="left"
            )
        )]
    )

    # -----------------------------
    # 4. Write combined HTML
    # -----------------------------
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
        f.write("<hr>")
        f.write(table.to_html(full_html=False, include_plotlyjs=False))
