# Schema Validation Analysis Report

**Date**: 2025-12-17
**Status**: Pre-Implementation Validation
**Scope**: Page 1 Executive Summary Staging Schema

---

## 1. Executive Summary

This report analyzes the consistency between:
- **Master Schema**: `task_schema.json` (Source data from Phase 1)
- **Staging Schema**: `page1-executive-summary_schema.json` (Target output)
- **Business Requirements**: `schemas/page-1-executive-simmary/dashboard-element-definition/*.md`
- **Transformation Specs**: `docs/03-json-to-staging/widgets/*.md`

### Validation Result: **SCHEMA UPDATE REQUIRED**

**Critical Issues Found**: 2
**Major Issues Found**: 3
**Minor Issues Found**: 4

---

## 2. Critical Issues

### CRITICAL-001: KPI Gauges Missing Time-Mode Structure

**Severity**: CRITICAL - Schema must be updated before implementation

**Problem**: The current staging schema does NOT support time-mode aware gauge values.

**Current Schema** (`page1-executive-summary_schema.json` lines 89-115):
```json
"kpi_gauges": {
  "aop": {
    "achieved_pct": { "type": "number" },
    "status_color": { "type": "string", "enum": ["red", "amber", "green"] },
    "actual_ytd": { "type": "number" },
    "plan_ytd": { "type": "number" }
  },
  "sprint": {
    "achieved_pct": { "type": "number" },
    "status_color": { "type": "string", "enum": ["red", "amber", "green"] },
    "sprint_actual": { "type": "number" },
    "sprint_plan": { "type": "number" }
  }
}
```

**Required Schema** (per `docs/03-json-to-staging/widgets/kpi-gauges.md` and `spec.md` US-004):
```json
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
```

**Business Requirement** (from `spec.md` US-004):
> Gauge values respond to **BOTH** filter selection **AND** time toggle simultaneously

**Impact**: Without this change, gauges cannot respond to time toggle (FY/Quarter/Month).

**Required Action**: Update `page1-executive-summary_schema.json` to add nested time-mode structure.

---

### CRITICAL-002: Sprint Field Name Mismatch

**Severity**: CRITICAL - May cause runtime errors

**Problem**: Inconsistent Sprint end date field naming across documents.

| Document | Field Name | Example |
|----------|-----------|---------|
| `task_schema.json` (line 106-108) | `dates.sprint.end` | `"end": "2025-05-15"` |
| `kpi-gauges.md` (line 75) | `dates.sprint.finish` | `"finish": "2025-06-15"` |
| Sprint analysis report | `dates.sprint.finish` | Per Option A recommendation |

**Evidence from `task_schema.json`**:
```json
"sprint": {
  "type": "object",
  "properties": {
    "start": {...},
    "end": {...},           // <-- Uses "end"
    "duration_days": {...}
  }
}
```

**Evidence from `kpi-gauges.md`**:
```python
"dates": {
    "sprint": {
        "start": "2025-04-15",
        "finish": "2025-06-15",  # Note: Sprint uses 'finish', not 'end'
        ...
    }
}
```

**Root Cause**: The original business definition from Asta Powerproject uses "finish", but the schema was normalized to use "end" for consistency with plan dates.

**Impact**: Code may fail if developers reference the wrong field name.

**Verification Result** (from `output/json/Miraya.json`):
```json
"sprint": {
  "start": "2025-01-02",
  "finish": "2028-10-05",      // <-- Actual output uses "finish"
  "duration_days": 981.0
}
```

**Resolution**: The actual ETL output uses `"finish"`, NOT `"end"`. The `task_schema.json` is INCORRECT.

**Required Action**:
1. **Update `task_schema.json`** line 106-108: Change `"end"` to `"finish"` for Sprint dates
2. Ensure all documentation uses `"finish"` (widget docs already correct)
3. This is a schema bug - actual implementation differs from schema definition

---

## 3. Major Issues

### MAJOR-001: Missing `tasks_with_sprint` Field in Schema

**Severity**: MAJOR - Missing required metric

**Problem**: Staging schema doesn't include `tasks_with_sprint` field for sprint gauge.

**Current Schema** (Sprint gauge):
```json
"sprint": {
  "achieved_pct": { "type": "number" },
  "status_color": { "type": "string" },
  "sprint_actual": { "type": "number" },
  "sprint_plan": { "type": "number" }
  // Missing: tasks_with_sprint
}
```

