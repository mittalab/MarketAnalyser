import calendar
from datetime import datetime

def get_current_expiry(trade_date):
    """
    Monthly expiry for stock futures.
    """
    expiry = get_last_weekday_of_month(trade_date.year, trade_date.month, calendar.TUESDAY)
    return expiry

def get_last_month_Monday(trade_date):
    """
    Monthly expiry for stock futures.
    """
    prev_month = get_prev_year_month(trade_date.month, trade_date.year)
    mon = get_last_weekday_of_month(prev_month[0], prev_month[1], calendar.MONDAY)
    return mon

def get_prev_year_month(curr_month, curr_year):
    """
    Monthly expiry for stock futures.
    """
    if curr_month == 1:
        prev_month = 12
        prev_year = curr_year - 1
    else:
        prev_month = curr_month - 1
        prev_year = curr_year

    return prev_year, prev_month

def get_last_weekday_of_month(year, month, weekday):
    """
    Calculates the date of the last specified weekday (0=Mon, 6=Sun) of a given month.
    """
    # Get the number of days in the month
    _, num_days = calendar.monthrange(year, month)

    # Start checking from the last day of the month
    for day in range(num_days, num_days - 7, -1):
        target_date = datetime(year, month, day)
        # Check if the day is the target weekday
        if target_date.weekday() == weekday:
            return target_date
    return None

def get_expiry_DDMMM(trade_date):
    expiry = get_last_weekday_of_month(trade_date.year, trade_date.month, calendar.TUESDAY)
    return expiry.strftime("%d%b").upper()

def get_expiry_YYMMM(trade_date):
    expiry = get_last_weekday_of_month(trade_date.year, trade_date.month, calendar.TUESDAY)
    return expiry.strftime("%y%b").upper()

def datetime_to_YYYY_MM_DD(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")