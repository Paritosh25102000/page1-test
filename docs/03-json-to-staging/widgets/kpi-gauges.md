# Widget Specification: KPI Gauges (AOP & Sprint)

**Widget ID**: PG1-WIDGET-03
**Dashboard Page**: Page 1 (Executive Summary)
**Element Type**: Semi-Circle Gauge
**Last Updated**: 2025-12-17

---

## 1. Business Context

### Purpose
Compare long-term stability (AOP) against short-term acceleration/bonus targets (Sprint).

### Key Questions Answered
- **AOP Gauge**: "Are we on track for the year?"
- **Sprint Gauge**: "Are we meeting the accelerated 'Squeezed AOP' targets?"

### Target Action
- High Sprint + Low AOP = Recovery is working
- Low Sprint = Immediate intervention needed
- Both Green = On track

### Interaction with Controls

Both gauges respond to **TWO independent controls simultaneously**:

1. **Global Filter** (Zone/Region/Project dropdown): Determines which tasks to aggregate
2. **Time Toggle** (FY/Quarter/Month): Determines the date range for cost calculation

**Matrix Distribution**: All combinations are pre-computed:

```
                    │   FY    │ Quarter │  Month  │
────────────────────┼─────────┼─────────┼─────────┤
ALL                 │ AOP+Spr │ AOP+Spr │ AOP+Spr │
ZONE_MZ             │ AOP+Spr │ AOP+Spr │ AOP+Spr │
ZONE_NZ             │ AOP+Spr │ AOP+Spr │ AOP+Spr │
REG_MZ1             │ AOP+Spr │ AOP+Spr │ AOP+Spr │
PROJ_Horizon        │ AOP+Spr │ AOP+Spr │ AOP+Spr │
... (~50 keys)      │   ...   │   ...   │   ...   │
────────────────────┴─────────┴─────────┴─────────┘

Total: ~50 filter keys × 3 time modes × 2 gauges = ~300 pre-computed values
```

---

## 2. Input Data

### Source Fields (from Master JSON)

```python
task = {
    "type": "leaf",  # Only leaf tasks contribute
    "cost_plan_total": 125000.00,  # Total task cost
    "cost_timeline": {
        "weekly_costs": [
            # Weekly cost distribution based on AOP plan dates
            {"week_start": "2025-04-07", "plan": {"cost": 5000}, "actual": {"cost": 4500}}
        ],
        "summary": {
            "plan_cost_in_fy": 125000.00,   # Plan cost for FY
            "actual_cost_in_fy": 108750.00  # Actual cost YTD
        }
    },
    "dates": {
        "plan": {
            "start": "2025-04-01",
            "end": "2025-06-30",
            "duration_days": 90
        },
        "sprint": {
            "start": "2025-04-15",  # Sprint start (null if no sprint)
            "finish": "2025-06-15",  # Note: Sprint uses 'finish', not 'end'
            "duration_days": 61
        }
    },
    "progress": {
        "percent_complete": 45,
        "is_complete": false
    },
    "attributes": {
        "zone": "MZ",
        "region": "MZ1",
        "project_name": "Horizon"
    }
}
```

### Filtering Rules

1. **Task Type**: Only `type == "leaf"` (work tasks)
2. **Filter Scope**: Apply zone/region/project filter
3. **AOP**: All leaf tasks with cost_timeline
4. **Sprint**: Only tasks where `dates.sprint.start` is not null

### Important Data Consideration

> **Sprint Date Mismatch**: Sprint schedules are RE-PLANNED timelines, not just compressed AOP. Sprint dates may be months or years different from AOP dates. The `weekly_costs` are distributed based on AOP dates, NOT Sprint dates.
>
> See `test/sprint-achievement-data-analysis.md` for detailed analysis.

---

## 3. Transformation Logic

### 3.1 AOP Gauge Calculation (Time-Mode Aware)

