import pandas as pd
import plotly.graph_objects as go

def generate_decision_ledger(decisions, output_path):
    rows = []

    for d in decisions:
        rows.append({
            "Date": f"<a href='day/{d['date']}.html'>{d['date']}</a>",
            "Close": d["futures_close"],
            "State": d["market_state"],
            "Raw": d["raw_signal"],
            "Final": d["final_signal"],
            "Confidence": d["confidence"],
            "ORB": d["ORB"],
            "ORB_Mom": d["ORB_momentum"],
            "Reason": d["reason"]
        })

    df = pd.DataFrame(rows)

    fig = go.Figure(
        data=[go.Table(
            header=dict(values=list(df.columns)),
            cells=dict(values=[df[col] for col in df.columns]),
        )]
    )

    fig.write_html(output_path, include_plotlyjs="cdn")
