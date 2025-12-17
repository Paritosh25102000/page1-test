# Stage 3: JSON → Staging Implementation Plan

**Stage**: 03-json-to-staging
**Date**: 2025-12-16
**Spec**: [spec.md](./spec.md)

---

## 1. Summary

Implement a Python ETL module that transforms Master JSON task data into pre-aggregated staging JSON files for dashboard consumption. The module reads 13 project JSON files, computes aggregations for every filter combination, and outputs one staging file per dashboard page.

---

## 2. Technical Context

| Aspect | Decision |
|--------|----------|
| **Language** | Python 3.8+ |
| **Dependencies** | Standard library only (json, datetime, pathlib, logging) |
| **Input** | `output/json/{project}.json` (13 files) |
| **Output** | `output/staging/page1-executive-summary.json` |
| **Deployment** | Static file (copied to frontend public folder) |
| **Performance** | <2 minutes for all projects, <1GB memory |

---

## 3. Module Structure

```
etl-cco-dashboard/
├── src/
│   └── staging/                         # NEW: Stage 3 modules
│       ├── __init__.py                  # Package init
│       ├── aggregator.py                # Core orchestration
│       ├── hierarchy_builder.py         # Zone/Region/Project tree
│       ├── coc_trend_calculator.py      # COC trend series
│       ├── kpi_calculator.py            # AOP/Sprint gauges
│       ├── matrix_calculator.py         # Project achievement buckets
│       ├── time_utils.py                # Date/time helpers
│       └── validators.py                # Output validation
│
├── runner_staging.py                    # CLI entry point
│
├── schemas/
│   └── staging/
│       └── page1-executive-summary.json # Output schema
│
└── output/
    └── staging/                         # Output directory
        └── page1-executive-summary.json
```

---

## 4. Module Specifications

### 4.1 `src/staging/aggregator.py` - Core Orchestration

**Purpose**: Load Master JSON, coordinate calculators, produce staging output.

```python
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
        return [t for t in tasks if t.get("attributes", {}).get("zone") == zone]

    if key.startswith("REG_"):
        region = key[4:]
        return [t for t in tasks if t.get("attributes", {}).get("region") == region]

    if key.startswith("PROJ_"):
        project = key[5:]
        return [t for t in tasks if t.get("attributes", {}).get("project_name") == project]

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
```

---

### 4.2 `src/staging/hierarchy_builder.py` - Hierarchy Tree

**Purpose**: Extract Zone → Region → Project tree from task attributes.

```python
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
```

---

### 4.3 `src/staging/coc_trend_calculator.py` - COC Trend

**Purpose**: Calculate COC trend series for all three time modes.

```python
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
```

---

### 4.4 `src/staging/kpi_calculator.py` - KPI Gauges

**Purpose**: Calculate AOP and Sprint achievement percentages.

```python
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

    for task in tasks:
        # Only include leaf tasks with cost data
        if task.get("type") != "leaf":
            continue

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
        "actual_ytd": round(total_actual, 2),
        "plan_ytd": round(total_plan, 2)
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
        if task.get("type") != "leaf":
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
        "sprint_actual": round(sprint_actual, 2),
        "sprint_plan": round(sprint_plan, 2),
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
```

---

### 4.5 `src/staging/matrix_calculator.py` - Project Matrix

**Purpose**: Calculate project counts by achievement bucket.

```python
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
        if task.get("type") != "leaf":
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
```

---

### 4.6 `src/staging/time_utils.py` - Time Utilities

```python
"""
Time Utilities - Date/time helper functions for staging calculations
"""

from datetime import datetime, timedelta
from typing import Tuple, Optional


# Financial Year constants (Indian FY: April 1 - March 31)
FY_START = "2025-04-01"
FY_END = "2026-03-31"


def get_fy_dates() -> Tuple[str, str]:
    """Return FY start and end dates."""
    return FY_START, FY_END


def get_current_quarter_dates(
    current_date: Optional[str] = None
) -> Tuple[str, str]:
    """
    Get current calendar quarter date range.

    Quarters:
        Q1: Jan 1 - Mar 31
        Q2: Apr 1 - Jun 30
        Q3: Jul 1 - Sep 30
        Q4: Oct 1 - Dec 31
    """
    if current_date:
        today = datetime.fromisoformat(current_date)
    else:
        today = datetime.now()

    quarter = (today.month - 1) // 3
    quarter_starts = [
        (1, 1), (4, 1), (7, 1), (10, 1)
    ]
    quarter_ends = [
        (3, 31), (6, 30), (9, 30), (12, 31)
    ]

    start_month, start_day = quarter_starts[quarter]
    end_month, end_day = quarter_ends[quarter]

    start = today.replace(month=start_month, day=start_day)
    end = today.replace(month=end_month, day=end_day)

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def get_looking_glass_dates(
    current_date: Optional[str] = None
) -> Tuple[str, str]:
    """
    Get +/- 5 weeks range around current date.

    Returns:
        (start_date, end_date) as YYYY-MM-DD strings
    """
    if current_date:
        today = datetime.fromisoformat(current_date)
    else:
        today = datetime.now()

    start = today - timedelta(weeks=5)
    end = today + timedelta(weeks=5)

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def get_week_start(date_str: str) -> str:
    """
    Get Monday of the week containing the given date.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Monday's date in YYYY-MM-DD format
    """
    date = datetime.fromisoformat(date_str)
    monday = date - timedelta(days=date.weekday())
    return monday.strftime("%Y-%m-%d")


def get_month_label(date: datetime) -> str:
    """
    Get month label for display (e.g., "Apr-25").

    Args:
        date: datetime object

    Returns:
        Label like "Apr-25", "May-25"
    """
    return date.strftime("%b-%y")


def get_week_label(date: datetime, week_num: int) -> str:
    """
    Get week label for display (e.g., "Wk 14").

    Args:
        date: Week start date
        week_num: Sequential week number in series

    Returns:
        Label like "Wk 14"
    """
    return f"Wk {date.isocalendar()[1]}"
```

