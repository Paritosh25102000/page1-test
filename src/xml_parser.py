"""
XML Parser for Microsoft Project XML files.

Extracts Tasks and Assignments from Asta Powerproject XML exports
using memory-efficient parsing for large files.
"""

import xml.etree.ElementTree as ET
from typing import Any

# Microsoft Project XML namespace
NAMESPACE = {"ms": "http://schemas.microsoft.com/project"}


def get_element_text(element: ET.Element, tag: str, ns: dict = NAMESPACE) -> str | None:
    """
    Get text content of a child element.

    Args:
        element: Parent XML element
        tag: Child element tag name (without namespace prefix)
        ns: Namespace dictionary

    Returns:
        Text content or None if element not found
    """
    child = element.find(f"ms:{tag}", ns)
    return child.text if child is not None else None


def parse_task_element(task_elem: ET.Element) -> dict:
    """
    Parse a Task element into a dictionary.

    Args:
        task_elem: XML Task element

    Returns:
        Dictionary with task fields
    """
    return {
        "uid": get_element_text(task_elem, "UID"),
        "id": get_element_text(task_elem, "ID"),
        "name": get_element_text(task_elem, "Name"),
        "wbs": get_element_text(task_elem, "WBS"),
        "outline_number": get_element_text(task_elem, "OutlineNumber"),
        "start": get_element_text(task_elem, "Start"),
        "finish": get_element_text(task_elem, "Finish"),
        "manual_start": get_element_text(task_elem, "ManualStart"),
        "manual_finish": get_element_text(task_elem, "ManualFinish"),
        "duration": get_element_text(task_elem, "Duration"),
        "manual_duration": get_element_text(task_elem, "ManualDuration"),
        "milestone": get_element_text(task_elem, "Milestone"),
        "summary": get_element_text(task_elem, "Summary"),
        "percent_complete": get_element_text(task_elem, "PercentComplete"),
        "fixed_cost": get_element_text(task_elem, "FixedCost"),
        "actual_start": get_element_text(task_elem, "ActualStart"),
        "actual_finish": get_element_text(task_elem, "ActualFinish"),
    }


def parse_timephased_data(tpd_elem: ET.Element) -> dict:
    """
    Parse a TimephasedData element.

    Args:
        tpd_elem: XML TimephasedData element

    Returns:
        Dictionary with timephased data fields
    """
    return {
        "type": get_element_text(tpd_elem, "Type"),
        "uid": get_element_text(tpd_elem, "UID"),
        "start": get_element_text(tpd_elem, "Start"),
        "finish": get_element_text(tpd_elem, "Finish"),
        "value": get_element_text(tpd_elem, "Value"),
    }


def parse_assignment_element(assign_elem: ET.Element) -> dict:
    """
    Parse an Assignment element into a dictionary.

    Args:
        assign_elem: XML Assignment element

    Returns:
        Dictionary with assignment fields and TimephasedData
    """
    assignment = {
        "uid": get_element_text(assign_elem, "UID"),
        "task_uid": get_element_text(assign_elem, "TaskUID"),
        "resource_uid": get_element_text(assign_elem, "ResourceUID"),
        "start": get_element_text(assign_elem, "Start"),
        "finish": get_element_text(assign_elem, "Finish"),
        "actual_start": get_element_text(assign_elem, "ActualStart"),
        "actual_finish": get_element_text(assign_elem, "ActualFinish"),
        "timephased_data": [],
    }

    # Extract all TimephasedData elements
    for tpd in assign_elem.findall("ms:TimephasedData", NAMESPACE):
        assignment["timephased_data"].append(parse_timephased_data(tpd))

    return assignment


def extract_tasks(root: ET.Element) -> list[dict]:
    """
    Extract all Task elements from XML root.

    Args:
        root: XML root element

    Returns:
        List of task dictionaries
    """
    tasks = []
    tasks_elem = root.find("ms:Tasks", NAMESPACE)

    if tasks_elem is not None:
        for task_elem in tasks_elem.findall("ms:Task", NAMESPACE):
            tasks.append(parse_task_element(task_elem))

    return tasks


def extract_assignments(root: ET.Element) -> list[dict]:
    """
    Extract all Assignment elements from XML root.

    Args:
        root: XML root element

    Returns:
        List of assignment dictionaries with TimephasedData
    """
    assignments = []
    assignments_elem = root.find("ms:Assignments", NAMESPACE)

    if assignments_elem is not None:
        for assign_elem in assignments_elem.findall("ms:Assignment", NAMESPACE):
            assignments.append(parse_assignment_element(assign_elem))

    return assignments


def build_task_assignment_map(assignments: list[dict]) -> dict[str, list[dict]]:
    """
    Build a mapping from TaskUID to list of assignments.

    This is used to find all assignments for a specific task,
    which is needed to derive actual dates from TimephasedData.

    Args:
        assignments: List of assignment dictionaries

    Returns:
        Dictionary mapping TaskUID (as string) to list of assignments
    """
    task_map: dict[str, list[dict]] = {}

    for assignment in assignments:
        task_uid = assignment.get("task_uid")
        if task_uid:
            if task_uid not in task_map:
                task_map[task_uid] = []
            task_map[task_uid].append(assignment)

    return task_map


def extract_project_metadata(root: ET.Element) -> dict:
    """
    Extract project-level metadata from XML.

    Args:
        root: XML root element

    Returns:
        Dictionary with project metadata
    """
    return {
        "name": get_element_text(root, "Name"),
        "title": get_element_text(root, "Title"),
        "start_date": get_element_text(root, "StartDate"),
        "finish_date": get_element_text(root, "FinishDate"),
        "author": get_element_text(root, "Author"),
    }


def parse_xml_file(file_path: str) -> dict[str, Any]:
    """
    Parse an XML file and return structured data.

    This function loads the entire XML into memory. For very large files,
    consider using iterparse-based streaming if memory becomes an issue.

    Args:
        file_path: Path to the XML file

    Returns:
        Dictionary containing:
        - project: Project metadata
        - tasks: List of task dictionaries
        - assignments: List of assignment dictionaries
        - task_assignment_map: Mapping of TaskUID -> assignments
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract components
    project = extract_project_metadata(root)
    tasks = extract_tasks(root)
    assignments = extract_assignments(root)
    task_assignment_map = build_task_assignment_map(assignments)

    return {
        "project": project,
        "tasks": tasks,
        "assignments": assignments,
        "task_assignment_map": task_assignment_map,
    }


def get_task_timephased_data(
    task_uid: str, task_assignment_map: dict[str, list[dict]]
) -> list[dict]:
    """
    Get all Type=2 (Actual Work) TimephasedData for a task.

    Collects TimephasedData from all assignments linked to the task.

    Args:
        task_uid: Task UID to look up
        task_assignment_map: Mapping from TaskUID to assignments

    Returns:
        List of TimephasedData dictionaries with Type=2
    """
    timephased_data = []

    assignments = task_assignment_map.get(task_uid, [])
    for assignment in assignments:
        for tpd in assignment.get("timephased_data", []):
            if tpd.get("type") == "2":  # Type 2 = Actual Work
                timephased_data.append(tpd)

    return timephased_data
