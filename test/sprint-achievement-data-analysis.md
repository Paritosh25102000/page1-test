# Sprint Achievement Data Analysis Report

**Date**: 2025-12-17
**Status**: Research Complete
**Project**: COO Dashboard - Phase 3 Staging

---

## 1. Executive Summary

This report analyzes the data architecture challenges for calculating Sprint Achievement in the COO Dashboard. The key finding is that **Sprint schedules are not compressed versions of AOP schedules, but completely re-planned timelines** - meaning Sprint dates can be months or even years different from AOP dates.

**Critical Issue**: The current `cost_timeline.weekly_costs` are distributed based on AOP Plan dates, NOT Sprint dates. For many tasks, Sprint windows don't overlap with AOP windows at all, making it impossible to calculate Sprint costs by simply filtering weekly_costs.

---

## 2. Data Analysis Results

### 2.1 Task Coverage (Ramaiah Project Sample)

| Metric | Count | Percentage |
|--------|-------|------------|
| Total tasks | 1,408 | 100% |
| Leaf tasks | 1,155 | 82% |
| Leaf tasks with Sprint dates | 738 | 64% of leaf |
| Leaf tasks with Sprint + cost_timeline | 524 | 45% of leaf |

### 2.2 Duration Comparison: AOP vs Sprint

| Category | Count | Percentage |
|----------|-------|------------|
| Same duration (Sprint = AOP) | 79 | 79% |
| Compressed (Sprint < AOP) | 20 | 20% |
| Extended (Sprint > AOP) | 1 | 1% |
| **Average duration change** | -6.5% | |

**Key Insight**: Sprint schedules mostly keep the same duration as AOP but **shift the dates** rather than compress them.

### 2.3 Date Range Overlap Analysis

**Critical Finding**: Sprint windows rarely align with AOP windows.

| Metric | Value |
|--------|-------|
| Tasks where Sprint window is fully within AOP window | 3% |
| Tasks where Sprint starts >30 days from AOP start | 513 tasks |
| Maximum Sprint shift earlier than AOP | 437 days |
| Maximum Sprint shift later than AOP | 497 days |

### 2.4 Example Tasks with Significant Date Mismatch

```
Task: Club structure
  AOP Plan:   2025-03-08 to 2026-09-10
  Sprint:     2026-07-18 to 2028-05-12
  Weekly costs cover: 2025-03-31 to 2026-04-05
  Sprint starts 497 days LATER than AOP

Task: Basement PHE works
  AOP Plan:   2027-01-01 to 2027-04-30
  Sprint:     2025-10-21 to 2026-04-10
  Weekly costs cover: N/A (outside FY)
  Sprint starts 437 days EARLIER than AOP
```

---

## 3. Problem Statement

### 3.1 Business Requirement (from schemas/page-1-executive-simmary/3-aop-and-sprint-gauges.md)

The business definition for Sprint Achievement:

> **Sprint Plan Cost**: For each task, calculate daily burn rate: `cost_plan_total / dates.sprint.duration_days`. Multiply by `days_elapsed_in_sprint`.
>
> **Sprint Actual Cost**: Sum `cost_timeline.weekly_costs.actual` specifically for weeks falling within the sprint window.

### 3.2 Data Architecture Limitation

The current Master JSON structure has:

```json
{
  "cost_plan_total": 625720100,
  "dates": {
    "plan": {"start": "2025-03-21", "end": "2025-06-29"},
    "sprint": {"start": "2025-04-01", "finish": "2025-06-26"}
  },
  "cost_timeline": {
    "weekly_costs": [
      // Weekly costs distributed based on AOP plan dates!
      {"week_start": "2025-03-31", "plan": {"cost": 123456}, "actual": {"cost": 110000}}
    ]
  }
}
```

**The Problem**: `weekly_costs` are calculated using AOP plan date ranges, NOT Sprint date ranges. When Sprint dates don't overlap with AOP dates, there are no weekly costs in the Sprint window to sum.

---

## 4. Solution Options

