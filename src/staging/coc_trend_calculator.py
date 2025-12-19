"""
COC Trend Calculator - Generate trend series for FY, Quarter, Month views
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .time_utils import (
    get_fy_dates,
    get_current_quarter_dates,
    get_looking_glass_dates,
    get_week_start,
    get_month_label,
    get_week_label
)


def calculate_coc_trend(
    tasks: List[Dict],
    current_date: Optional[str] = None
) -> Dict:
    """
    Calculate COC trend series for all three time modes.

    Args:
        tasks: Filtered tasks
        current_date: Override for "today" (YYYY-MM-DD)

    Returns:
        {
            "fy_series": [...],      # Monthly data points
            "quarter_series": [...], # Weekly data points
            "month_series": [...]    # Weekly data points (+/- 5 weeks)
        }
    """
    # Aggregate weekly costs from all tasks
    weekly_totals = aggregate_weekly_costs(tasks)

    # Generate series for each time mode
    return {
        "fy_series": generate_fy_series(weekly_totals),
        "quarter_series": generate_quarter_series(weekly_totals, current_date),
        "month_series": generate_month_series(weekly_totals, current_date)
    }


def aggregate_weekly_costs(tasks: List[Dict]) -> Dict[str, Dict]:
    """
    Aggregate weekly costs across all tasks.

    Returns:
        {
            "2025-04-07": {"plan": 12345.0, "actual": 11000.0},
            "2025-04-14": {"plan": 15000.0, "actual": 14500.0},
            ...
        }
    """
    weekly = defaultdict(lambda: {"plan": 0.0, "actual": 0.0})

    for task in tasks:
        timeline = task.get("cost_timeline") or {}
        weekly_costs = timeline.get("weekly_costs") or []

        for week in weekly_costs:
            week_start = week.get("week_start")
            if not week_start:
                continue

            plan = week.get("plan", {}).get("cost") or 0.0
            actual = week.get("actual", {}).get("cost") or 0.0

            weekly[week_start]["plan"] += plan
            weekly[week_start]["actual"] += actual

    return dict(weekly)


def generate_fy_series(weekly_totals: Dict) -> List[Dict]:
    """
    Generate monthly series for Financial Year view.

    Aggregates weekly data into months with proration for split weeks.
    """
    fy_start, fy_end = get_fy_dates()

    # Aggregate by month
    monthly = defaultdict(lambda: {"plan": 0.0, "actual": 0.0})

    for week_start, costs in weekly_totals.items():
        # Get month for this week (use week start date's month)
        week_date = datetime.fromisoformat(week_start)
        month_key = week_date.strftime("%Y-%m")

        # Only include if within FY
        if fy_start <= week_start <= fy_end:
            monthly[month_key]["plan"] += costs["plan"]
            monthly[month_key]["actual"] += costs["actual"]

    # Build series with cumulative
    series = []
    cumm_plan = 0.0
    cumm_actual = 0.0

    # Generate all months in FY
    current = datetime.fromisoformat(fy_start)
    end = datetime.fromisoformat(fy_end)

    while current <= end:
        month_key = current.strftime("%Y-%m")
        costs = monthly.get(month_key, {"plan": 0.0, "actual": 0.0})

        cumm_plan += costs["plan"]
        cumm_actual += costs["actual"]

        series.append({
            "label": get_month_label(current),
            "sort_date": current.strftime("%Y-%m-01"),
            "plan_cost": costs["plan"] if costs["plan"] else None,
            "actual_cost": costs["actual"] if costs["actual"] else None,
            "cumm_plan": cumm_plan,
            "cumm_actual": cumm_actual
        })

        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    return series


def generate_quarter_series(
    weekly_totals: Dict,
    current_date: Optional[str] = None
) -> List[Dict]:
    """Generate weekly series for current quarter."""
    q_start, q_end = get_current_quarter_dates(current_date)
    return generate_weekly_series(weekly_totals, q_start, q_end)


def generate_month_series(
    weekly_totals: Dict,
    current_date: Optional[str] = None
) -> List[Dict]:
    """Generate weekly series for +/- 5 weeks (looking glass)."""
    lg_start, lg_end = get_looking_glass_dates(current_date)
    return generate_weekly_series(weekly_totals, lg_start, lg_end)


def generate_weekly_series(
    weekly_totals: Dict,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """
    Generate weekly series for a date range.

    Args:
        weekly_totals: Aggregated weekly costs
        start_date: Range start (YYYY-MM-DD)
        end_date: Range end (YYYY-MM-DD)

    Returns:
        List of trend points sorted by date
    """
    series = []
    cumm_plan = 0.0
    cumm_actual = 0.0

    # Get all weeks in range
    current = datetime.fromisoformat(get_week_start(start_date))
    end = datetime.fromisoformat(end_date)
    week_num = 1

    while current <= end:
        week_key = current.strftime("%Y-%m-%d")
        costs = weekly_totals.get(week_key, {"plan": 0.0, "actual": 0.0})

        cumm_plan += costs["plan"]
        cumm_actual += costs["actual"]

        series.append({
            "label": get_week_label(current, week_num),
            "sort_date": week_key,
            "plan_cost": costs["plan"] if costs["plan"] else None,
            "actual_cost": costs["actual"] if costs["actual"] else None,
            "cumm_plan": cumm_plan,
            "cumm_actual": cumm_actual
        })

        current += timedelta(days=7)
        week_num += 1

    return series
