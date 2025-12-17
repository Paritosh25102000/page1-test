# Stage 3: JSON → Staging Data Model

**Stage**: 03-json-to-staging
**Date**: 2025-12-16
**Source Schema**: `schemas/page-1-executive-simmary/page1-executive-summary_schema.json`

---

## 1. Entity Relationship Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       StagingData                                │
├─────────────────────────────────────────────────────────────────┤
│  meta: Meta                                                      │
│  controls: Controls                                              │
│  dashboard_data: Record<FilterKey, NodeData>                     │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│      Meta       │  │    Controls     │  │    NodeData     │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ generated_at    │  │ hierarchy_tree  │  │ kpi_gauges      │
│ data_version    │  │ time_modes      │  │ coc_trend       │
│ currency_unit   │  │                 │  │ project_matrix  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │                    │
                     ┌────────┴────────┐    ┌──────┴──────┐
                     ▼                 ▼    ▼             ▼
              ┌───────────┐     ┌───────────┐  ┌───────────────┐
              │ Hierarchy │     │ TimeModes │  │   KPIGauges   │
              │   Tree    │     │           │  ├───────────────┤
              └───────────┘     └───────────┘  │ aop: Gauge    │
                                               │ sprint: Gauge │
                                               └───────────────┘
```

---

## 2. Input Entity: Task (from Master JSON)

### Task (Source)

The Stage 3 input is the Master JSON task from Stage 1.

| Field | Type | Used In | Purpose |
|-------|------|---------|---------|
| `uid` | integer | - | Not used in staging |
| `type` | "parent" \| "leaf" \| "milestone" | All | Filter to leaf only |
| `attributes.zone` | string | Hierarchy, Filter | Zone grouping |
| `attributes.region` | string | Hierarchy, Filter | Region grouping |
| `attributes.project_name` | string | Hierarchy, Filter, Matrix | Project grouping |
| `cost_timeline.weekly_costs` | array | COC Trend | Weekly cost aggregation |
| `cost_timeline.summary.plan_cost_in_fy` | number | KPI, Matrix | Plan cost YTD |
| `cost_timeline.summary.actual_cost_in_fy` | number | KPI, Matrix | Actual cost YTD |
| `dates.sprint.start` | string | Sprint Gauge | Sprint filter |

---

## 3. Output Entities

### 3.1 StagingData (Root)

The root output object for a staging file.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `meta` | Meta | Yes | ETL run metadata |
| `controls` | Controls | Yes | UI filter configuration |
| `dashboard_data` | Record<FilterKey, NodeData> | Yes | Pre-aggregated data per filter |

### 3.2 Meta

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `generated_at` | string (ISO 8601) | Yes | Timestamp of ETL run |
| `data_version` | string | No | Schema version (default: "1.0") |
| `currency_unit` | string | No | Currency code (default: "INR") |
| `page` | string | No | Page identifier |

**Example**:
```json
{
  "generated_at": "2025-12-16T10:30:00.000Z",
  "data_version": "1.0",
  "currency_unit": "INR",
  "page": "page1"
}
```

### 3.3 Controls

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `hierarchy_tree` | HierarchyTree | Yes | Zone → Region → Project tree |
| `time_modes` | TimeModes | Yes | FY, Quarter, Month configurations |

### 3.4 HierarchyTree

Nested structure for cascading dropdowns.

**Type**: `Record<ZoneId, Record<RegionId, Project[]>>`

**Example**:
```json
{
  "MZ": {
    "MZ1": [
      {"id": "Horizon", "name": "Horizon"},
      {"id": "Reserve", "name": "Reserve"},
      {"id": "Avenue 11", "name": "Avenue 11"}
    ]
  },
  "NZ": {
    "NZ1": [
      {"id": "Miraya", "name": "Miraya"},
      {"id": "Aristocrat", "name": "Aristocrat"},
      {"id": "Zenith", "name": "Zenith"}
    ],
    "NZ2": [
      {"id": "Tropical Isle", "name": "Tropical Isle"},
      {"id": "Jardinia", "name": "Jardinia"},
      {"id": "Sec. 44, Noida", "name": "Sec. 44, Noida"}
    ]
  },
  "SZ": {
    "SZ1": [
      {"id": "Woodscapes", "name": "Woodscapes"},
      {"id": "RGA 2", "name": "RGA 2"}
    ],
    "SZ2": [
      {"id": "Ramaiah", "name": "Ramaiah"}
    ]
  },
  "WEZ": {
    "Kolkata": [
      {"id": "BL Saha", "name": "BL Saha"}
    ]
  }
}
```

### 3.5 Project

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique project identifier (for filter keys) |
| `name` | string | Yes | Display name |

### 3.6 TimeModes

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fy` | TimeMode | Yes | Financial Year configuration |
| `quarter` | TimeMode | Yes | Current Quarter configuration |
| `month` | TimeMode | Yes | Looking Glass configuration |

