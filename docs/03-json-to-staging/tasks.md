# Stage 3: JSON → Staging Tasks

**Stage**: 03-json-to-staging
**Date**: 2025-12-16
**Prerequisites**: spec.md, plan.md, data-model.md

---

## Format

`[ID] [P?] [Phase] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Phase]**: Implementation phase

---

## Phase 1: Core Infrastructure

**Purpose**: Package structure and utility modules

- [X] T001 Create `src/staging/__init__.py` package file
- [X] T002 [P] Implement `src/staging/time_utils.py` with FY/Quarter/Month date helpers
- [ ] T003 [P] Write unit tests for time_utils (test/staging/test_time_utils.py)
- [X] T004 Implement `src/staging/hierarchy_builder.py` with build_hierarchy_tree()
- [ ] T005 Write unit tests for hierarchy_builder

**Checkpoint**: Time utilities and hierarchy builder tested and working

---

## Phase 2: Calculators

**Purpose**: Implement widget calculation modules

### COC Trend Calculator
- [X] T006 Implement `aggregate_weekly_costs()` in coc_trend_calculator.py
- [X] T007 [P] Implement `generate_fy_series()` with monthly aggregation
- [X] T008 [P] Implement `generate_quarter_series()` with date filtering
- [X] T009 [P] Implement `generate_month_series()` for looking glass
- [X] T010 Implement `calculate_coc_trend()` orchestration function
- [ ] T011 Write unit tests for coc_trend_calculator

### KPI Calculator
- [X] T012 [P] Implement `calculate_aop_gauge()` in kpi_calculator.py
- [X] T013 [P] Implement `calculate_sprint_gauge()` with Sprint filter
- [X] T014 [P] Implement `get_status_color()` threshold function
- [X] T015 Implement `calculate_kpi_gauges()` orchestration
- [ ] T016 Write unit tests for kpi_calculator

### Matrix Calculator
- [X] T017 Implement `calculate_project_achievements()` in matrix_calculator.py
- [X] T018 [P] Implement `bucket_achievement()` function
- [X] T019 [P] Implement `generate_zone_rows()` for ALL view
- [X] T020 [P] Implement `generate_region_rows()` for Zone view
- [X] T021 Implement `calculate_project_matrix()` orchestration
- [ ] T022 Write unit tests for matrix_calculator

**Checkpoint**: All calculators tested with sample data

---

## Phase 3: Aggregator Integration

**Purpose**: Wire calculators together and create runner

- [X] T023 Implement `load_all_projects()` in aggregator.py
- [X] T024 [P] Implement `generate_filter_keys()` from hierarchy
- [X] T025 [P] Implement `filter_tasks()` by key type
- [X] T026 [P] Implement `build_meta()` for output metadata
- [X] T027 [P] Implement `build_time_modes()` from current date
- [X] T028 Implement `generate_staging_data()` main orchestration
- [ ] T029 Write integration tests for aggregator

### Validators
- [X] T030 Implement `validate_staging_output()` in validators.py
- [ ] T031 [P] Add schema validation against JSON Schema
- [X] T032 [P] Add completeness checks (all filter keys present)
- [X] T033 [P] Add data integrity checks (non-negative values, etc.)
- [ ] T034 Write unit tests for validators

### CLI Runner
- [X] T035 Create `runner_staging.py` CLI entry point
- [X] T036 [P] Add --page argument support
- [X] T037 [P] Add --dry-run and --validate-only modes
- [X] T038 [P] Add --current-date override for testing
- [X] T039 Add logging and progress output

**Checkpoint**: Runner generates valid staging JSON for single project

---

## Phase 4: Testing & Validation

**Purpose**: End-to-end testing with all projects

- [X] T040 Integration test with Miraya.json only
- [X] T041 Test with all 13 project files combined
- [X] T042 Validate output against page1-executive-summary_schema.json schema
- [X] T043 Verify all filter keys present (24 keys generated)
- [X] T044 Benchmark performance (achieved: 2.4 seconds, target: <2 minutes) ✓
- [X] T045 Memory profiling (target: <1GB) ✓
- [X] T046 Verify output file size (0.26 MB, target: <5MB) ✓

**Checkpoint**: Full pipeline works for all projects

---

## Phase 5: Documentation & Polish

**Purpose**: Final documentation and cleanup

- [ ] T047 Create `quickstart.md` with usage examples
- [ ] T048 [P] Create `contracts/staging_schema.py` Python dataclasses
- [ ] T049 [P] Update SYSTEM_DESIGN.md with Stage 3 details
- [ ] T050 Add inline documentation to all modules
- [ ] T051 Create staging_report.json output for QA

**Checkpoint**: Stage 3 fully documented and ready for use

---

## Dependencies

### Task Dependencies

```
T001 ─┬─▶ T002 ─▶ T003
      └─▶ T004 ─▶ T005

T005 ─┬─▶ T006 ─▶ T007, T008, T009 ─▶ T010 ─▶ T011
      │
      ├─▶ T012, T013, T014 ─▶ T015 ─▶ T016
      │
      └─▶ T017 ─▶ T018, T019, T020 ─▶ T021 ─▶ T022

T011, T016, T022 ─▶ T023 ─▶ T024, T025, T026, T027 ─▶ T028 ─▶ T029

T029 ─▶ T030 ─▶ T031, T032, T033 ─▶ T034

T034 ─▶ T035 ─▶ T036, T037, T038 ─▶ T039

T039 ─▶ T040 ─▶ T041 ─▶ T042 ─▶ T043 ─▶ T044, T045, T046

T046 ─▶ T047, T048, T049, T050, T051
```

### Parallel Opportunities

**Phase 1**:
- T002, T003 can run in parallel (time utils + tests)
- T004, T005 sequential after T001

**Phase 2**:
- T007, T008, T009 parallel (series generators)
- T012, T013, T014 parallel (gauge functions)
- T018, T019, T020 parallel (row generators)

**Phase 3**:
- T024, T025, T026, T027 parallel (helper functions)
- T031, T032, T033 parallel (validation checks)
- T036, T037, T038 parallel (CLI arguments)

**Phase 5**:
- T047, T048, T049 parallel (different docs)

---

## Estimated Effort

| Phase | Tasks | Est. Hours |
|-------|-------|------------|
| Phase 1: Core Infrastructure | 5 | 2-3 |
| Phase 2: Calculators | 17 | 6-8 |
| Phase 3: Integration | 17 | 4-6 |
| Phase 4: Testing | 7 | 2-3 |
| Phase 5: Documentation | 5 | 2-3 |
| **Total** | **51** | **16-23** |

---

## MVP Scope

**Minimum Viable Staging ETL**: Phase 1-4

Required for MVP:
- Core infrastructure (T001-T005)
- All calculators (T006-T022)
- Basic aggregator (T023-T029)
- Basic validator (T030)
- CLI runner (T035, T039)
- Basic testing (T040-T043)

Can defer:
- Schema validation (T031)
- Advanced validation (T032-T034)
- Performance optimization (T044-T046)
- Full documentation (T047-T051)
