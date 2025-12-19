"""
Matrix Calculator - Project achievement bucket distribution
"""

from typing import Dict, List
from collections import defaultdict


def calculate_project_matrix(
    tasks: List[Dict],
    hierarchy: Dict,
    filter_key: str
) -> Dict:
    """
    Calculate project achievement matrix.

    Args:
        tasks: Filtered tasks
        hierarchy: Full hierarchy tree
        filter_key: Current filter (determines row granularity)

    Returns:
        {
            "rows": [
                {"label": "MZ", "id": "ZONE_MZ", "buckets": {...}},
                {"label": "NZ", "id": "ZONE_NZ", "buckets": {...}}
            ]
        }
    """
    # Calculate per-project achievement
    project_achievements = calculate_project_achievements(tasks)

    # Determine row granularity based on filter
    if filter_key == "ALL":
        # Show Zone-level rows
        rows = generate_zone_rows(project_achievements, hierarchy)
    elif filter_key.startswith("ZONE_"):
        # Show Region-level rows for this zone
        zone = filter_key[5:]
        rows = generate_region_rows(project_achievements, hierarchy, zone)
    else:
        # For region/project level, show the projects directly
        rows = generate_project_rows(project_achievements, tasks)

    return {"rows": rows}


def calculate_project_achievements(tasks: List[Dict]) -> Dict[str, float]:
    """
    Calculate achievement percentage per project.

    Returns:
        {"Horizon": 87.5, "Miraya": 92.3, ...}
    """
    project_costs = defaultdict(lambda: {"plan": 0.0, "actual": 0.0})

    for task in tasks:
        if task.get("is_summary") or task.get("is_milestone"):
            continue

        project = task.get("attributes", {}).get("project_name")
        if not project:
            continue

        timeline = task.get("cost_timeline") or {}
        summary = timeline.get("summary") or {}

        plan = summary.get("plan_cost_in_fy") or 0.0
        actual = summary.get("actual_cost_in_fy") or 0.0

        project_costs[project]["plan"] += plan
        project_costs[project]["actual"] += actual

    # Calculate percentages
    achievements = {}
    for project, costs in project_costs.items():
        if costs["plan"] > 0:
            achievements[project] = (costs["actual"] / costs["plan"]) * 100
        else:
            achievements[project] = 0.0

    return achievements


def bucket_achievement(percentage: float) -> str:
    """
    Assign achievement percentage to bucket.

    Buckets:
        - gt_120: > 120%
        - 100_120: 100% - 120%
        - 85_100: 85% - 100%
        - 60_85: 60% - 85%
        - lt_60: < 60%
    """
    if percentage > 120:
        return "gt_120"
    elif percentage >= 100:
        return "100_120"
    elif percentage >= 85:
        return "85_100"
    elif percentage >= 60:
        return "60_85"
    else:
        return "lt_60"


def empty_buckets() -> Dict[str, int]:
    """Return empty bucket counts."""
    return {
        "gt_120": 0,
        "100_120": 0,
        "85_100": 0,
        "60_85": 0,
        "lt_60": 0
    }


def generate_zone_rows(
    project_achievements: Dict[str, float],
    hierarchy: Dict
) -> List[Dict]:
    """Generate rows for each zone."""
    rows = []

    for zone in sorted(hierarchy.keys()):
        buckets = empty_buckets()

        # Count projects in this zone
        for region, projects in hierarchy[zone].items():
            for project in projects:
                project_id = project["id"]
                if project_id in project_achievements:
                    bucket = bucket_achievement(project_achievements[project_id])
                    buckets[bucket] += 1

        rows.append({
            "label": zone,
            "id": f"ZONE_{zone}",
            "buckets": buckets
        })

    return rows


def generate_region_rows(
    project_achievements: Dict[str, float],
    hierarchy: Dict,
    zone: str
) -> List[Dict]:
    """Generate rows for each region in a zone."""
    rows = []

    regions = hierarchy.get(zone, {})
    for region in sorted(regions.keys()):
        buckets = empty_buckets()

        for project in regions[region]:
            project_id = project["id"]
            if project_id in project_achievements:
                bucket = bucket_achievement(project_achievements[project_id])
                buckets[bucket] += 1

        rows.append({
            "label": region,
            "id": f"REG_{region}",
            "buckets": buckets
        })

    return rows


def generate_project_rows(
    project_achievements: Dict[str, float],
    tasks: List[Dict]
) -> List[Dict]:
    """Generate rows for each project (at region/project filter level)."""
    # Get unique projects from tasks
    projects = set()
    for task in tasks:
        project = task.get("attributes", {}).get("project_name")
        if project:
            projects.add(project)

    rows = []
    for project in sorted(projects):
        achievement = project_achievements.get(project, 0.0)
        bucket = bucket_achievement(achievement)

        buckets = empty_buckets()
        buckets[bucket] = 1  # Single project

        rows.append({
            "label": project,
            "id": f"PROJ_{project}",
            "buckets": buckets,
            "achievement_pct": round(achievement, 1)
        })

    return rows
