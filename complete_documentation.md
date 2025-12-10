# Microsoft Project XML Data - Complete Documentation

**Version**: 2.0 (Comprehensive Merged Documentation)
**Date**: 2025-12-08
**Source**: Asta Powerproject XML Export (Miraya.xml, 4.4 MB)
**Project**: Miraya | Sec 43 Construction Schedule (2025-2031, ~6 years)

---

## Table of Contents

1. [Overview](#overview)
2. [Target JSON Schema](#target-json-schema)
3. [XML File Structure](#xml-file-structure)
4. [Field Definitions Reference](#field-definitions-reference)
5. [WBS Explained](#wbs-explained)
6. [Detailed Q&A](#detailed-qa)
7. [ETL Pipeline Recommendations](#etl-pipeline-recommendations)
8. [Common Use Cases](#common-use-cases)
9. [Quick Reference Tables](#quick-reference-tables)

---

## Overview

### Project Statistics

- **Total Tasks**: 2,849 (including 4 milestones)
- **Assignments**: 64
- **Resources**: 5
- **Calendars**: 25
- **Project Duration**: 2025-12-02 to 2031-09-17 (~6 years)
- **File Size**: 4.4 MB
- **Format**: Microsoft Project XML (MSPDI)

### What This Data Contains

**Complete:**
- ✓ Task structure and hierarchy
- ✓ Planned dates and durations
- ✓ 4 project milestones (key events)
- ✓ Dependencies (though may not be active)
- ✓ Calendars with exceptions
- ✓ Some work tracking (TimephasedData)
- ✓ Custom fields (Extended Attributes)

**Limited:**
- ⚠️ Resource details (only 5 resources, mostly ResourceUID=-65535)
- ⚠️ No ActualStart/ActualFinish fields
- ⚠️ Dependencies may be informational only
- ⚠️ Cost tracking is aggregate (FixedCost), not detailed

**Missing:**
- ✗ Detailed resource loading/leveling
- ✗ Resource skill sets or rates
- ✗ Earned value metrics
- ✗ Risk or issue tracking

---

## Target JSON Schema

This section documents the **ETL output structure** - the target JSON format for CCO Dashboard analysis. For full schema details, see `task_schema.json`.

### Field Order

```
Task Object
├── uid                    (integer) - XML Task/UID
├── id                     (integer) - XML Task/ID
├── wbs                    (string) - XML Task/WBS
├── outline_number         (string) - XML Task/OutlineNumber
├── name                   (string) - XML Task/Name
├── parent_wbs             (string|null) - DERIVED: WBS with last segment removed
├── is_summary             (boolean) - XML Summary='1'
├── is_milestone           (boolean) - XML Milestone='1'
├── dates
│   ├── plan {start, end, duration_days}
│   ├── manual {start, end, duration_days}
│   ├── sprint {start, end, duration_days}    ← From separate sprint XML
│   └── actual {start, end, duration_days}    ← From TimephasedData Type=2
├── attributes             (object|null) - From EXTERNAL master data
├── progress               (object|null) - {percent_complete, is_complete}
├── cost_plan_total        (number|null) - XML FixedCost
└── cost_timeline          (object|null) - Weekly cost breakdown for FY 2025-26
```

### Task Types and Null Fields

| Field | Parent (is_summary=true) | Leaf Task | Milestone |
|-------|--------------------------|-----------|-----------|
| dates.plan | ✅ values | ✅ values | ✅ values (0 duration) |
| dates.actual | null | ✅ from TimephasedData | ✅ from ActualStart/Finish |
| attributes | null | ✅ from master data | null |
| progress | null | ✅ values | ✅ values |
| cost_plan_total | null | ✅ values | 0 |
| cost_timeline | null | ✅ calculated | null |

### Attributes (From External Master Data)

Attributes are NOT extracted from XML ExtendedAttributes. They come from external master data lookup by WBS.

| Attribute | Allowed Values |
|-----------|----------------|
| project_name | Horizon, Reserve, Avenue 11, Miraya, Aristocrat, Zenith, Tropical Isle, Jardinia, Sec. 44 Noida, Ramaiah, Woodscapes, RGA 2, BL Saha |
| zone | MZ, NZ, SZ, WEZ |
| region | MZ1, NZ1, NZ2, SZ2, SZ1, Kolkata |
| main_category | Civil Works- RCC, MEP, Finishing, Infra |
| sub_category | RCC, Tower MEP, Tower Civil Finishes, Tower Finishing, Common area finishes, Common area-MEP, Ext MEP, BRM-Security, Miscellaneous, Ext Infra, NTA RCC |
| trade_type | Reinforcement, Shuttering- Conventional, Shuttering- AL, Electrical, Concreting, Post Pour, Blockwork, Railing, Waterproofing, Plumbing, Door, Int Plaster, Paint, Flooring, False Ceiling, CA-Blockwork, Lift, CA-Railing, CA-Flooring, CA-Door, CA-Electrical, CA-Int Plaster, CA-Paint, CA-PHE, CA-Fire-fighting & FAPA, CA-HVAC, Ext Electrical, BRM-Security, Ext Fire fighting & FAPA, Ext PHE, Ext Paint, CP Sanitary, Misc, Ext Plaster, STP, OWC, WTP, Solar, Ext Infra, NTA RCC, NTA Finishing |
| slab_works | Typical, Non-typical, Non-slab |
| tower | Project-specific (e.g., 'Tower 1', 'Tower A') |
| floor | Project-specific (e.g., 'Floor 1', 'GF', 'B1') |

### Cost Timeline Structure (FY 2025-26)

Weekly cost breakdown for financial year April 1, 2025 to March 31, 2026.

```json
{
  "cost_timeline": {
    "fy_period": {
      "start": "2025-04-01",
      "end": "2026-03-31"
    },
    "incoming_cost": {
      "plan": {"days_before_fy": 17, "cost": 180851.06},
      "actual": {"days_before_fy": 14, "cost": 142857.14}
    },
    "weekly_costs": [
      {
        "week_number": 1,
        "week_start": "2025-03-31",
        "week_end": "2025-04-06",
        "days_in_task": {"plan": 6, "actual": 6},
        "plan": {"cost": 63829.79, "accumulated": 244680.85},
        "actual": {"cost": 61224.49, "accumulated": 204081.63}
      }
    ],
    "summary": {
      "total_weeks_in_fy": 8,
      "plan_cost_in_fy": 531914.93,
      "actual_cost_in_fy": 561224.48,
      "plan_cost_before_fy": 180851.06,
      "actual_cost_before_fy": 142857.14
    }
  }
}
```

**Calculation Rules:**

| Scenario | Plan Cost Formula | Actual Cost Formula |
|----------|-------------------|---------------------|
| Incoming (before FY) | cost_plan_total / duration_plan_days × days_before_fy | cost_plan_total / duration_actual_days × actual_days_before_fy |
| Weekly (full week) | cost_plan_total / duration_plan_days × 7 | If complete: cost_plan_total / duration_actual_days × 7. If incomplete: use plan rate |
| Weekly (partial week) | Prorated to days in task | Prorated to days in task |

**Validation Rule:** Sum of weekly actual costs should equal `percent_complete × cost_plan_total`.

### Dates Derivation

| Date Field | Source | Notes |
|------------|--------|-------|
| dates.plan.start | XML Start | Extract date from datetime |
| dates.plan.end | XML Finish | Extract date from datetime |
| dates.plan.duration_days | XML Duration | Convert PT{hours}H0M0S ÷ 8 |
| dates.manual.* | XML ManualStart/ManualFinish/ManualDuration | Same conversions |
| dates.sprint.* | Separate sprint XML files | Null in baseline ETL |
| dates.actual.start (leaf) | TimephasedData Type=2 | Earliest entry with Value > 0 |
| dates.actual.end (leaf) | TimephasedData Type=2 | Latest entry with Value > 0 |
| dates.actual.* (milestone) | XML ActualStart/ActualFinish | Only 5/12 files have these |

### Fields NOT in Target Schema (Excluded from XML)

These XML fields are deliberately excluded from the target JSON:

| XML Field | Reason |
|-----------|--------|
| Type | All tasks use Type 0 (Fixed Units) - no variation |
| IsNull | Internal MS Project flag |
| OutlineLevel | Derivable from WBS depth |
| DurationFormat | Handled during conversion |
| Resume, ResumeValid | Internal scheduling fields |
| Critical | Variable, can be recalculated |
| FixedCostAccrual | Not needed for cost timeline |
| ConstraintType, ConstraintDate | Scheduling constraints not needed |
| CalendarUID | Calendar reference not needed in flat output |
| ExtendedAttribute | Attributes from external master data |
| PredecessorLink | Dependencies handled separately if needed |

### Sample Objects

See `sample_tasks.json` for complete examples of:
1. **Parent element** - Summary task with null attributes, progress, cost
2. **Leaf element** - Work task with full cost timeline and attributes
3. **Milestone element** - Zero duration event with progress but no cost timeline

---

## XML File Structure

### Physical Organization

The XML file has a **flat, linear structure** with **6 main sections** in sequential order:

```
<Project xmlns="http://schemas.microsoft.com/project">
  ├─ 1. PROJECT METADATA (21 fields)
  ├─ 2. DEFINITIONS (2 sections: OutlineCodes, ExtendedAttributes)
  ├─ 3. CALENDARS (25 items)
  ├─ 4. TASKS (2,849 items) ⭐ LARGEST SECTION - 80% of file
  ├─ 5. RESOURCES (5 items)
  └─ 6. ASSIGNMENTS (64 items)
</Project>
```

### Section 1: Project Metadata (Lines 1-21)

Project-level settings and configuration:

```xml
<Project xmlns="http://schemas.microsoft.com/project">
  <Name>Untitled</Name>
  <Title>Untitled</Title>
  <Author>Sameer Gupta</Author>
  <ScheduleFromStart>1</ScheduleFromStart>
  <StartDate>2025-12-02T00:00:00</StartDate>
  <FinishDate>2031-09-17T17:00:00</FinishDate>
  <CurrencySymbol>£</CurrencySymbol>
  <MinutesPerDay>480</MinutesPerDay>  <!-- 8 hours -->
  <MinutesPerWeek>2400</MinutesPerWeek>  <!-- 40 hours -->
  <CalendarUID>1</CalendarUID>
  ...
</Project>
```

**Key Settings:**
- Working time: 480 min/day (8 hours), 2400 min/week (40 hours)
- Currency: £ (British Pounds)
- Schedule direction: Forward scheduled (from start date)

### Section 2: Definitions (Lines 22-23)

Lookup tables and custom field definitions:

**2A. OutlineCodes** (1 item)
- Defines custom WBS coding scheme (APP_WBS)
- FieldID: 188744096

**2B. ExtendedAttributes** (3 items)

1. **Buffer_Task** (Flag1, FieldID: 188743752)
   - Boolean flag identifying buffer/contingency tasks

2. **Unique_Task_ID** (Text1, FieldID: 188743731)
   - Custom task identifier from original planning system

3. **APP_WBS** (Outline Code1, FieldID: 188744096)
   - Custom WBS coding system

**Important**: Parse these definitions FIRST to understand custom fields when you encounter them in tasks.

### Section 3: Calendars (25 items, ~500 KB)

Working time definitions including:
- Standard working hours (8am-12pm, 1pm-5pm, Monday-Saturday)
- Exceptions and holidays
- Non-working periods (monsoon season: Nov 2-29, 2025)

**Key Calendars:**
- "Standard" (UID 1)
- "Sector 43" (UID 20) - Used by task 188
- "Yashwantpur Finshing" (UID 18)
- Plus 22 more calendars

### Section 4: Tasks (2,849 items, ~3.5 MB - 80% of file)

**Structure:**

```xml
<Tasks>
  <!-- All 2,849 tasks are sequential children of <Tasks> -->

  <!-- Summary Task -->
  <Task>
    <UID>31</UID>
    <Name>Miraya | Sec 43</Name>
    <Summary>1</Summary>  <!-- Parent task -->
    <OutlineLevel>1</OutlineLevel>
    ...
  </Task>

  <!-- Milestone -->
  <Task>
    <UID>35</UID>
    <Name>Start of project</Name>
    <Milestone>1</Milestone>
    <Duration>PT0H0M0S</Duration>  <!-- Zero duration -->
    ...
  </Task>

  <!-- Regular Task with Dependency -->
  <Task>
    <UID>188</UID>
    <Name>Excavation for isolated fottings of NTA</Name>
    <Summary>0</Summary>  <!-- Leaf task -->
    <PredecessorLink>  <!-- ⭐ EMBEDDED HERE -->
      <PredecessorUID>477</PredecessorUID>
      <Type>1</Type>  <!-- Finish-to-Start -->
      <LinkLag>-475200</LinkLag>
    </PredecessorLink>
    ...
  </Task>
</Tasks>
```

**Key Points:**
- All tasks in ONE block (not grouped by level/phase)
- Dependencies are **embedded** in each task
- Milestones are tasks with `Milestone=1` and `Duration=PT0H0M0S`
- Hierarchy via `OutlineLevel` field
- **89% of tasks** (2,525/2,849) have dependencies

### Section 5: Resources (5 items, ~2 KB)

People, equipment, materials:

```xml
<Resources>
  <Resource>
    <UID>27</UID>
    <Name>Zenith</Name>
    <Type>0</Type>  <!-- 0=Work, 1=Material, 2=Cost -->
    <IsCostResource>1</IsCostResource>
    <CalendarUID>28</CalendarUID>
    ...
  </Resource>
</Resources>
```

**Note**: Only 5 resources for 2,849 tasks = very high-level resource tracking

### Section 6: Assignments (64 items, ~400 KB)

Links tasks to resources:

```xml
<Assignments>
  <Assignment>
    <UID>190</UID>
    <TaskUID>188</TaskUID>  <!-- Links to Task.UID -->
    <ResourceUID>-65535</ResourceUID>  <!-- -65535 = unassigned/cost -->

    <Work>PT960H0M0S</Work>
    <ActualWork>PT136H0M0S</ActualWork>
    <RemainingWork>PT824H0M0S</RemainingWork>

    <!-- ⭐ TIMEPHASED DATA EMBEDDED HERE -->
    <TimephasedData>
      <Type>1</Type>  <!-- 1=Planned work -->
      <Start>2025-11-30T08:00:00</Start>
      <Finish>2025-11-30T17:00:00</Finish>
      <Value>PT8H0M0S</Value>
    </TimephasedData>

    <TimephasedData>
      <Type>2</Type>  <!-- 2=Actual work -->
      <Start>2025-07-13T08:00:00</Start>
      <Value>PT8H0M0S</Value>
    </TimephasedData>

    <!-- 100+ more TimephasedData entries -->
  </Assignment>
</Assignments>
```

**Key Points:**
- Each assignment contains 100+ timephased entries
- Most use ResourceUID=-65535 (cost/material without detailed tracking)
- 1:1 task-to-assignment ratio in this dataset

### Data Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                        <Project>                            │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌────────┐         ┌─────────┐         ┌────────────┐
    │Calendar│◄────┐   │  Task   │         │  Resource  │
    │(UID:1) │     │   │(UID:188)│         │ (UID:27)   │
    └────────┘     │   └─────────┘         └────────────┘
                   │        │                      │
                   │        │    ┌─────────────────┘
                   │        │    │
                   │        ▼    ▼
                   │   ┌──────────────┐
                   └───┤  Assignment  │
                       │  (UID:190)   │
                       └──────────────┘
                            │
                            │ contains
                            ▼
                    ┌───────────────┐
                    │ TimephasedData│ (100+ entries)
                    └───────────────┘

Dependencies:
Task ──PredecessorLink──> Task
(UID:188)  references    (UID:477)
```

### Important Structural Facts

**✅ What IS in Separate Sections:**
1. Calendars
2. Tasks
3. Resources
4. Assignments

**❌ What is NOT in Separate Sections (EMBEDDED):**
1. Dependencies - Embedded in tasks as `<PredecessorLink>`
2. Milestones - Just tasks with `Milestone=1`
3. TimephasedData - Embedded in assignments (100+ per assignment)
4. Extended attribute values - Embedded in tasks
5. Calendar exceptions - Embedded in calendars

### File Size Breakdown

| Section | Size | % of Total | Item Count |
|---------|------|-----------|------------|
| Metadata | ~5 KB | <1% | 21 fields |
| Definitions | ~2 KB | <1% | 4 items |
| Calendars | ~500 KB | 11% | 25 items |
| **Tasks** | **~3.5 MB** | **80%** | **2,849 items** |
| Resources | ~2 KB | <1% | 5 items |
| Assignments | ~400 KB | 9% | 64 items |
| **Total** | **~4.4 MB** | **100%** | |

---

## Field Definitions Reference

### Task Fields

#### Identifiers

| Field | Type | Description | Example | Notes |
|-------|------|-------------|---------|-------|
| `UID` | Integer | Unique identifier for the task | `188` | Can change between exports |
| `ID` | Integer | Sequential ID (can change if reordered) | `77` | Not stable |
| `Name` | String | Task name/description | `"Excavation for isolated fottings of NTA"` | |
| `WBS` | String | Work Breakdown Structure code | `"37300.37500.51900.52300.64000.134100.232200"` | **Most stable identifier** |
| `OutlineNumber` | String | Outline position in hierarchy | `"1.1.3.1.1.1.1"` | Changes if reordered |
| `OutlineLevel` | Integer | Depth in hierarchy (1 = top) | `7` | Equals number of WBS segments |

**Identifier Comparison:**

| Field | Stable? | Meaningful? | Best For |
|-------|---------|-------------|----------|
| **UID** | ❌ Can change | ❌ No | Internal database joins |
| **WBS** | ✅ Never changes | ✅ Business/org codes | **Primary key, reporting, integration** |
| **OutlineNumber** | ❌ Changes | ❌ Position only | Display only |

#### Dates and Duration

| Field | Type | Description | Example | Notes |
|-------|------|-------------|---------|-------|
| `Start` | DateTime | Scheduled start date | `"2025-07-13T08:00:00"` | |
| `Finish` | DateTime | Scheduled finish date | `"2026-03-12T17:00:00"` | |
| `ManualStart` | DateTime | Manually entered start | `"2025-07-13T08:00:00"` | If Start=ManualStart, may be manually scheduled |
| `ManualFinish` | DateTime | Manually entered finish | `"2026-03-12T17:00:00"` | Won't auto-update when predecessors change |
| `Duration` | ISO 8601 | Task duration | `"PT960H0M0S"` | 960 hours = 120 days |
| `Resume` | DateTime | Date work resumes after split | `"2025-11-30T08:00:00"` | After calendar exception or manual pause |
| `ResumeValid` | Boolean | Whether Resume date is valid | `"1"` | Task currently split/paused |
| `ActualStart` | DateTime | **NOT IN THIS EXPORT** | - | Derive from TimephasedData Type=2 |
| `ActualFinish` | DateTime | **NOT IN THIS EXPORT** | - | Would appear when 100% complete |

**Duration Format Values:**
- `3` = Minutes, `4` = Hours, `5` = Days, `6` = Weeks, `7` = Days (default), `8` = Months

**ISO 8601 Duration Examples:**
- `PT960H0M0S` = 960 hours
- `PT8H0M0S` = 8 hours
- `PT0H0M0S` = Zero duration (milestone)

#### Status and Type

| Field | Type | Description | Values | Notes |
|-------|------|-------------|--------|-------|
| `Type` | Integer | Task type (controls recalculation) | `0`, `1`, `2` | **All 2,849 tasks are Type 0** |
| `Summary` | Boolean | Parent task with children | `0` (leaf), `1` (parent) | |
| `Milestone` | Boolean | Zero duration marker event | `0`, `1` | **4 milestones found** (0.14%) |
| `Critical` | Boolean | On critical path | `0`, `1` | |
| `PercentComplete` | Integer | Duration completion (0-100) | `14` | **Duration-based**, not work-based |

**Task Types:**

| Value | Type | Behavior | Formula | Use Case |
|-------|------|----------|---------|----------|
| `0` | Fixed Units | Resources stay constant | Work = Duration × Units | "1 excavator, regardless of time" |
| `1` | Fixed Duration | Time stays constant | Duration fixed, Units adjust | "28 days concrete curing" |
| `2` | Fixed Work | Effort stays constant | Work fixed, Duration adjusts | "1000 m³ to excavate" |

#### Constraints

| Field | Type | Description | Example | Warning |
|-------|------|-------------|---------|---------|
| `ConstraintType` | Integer | Scheduling constraint | `4` (SNET) | **Constraints override dependencies!** |
| `ConstraintDate` | DateTime | Constraint date | `"2025-07-13T08:00:00"` | |
| `CalendarUID` | Integer | Task calendar reference | `20` | Links to Calendar.UID |

**Constraint Types:**

| Value | Code | Category | Description | Impact |
|-------|------|----------|-------------|--------|
| `0` | ASAP | Flexible | As Soon As Possible | No constraint |
| `1` | ALAP | Flexible | As Late As Possible | Backward schedule |
| `2` | MSO | **Inflexible** | Must Start On | **Locks start date** |
| `3` | MFO | **Inflexible** | Must Finish On | **Locks finish date** |
| `4` | SNET | Semi-flexible | Start No Earlier Than | Common in your data |
| `5` | SNLT | Semi-flexible | Start No Later Than | |
| `6` | FNET | Semi-flexible | Finish No Earlier Than | |
| `7` | FNLT | Semi-flexible | Finish No Later Than | |

**⚠️ CRITICAL**: When `ConstraintType > 0`, constraints take priority over dependencies. This is why dates may not auto-update when predecessors slip.

#### Costs

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `FixedCost` | Decimal | Fixed cost (project currency) | `216212400` (£216,212,400) |
| `FixedCostAccrual` | Integer | When costs accrue | `3` (Prorated) |

**Cost Accrual Values:**
- `1` = Start (cost incurred at task start)
- `2` = End (cost incurred at completion)
- `3` = Prorated (cost spread across duration)

### Assignment Fields

Assignments link Resources to Tasks, tracking work and progress.

#### Core Fields

| Field | Type | Description | Example | Notes |
|-------|------|-------------|---------|-------|
| `UID` | Integer | Assignment unique ID | `190` | Different from TaskUID |
| `TaskUID` | Integer | Reference to Task.UID | `188` | Multiple assignments can share TaskUID |
| `ResourceUID` | Integer | Reference to Resource.UID | `-65535` | **-65535 = unassigned/cost resource** |

**Special ResourceUID Values:**
- `-65535` = Unassigned resource or material/cost resource
- Positive numbers = Specific named resources

#### Work Tracking

| Field | Type | Description | Example | Formula |
|-------|------|-------------|---------|---------|
| `Work` | ISO 8601 | Total planned work | `"PT960H0M0S"` | ActualWork + RemainingWork |
| `ActualWork` | ISO 8601 | Work completed | `"PT136H0M0S"` | From timephased actual |
| `RemainingWork` | ISO 8601 | Work still needed | `"PT824H0M0S"` | Work - ActualWork |
| `RegularWork` | ISO 8601 | Non-overtime work | `"PT0H0M0S"` | |
| `OvertimeWork` | ISO 8601 | Overtime hours | `"PT0H0M0S"` | |

**Example:** 960 total hours = 136 actual + 824 remaining

#### Progress

| Field | Type | Description | Example | Difference |
|-------|------|-------------|---------|-----------|
| `PercentWorkComplete` | Integer | Work effort completion | `0` | **Work-based** (vs Task.PercentComplete) |

**Key Difference:**
- **Task.PercentComplete** (14%) = Duration elapsed (14% of time passed)
- **Assignment.PercentWorkComplete** (0%) = Work effort completed (0% of work done)

#### Scheduling

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Start` | DateTime | Assignment start | `"2025-07-13T08:00:00"` |
| `Finish` | DateTime | Assignment finish | `"2026-03-12T17:00:00"` |
| `Resume` | DateTime | Resume after interruption | `"2025-11-30T08:00:00"` |
| `Delay` | Integer | Delay before start (minutes) | `0` |

#### Resource Allocation

| Field | Type | Description | Example | Meaning |
|-------|------|-------------|---------|---------|
| `Units` | Decimal | Resource allocation | `1.0` | 1.0 = 100% = 1 full-time person |
| `HasFixedRateUnits` | Boolean | Units are fixed | `1` | |
| `FixedMaterial` | Boolean | Fixed material assignment | `0` | |

**Units Examples:**
- `1.0` = Full-time (100%)
- `0.5` = Half-time (50%)
- `2.0` = Two full-time resources (200%)

#### Timephased Data

Day-by-day work distribution:

| Field | Type | Description | Example | Notes |
|-------|------|-------------|---------|-------|
| `Type` | Integer | Data type | `1`, `2`, `3` | 1=Planned, 2=Actual, 3=Overtime |
| `UID` | Integer | Assignment UID reference | `190` | |
| `Start` | DateTime | Period start | `"2025-11-30T08:00:00"` | |
| `Finish` | DateTime | Period end | `"2025-11-30T17:00:00"` | |
| `Unit` | Integer | Time unit | `2` | 2=Hours, 3=Days |
| `Value` | ISO 8601 | Work amount | `"PT8H0M0S"` | PT0H0M0S = pause period |

**Timephased Types:**
- `1` = Planned/scheduled future work
- `2` = **Actual work completed** (use to derive ActualStart)
- `3` = Overtime work

**How to Derive Actual Start:**
Find earliest TimephasedData entry with `Type=2` and `Value > PT0H0M0S`

### Resource Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `UID` | Integer | Resource unique ID | `27` |
| `Name` | String | Resource name | `"Zenith"` |
| `Type` | Integer | Resource type | `0` (0=Work, 1=Material, 2=Cost) |
| `Initials` | String | Abbreviation | `"Z"` |
| `CalendarUID` | Integer | Resource calendar | `28` |
| `IsCostResource` | Boolean | Cost-only resource | `1` |
| `AccrueAt` | Integer | When costs accrue | `3` (1=Start, 2=End, 3=Prorated) |

### Calendar Fields

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `UID` | Integer | Calendar unique ID | Positive integer |
| `Name` | String | Calendar name | `"Sector 43"` |
| `IsBaseCalendar` | Boolean | Base calendar | `1` |
| `BaseCalendarUID` | Integer | Parent calendar | `-1` (none) |

#### WeekDays

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `DayType` | Integer | Day type | 0=Exception, 1=Sun, 2=Mon, ..., 7=Sat |
| `DayWorking` | Boolean | Working day | `1` (working), `0` (non-working) |

**Working Times:**
- `FromTime` / `ToTime`: `"08:00:00"` to `"12:00:00"`, `"13:00:00"` to `"17:00:00"`
- Total: 8 hours/day (4 morning + 4 afternoon)

**Time Period (Exceptions):**
- `FromDate` / `ToDate`: Specific date ranges (holidays, monsoon season)
- Example: Nov 2-29, 2025 (non-working period)

### Predecessor/Dependency Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `PredecessorUID` | Integer | Predecessor task UID | `477` |
| `Type` | Integer | Link type | `1` (Finish-to-Start) |
| `LinkLag` | Integer | Lag time in minutes | `-475200` (negative = lead) |
| `LagFormat` | Integer | Display format | `7` |

**Link Types:**

| Value | Type | Description |
|-------|------|-------------|
| `0` | FF | Finish-to-Finish |
| `1` | **FS** | **Finish-to-Start** (most common) |
| `2` | SS | Start-to-Start |
| `3` | SF | Start-to-Finish |

**Link Lag:**
- **Positive** = Lag (delay after predecessor)
- **Negative** = Lead (overlap before predecessor finishes)
- Example: `-475200` min = -330 days = task starts 330 days before predecessor finishes

**⚠️ Inactive Dependencies:**

Dependencies may be **informational only** (not controlling dates) when:
1. Tasks are manually scheduled (Start = ManualStart)
2. Constraints override dependencies (ConstraintType > 0)
3. Scheduling engine not set to auto-update

### Extended Attributes (Custom Fields)

**Field Definitions** (at project level):

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `FieldID` | String | Unique field ID | `"188743752"` |
| `FieldName` | String | Internal name | `"Flag1"` |
| `Alias` | String | User-friendly name | `"Buffer_Task"` |

**Field Values** (at task/resource level):

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `FieldID` | String | Reference to definition | `"188743752"` |
| `Value` | String | Field value | `"0"` |

**Custom Fields in This Project:**

1. **Buffer_Task** (Flag1, ID: 188743752)
   - Boolean flag
   - Identifies buffer/contingency tasks

2. **Unique_Task_ID** (Text1, ID: 188743731)
   - Text field
   - Custom identifier from original system

3. **APP_WBS** (Outline Code1, ID: 188744096)
   - Outline code
   - Custom WBS coding system

### Milestones

**Characteristics:**

| Property | Value | Why |
|----------|-------|-----|
| `Milestone` | `"1"` | Marks as milestone |
| `Duration` | `"PT0H0M0S"` | Zero duration (point in time) |
| `Start` = `Finish` | Same datetime | Single moment |

**Your Project's Milestones (4 total, 0.14% of tasks):**

1. **Start of project** - Nov 30, 2025
2. **Completion of project** - Sep 6, 2029
3. **Removal of soldier piles** - Mar 21, 2027
4. **Completion of Landscape works** - Oct 13, 2028

**How to Identify:**

```python
def is_milestone(task):
    return (
        task.get('Milestone') == '1' and
        task.get('Duration') == 'PT0H0M0S'
    )
```

---

## WBS Explained

### What is WBS?

**WBS codes are custom business/organizational identifiers**, NOT system-generated IDs. They represent your organization's cost code structure or project coding standard.

**Example:**
```
WBS: "37300.37500.51900.52300.64000.134100.232200"
```

**Breaking it down:**
```
37300.37500.51900.52300.64000.134100.232200
  │     │     │     │     │      │       │
  │     │     │     │     │      │       └─ Level 7: Specific activity
  │     │     │     │     │      └─ Level 6: Sub-activity type
  │     │     │     │     └─ Level 5: Work area/phase
  │     │     │     └─ Level 4: Discipline/work type
  │     │     └─ Level 3: Major work package
  │     └─ Level 2: Site/Location
  └─ Level 1: Project
```

### WBS vs UID - Key Differences

| Property | UID | WBS |
|----------|-----|-----|
| **Type** | Sequential integer | Hierarchical dot-separated code |
| **Example** | `188` | `37300.37500.51900...` |
| **Purpose** | Database key | Business identifier |
| **Generated by** | System (auto) | User/organization (custom) |
| **Stability** | ❌ Can change | ✅ **Never changes** |
| **Meaning** | ❌ None | ✅ **Encodes hierarchy & org structure** |
| **Best for** | Internal joins | **Business reporting, cost tracking** |

### WBS Structure in Your Project

**Perfect Correlation with Hierarchy:**

WBS segments ALWAYS equal OutlineLevel:

| Outline Level | WBS Segments | Example |
|---------------|--------------|---------|
| Level 1 | 1 segment | `37300` |
| Level 2 | 2 segments | `37300.37500` |
| Level 3 | 3 segments | `37300.37500.51900` |
| Level 4 | 4 segments | `37300.37500.51900.52300` |
| Level 5 | 5 segments | `37300.37500.51900.52300.64000` |
| Level 6 | 6 segments | `37300.37500.51900.52300.64000.134100` |
| Level 7 | 7 segments | `37300.37500.51900.52300.64000.134100.232200` |

### Finding Parent Tasks Using WBS

**Algorithm:**

```python
def find_parent_wbs(child_wbs):
    """Get parent WBS by removing last segment"""
    segments = child_wbs.split('.')
    if len(segments) <= 1:
        return None  # No parent (this is root)

    parent_wbs = '.'.join(segments[:-1])
    return parent_wbs

# Example:
child = "37300.37500.51900.52300.64000.134100.232200"
parent = find_parent_wbs(child)
# Returns: "37300.37500.51900.52300.64000.134100"
```

**Real Example - Tracing Hierarchy:**

```
Level 7: 37300.37500.51900.52300.64000.134100.232200
         → Excavation for isolated fottings of NTA

Level 6: 37300.37500.51900.52300.64000.134100
         → Footings including grade slab

Level 5: 37300.37500.51900.52300.64000
         → Phase 01 - Area excluding downramp

Level 4: 37300.37500.51900.52300
         → RCC works

Level 3: 37300.37500.51900
         → NTA works

Level 2: 37300.37500
         → Godrej Miraya

Level 1: 37300
         → Miraya | Sec 43 (Project Root)
```

### What Do the Codes Mean?

#### Level 1: Project Code
- `37300` - **1 unique code**
- Meaning: "Miraya | Sec 43"
- Purpose: Distinguish this project from others

#### Level 2: Site/Location
- `37300.37500` - **1 unique code**
- Meaning: "Godrej Miraya"
- Purpose: Specific site/development

#### Level 3: Major Work Package
- **4 unique codes** at this level
- Examples:
  - `37300.37500.51900` → NTA works
  - `37300.37500.117800` → Soldier Piling & Excavation
  - `37300.37500.46000` → Project Snapshot
  - `37300.37500.38800` → Tower area

#### Level 4: Discipline/Work Type
- **13 unique codes**
- Examples:
  - `.52300` → RCC works
  - `.130000` → MEP works
  - `.221600` → Finishing works

#### Level 5: Work Area/Phase
- **93 unique codes**
- Examples:
  - `.64000` → Phase 01 - Area excluding downramp
  - `.116300` → Basements
  - `.123400` → Ground floor

#### Level 6: Activity Category
- **112 unique codes**
- Examples:
  - `.134100` → Footings including grade slab
  - `.123600` → Columns
  - `.127500` → Beams

#### Level 7: Specific Activity
- **609 unique codes**
- Examples:
  - `.232200` → Excavation for isolated fottings
  - `.127600` → PCC for isolated footings
  - `.233500` → Reinforcement for footings

#### Level 8: Sub-Activity Detail
- **2,014 unique codes** (most granular)

### Uniqueness Statistics

| Level | Unique Codes | Pattern |
|-------|-------------|---------|
| 1 | 1 | All tasks start with `37300` |
| 2 | 1 | All have `37300.37500` |
| 3 | 4 | Major work packages |
| 4 | 13 | Disciplines |
| 5 | 93 | Areas/phases |
| 6 | 112 | Activity types |
| 7 | 609 | Specific activities |
| 8 | 2,014 | Sub-activities |

**Total unique WBS codes: 2,847** (one per task - perfectly unique!)

### Why WBS is Better Than UID for ETL

**✅ Use WBS for:**

1. **Building hierarchies** - Parent is WBS with last segment removed
2. **Cross-system integration** - WBS stays consistent across exports/imports
3. **Business reporting** - WBS codes match cost codes, org structure
4. **Data stability** - WBS never changes, even if tasks reordered
5. **Meaningful queries** - "All RCC works" = filter by `*.52300.*`
6. **External system mapping** - ERP, accounting likely use these codes

**❌ UID limitations:**

1. Can change between exports
2. No business meaning
3. May not match between systems
4. Not suitable for external reporting

### Practical Examples

**Example 1: Find All Tasks Under "NTA works"**

```python
nta_wbs_prefix = "37300.37500.51900"

nta_tasks = [
    task for task in tasks
    if task['WBS'].startswith(nta_wbs_prefix)
]
```

**Example 2: Find All RCC Works (Any Location)**

```python
rcc_code = "52300"

rcc_tasks = [
    task for task in tasks
    if rcc_code in task['WBS'].split('.')
]
```

**Example 3: Build Hierarchy Tree**

```python
def build_hierarchy(tasks):
    """Build parent-child tree using WBS"""
    tree = {}
    tasks_by_wbs = {task['WBS']: task for task in tasks}

    for task in tasks:
        segments = task['WBS'].split('.')

        if len(segments) > 1:
            parent_wbs = '.'.join(segments[:-1])
            parent = tasks_by_wbs.get(parent_wbs)

            if parent:
                if 'children' not in parent:
                    parent['children'] = []
                parent['children'].append(task)
        else:
            tree[task['WBS']] = task

    return tree
```

**Example 4: Aggregate Costs by WBS Level**

```python
def aggregate_by_level(tasks, level=3):
    """Sum costs by WBS code at specific level"""
    aggregates = {}

    for task in tasks:
        segments = task['WBS'].split('.')
        if len(segments) >= level:
            level_wbs = '.'.join(segments[:level])

            if level_wbs not in aggregates:
                aggregates[level_wbs] = {'cost': 0, 'tasks': []}

            aggregates[level_wbs]['cost'] += task.get('FixedCost', 0)
            aggregates[level_wbs]['tasks'].append(task)

    return aggregates
```

### Common Patterns

**Pattern 1: All Tasks Start the Same**
```
ALL tasks begin with: 37300.37500
```
Single project scope, single site, branching at Level 3

**Pattern 2: Codes Are NOT Sequential**
```
Level 3 codes: 46000, 51900, 117800, 38800
```
These are organizational codes with embedded meaning (cost codes, standards)

### WBS Summary

| Question | Answer |
|----------|--------|
| **What is WBS?** | Hierarchical organizational/cost code structure |
| **Who creates it?** | Your organization (not system-generated) |
| **Does it change?** | No - permanent identifier |
| **Is it unique?** | Yes - 2,847 unique codes for 2,847 tasks |
| **How to find parent?** | Remove last segment |
| **Why use vs UID?** | Stable, meaningful, matches external systems |
| **What do codes mean?** | Project → Site → Phase → Discipline → Area → Activity |
| **Best for?** | **Primary key for ETL, business reporting, cost tracking** |

---

## Detailed Q&A

### Q1: What is WBS and How Does It Work?

**Answer:** See [WBS Explained](#wbs-explained) section above for complete details.

**Summary:**
- WBS is a hierarchical numbering system organizing the project into levels
- Each segment represents one hierarchy level
- Parent-child relationships found by removing segments
- Most stable identifier for tracking tasks
- Encodes business meaning (cost codes, organizational structure)

### Q2: Where is the Actual Start Date?

**Answer:** There is NO ActualStart field in your data.

**What We Found:**

```
Task UID 188:
  ✗ ActualStart: NOT FOUND
  ✗ ActualFinish: NOT FOUND
  ✓ Start: 2025-07-13T08:00:00 (scheduled start)
  ✓ Finish: 2026-03-12T17:00:00 (scheduled finish)
```

**Why Actual Fields Are Missing:**

1. Asta Powerproject export settings may not include actual tracking
2. Actual tracking might not be enabled in source system
3. Asta stores actuals differently than MS Project

**How Progress IS Tracked:**

**1. Task Level:**
- `PercentComplete`: 14% (duration-based)

**2. Assignment Level:**
- `ActualWork`: PT136H0M0S (136 hours completed)
- `RemainingWork`: PT824H0M0S (824 hours remaining)

**3. Timephased Data:**
- Type 1: Planned work
- Type 2: **Actual work completed** (day-by-day)

**Deriving Actual Start:**

Find earliest TimephasedData entry with Type=2 and Value > 0:

```json
{
  "Type": "2",
  "Start": "2025-07-13T08:00:00",  ← This is actual start
  "Value": "PT8H0M0S"
}
```

**Conclusion:** Actual start = earliest Timephased Type=2 entry with work recorded.

### Q3: Why Are There Start/Finish/Duration AND Manual Versions?

**Answer:** Due to Microsoft Project's **two scheduling modes**.

**Auto-Scheduled (Traditional):**
- Start/Finish/Duration calculated by scheduling engine
- Considers dependencies, constraints, calendars, resources
- Dates change automatically when predecessors shift

**Manually Scheduled (MS Project 2010+):**
- ManualStart/ManualFinish/ManualDuration set by user
- Dates DON'T automatically change based on dependencies
- User has full control

**In Your Data:**

```
Start: 2025-07-13T08:00:00
ManualStart: 2025-07-13T08:00:00  ← Same!

Finish: 2026-03-12T17:00:00
ManualFinish: 2026-03-12T17:00:00  ← Same!
```

**They are identical!** This means:
1. Tasks are manually scheduled (dates set by user), OR
2. Scheduling engine agrees with manual dates, OR
3. Asta exports both values as the same

**How to Detect Manual vs Auto:**
- Start = ManualStart: Either manually scheduled OR engine agrees
- ConstraintType = 4 (SNET): Task has constraint forcing specific dates

**Implication:** This is why dependencies might not push dates. If tasks are manually scheduled, dependencies are informational only.

### Q4: What is Resume and Split/Interruption?

**Answer:** Resume indicates when work **restarts after a planned interruption** (split).

**What is a Task Split?**

A split divides a task into segments with non-working time between:

```
Original Plan:
[===========================] 960 hours continuous
July 13, 2025 → March 12, 2026

With Split:
[====]  [pause]  [================]
Start   Stop     Resume           Finish
Jul 13  Jul 28   Nov 30           Mar 12
```

**In Your Task:**

```json
{
  "Start": "2025-07-13T08:00:00",    ← Work begins
  "Resume": "2025-11-30T08:00:00",    ← Resumes after pause
  "ResumeValid": "1",                 ← Resume date valid
  "Finish": "2026-03-12T17:00:00"     ← Final completion
}
```

**Why the Interruption?**

Calendar has exception period:

```json
{
  "DayType": "0",
  "DayWorking": "0",
  "TimePeriod": {
    "FromDate": "2025-11-02T00:00:00",
    "ToDate": "2025-11-29T23:59:59"  ← Non-working period
  }
}
```

**Reason:** Calendar-driven (monsoon season, holiday period, or planned site shutdown)

**Evidence in Timephased Data:**

```
Type 2 (Actual Work):
  July 13-27: PT8H0M0S per day  ← Work happening
  July 28 - Nov 29: PT0H0M0S    ← NO WORK (pause)
  Nov 30 onwards: PT8H0M0S      ← Work resumes
```

**How to Detect Splits:**

1. Check for Resume field with ResumeValid=1
2. Look for PT0H0M0S gaps in TimephasedData
3. Check calendar exceptions

### Q5: What is Task Type (Fixed Units/Duration/Work)?

**Answer:** Task Type controls **how MS Project recalculates** when you change Work, Duration, or Units.

**The Formula:**

```
Work = Duration × Units

Where:
- Work: Total effort (e.g., 960 hours)
- Duration: Calendar time (e.g., 120 days)
- Units: Resource allocation (e.g., 1.0 = 100%)
```

**The Three Types:**

**Type 0: Fixed Units** (Your Data - ALL 2,849 tasks)
- **Units stay constant** when Work or Duration changes
- Most common for construction

Example:
```
Initial: 960 hours = 120 days × 1 person
Change duration to 60 days → Work becomes 480 hours (Units=1 fixed)
Change work to 1200 hours → Duration becomes 150 days (Units=1 fixed)
```

Use case: "I have 1 excavator, regardless of how long it takes"

**Type 1: Fixed Duration**
- **Duration stays constant** when Work or Units change

Example:
```
Initial: 960 hours = 120 days × 1 person
Change work to 1200 hours → Units become 1.25 (120 days fixed)
Add person (Units=2) → Work becomes 1920 hours (120 days fixed)
```

Use case: "Concrete curing must take 28 days"

**Type 2: Fixed Work**
- **Work stays constant** when Duration or Units change

Example:
```
Initial: 960 hours = 120 days × 1 person
Change duration to 60 days → Units become 2 people (960 hours fixed)
Add person (Units=2) → Duration becomes 60 days (960 hours fixed)
```

Use case: "Must excavate 1000 m³, add machines to finish faster"

**Why Your Project Uses Fixed Units:**

Construction typically uses Fixed Units because:
- Equipment capacity is usually fixed
- Crew sizes are predetermined
- Planning around available resources, not arbitrary durations

### Q6: Why Assignment UID ≠ Task UID? Can Multiple Assignments Exist?

**Answer:** Yes, multiple assignments per task are standard! UIDs reference different entities.

**Data Model:**

```
Tasks (what work needs to be done)
  ↓
Assignments (who/what is doing the work)
  ↓
Resources (people, equipment, materials)
```

**UID Relationships:**

```
Task {
  UID: 188  ← Task identifier
  Name: "Excavation..."
}

Assignment {
  UID: 190  ← Assignment identifier
  TaskUID: 188  ← Points to Task
  ResourceUID: -65535  ← Points to Resource
}

Resource {
  UID: 27  ← Resource identifier
  Name: "Excavator"
}
```

**Multiple Assignments Example:**

```
Task: "Install formwork"
  ├─ Assignment 1: Carpenter Team - 40 hours
  ├─ Assignment 2: Formwork Materials - 100 m²
  └─ Assignment 3: Crane - 8 hours

Each has unique Assignment.UID
All share same TaskUID
Different ResourceUID values
```

**Your Data Reality:**

- **0 tasks have multiple assignments**
- 64 tasks have assignments (all 1:1)

This suggests:
1. Simplified resource tracking
2. Aggregated resources (one assignment = team/resource group)
3. Export settings may limit detail
4. Cost-based tracking (ResourceUID=-65535)

**Why ResourceUID = -65535?**

Special values:
- `-65535`: Unassigned or material/cost resource
- `-1`: Sometimes summary/unspecified
- Positive: Specific named resources

Your data uses -65535, indicating cost-based tracking rather than detailed resource allocation.

### Q7: Is Resume Manual? How to See When It Was Paused?

**Answer:** Resume is BOTH manual AND automatic, depending on how the split was created.

**Two Ways to Create Splits:**

**1. Manual Split (User-Created)**
- User explicitly splits task
- User sets Resume date manually
- Creates gap regardless of calendar

**2. Automatic Split (Calendar-Driven)** ← Your data
- Non-working periods create automatic splits
- Resume calculated based on calendar
- This is what happened in your task!

**Evidence Your Split is Calendar-Driven:**

1. **Calendar has non-working period:**
```json
"TimePeriod": {
  "FromDate": "2025-11-02T00:00:00",
  "ToDate": "2025-11-29T23:59:59"
}
```

2. **Resume matches calendar:**
```json
"Resume": "2025-11-30T08:00:00"  ← Exactly when calendar allows work
```

3. **Timephased Data confirms:**
```
Oct 20: PT8H0M0S  ← Last day of work
Oct 21 - Nov 29: PT0H0M0S  ← Zero work during exception
Nov 30: PT8H0M0S  ← Work resumes
```

**Where to See When Paused:**

**Option 1: Timephased Data (Most Accurate)**

Find last Type 2 entry with Value > 0 before pause:

```json
{
  "Type": "2",
  "Start": "2025-10-20T08:00:00",
  "Value": "PT8H0M0S"  ← Last day of work
}
```

Paused on: October 20, 2025

**Option 2: Calendar Exceptions**

Check calendar for non-working periods between Start and Finish.

**Option 3: Resume Field**

If Resume exists and ResumeValid=1, work is currently paused:

```json
"Resume": "2025-11-30T08:00:00"  ← Currently paused, resumes here
```

**Manual vs Calendar Split Detection:**

```python
def detect_split_type(task, calendar):
    resume_date = task['Resume']

    # Check if calendar has exception covering resume
    for exception in calendar['WeekDays']['WeekDay']:
        if exception['DayType'] == '0':
            if is_date_in_period(resume_date, exception['TimePeriod']):
                return "Calendar-driven split"

    return "Manual split"
```

### Q8: Why Aren't Dependencies Updating Dates?

**Answer:** There is NO field for "implicit vs explicit" dependencies. However, dependencies may be **informational only** (not controlling dates).

**Analysis Results:**

```
- Tasks with predecessors: 2,525 out of 2,849 (89%)
- Start = ManualStart: TRUE in ALL cases
- ConstraintType: Many tasks use Type 4 (SNET)
```

**Why Dependencies Don't Push Dates:**

**1. Manual Scheduling Mode** (Most Likely)

When manually scheduled:
- Dependencies are **INFORMATIONAL only**
- Dates don't auto-update when predecessors slip
- User must manually adjust

Evidence:
```json
{
  "Start": "2025-07-13T08:00:00",
  "ManualStart": "2025-07-13T08:00:00",  ← Same = manually set
  "ConstraintType": "4",  ← SNET locks date
  "PredecessorLink": {
    "PredecessorUID": "477",
    "Type": "1"  ← Dependency exists but...
  }
}
```

Dependency exists, but constraint **overrides** it.

**2. Constraints Override Dependencies**

**Hierarchy of scheduling rules:**
```
1. Manual dates (highest priority)
2. Constraints (MSO, SNET, etc.)
3. Dependencies (FS links)
4. Project calendar (lowest priority)
```

Your tasks have ConstraintType=4 (SNET):
- "Cannot start before July 13, 2025"
- Even if predecessor delays, task won't auto-adjust

**How to Detect "Inactive" Dependencies:**

Dependencies are effectively disabled when:

```python
def is_dependency_active(task, predecessor):
    """Check if dependency controls task date"""

    # Check 1: Manual scheduling
    if task['Start'] == task['ManualStart']:
        is_manual = True

    # Check 2: Constraint overrides
    if task['ConstraintType'] in ['2', '3', '4', '5', '6', '7']:
        is_constrained = True

    # Check 3: Start date vs expected from predecessor
    expected_start = calculate_from_predecessor(predecessor, task['PredecessorLink'])
    if task['Start'] != expected_start:
        return False  # Dependency not controlling

    return True
```

**What You're Calling "Implicit vs Explicit":**

| Your Term | Actual Meaning | How to Detect |
|-----------|----------------|---------------|
| **Explicit** | Active dependency (auto-schedules) | Start ≠ ManualStart AND ConstraintType=0 |
| **Implicit** | Informational dependency (manual) | Start = ManualStart OR ConstraintType > 0 |

**In your data:** Most/all dependencies are "implicit" (informational) because:
1. Manual scheduling is used
2. Constraints are applied
3. Dates don't auto-update

**Recommended Approach for ETL:**

1. Store all dependencies regardless of active status
2. Flag tasks with constraints (ConstraintType > 0)
3. Assume dependencies are informational unless proven otherwise
4. Calculate critical path manually if needed
5. Track Start vs ManualStart differences

### Q9: What About Milestones?

**Answer:** Yes, the project has **4 milestones** representing key events.

**Your Project's Milestones:**

| Milestone | Date | WBS | Status |
|-----------|------|-----|--------|
| Start of project | Nov 30, 2025 | 37300.37500.46000.221600.949200 | Not started |
| Completion of project | Sep 6, 2029 | 37300.37500.46000.221600.949100 | Not started |
| Removal of soldier piles | Mar 21, 2027 | 37300.37500.46000.48100.949000 | Not started |
| Completion of Landscape works | Oct 13, 2028 | 37300.37500.46000.48100.948900 | Not started |

**Milestone Characteristics:**

```json
{
  "Milestone": "1",
  "Duration": "PT0H0M0S",  // Zero duration
  "Start": "2025-11-30T08:00:00",
  "Finish": "2025-11-30T08:00:00",  // Same as Start
  "PercentComplete": "0"
}
```

**Key Points:**

1. Very few milestones: Only 4 out of 2,849 tasks (0.14%)
2. Zero duration: All have Duration=PT0H0M0S
3. Start = Finish: Single point in time
4. All at Level 5: Under "Project Snapshot"
5. All future events: None started yet

**How to Identify:**

```python
def is_milestone(task):
    return (
        task.get('Milestone') == '1' and
        task.get('Duration') == 'PT0H0M0S' and
        task.get('Start') == task.get('Finish')
    )

milestones = [task for task in tasks if is_milestone(task)]
```

**Practical Use:**

- Project tracking: High-level progress indicators
- Reporting: Executive dashboards
- Baseline comparison: Track slippage of major events
- Gantt charts: Visual markers
- Alerts: Notify stakeholders

---

## ETL Pipeline Recommendations

**Reference Files:**
- `task_schema.json` - Target JSON schema (draft 2020-12)
- `xml_to_json_mapping.json` - Field mapping specification
- `sample_tasks.json` - Example output objects

### Phase 1: Extract

**1. Parse XML**

Use streaming parser for large files:

```python
import xml.etree.ElementTree as ET

def parse_miraya_xml(file_path):
    context = ET.iterparse(file_path, events=('start', 'end'))
    context = iter(context)
    event, root = next(context)

    # Remove namespace
    ns = '{http://schemas.microsoft.com/project}'

    for event, elem in context:
        if event == 'end':
            elem.tag = elem.tag.replace(ns, '')

            if elem.tag == 'Task':
                task = parse_task(elem)
                yield task

                # Clear memory
                elem.clear()
                root.clear()
```

**2. Extract Order**

```python
# 1. Parse metadata first
project_metadata = parse_project_metadata(root)

# 2. Parse lookup tables (needed for interpretation)
extended_attributes = parse_extended_attributes(root)
outline_codes = parse_outline_codes(root)

# 3. Parse calendars (needed for date calculations)
calendars = {}
for calendar in root.find('Calendars'):
    calendars[calendar.UID] = parse_calendar(calendar)

# 4. Parse tasks (LARGEST - 80% of file)
tasks = {}
for task in root.find('Tasks'):
    task_data = parse_task(task)

    # Dependencies embedded here
    if task.PredecessorLink:
        task_data['predecessors'] = parse_predecessors(task.PredecessorLink)

    tasks[task.UID] = task_data

# 5. Parse resources
resources = {}
for resource in root.find('Resources'):
    resources[resource.UID] = parse_resource(resource)

# 6. Parse assignments
assignments = []
for assignment in root.find('Assignments'):
    assign_data = parse_assignment(assignment)

    # TimephasedData embedded (100+ entries)
    assign_data['timephased'] = parse_timephased_data(assignment.TimephasedData)

    assignments.append(assign_data)
```

**3. Store Raw Data**

Store raw XML for audit/reprocessing.

### Phase 2: Transform

**1. Normalize Durations**

```python
def parse_iso8601_duration(duration_str):
    """Convert PT960H0M0S to 960 hours"""
    import re
    match = re.match(r'PT(\d+)H(\d+)M(\d+)S', duration_str)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        return hours + (minutes / 60) + (seconds / 3600)
    return 0

# Convert to days
hours = parse_iso8601_duration(task['Duration'])
days = hours / 8  # 8-hour workday
```

**2. Enrich Tasks**

```python
def enrich_task(task, calendars, predecessors, assignments):
    """Add embedded calendar, predecessor, assignment details"""

    # Add calendar details
    if task.get('CalendarUID'):
        task['calendar_details'] = calendars.get(task['CalendarUID'])

    # Add predecessor task details
    if task.get('PredecessorLink'):
        pred_uid = task['PredecessorLink']['PredecessorUID']
        task['predecessor_task'] = predecessors.get(pred_uid)

    # Add assignments
    task['assignments'] = [
        a for a in assignments
        if a['TaskUID'] == task['UID']
    ]

    return task
```

**3. Calculate Derived Fields**

```python
def calculate_derived_fields(task, assignments):
    """Calculate actual start, work progress, etc."""

    # Actual start from TimephasedData Type=2
    actual_starts = []
    for assignment in task['assignments']:
        for tp in assignment.get('timephased', []):
            if tp['Type'] == '2' and tp['Value'] != 'PT0H0M0S':
                actual_starts.append(tp['Start'])

    task['actual_start'] = min(actual_starts) if actual_starts else None

    # Work-based progress
    total_work = 0
    actual_work = 0
    for assignment in task['assignments']:
        total_work += parse_iso8601_duration(assignment.get('Work', 'PT0H0M0S'))
        actual_work += parse_iso8601_duration(assignment.get('ActualWork', 'PT0H0M0S'))

    task['work_progress'] = (actual_work / total_work * 100) if total_work > 0 else 0

    # Detect active vs inactive dependencies
    task['dependency_active'] = detect_dependency_active(task)

    # Detect pause periods
    task['pause_periods'] = detect_pauses(task)

    return task

def detect_dependency_active(task):
    """Check if dependency controls dates"""
    if task.get('Start') == task.get('ManualStart'):
        return False  # Manually scheduled
    if task.get('ConstraintType') not in ['0', None]:
        return False  # Constraint overrides
    return True

def detect_pauses(task):
    """Find pause periods from TimephasedData"""
    pauses = []
    for assignment in task.get('assignments', []):
        for tp in assignment.get('timephased', []):
            if tp['Type'] == '2' and tp['Value'] == 'PT0H0M0S':
                pauses.append({
                    'start': tp['Start'],
                    'end': tp['Finish']
                })
    return pauses
```

**4. Flag Data Quality Issues**

```python
def flag_quality_issues(task):
    """Identify data quality problems"""
    issues = []

    # Tasks with Start ≠ ManualStart
    if task['Start'] != task['ManualStart']:
        issues.append('start_mismatch')

    # Dependencies with large lead/lag
    if task.get('PredecessorLink'):
        lag_minutes = int(task['PredecessorLink'].get('LinkLag', 0))
        if abs(lag_minutes) > 10000:  # > ~7 days
            issues.append('large_lag')

    # Tasks with missing assignments
    if not task.get('assignments'):
        issues.append('no_assignments')

    # Constraints that may block scheduling
    if task.get('ConstraintType') in ['2', '3']:  # MSO, MFO
        issues.append('inflexible_constraint')

    task['quality_issues'] = issues
    return task
```

### Phase 3: Load

**Output Format: Target JSON Schema**

See `task_schema.json` for the complete output structure. Each task object follows this pattern:

```python
def transform_to_target_schema(task, assignments, external_attributes):
    """Transform XML task to target JSON schema"""

    # Determine task type
    is_summary = task.get('Summary') == '1'
    is_milestone = task.get('Milestone') == '1'

    # Build target object
    target = {
        'uid': int(task['UID']),
        'id': int(task['ID']),
        'wbs': task['WBS'],
        'outline_number': task['OutlineNumber'],
        'name': task['Name'],
        'parent_wbs': get_parent_wbs(task['WBS']),
        'is_summary': is_summary,
        'is_milestone': is_milestone,

        'dates': {
            'plan': {
                'start': extract_date(task['Start']),
                'end': extract_date(task['Finish']),
                'duration_days': parse_duration_to_days(task['Duration'])
            },
            'manual': {
                'start': extract_date(task.get('ManualStart')),
                'end': extract_date(task.get('ManualFinish')),
                'duration_days': parse_duration_to_days(task.get('ManualDuration'))
            },
            'sprint': {
                'start': None,  # From separate sprint XML
                'end': None,
                'duration_days': None
            },
            'actual': get_actual_dates(task, assignments, is_milestone)
        },

        # Null for parent/summary tasks and milestones
        'attributes': None if (is_summary or is_milestone) else external_attributes.get(task['WBS']),

        # Null for parent/summary tasks
        'progress': None if is_summary else {
            'percent_complete': int(task.get('PercentComplete', 0)),
            'is_complete': int(task.get('PercentComplete', 0)) == 100
        },

        # Null for parent/summary tasks, 0 for milestones
        'cost_plan_total': None if is_summary else (0 if is_milestone else float(task.get('FixedCost', 0))),

        # Null for parent tasks and milestones
        'cost_timeline': None if (is_summary or is_milestone) else calculate_cost_timeline(task, assignments)
    }

    return target
```

**Legacy Table Format (Optional)**

```python
# tasks table (use WBS as primary key)
tasks_table = pd.DataFrame([{
    'wbs': task['WBS'],
    'uid': task['UID'],
    'name': task['Name'],
    'start': task['Start'],
    'finish': task['Finish'],
    'duration_hours': parse_iso8601_duration(task['Duration']),
    'percent_complete': task['PercentComplete'],
    'actual_start': task.get('actual_start'),
    'work_progress': task.get('work_progress'),
    'is_milestone': task.get('Milestone') == '1',
    'constraint_type': task.get('ConstraintType'),
    'calendar_uid': task.get('CalendarUID'),
    'parent_wbs': get_parent_wbs(task['WBS'])
} for task in tasks])

# task_predecessors table
predecessors_table = pd.DataFrame([{
    'task_wbs': task['WBS'],
    'predecessor_uid': task['PredecessorLink']['PredecessorUID'],
    'link_type': task['PredecessorLink']['Type'],
    'lag_minutes': task['PredecessorLink']['LinkLag']
} for task in tasks if task.get('PredecessorLink')])

# task_assignments table
assignments_table = pd.DataFrame([{
    'assignment_uid': assign['UID'],
    'task_wbs': tasks_by_uid[assign['TaskUID']]['WBS'],
    'resource_uid': assign['ResourceUID'],
    'work_hours': parse_iso8601_duration(assign['Work']),
    'actual_work_hours': parse_iso8601_duration(assign['ActualWork']),
    'remaining_work_hours': parse_iso8601_duration(assign['RemainingWork'])
} for assign in assignments])

# task_timephased table
timephased_table = pd.DataFrame([{
    'assignment_uid': assign['UID'],
    'task_wbs': tasks_by_uid[assign['TaskUID']]['WBS'],
    'type': tp['Type'],
    'start': tp['Start'],
    'finish': tp['Finish'],
    'hours': parse_iso8601_duration(tp['Value'])
} for assign in assignments for tp in assign.get('timephased', [])])

# calendars table
calendars_table = pd.DataFrame([{
    'uid': cal['UID'],
    'name': cal['Name'],
    'is_base': cal['IsBaseCalendar']
} for cal in calendars.values()])

# resources table
resources_table = pd.DataFrame([{
    'uid': res['UID'],
    'name': res['Name'],
    'type': res['Type'],
    'is_cost': res['IsCostResource']
} for res in resources.values()])
```

**2. Denormalized Views**

```python
# Hierarchical view with parent-child
hierarchy_view = tasks_table.copy()
hierarchy_view['parent_name'] = hierarchy_view['parent_wbs'].map(
    tasks_table.set_index('wbs')['name']
)
hierarchy_view['level'] = hierarchy_view['wbs'].apply(lambda x: len(x.split('.')))

# Progress dashboard view
progress_view = tasks_table.merge(
    assignments_table.groupby('task_wbs').agg({
        'work_hours': 'sum',
        'actual_work_hours': 'sum',
        'remaining_work_hours': 'sum'
    }),
    left_on='wbs',
    right_index=True,
    how='left'
)
```

### Recommended Reading Order for Parsing

1. **Parse metadata** → Get project settings
2. **Parse ExtendedAttributes definitions** → Build lookup table
3. **Parse Calendars** → Needed for date calculations
4. **Parse Tasks** (80% of file) → Use streaming if possible
5. **Parse Resources** → Small section
6. **Parse Assignments** → Contains TimephasedData

### Memory Considerations

- **Tasks section**: ~3.5 MB, 2,849 items → **Use streaming for large files**
- **Assignments**: ~400 KB but dense (100+ timephased per assignment)
- **Total**: 4.4 MB → Can load in memory, but streaming recommended for future larger files

### Common Pitfalls to Avoid

**❌ Don't Do This:**

1. Loading entire file as dict (future files may be larger)
2. Looking for separate Dependencies section (embedded in tasks)
3. Treating milestones as separate (just tasks with Milestone=1)
4. Parsing tasks without ExtendedAttributes definitions first
5. Ignoring TimephasedData (contains actual progress)

**✅ Do This:**

1. Use streaming XML parser (SAX/iterparse)
2. Parse ExtendedAttributes first → Build lookup
3. Build UID indexes → Fast lookups
4. Extract dependencies during task parsing (embedded)
5. Handle TimephasedData carefully (100+ entries)

---

## Common Use Cases

### 1. Build Task Hierarchy

```python
def build_hierarchy(tasks):
    """Build parent-child tree using WBS"""
    tasks_by_wbs = {task['WBS']: task for task in tasks}

    def get_parent_wbs(wbs):
        segments = wbs.split('.')
        return '.'.join(segments[:-1]) if len(segments) > 1 else None

    tree = {}
    for task in tasks:
        parent_wbs = get_parent_wbs(task['WBS'])
        if parent_wbs and parent_wbs in tasks_by_wbs:
            parent = tasks_by_wbs[parent_wbs]
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(task)
        else:
            tree[task['WBS']] = task

    return tree
```

### 2. Calculate True Progress

```python
def calculate_progress(task, assignments):
    """Calculate work-based progress (not duration-based)"""
    total_work = 0
    actual_work = 0

    for assignment in assignments:
        if assignment['TaskUID'] == task['UID']:
            total_work += parse_duration(assignment['Work'])
            actual_work += parse_duration(assignment['ActualWork'])

    return (actual_work / total_work * 100) if total_work > 0 else 0
```

### 3. Extract Working Days from Calendar

```python
def get_working_days(calendar):
    """Extract working days and hours"""
    working_days = []

    for weekday in calendar['WeekDays']['WeekDay']:
        if weekday['DayWorking'] == '1':
            day_type = int(weekday['DayType'])
            working_times = weekday.get('WorkingTimes', {})

            hours = []
            for wt in working_times.get('WorkingTime', []):
                hours.append({
                    'from': wt['FromTime'],
                    'to': wt['ToTime']
                })

            working_days.append({
                'day': day_type,
                'hours': hours
            })

    return working_days
```

### 4. Detect Schedule Delays

```python
def is_task_delayed(task, predecessor_tasks):
    """Check if task should have started based on predecessor"""
    if 'PredecessorLink' not in task:
        return False

    pred_link = task['PredecessorLink']
    predecessor = predecessor_tasks.get(pred_link['PredecessorUID'])
    if not predecessor:
        return False

    # Calculate expected start
    expected_start = calculate_start_from_predecessor(
        predecessor['Finish'],
        pred_link['LinkLag'],
        pred_link['Type']
    )

    # Compare with actual
    actual_start = task['Start']

    return actual_start > expected_start
```

### 5. Find All Tasks in a WBS Branch

```python
def find_tasks_in_branch(tasks, wbs_prefix):
    """Find all tasks under a specific WBS branch"""
    return [
        task for task in tasks
        if task['WBS'].startswith(wbs_prefix)
    ]

# Example: Find all NTA works
nta_tasks = find_tasks_in_branch(tasks, "37300.37500.51900")
```

### 6. Aggregate Costs by Level

```python
def aggregate_by_wbs_level(tasks, level):
    """Sum costs at specific WBS level"""
    aggregates = {}

    for task in tasks:
        segments = task['WBS'].split('.')
        if len(segments) >= level:
            level_wbs = '.'.join(segments[:level])

            if level_wbs not in aggregates:
                aggregates[level_wbs] = {
                    'cost': 0,
                    'duration': 0,
                    'tasks': []
                }

            aggregates[level_wbs]['cost'] += task.get('FixedCost', 0)
            aggregates[level_wbs]['duration'] += parse_duration(task.get('Duration', 'PT0H0M0S'))
            aggregates[level_wbs]['tasks'].append(task)

    return aggregates

# Example: Aggregate by Level 3 (major work packages)
level3_costs = aggregate_by_wbs_level(tasks, 3)
```

---

## Quick Reference Tables

### Task Type Values

| Value | Type | What Stays Fixed | Formula |
|-------|------|-----------------|---------|
| `0` | Fixed Units | Resources | Work = Duration × Units |
| `1` | Fixed Duration | Time | Duration = Work / Units |
| `2` | Fixed Work | Effort | Units = Work / Duration |

### Constraint Type Values

| Value | Code | Description | Priority |
|-------|------|-------------|----------|
| `0` | ASAP | As Soon As Possible | Low |
| `1` | ALAP | As Late As Possible | Low |
| `2` | MSO | Must Start On | **High** |
| `3` | MFO | Must Finish On | **High** |
| `4` | SNET | Start No Earlier Than | Medium |
| `5` | SNLT | Start No Later Than | Medium |
| `6` | FNET | Finish No Earlier Than | Medium |
| `7` | FNLT | Finish No Later Than | Medium |

### Dependency Link Types

| Value | Type | Description |
|-------|------|-------------|
| `0` | FF | Finish-to-Finish |
| `1` | **FS** | **Finish-to-Start** (most common) |
| `2` | SS | Start-to-Start |
| `3` | SF | Start-to-Finish |

### TimephasedData Types

| Value | Type | Description |
|-------|------|-------------|
| `1` | Planned Work | Future scheduled work |
| `2` | **Actual Work** | **Completed work (use for ActualStart)** |
| `3` | Overtime | Overtime work |

### Resource Types

| Value | Type | Description |
|-------|------|-------------|
| `0` | Work | Labor (people, equipment) |
| `1` | Material | Consumables |
| `2` | Cost | Cost-only resources |

### Special Values

| Field | Value | Meaning |
|-------|-------|---------|
| ResourceUID | `-65535` | Unassigned/cost resource |
| Duration | `PT0H0M0S` | Milestone (zero duration) |
| ConstraintType | `0` | No constraint |
| DayType | `0` | Calendar exception |
| DayWorking | `0` | Non-working day |
| CalendarUID | `-1` | No parent calendar |

### ISO 8601 Duration Examples

| Format | Meaning |
|--------|---------|
| `PT960H0M0S` | 960 hours |
| `PT8H0M0S` | 8 hours |
| `PT30M0S` | 30 minutes |
| `PT0H0M0S` | Zero duration (milestone) |

### DateTime Format

```
Format: YYYY-MM-DDTHH:MM:SS
Example: 2025-07-13T08:00:00
         └─ Date ─┘ └─Time─┘
                  T = separator
```

### Your Project Summary

| Attribute | Value |
|-----------|-------|
| **Total Tasks** | 2,849 |
| **Milestones** | 4 (0.14%) |
| **Assignments** | 64 |
| **Resources** | 5 |
| **Calendars** | 25 |
| **Tasks with Dependencies** | 2,525 (89%) |
| **Task Type** | All Type 0 (Fixed Units) |
| **File Size** | 4.4 MB |
| **Project Duration** | Dec 2, 2025 → Sep 17, 2031 (~6 years) |
| **Working Hours** | 8 hours/day (8am-12pm, 1pm-5pm) |
| **Working Days** | Monday-Saturday |
| **Currency** | £ (British Pounds) |

---

## Version History

**v2.1** (2025-12-09) - Target Schema Alignment
- Added "Target JSON Schema" section documenting ETL output format
- Documented attributes enum values from external master data
- Added cost_timeline structure with FY 2025-26 weekly breakdown
- Documented dates derivation (plan, manual, sprint, actual)
- Listed excluded XML fields with reasons
- Updated ETL Pipeline with transform_to_target_schema function
- Updated file references to task_schema.json, xml_to_json_mapping.json, sample_tasks.json

**v2.0** (2025-12-08) - Complete Merged Documentation
- Merged all documentation into single comprehensive guide
- Integrated XML structure, field definitions, WBS explanation, and detailed Q&A
- Added ETL recommendations and common use cases
- Created quick reference tables

**v1.2** (2025-12-08)
- Added xml_structure_guide.md
- Added wbs_explained.md
- Explained WBS vs UID, hierarchy, business integration

**v1.1** (2025-12-08)
- Added milestone documentation
- Found 4 project milestones
- Updated all documentation files

**v1.0** (2025-12-07)
- Initial documentation created
- Analyzed Miraya.xml (2,849 tasks)
- Created field definitions, detailed Q&A, example data

---

## Support & References

### Official Microsoft Documentation

- [Microsoft Project XML Schema](https://learn.microsoft.com/en-us/office-project/xml-data-interchange/)
- [Task Elements Reference](https://learn.microsoft.com/en-us/office-project/xml-data-interchange/task-elements-and-xml-structure)
- [Assignment Elements Reference](https://learn.microsoft.com/en-us/office-project/xml-data-interchange/assignment-elements-and-xml-structure)
- [XML Schema for Assignments](https://learn.microsoft.com/en-us/office-project/xml-data-interchange/xml-schema-for-the-assignments-element)
- [Constraint Type Reference](https://support.microsoft.com/en-us/office/constraint-type-task-field-0cb70e9a-ea3f-475e-b7ed-e75c5ab033f4)
- [ISO 8601 Duration Format](https://docs.digi.com/resources/documentation/digidocs/90001488-13/reference/r_iso_8601_duration_format.htm)

### This Documentation Set

- **complete_documentation.md** - This file (comprehensive merged guide)
- **task_schema.json** - Target JSON schema (JSON Schema draft 2020-12)
- **xml_to_json_mapping.json** - Field mapping from XML source to target JSON
- **sample_tasks.json** - Example objects for parent, leaf, and milestone tasks

---

**End of Complete Documentation**
