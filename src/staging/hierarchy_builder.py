"""
Hierarchy Builder - Extract organizational tree from task data
"""

from typing import Dict, List
from collections import defaultdict


def build_hierarchy_tree(tasks: List[Dict]) -> Dict[str, Dict[str, List[Dict]]]:
    """
    Build Zone -> Region -> Project hierarchy from tasks.

    Args:
        tasks: All tasks from Master JSON

    Returns:
        Nested dictionary:
        {
            "MZ": {
                "MZ1": [{"id": "Horizon", "name": "Horizon"}, ...]
            },
            "NZ": {...}
        }

    Note:
        Projects are deduplicated by id within each region.
    """
    hierarchy = defaultdict(lambda: defaultdict(dict))

    for task in tasks:
        attrs = task.get("attributes") or {}
        zone = attrs.get("zone")
        region = attrs.get("region")
        project_name = attrs.get("project_name")

        if zone and region and project_name:
            # Use project_name as both id and name
            hierarchy[zone][region][project_name] = {
                "id": project_name,
                "name": project_name
            }

    # Convert to regular dicts and project dicts to lists
    result = {}
    for zone, regions in sorted(hierarchy.items()):
        result[zone] = {}
        for region, projects in sorted(regions.items()):
            result[zone][region] = sorted(
                projects.values(),
                key=lambda p: p["name"]
            )

    return result


def get_all_zones(hierarchy: Dict) -> List[str]:
    """Get list of all zone IDs."""
    return list(hierarchy.keys())


def get_regions_for_zone(hierarchy: Dict, zone: str) -> List[str]:
    """Get list of region IDs for a zone."""
    return list(hierarchy.get(zone, {}).keys())


def get_projects_for_region(hierarchy: Dict, zone: str, region: str) -> List[Dict]:
    """Get list of projects for a region."""
    return hierarchy.get(zone, {}).get(region, [])
