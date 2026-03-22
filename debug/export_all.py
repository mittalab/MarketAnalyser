import os
from debug.decision_ledger import generate_decision_ledger
from debug.future_oi_overview import generate_future_oi_view
from debug.day_view import generate_day_view

def export_all(decisions, SYMBOL, YYMMM):

    os.makedirs(f"debug/{YYMMM}", exist_ok=True)
    os.makedirs(f"debug/{YYMMM}/{SYMBOL}", exist_ok=True)
    os.makedirs(f"debug/{YYMMM}/{SYMBOL}/day", exist_ok=True)

    # Price/OI overview page
    generate_future_oi_view(decisions, f"debug/{YYMMM}/{SYMBOL}/future_oi_overview.html")

    generate_decision_ledger(decisions, f"debug/{YYMMM}/{SYMBOL}/decision_ledger.html")

    for d in decisions:
        generate_day_view(d, f"debug/{YYMMM}/{SYMBOL}/day/{d['date']}.html")