### 3.7 TimeMode

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | Display label |
| `start` | string (date) | Yes | Period start (YYYY-MM-DD) |
| `end` | string (date) | Yes | Period end (YYYY-MM-DD) |
| `resolution` | "month" \| "week" | Yes | Data granularity |

**Example**:
```json
{
  "fy": {
    "label": "Financial Year",
    "start": "2025-04-01",
    "end": "2026-03-31",
    "resolution": "month"
  },
  "quarter": {
    "label": "Current Quarter",
    "start": "2025-10-01",
    "end": "2025-12-31",
    "resolution": "week"
  },
  "month": {
    "label": "Looking Glass (+/- 5 Wks)",
    "start": "2025-11-11",
    "end": "2026-01-20",
    "resolution": "week"
  }
}
```

---

## 4. Filter Keys

### 4.1 FilterKey (Union Type)

Pattern for `dashboard_data` keys:

| Pattern | Example | Description | Count |
|---------|---------|-------------|-------|
| `"ALL"` | `"ALL"` | Global aggregate | 1 |
| `"ZONE_{id}"` | `"ZONE_MZ"` | Zone aggregate | 4 |
| `"REG_{id}"` | `"REG_MZ1"` | Region aggregate | 7 |
| `"PROJ_{id}"` | `"PROJ_Horizon"` | Project data | 13 |

**Total Filter Keys**: 25 (1 + 4 + 7 + 13)

### 4.2 Key Construction Logic

```python
def construct_filter_key(zone: str = None, region: str = None, project: str = None) -> str:
    """
    Construct filter key from selection.

    Priority: project > region > zone > ALL
    """
    if project:
        return f"PROJ_{project}"
    if region:
        return f"REG_{region}"
    if zone:
        return f"ZONE_{zone}"
    return "ALL"
```

### 4.3 Zone/Region Mapping Helper

The following mapping defines the organizational hierarchy used for filter construction and hierarchy tree generation:

```python
ZONE_REGION_MAP = {
    "MZ": {
        "name": "MZ",
        "regions": {
            "MZ1": {
                "name": "MZ1",
                "projects": ["Horizon", "Reserve", "Avenue 11"]
            }
        }
    },
    "NZ": {
        "name": "NZ",
        "regions": {
            "NZ1": {
                "name": "NZ1",
                "projects": ["Miraya", "Aristocrat", "Zenith"]
            },
            "NZ2": {
                "name": "NZ2",
                "projects": ["Tropical Isle", "Jardinia", "Sec. 44, Noida"]
            }
        }
    },
    "SZ": {
        "name": "SZ",
        "regions": {
            "SZ1": {
                "name": "SZ1",
                "projects": ["Woodscapes", "RGA 2"]
            },
            "SZ2": {
                "name": "SZ2",
                "projects": ["Ramaiah"]
            }
        }
    },
    "WEZ": {
        "name": "WEZ",
        "regions": {
            "Kolkata": {
                "name": "Kolkata",
                "projects": ["BL Saha"]
            }
        }
    }
}
```

**Helper Functions**:

```python
def get_zone_for_project(project_name: str) -> str:
    """Get zone ID for a project."""
    for zone_id, zone_data in ZONE_REGION_MAP.items():
        for region_data in zone_data["regions"].values():
            if project_name in region_data["projects"]:
                return zone_id
    raise ValueError(f"Project not found: {project_name}")

def get_region_for_project(project_name: str) -> str:
    """Get region ID for a project."""
    for zone_data in ZONE_REGION_MAP.values():
        for region_id, region_data in zone_data["regions"].items():
            if project_name in region_data["projects"]:
                return region_id
    raise ValueError(f"Project not found: {project_name}")

def get_projects_for_region(region_id: str) -> list[str]:
    """Get all projects in a region."""
    for zone_data in ZONE_REGION_MAP.values():
        if region_id in zone_data["regions"]:
            return zone_data["regions"][region_id]["projects"]
    raise ValueError(f"Region not found: {region_id}")

def get_projects_for_zone(zone_id: str) -> list[str]:
    """Get all projects in a zone."""
    if zone_id not in ZONE_REGION_MAP:
        raise ValueError(f"Zone not found: {zone_id}")

    projects = []
    for region_data in ZONE_REGION_MAP[zone_id]["regions"].values():
        projects.extend(region_data["projects"])
    return projects
```