```python
def calculate_aop_gauge(tasks: List[Dict], time_mode: str, current_date: str) -> Dict:
    """
    AOP Achievement = (Total Actual / Total Plan) * 100

    Args:
        tasks: Filtered tasks (by zone/region/project)
        time_mode: "fy", "quarter", or "month"
        current_date: Reference date for calculations

    Time Mode Behavior:
        - FY: Use cost_timeline.summary totals (full year)
        - Quarter: Sum weekly_costs within current quarter
        - Month: Sum weekly_costs within +/- 5 weeks
    """
    time_start, time_end = get_time_boundaries(time_mode, current_date)

    total_plan = 0.0
    total_actual = 0.0

    for task in tasks:
        if task.get("type") != "leaf":
            continue

        timeline = task.get("cost_timeline") or {}

        if time_mode == "fy":
            # Use pre-calculated summary for FY
            summary = timeline.get("summary") or {}
            total_plan += summary.get("plan_cost_in_fy") or 0.0
            total_actual += summary.get("actual_cost_in_fy") or 0.0
        else:
            # Sum weekly costs within time window
            for week in timeline.get("weekly_costs") or []:
                week_start = week.get("week_start")
                if time_start <= week_start <= time_end:
                    total_plan += week.get("plan", {}).get("cost") or 0.0
                    total_actual += week.get("actual", {}).get("cost") or 0.0

    achieved_pct = (total_actual / total_plan * 100) if total_plan > 0 else 0.0

    return {
        "achieved_pct": round(achieved_pct, 1),
        "status_color": get_status_color(achieved_pct),
        "actual": round(total_actual, 2),
        "plan": round(total_plan, 2)
    }
```

### 3.2 Sprint Gauge Calculation (Time-Mode Aware)

**Challenge**: Sprint dates are often outside the AOP weekly_costs window. Sprint is a RE-PLANNED schedule, not just compressed.

**Recommended Approach**: Re-calculate Sprint costs using `cost_plan_total` and Sprint dates.

```python
def calculate_sprint_gauge(tasks: List[Dict], time_mode: str, current_date: str) -> Dict:
    """
    Sprint Achievement = (Sprint Actual / Sprint Plan) * 100

    Only considers tasks with Sprint dates.
    Calculates Sprint Plan by prorating cost_plan_total over Sprint duration.
    Estimates Sprint Actual based on task progress.

    Args:
        tasks: Filtered tasks (by zone/region/project)
        time_mode: "fy", "quarter", or "month"
        current_date: Reference date for calculations
    """
    time_start, time_end = get_time_boundaries(time_mode, current_date)

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

        sprint_start = parse_date(sprint["start"])
        sprint_end = parse_date(sprint["finish"])
        sprint_duration = sprint.get("duration_days") or 1

        # Calculate overlap between Sprint window and selected time mode
        overlap_start = max(sprint_start, time_start)
        overlap_end = min(sprint_end, time_end)

        if overlap_start >= overlap_end:
            continue  # No overlap with selected time window

        overlap_days = (overlap_end - overlap_start).days
        cost_total = task.get("cost_plan_total") or 0.0
        daily_rate = cost_total / sprint_duration

        # Sprint Plan: prorated cost for overlap period
        task_sprint_plan = daily_rate * overlap_days
        sprint_plan += task_sprint_plan

        # Sprint Actual: based on task progress
        progress = task.get("progress") or {}
        if progress.get("is_complete"):
            sprint_actual += task_sprint_plan  # 100% delivered
        else:
            pct = (progress.get("percent_complete") or 0) / 100
            sprint_actual += task_sprint_plan * pct

    achieved_pct = (sprint_actual / sprint_plan * 100) if sprint_plan > 0 else 0.0

    return {
        "achieved_pct": round(achieved_pct, 1),
        "status_color": get_status_color(achieved_pct),
        "sprint_actual": round(sprint_actual, 2),
        "sprint_plan": round(sprint_plan, 2),
        "tasks_with_sprint": tasks_with_sprint
    }
```

### Status Color Logic

