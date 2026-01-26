import os
from debug.decision_ledger import generate_decision_ledger
from debug.day_view import generate_day_view

def export_all(decisions, SYMBOL):

    os.makedirs(f"debug/{SYMBOL}", exist_ok=True)
    os.makedirs(f"debug/{SYMBOL}/day", exist_ok=True)

    generate_decision_ledger(decisions, f"debug/{SYMBOL}/decision_ledger.html")

    for d in decisions:
        generate_day_view(d, f"debug/{SYMBOL}/day/{d['date']}.html")
