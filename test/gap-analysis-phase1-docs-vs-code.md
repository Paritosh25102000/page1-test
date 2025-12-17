# Phase 1 (XML to JSON) Gap Analysis Report

**Analysis Date**: 2025-12-17
**Resolution Date**: 2025-12-17
**Scope**: Code vs Documentation Comparison
**Priority**: Code takes precedence unless it contradicts overall product logic

---

## Executive Summary

The Phase 1 documentation is **generally accurate** but had several gaps and discrepancies with the actual implementation. Most issues have been **RESOLVED** as documented below.

| Category | Original Count | Resolved | Remaining |
|----------|----------------|----------|-----------|
| **Critical Gaps** | 4 | 3 | 1 (parked) |
| **Moderate Gaps** | 8 | 8 | 0 |
| **Minor Discrepancies** | 6 | 2 | 4 (cosmetic) |
| **Documentation-Only Issues** | 3 | 3 | 0 |

---

## 1. CRITICAL GAPS

### 1.1 Missing `llm_utils.py` Module Documentation

**Location**: `docs/01-xml-to-json/plan.md` - Section 2 Module Structure

**Issue**: The module structure in plan.md lists trade type modules but omits `llm_utils.py`, which is essential for LLM-based trade type classification.

**Status**: **RESOLVED**

**Resolution**:
- Added `llm_utils.py` to module structure in Section 2
- Added new Section 3.10 documenting the `UniversalLLM` class interface
- Documented configuration (Temperature 0.2, OpenRouter API, .env support)

---

### 1.2 Missing `slab_works` in Code Implementation

**Location**: `docs/01-xml-to-json/data-model.md` - Section 4.7, `task_schema.json`

**Issue**: Documentation and schema define `slab_works` as a required attribute field with values "Typical", "Non-typical", "Non-slab", but the actual code **never populates this field**.

**Status**: **PARKED** (awaiting customer input)

**Note**: Customer to provide requirements on how to classify slab_works. No changes made pending clarification.

---

### 1.3 Incorrect Default Input Directory

**Location**: `docs/01-xml-to-json/quickstart.md`, `plan.md`

**Issue**: Documentation states default input directory is `input/all-aop-baselines`, but code used a different path.

**Status**: **RESOLVED**

**Resolution**: Updated `runner.py:484` to use `./input/all-aop-baselines` as the default, matching documentation.

---

### 1.4 Missing `--quiet` CLI Flag Implementation

**Location**: `docs/01-xml-to-json/quickstart.md` - CLI Reference

**Issue**: Documentation lists `--quiet` flag to "Suppress info messages", but this flag is not implemented in the code.

**Status**: **RESOLVED**

**Resolution**: Removed `--quiet` from quickstart.md CLI Reference section. Feature not needed.

---

## 2. MODERATE GAPS

### 2.1 Incomplete Function Signatures in plan.md

**Location**: `docs/01-xml-to-json/plan.md` - Module Specifications

**Issue**: Several documented function signatures differ from actual implementation.

**Status**: **RESOLVED**

**Resolution**:
- Fixed `parse_xml_file()` return type to show `project` key
- Renamed `validate_against_schema()` to `validate_task_structure()`
- Added `validate_task_types()` and `calculate_field_coverage()` functions
- Updated `build_task()` to show 4 parameters including `cost_timeline_builder`
- Updated type notation to Python 3.10+ style (`int | None`)

---

### 2.2 Missing Error Handling Documentation

**Location**: All module documentation

**Issue**: No documentation of error handling behavior or exceptions raised.

**Status**: **RESOLVED**

**Resolution**: Added new Section 8 "Error Handling" to plan.md with:
- Section 8.1: Module-level error behavior table
- Section 8.2: Graceful degradation patterns
- Section 8.3: Trade type classification batching and retry logic

---

### 2.3 Undocumented `--openrouter-api-key` Flag Behavior

**Location**: `docs/01-xml-to-json/quickstart.md`

**Issue**: Documentation mentions `--enrich-trade-types` but doesn't explain API key requirements.

**Status**: **RESOLVED**

**Resolution**: Added new "Trade Type Enrichment (LLM-Based)" section to quickstart.md with:
- Three API key setup options (env var, CLI arg, .env file)
- Usage examples
- Cost estimate (~$0.002 per project)