### Option A: Re-distribute Costs for Sprint Window (Recommended)

**Approach**: Calculate Sprint costs independently using `cost_plan_total` and Sprint dates.

**Sprint Plan Cost Calculation**:
```python
sprint_duration = dates.sprint.duration_days
daily_rate = cost_plan_total / sprint_duration
days_elapsed = calculate_days_elapsed_in_sprint(current_date, sprint_start, sprint_end)
sprint_plan_cost = daily_rate * days_elapsed
```

**Sprint Actual Cost Calculation**:
- If task is complete (`progress.is_complete = true`): Use `cost_plan_total` as actual (assumes full delivery)
- If task is in progress: Prorate based on `progress.percent_complete`
- If task not started: Use 0

**Pros**:
- Works with existing data
- Mathematically consistent
- No changes to Stage 1 ETL

**Cons**:
- Assumes linear cost distribution
- Doesn't account for actual weekly variations
- Sprint "actual" is an approximation, not true actual

### Option B: Generate Sprint-Based Weekly Costs (Major Change)

**Approach**: Modify Stage 1 ETL to generate a second `cost_timeline` based on Sprint dates.

**Data Model Change**:
```json
{
  "cost_timeline": {
    "aop_weekly_costs": [...],  // Current: based on AOP plan dates
    "sprint_weekly_costs": [...] // NEW: based on Sprint dates
  }
}
```

**Pros**:
- True weekly cost distribution for Sprint
- More accurate Sprint achievement

**Cons**:
- Significant Stage 1 refactoring required
- Increases JSON file size (~40% larger)
- Sprint dates may be outside FY window (no costs to distribute)
- Complex to maintain two parallel cost timelines

### Option C: Use Progress-Based Approximation (Simplest)

**Approach**: Ignore time-based cost distribution; use task completion status.

**Sprint Achievement**:
```python
sprint_plan = sum(cost_plan_total for tasks with sprint dates)
sprint_actual = sum(cost_plan_total * percent_complete/100 for tasks with sprint dates)
sprint_achievement = sprint_actual / sprint_plan * 100
```

**Pros**:
- Simple to implement
- Works with existing data
- No assumptions about cost distribution

**Cons**:
- Ignores actual vs plan timing
- Doesn't reflect acceleration/delay
- May not match business expectation

### Option D: Hybrid Approach (Balanced)

**Approach**: Combine Options A and C based on data availability.

1. For tasks with Sprint dates within AOP window: Use weekly_costs filtering (current approach)
2. For tasks with Sprint dates outside AOP window: Use progress-based calculation

**Implementation**:
```python
def calculate_sprint_cost(task):
    if sprint_window_overlaps_aop(task):
        # Filter weekly_costs by Sprint window
        return sum_weekly_costs_in_sprint_window(task)
    else:
        # Fall back to progress-based
        return task.cost_plan_total * (task.progress.percent_complete / 100)
```

---

## 5. Recommendation

### Recommended Solution: Option A (Re-distribute Costs for Sprint Window)

**Rationale**:
1. Works with existing Master JSON structure - no Stage 1 changes
2. Provides time-mode aware calculations (FY, Quarter, Month)
3. Aligns with business definition of "cost prorated over Sprint duration"
4. Can be implemented entirely in Stage 3

**Implementation Details**:

```python
def calculate_sprint_achievement(tasks, time_mode, current_date):
    """Calculate Sprint achievement for filtered tasks in given time mode."""
    sprint_plan_total = 0
    sprint_actual_total = 0

    time_start, time_end = get_time_boundaries(time_mode, current_date)

    for task in tasks:
        sprint = task.get('dates', {}).get('sprint', {})
        if not sprint.get('start'):
            continue

        # Calculate Sprint Plan Cost for this time window
        sprint_start = parse_date(sprint['start'])
        sprint_end = parse_date(sprint['finish'])
        sprint_duration = sprint['duration_days']

        # Overlap between Sprint window and selected time mode
        overlap_start = max(sprint_start, time_start)
        overlap_end = min(sprint_end, time_end)

        if overlap_start < overlap_end:
            overlap_days = (overlap_end - overlap_start).days
            daily_rate = task['cost_plan_total'] / sprint_duration
            sprint_plan_total += daily_rate * overlap_days

            # Sprint Actual: based on task progress
            if task.get('progress', {}).get('is_complete'):
                sprint_actual_total += daily_rate * overlap_days
            else:
                pct = task.get('progress', {}).get('percent_complete', 0) / 100
                sprint_actual_total += daily_rate * overlap_days * pct

    return (sprint_actual_total / sprint_plan_total * 100) if sprint_plan_total > 0 else 0
```

