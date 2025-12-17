# Stage 3: JSON → Staging Specification

**Stage**: 03-json-to-staging
**Status**: Draft
**Last Updated**: 2025-12-16
**Depends On**: Stage 1 (XML → JSON)

---

## 1. Overview

Stage 3 transforms enriched Master JSON files into pre-aggregated staging datasets optimized for dashboard rendering. Each dashboard page has its own staging JSON file containing data pre-computed for every possible filter combination.

### Key Principle: Pre-Aggregation

Instead of computing aggregations in the browser, all calculations are performed during ETL:

```
Browser Request: "Show me COC trend for Zone MZ"

Traditional Approach:
  → Load all 110,000 tasks
  → Filter by zone == "MZ"
  → Aggregate weekly costs
  → Calculate cumulative values
  → Render chart
  (Time: 2-5 seconds)

Pre-Aggregation Approach:
  → Lookup dashboard_data["ZONE_MZ"]
  → Render chart
  (Time: <100ms)
```

---

## 2. Input / Output

### 2.1 Input

| Item | Location | Format |
|------|----------|--------|
| Master JSON | `output/json/{project}.json` | JSON array of tasks |
| Schema | `task_schema.json` | JSON Schema |

**Input Statistics**:
- 13 project files
- ~110,000 tasks total
- ~98,000 leaf tasks (work items)
- File sizes: 1-15 MB per project

### 2.2 Output

| Item | Location | Format |
|------|----------|--------|
| Page 1 Staging | `output/staging/page1-executive-summary.json` | Staging JSON |
| Page 2 Staging | `output/staging/page2-{name}.json` | Staging JSON (future) |
| Page 3 Staging | `output/staging/page3-{name}.json` | Staging JSON (future) |
| Staging Report | `output/staging/staging_report.json` | Validation report |

**Output Characteristics**:
- Single file per dashboard page
- Pre-computed for ~50 filter combinations per page
- Target size: <5 MB per page
- Static file deployment (CDN-friendly)

---

## 3. User Stories

### US-001: Generate Page 1 Staging Data (P1)

**As** an ETL operator,
**I need** to generate Page 1 Executive Summary staging data,
**So that** the dashboard can render instantly without client-side computation.

**Acceptance Criteria**:
1. Running `runner_staging.py --page page1` produces `output/staging/page1-executive-summary.json`
2. Output validates against `schemas/staging/page1-executive-summary.json`
3. All filter combinations (ALL, ZONE_*, REG_*, PROJ_*) are present
4. Processing completes in under 2 minutes

### US-002: Pre-Compute All Filter Combinations (P1)

**As** a dashboard user,
**I need** all filter combinations to be pre-computed,
**So that** switching filters feels instant (<100ms).

**Acceptance Criteria**:
1. Staging JSON contains keys for: ALL, all zones, all regions, all projects
2. Each key contains complete widget data (gauges, trend, matrix)
3. No additional calculation required in browser

### US-003: Generate COC Trend Series (P1)

**As** a COO,
**I need** COC trend data for all three time modes (FY, Quarter, Month),
**So that** I can switch between strategic and tactical views.

**Acceptance Criteria**:
1. Each filter key contains `fy_series`, `quarter_series`, `month_series`
2. FY series has monthly data points (12 max)
3. Quarter/Month series have weekly data points
4. Each point has: label, sort_date, plan_cost, actual_cost, cumm_plan, cumm_actual

### US-004: Calculate KPI Gauge Values (P1)

**As** a COO,
**I need** AOP and Sprint achievement percentages pre-calculated,
**So that** I can quickly assess schedule performance.

**Acceptance Criteria**:
1. Each filter key contains `kpi_gauges.aop` and `kpi_gauges.sprint`
2. AOP achievement = (Actual Cost YTD / Plan Cost YTD) * 100
3. Sprint achievement = Sprint actual / Sprint plan (where sprint data exists)
4. Status color is pre-determined: red (<85%), amber (85-95%), green (>95%)

### US-005: Generate Project Achievement Matrix (P1)

**As** a COO,
**I need** project counts distributed by achievement bucket,
**So that** I can identify at-risk projects at a glance.

**Acceptance Criteria**:
1. Each filter key contains `project_matrix.rows`
2. Rows are Zone-level for ALL, Region-level when Zone selected
3. Buckets: >120%, 100-120%, 85-100%, 60-85%, <60%
4. Counts are integers representing project counts

### US-006: Build Hierarchy Tree (P1)

**As** a dashboard,
**I need** the complete Zone → Region → Project hierarchy,
**So that** cascading dropdowns can be populated.

**Acceptance Criteria**:
1. `controls.hierarchy_tree` contains nested Zone → Region → Project structure
2. Each project has `id` and `name` properties
3. Hierarchy matches actual data in Master JSON

### US-007: Validate Staging Output (P1)

**As** an ETL operator,
**I need** staging output to be validated,
**So that** I catch data issues before deployment.

**Acceptance Criteria**:
1. Output validates against JSON Schema
2. All expected keys are present
3. No null values where required
4. Numeric values are within expected ranges

