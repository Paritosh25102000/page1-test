"""
Time Utilities - Date/time helper functions for staging calculations
"""

from datetime import datetime, timedelta
from typing import Tuple, Optional


# Financial Year constants (Indian FY: April 1 - March 31)
FY_START = "2025-04-01"
FY_END = "2026-03-31"


def get_fy_dates() -> Tuple[str, str]:
    """Return FY start and end dates."""
    return FY_START, FY_END


def get_current_quarter_dates(
    current_date: Optional[str] = None
) -> Tuple[str, str]:
    """
    Get current calendar quarter date range.

    Quarters:
        Q1: Jan 1 - Mar 31
        Q2: Apr 1 - Jun 30
        Q3: Jul 1 - Sep 30
        Q4: Oct 1 - Dec 31
    """
    if current_date:
        today = datetime.fromisoformat(current_date)
    else:
        today = datetime.now()

    quarter = (today.month - 1) // 3
    quarter_starts = [
        (1, 1), (4, 1), (7, 1), (10, 1)
    ]
    quarter_ends = [
        (3, 31), (6, 30), (9, 30), (12, 31)
    ]

    start_month, start_day = quarter_starts[quarter]
    end_month, end_day = quarter_ends[quarter]

    start = today.replace(month=start_month, day=start_day)
    end = today.replace(month=end_month, day=end_day)

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def get_looking_glass_dates(
    current_date: Optional[str] = None
) -> Tuple[str, str]:
    """
    Get +/- 5 weeks range around current date.

    Returns:
        (start_date, end_date) as YYYY-MM-DD strings
    """
    if current_date:
        today = datetime.fromisoformat(current_date)
    else:
        today = datetime.now()

    start = today - timedelta(weeks=5)
    end = today + timedelta(weeks=5)

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def get_week_start(date_str: str) -> str:
    """
    Get Monday of the week containing the given date.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Monday's date in YYYY-MM-DD format
    """
    date = datetime.fromisoformat(date_str)
    monday = date - timedelta(days=date.weekday())
    return monday.strftime("%Y-%m-%d")


def get_month_label(date: datetime) -> str:
    """
    Get month label for display (e.g., "Apr-25").

    Args:
        date: datetime object

    Returns:
        Label like "Apr-25", "May-25"
    """
    return date.strftime("%b-%y")


def get_week_label(date: datetime, week_num: int) -> str:
    """
    Get week label for display (e.g., "Wk 14").

    Args:
        date: Week start date
        week_num: Sequential week number in series

    Returns:
        Label like "Wk 14"
    """
    return f"Wk {date.isocalendar()[1]}"