**Required** (per `kpi-gauges.md`):
```json
"sprint": {
  "achieved_pct": {...},
  "status_color": {...},
  "sprint_actual": {...},
  "sprint_plan": {...},
  "tasks_with_sprint": { "type": "integer" }  // Count of tasks with sprint data
}
```

**Business Value**: Provides context about Sprint data coverage (only 64% of leaf tasks have Sprint dates per analysis).

**Required Action**: Add `tasks_with_sprint` field to Sprint gauge schema.

---

### MAJOR-002: Field Naming Inconsistency (actual_ytd vs actual)

**Severity**: MAJOR - Inconsistent API contract

**Problem**: Different field names used across documents for the same data.

| Context | Plan Field | Actual Field |
|---------|-----------|--------------|
| Current staging schema | `plan_ytd` | `actual_ytd` |
| kpi-gauges.md (time-mode structure) | `plan` | `actual` |
| Mock data | `plan_ytd` | `actual_ytd` |
| data-model.md example | `plan_ytd` | `actual_ytd` |

**Recommendation**:
- Use `plan` and `actual` for time-mode aware gauges (shorter, cleaner)
- The "YTD" suffix is implicit in the FY time mode

**Required Action**: Define canonical field names and update all documentation.

---

### MAJOR-003: Hierarchy Tree Project Count Mismatch

**Severity**: MAJOR - Data completeness issue

**Problem**: Phase 3 data-model.md hierarchy example shows 12 projects, but there are 13 projects.

**Projects in `task_schema.json`** (13 total):
```
Horizon, Reserve, Avenue 11, Miraya, Aristocrat, Zenith,
Tropical Isle, Jardinia, Sec. 44, Noida, Ramaiah,
Woodscapes, RGA 2, BL Saha
```

**Projects in `data-model.md` Hierarchy Example** (12 total):
- Missing: **Ramaiah**

**Projects in Mock Data** (13 total):
```
Horizon, Reserve, Avenue11, Miraya, Aristocrat, Zenith,
TropicalIsle, Jardinia, Sec44Noida, Ramaiah,
Woodscapes, RGA2, BLSaha
```

**Root Cause**: Ramaiah was added as the 13th project recently, documentation not fully updated.

**Required Action**: Update data-model.md hierarchy example to include Ramaiah.

---

## 4. Minor Issues

### MINOR-001: Type Field Not Explicit in Master Schema

**Severity**: Minor - Implicit derivation

**Problem**: Phase 3 docs reference a `type` field ("parent", "leaf", "milestone"), but `task_schema.json` uses `is_summary` and `is_milestone` booleans.

**Phase 3 data-model.md**:
```
| `type` | "parent" | "leaf" | "milestone" | All | Filter to leaf only |
```

**Master Schema** (`task_schema.json`):
```json
"is_summary": { "type": "boolean" },
"is_milestone": { "type": "boolean" }
```

**Derivation Logic** (from Phase 1 `data-model.md`):
```
is_summary == true  →  type = "parent"
is_milestone == true →  type = "milestone"
otherwise           →  type = "leaf"
```

**Impact**: None - derivation is clear, but could add explicit `type` field for clarity.

**Recommendation**: Consider adding `type` field to Master Schema v2.1 or document the derivation clearly.

---

### MINOR-002: Project ID Format Inconsistency in Mock Data

**Severity**: Minor - Cosmetic

**Problem**: Mock data uses camelCase IDs without spaces, while schema allows spaces.

| Schema Enum Value | Mock Data ID |
|-------------------|--------------|
| `"Avenue 11"` | `"Avenue11"` |
| `"Tropical Isle"` | `"TropicalIsle"` |
| `"Sec. 44, Noida"` | `"Sec44Noida"` |
| `"RGA 2"` | `"RGA2"` |
| `"BL Saha"` | `"BLSaha"` |

**Recommendation**: Standardize on schema enum values OR update schema to use simplified IDs.

---

### MINOR-003: Zone/Region Mapping Not in Schema

**Severity**: Minor - External dependency

**Problem**: The zone/region mapping for each project is not defined in the schema - it's an external lookup.

**Current State**:
- `task_schema.json` defines allowed zone values: `["MZ", "NZ", "SZ", "WEZ"]`
- `task_schema.json` defines allowed region values: `["MZ1", "NZ1", "NZ2", "SZ1", "SZ2", "Kolkata"]`
- Project → Zone → Region mapping is in external configuration