---

## 4. Requirements

### 4.1 Functional Requirements

#### Aggregation Core

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | System MUST aggregate task data by zone, region, and project | P1 |
| FR-002 | System MUST generate global "ALL" aggregate | P1 |
| FR-003 | System MUST produce one staging file per dashboard page | P1 |
| FR-004 | System MUST validate output against JSON Schema | P1 |

#### COC Trend

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-010 | System MUST sum `weekly_costs.plan.cost` and `weekly_costs.actual.cost` by week | P1 |
| FR-011 | System MUST aggregate weeks into months for FY series | P1 |
| FR-012 | System MUST filter weeks by date range for Quarter series | P1 |
| FR-013 | System MUST filter weeks by +/- 5 weeks for Month series | P1 |
| FR-014 | System MUST calculate cumulative values within each series | P1 |
| FR-015 | System MUST handle null actual costs gracefully | P1 |

#### KPI Gauges

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-020 | System MUST calculate AOP achievement as actual_ytd / plan_ytd | P1 |
| FR-021 | System MUST calculate Sprint achievement from sprint date tasks only | P1 |
| FR-022 | System MUST determine status_color based on percentage thresholds | P1 |
| FR-023 | System MUST handle cases where Sprint data is unavailable | P2 |

#### Project Matrix

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-030 | System MUST calculate per-project achievement (actual_ytd / plan_ytd) | P1 |
| FR-031 | System MUST bucket projects into 5 achievement ranges | P1 |
| FR-032 | System MUST count projects per bucket per zone/region | P1 |
| FR-033 | System MUST generate Zone rows for ALL view, Region rows for Zone view | P1 |

#### Hierarchy

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-040 | System MUST extract unique zones from task attributes | P1 |
| FR-041 | System MUST extract regions per zone from task attributes | P1 |
| FR-042 | System MUST extract projects per region from task attributes | P1 |
| FR-043 | System MUST structure as nested dictionary for cascading dropdowns | P1 |

### 4.2 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001 | Processing time for all 13 projects | <2 minutes |
| NFR-002 | Memory usage | <1 GB |
| NFR-003 | Output file size per page | <5 MB |
| NFR-004 | Output must be valid JSON | 100% |
| NFR-005 | All filter keys must be present | 100% |

---

## 5. Constraints

### 5.1 Technical Constraints

1. **Static Output**: Output must be static JSON files (no API, no database)
2. **Single File Per Page**: Each dashboard page gets exactly one staging JSON
3. **Python 3.8+**: Must use Python standard library + existing dependencies
4. **Memory Limit**: Must process without loading all tasks into memory simultaneously

### 5.2 Business Constraints

1. **Financial Year**: FY runs April 1 - March 31 (Indian fiscal year)
2. **Currency**: All costs in INR
3. **Time Zones**: All dates in IST (UTC+5:30)

---

## 6. Assumptions

1. Master JSON files are valid and conform to `task_schema.json`
2. All tasks have `attributes.zone`, `attributes.region`, `attributes.project_name`
3. Leaf tasks have `cost_timeline.weekly_costs` populated
4. Sprint dates may be null for some tasks
5. Dashboard pages beyond Page 1 will follow similar structure

---

## 7. Edge Cases

| Scenario | Handling |
|----------|----------|
| Zone has no regions | Include zone in hierarchy with empty regions dict |
| Project has no leaf tasks | Include project with zero costs |
| All actual costs are null | Show plan costs only, actual as null |
| Sprint data unavailable for all tasks | Sprint gauge shows 0% with note |
| Week splits across months (FY aggregation) | Prorate cost by days in each month |
| Task has cost but no dates | Exclude from timeline, include in totals |
| Negative cost values | Treat as valid (adjustments) |
| Future dates in actual | Include if present (data quality issue, not ETL issue) |

---

## 8. Dependencies

### 8.1 Upstream Dependencies

| Dependency | Type | Impact if Missing |
|------------|------|-------------------|
| Stage 1 Output | Required | Cannot run |
| `task_schema.json` | Required | Cannot validate input |
| Zone/Region mapping | Required | Cannot build hierarchy |

### 8.2 Downstream Dependents

| Dependent | Impact |
|-----------|--------|
| Dashboard Frontend | Consumes staging JSON |
| QA Reports | Validates staging completeness |

---

## 9. Glossary

| Term | Definition |
|------|------------|
| **Staging JSON** | Pre-aggregated dashboard data file |
| **Filter Key** | Composite ID like "ZONE_MZ" or "PROJ_Horizon" |
| **YTD** | Year to Date (from FY start to current week) |
| **COC** | Cost of Construction |
| **Bucket** | Achievement range (e.g., 85-100%) |

---

## 10. Related Documents

| Document | Purpose |
|----------|---------|
| `plan.md` | Implementation plan and module structure |
| `data-model.md` | Entity definitions and relationships |
| `tasks.md` | Detailed task breakdown |
| `widgets/*.md` | Per-widget transformation specifications |
| `../SYSTEM_DESIGN.md` | System architecture overview |
