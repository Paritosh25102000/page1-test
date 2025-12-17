# Widget Specification: Project Achievement Matrix

**Widget ID**: PG1-WIDGET-04
**Dashboard Page**: Page 1 (Executive Summary)
**Element Type**: Heatmap Table

---

## 1. Business Context

### Purpose
Portfolio health-check matrix that distributes projects into performance buckets.

### Key Questions Answered
- "How many projects are critically failing (<60%)?"
- "Is the West Zone (WEZ) performing better than North Zone (NZ)?"
- "Which region has the most at-risk projects?"

### Target Action
COO looks for the "<60%" column. If count > 0, drill down to see which projects.

---

## 2. Input Data

### Source Fields (from Master JSON)

```python
task = {
    "type": "leaf",  # Only leaf tasks contribute
    "cost_timeline": {
        "summary": {
            "plan_cost_in_fy": 125000.00,
            "actual_cost_in_fy": 108750.00
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
3. **Aggregation**: Group by `project_name` within filter scope

---

## 3. Transformation Logic

### Step 1: Calculate Per-Project Achievement

```python
def calculate_project_achievements(tasks: List[Dict]) -> Dict[str, float]:
    """
    Calculate achievement percentage per project.

    Achievement = (Actual Cost YTD / Plan Cost YTD) * 100
    """
    project_costs = {}  # project_name -> {plan: float, actual: float}

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

        if project not in project_costs:
            project_costs[project] = {"plan": 0.0, "actual": 0.0}

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
```

### Step 2: Bucket Assignment

```python
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
```

### Step 3: Generate Matrix Rows

#### For "ALL" Filter (Zone Rows)

```python
def generate_zone_rows(
    project_achievements: Dict[str, float],
    hierarchy: Dict
) -> List[Dict]:
    """Generate one row per zone."""
    rows = []

    for zone in sorted(hierarchy.keys()):
        buckets = {"gt_120": 0, "100_120": 0, "85_100": 0, "60_85": 0, "lt_60": 0}

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
```

#### For Zone Filter (Region Rows)

```python
def generate_region_rows(
    project_achievements: Dict[str, float],
    hierarchy: Dict,
    zone: str
) -> List[Dict]:
    """Generate one row per region in the selected zone."""
    rows = []

    regions = hierarchy.get(zone, {})
    for region in sorted(regions.keys()):
        buckets = {"gt_120": 0, "100_120": 0, "85_100": 0, "60_85": 0, "lt_60": 0}

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
```

#### For Region/Project Filter (Project Rows)

```python
def generate_project_rows(
    project_achievements: Dict[str, float],
    tasks: List[Dict]
) -> List[Dict]:
    """Generate one row per project in scope."""
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

        buckets = {"gt_120": 0, "100_120": 0, "85_100": 0, "60_85": 0, "lt_60": 0}
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

## 4. Output Schema

### Project Matrix Object

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
    },
    {
      "label": "SZ",
      "id": "ZONE_SZ",
      "buckets": {
        "gt_120": 0,
        "100_120": 1,
        "85_100": 1,
        "60_85": 0,
        "lt_60": 0
      }
    },
    {
      "label": "WEZ",
      "id": "ZONE_WEZ",
      "buckets": {
        "gt_120": 0,
        "100_120": 0,
        "85_100": 1,
        "60_85": 0,
        "lt_60": 0
      }
    }
  ]
}
```

### MatrixRow Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | Row header (Zone/Region/Project name) |
| `id` | string | No | Filter key for drill-down |
| `buckets` | Buckets | Yes | Project counts per bucket |
| `achievement_pct` | number | No | Individual achievement (project rows only) |

### Buckets Schema

| Field | Type | Description |
|-------|------|-------------|
| `gt_120` | integer | Projects > 120% |
| `100_120` | integer | Projects 100-120% |
| `85_100` | integer | Projects 85-100% |
| `60_85` | integer | Projects 60-85% |
| `lt_60` | integer | Projects < 60% (critical) |

---

## 5. Bucket Definitions

| Bucket | Range | Meaning | Visual Style |
|--------|-------|---------|--------------|
| `gt_120` | > 120% | Over-performing | Light green |
| `100_120` | 100-120% | On track | Green |
| `85_100` | 85-100% | Acceptable | Amber/yellow |
| `60_85` | 60-85% | Needs attention | Orange |
| `lt_60` | < 60% | Critical | Red (highlighted) |

### Column Order (Left to Right)
```
> 120%  |  100-120%  |  85-100%  |  60-85%  |  < 60%
```

---

## 6. Row Granularity by Filter

| Current Filter | Rows Show | Example |
|----------------|-----------|---------|
| ALL | Zones | MZ, NZ, SZ, WEZ |
| ZONE_MZ | Regions in MZ | MZ1, Kolkata |
| ZONE_NZ | Regions in NZ | NZ1, NZ2 |
| REG_MZ1 | Projects in MZ1 | Horizon, Reserve, Avenue 11 |
| PROJ_Horizon | Single project | Horizon (with achievement %) |

---

## 7. Edge Cases

| Scenario | Handling |
|----------|----------|
| Zone has no projects | Show row with all zero buckets |
| Project has no cost data | Achievement = 0%, bucketed as lt_60 |
| All projects in same bucket | Other buckets show 0 |
| Achievement exactly 85% | Goes to "85_100" bucket |
| Achievement exactly 100% | Goes to "100_120" bucket |
| Negative achievement | Bucket as lt_60 |

---

## 8. Drill-Down Behavior

When user clicks a cell:

1. **Cell Identification**: `(row_id, bucket_name)`
2. **Action**: Log to console (current), Modal popup (future)
3. **Modal Content** (future): List of project names in that bucket for that row

```javascript
// Example click handler
onClick={(row, bucket) => {
    console.log(`Clicked: ${row.label} / ${bucket}`);
    // Future: showProjectListModal(row.id, bucket)
}}
```

---

## 9. Heatmap Styling

### Color Intensity

Cell background color intensity based on:
- **Option A**: Count value (higher = more intense)
- **Option B**: Bucket type (lt_60 always red)

Current implementation: **Option B** (bucket-based coloring)

### CSS Classes

```css
.bucket-gt_120  { background: #d4edda; }  /* Light green */
.bucket-100_120 { background: #c3e6cb; }  /* Green */
.bucket-85_100  { background: #ffeeba; }  /* Amber */
.bucket-60_85   { background: #f5c6cb; }  /* Light red */
.bucket-lt_60   { background: #f8d7da; border: 2px solid #dc3545; }  /* Red with border */
```

---

## 10. Performance Considerations

- **Aggregation**: O(n) where n = filtered task count
- **Memory**: Store only project totals, then bucket counts
- **Output size**: ~300 bytes per filter key (4 rows × 5 buckets)