---

## 5. NodeData (Per-Filter Data)

Each filter key maps to a NodeData object containing widget data.

### 5.1 NodeData

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kpi_gauges` | KPIGauges | Yes | AOP and Sprint gauge data |
| `coc_trend` | COCTrend | Yes | Cost trend series |
| `project_matrix` | ProjectMatrix | Yes | Project achievement distribution |

### 5.2 KPIGauges

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `aop` | GaugeData | Yes | AOP Achievement gauge |
| `sprint` | GaugeData | Yes | Sprint Achievement gauge |

### 5.3 GaugeData

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `achieved_pct` | number | Yes | Achievement percentage (0-200+) |
| `status_color` | "red" \| "amber" \| "green" | Yes | Pre-calculated threshold color |
| `actual_ytd` | number | No | Actual cost year-to-date |
| `plan_ytd` | number | No | Planned cost year-to-date |
| `sprint_actual` | number | No | Sprint actual cost (sprint gauge only) |
| `sprint_plan` | number | No | Sprint plan cost (sprint gauge only) |

**Color Thresholds**:
- Red: < 85%
- Amber: 85% - 95%
- Green: > 95%

**Example**:
```json
{
  "aop": {
    "achieved_pct": 87.5,
    "status_color": "amber",
    "actual_ytd": 125000000.00,
    "plan_ytd": 142857142.86
  },
  "sprint": {
    "achieved_pct": 92.3,
    "status_color": "amber",
    "sprint_actual": 98000000.00,
    "sprint_plan": 106175000.00
  }
}
```

### 5.4 COCTrend

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fy_series` | TrendPoint[] | Yes | Monthly data for FY view |
| `quarter_series` | TrendPoint[] | Yes | Weekly data for Quarter view |
| `month_series` | TrendPoint[] | Yes | Weekly data for Looking Glass |

### 5.5 TrendPoint

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | X-axis label (e.g., "Apr-25", "Wk 14") |
| `sort_date` | string (date) | Yes | ISO date for sorting |
| `plan_cost` | number \| null | Yes | Periodic plan cost (bar) |
| `actual_cost` | number \| null | Yes | Periodic actual cost (bar) |
| `cumm_plan` | number \| null | No | Cumulative plan cost (line) |
| `cumm_actual` | number \| null | No | Cumulative actual cost (line) |

**Example (FY Series)**:
```json
[
  {
    "label": "Apr-25",
    "sort_date": "2025-04-01",
    "plan_cost": 12500000,
    "actual_cost": 11800000,
    "cumm_plan": 12500000,
    "cumm_actual": 11800000
  },
  {
    "label": "May-25",
    "sort_date": "2025-05-01",
    "plan_cost": 14200000,
    "actual_cost": 13900000,
    "cumm_plan": 26700000,
    "cumm_actual": 25700000
  }
]
```

### 5.6 ProjectMatrix

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rows` | MatrixRow[] | Yes | Rows for heatmap table |

### 5.7 MatrixRow

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | Row header (Zone/Region name) |
| `id` | string | No | Filter key for drill-down |
| `buckets` | Buckets | Yes | Project counts per achievement range |
| `achievement_pct` | number | No | Individual project achievement (project rows only) |

### 5.8 Buckets

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `gt_120` | integer | Yes | Projects > 120% |
| `100_120` | integer | Yes | Projects 100-120% |
| `85_100` | integer | Yes | Projects 85-100% |
| `60_85` | integer | Yes | Projects 60-85% |
| `lt_60` | integer | Yes | Projects < 60% |

**Example**:
```json
{
  "rows": [
    {
      "label": "MZ",
      "id": "ZONE_MZ",
      "buckets": {
        "gt_120": 0,
        "100_120": 1,
        "85_100": 1,
        "60_85": 1,
        "lt_60": 0
      }
    },
    {
      "label": "NZ",
      "id": "ZONE_NZ",
      "buckets": {
        "gt_120": 1,
        "100_120": 2,
        "85_100": 2,
        "60_85": 1,
        "lt_60": 0
      }
    }
  ]
}
```

---

## 6. Aggregation Rules

### 6.1 COC Trend Aggregation

**Weekly Aggregation**:
```
For each task:
  For each week in task.cost_timeline.weekly_costs:
    weekly_totals[week_start].plan += week.plan.cost
    weekly_totals[week_start].actual += week.actual.cost
```

**Monthly Aggregation (FY Series)**:
```
For each week in weekly_totals:
  month = week_start.month
  monthly_totals[month].plan += week.plan
  monthly_totals[month].actual += week.actual
