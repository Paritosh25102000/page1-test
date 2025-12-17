# Stage 1 Data Model: XML to JSON

**Document Version**: 1.0
**Status**: Production
**Last Updated**: 2025-12-16

---

## 1. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Task (Root)                                │
├─────────────────────────────────────────────────────────────────────────┤
│ uid: int                  │ Unique identifier from XML                  │
│ id: int                   │ Sequential ID                               │
│ wbs: string               │ Work Breakdown Structure code               │
│ outline_number: string    │ Human-readable outline (1.2.3.4)           │
│ name: string              │ Task name                                   │
│ parent_wbs: string|null   │ Parent task WBS (derived)                  │
│ is_summary: boolean       │ True if parent task                         │
│ is_milestone: boolean     │ True if milestone                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                 │                                       │
│         ┌───────────────────────┼───────────────────────┐              │
│         │                       │                       │              │
│         ▼                       ▼                       ▼              │
│  ┌─────────────┐         ┌─────────────┐        ┌─────────────┐       │
│  │   dates     │         │ attributes  │        │  progress   │       │
│  │  (Object)   │         │ (Obj|null)  │        │ (Obj|null)  │       │
│  └──────┬──────┘         └──────┬──────┘        └──────┬──────┘       │
│         │                       │                      │               │
│    ┌────┴────┐            ┌─────┴─────┐          ┌─────┴─────┐        │
│    │ • plan  │            │ project   │          │ percent   │        │
│    │ • manual│            │ zone      │          │ is_complete│       │
│    │ • sprint│            │ region    │          └───────────┘        │
│    │ • actual│            │ tower     │                               │
│    └─────────┘            │ floor     │                               │
│                           │ main_cat  │                               │
│                           │ sub_cat   │                               │
│                           │ trade_type│                               │
│                           │ slab_works│                               │
│                           └───────────┘                               │
│                                                                        │
│         ┌────────────────────────────────────────────┐                │
│         │              cost_timeline (Obj|null)      │                │
│         ├────────────────────────────────────────────┤                │
│         │ fy_period: {start, end}                    │                │
│         │ incoming_cost: {plan, actual}              │                │
│         │ weekly_costs: [WeeklyCost, ...]            │                │
│         │ summary: {totals}                          │                │
│         └────────────────────────────────────────────┘                │
│                                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Entities

### 2.1 Task (Root Entity)

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| uid | integer | XML Task/UID | Unique identifier |
| id | integer | XML Task/ID | Sequential ID |
| wbs | string | XML Task/WBS | Work Breakdown Structure |
| outline_number | string | XML Task/OutlineNumber | Human-readable (1.2.3) |
| name | string | XML Task/Name | Task name |
| parent_wbs | string\|null | Derived | Parent WBS (remove last segment) |
| is_summary | boolean | XML Task/Summary | True if parent |
| is_milestone | boolean | XML Task/Milestone | True if milestone |
| dates | Dates | Derived | Date information |
| attributes | Attributes\|null | Enrichment | Task attributes |
| progress | Progress\|null | XML | Completion status |
| cost_plan_total | number\|null | XML Task/FixedCost | Total planned cost |
| cost_timeline | CostTimeline\|null | Calculated | Weekly cost breakdown |

### 2.2 Dates

| Field | Type | Description |
|-------|------|-------------|
| plan | DateRange | Planned dates from schedule |
| manual | DateRange | Manually entered dates |
| sprint | DateRange\|null | Sprint schedule dates |
| actual | DateRange\|null | Actual work dates |

### 2.3 DateRange

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| start | string\|null | Various | Start date (YYYY-MM-DD) |
| end | string\|null | Various | End date (YYYY-MM-DD) |
| duration_days | number\|null | Calculated | Duration in calendar days |

### 2.4 Attributes

| Field | Type | Source | Enum Values |
|-------|------|--------|-------------|
| project_name | string | Filename | See Project List |
| zone | string | Lookup | MZ, NZ, SZ, WEZ |
| region | string | Lookup | MZ1, NZ1, NZ2, SZ1, SZ2, Kolkata |
| tower | string\|null | Hierarchy | Project-specific |
| floor | string\|null | Hierarchy | Project-specific |
| main_category | string | LLM | Civil Works-RCC, MEP, Finishing, Infra |
| sub_category | string | LLM | RCC, Tower MEP, etc. |
| trade_type | string | LLM | See Trade Types |
| slab_works | string | LLM | Typical, Non-typical, Non-slab |

