# Widget Specification: COC Trend Chart

**Widget ID**: PG1-WIDGET-01
**Dashboard Page**: Page 1 (Executive Summary)
**Element Type**: Combo Chart (Bar + Line)

---

## 1. Business Context

### Purpose
Visualize planned vs actual cost burn rate at the resolution relevant to the user (Macro vs Tactical).

### Key Questions Answered
- **FY Mode**: "Are we spending according to the AOP?"
- **Quarter Mode**: "How is this quarter tracking?"
- **Month Mode**: "Did we hit production targets last week?"

### Target Action
Monitor the gap between Cumulative Actual (blue line) and Cumulative Plan (green line).

---

## 2. Input Data

### Source Fields (from Master JSON)

```python
task = {
    "type": "leaf",  # Only leaf tasks contribute
    "cost_timeline": {
        "weekly_costs": [
            {
                "week_start": "2025-04-07",  # Monday
                "plan": {"cost": 12500.00},
                "actual": {"cost": 11800.00}
            },
            # ... more weeks
        ]
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
2. **Filter Scope**: Apply zone/region/project filter from current selection
3. **Cost Data**: Exclude tasks with no `cost_timeline` or empty `weekly_costs`

---

## 3. Transformation Logic

### Step 1: Aggregate Weekly Costs

```python
# For all filtered tasks
weekly_totals = {}  # week_start -> {plan: float, actual: float}

for task in filtered_tasks:
    if task.type != "leaf":
        continue

    for week in task.cost_timeline.weekly_costs:
        week_key = week.week_start

        if week_key not in weekly_totals:
            weekly_totals[week_key] = {"plan": 0.0, "actual": 0.0}

        weekly_totals[week_key]["plan"] += week.plan.cost or 0.0
        weekly_totals[week_key]["actual"] += week.actual.cost or 0.0
```

### Step 2: Generate FY Series (Monthly)

```python
# Aggregate weeks into months
FY_START = "2025-04-01"
FY_END = "2026-03-31"

monthly_totals = {}  # YYYY-MM -> {plan: float, actual: float}

for week_start, costs in weekly_totals.items():
    if FY_START <= week_start <= FY_END:
        month_key = week_start[:7]  # "2025-04"
        if month_key not in monthly_totals:
            monthly_totals[month_key] = {"plan": 0.0, "actual": 0.0}
        monthly_totals[month_key]["plan"] += costs["plan"]
        monthly_totals[month_key]["actual"] += costs["actual"]

# Build series with cumulative
fy_series = []
cumm_plan = 0.0
cumm_actual = 0.0

for month in sorted(monthly_totals.keys()):
    costs = monthly_totals[month]
    cumm_plan += costs["plan"]
    cumm_actual += costs["actual"]

    fy_series.append({
        "label": format_month(month),  # "Apr-25"
        "sort_date": f"{month}-01",
        "plan_cost": costs["plan"],
        "actual_cost": costs["actual"],
        "cumm_plan": cumm_plan,
        "cumm_actual": cumm_actual
    })
```

### Step 3: Generate Quarter Series (Weekly)

```python
# Filter weekly data to current quarter
q_start, q_end = get_current_quarter_dates()

quarter_series = []
cumm_plan = 0.0
cumm_actual = 0.0

for week_start in sorted(weekly_totals.keys()):
    if q_start <= week_start <= q_end:
        costs = weekly_totals[week_start]
        cumm_plan += costs["plan"]
        cumm_actual += costs["actual"]

        quarter_series.append({
            "label": format_week(week_start),  # "Wk 14"
            "sort_date": week_start,
            "plan_cost": costs["plan"],
            "actual_cost": costs["actual"],
            "cumm_plan": cumm_plan,
            "cumm_actual": cumm_actual
        })
```

### Step 4: Generate Month Series (Looking Glass)

```python
# Filter weekly data to +/- 5 weeks
today = datetime.now()
lg_start = today - timedelta(weeks=5)
lg_end = today + timedelta(weeks=5)

month_series = []
cumm_plan = 0.0
cumm_actual = 0.0

for week_start in sorted(weekly_totals.keys()):
    if lg_start <= datetime.fromisoformat(week_start) <= lg_end:
        costs = weekly_totals[week_start]
        cumm_plan += costs["plan"]
        cumm_actual += costs["actual"]

        month_series.append({
            "label": format_week(week_start),
            "sort_date": week_start,
            "plan_cost": costs["plan"],
            "actual_cost": costs["actual"],
            "cumm_plan": cumm_plan,
            "cumm_actual": cumm_actual
        })
```

---

## 4. Output Schema

### COC Trend Object

```json
{
  "fy_series": [
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
    // ... up to 12 months
  ],
  "quarter_series": [
    {
      "label": "Wk 40",
      "sort_date": "2025-10-06",
      "plan_cost": 3100000,
      "actual_cost": 2900000,
      "cumm_plan": 3100000,
      "cumm_actual": 2900000
    }
    // ... up to 13 weeks
  ],
  "month_series": [
    {
      "label": "Wk 50",
      "sort_date": "2025-12-08",
      "plan_cost": 2800000,
      "actual_cost": 2600000,
      "cumm_plan": 2800000,
      "cumm_actual": 2600000
    }
    // ... 11 weeks (5 back, current, 5 forward)
  ]
}
```

### TrendPoint Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | X-axis label |
| `sort_date` | string | Yes | YYYY-MM-DD for sorting |
| `plan_cost` | number \| null | Yes | Periodic plan cost (bar) |
| `actual_cost` | number \| null | Yes | Periodic actual cost (bar) |
| `cumm_plan` | number \| null | No | Cumulative plan (line) |
| `cumm_actual` | number \| null | No | Cumulative actual (line) |

---

## 5. Visualization Mapping

### Chart Configuration

| Series | Type | Y-Axis | Color |
|--------|------|--------|-------|
| Plan Cost | Bar | Left (Primary) | Blue |
| Actual Cost | Bar | Left (Primary) | Green |
| Cumm Plan | Line | Right (Secondary) | Blue (dashed) |
| Cumm Actual | Line | Right (Secondary) | Green (solid) |

### X-Axis Labels

| Mode | Label Format | Example | Max Points |
|------|--------------|---------|------------|
| FY | "MMM-YY" | "Apr-25" | 12 |
| Quarter | "Wk {N}" | "Wk 14" | 13 |
| Month | "Wk {N}" | "Wk 50" | 11 |

---

## 6. Edge Cases

| Scenario | Handling |
|----------|----------|
| No cost data in period | Show empty series (no bars/lines) |
| Null actual cost | Show plan bar only, no actual bar |
| Future weeks (month mode) | Show plan bar, null actual |
| Week splits across months | Assign to week's start date month |
| Very large values | Frontend handles number formatting |

---

## 7. Performance Considerations

- **Aggregation**: O(n) where n = total weeks across all tasks
- **Memory**: Store only weekly totals, not individual task data
- **Output size**: ~1KB per series (~3KB per filter key)