```

**Cumulative Calculation**:
```
cumm_plan = 0
cumm_actual = 0
For each period (sorted by date):
  cumm_plan += period.plan
  cumm_actual += period.actual
  period.cumm_plan = cumm_plan
  period.cumm_actual = cumm_actual
```

### 6.2 KPI Gauge Aggregation

**AOP Achievement**:
```
total_plan = sum(task.cost_timeline.summary.plan_cost_in_fy for all leaf tasks)
total_actual = sum(task.cost_timeline.summary.actual_cost_in_fy for all leaf tasks)
aop_pct = (total_actual / total_plan) * 100
```

**Sprint Achievement**:
```
sprint_tasks = [t for t in tasks if t.dates.sprint.start is not null]
sprint_plan = sum(task.cost_timeline.summary.plan_cost_in_fy for sprint_tasks)
sprint_actual = sum(task.cost_timeline.summary.actual_cost_in_fy for sprint_tasks)
sprint_pct = (sprint_actual / sprint_plan) * 100
```

### 6.3 Matrix Aggregation

**Per-Project Achievement**:
```
For each project:
  project_plan = sum(task.cost_timeline.summary.plan_cost_in_fy
                     where task.attributes.project_name == project)
  project_actual = sum(task.cost_timeline.summary.actual_cost_in_fy
                       where task.attributes.project_name == project)
  project_pct = (project_actual / project_plan) * 100
```

**Bucket Assignment**:
```
if pct > 120: bucket = "gt_120"
elif pct >= 100: bucket = "100_120"
elif pct >= 85: bucket = "85_100"
elif pct >= 60: bucket = "60_85"
else: bucket = "lt_60"
```

---

## 7. Validation Rules

### 7.1 Structural Validation

1. `dashboard_data` must contain key `"ALL"`
2. All zone keys in `hierarchy_tree` must have corresponding `ZONE_*` keys
3. All region keys must have corresponding `REG_*` keys
4. All project ids must have corresponding `PROJ_*` keys

### 7.2 Data Validation

1. `achieved_pct` must be non-negative
2. `status_color` must match threshold calculation
3. Bucket counts must be non-negative integers
4. Trend series must be sorted by `sort_date`
5. Cumulative values must be monotonically increasing (for positive costs)

### 7.3 Completeness Validation

1. Each `NodeData` must have all three widgets
2. `coc_trend` must have all three series
3. `kpi_gauges` must have both `aop` and `sprint`
4. `project_matrix` must have at least one row (except for project-level filters)

---

## 8. Sample Data

### Complete NodeData Example

```json
{
  "ALL": {
    "kpi_gauges": {
      "aop": {
        "achieved_pct": 87.5,
        "status_color": "amber",
        "actual_ytd": 125000000,
        "plan_ytd": 142857142.86
      },
      "sprint": {
        "achieved_pct": 92.3,
        "status_color": "amber",
        "sprint_actual": 98000000,
        "sprint_plan": 106175000
      }
    },
    "coc_trend": {
      "fy_series": [
        {"label": "Apr-25", "sort_date": "2025-04-01", "plan_cost": 12500000, "actual_cost": 11800000, "cumm_plan": 12500000, "cumm_actual": 11800000},
        {"label": "May-25", "sort_date": "2025-05-01", "plan_cost": 14200000, "actual_cost": 13900000, "cumm_plan": 26700000, "cumm_actual": 25700000}
      ],
      "quarter_series": [
        {"label": "Wk 40", "sort_date": "2025-10-06", "plan_cost": 3100000, "actual_cost": 2900000, "cumm_plan": 3100000, "cumm_actual": 2900000}
      ],
      "month_series": [
        {"label": "Wk 50", "sort_date": "2025-12-08", "plan_cost": 2800000, "actual_cost": 2600000, "cumm_plan": 2800000, "cumm_actual": 2600000}
      ]
    },
    "project_matrix": {
      "rows": [
        {"label": "MZ", "id": "ZONE_MZ", "buckets": {"gt_120": 0, "100_120": 1, "85_100": 1, "60_85": 1, "lt_60": 0}},
        {"label": "NZ", "id": "ZONE_NZ", "buckets": {"gt_120": 1, "100_120": 2, "85_100": 2, "60_85": 1, "lt_60": 0}},
        {"label": "SZ", "id": "ZONE_SZ", "buckets": {"gt_120": 0, "100_120": 1, "85_100": 1, "60_85": 0, "lt_60": 0}},
        {"label": "WEZ", "id": "ZONE_WEZ", "buckets": {"gt_120": 0, "100_120": 0, "85_100": 1, "60_85": 0, "lt_60": 0}}
      ]
    }
  }
}
```
