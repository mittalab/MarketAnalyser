import pandas as pd
import plotly.express as px

def generate_day_view(decision, output_path):
    df = pd.DataFrame(decision["option_chain"])

    print(decision)
    fig = px.bar(
        df,
        x="strike",
        y="oi",
        color="type",
        title=f"{decision['date']} | {decision['final_signal']} | Conf={decision['confidence']}"
    )

    # ATM lines
    if decision["put_atm_strike"]:
        fig.add_vline(x=decision["put_atm_strike"], line_color="green", line_dash="dash")
    if decision["call_atm_strike"]:
        fig.add_vline(x=decision["call_atm_strike"], line_color="red", line_dash="dash")

    # Subtitle annotation
    fig.add_annotation(
        text=decision["reason"],
        xref="paper", yref="paper",
        x=0, y=1.15,
        showarrow=False
    )

    fig.write_html(output_path, include_plotlyjs="cdn")
