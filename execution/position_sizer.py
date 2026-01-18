def size_futures_position(capital, risk_pct, entry, stop):
    risk_amount = capital * risk_pct
    risk_per_unit = abs(entry - stop)

    if risk_per_unit == 0:
        return 0

    quantity = risk_amount // risk_per_unit
    return int(quantity)

def size_option_position(capital, risk_pct, premium):
    max_loss = capital * risk_pct
    lots = max_loss // premium
    return int(lots)