### 2.5 Progress

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| percent_complete | integer | XML PercentComplete | 0-100 |
| is_complete | boolean | Derived | True if percent_complete == 100 |

### 2.6 CostTimeline

| Field | Type | Description |
|-------|------|-------------|
| fy_period | FYPeriod | Financial year bounds |
| incoming_cost | IncomingCost | Cost before FY start |
| weekly_costs | WeeklyCost[] | Weekly breakdown |
| summary | CostSummary | Aggregated totals |

### 2.7 WeeklyCost

| Field | Type | Description |
|-------|------|-------------|
| week_number | integer | Sequential week (1-based) |
| week_start | string | Monday (YYYY-MM-DD) |
| week_end | string | Sunday (YYYY-MM-DD) |
| days_in_task | {plan, actual} | Days overlapping with task |
| plan | CostEntry | Plan cost for week |
| actual | CostEntry | Actual cost for week |

### 2.8 CostEntry

| Field | Type | Description |
|-------|------|-------------|
| cost | number | Cost for this period |
| accumulated | number | Running total |

---

## 3. Task Type Rules

### 3.1 Classification

Task type is determined by the `is_summary` and `is_milestone` boolean flags in the XML source:

```
is_summary == true  →  type = "parent"
is_milestone == true →  type = "milestone"
otherwise           →  type = "leaf"
```

**Note**: While task type is not explicitly stored as a separate field in the Master JSON schema, it can be derived from these two flags using the logic above. The helper function `determine_task_type(is_summary: bool, is_milestone: bool)` is available in `task_schema.py` for this purpose.

### 3.2 Nullability by Type

| Field | Parent | Milestone | Leaf |
|-------|--------|-----------|------|
| dates.plan | Object | Object | Object |
| dates.manual | Object | Object | Object |
| dates.sprint | null | null | Object\|null |
| dates.actual | null | Object\|null | Object\|null |
| attributes | null | null | Object |
| progress | null | Object | Object |
| cost_plan_total | null | 0 | Number |
| cost_timeline | null | null | Object\|null |

---

## 4. Enumerated Values

### 4.1 Projects

```
Horizon, Reserve, Avenue 11, Miraya, Aristocrat, Zenith,
Tropical Isle, Jardinia, Sec. 44, Noida, Ramaiah,
Woodscapes, RGA 2, BL Saha
```

### 4.2 Zones

```
MZ    - Maharashtra Zone
NZ    - North Zone
SZ    - South Zone
WEZ   - West & East Zone
```

### 4.3 Regions

```
MZ1     - Maharashtra Region 1
NZ1     - North Region 1
NZ2     - North Region 2
SZ1     - South Region 1
SZ2     - South Region 2
Kolkata - Kolkata Region
```

### 4.4 Main Categories

```
Civil Works- RCC    - Structural concrete work
MEP                 - Mechanical, Electrical, Plumbing
Finishing           - Interior and exterior finishing
Infra               - Infrastructure and site work
```

### 4.5 Sub-Categories

| Main Category | Sub-Categories |
|---------------|----------------|
| Civil Works- RCC | RCC |
| MEP | Tower MEP, Common area-MEP, External-MEP |
| Finishing | Tower Civil Finishes, Tower Finishing, Common area finishes, External |
| Infra | Infra |

### 4.6 Trade Types (42 Unique Types, 81 Activity Mappings)

Complete list from `trade-type-cheat-sheet.md`. The cheat sheet contains 81 activity-to-trade-type mappings across 42 unique trade types:

**Civil Works - RCC (6 trade types)**:
| Trade Type | Example Activities |
|------------|-------------------|
| Reinforcement | Reinforcement |
| Shuttering- Conventional | Shuttering- conventional |
| Shuttering- AL | Shuttering- Aluform |
| Concreting | Concreting |
| Post Pour | Post pour |
| NTA RCC | RCC works (Non-Tower Area) |

**Tower MEP (4 trade types)**:
| Trade Type | Example Activities |
|------------|-------------------|
| Electrical | Concealed Electrical, Electrical wiring & switches |
| Plumbing | Concealed Plumbing for Toilets & Kitchen |
| CP Sanitary | CP sanitaryware Fixing |

