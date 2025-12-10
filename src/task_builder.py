"""
Task Builder for constructing target JSON objects.

Transforms parsed XML task data into the target schema format
as defined in task_schema.json.
"""

from typing import Any

from .transformers import (
    boolean_from_string,
    calculate_duration_days,
    derive_actual_end,
    derive_actual_start,
    extract_date,
    iso8601_duration_to_days,
    parse_float,
    parse_int,
    remove_last_segment,
)
from .xml_parser import get_task_timephased_data


def determine_task_type(xml_task: dict) -> str:
    """
    Determine the task type based on flags.

    Args:
        xml_task: Parsed XML task dictionary

    Returns:
        'parent', 'leaf', or 'milestone'
    """
    is_summary = boolean_from_string(xml_task.get("summary"))
    is_milestone = boolean_from_string(xml_task.get("milestone"))

    if is_summary:
        return "parent"
    elif is_milestone:
        return "milestone"
    else:
        return "leaf"


def build_dates_plan(xml_task: dict) -> dict:
    """
    Build the dates.plan object.

    Args:
        xml_task: Parsed XML task dictionary

    Returns:
        Plan dates object with start, end, duration_days
    """
    return {
        "start": extract_date(xml_task.get("start")),
        "end": extract_date(xml_task.get("finish")),
        "duration_days": iso8601_duration_to_days(xml_task.get("duration")),
    }


def build_dates_manual(xml_task: dict) -> dict:
    """
    Build the dates.manual object.

    Args:
        xml_task: Parsed XML task dictionary

    Returns:
        Manual dates object with start, end, duration_days
    """
    return {
        "start": extract_date(xml_task.get("manual_start")),
        "end": extract_date(xml_task.get("manual_finish")),
        "duration_days": iso8601_duration_to_days(xml_task.get("manual_duration")),
    }


def build_dates_sprint() -> dict:
    """
    Build the dates.sprint object.

    Sprint dates come from separate XML files, so always null in baseline ETL.

    Returns:
        Sprint dates object with all null values
    """
    return {
        "start": None,
        "end": None,
        "duration_days": None,
    }


def build_dates_actual_leaf(
    xml_task: dict, task_assignment_map: dict[str, list[dict]]
) -> dict:
    """
    Build the dates.actual object for leaf tasks.

    Actual dates are derived from TimephasedData Type=2 in Assignments.

    Args:
        xml_task: Parsed XML task dictionary
        task_assignment_map: Mapping from TaskUID to assignments

    Returns:
        Actual dates object
    """
    task_uid = xml_task.get("uid")
    timephased_data = get_task_timephased_data(task_uid, task_assignment_map)

    actual_start = derive_actual_start(timephased_data)
    actual_end = derive_actual_end(timephased_data)
    duration_days = calculate_duration_days(actual_start, actual_end)

    return {
        "start": actual_start,
        "end": actual_end,
        "duration_days": duration_days,
    }


def build_dates_actual_milestone(xml_task: dict) -> dict:
    """
    Build the dates.actual object for milestones.

    Milestones use ActualStart/ActualFinish from the Task element directly.

    Args:
        xml_task: Parsed XML task dictionary

    Returns:
        Actual dates object (duration always 0 for milestones)
    """
    actual_start = extract_date(xml_task.get("actual_start"))
    actual_finish = extract_date(xml_task.get("actual_finish"))

    # If task is complete, use actual finish as both start and end
    # (milestones have 0 duration)
    return {
        "start": actual_start,
        "end": actual_finish,
        "duration_days": 0 if actual_start or actual_finish else None,
    }


def build_dates_actual_parent() -> dict:
    """
    Build the dates.actual object for parent tasks.

    Parent tasks don't have actual dates (rolled up from children).

    Returns:
        Actual dates object with all null values
    """
    return {
        "start": None,
        "end": None,
        "duration_days": None,
    }


def build_dates_object(
    xml_task: dict, task_type: str, task_assignment_map: dict[str, list[dict]]
) -> dict:
    """
    Build the complete dates object.

    Args:
        xml_task: Parsed XML task dictionary
        task_type: 'parent', 'leaf', or 'milestone'
        task_assignment_map: Mapping from TaskUID to assignments

    Returns:
        Complete dates object with plan, manual, sprint, actual
    """
    # Build actual dates based on task type
    if task_type == "parent":
        actual = build_dates_actual_parent()
    elif task_type == "milestone":
        actual = build_dates_actual_milestone(xml_task)
    else:  # leaf
        actual = build_dates_actual_leaf(xml_task, task_assignment_map)

    return {
        "plan": build_dates_plan(xml_task),
        "manual": build_dates_manual(xml_task),
        "sprint": build_dates_sprint(),
        "actual": actual,
    }


