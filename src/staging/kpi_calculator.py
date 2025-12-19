"""
KPI Calculator - Calculate AOP and Sprint achievement gauges
"""

from typing import Dict, List, Optional
from datetime import datetime

from .time_utils import (
    get_fy_dates,
    get_current_quarter_dates,
    get_looking_glass_dates
)


def calculate_kpi_gauges(
    tasks: List[Dict],
    current_date: Optional[str] = None
) -> Dict:
    """
    Calculate AOP and Sprint achievement values for all time modes.

    Args:
        tasks: Filtered tasks
        current_date: Override for "today" (YYYY-MM-DD)

    Returns:
        {
            "aop": {
                "fy": {"achieved_pct": 87.5, "status_color": "amber", ...},
                "quarter": {...},
                "month": {...}
            },
            "sprint": {
                "fy": {...},
                "quarter": {...},
                "month": {...}
            }
        }
    """
    # Get date ranges for each time mode
    fy_start, fy_end = get_fy_dates()
    q_start, q_end = get_current_quarter_dates(current_date)
    lg_start, lg_end = get_looking_glass_dates(current_date)

    return {
        "aop": {
            "fy": calculate_aop_gauge_for_period(tasks, fy_start, fy_end),
            "quarter": calculate_aop_gauge_for_period(tasks, q_start, q_end),
            "month": calculate_aop_gauge_for_period(tasks, lg_start, lg_end)
        },
        "sprint": {
            "fy": calculate_sprint_gauge_for_period(tasks, fy_start, fy_end),
            "quarter": calculate_sprint_gauge_for_period(tasks, q_start, q_end),
            "month": calculate_sprint_gauge_for_period(tasks, lg_start, lg_end)
        }
    }


def calculate_aop_gauge_for_period(tasks: List[Dict], start_date: str, end_date: str) -> Dict:
    """
    Calculate AOP Achievement gauge for a specific period.

    Sums weekly costs that fall within the period.
    """
    total_plan = 0.0
    total_actual = 0.0
    tasks_with_sprint = 0

    for task in tasks:
        # Only include leaf tasks with cost data
        if task.get("is_summary") or task.get("is_milestone"):
            continue

        # Check if task has sprint dates (for QC metric)
        dates = task.get("dates") or {}
        sprint = dates.get("sprint") or {}
        if sprint.get("start"):
            tasks_with_sprint += 1

        timeline = task.get("cost_timeline") or {}
        weekly_costs = timeline.get("weekly_costs") or []

        # Sum costs for weeks within the period
        for week in weekly_costs:
            week_start = week.get("week_start")
            if not week_start:
                continue

            # Check if week falls within period
            if start_date <= week_start <= end_date:
                plan = week.get("plan", {}).get("cost") or 0.0
                actual = week.get("actual", {}).get("cost") or 0.0
                total_plan += plan
                total_actual += actual

    # Calculate percentage
    if total_plan > 0:
        achieved_pct = (total_actual / total_plan) * 100
    else:
        achieved_pct = 0.0

    return {
        "achieved_pct": round(achieved_pct, 1),
        "status_color": get_status_color(achieved_pct),
        "actual": round(total_actual, 2),
        "plan": round(total_plan, 2),
        "tasks_with_sprint": tasks_with_sprint
    }


def calculate_sprint_gauge_for_period(tasks: List[Dict], start_date: str, end_date: str) -> Dict:
    """
    Calculate Sprint Achievement gauge for a specific period.

    Only considers tasks with Sprint dates.
    """
    sprint_plan = 0.0
    sprint_actual = 0.0
    tasks_with_sprint = 0

    for task in tasks:
        if task.get("is_summary") or task.get("is_milestone"):
            continue

        # Check if task has Sprint dates
        dates = task.get("dates") or {}
        sprint = dates.get("sprint") or {}

        if not sprint.get("start"):
            continue

        tasks_with_sprint += 1

        # Get cost data for weeks within period
        timeline = task.get("cost_timeline") or {}
        weekly_costs = timeline.get("weekly_costs") or []

        for week in weekly_costs:
            week_start = week.get("week_start")
            if not week_start:
                continue

            # Check if week falls within period
            if start_date <= week_start <= end_date:
                plan = week.get("plan", {}).get("cost") or 0.0
                actual = week.get("actual", {}).get("cost") or 0.0
                sprint_plan += plan
                sprint_actual += actual

    # Calculate percentage
    if sprint_plan > 0:
        achieved_pct = (sprint_actual / sprint_plan) * 100
    else:
        achieved_pct = 0.0

    return {
        "achieved_pct": round(achieved_pct, 1),
        "status_color": get_status_color(achieved_pct),
        "actual": round(sprint_actual, 2),
        "plan": round(sprint_plan, 2),
        "tasks_with_sprint": tasks_with_sprint
    }


def get_status_color(percentage: float) -> str:
    """
    Determine gauge color based on achievement percentage.

    Thresholds:
        - Red: < 85%
        - Amber: 85% - 95%
        - Green: > 95%
    """
    if percentage < 85:
        return "red"
    elif percentage <= 95:
        return "amber"
    else:
        return "green"
