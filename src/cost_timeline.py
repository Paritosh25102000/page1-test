"""
Cost Timeline Calculator for weekly cost breakdown.

Calculates cost distribution across weeks within the financial year
(FY 2025-26: April 1, 2025 to March 31, 2026).
"""

from datetime import datetime, timedelta
from typing import Optional

from .utils import format_number

# Financial Year boundaries
FY_START = "2025-04-01"
FY_END = "2026-03-31"


def parse_date(date_str: str | None) -> datetime | None:
    """Parse date string to datetime object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def date_to_string(dt: datetime | None) -> str | None:
    """Convert datetime to date string."""
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d")


def get_monday_of_week(dt: datetime) -> datetime:
    """Get the Monday of the week containing the date."""
    return dt - timedelta(days=dt.weekday())


def get_sunday_of_week(dt: datetime) -> datetime:
    """Get the Sunday of the week containing the date."""
    return dt + timedelta(days=(6 - dt.weekday()))


def calculate_days_overlap(
    period_start: datetime,
    period_end: datetime,
    window_start: datetime,
    window_end: datetime,
) -> int:
    """
    Calculate number of days a period overlaps with a window.

    Args:
        period_start: Start of the period
        period_end: End of the period
        window_start: Start of the window
        window_end: End of the window

    Returns:
        Number of overlapping days (0 if no overlap)
    """
    # Find overlap bounds
    overlap_start = max(period_start, window_start)
    overlap_end = min(period_end, window_end)

    if overlap_start > overlap_end:
        return 0

    # +1 because both start and end are inclusive
    return (overlap_end - overlap_start).days + 1


def calculate_incoming_cost(
    cost_total: float,
    duration_days: float,
    start_date: str,
    fy_start: str = FY_START,
) -> dict:
    """
    Calculate incoming cost before FY start.

    Args:
        cost_total: Total cost for the task
        duration_days: Duration in days
        start_date: Task start date (YYYY-MM-DD)
        fy_start: FY start date (YYYY-MM-DD)

    Returns:
        Dictionary with days_before_fy and cost
    """
    start_dt = parse_date(start_date)
    fy_start_dt = parse_date(fy_start)

    if not start_dt or not fy_start_dt or duration_days <= 0:
        return {"days_before_fy": 0, "cost": 0.0}

    # If task starts on or after FY start, no incoming cost
    if start_dt >= fy_start_dt:
        return {"days_before_fy": 0, "cost": 0.0}

    # Calculate days before FY start
    days_before = (fy_start_dt - start_dt).days

    # Can't have more days before FY than total duration
    days_before = min(days_before, int(duration_days))

    # Calculate prorated cost
    daily_rate = cost_total / duration_days
    incoming = daily_rate * days_before

    return {
        "days_before_fy": days_before,
        "cost": format_number(incoming),
    }


def generate_weekly_costs(
    cost_total: float,
    plan_dates: dict,
    actual_dates: dict,
    is_complete: bool,
    fy_start: str = FY_START,
    fy_end: str = FY_END,
) -> tuple[list[dict], dict]:
    """
    Generate weekly cost entries for the financial year.

    Args:
        cost_total: Total cost for the task
        plan_dates: Plan dates dict with start, end, duration_days
        actual_dates: Actual dates dict with start, end, duration_days
        is_complete: Whether task is complete
        fy_start: FY start date
        fy_end: FY end date

    Returns:
        Tuple of (weekly_costs list, summary dict)
    """
    weekly_costs = []

    # Parse FY boundaries
    fy_start_dt = parse_date(fy_start)
    fy_end_dt = parse_date(fy_end)

    # Parse plan dates
    plan_start_dt = parse_date(plan_dates.get("start"))
    plan_end_dt = parse_date(plan_dates.get("end"))
    plan_duration = plan_dates.get("duration_days") or 0

    # Parse actual dates
    actual_start_dt = parse_date(actual_dates.get("start"))
    actual_end_dt = parse_date(actual_dates.get("end"))
    actual_duration = actual_dates.get("duration_days") or 0

    # Calculate daily rates
    plan_daily_rate = cost_total / plan_duration if plan_duration > 0 else 0

    # Actual rate: use actual duration if complete, else use plan duration
    if is_complete and actual_duration > 0:
        actual_daily_rate = cost_total / actual_duration
    else:
        actual_daily_rate = plan_daily_rate

    # Determine the date range to cover
    # For plan: intersection of task dates with FY
    # For actual: intersection of actual dates with FY (or plan dates if incomplete)

    # Find the earliest and latest dates we need to cover
    all_starts = [d for d in [plan_start_dt, actual_start_dt] if d is not None]
    all_ends = [d for d in [plan_end_dt, actual_end_dt] if d is not None]

    if not all_starts or not all_ends:
        # No valid dates, return empty
        return [], {
            "total_weeks_in_fy": 0,
            "plan_cost_in_fy": 0.0,
            "actual_cost_in_fy": 0.0,
            "plan_cost_before_fy": 0.0,
            "actual_cost_before_fy": 0.0,
        }

    earliest_start = min(all_starts)
    latest_end = max(all_ends)

    # Constrain to FY
    range_start = max(earliest_start, fy_start_dt)
    range_end = min(latest_end, fy_end_dt)

    if range_start > range_end:
        # Task doesn't overlap with FY
        return [], {
            "total_weeks_in_fy": 0,
            "plan_cost_in_fy": 0.0,
            "actual_cost_in_fy": 0.0,
            "plan_cost_before_fy": 0.0,
            "actual_cost_before_fy": 0.0,
        }

    # Calculate incoming costs
    plan_incoming = calculate_incoming_cost(
        cost_total, plan_duration, plan_dates.get("start"), fy_start
    )

    if actual_start_dt:
        actual_incoming = calculate_incoming_cost(
            cost_total,
            actual_duration if actual_duration > 0 else plan_duration,
            actual_dates.get("start"),
            fy_start,
        )
    else:
        actual_incoming = {"days_before_fy": 0, "cost": 0.0}

    # Initialize accumulators with incoming costs
    plan_accumulated = plan_incoming["cost"]
    actual_accumulated = actual_incoming["cost"]

    # Track totals within FY
    plan_cost_in_fy = 0.0
    actual_cost_in_fy = 0.0

    # Start from the Monday of the first week in range
    current_monday = get_monday_of_week(range_start)
    week_number = 0

    while current_monday <= range_end:
        week_number += 1
        current_sunday = get_sunday_of_week(current_monday)

        # Calculate plan days in this week
        if plan_start_dt and plan_end_dt:
            plan_days = calculate_days_overlap(
                plan_start_dt, plan_end_dt, current_monday, current_sunday
            )
            # Also constrain to FY
            plan_days_in_fy = calculate_days_overlap(
                max(plan_start_dt, fy_start_dt),
                min(plan_end_dt, fy_end_dt),
                current_monday,
                current_sunday,
            )
        else:
            plan_days = 0
            plan_days_in_fy = 0

        # Calculate actual days in this week
        if actual_start_dt and actual_end_dt:
            actual_days = calculate_days_overlap(
                actual_start_dt, actual_end_dt, current_monday, current_sunday
            )
            # Constrain to FY
            actual_days_in_fy = calculate_days_overlap(
                max(actual_start_dt, fy_start_dt),
                min(actual_end_dt, fy_end_dt),
                current_monday,
                current_sunday,
            )
        else:
            # If no actual dates but task is in progress, use plan days for actual
            actual_days = plan_days if not is_complete else 0
            actual_days_in_fy = plan_days_in_fy if not is_complete else 0

        # Skip weeks with no task days
        if plan_days_in_fy == 0 and actual_days_in_fy == 0:
            current_monday = current_monday + timedelta(days=7)
            continue

        # Calculate costs for this week
        plan_cost = plan_daily_rate * plan_days_in_fy
        actual_cost = actual_daily_rate * actual_days_in_fy

        # Update accumulators
        plan_accumulated += plan_cost
        actual_accumulated += actual_cost

        # Track FY totals
        plan_cost_in_fy += plan_cost
        actual_cost_in_fy += actual_cost

        weekly_costs.append(
            {
                "week_number": week_number,
                "week_start": date_to_string(current_monday),
                "week_end": date_to_string(current_sunday),
                "days_in_task": {
                    "plan": plan_days_in_fy,
                    "actual": actual_days_in_fy,
                },
                "plan": {
                    "cost": format_number(plan_cost),
                    "accumulated": format_number(plan_accumulated),
                },
                "actual": {
                    "cost": format_number(actual_cost),
                    "accumulated": format_number(actual_accumulated),
                },
            }
        )

        # Move to next week
        current_monday = current_monday + timedelta(days=7)

    # Build summary
    summary = {
        "total_weeks_in_fy": len(weekly_costs),
        "plan_cost_in_fy": format_number(plan_cost_in_fy),
        "actual_cost_in_fy": format_number(actual_cost_in_fy),
        "plan_cost_before_fy": plan_incoming["cost"],
        "actual_cost_before_fy": actual_incoming["cost"],
    }

    return weekly_costs, summary


def calculate_cost_timeline(
    cost_plan_total: float,
    plan_dates: dict,
    actual_dates: dict,
    is_complete: bool,
) -> dict | None:
    """
    Calculate the full cost_timeline object.

    Args:
        cost_plan_total: Total planned cost
        plan_dates: Plan dates dict
        actual_dates: Actual dates dict
        is_complete: Whether task is complete

    Returns:
        cost_timeline object or None if not applicable
    """
    # Skip if no cost or no plan dates
    if not cost_plan_total or cost_plan_total <= 0:
        return None

    plan_start = plan_dates.get("start")
    plan_end = plan_dates.get("end")
    plan_duration = plan_dates.get("duration_days")

    if not plan_start or not plan_end or not plan_duration:
        return None

    # Generate weekly costs
    weekly_costs, summary = generate_weekly_costs(
        cost_total=cost_plan_total,
        plan_dates=plan_dates,
        actual_dates=actual_dates,
        is_complete=is_complete,
    )

    # Calculate incoming costs
    plan_incoming = calculate_incoming_cost(
        cost_plan_total, plan_duration, plan_start, FY_START
    )

    actual_start = actual_dates.get("start")
    actual_duration = actual_dates.get("duration_days")

    if actual_start and actual_duration:
        actual_incoming = calculate_incoming_cost(
            cost_plan_total, actual_duration, actual_start, FY_START
        )
    else:
        actual_incoming = {"days_before_fy": 0, "cost": 0.0}

    return {
        "fy_period": {
            "start": FY_START,
            "end": FY_END,
        },
        "incoming_cost": {
            "plan": plan_incoming,
            "actual": actual_incoming,
        },
        "weekly_costs": weekly_costs,
        "summary": summary,
    }
