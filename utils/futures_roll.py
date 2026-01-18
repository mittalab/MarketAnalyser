import calendar
from utils.expiry import get_current_expiry

ROLL_DAYS = 3


def should_roll(trade_date):
    expiry = get_current_expiry(trade_date)
    return (expiry - trade_date).days <= ROLL_DAYS


def get_active_futures_symbol(symbol, trade_date):
    expiry = get_current_expiry(trade_date)

    if should_roll(trade_date):
        # use next month
        if expiry.month == 12:
            next_expiry_month = 1
            year = expiry.year + 1
        else:
            next_expiry_month = expiry.month + 1
            year = expiry.year
    else:
        next_expiry_month = expiry.month
        year = expiry.year

    month_code = calendar.month_abbr[next_expiry_month].upper()
    yy = str(year)[-2:]

    return f"NSE:{symbol}{yy}{month_code}FUT"
