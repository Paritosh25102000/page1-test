# Widget Specification: KPI Gauges (AOP & Sprint)

**Widget ID**: PG1-WIDGET-03
**Dashboard Page**: Page 1 (Executive Summary)
**Element Type**: Semi-Circle Gauge

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

---

## 2. Input Data

### Source Fields (from Master JSON)

```python
task = {
    "type": "leaf",  # Only leaf tasks contribute
    "cost_timeline": {
        "summary": {
            "plan_cost_in_fy": 125000.00,   # Plan cost for FY
            "actual_cost_in_fy": 108750.00  # Actual cost YTD
        }
    },
    "dates": {
        "sprint": {
            "start": "2025-04-01",  # Sprint start (null if no sprint)
            "end": "2025-05-15",
            "duration_days": 44
        }
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
3. **AOP**: All leaf tasks with cost_timeline.summary
4. **Sprint**: Only tasks where `dates.sprint.start` is not null

---

## 3. Transformation Logic

### AOP Gauge Calculation

```python
def calculate_aop_gauge(tasks: List[Dict]) -> Dict:
    """
    AOP Achievement = (Total Actual YTD / Total Plan YTD) * 100

    Uses cost_timeline.summary for YTD totals.
    """
    total_plan = 0.0
    total_actual = 0.0

    for task in tasks:
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
```

### Sprint Gauge Calculation

```python
def calculate_sprint_gauge(tasks: List[Dict]) -> Dict:
    """
    Sprint Achievement = (Sprint Actual / Sprint Plan) * 100

    Only considers tasks with Sprint dates set.
    Sprint plan = tasks' plan cost aligned to sprint schedule.
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
            continue  # Skip tasks without sprint

        tasks_with_sprint += 1

        # Get cost data
        timeline = task.get("cost_timeline") or {}
        summary = timeline.get("summary") or {}

        # Use plan_cost_in_fy as proxy for sprint plan
        # (More sophisticated: prorate based on sprint vs AOP duration)
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

### KPI Gauges Object

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
    "sprint_plan": 106175000.00,
    "tasks_with_sprint": 45678
  }
}
```

### GaugeData Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `achieved_pct` | number | Yes | Achievement percentage (0-200+) |
| `status_color` | "red"\|"amber"\|"green" | Yes | Pre-calculated color |
| `actual_ytd` | number | No | Actual cost YTD (AOP) |
| `plan_ytd` | number | No | Plan cost YTD (AOP) |
| `sprint_actual` | number | No | Sprint actual cost |
| `sprint_plan` | number | No | Sprint plan cost |
| `tasks_with_sprint` | integer | No | Count of tasks with sprint data |

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

## 7. Advanced Sprint Calculation (Future)

The current implementation uses `plan_cost_in_fy` as a proxy for sprint plan. A more sophisticated approach:

```python
def calculate_sprint_plan_prorated(task: Dict) -> float:
    """
    Calculate sprint plan cost prorated by duration compression.

    Sprint schedules are typically ~40% shorter than AOP.
    Prorate: sprint_plan = cost * (sprint_days / aop_days)

    This assumes cost is spread linearly over duration.
    """
    cost = task.cost_plan_total or 0.0
    sprint_duration = task.dates.sprint.duration_days
    aop_duration = task.dates.plan.duration_days

    if not sprint_duration or not aop_duration:
        return cost  # Fallback to full cost

    # Sprint is shorter, so less of the cost should be "in scope"
    # But business typically expects full cost delivered in sprint time
    return cost  # Keep full cost as target
```

---

## 8. Performance Considerations

- **Aggregation**: O(n) where n = filtered task count
- **Memory**: Constant - only totals stored
- **Output size**: ~200 bytes per filter key
