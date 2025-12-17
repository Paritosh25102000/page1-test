# Stage 1 Task List: XML to JSON Conversion

**Document Version**: 1.0
**Status**: Complete (All tasks done)
**Last Updated**: 2025-12-16

---

## Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| Phase 1: Infrastructure | 5 | Complete |
| Phase 2: XML Parsing | 6 | Complete |
| Phase 3: Task Building | 7 | Complete |
| Phase 4: Cost Timeline | 6 | Complete |
| Phase 5: Validation | 5 | Complete |
| Phase 6: Runner/CLI | 6 | Complete |
| Phase 7: Enrichment | 10 | Complete |
| Phase 8: Sprint Integration | 8 | Complete |
| **Total** | **53** | **Complete** |

---

## Phase 1: Infrastructure

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 1.1 | Create `src/` directory structure | Done | |
| 1.2 | Implement `src/utils.py` logging setup | Done | |
| 1.3 | Implement file I/O utilities | Done | load_json, save_json |
| 1.4 | Implement directory utilities | Done | ensure_dir, get_xml_files |
| 1.5 | Create unit test scaffolding | Done | pytest structure |

---

## Phase 2: XML Parsing

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 2.1 | Implement `parse_xml_file()` | Done | Main entry point |
| 2.2 | Implement `extract_tasks()` | Done | Task element extraction |
| 2.3 | Implement `extract_assignments()` | Done | Assignment extraction |
| 2.4 | Handle XML namespace | Done | MS Project namespace |
| 2.5 | Build task-assignment mapping | Done | For actual dates |
| 2.6 | Test with Miraya.xml | Done | Smallest file (2,849 tasks) |

---

## Phase 3: Task Building

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 3.1 | Implement `determine_task_type()` | Done | parent/leaf/milestone |
| 3.2 | Implement `build_dates_object()` | Done | plan/manual/sprint/actual |
| 3.3 | Implement actual date derivation | Done | From TimephasedData |
| 3.4 | Implement `build_progress_object()` | Done | percent_complete |
| 3.5 | Implement `build_attributes_placeholder()` | Done | Project name only |
| 3.6 | Implement `build_task()` main function | Done | Full transformation |
| 3.7 | Verify output matches sample_tasks.json | Done | Structure validation |

---

## Phase 4: Cost Timeline

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 4.1 | Implement FY period constants | Done | 2025-04-01 to 2026-03-31 |
| 4.2 | Implement `get_week_boundaries()` | Done | Monday-Sunday |
| 4.3 | Implement `calculate_incoming_cost()` | Done | Pre-FY costs |
| 4.4 | Implement `generate_weekly_costs()` | Done | Weekly breakdown |
| 4.5 | Implement `calculate_cost_timeline()` | Done | Full timeline |
| 4.6 | Test weekly calculations | Done | Known inputs |

---

## Phase 5: Validation

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 5.1 | Implement `validate_against_schema()` | Done | JSON Schema |
| 5.2 | Implement `sample_validation()` | Done | Compare to XML |
| 5.3 | Implement `generate_qa_report()` | Done | Per-project report |
| 5.4 | Create field coverage statistics | Done | |
| 5.5 | Test validation with all files | Done | |

---

## Phase 6: Runner/CLI

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 6.1 | Create `runner.py` with argparse | Done | CLI interface |
| 6.2 | Implement `process_single_file()` | Done | Single file processing |
| 6.3 | Implement batch processing | Done | All files |
| 6.4 | Add `--dry-run` mode | Done | Parse without saving |
| 6.5 | Add `--validate-only` mode | Done | Validation only |
| 6.6 | End-to-end test all 13 files | Done | Full pipeline |

---

## Phase 7: Enrichment

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 7.1 | Create project name aliases | Done | XML → Canonical |
| 7.2 | Create zone/region mapping | Done | Lookup table |
| 7.3 | Implement `enrich_zone_region()` | Done | Apply to tasks |
| 7.4 | Implement tower pattern extraction | Done | Regex patterns |
| 7.5 | Implement floor pattern extraction | Done | Regex patterns |
| 7.6 | Implement basement normalization | Done | B1 → Basement 1 |
| 7.7 | Implement `build_task_hierarchy()` | Done | WBS hierarchy |
| 7.8 | Implement `enrich_tower_floor()` | Done | Hierarchy traversal |
| 7.9 | Add enrichment CLI arguments | Done | --no-enrich-* |
| 7.10 | Test enrichment on all projects | Done | Validate coverage |

---

## Phase 8: Sprint Integration

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 8.1 | Implement `parse_sprint_schedule()` | Done | Sprint XML parser |
| 8.2 | Implement outline_number matching | Done | 99.5% match rate |
| 8.3 | Implement `match_sprint_to_aop()` | Done | Matching logic |
| 8.4 | Implement `enrich_sprint_dates()` | Done | Single file |
| 8.5 | Implement `batch_enrich_sprint()` | Done | All files |
| 8.6 | Add Sprint CLI arguments | Done | --sprint-dir |
| 8.7 | Add Sprint statistics to reports | Done | Match rates |
| 8.8 | Validate Sprint date consistency | Done | Dates ordering |

---

## Task Dependencies

```
Phase 1 (Infrastructure)
    │
    ▼
Phase 2 (XML Parsing)
    │
    ├──────────────────┐
    ▼                  ▼
Phase 3 (Task Build)  Phase 7 (Enrichment) ←─── Parallel
    │                  │
    ▼                  │
Phase 4 (Cost Timeline)│
    │                  │
    ▼                  │
Phase 5 (Validation)───┘
    │
    ▼
Phase 6 (Runner/CLI)
    │
    ▼
Phase 8 (Sprint Integration)
```

---

## Parallel Execution Opportunities

| Tasks | Can Run In Parallel |
|-------|---------------------|
| 3.1-3.5 | Yes (independent functions) |
| 4.2-4.4 | Yes (independent calculations) |
| 7.4-7.6 | Yes (independent extractors) |
| 8.1-8.3 | Yes (independent modules) |

---

## Known Issues Resolved

| Issue | Resolution | Date |
|-------|------------|------|
| Actual dates from Task fields unreliable | Use TimephasedData Type=2 | 2025-12-10 |
| Large file memory issues | Implemented iterparse | 2025-12-09 |
| Tower extraction false positives | Added exclusion patterns | 2025-12-11 |
| Basement normalization inconsistent | Added normalization rules | 2025-12-11 |
| Sprint UID mismatch | Switched to outline_number | 2025-12-12 |
| actual.end null for incomplete tasks | Fixed logic to derive from plan.end | 2025-12-15 |

---

## Future Enhancements

| ID | Enhancement | Priority | Status |
|----|-------------|----------|--------|
| F.1 | Trade type LLM caching | Medium | Done |
| F.2 | Incremental processing | Low | Planned |
| F.3 | Multi-threading for batch | Low | Planned |
| F.4 | Progress bars for CLI | Low | Done |
| F.5 | Export to Parquet format | Medium | Planned |
