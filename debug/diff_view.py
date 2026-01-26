import pandas as pd
import plotly.graph_objects as go


def generate_diff_view(decisions_a, decisions_b, output_path):
    map_a = {d["date"]: d for d in decisions_a}
    map_b = {d["date"]: d for d in decisions_b}

    rows = []

    for date in sorted(set(map_a) & set(map_b)):
        a = map_a[date]
        b = map_b[date]

        if a["final_signal"] != b["final_signal"]:
            rows.append({
                "Date": date,
                "Signal_A": a["final_signal"],
                "Conf_A": a["confidence"],
                "Signal_B": b["final_signal"],
                "Conf_B": b["confidence"],
                "ORB_A": a["ORB"],
                "ORB_B": b["ORB"],
                "Reason_A": a["reason"],
                "Reason_B": b["reason"],
            })

    df = pd.DataFrame(rows)

    fig = go.Figure(
        data=[go.Table(
            header=dict(values=list(df.columns)),
            cells=dict(values=[df[col] for col in df.columns])
        )]
    )

    fig.write_html(output_path)