**Impact**: ETL must have access to correct mapping data.

**Recommendation**: Document the authoritative project-to-zone mapping in a single source of truth.

---

### MINOR-004: FY Period Hardcoded in Multiple Places

**Severity**: Minor - Maintenance concern

**Problem**: FY 2025-26 (Apr 1, 2025 - Mar 31, 2026) is hardcoded in multiple files.

**Occurrences**:
- `task_schema.json` lines 303-313 (const values)
- `page1-executive-summary_schema.json` lines 51-52
- `coc-trend.md` lines 83-84
- `spec.md` lines 291-293

**Recommendation**: For future FY changes, ensure all files are updated together. Consider a configuration-driven approach.

---

## 5. Schema Field Mapping Matrix

### Source → Staging Field Mapping

| Master JSON Field | Staging Widget | Staging Field | Status |
|-------------------|----------------|---------------|--------|
| `cost_timeline.weekly_costs[].plan.cost` | coc_trend | `*_series[].plan_cost` | OK |
| `cost_timeline.weekly_costs[].actual.cost` | coc_trend | `*_series[].actual_cost` | OK |
| `cost_timeline.summary.plan_cost_in_fy` | kpi_gauges.aop | `plan` / `plan_ytd` | NAMING ISSUE |
| `cost_timeline.summary.actual_cost_in_fy` | kpi_gauges.aop | `actual` / `actual_ytd` | NAMING ISSUE |
| `dates.sprint.start` | kpi_gauges.sprint | (filter only) | OK |
| `dates.sprint.finish` | kpi_gauges.sprint | (calculation) | OK (schema needs fix) |
| `dates.sprint.duration_days` | kpi_gauges.sprint | (calculation) | OK |
| `cost_plan_total` | kpi_gauges.sprint | (calculation) | OK |
| `progress.percent_complete` | kpi_gauges.sprint | (calculation) | OK |
| `progress.is_complete` | kpi_gauges.sprint | (calculation) | OK |
| `attributes.zone` | hierarchy_tree, filter | Zone key | OK |
| `attributes.region` | hierarchy_tree, filter | Region key | OK |
| `attributes.project_name` | hierarchy_tree, filter, matrix | Project key | OK |

---

## 6. Validation Checklist

### Pre-Implementation Requirements

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Update staging schema with time-mode gauge structure | REQUIRED | CRITICAL-001 |
| 2 | Verify Sprint field name (end vs finish) | REQUIRED | CRITICAL-002 |
| 3 | Add tasks_with_sprint to schema | REQUIRED | MAJOR-001 |
| 4 | Standardize plan/actual field naming | RECOMMENDED | MAJOR-002 |
| 5 | Add Ramaiah to hierarchy example | REQUIRED | MAJOR-003 |
| 6 | Verify project ID format (spaces vs camelCase) | RECOMMENDED | MINOR-002 |

### Schema Completeness Check

| Widget | Schema Defined | Docs Complete | Implementation Ready |
|--------|----------------|---------------|---------------------|
| Global Filter (PG1-CTRL-01) | YES | YES | YES |
| COC Trend (PG1-WIDGET-01) | YES | YES | YES |
| KPI Gauges (PG1-WIDGET-03) | PARTIAL | YES | **NO - needs schema update** |
| Project Matrix (PG1-WIDGET-04) | YES | YES | YES |

---

## 7. Recommended Schema Updates

### 7.1 Updated KPI Gauges Schema

```json
"kpi_gauges": {
  "type": "object",
  "description": "Data for Element PG1-WIDGET-03 (AOP/Sprint Gauges).",
  "properties": {
    "aop": {
      "type": "object",
      "description": "AOP Achievement gauge with time-mode values",
      "properties": {
        "fy": { "$ref": "#/$defs/aop_gauge_data" },
        "quarter": { "$ref": "#/$defs/aop_gauge_data" },
        "month": { "$ref": "#/$defs/aop_gauge_data" }
      },
      "required": ["fy", "quarter", "month"]
    },
    "sprint": {
      "type": "object",
      "description": "Sprint Achievement gauge with time-mode values",
      "properties": {
        "fy": { "$ref": "#/$defs/sprint_gauge_data" },
        "quarter": { "$ref": "#/$defs/sprint_gauge_data" },
        "month": { "$ref": "#/$defs/sprint_gauge_data" }
      },
      "required": ["fy", "quarter", "month"]
    }
  },
  "required": ["aop", "sprint"]
}
```

