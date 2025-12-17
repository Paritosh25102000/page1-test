# Widget Specification: Global Filter & Timeline Panel

**Widget ID**: PG1-CTRL-01
**Dashboard Page**: Page 1 (Executive Summary)
**Element Type**: Control Component (Dropdowns + Toggle)

---

## 1. Business Context

### Purpose
Allow the COO to:
1. Filter dashboard by organizational hierarchy (Zone → Region → Project)
2. Toggle between strategic long-term views (FY) and tactical short-term views (Quarter/Month)

### Key Actions
- Switch from "FY View" (macro trends) to "Monthly View" (immediate operational issues)
- Drill from organization-wide to specific project

---

## 2. Input Data

### Hierarchy Tree Structure

Built from task attributes across all projects:

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
    ]
  },
  "WEZ": {
    "Kolkata": [
      {"id": "BL Saha", "name": "BL Saha"}
    ]
  }
}
```

### Time Modes Configuration

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

## 3. Transformation Logic

### Build Hierarchy Tree

```python
def build_hierarchy_tree(tasks: List[Dict]) -> Dict:
    """
    Extract Zone → Region → Project hierarchy from task attributes.

    Deduplicates projects by id within each region.
    """
    from collections import defaultdict

    hierarchy = defaultdict(lambda: defaultdict(dict))

    for task in tasks:
        attrs = task.get("attributes") or {}
        zone = attrs.get("zone")
        region = attrs.get("region")
        project_name = attrs.get("project_name")

        if zone and region and project_name:
            hierarchy[zone][region][project_name] = {
                "id": project_name,
                "name": project_name
            }

    # Convert to sorted structure
    result = {}
    for zone in sorted(hierarchy.keys()):
        result[zone] = {}
        for region in sorted(hierarchy[zone].keys()):
            result[zone][region] = sorted(
                hierarchy[zone][region].values(),
                key=lambda p: p["name"]
            )

    return result
```

### Build Time Modes

```python
def build_time_modes(current_date: Optional[str] = None) -> Dict:
    """
    Build time mode configurations.

    FY: Fixed April 1 - March 31
    Quarter: Dynamic based on current date
    Month: Dynamic +/- 5 weeks from current date
    """
    from datetime import datetime, timedelta

    if current_date:
        today = datetime.fromisoformat(current_date)
    else:
        today = datetime.now()

    # FY (Fixed)
    fy_start = "2025-04-01"
    fy_end = "2026-03-31"

    # Quarter (Dynamic)
    quarter = (today.month - 1) // 3
    q_starts = [(1, 1), (4, 1), (7, 1), (10, 1)]
    q_ends = [(3, 31), (6, 30), (9, 30), (12, 31)]

    q_start = today.replace(month=q_starts[quarter][0], day=q_starts[quarter][1])
    q_end = today.replace(month=q_ends[quarter][0], day=q_ends[quarter][1])

    # Month / Looking Glass (Dynamic)
    lg_start = today - timedelta(weeks=5)
    lg_end = today + timedelta(weeks=5)

    return {
        "fy": {
            "label": "Financial Year",
            "start": fy_start,
            "end": fy_end,
            "resolution": "month"
        },
        "quarter": {
            "label": "Current Quarter",
            "start": q_start.strftime("%Y-%m-%d"),
            "end": q_end.strftime("%Y-%m-%d"),
            "resolution": "week"
        },
        "month": {
            "label": "Looking Glass (+/- 5 Wks)",
            "start": lg_start.strftime("%Y-%m-%d"),
            "end": lg_end.strftime("%Y-%m-%d"),
            "resolution": "week"
        }
    }
```

---

## 4. Output Schema

### Controls Object

```json
{
  "hierarchy_tree": {
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
      ]
    },
    "WEZ": {
      "Kolkata": [
        {"id": "BL Saha", "name": "BL Saha"}
      ]
    }
  },
  "time_modes": {
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
}
```

---

## 5. Filter Key Construction

The frontend uses filter state to construct data keys:

```typescript
function constructFilterKey(state: FilterState): string {
    if (state.project) return `PROJ_${state.project}`;
    if (state.region) return `REG_${state.region}`;
    if (state.zone) return `ZONE_${state.zone}`;
    return "ALL";
}
```

### Key Examples

| Filter State | Key |
|--------------|-----|
| (none selected) | `ALL` |
| Zone: MZ | `ZONE_MZ` |
| Zone: MZ, Region: MZ1 | `REG_MZ1` |
| Zone: MZ, Region: MZ1, Project: Horizon | `PROJ_Horizon` |

---

## 6. UI Behavior

### Cascading Dropdowns

| Zone Selected | Region Dropdown | Project Dropdown |
|---------------|-----------------|------------------|
| None | Disabled | Disabled |
| MZ | Enabled (MZ regions) | Disabled |
| MZ + MZ1 | Enabled | Enabled (MZ1 projects) |

### Clearing Behavior

| Action | Result |
|--------|--------|
| Clear Zone | Region and Project cleared |
| Clear Region | Project cleared |
| Clear Project | Zone and Region unchanged |

### Time Mode Toggle

| Mode | Chart Resolution | Default |
|------|------------------|---------|
| FY | Monthly (12 points) | Yes |
| Quarter | Weekly (13 points) | No |
| Month | Weekly (11 points) | No |

---

## 7. Zone/Region Mapping Reference

| Zone | Regions | Projects |
|------|---------|----------|
| MZ | MZ1 | Horizon, Reserve, Avenue 11 |
| NZ | NZ1 | Miraya, Aristocrat, Zenith |
| NZ | NZ2 | Tropical Isle, Jardinia, Sec. 44 Noida |
| SZ | SZ1 | Woodscapes, RGA 2 |
| WEZ | Kolkata | BL Saha |

**Total**: 4 Zones, 5 Regions, 12 Projects

---

## 8. Edge Cases

| Scenario | Handling |
|----------|----------|
| Zone has no regions | Show zone in dropdown, regions list empty |
| Region has no projects | Show region in dropdown, projects list empty |
| Project not in any region | Data issue - should not happen with proper enrichment |
| Time mode boundaries | Quarter/Month dates update when staging is regenerated |

---

## 9. Performance Notes

- Hierarchy tree is extracted once during staging generation
- Tree structure is small (~1KB) and cached in frontend
- Time modes are static per staging file
- No computation needed in browser for filter population
