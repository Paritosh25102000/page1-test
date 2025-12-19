# Data Model: Page 1 Executive Summary Dashboard

**Feature**: 001-page1-executive-summary
**Date**: 2025-12-15
**Source Schema**: `etl-cco-dashboard/schemas/page-1-executive-simmary/page1-executive-summary.json`

## Entity Relationship Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     DashboardData                           │
├─────────────────────────────────────────────────────────────┤
│  meta: Meta                                                 │
│  controls: Controls                                         │
│  dashboard_data: Record<DataKey, NodeData>                  │
└─────────────────────────────────────────────────────────────┘
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
```

## Entity Definitions

### Meta

Metadata about the ETL run that generated this dataset.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| generated_at | string (ISO 8601) | Yes | Timestamp when data was generated |
| data_version | string | No | Version identifier for the dataset |
| currency_unit | string | No | Currency code (default: "INR") |

### Controls

Configuration data for UI filters and time mode logic.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| hierarchy_tree | HierarchyTree | Yes | Nested Zone → Region → Project structure |
| time_modes | TimeModes | Yes | FY, Quarter, Month configuration |

### HierarchyTree

Nested structure: `Record<ZoneId, Record<RegionId, Project[]>>`

Example:
```json
{
  "MZ": {
    "MZ1": [
      { "id": "Horizon", "name": "Horizon" },
      { "id": "Reserve", "name": "Reserve" }
    ]
  }
}
```

### Project

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique project identifier (used in data keys) |
| name | string | Yes | Display name for dropdown |

### TimeModes

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| fy | TimeMode | Yes | Financial Year configuration |
| quarter | TimeMode | Yes | Current Quarter configuration |
| month | TimeMode | Yes | Looking Glass (+/- 5 weeks) configuration |

### TimeMode

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| label | string | Yes | Display label (e.g., "Financial Year") |
| start | string (date) | Yes | Period start date (YYYY-MM-DD) |
| end | string (date) | Yes | Period end date (YYYY-MM-DD) |
| resolution | "month" \| "week" | Yes | Data granularity |

### DataKey (Union Type)

Pattern for `dashboard_data` keys:

| Pattern | Example | Description |
|---------|---------|-------------|
| "ALL" | "ALL" | Global aggregate (no filters) |
| "ZONE_{id}" | "ZONE_MZ" | Zone-level aggregate |
| "REG_{id}" | "REG_MZ1" | Region-level aggregate |
| "PROJ_{id}" | "PROJ_Horizon" | Project-level data |

### NodeData

Data payload for each filter selection node.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| kpi_gauges | KPIGauges | Yes | AOP and Sprint achievement data |
| coc_trend | COCTrend | Yes | Cost trend series for all time modes |
| project_matrix | ProjectMatrix | Yes | Project counts by achievement bucket |

### KPIGauges

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| aop | GaugeData | Yes | AOP Achievement gauge data |
| sprint | GaugeData | Yes | Sprint Achievement gauge data |

### GaugeData

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| achieved_pct | number | Yes | Achievement percentage (0-100+) |
| status_color | "red" \| "amber" \| "green" | Yes | Pre-calculated threshold color |
| actual_ytd | number | No | Actual cost year-to-date |
| plan_ytd | number | No | Planned cost year-to-date |

**Color Thresholds**:
- Red: < 85%
- Amber: 85% - 95%
- Green: > 95%

### COCTrend

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| fy_series | TrendPoint[] | Yes | Monthly data for Financial Year view |
| quarter_series | TrendPoint[] | Yes | Weekly data for Quarter view |
| month_series | TrendPoint[] | Yes | Weekly data for Looking Glass view |

### TrendPoint

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| label | string | Yes | X-axis label (e.g., "Apr-25", "Wk 14") |
| sort_date | string (date) | Yes | ISO date for sorting |
| plan_cost | number \| null | Yes | Planned periodic cost (bar height) |
| actual_cost | number \| null | Yes | Actual periodic cost (bar height) |
| cumm_plan | number \| null | No | Cumulative planned cost (line Y-value) |
| cumm_actual | number \| null | No | Cumulative actual cost (line Y-value) |

### ProjectMatrix

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| rows | MatrixRow[] | Yes | Rows for the heatmap table |

### MatrixRow

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| label | string | Yes | Row header (Zone or Region name) |
| id | string | No | ID for drill-down navigation |
| buckets | Buckets | Yes | Project counts per achievement bucket |

### Buckets

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| gt_120 | integer | Yes | Count of projects > 120% |
| 100_120 | integer | Yes | Count of projects 100-120% |
| 85_100 | integer | Yes | Count of projects 85-100% |
| 60_85 | integer | Yes | Count of projects 60-85% |
| lt_60 | integer | Yes | Count of projects < 60% |

## State Entities (Frontend Only)

### FilterState

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| zone | string \| null | null | Selected zone ID |
| region | string \| null | null | Selected region ID |
| project | string \| null | null | Selected project ID |

### TimeMode (State)

| Value | Description |
|-------|-------------|
| "FY" | Financial Year view (monthly) |
| "Quarter" | Current Quarter view (weekly) |
| "Month" | Looking Glass view (weekly) |

Default: "FY"

## Validation Rules

1. **Cascading dependency**: If `zone` is null, `region` and `project` must be null
2. **Cascading dependency**: If `region` is null, `project` must be null
3. **Data key construction**: Based on most specific non-null filter
4. **Gauge color validation**: Color must match threshold calculation
5. **Trend series selection**: Based on current TimeMode state
