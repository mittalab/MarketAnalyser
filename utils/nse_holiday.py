import os
import json
import requests
from datetime import datetime, date
from bs4 import BeautifulSoup

HOLIDAY_URL = "https://www.nseindia.com/resources/exchange-communication-holidays#holiday_trading"
HOLIDAY_FILE = "C:\\Users\\Abhishek\\Trading_Projects\\MarketAnalyser\\utils\\data\\nse_holidays.json"
WORKING_FILE = "C:\\Users\\Abhishek\\Trading_Projects\\MarketAnalyser\\utils\\data\\nse_exception.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

def _today_str():
    return date.today().isoformat()

def _validate_fetched_year(fetched_on: str):
    """
    fetched_on: YYYY-MM-DD
    Raises ValueError if fetched year < current year
    """
    fetched_date = date.fromisoformat(fetched_on)
    current_year = date.today().year

    if fetched_date.year < current_year:
        raise ValueError(
            f"Holiday data is stale: fetched_on={fetched_on}, current_year={current_year}"
        )
    return True

def _file_is_fresh(filepath: str):
    if not os.path.exists(filepath):
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    fetched_on = data.get("fetched_on")
    return _validate_fetched_year(fetched_on)
    # return data.get("fetched_on") == _today_str()


def _fetch_nse_holidays() -> list[str]:
    session = requests.Session()
    session.headers.update(HEADERS)

    # First request to set cookies (critical for NSE)
    session.get("https://www.nseindia.com", timeout=10)

    print("Hello")
    response = session.get(HOLIDAY_URL, timeout=15)
    response.raise_for_status()
    # print(response)
    print("Hello")
    # print(response.text)

    soup = BeautifulSoup(response.text, "html.parser")

    holidays = []

    # NSE usually publishes holiday tables – parse all tables safely
    tables = soup.find_all("table")
    print(tables)
    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 2:
                try:
                    holiday_date = datetime.strptime(cols[1], "%d-%b-%Y").date()
                    holidays.append(holiday_date.isoformat())
                except Exception:
                    continue

    return sorted(set(holidays))


def _load_or_update_holidays() -> set[date]:
    if _file_is_fresh(HOLIDAY_FILE):
        with open(HOLIDAY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    return {datetime.strptime(d, "%d-%b-%Y").date() for d in data["holidays"]}

def _load_or_update_working_days() -> set[date]:
    if _file_is_fresh(WORKING_FILE):
        with open(WORKING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    return {datetime.strptime(d, "%d-%b-%Y").date() for d in data["working"]}

    # holidays = _fetch_nse_holidays()
    #
    # payload = {
    #     "fetched_on": _today_str(),
    #     "holidays": holidays,
    # }
    #
    # with open(HOLIDAY_FILE, "w", encoding="utf-8") as f:
    #     json.dump(payload, f, indent=2)
    #
    # return {date.fromisoformat(d) for d in holidays}


# --------------------------------------------------
# PUBLIC UTILITY FUNCTION
# --------------------------------------------------

def is_holiday(check_date: date | datetime | str) -> bool:
    if isinstance(check_date, datetime):
        check_date = check_date.date()
    elif isinstance(check_date, str):
        check_date = date.fromisoformat(check_date)

    working = _load_or_update_working_days()
    if check_date in working:
        return False

    # Saturday / Sunday check
    if check_date.weekday() == 5 or check_date.weekday() == 6:
        return True

    # NSE Holidays check
    holidays = _load_or_update_holidays()
    return check_date in holidays

def test():
    print(is_holiday(datetime.now()))

# test()