### 7.2 New $defs for Gauge Data

```json
"$defs": {
  "aop_gauge_data": {
    "type": "object",
    "properties": {
      "achieved_pct": { "type": "number", "description": "Achievement percentage (0-200+)" },
      "status_color": { "type": "string", "enum": ["red", "amber", "green"] },
      "actual": { "type": "number", "description": "Actual cost for time period" },
      "plan": { "type": "number", "description": "Plan cost for time period" }
    },
    "required": ["achieved_pct", "status_color", "actual", "plan"]
  },
  "sprint_gauge_data": {
    "type": "object",
    "properties": {
      "achieved_pct": { "type": "number", "description": "Achievement percentage (0-200+)" },
      "status_color": { "type": "string", "enum": ["red", "amber", "green"] },
      "sprint_actual": { "type": "number", "description": "Sprint actual cost (progress-based)" },
      "sprint_plan": { "type": "number", "description": "Sprint plan cost (prorated)" },
      "tasks_with_sprint": { "type": "integer", "description": "Count of tasks with sprint data" }
    },
    "required": ["achieved_pct", "status_color", "sprint_actual", "sprint_plan", "tasks_with_sprint"]
  },
  "trend_point": {
    // ... existing definition
  }
}
```

---

## 8. Action Items

### Immediate (Before Implementation)

1. **[CRITICAL]** Update `page1-executive-summary_schema.json` with time-mode aware KPI gauge structure
2. **[CRITICAL]** Fix `task_schema.json` Sprint field: Change `dates.sprint.end` to `dates.sprint.finish` (actual output uses "finish")
3. **[MAJOR]** Add `tasks_with_sprint` field to Sprint gauge definition
4. **[MAJOR]** Update `data-model.md` hierarchy example to include Ramaiah

### Recommended (During Implementation)

5. Standardize on `plan`/`actual` field names (without `_ytd` suffix) for time-mode gauges
6. Create authoritative project-zone-region mapping document
7. Verify mock data project IDs match schema enum values

### Future Considerations

8. Add explicit `type` field to Master Schema v2.1
9. Consider configuration-driven FY period instead of hardcoding

---

## 9. Conclusion

The schemas require **2 critical updates** before Phase 3 implementation can proceed:

1. **Staging Schema** (`page1-executive-summary_schema.json`): Add time-mode structure to KPI gauges (fy/quarter/month nesting)
2. **Master Schema** (`task_schema.json`): Fix Sprint field name from `end` to `finish` (actual ETL output already uses "finish")

Additionally, 3 major issues should be addressed:
- Add `tasks_with_sprint` field to Sprint gauge
- Update hierarchy example to include Ramaiah (13th project)
- Standardize field naming (plan/actual vs plan_ytd/actual_ytd)

Once these updates are made, the schemas will be complete and consistent with all transformation documentation and business requirements.

**Estimated Schema Update Effort**: 1-2 hours
**Recommendation**: Update both schemas before starting implementation tasks.

---

## Appendix: Files Analyzed

| File | Purpose | Version |
|------|---------|---------|
| `task_schema.json` | Master JSON schema | v2.0 |
| `page1-executive-summary_schema.json` | Staging output schema | 1.0 |
| `docs/01-xml-to-json/spec.md` | Phase 1 specification | 1.0 |
| `docs/01-xml-to-json/data-model.md` | Phase 1 data model | 1.0 |
| `docs/03-json-to-staging/spec.md` | Phase 3 specification | Draft |
| `docs/03-json-to-staging/data-model.md` | Phase 3 data model | Draft |
| `docs/03-json-to-staging/widgets/coc-trend.md` | COC Trend transformation | 1.0 |
| `docs/03-json-to-staging/widgets/kpi-gauges.md` | KPI Gauges transformation | 1.0 |
| `docs/03-json-to-staging/widgets/project-matrix.md` | Project Matrix transformation | 1.0 |
| `schemas/page-1-executive-simmary/dashboard-element-definition/*.md` | Business requirements | 1.0 |
| `page1-mock-data.json` | Test data | 1.0.0-mock |
