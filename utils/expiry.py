import calendar
from datetime import datetime, timedelta
from utils.nse_holiday import is_holiday
import logging

logger = logging.getLogger(__name__)

def get_first_day_of_this_expiry(YYMMM: str, day) -> datetime:
    """
    Given an expiry month in YYMMM format (e.g., "26JAN"),
    returns the date of the last Monday of the month preceding this expiry month.
    """
    logger.info(f"Calculating first day of expiry for: {YYMMM}")

    # Parse YYMMM string
    year_str = YYMMM[:2]
    month_abbr = YYMMM[2:]

    # Convert YY to full year (assuming current century, adjust if needed)
    current_year_prefix = int(datetime.now().year / 100)
    full_year = int(f"{current_year_prefix}{year_str}")

    # Convert month abbreviation to month number
    # Use datetime parsing for robustness
    month_num = datetime.strptime(month_abbr, '%b').month

    logger.info(f"Parsed year: {full_year}, month: {month_num}")

    # Get previous month's year and month
    prev_year, prev_month_num = _get_prev_year_month(month_num, full_year)
    logger.info(f"Previous month: {prev_month_num}/{prev_year}")

    # Get the last day of the previous month
    last_day = _get_last_weekday_of_month(prev_year, prev_month_num, day)
    logger.info(f"Last Monday of previous month: {last_day}")

    return last_day

def _get_last_month_Monday(trade_date):
    """
    Monthly expiry for stock futures.
    """
    prev_month = _get_prev_year_month(trade_date.month, trade_date.year)
    mon = _get_last_weekday_of_month(prev_month[0], prev_month[1], calendar.MONDAY)
    return mon


def get_next_year_month(curr_month, curr_year):
    """
    Monthly expiry for stock futures.
    """
    if curr_month == 12:
        next_month = 1
        next_year = curr_year + 1
    else:
        next_month = curr_month + 1
        next_year = curr_year

    return next_year, next_month

def _get_prev_year_month(curr_month, curr_year):
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

def _get_last_weekday_of_month(year, month, weekday):
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

def _get_last_trading_day(trade_date: datetime) -> datetime:
    date_to_check = trade_date
    while True:
        if is_holiday(date_to_check) or date_to_check.weekday() == 5 or date_to_check.weekday() == 6:
            date_to_check = date_to_check - timedelta(days=1)
        else:
            dt_330 = date_to_check.replace(hour=15, minute=30, second=0, microsecond=0)
            return dt_330

def get_expiry(trade_date):
    expiry = _get_last_weekday_of_month(trade_date.year, trade_date.month, calendar.TUESDAY)
    if expiry < datetime(trade_date.year, trade_date.month, trade_date.day):
        next_year, next_month = get_next_year_month(trade_date.month, trade_date.year)
        expiry = _get_last_weekday_of_month(next_year, next_month, calendar.TUESDAY)
    return _get_last_trading_day(expiry)

def get_DDMMM(trade_date):
    return trade_date.strftime("%d%b").upper()

def _get_expiry_DDMMM(trade_date):
    exp = get_expiry(trade_date)
    return get_DDMMM(exp)

def get_expiry_YYMMM(trade_date) -> str:
    expiry = get_expiry(trade_date)
    return expiry.strftime("%y%b").upper()

def datetime_to_YYYY_MM_DD(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")

def days_to_expiry(trade_date):
   exp = get_expiry(trade_date)
   curr_date = datetime(trade_date.year, trade_date.month, trade_date.day)
   return (exp - curr_date).days

def test():
    today = datetime.now()
    # today_plus_4 = today + timedelta(days=4)
    print(_get_last_trading_day(today))
    # print (_get_expiry_DDMMM(today))
    # print (_get_expiry_DDMMM(today_plus_4))
    # print(days_to_expiry(today_plus_4))

test()