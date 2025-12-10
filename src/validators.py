"""
Validators for QA and schema validation.

Provides validation against JSON schema and sample comparison
with source XML for quality assurance.
"""

import random
import xml.etree.ElementTree as ET
from typing import Any

from .transformers import (
    boolean_from_string,
    extract_date,
    iso8601_duration_to_days,
    parse_float,
    parse_int,
)
from .xml_parser import NAMESPACE, get_element_text


def validate_task_structure(task: dict) -> list[str]:
    """
    Validate that a task has all required fields.

    Args:
        task: Task dictionary to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Required top-level fields
    required_fields = [
        "uid",
        "id",
        "wbs",
        "outline_number",
        "name",
        "parent_wbs",
        "is_summary",
        "is_milestone",
        "dates",
        "attributes",
        "progress",
        "cost_plan_total",
        "cost_timeline",
    ]

    for field in required_fields:
        if field not in task:
            errors.append(f"Missing required field: {field}")

    # Validate dates structure
    if "dates" in task:
        dates = task["dates"]
        for date_type in ["plan", "manual", "sprint", "actual"]:
            if date_type not in dates:
                errors.append(f"Missing dates.{date_type}")
            else:
                for date_field in ["start", "end", "duration_days"]:
                    if date_field not in dates[date_type]:
                        errors.append(f"Missing dates.{date_type}.{date_field}")

    # Validate progress structure for non-parent tasks
    if task.get("progress") is not None:
        progress = task["progress"]
        if "percent_complete" not in progress:
            errors.append("Missing progress.percent_complete")
        if "is_complete" not in progress:
            errors.append("Missing progress.is_complete")

    return errors


def validate_task_types(tasks: list[dict]) -> dict:
    """
    Validate task type consistency.

    Args:
        tasks: List of task dictionaries

    Returns:
        Dictionary with validation results
    """
    results = {
        "total": len(tasks),
        "parents": 0,
        "leaves": 0,
        "milestones": 0,
        "issues": [],
    }

    for task in tasks:
        is_summary = task.get("is_summary", False)
        is_milestone = task.get("is_milestone", False)

        if is_summary:
            results["parents"] += 1
            # Parents should have null attributes, progress, cost
            if task.get("attributes") is not None:
                results["issues"].append(
                    f"UID {task.get('uid')}: Parent has non-null attributes"
                )
            if task.get("progress") is not None:
                results["issues"].append(
                    f"UID {task.get('uid')}: Parent has non-null progress"
                )
            if task.get("cost_plan_total") is not None:
                results["issues"].append(
                    f"UID {task.get('uid')}: Parent has non-null cost_plan_total"
                )
        elif is_milestone:
            results["milestones"] += 1
            # Milestones should have null attributes and cost_timeline
            if task.get("attributes") is not None:
                results["issues"].append(
                    f"UID {task.get('uid')}: Milestone has non-null attributes"
                )
            if task.get("cost_timeline") is not None:
                results["issues"].append(
                    f"UID {task.get('uid')}: Milestone has non-null cost_timeline"
                )
        else:
            results["leaves"] += 1

    return results


def find_xml_task_by_uid(xml_file: str, uid: int) -> dict | None:
    """
    Find a task in XML file by UID.

    Args:
        xml_file: Path to XML file
        uid: Task UID to find

    Returns:
        Dictionary with XML task data or None
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    tasks_elem = root.find("ms:Tasks", NAMESPACE)
    if tasks_elem is None:
        return None

    for task_elem in tasks_elem.findall("ms:Task", NAMESPACE):
        task_uid = get_element_text(task_elem, "UID")
        if task_uid == str(uid):
            return {
                "uid": task_uid,
                "id": get_element_text(task_elem, "ID"),
                "name": get_element_text(task_elem, "Name"),
                "wbs": get_element_text(task_elem, "WBS"),
                "outline_number": get_element_text(task_elem, "OutlineNumber"),
                "start": get_element_text(task_elem, "Start"),
                "finish": get_element_text(task_elem, "Finish"),
                "duration": get_element_text(task_elem, "Duration"),
                "percent_complete": get_element_text(task_elem, "PercentComplete"),
                "fixed_cost": get_element_text(task_elem, "FixedCost"),
                "summary": get_element_text(task_elem, "Summary"),
                "milestone": get_element_text(task_elem, "Milestone"),
            }

    return None