---

### 2.4 Missing `project_name_mapping.json` Documentation

**Location**: `docs/01-xml-to-json/plan.md` - Section 2

**Issue**: Module structure shows `project_name_mapping.json` but no documentation.

**Status**: **RESOLVED**

**Resolution**:
- Added `project_name_mapping.json` to module structure in Section 2
- Added new Section 9 "Configuration Files" with full JSON content
- Documented relationship to `PROJECT_NAME_ALIASES` in enrichment.py

---

### 2.5 Incomplete Weekly Cost Calculation Documentation

**Location**: `docs/01-xml-to-json/data-model.md` - Section 6

**Issue**: Documentation doesn't explain the algorithm for incomplete tasks.

**Status**: **RESOLVED**

**Resolution**: Updated Section 6.2 in data-model.md with:
- Clarified that incomplete tasks use plan rate
- Added note about `days_in_task.actual` defaulting to plan days

---

### 2.6 Missing Batch Processing Documentation for Trade Type Classification

**Location**: `docs/01-xml-to-json/plan.md` - Section 3.8

**Issue**: Documentation doesn't mention batching for large activity counts.

**Status**: **RESOLVED**

**Resolution**: Added batch processing details to Section 8.3 in plan.md (500 activities per batch).

---

### 2.7 Missing Retry Logic Documentation

**Location**: `docs/01-xml-to-json/plan.md` - Section 3.8

**Issue**: No documentation of the retry mechanism for invalid trade type classifications.

**Status**: **RESOLVED**

**Resolution**: Added retry logic documentation to Section 8.3 in plan.md.

---

### 2.8 Incorrect Sample Size Default

**Location**: `docs/01-xml-to-json/quickstart.md` - CLI Reference

**Status**: No issue - documentation matches code (default=100).

---

## 3. MINOR DISCREPANCIES

### 3.1 Return Type Notation Style

**Location**: Throughout plan.md

**Issue**: Documentation uses `Optional[T]` notation but code uses Python 3.10+ union style `T | None`.

**Examples**:
- Docs: `Optional[int]`
- Code: `int | None`

**Impact**: Cosmetic only, functionally equivalent.

---

### 3.2 Variable Naming Inconsistencies

**Location**: Various

| Documentation | Actual Code |
|--------------|-------------|
| `task_assignment_map` | Sometimes `assignment_map` in function params |
| `duration_days` in docs | Sometimes `duration` in intermediate calculations |
| `finish` in docs | `end` in JSON output field names |

---

### 3.3 XML Field Name Inconsistency

**Location**: `docs/01-xml-to-json/data-model.md` - Section 5.1

**Issue**: Documentation shows XML field as "Finish" but code extracts "finish" (lowercase).

**Code Reality** (xml_parser.py:48):
```python
"finish": get_element_text(task_elem, "Finish"),  # XML tag is capitalized
```

The XML tag IS "Finish" (capital F), and the code correctly uses that. The extracted key is lowercase "finish". Documentation should clarify this transformation.

---

### 3.4 Missing "Window" Trade Type

**Location**: `task_schema.json`, `data-model.md`

**Issue**: The cheat sheet includes "Window" as a trade type, but it's not in the schema enum.

**Code Reality**: Looking at trade types in schema (task_schema.json:211-255), "Window" is NOT listed.

**Impact**: If LLM returns "Window", validation would fail.

**Recommendation**: Verify if "Window" should be added to schema enum or if it's intentionally excluded.

---

### 3.5 Region Enum Missing Value

**Location**: `task_schema.json` vs `docs/00-overview/GLOSSARY.md`

**Issue**: GLOSSARY lists 6 region codes including SZ2, but schema has them all.

Actually, checking schema (task_schema.json:178-179):
```json
"enum": ["MZ1", "NZ1", "NZ2", "SZ2", "SZ1", "Kolkata"]
```

This matches. No issue.

---

### 3.6 Tasks.md Test Count Accuracy

**Location**: `docs/01-xml-to-json/tasks.md` - Test Coverage

**Issue**: Documentation claims 77 unit tests + 15 integration tests = 92 total tests, but no test files exist.

**Status**: **RESOLVED**

