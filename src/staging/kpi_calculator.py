"""
KPI Calculator - Calculate AOP and Sprint achievement gauges
"""

from typing import Dict, List, Optional


def calculate_kpi_gauges(
    tasks: List[Dict],
    current_date: Optional[str] = None
) -> Dict:
    """
    Calculate AOP and Sprint achievement values.

    Args:
        tasks: Filtered tasks
        current_date: Override for "today" (YYYY-MM-DD)

    Returns:
        {
            "aop": {"achieved_pct": 87.5, "status_color": "amber", ...},
            "sprint": {"achieved_pct": 92.0, "status_color": "green", ...}
        }
    """
    return {
        "aop": calculate_aop_gauge(tasks),
        "sprint": calculate_sprint_gauge(tasks, current_date)
    }


def calculate_aop_gauge(tasks: List[Dict]) -> Dict:
    """
    Calculate AOP Achievement gauge.

    Formula: (Total Actual Cost YTD / Total Plan Cost YTD) * 100
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
        summary = timeline.get("summary") or {}

        plan = summary.get("plan_cost_in_fy") or 0.0
        actual = summary.get("actual_cost_in_fy") or 0.0

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


def calculate_sprint_gauge(
    tasks: List[Dict],
    current_date: Optional[str] = None
) -> Dict:
    """
    Calculate Sprint Achievement gauge.

    Only considers tasks with Sprint dates.
    Formula: (Sprint Actual / Sprint Plan) * 100
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

        # Get cost data
        timeline = task.get("cost_timeline") or {}
        summary = timeline.get("summary") or {}

        # Sprint plan = portion of cost aligned to sprint schedule
        # For simplicity, use plan_cost_in_fy as sprint plan
        # (More sophisticated: prorate based on sprint duration)
        plan = summary.get("plan_cost_in_fy") or 0.0
        actual = summary.get("actual_cost_in_fy") or 0.0

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