def compare_task_to_xml(task: dict, xml_task: dict) -> dict:
    """
    Compare a transformed task against source XML task.

    Args:
        task: Transformed task dictionary
        xml_task: Original XML task dictionary

    Returns:
        Dictionary with comparison results
    """
    result = {
        "uid": task.get("uid"),
        "matches": True,
        "fields": {},
    }

    # Compare WBS
    xml_wbs = xml_task.get("wbs")
    task_wbs = task.get("wbs")
    result["fields"]["wbs"] = {
        "expected": xml_wbs,
        "actual": task_wbs,
        "match": xml_wbs == task_wbs,
    }

    # Compare name
    xml_name = xml_task.get("name")
    task_name = task.get("name")
    result["fields"]["name"] = {
        "expected": xml_name,
        "actual": task_name,
        "match": xml_name == task_name,
    }

    # Compare plan start
    xml_start = extract_date(xml_task.get("start"))
    task_start = task.get("dates", {}).get("plan", {}).get("start")
    result["fields"]["dates.plan.start"] = {
        "expected": xml_start,
        "actual": task_start,
        "match": xml_start == task_start,
    }

    # Compare plan end
    xml_end = extract_date(xml_task.get("finish"))
    task_end = task.get("dates", {}).get("plan", {}).get("end")
    result["fields"]["dates.plan.end"] = {
        "expected": xml_end,
        "actual": task_end,
        "match": xml_end == task_end,
    }

    # Compare duration
    xml_duration = iso8601_duration_to_days(xml_task.get("duration"))
    task_duration = task.get("dates", {}).get("plan", {}).get("duration_days")
    result["fields"]["dates.plan.duration_days"] = {
        "expected": xml_duration,
        "actual": task_duration,
        "match": xml_duration == task_duration,
    }

    # Compare percent_complete (for non-parents)
    if task.get("progress") is not None:
        xml_pct = parse_int(xml_task.get("percent_complete")) or 0
        task_pct = task.get("progress", {}).get("percent_complete")
        result["fields"]["progress.percent_complete"] = {
            "expected": xml_pct,
            "actual": task_pct,
            "match": xml_pct == task_pct,
        }

    # Compare cost_plan_total (for non-parents)
    if not boolean_from_string(xml_task.get("summary")):
        xml_cost = parse_float(xml_task.get("fixed_cost"))
        task_cost = task.get("cost_plan_total")
        result["fields"]["cost_plan_total"] = {
            "expected": xml_cost,
            "actual": task_cost,
            "match": xml_cost == task_cost,
        }

    # Check if all fields match
    for field_result in result["fields"].values():
        if not field_result.get("match"):
            result["matches"] = False
            break

    return result


def sample_validation(
    output_tasks: list[dict], xml_file: str, sample_size: int = 100
) -> dict:
    """
    Validate a random sample of output tasks against source XML.

    Args:
        output_tasks: List of transformed task dictionaries
        xml_file: Path to source XML file
        sample_size: Number of tasks to sample

    Returns:
        Dictionary with sample validation results
    """
    results = {
        "sample_size": min(sample_size, len(output_tasks)),
        "passed": 0,
        "failed": 0,
        "comparisons": [],
    }

    # Select random sample
    sample = random.sample(output_tasks, results["sample_size"])

    for task in sample:
        uid = task.get("uid")

        # Find corresponding XML task
        xml_task = find_xml_task_by_uid(xml_file, uid)

        if xml_task is None:
            results["failed"] += 1
            results["comparisons"].append(
                {
                    "uid": uid,
                    "error": f"Task UID {uid} not found in XML",
                }
            )
            continue

        # Compare
        comparison = compare_task_to_xml(task, xml_task)
        results["comparisons"].append(comparison)

        if comparison["matches"]:
            results["passed"] += 1
        else:
            results["failed"] += 1

    results["pass_rate"] = (
        results["passed"] / results["sample_size"] if results["sample_size"] > 0 else 0
    )

    return results


def calculate_field_coverage(tasks: list[dict]) -> dict:
    """
    Calculate coverage statistics for nullable fields.

    Args:
        tasks: List of transformed task dictionaries

    Returns:
        Dictionary with field coverage percentages
    """
    total = len(tasks)
    if total == 0:
        return {}

    coverage = {
        "dates.actual.start": 0,
        "dates.actual.end": 0,
        "dates.actual.duration_days": 0,
        "cost_timeline": 0,
        "attributes": 0,
        "progress": 0,
    }

    for task in tasks:
        # Count non-null actual dates
        actual = task.get("dates", {}).get("actual", {})
        if actual.get("start") is not None:
            coverage["dates.actual.start"] += 1
        if actual.get("end") is not None:
            coverage["dates.actual.end"] += 1
        if actual.get("duration_days") is not None:
            coverage["dates.actual.duration_days"] += 1

        # Count non-null cost_timeline
        if task.get("cost_timeline") is not None:
            coverage["cost_timeline"] += 1

        # Count non-null attributes
        if task.get("attributes") is not None:
            coverage["attributes"] += 1

        # Count non-null progress
        if task.get("progress") is not None:
            coverage["progress"] += 1

    # Convert to percentages
    for field in coverage:
        coverage[field] = round(coverage[field] / total, 2)

    return coverage


def generate_qa_report(
    project_name: str,
    total_tasks: int,
    type_validation: dict,
    sample_results: dict,
    field_coverage: dict,
) -> dict:
    """
    Generate comprehensive QA report.

    Args:
        project_name: Name of the project
        total_tasks: Total number of tasks processed
        type_validation: Results from validate_task_types
        sample_results: Results from sample_validation
        field_coverage: Results from calculate_field_coverage

    Returns:
        Complete QA report dictionary
    """
    return {
        "project": project_name,
        "total_tasks": total_tasks,
        "parents": type_validation.get("parents", 0),
        "leaves": type_validation.get("leaves", 0),
        "milestones": type_validation.get("milestones", 0),
        "sample_size": sample_results.get("sample_size", 0),
        "sample_pass_rate": sample_results.get("pass_rate", 0),
        "validation_issues": type_validation.get("issues", []),
        "sample_failures": [
            c for c in sample_results.get("comparisons", []) if not c.get("matches", True)
        ],
        "field_coverage": field_coverage,
    }