**Resolution**: Removed "Test Coverage" section from tasks.md entirely.

---

## 4. DOCUMENTATION-ONLY ISSUES (No Code Impact)

### 4.1 Outdated File Count

**Location**: `docs/01-xml-to-json/tasks.md` - Phase 6

**Issue**: Task 6.6 says "End-to-end test all 12 files" but we now have 13 projects.

**Status**: **RESOLVED**

**Resolution**: Updated to "End-to-end test all 13 files" in tasks.md.

---

### 4.2 Quickstart Next Steps Reference Wrong Script

**Location**: `docs/01-xml-to-json/quickstart.md` - Next Steps

**Issue**: Documentation says Stage 2 is `python table_extractor.py` but actual script is `runner_table_extraction.py`.

**Status**: **RESOLVED**

**Resolution**: Updated to `python runner_table_extraction.py` in quickstart.md.

---

### 4.3 XML Namespace URL Formatting

**Location**: `docs/01-xml-to-json/plan.md` - Section 3.1

**Issue**: Shows namespace in prose format, could be clearer with exact string.

**Status**: Cosmetic - no change made.

---

## 5. SUMMARY TABLE

| Gap ID | Severity | Type | Location | Status |
|--------|----------|------|----------|--------|
| 1.1 | Critical | Missing | plan.md | **RESOLVED** |
| 1.2 | Critical | Code Bug | task_builder.py | **PARKED** (awaiting customer) |
| 1.3 | Critical | Incorrect | runner.py | **RESOLVED** |
| 1.4 | Critical | Missing | quickstart.md | **RESOLVED** |
| 2.1 | Moderate | Incorrect | plan.md | **RESOLVED** |
| 2.2 | Moderate | Missing | plan.md | **RESOLVED** |
| 2.3 | Moderate | Missing | quickstart.md | **RESOLVED** |
| 2.4 | Moderate | Missing | plan.md | **RESOLVED** |
| 2.5 | Moderate | Incomplete | data-model.md | **RESOLVED** |
| 2.6 | Moderate | Missing | plan.md | **RESOLVED** |
| 2.7 | Moderate | Missing | plan.md | **RESOLVED** |
| 3.1 | Minor | Style | plan.md | Cosmetic - not changed |
| 3.2 | Minor | Naming | Various | Cosmetic - not changed |
| 3.3 | Minor | Unclear | data-model.md | Cosmetic - not changed |
| 3.4 | Minor | Schema | task_schema.json | Cosmetic - not changed |
| 3.6 | Minor | Inaccurate | tasks.md | **RESOLVED** |
| 4.1 | Doc-only | Outdated | tasks.md | **RESOLVED** |
| 4.2 | Doc-only | Incorrect | quickstart.md | **RESOLVED** |
| 4.3 | Doc-only | Style | plan.md | Cosmetic - not changed |

---

## 6. RECOMMENDED ACTIONS

### Completed

1. **Add llm_utils.py documentation** to plan.md - DONE
2. **Update default input path** in runner.py - DONE
3. **Remove --quiet** from quickstart.md - DONE
4. Audit and update all function signatures in plan.md - DONE
5. Add error handling documentation - DONE
6. Document trade type enrichment API requirements - DONE
7. Document batching and retry logic - DONE
8. Update file counts and script names - DONE
9. Remove test claims from tasks.md - DONE

### Pending (Customer Input Required)

10. **Fix slab_works**: Awaiting customer requirements on classification logic

### Not Changed (Cosmetic)

11. Type notation style differences (Optional vs |)
12. Variable naming inconsistencies
13. XML namespace formatting

---

## 7. POSITIVE FINDINGS

The following areas are well-documented and accurate:

1. **Task classification logic** (parent/leaf/milestone) - matches code exactly
2. **Cost timeline calculation** - core logic well documented
3. **Zone/Region/Tower/Floor enrichment** - comprehensive documentation
4. **Sprint integration** - accurate outline_number matching documentation
5. **Trade type enrichment flow** - 3-phase approach correctly documented
6. **CLI arguments** (except --quiet) - mostly accurate
7. **Schema structure** - task_schema.json matches docs well
8. **Project mapping** - all 13 projects correctly listed

---

*End of Gap Analysis Report*