```python
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

## 4. Output Schema

### KPI Gauges - Full Matrix Structure

Each filter key in `dashboard_data` contains KPI gauges with pre-calculated values for all three time modes. The full staging structure shows the matrix distribution:

```json
{
  "dashboard_data": {
    "ALL": {
      "kpi_gauges": {
        "aop": {
          "fy": {"achieved_pct": 87.5, "status_color": "amber", "actual": 1000000000, "plan": 1142857143},
          "quarter": {"achieved_pct": 92.0, "status_color": "green", "actual": 250000000, "plan": 271739130},
          "month": {"achieved_pct": 88.0, "status_color": "amber", "actual": 100000000, "plan": 113636364}
        },
        "sprint": {
          "fy": {"achieved_pct": 92.0, "status_color": "green", "sprint_actual": 800000000, "sprint_plan": 869565217, "tasks_with_sprint": 45000},
          "quarter": {"achieved_pct": 95.0, "status_color": "green", "sprint_actual": 200000000, "sprint_plan": 210526316, "tasks_with_sprint": 12000},
          "month": {"achieved_pct": 90.0, "status_color": "amber", "sprint_actual": 80000000, "sprint_plan": 88888889, "tasks_with_sprint": 3500}
        }
      }
    },
    "ZONE_MZ": {
      "kpi_gauges": {
        "aop": {
          "fy": {"achieved_pct": 91.2, "status_color": "green", "actual": 320000000, "plan": 351000000},
          "quarter": {"achieved_pct": 94.5, "status_color": "amber", "actual": 85000000, "plan": 89947090},
          "month": {"achieved_pct": 89.0, "status_color": "amber", "actual": 32000000, "plan": 35955056}
        },
        "sprint": {
          "fy": {"achieved_pct": 93.5, "status_color": "green", "sprint_actual": 280000000, "sprint_plan": 299465241, "tasks_with_sprint": 15000},
          "quarter": {"achieved_pct": 96.0, "status_color": "green", "sprint_actual": 72000000, "sprint_plan": 75000000, "tasks_with_sprint": 4000},
          "month": {"achieved_pct": 91.0, "status_color": "amber", "sprint_actual": 28000000, "sprint_plan": 30769231, "tasks_with_sprint": 1200}
        }
      }
    },
    "PROJ_Horizon": {
      "kpi_gauges": {
        "aop": {
          "fy": {"achieved_pct": 88.0, "status_color": "amber", "actual": 95000000, "plan": 107954545},
          "quarter": {"achieved_pct": 90.0, "status_color": "amber", "actual": 24000000, "plan": 26666667},
          "month": {"achieved_pct": 85.5, "status_color": "amber", "actual": 9500000, "plan": 11111111}
        },
        "sprint": {
          "fy": {"achieved_pct": 90.0, "status_color": "amber", "sprint_actual": 82000000, "sprint_plan": 91111111, "tasks_with_sprint": 4500},
          "quarter": {"achieved_pct": 92.0, "status_color": "green", "sprint_actual": 21000000, "sprint_plan": 22826087, "tasks_with_sprint": 1200},
          "month": {"achieved_pct": 88.0, "status_color": "amber", "sprint_actual": 8200000, "sprint_plan": 9318182, "tasks_with_sprint": 350}
        }
      }
    }
  }
}
```

### Frontend Lookup

```javascript
// User selects: Zone = MZ, Time = Quarter
const filterKey = "ZONE_MZ";
const timeMode = "quarter";

const aopGauge = stagingData.dashboard_data[filterKey].kpi_gauges.aop[timeMode];
// Returns: {achieved_pct: 94.5, status_color: "amber", actual: 85000000, plan: 89947090}

