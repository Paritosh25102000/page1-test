# Stage 2 Task List: JSON to CSV Extraction

**Document Version**: 1.0
**Status**: Complete (All tasks done)
**Last Updated**: 2025-12-16

---

## Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| Phase 1: Core Implementation | 4 | Complete |
| Phase 2: CLI Runner | 5 | Complete |
| Phase 3: Testing | 4 | Complete |
| Phase 4: Documentation | 3 | Complete |
| **Total** | **16** | **Complete** |

---

## Phase 1: Core Implementation

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 1.1 | Implement `extract_row()` function | Done | Field mapping logic |
| 1.2 | Implement `extract_to_csv()` function | Done | Single file extraction |
| 1.3 | Implement `batch_extract()` function | Done | Directory processing |
| 1.4 | Implement `generate_extraction_report()` | Done | Statistics report |

---

## Phase 2: CLI Runner

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 2.1 | Create `runner_table_extraction.py` | Done | CLI entry point |
| 2.2 | Add single-file mode | Done | `--file` argument |
| 2.3 | Add batch mode | Done | `--input-dir` argument |
| 2.4 | Add filtering arguments | Done | `--no-summary`, `--no-milestones` |
| 2.5 | Add report generation | Done | `--report` argument |

---

## Phase 3: Testing

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 3.1 | Test with Miraya.json | Done | Verify row count |
| 3.2 | Test null handling | Done | Empty strings for null |
| 3.3 | Batch test all 12 files | Done | All projects |
| 3.4 | Excel/Sheets compatibility test | Done | Loads correctly |

---

## Phase 4: Documentation

| ID | Task | Status | Notes |
|----|------|--------|-------|
| 4.1 | Document CSV schema | Done | Column definitions |
| 4.2 | Document CLI usage | Done | Help text |
| 4.3 | Create extraction report format | Done | JSON schema |

---

## Task Dependencies

```
Phase 1 (Core)
    │
    ├─────────────┐
    ▼             ▼
Phase 2 (CLI)  Phase 4 (Docs)
    │
    ▼
Phase 3 (Testing)
```

---

## Test Coverage

| Function | Tests |
|----------|-------|
| `extract_row()` - summary task | 1 |
| `extract_row()` - leaf task | 1 |
| `extract_row()` - milestone task | 1 |
| `extract_row()` - null handling | 2 |
| `extract_to_csv()` - basic | 1 |
| `extract_to_csv()` - filtering | 2 |
| `batch_extract()` | 1 |
| **Total** | **9** |

---

## Performance Benchmarks

| File | Tasks | Extraction Time |
|------|-------|-----------------|
| Miraya.json | 2,849 | ~1 second |
| Woodscapes.json | 23,494 | ~3 seconds |
| All 12 files | ~110,000 | ~15 seconds |

---

## Known Issues Resolved

| Issue | Resolution | Date |
|-------|------------|------|
| Literal "null" in CSV | Convert to empty string | 2025-12-09 |
| Unicode encoding errors | UTF-8 with no BOM | 2025-12-09 |

---

## Future Enhancements

| ID | Enhancement | Priority | Status |
|----|-------------|----------|--------|
| F.1 | Excel (.xlsx) output | Low | Planned |
| F.2 | Column selection | Low | Planned |
| F.3 | Filter by tower/floor | Low | Planned |