def build_attributes_placeholder(project_name: str, task_type: str) -> dict | None:
    """
    Build the attributes placeholder object.

    Attributes come from external master data. In this ETL we only set
    project_name; other fields are null to be enriched separately.

    Args:
        project_name: Project name derived from filename
        task_type: 'parent', 'leaf', or 'milestone'

    Returns:
        Attributes object with project_name, or None for parents/milestones
    """
    # Parents and milestones have null attributes
    if task_type in ("parent", "milestone"):
        return None

    # Leaf tasks get placeholder attributes
    return {
        "project_name": project_name,
        "zone": None,
        "region": None,
        "tower": None,
        "floor": None,
        "main_category": None,
        "sub_category": None,
        "trade_type": None,
        "slab_works": None,
    }


def build_progress_object(xml_task: dict, task_type: str) -> dict | None:
    """
    Build the progress object.

    Args:
        xml_task: Parsed XML task dictionary
        task_type: 'parent', 'leaf', or 'milestone'

    Returns:
        Progress object or None for parent tasks
    """
    # Parent tasks have null progress
    if task_type == "parent":
        return None

    percent_complete = parse_int(xml_task.get("percent_complete")) or 0

    return {
        "percent_complete": percent_complete,
        "is_complete": percent_complete == 100,
    }


def build_task(
    xml_task: dict,
    task_assignment_map: dict[str, list[dict]],
    project_name: str,
    cost_timeline_builder: Any = None,
) -> dict:
    """
    Transform XML task to target schema format.

    Args:
        xml_task: Parsed XML task dictionary
        task_assignment_map: Mapping from TaskUID to assignments
        project_name: Project name for attributes
        cost_timeline_builder: Optional callable to build cost_timeline

    Returns:
        Task dictionary conforming to task_schema.json
    """
    task_type = determine_task_type(xml_task)
    dates = build_dates_object(xml_task, task_type, task_assignment_map)
    progress = build_progress_object(xml_task, task_type)

    # Get cost_plan_total (null for parents)
    if task_type == "parent":
        cost_plan_total = None
    else:
        cost_plan_total = parse_float(xml_task.get("fixed_cost"))

    # Build cost_timeline if builder provided and applicable
    cost_timeline = None
    if (
        cost_timeline_builder is not None
        and task_type == "leaf"
        and cost_plan_total
        and cost_plan_total > 0
    ):
        is_complete = progress.get("is_complete", False) if progress else False
        cost_timeline = cost_timeline_builder(
            cost_plan_total=cost_plan_total,
            plan_dates=dates["plan"],
            actual_dates=dates["actual"],
            is_complete=is_complete,
        )

    return {
        "uid": parse_int(xml_task.get("uid")),
        "id": parse_int(xml_task.get("id")),
        "wbs": xml_task.get("wbs"),
        "outline_number": xml_task.get("outline_number"),
        "name": xml_task.get("name"),
        "parent_wbs": remove_last_segment(xml_task.get("wbs")),
        "is_summary": boolean_from_string(xml_task.get("summary")),
        "is_milestone": boolean_from_string(xml_task.get("milestone")),
        "dates": dates,
        "attributes": build_attributes_placeholder(project_name, task_type),
        "progress": progress,
        "cost_plan_total": cost_plan_total,
        "cost_timeline": cost_timeline,
    }


def build_all_tasks(
    tasks: list[dict],
    task_assignment_map: dict[str, list[dict]],
    project_name: str,
    cost_timeline_builder: Any = None,
) -> list[dict]:
    """
    Transform all XML tasks to target schema format.

    Args:
        tasks: List of parsed XML task dictionaries
        task_assignment_map: Mapping from TaskUID to assignments
        project_name: Project name for attributes
        cost_timeline_builder: Optional callable to build cost_timeline

    Returns:
        List of task dictionaries conforming to task_schema.json
    """
    return [
        build_task(task, task_assignment_map, project_name, cost_timeline_builder)
        for task in tasks
    ]
