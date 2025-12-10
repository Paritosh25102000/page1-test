"""
Extract unique work activities from project tasks for trade type classification.

Handles:
- Spatial vs activity leaf detection
- Parent hierarchy traversal
- Context type determination (tower, common area, external, infrastructure)
- Activity grouping and statistics
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


def is_spatial_leaf(task_name: str) -> bool:
    """
    Detect if leaf task represents spatial division rather than actual activity.

    Spatial patterns:
    - "Floor 1", "Floor 2", "1st Floor", "2nd Floor"
    - "Tower A", "Tower B", "Tower 1"
    - "Unit 101", "Flat A", "Apartment 201"
    - Pure numbers: "1", "2", "3"
    - Floor ranges: "Floor 1 to 2", "1-5"

    Args:
        task_name: Task name to check

    Returns:
        True if spatial, False if actual activity
    """
    if not task_name:
        return False

    name_lower = task_name.lower().strip()

    # Pattern 1: Pure floor references
    if re.match(r'^(floor\s+)?(\d+)(st|nd|rd|th)?(\s+floor)?$', name_lower):
        return True

    # Pattern 2: Floor ranges
    if re.match(r'^(floor\s+)?\d+\s*(to|-)\s*\d+$', name_lower):
        return True

    # Pattern 3: Ground/Terrace/Basement alone
    if name_lower in ['ground floor', 'terrace', 'basement', 'ground', 'gf']:
        return True

    # Pattern 4: Tower/Block alone
    if re.match(r'^(tower|block|building)\s*[a-z0-9]+$', name_lower):
        return True

    # Pattern 5: Unit/Flat/Apartment references
    if re.match(r'^(unit|flat|apartment|apt)\s*[a-z0-9]+$', name_lower):
        return True

    # Pattern 6: Pure numbers (likely floor numbers in context)
    if re.match(r'^\d+$', name_lower):
        return True

    return False


def extract_activity_from_parent(
    task: Dict,
    tasks_by_wbs: Dict[str, Dict]
) -> Tuple[str, List[str]]:
    """
    Traverse parent chain to find actual activity name.

    Args:
        task: Task dictionary
        tasks_by_wbs: Mapping of WBS -> task for quick lookup

    Returns:
        Tuple of (activity_name, parent_chain_names)
    """
    parent_chain = []
    current_wbs = task.get("parent_wbs")
    max_depth = 10

    while current_wbs and max_depth > 0:
        parent = tasks_by_wbs.get(current_wbs)
        if not parent:
            break

        parent_name = parent.get("name", "")
        parent_chain.append(parent_name)

        # If parent is not spatial and not a summary container, use it as activity
        if not is_spatial_leaf(parent_name) and parent_name:
            # Check if it's a meaningful activity name (not just container)
            if not _is_generic_container(parent_name):
                return parent_name, parent_chain

        current_wbs = parent.get("parent_wbs")
        max_depth -= 1

    # If no suitable parent found, use task's own name
    return task.get("name", "Unknown"), parent_chain


def _is_generic_container(name: str) -> bool:
    """Check if name is a generic container (not actual activity)."""
    generic_patterns = [
        r'^project\s',
        r'^phase\s',
        r'^stage\s',
        r'^\w+\s*\|\s*\w+$',  # "Miraya | Sec 43"
        r'^snapshot$',
        r'^data$',
    ]

    name_lower = name.lower()
    for pattern in generic_patterns:
        if re.search(pattern, name_lower):
            return True

    return False


def determine_context_type(
    task: Dict,
    parent_chain: List[str],
    tasks_by_wbs: Dict[str, Dict]
) -> str:
    """
    Determine activity context from task attributes and parent hierarchy.

    Context Types:
    - "tower": Flat/apartment finishing (has tower+floor context)
    - "common_area": Shared spaces (staircase, lift, lobby, basement)
    - "external": Site work, external services
    - "infrastructure": MEP infrastructure (STP, WTP, DG, Substation)

    Args:
        task: Task dictionary
        parent_chain: List of parent task names
        tasks_by_wbs: Task lookup dictionary

    Returns:
        Context type string
    """
    # Check task attributes first
    attributes = task.get("attributes")
    if attributes:
        tower = attributes.get("tower")
        floor = attributes.get("floor")

        # If has both tower and floor, likely tower/flat context
        if tower and floor:
            # Check for common area indicators in parent chain
            if _has_common_area_indicators(parent_chain):
                return "common_area"
            return "tower"

        # Has tower but no floor - could be tower-level common areas
        if tower and not floor:
            if _has_common_area_indicators(parent_chain):
                return "common_area"
            # Tower-level work (e.g., terrace, roof)
            return "tower"

    # Check parent chain for context clues
    parent_chain_text = " ".join(parent_chain).lower()

    # Infrastructure indicators
    if any(keyword in parent_chain_text for keyword in [
        'stp', 'sewage', 'treatment plant',
        'wtp', 'water treatment',
        'substation', 'transformer',
        'dg', 'generator',
        'solar', 'panel',
        'owc', 'waste'
    ]):
        return "infrastructure"

    # External indicators
    if any(keyword in parent_chain_text for keyword in [
        'external', 'exterior', 'outside',
        'site', 'boundary', 'compound',
        'road', 'pavement', 'driveway',
        'landscape', 'garden', 'softscape', 'hardscape',
        'main', 'rising main'
    ]):
        return "external"

    # Common area indicators
    if _has_common_area_indicators(parent_chain):
        return "common_area"

    # Default to tower if no other context found
    return "tower"


def _has_common_area_indicators(parent_chain: List[str]) -> bool:
    """Check if parent chain contains common area indicators."""
    parent_chain_text = " ".join(parent_chain).lower()

    common_area_keywords = [
        'common area', 'common',
        'staircase', 'stair',
        'lift', 'elevator',
        'lobby', 'entrance', 'foyer',
        'corridor', 'passage',
        'basement', 'parking',
        'terrace', 'roof',  # When at common area level
        'lmr', 'mumty',
        'shaft', 'duct'
    ]

    return any(keyword in parent_chain_text for keyword in common_area_keywords)


def build_tasks_by_wbs(tasks: List[Dict]) -> Dict[str, Dict]:
    """Build WBS -> task mapping for quick lookup."""
    return {task["wbs"]: task for task in tasks if task.get("wbs")}


def extract_unique_activities(tasks: List[Dict], project_name: str) -> Dict:
    """
    Extract unique work activities from project tasks.

    Algorithm:
    1. Identify leaf tasks (non-summary, non-milestone, has attributes)
    2. For each leaf task:
       - Check if task name is spatial
       - If spatial: traverse to parent for actual activity name
       - Extract context from attributes and parent chain
    3. Group by activity name + context type
    4. Collect occurrence stats and sample information

    Args:
        tasks: List of task dictionaries
        project_name: Name of the project

    Returns:
        Dictionary with unique_activities list
    """
    # Build lookup
    tasks_by_wbs = build_tasks_by_wbs(tasks)

    # Extract activities from leaf tasks
    activity_extractions = []

    for task in tasks:
        # Only process leaf tasks with attributes (parent tasks don't get enriched)
        if task.get("is_summary") or task.get("is_milestone"):
            continue

        if task.get("attributes") is None:
            continue

        task_name = task.get("name", "")
        if not task_name:
            continue

        # Determine activity name
        if is_spatial_leaf(task_name):
            activity_name, parent_chain = extract_activity_from_parent(task, tasks_by_wbs)
        else:
            activity_name = task_name
            # Still get parent chain for context
            parent_chain = []
            current_wbs = task.get("parent_wbs")
            depth = 5
            while current_wbs and depth > 0:
                parent = tasks_by_wbs.get(current_wbs)
                if parent:
                    parent_chain.append(parent.get("name", ""))
                    current_wbs = parent.get("parent_wbs")
                depth -= 1

        # Determine context type
        context_type = determine_context_type(task, parent_chain, tasks_by_wbs)

        # Get tower and floor info
        attributes = task.get("attributes", {})
        tower = attributes.get("tower")
        floor = attributes.get("floor")

        activity_extractions.append({
            "activity_name": activity_name,
            "context_type": context_type,
            "task_name": task_name,
            "parent_chain": parent_chain,
            "tower": tower,
            "floor": floor,
            "wbs": task.get("wbs"),
        })

    # Group activities
    grouped = group_activities(activity_extractions)

    return {
        "project": project_name,
        "unique_activities": list(grouped.values()),
        "total_leaf_tasks": len(activity_extractions),
        "unique_activity_count": len(grouped),
    }


def group_activities(activity_extractions: List[Dict]) -> Dict[str, Dict]:
    """
    Group extracted activities by (activity_name, context_type).

    Aggregates:
    - Occurrence count
    - Unique towers/floors
    - Sample parent chains
    - Sample task names

    Args:
        activity_extractions: List of extracted activity dictionaries

    Returns:
        Dictionary of unique activities keyed by (activity_name, context_type)
    """
    groups = defaultdict(lambda: {
        "activity_name": "",
        "context_type": "",
        "occurrence_count": 0,
        "sample_task_names": [],
        "sample_parent_chains": [],
        "towers": set(),
        "floors": set(),
    })

    for extraction in activity_extractions:
        key = (extraction["activity_name"], extraction["context_type"])

        group = groups[key]
        group["activity_name"] = extraction["activity_name"]
        group["context_type"] = extraction["context_type"]
        group["occurrence_count"] += 1

        # Collect samples (limit to 5)
        if len(group["sample_task_names"]) < 5:
            group["sample_task_names"].append(extraction["task_name"])

        if len(group["sample_parent_chains"]) < 3:
            parent_chain_str = " → ".join(extraction["parent_chain"][:3])
            if parent_chain_str and parent_chain_str not in group["sample_parent_chains"]:
                group["sample_parent_chains"].append(parent_chain_str)

        # Collect unique towers and floors
        if extraction["tower"]:
            group["towers"].add(extraction["tower"])
        if extraction["floor"]:
            group["floors"].add(extraction["floor"])

    # Convert sets to sorted lists
    for group in groups.values():
        group["towers"] = sorted(list(group["towers"])) if group["towers"] else None
        group["floors"] = sorted(list(group["floors"])) if group["floors"] else None

    return groups


def get_activity_summary(unique_activities_data: Dict) -> str:
    """
    Generate a human-readable summary of extracted activities.

    Args:
        unique_activities_data: Output from extract_unique_activities

    Returns:
        Formatted summary string
    """
    activities = unique_activities_data["unique_activities"]
    project = unique_activities_data["project"]

    summary_lines = [
        f"Project: {project}",
        f"Total leaf tasks: {unique_activities_data['total_leaf_tasks']}",
        f"Unique activities: {unique_activities_data['unique_activity_count']}",
        "",
        "Activity Breakdown by Context:",
    ]

    # Group by context
    by_context = defaultdict(list)
    for activity in activities:
        by_context[activity["context_type"]].append(activity)

    for context, acts in sorted(by_context.items()):
        summary_lines.append(f"  {context}: {len(acts)} activities")

    summary_lines.append("")
    summary_lines.append("Sample Activities:")

    # Show top 10 by occurrence
    top_activities = sorted(activities, key=lambda x: x["occurrence_count"], reverse=True)[:10]
    for i, activity in enumerate(top_activities, 1):
        summary_lines.append(
            f"  {i}. {activity['activity_name']} ({activity['context_type']}) - "
            f"{activity['occurrence_count']} occurrences"
        )

    return "\n".join(summary_lines)
