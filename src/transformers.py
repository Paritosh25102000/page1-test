"""
Field transformation functions for XML to JSON conversion.

Implements all transformation rules defined in xml_to_json_mapping.json.
"""

import re
from datetime import datetime, timedelta
from typing import Optional


def parse_int(value: str | None) -> int | None:
    """
    Parse string to integer.

    Args:
        value: String representation of integer

    Returns:
        Integer value or None if empty/invalid
    """
    if not value:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def parse_float(value: str | None) -> float | None:
    """
    Parse string to float.

    Args:
        value: String representation of float

    Returns:
        Float value or None if empty/invalid
    """
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def boolean_from_string(value: str | None) -> bool:
    """
    Convert '0'/'1' string to boolean.

    Args:
        value: '0' or '1' string

    Returns:
        True if '1', False otherwise
    """
    return value == "1"


def extract_date(datetime_str: str | None) -> str | None:
    """
    Extract date portion from ISO 8601 datetime string.

    Args:
        datetime_str: ISO 8601 datetime (e.g., '2025-03-15T08:00:00')

    Returns:
        Date string 'YYYY-MM-DD' or None
    """
    if not datetime_str:
        return None
    # Take first 10 characters (YYYY-MM-DD)
    return datetime_str[:10] if len(datetime_str) >= 10 else None


def iso8601_duration_to_days(duration: str | None) -> float | None:
    """
    Convert ISO 8601 duration to days.

    Assumes 8-hour workday for conversion.

    Args:
        duration: ISO 8601 duration string (e.g., 'PT960H0M0S')

    Returns:
        Duration in days or None if invalid

    Examples:
        'PT960H0M0S' -> 120.0 (960 hours / 8)
        'PT8H0M0S' -> 1.0
        'PT0H0M0S' -> 0.0
    """
    if not duration:
        return None

    # Pattern: PT{hours}H{minutes}M{seconds}S
    pattern = r"PT(\d+)H(\d+)M(\d+)S"
    match = re.match(pattern, duration)

    if not match:
        return None

    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))

    # Convert to total hours, then to days (8-hour workday)
    total_hours = hours + minutes / 60 + seconds / 3600
    days = total_hours / 8

    return days


def remove_last_segment(wbs: str | None) -> str | None:
    """
    Remove the last segment from a dot-separated WBS code.

    Args:
        wbs: WBS code (e.g., '37300.37500.51900')

    Returns:
        Parent WBS code or None if single segment

    Examples:
        '37300.37500.51900' -> '37300.37500'
        '37300.37500' -> '37300'
        '37300' -> None
    """
    if not wbs:
        return None

    segments = wbs.split(".")
    if len(segments) <= 1:
        return None

    return ".".join(segments[:-1])


def derive_actual_start(timephased_data: list[dict]) -> str | None:
    """
    Derive actual start date from TimephasedData entries.

    Finds the earliest Start date from Type=2 entries with non-zero Value.

    Args:
        timephased_data: List of TimephasedData dictionaries with
                        'type', 'start', 'finish', 'value' keys

    Returns:
        Earliest actual start date (YYYY-MM-DD) or None
    """
    if not timephased_data:
        return None

    valid_starts = []
    for entry in timephased_data:
        # Type 2 = Actual Work
        if entry.get("type") == "2" and entry.get("value") != "PT0H0M0S":
            start = extract_date(entry.get("start"))
            if start:
                valid_starts.append(start)

    return min(valid_starts) if valid_starts else None


def derive_actual_end(timephased_data: list[dict]) -> str | None:
    """
    Derive actual end date from TimephasedData entries.

    Finds the latest Finish date from Type=2 entries with non-zero Value.

    Args:
        timephased_data: List of TimephasedData dictionaries

    Returns:
        Latest actual end date (YYYY-MM-DD) or None
    """
    if not timephased_data:
        return None

    valid_ends = []
    for entry in timephased_data:
        if entry.get("type") == "2" and entry.get("value") != "PT0H0M0S":
            end = extract_date(entry.get("finish"))
            if end:
                valid_ends.append(end)

    return max(valid_ends) if valid_ends else None


def calculate_duration_days(start: str | None, end: str | None) -> int | None:
    """
    Calculate calendar days between two dates (inclusive).

    Args:
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)

    Returns:
        Number of calendar days or None if dates invalid
    """
    if not start or not end:
        return None

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        delta = (end_date - start_date).days
        return max(0, delta)  # Ensure non-negative
    except ValueError:
        return None


def parse_date(date_str: str | None) -> Optional[datetime]:
    """
    Parse a date string to datetime object.

    Args:
        date_str: Date string (YYYY-MM-DD)

    Returns:
        datetime object or None
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def date_to_string(dt: datetime | None) -> str | None:
    """
    Convert datetime object to date string.

    Args:
        dt: datetime object

    Returns:
        Date string (YYYY-MM-DD) or None
    """
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d")


def get_week_monday(date_str: str) -> str:
    """
    Get the Monday of the week containing the given date.

    Args:
        date_str: Date string (YYYY-MM-DD)

    Returns:
        Monday's date string (YYYY-MM-DD)
    """
    dt = parse_date(date_str)
    if not dt:
        return None
    # weekday() returns 0 for Monday
    monday = dt - timedelta(days=dt.weekday())
    return date_to_string(monday)


def get_week_sunday(date_str: str) -> str:
    """
    Get the Sunday of the week containing the given date.

    Args:
        date_str: Date string (YYYY-MM-DD)

    Returns:
        Sunday's date string (YYYY-MM-DD)
    """
    dt = parse_date(date_str)
    if not dt:
        return None
    # weekday() returns 0 for Monday, so Sunday is 6 - weekday days ahead
    sunday = dt + timedelta(days=(6 - dt.weekday()))
    return date_to_string(sunday)


def get_week_boundaries(date_str: str) -> tuple[str, str] | None:
    """
    Get Monday and Sunday of the week containing the given date.

    Args:
        date_str: Date string (YYYY-MM-DD)

    Returns:
        Tuple of (monday, sunday) date strings, or None if invalid
    """
    monday = get_week_monday(date_str)
    sunday = get_week_sunday(date_str)
    if monday and sunday:
        return (monday, sunday)
    return None