**Tower Civil Finishes (5 trade types)**:
| Trade Type | Example Activities |
|------------|-------------------|
| Blockwork | Internal Block Work |
| Railing | Balcony Railing |
| Waterproofing | Toilet & Kitchen WP - Primer, Basecoat |
| Int Plaster | Internal Plaster |

**Tower Finishing (7 trade types)**:
| Trade Type | Example Activities |
|------------|-------------------|
| Door | Door Frame Fixing, Main Door, Internal Door, Aluminium Door |
| Window | Aluminium Windows/Shutters |
| Flooring | Dado, Flat Flooring Tiles, Toilet Flooring, IPS, Wooden Flooring |
| Paint | Putty, Primer coat, 1st Coat, 2nd Coat |
| False Ceiling | False Ceiling |
| Ext Plaster | External Plaster |
| Ext Paint | External Painting |

**Common Area Finishes - CA (7 trade types)**:
| Trade Type | Example Activities |
|------------|-------------------|
| CA-Blockwork | Blockwork, Lift Shaft Blockwork |
| CA-Railing | Staircase Railing Fixing |
| CA-Flooring | Staircase Flooring, Flooring Work |
| CA-Door | Fire Door Work |
| CA-Int Plaster | Ceiling & Wall POP |
| CA-Paint | Ceiling & Wall Paint |

**Common Area MEP - CA (5 trade types)**:
| Trade Type | Example Activities |
|------------|-------------------|
| CA-Electrical | Electrical Wiring Work |
| CA-PHE | Internal Drainage, Water Supply, Testing & Commissioning |
| CA-Fire-fighting & FAPA | Fire Fighting Work, Fire Alarm & PA, Rising Main |
| CA-HVAC | HVAC |
| Lift | Lift Architrave Work, Lift installation |

**External MEP (3 trade types)**:
| Trade Type | Example Activities |
|------------|-------------------|
| Ext Electrical | Cables, Mains, LV systems, Inverter, Light fixtures, DG, Substation |
| Ext Fire fighting & FAPA | External FF, FAPA |
| Ext PHE | External Plumbing/Sewerage/Drain/Water Supply/Irrigation |

**BRM-Security (1 trade type)**:
| Trade Type | Example Activities |
|------------|-------------------|
| BRM-Security | Security systems, BRM, Boom Barrier, Gate, CCTV |

**External Infrastructure (5 trade types)**:
| Trade Type | Example Activities |
|------------|-------------------|
| STP | STP Electro Mechanical |
| OWC | OWC |
| WTP | Water Treatment Plant |
| Solar | Solar related activities |
| Ext Infra | Other Infra Works, Softscape, Hardscape, Road, Landscape, Boundary Wall |

**Miscellaneous (2 trade types)**:
| Trade Type | Example Activities |
|------------|-------------------|
| Misc | Handover Activity Completion |
| NTA Finishing | NTA Finishing works |

### 4.7 Slab Works Classification

```
Typical      - Standard floor slab construction
Non-typical  - Non-standard slab work (podium, transfer, etc.)
Non-slab     - Non-slab related work (MEP, finishing, etc.)
```

### 4.8 Trade Type Enrichment Process

Trade type classification uses an LLM-based approach:

1. **Unique Activity Extraction** (`trade_type_extractor.py`)
   - Extract ~50-150 unique activities per project
   - Detect spatial leaves (Floor X, Tower Y) and traverse to parent
   - Determine context type: tower, common_area, external, infrastructure

2. **LLM Classification** (`trade_type_classifier.py`)
   - Model: Gemini Flash 2.5 via OpenRouter
   - Reference: `trade-type-cheat-sheet.md` (81 activity mappings → 42 trade types)
   - One API call per project (~$0.002/project)

3. **Task Mapping** (`trade_type_mapper.py`)
   - Map classifications back to individual tasks
   - Match by activity_name + context_type
   - Apply main_category, sub_category, trade_type, slab_works

**Context Type Indicators**:
| Context | Indicators |
|---------|------------|
| tower | Has tower attribute, floor attribute, "flat", "unit" |
| common_area | "staircase", "lift", "common", "lobby", "corridor" |
| external | "external", "site", "boundary", "road", "landscape" |
| infrastructure | "STP", "WTP", "DG", "substation", "solar" |