const sprintGauge = stagingData.dashboard_data[filterKey].kpi_gauges.sprint[timeMode];
// Returns: {achieved_pct: 96.0, status_color: "green", sprint_actual: 72000000, sprint_plan: 75000000, tasks_with_sprint: 4000}
```

### GaugeData Schema (per time mode)

**AOP Gauge Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `achieved_pct` | number | Yes | Achievement percentage (0-200+) |
| `status_color` | "red"\|"amber"\|"green" | Yes | Pre-calculated color |
| `actual` | number | Yes | Actual cost in time window |
| `plan` | number | Yes | Plan cost in time window |

**Sprint Gauge Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `achieved_pct` | number | Yes | Achievement percentage (0-200+) |
| `status_color` | "red"\|"amber"\|"green" | Yes | Pre-calculated color |
| `sprint_actual` | number | Yes | Estimated Sprint actual (progress-based) |
| `sprint_plan` | number | Yes | Sprint plan cost (prorated) |
| `tasks_with_sprint` | integer | Yes | Count of tasks with sprint data in window |

---

## 5. Color Thresholds

| Range | Color | Meaning |
|-------|-------|---------|
| < 85% | Red | Critical - significantly behind |
| 85% - 95% | Amber | Warning - slightly behind |
| > 95% | Green | On track or ahead |

### Visual Mapping

```
        Red           Amber          Green
  |------------|---------------|------------|
  0           85              95          100+
```

---

## 6. Edge Cases

| Scenario | Handling |
|----------|----------|
| No tasks in filter | AOP: 0%, Sprint: 0% with "red" |
| All plan costs are 0 | Return 0% (avoid division by zero) |
| No tasks with Sprint data | Sprint: 0% with note in `tasks_with_sprint: 0` |
| Achievement > 100% | Show actual value (e.g., 115%) |
| Achievement > 200% | Cap display at 200% but show real value |
| Negative costs (adjustments) | Include in calculation |

---

## 7. Sprint Calculation Details

### Why Sprint Requires Special Handling

Based on data analysis (`test/sprint-achievement-data-analysis.md`):

1. **Sprint is a RE-PLANNED schedule**: Sprint dates can be months or years different from AOP dates
2. **Only 3% overlap**: Only 3% of tasks have Sprint window fully within AOP window
3. **Date shifts up to 497 days**: Sprint dates may be shifted significantly from AOP

### Recommended Sprint Calculation Approach

```python
def calculate_sprint_plan_for_task(task: Dict, time_start: str, time_end: str) -> float:
    """
    Calculate Sprint Plan Cost for a task within a time window.

    Steps:
    1. Get Sprint window (start, finish, duration)
    2. Calculate overlap between Sprint window and selected time window
    3. Prorate cost_plan_total over Sprint duration for overlap period
    """
    sprint = task.get("dates", {}).get("sprint", {})
    if not sprint.get("start"):
        return 0.0

    sprint_start = parse_date(sprint["start"])
    sprint_end = parse_date(sprint["finish"])
    sprint_duration = sprint.get("duration_days") or 1

    # Overlap calculation
    overlap_start = max(sprint_start, parse_date(time_start))
    overlap_end = min(sprint_end, parse_date(time_end))

    if overlap_start >= overlap_end:
        return 0.0  # No overlap

    overlap_days = (overlap_end - overlap_start).days
    daily_rate = (task.get("cost_plan_total") or 0.0) / sprint_duration

    return daily_rate * overlap_days
```

### Sprint Actual Estimation

Since `weekly_costs` are based on AOP dates (not Sprint dates), Sprint Actual must be estimated:

| Task Status | Sprint Actual Calculation |
|-------------|---------------------------|
| Complete (`is_complete = true`) | `sprint_plan` (100% delivered) |
| In Progress | `sprint_plan * percent_complete / 100` |
| Not Started | 0 |

### Data Quality Considerations

- **64% of leaf tasks** have Sprint dates
- **45% of leaf tasks** have both Sprint dates AND cost_timeline
- Sprint Actual is an **approximation** based on progress, not actual weekly costs

---

## 8. Performance Considerations

- **Aggregation**: O(n) where n = filtered task count
- **Memory**: Constant - only totals stored
- **Output size**: ~200 bytes per filter key