### Alternative Consideration

If business requires true weekly actual costs (not approximations), recommend **Option B** but with significant scope increase:
- Add `sprint_cost_timeline` to Master JSON in Stage 1
- Recalculate weekly costs using Sprint dates as the basis
- This would require re-running Stage 1 for all projects

---

## 6. Impact on Staging Data Structure

### 6.1 Filter Matrix

KPI Gauges must respond to **two independent controls**:
1. **Filter Selection** (Zone/Region/Project dropdown) → ~50 filter keys
2. **Time Toggle** (FY/Quarter/Month) → 3 time modes

This creates a **matrix of pre-computed values**:

```
                    │   FY    │ Quarter │  Month  │
────────────────────┼─────────┼─────────┼─────────┤
ALL                 │  value  │  value  │  value  │
ZONE_MZ             │  value  │  value  │  value  │
ZONE_NZ             │  value  │  value  │  value  │
ZONE_SZ             │  value  │  value  │  value  │
ZONE_WEZ            │  value  │  value  │  value  │
REG_MZ1             │  value  │  value  │  value  │
REG_NZ1             │  value  │  value  │  value  │
... (all regions)   │   ...   │   ...   │   ...   │
PROJ_Horizon        │  value  │  value  │  value  │
PROJ_Miraya         │  value  │  value  │  value  │
... (all 13 proj)   │   ...   │   ...   │   ...   │
────────────────────┴─────────┴─────────┴─────────┘
```

**Total combinations**: ~50 filter keys × 3 time modes = ~150 pre-computed values per gauge

### 6.2 Recommended Staging Data Structure

Each filter key contains gauges with all time mode values:

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

### 6.3 Frontend Lookup Logic

```javascript
// User selects: Zone = MZ, Time = Quarter
const filterKey = "ZONE_MZ";
const timeMode = "quarter";

const aopGauge = stagingData.dashboard_data[filterKey].kpi_gauges.aop[timeMode];
// Returns: {achieved_pct: 94.5, status_color: "amber", actual: 85000000, plan: 89947090}

const sprintGauge = stagingData.dashboard_data[filterKey].kpi_gauges.sprint[timeMode];
// Returns: {achieved_pct: 96.0, status_color: "green", sprint_actual: 72000000, sprint_plan: 75000000, tasks_with_sprint: 4000}
```

---

## 7. Data Quality Considerations

1. **Tasks without Sprint dates**: 36% of leaf tasks have no Sprint dates. Sprint Achievement will only reflect Sprint-enabled tasks.

2. **Tasks with Sprint outside FY**: Some Sprint windows extend beyond FY 2025-26. These contribute $0 to FY Sprint calculations.

3. **Progress accuracy**: Sprint Actual relies on `percent_complete` field. If this isn't regularly updated, Sprint Actual may be inaccurate.

4. **Cost approximation**: The recommended approach assumes linear cost distribution. Real construction projects may have non-linear cost profiles (e.g., front-loaded for materials procurement).

---

## 8. Next Steps

1. **Confirm business acceptance** of the recommended approach (Option A)
2. **Update Stage 3 spec** with the new calculation logic
3. **Update kpi_calculator.py** implementation plan
4. **Add validation** for Sprint data quality in staging reports

---

## Appendix: Raw Data Analysis Script

```python
# Analysis performed on Ramaiah.json
# See test/sprint-achievement-data-analysis.md for methodology
```