---

## 5. XML Field Mapping

### 5.1 Direct Mappings

| JSON Field | XML Path | Transformation |
|------------|----------|----------------|
| uid | Task/UID | parse_int |
| id | Task/ID | parse_int |
| wbs | Task/WBS | as-is |
| outline_number | Task/OutlineNumber | as-is |
| name | Task/Name | as-is |
| is_summary | Task/Summary | boolean_from_string |
| is_milestone | Task/Milestone | boolean_from_string |
| dates.plan.start | Task/Start | extract_date |
| dates.plan.end | Task/Finish | extract_date |
| dates.plan.duration_days | Task/Duration | iso8601_to_days |
| dates.manual.start | Task/ManualStart | extract_date |
| dates.manual.end | Task/ManualFinish | extract_date |
| dates.manual.duration_days | Task/ManualDuration | iso8601_to_days |
| progress.percent_complete | Task/PercentComplete | parse_int |
| cost_plan_total | Task/FixedCost | parse_float |

### 5.2 Derived Fields

| JSON Field | Source | Logic |
|------------|--------|-------|
| parent_wbs | wbs | Remove last segment |
| progress.is_complete | percent_complete | == 100 |
| dates.actual.start | TimephasedData | Earliest Type=2 Start |
| dates.actual.end | TimephasedData | Latest Type=2 Finish |
| dates.actual.duration_days | actual dates | Calendar days |

### 5.3 Enriched Fields

| JSON Field | Source | Method |
|------------|--------|--------|
| attributes.project_name | Filename | Alias lookup |
| attributes.zone | Project | Zone map lookup |
| attributes.region | Project | Region map lookup |
| attributes.tower | Hierarchy | Pattern extraction |
| attributes.floor | Hierarchy | Pattern extraction |
| attributes.main_category | Task name | LLM classification |
| attributes.sub_category | Task name | LLM classification |
| attributes.trade_type | Task name | LLM classification |
| attributes.slab_works | Task name | LLM classification |
| dates.sprint.* | Sprint XML | outline_number match |

---

## 6. Cost Timeline Calculations

### 6.1 Plan Cost Rate

```
plan_rate = cost_plan_total / dates.plan.duration_days
plan_cost_week = plan_rate * days_in_task.plan
```

### 6.2 Actual Cost Rate

```
if is_complete and dates.actual.duration_days > 0:
    actual_rate = cost_plan_total / dates.actual.duration_days
else:
    actual_rate = plan_rate  # Incomplete tasks use plan rate

actual_cost_week = actual_rate * days_in_task.actual
```

**Note for Incomplete Tasks**:
- When a task is incomplete (`is_complete = false`), the actual cost uses the plan daily rate
- If actual dates are not available but task is in progress, `days_in_task.actual` defaults to `days_in_task.plan`

### 6.3 Incoming Cost

```
if dates.plan.start < FY_START:
    days_before = (FY_START - dates.plan.start).days
    incoming_plan = plan_rate * days_before

if dates.actual.start and dates.actual.start < FY_START:
    days_before = (FY_START - dates.actual.start).days
    incoming_actual = actual_rate * days_before
```

### 6.4 Summary Calculations

```
summary.plan_cost_in_fy = sum(weekly_costs[*].plan.cost)
summary.actual_cost_in_fy = sum(weekly_costs[*].actual.cost)
summary.plan_cost_before_fy = incoming_cost.plan.cost
summary.actual_cost_before_fy = incoming_cost.actual.cost
summary.total_weeks_in_fy = len(weekly_costs)
```

---

## 7. Validation Rules

### 7.1 Schema Validation

- All required fields present
- Types match schema definition
- Enum values valid
- Patterns match (wbs, dates)

### 7.2 Business Rules

| Rule | Validation |
|------|------------|
| VR-001 | plan.start <= plan.end |
| VR-002 | duration_days >= 0 |
| VR-003 | 0 <= percent_complete <= 100 |
| VR-004 | cost_plan_total >= 0 |
| VR-005 | Parent tasks have null cost_timeline |
| VR-006 | Leaf tasks have non-null attributes |
| VR-007 | Accumulated cost is monotonically increasing |

