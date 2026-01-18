from datetime import datetime
from pathlib import Path

def datetime_to_DDYYY(dt: datetime) -> str:
    day_of_month = dt.strftime("%d")   # DD
    day_of_year = dt.strftime("%j")    # YYY (001–366)
    return f"{day_of_month}{day_of_year}"

def datetime_to_DDMMM(dt: datetime) -> str:
    return dt.strftime("%d%b").upper()

def datetime_to_YYYY_MM_DD(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")

PROJECT_ROOT = Path(__file__).parent  # main directory

def to_project_relative(path):
    """
    Convert any path (absolute or relative) to a path
    relative to the project root directory.
    """
    path = Path(path).resolve()
    project_root = Path(PROJECT_ROOT).resolve()
    return path.relative_to(project_root)