---

### 4.7 `runner_staging.py` - CLI Entry Point

```python
#!/usr/bin/env python3
"""
Staging ETL Runner

Generates pre-aggregated staging JSON for dashboard pages.

Usage:
    python runner_staging.py                    # Generate Page 1
    python runner_staging.py --page page1       # Explicit page
    python runner_staging.py --dry-run          # Preview without saving
    python runner_staging.py --validate-only    # Validate existing output
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

from src.staging.aggregator import generate_staging_data
from src.staging.validators import validate_staging_output


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    parser = argparse.ArgumentParser(
        description='Generate staging JSON for dashboard'
    )

    parser.add_argument(
        '--page',
        default='page1',
        help='Dashboard page to generate (default: page1)'
    )
    parser.add_argument(
        '--input-dir',
        default='output/json',
        help='Directory containing Master JSON files'
    )
    parser.add_argument(
        '--output-dir',
        default='output/staging',
        help='Directory for staging output'
    )
    parser.add_argument(
        '--current-date',
        help='Override current date (YYYY-MM-DD) for testing'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate but do not save output'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Validate existing output without regenerating'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Output file mapping
    page_files = {
        'page1': 'page1-executive-summary.json'
    }

    output_file = page_files.get(args.page)
    if not output_file:
        logger.error(f"Unknown page: {args.page}")
        return 1

    output_path = Path(args.output_dir) / output_file

    # Validate-only mode
    if args.validate_only:
        logger.info(f"Validating existing output: {output_path}")
        with open(output_path, 'r') as f:
            data = json.load(f)
        errors = validate_staging_output(data, args.page)
        if errors:
            logger.error(f"Validation errors: {errors}")
            return 1
        logger.info("Validation passed")
        return 0

    # Generate staging data
    logger.info(f"Generating staging data for {args.page}")
    start_time = datetime.now()

    data = generate_staging_data(
        json_dir=args.input_dir,
        page=args.page,
        current_date=args.current_date
    )

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"Generated in {elapsed:.1f} seconds")

    # Summary
    filter_count = len(data.get('dashboard_data', {}))
    logger.info(f"Filter keys generated: {filter_count}")

    # Save output
    if not args.dry_run:
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved to: {output_path}")

        # File size
        size_mb = output_path.stat().st_size / (1024 * 1024)
        logger.info(f"File size: {size_mb:.2f} MB")
    else:
        logger.info("Dry run - output not saved")

    return 0


if __name__ == '__main__':
    exit(main())
```

---

## 5. Implementation Phases

### Phase 1: Core Infrastructure (Day 1)
- [ ] Create `src/staging/` package structure
- [ ] Implement `time_utils.py`
- [ ] Implement `hierarchy_builder.py`
- [ ] Write unit tests for time utilities

### Phase 2: Calculators (Day 2-3)
- [ ] Implement `coc_trend_calculator.py`
- [ ] Implement `kpi_calculator.py`
- [ ] Implement `matrix_calculator.py`
- [ ] Write unit tests for each calculator

### Phase 3: Integration (Day 3-4)
- [ ] Implement `aggregator.py`
- [ ] Implement `validators.py`
- [ ] Create `runner_staging.py`
- [ ] Integration test with Miraya.json

### Phase 4: Testing & Validation (Day 4-5)
- [ ] Test with all 13 projects
- [ ] Validate output against schema
- [ ] Performance testing (<2 min target)
- [ ] Memory profiling (<1GB target)

---

## 6. Success Criteria

| Metric | Target |
|--------|--------|
| All 13 projects processed | Yes |
| Output validates against schema | 100% |
| All filter keys present | ~50 keys |
| Processing time | <2 minutes |
| Memory usage | <1 GB |
| Output file size | <5 MB |
| Zero runtime errors | Yes |