### 7.3 Cross-Field Validation

```
# Duration consistency
if plan.start and plan.end and plan.duration_days:
    calculated = (plan.end - plan.start).days
    assert abs(calculated - duration_days) < 2  # 1-day tolerance

# Cost timeline consistency
if cost_timeline:
    sum_weekly = sum(w.plan.cost for w in weekly_costs)
    assert abs(sum_weekly - summary.plan_cost_in_fy) < 0.01
```

---

## 8. Sample Data

### 8.1 Leaf Task

```json
{
  "uid": 51912,
  "id": 2501,
  "wbs": "37300.37500.51900",
  "outline_number": "2.7.3.5.1.4.13",
  "name": "Block Work Ground Floor",
  "parent_wbs": "37300.37500",
  "is_summary": false,
  "is_milestone": false,
  "dates": {
    "plan": {
      "start": "2025-04-15",
      "end": "2025-05-20",
      "duration_days": 35
    },
    "manual": {
      "start": "2025-04-15",
      "end": "2025-05-20",
      "duration_days": 35
    },
    "sprint": {
      "start": "2025-04-10",
      "end": "2025-05-10",
      "duration_days": 30
    },
    "actual": {
      "start": "2025-04-18",
      "end": null,
      "duration_days": null
    }
  },
  "attributes": {
    "project_name": "Miraya",
    "zone": "NZ",
    "region": "NZ1",
    "tower": "Tower 1",
    "floor": "Ground Floor",
    "main_category": "Finishing",
    "sub_category": "Tower Civil Finishes",
    "trade_type": "Blockwork",
    "slab_works": "Non-slab"
  },
  "progress": {
    "percent_complete": 45,
    "is_complete": false
  },
  "cost_plan_total": 125000.00,
  "cost_timeline": {
    "fy_period": {
      "start": "2025-04-01",
      "end": "2026-03-31"
    },
    "incoming_cost": {
      "plan": {"days_before_fy": 0, "cost": 0},
      "actual": {"days_before_fy": 0, "cost": 0}
    },
    "weekly_costs": [
      {
        "week_number": 1,
        "week_start": "2025-04-14",
        "week_end": "2025-04-20",
        "days_in_task": {"plan": 5, "actual": 2},
        "plan": {"cost": 17857.14, "accumulated": 17857.14},
        "actual": {"cost": 7142.86, "accumulated": 7142.86}
      }
    ],
    "summary": {
      "total_weeks_in_fy": 6,
      "plan_cost_in_fy": 125000.00,
      "actual_cost_in_fy": 56250.00,
      "plan_cost_before_fy": 0,
      "actual_cost_before_fy": 0
    }
  }
}
```

### 8.2 Parent Task

```json
{
  "uid": 37500,
  "id": 150,
  "wbs": "37300.37500",
  "outline_number": "2.7.3.5",
  "name": "Tower 1 Finishing",
  "parent_wbs": "37300",
  "is_summary": true,
  "is_milestone": false,
  "dates": {
    "plan": {
      "start": "2025-04-01",
      "end": "2026-01-15",
      "duration_days": 290
    },
    "manual": {
      "start": "2025-04-01",
      "end": "2026-01-15",
      "duration_days": 290
    },
    "sprint": null,
    "actual": null
  },
  "attributes": null,
  "progress": null,
  "cost_plan_total": null,
  "cost_timeline": null
}
```

### 8.3 Milestone

```json
{
  "uid": 99001,
  "id": 5000,
  "wbs": "37300.99000",
  "outline_number": "2.7.3.99",
  "name": "Tower 1 Handover",
  "parent_wbs": "37300",
  "is_summary": false,
  "is_milestone": true,
  "dates": {
    "plan": {
      "start": "2026-01-15",
      "end": "2026-01-15",
      "duration_days": 0
    },
    "manual": {
      "start": "2026-01-15",
      "end": "2026-01-15",
      "duration_days": 0
    },
    "sprint": null,
    "actual": {
      "start": null,
      "end": null,
      "duration_days": null
    }
  },
  "attributes": null,
  "progress": {
    "percent_complete": 0,
    "is_complete": false
  },
  "cost_plan_total": 0,
  "cost_timeline": null
}
```
