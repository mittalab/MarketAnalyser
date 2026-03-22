import pandas as pd
import plotly.graph_objects as go


def generate_future_oi_view(decisions, output_path):
    df = pd.DataFrame(decisions)

    fig = go.Figure()

    # -----------------------------
    # 1️⃣ Futures Price (Line)
    # -----------------------------
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["futures_close"],
            mode="lines",
            name="Futures Price",
            line=dict(color="black", width=2),
            yaxis="y1"
        )
    )

    # -----------------------------
    # 2️⃣ Futures OI (Bars)
    # -----------------------------
    fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["futures_oi"],
            name="Futures OI",
            marker_color="blue",
            opacity=0.4,
            text=df["futures_oi"].apply(lambda x: f"{int(x):,}"),   # 👈 write value inside bar
            textposition="inside",
            yaxis="y2"
        )
    )

    # -----------------------------
    # 3️⃣ Signal Markers
    # -----------------------------
    for signal, color in [("LONG", "green"), ("SHORT", "red")]:
        mask = df["final_signal"] == signal
        fig.add_trace(
            go.Scatter(
                x=df[mask]["date"],
                y=df[mask]["futures_close"],
                mode="markers",
                marker=dict(color=color, size=8),
                name=signal,
                yaxis="y1"
            )
        )

    # -----------------------------
    # 4️⃣ Layout with Dual Axis
    # -----------------------------
    fig.update_layout(
        title="Futures Price & OI Overlay",
        xaxis=dict(title="Date"),

        yaxis=dict(
            title="Futures Price",
            side="left"
        ),

        yaxis2=dict(
            title="Futures OI",
            overlaying="y",
            side="right",
            showgrid=False
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02
        ),

        height=650
    )

    fig.write_html(output_path, include_plotlyjs="cdn")

