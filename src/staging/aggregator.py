"""
Staging Aggregator - Core orchestration for Stage 3 ETL

Coordinates the transformation of Master JSON into pre-aggregated
staging data for dashboard consumption.
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
import logging

from .hierarchy_builder import build_hierarchy_tree
from .coc_trend_calculator import calculate_coc_trend
from .kpi_calculator import calculate_kpi_gauges
from .matrix_calculator import calculate_project_matrix
from .validators import validate_staging_output


def generate_staging_data(
    json_dir: str,
    page: str = "page1",
    current_date: Optional[str] = None
) -> Dict:
    """
    Generate pre-aggregated staging data for a dashboard page.

    Args:
        json_dir: Directory containing Master JSON files
        page: Dashboard page identifier (e.g., "page1")
        current_date: Override for "today" (testing), format YYYY-MM-DD

    Returns:
        Complete staging data structure

    Example:
        data = generate_staging_data("output/json", page="page1")
        save_json(data, "output/staging/page1-executive-summary.json")
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Generating staging data for {page}")

    # 1. Load all project tasks
    all_tasks = load_all_projects(json_dir)
    logger.info(f"Loaded {len(all_tasks)} total tasks")

    # 2. Build hierarchy tree
    hierarchy = build_hierarchy_tree(all_tasks)

    # 3. Generate filter keys
    filter_keys = generate_filter_keys(hierarchy)
    logger.info(f"Generated {len(filter_keys)} filter keys")

    # 4. Calculate data for each filter key
    dashboard_data = {}
    for key in filter_keys:
        filtered_tasks = filter_tasks(all_tasks, key)

        dashboard_data[key] = {
            "kpi_gauges": calculate_kpi_gauges(filtered_tasks, current_date),
            "coc_trend": calculate_coc_trend(filtered_tasks, current_date),
            "project_matrix": calculate_project_matrix(
                filtered_tasks,
                hierarchy,
                key
            )
        }
        logger.debug(f"Calculated data for {key}")

    # 5. Assemble output
    staging_data = {
        "meta": build_meta(page),
        "controls": {
            "hierarchy_tree": hierarchy,
            "time_modes": build_time_modes(current_date)
        },
        "dashboard_data": dashboard_data
    }

    # 6. Validate
    errors = validate_staging_output(staging_data, page)
    if errors:
        logger.warning(f"Validation warnings: {errors}")

    return staging_data


def load_all_projects(json_dir: str) -> List[Dict]:
    """Load and merge all project JSON files."""
    all_tasks = []
    json_path = Path(json_dir)

    for json_file in sorted(json_path.glob("*.json")):
        with open(json_file, 'r') as f:
            tasks = json.load(f)
            all_tasks.extend(tasks)

    return all_tasks


def generate_filter_keys(hierarchy: Dict) -> List[str]:
    """
    Generate all filter key combinations.

    Returns:
        ["ALL", "ZONE_MZ", "ZONE_NZ", ..., "REG_MZ1", ..., "PROJ_Horizon", ...]
    """
    keys = ["ALL"]

    for zone_id, regions in hierarchy.items():
        keys.append(f"ZONE_{zone_id}")

        for region_id, projects in regions.items():
            keys.append(f"REG_{region_id}")

            for project in projects:
                keys.append(f"PROJ_{project['id']}")

    return keys


def filter_tasks(tasks: List[Dict], key: str) -> List[Dict]:
    """
    Filter tasks based on filter key.

    Args:
        tasks: All tasks
        key: Filter key like "ALL", "ZONE_MZ", "REG_MZ1", "PROJ_Horizon"

    Returns:
        Filtered task list
    """
    if key == "ALL":
        return tasks

    if key.startswith("ZONE_"):
        zone = key[5:]
        return [t for t in tasks if (t.get("attributes") or {}).get("zone") == zone]

    if key.startswith("REG_"):
        region = key[4:]
        return [t for t in tasks if (t.get("attributes") or {}).get("region") == region]

    if key.startswith("PROJ_"):
        project = key[5:]
        return [t for t in tasks if (t.get("attributes") or {}).get("project_name") == project]

    return tasks


def build_meta(page: str) -> Dict:
    """Build metadata object."""
    from datetime import datetime

    return {
        "generated_at": datetime.now().isoformat(),
        "data_version": "1.0",
        "currency_unit": "INR",
        "page": page
    }


def build_time_modes(current_date: Optional[str] = None) -> Dict:
    """Build time mode configurations."""
    from .time_utils import (
        get_fy_dates,
        get_current_quarter_dates,
        get_looking_glass_dates
    )

    fy_start, fy_end = get_fy_dates()
    q_start, q_end = get_current_quarter_dates(current_date)
    lg_start, lg_end = get_looking_glass_dates(current_date)

    return {
        "fy": {
            "label": "Financial Year",
            "start": fy_start,
            "end": fy_end,
            "resolution": "month"
        },
        "quarter": {
            "label": "Current Quarter",
            "start": q_start,
            "end": q_end,
            "resolution": "week"
        },
        "month": {
            "label": "Looking Glass (+/- 5 Wks)",
            "start": lg_start,
            "end": lg_end,
            "resolution": "week"
        }
    }
