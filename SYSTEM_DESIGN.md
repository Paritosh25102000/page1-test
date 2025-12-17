# COO Dashboard ETL System Design

**Version**: 1.0
**Date**: 2025-12-16
**Status**: Active

---

## 1. Executive Summary

The COO Dashboard ETL system transforms construction project schedules from Asta Powerproject XML format into dashboard-ready JSON datasets. The system processes ~110,000 tasks across 13 projects through a three-stage pipeline:

1. **Stage 1**: XML → Master JSON (Extraction & Enrichment)
2. **Stage 2**: Master JSON → CSV (Table Export)
3. **Stage 3**: Master JSON → Staging JSON (Dashboard Aggregation)

The final output is a set of pre-aggregated static JSON files consumed by a React dashboard application.

---

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              COO Dashboard ETL System                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌───────────┐  │
│  │   SOURCE DATA   │    │    STAGE 1       │    │    STAGE 2       │    │  STAGE 3  │  │
│  │                 │    │  XML → JSON      │    │  JSON → CSV      │    │ JSON→JSON │  │
│  │  ┌───────────┐  │    │                  │    │                  │    │           │  │
│  │  │ AOP XML   │──┼───▶│  ┌────────────┐  │    │  ┌────────────┐  │    │ ┌───────┐ │  │
│  │  │ (13 files)│  │    │  │ XML Parser │  │    │  │  Table     │  │    │ │ Aggre-│ │  │
│  │  └───────────┘  │    │  └─────┬──────┘  │    │  │ Extractor  │  │    │ │ gator │ │  │
│  │                 │    │        │         │    │  └─────┬──────┘  │    │ └───┬───┘ │  │
│  │  ┌───────────┐  │    │  ┌─────▼──────┐  │    │        │         │    │     │     │  │
│  │  │Sprint XML │──┼───▶│  │Task Builder│  │    │        ▼         │    │     ▼     │  │
│  │  │ (optional)│  │    │  └─────┬──────┘  │    │  ┌────────────┐  │    │ ┌───────┐ │  │
│  │  └───────────┘  │    │        │         │    │  │   CSV      │  │    │ │Staging│ │  │
│  │                 │    │  ┌─────▼──────┐  │    │  │   Files    │  │    │ │ JSON  │ │  │
│  │  ┌───────────┐  │    │  │ Enrichment │  │    │  │ (13 files) │  │    │ │(1/page│ │  │
│  │  │Trade Type │──┼───▶│  │   Engine   │  │    │  └────────────┘  │    │ └───────┘ │  │
│  │  │  Config   │  │    │  └─────┬──────┘  │    │                  │    │           │  │
│  │  └───────────┘  │    │        │         │    └──────────────────┘    └───────────┘  │
│  │                 │    │        ▼         │                                  │        │
│  └─────────────────┘    │  ┌────────────┐  │                                  │        │
│                         │  │Master JSON │  │                                  ▼        │
│                         │  │ (13 files) │──┼─────────────────────────────────────────▶ │
│                         │  └────────────┘  │                                           │
│                         └──────────────────┘                                           │
│                                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │                              DASHBOARD FRONTEND                                  │  │
│  │                                                                                  │  │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐        │  │
│  │   │   Page 1    │   │   Page 2    │   │   Page 3    │   │   Page 4    │        │  │
│  │   │  Executive  │   │   (TBD)     │   │   (TBD)     │   │   (TBD)     │        │  │
│  │   │   Summary   │   │             │   │             │   │             │        │  │
│  │   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘        │  │
│  │                                                                                  │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                  DATA LINEAGE                                         │
└──────────────────────────────────────────────────────────────────────────────────────┘

  SOURCE                    STAGE 1                    STAGE 2            STAGE 3
  ──────                    ───────                    ───────            ───────

  Miraya.xml ──────┐
  Aristocrat.xml ──┤
  Horizon.xml ─────┤
  Reserve.xml ─────┼──▶  runner.py  ──▶  output/json/     output/table/
  Jardinia.xml ────┤     (Python)       ├── Miraya.json   ├── Miraya.csv
  Zenith.xml ──────┤                    ├── Horizon.json  ├── Horizon.csv
  ... (13 total) ──┘                    └── ... (13)      └── ... (13)
                                              │
                                              │
  Sprint XMLs ─────────────────────────────┐ │
  (optional)                                │ │
                                            │ │
  trade-type-cheat-sheet.md ────────────────┘ │
  (LLM enrichment config)                     │
                                              │
                                              ▼
                                        ┌───────────────┐
                                        │ runner_       │     output/staging/
                                        │ staging.py    │──▶  ├── page1.json
                                        │ (Python)      │     ├── page2.json
                                        └───────────────┘     └── ... (per page)
                                                                    │
                                                                    ▼
                                                              ┌───────────────┐
                                                              │   Dashboard   │
                                                              │   Frontend    │
                                                              │   (React)     │
                                                              └───────────────┘
```

---

## 3. Pipeline Stages

### 3.1 Stage 1: XML → Master JSON

**Purpose**: Extract task data from Asta Powerproject XML files and transform into a normalized, enriched JSON format.

**Implementation**: `runner.py` + `src/` modules

#### Input
- **AOP Baseline XML**: 13 files (~171 MB total)
- **Sprint Schedule XML**: Optional, for Sprint date enrichment
- **Trade Type Config**: LLM-based enrichment rules

#### Output
- **Master JSON**: 13 files in `output/json/`
- **QA Reports**: Per-project validation reports in `output/reports/`

#### Key Transformations

| Transformation | Description |
|----------------|-------------|
| Task Extraction | Parse XML Tasks, Assignments, TimephasedData |
| Date Derivation | Derive actual dates from TimephasedData Type=2 |
| Cost Timeline | Calculate weekly cost breakdown for FY 2025-26 |
| Zone/Region Enrichment | Map project → zone/region from lookup table |
| Tower/Floor Enrichment | Extract from task hierarchy patterns |
| Trade Type Enrichment | LLM-based classification (see below) |
| Sprint Enrichment | Match Sprint dates by outline_number |

#### Trade Type Enrichment Details

Trade type classification uses a 3-phase LLM-based approach:

1. **Activity Extraction** (`trade_type_extractor.py`): Extract ~50-150 unique activities per project by traversing task hierarchy
2. **LLM Classification** (`trade_type_classifier.py`): Classify activities via Gemini Flash 2.5 using `trade-type-cheat-sheet.md`
3. **Task Mapping** (`trade_type_mapper.py`): Map classifications back to individual tasks

**Key Features**:
- Context detection: Tower vs Common Area (CA-) vs External (Ext-)
- Cheat sheet reference: 81 activity mappings → 42 trade types
- One API call per project (~$0.002/project)
- Handles spatial leaf tasks by parent traversal

#### Schema
- **Input**: Microsoft Project XML (MSPDI format)
- **Output**: `task_schema.json` (custom schema)

#### Statistics (Current)
```
Total Projects: 13
Total Tasks: 110,424
├── Parent/Summary: 12,270
├── Leaf/Work: 97,977
└── Milestones: 177

Enrichment Rates:
├── Zone/Region: 100%
├── Tower/Floor: ~85%
├── Trade Types: ~99%
└── Sprint Dates: ~96% (where available)
```

---

### 3.2 Stage 2: Master JSON → CSV

**Purpose**: Export selected fields from Master JSON to flat CSV format for external analysis (Excel, BI tools).

**Implementation**: `runner_table_extraction.py` + `src/table_extractor.py`

#### Input
- Master JSON files from Stage 1

#### Output
- CSV files in `output/table/` (one per project)
- Extraction report: `output/table/extraction_report.json`

#### Columns Exported
```
code, title, tower, floor, main_category, sub_category, trade_type,
slab_works, cost_plan_total, start_date_plan, end_date_plan,
start_date_actual, end_date_actual, start_date_sprint, end_date_sprint,
progress
```

#### Use Cases
- Data validation in Excel
- Ad-hoc analysis
- Integration with external BI tools
- Audit trail

---

### 3.3 Stage 3: Master JSON → Staging JSON

**Purpose**: Aggregate task-level data into dashboard-ready JSON datasets, pre-computed for every filter combination.

**Implementation**: `runner_staging.py` + `src/staging/` modules (to be implemented)

#### Input
- Master JSON files from Stage 1

#### Output
- Pre-aggregated JSON per dashboard page
- Currently: `output/staging/page1-executive-summary.json`
- Future: Additional pages (3-4 more planned)

#### Pre-Aggregation Strategy

The staging JSON contains pre-computed data for every possible filter selection:

```json
{
  "dashboard_data": {
    "ALL": { /* Global aggregate */ },
    "ZONE_MZ": { /* Zone aggregate */ },
    "ZONE_NZ": { /* Zone aggregate */ },
    "REG_MZ1": { /* Region aggregate */ },
    "PROJ_Horizon": { /* Project data */ }
  }
}
```

**Benefits**:
- Zero computation in browser
- Instant filter response (<100ms)
- Single static file deployment
- CDN-friendly caching

#### Page 1 Widgets

| Widget | Data Source | Aggregation |
|--------|-------------|-------------|
| Global Filter | `attributes.*` | Unique hierarchy tree |
| COC Trend | `cost_timeline.weekly_costs` | Sum by week/month |
| AOP Gauge | `cost_timeline.summary` | YTD actual / YTD plan |
| Sprint Gauge | `dates.sprint` + costs | Sprint actual / Sprint plan |
| Project Matrix | Per-project COC achievement | Count by bucket |

---

## 4. Component Architecture

### 4.1 Stage 1 Modules

```
src/
├── __init__.py
├── xml_parser.py             # XML parsing with streaming
├── transformers.py           # Field transformation functions
├── task_builder.py           # Task object construction
├── cost_timeline.py          # Weekly cost calculations
├── validators.py             # Schema validation & QA
├── enrichment.py             # Zone/Region/Tower/Floor enrichment
├── trade_type_extractor.py   # Extract unique activities from tasks
├── trade_type_classifier.py  # LLM-based classification (Gemini Flash)
├── trade_type_mapper.py      # Map classifications to individual tasks
├── sprint_enrichment.py      # Sprint schedule integration
└── utils.py                  # Shared utilities
```

### 4.2 Stage 2 Modules

```
src/
└── table_extractor.py      # JSON → CSV extraction
```

### 4.3 Stage 3 Modules (Planned)

```
src/staging/
├── __init__.py
├── aggregator.py           # Core aggregation orchestration
├── hierarchy_builder.py    # Zone/Region/Project tree builder
├── coc_trend_calculator.py # COC trend series generator
├── kpi_calculator.py       # AOP/Sprint gauge values
├── matrix_calculator.py    # Project achievement buckets
└── validators.py           # Staging data validation
```

### 4.4 Runners

| Runner | Stage | Command |
|--------|-------|---------|
| `runner.py` | 1 | `python runner.py --input-dir input/all-aop-baselines` |
| `runner_table_extraction.py` | 2 | `python runner_table_extraction.py` |
| `runner_staging.py` | 3 | `python runner_staging.py --page page1` |

---

## 5. Data Schemas

### 5.1 Schema Inventory

| Schema | Format | Location | Purpose |
|--------|--------|----------|---------|
| Task Schema | JSON Schema | `task_schema.json` | Master JSON validation |
| XML Mapping | JSON | `xml_to_json_mapping.json` | Field transformation rules |
| Page 1 Staging | JSON Schema | `schemas/staging/page1-executive-summary.json` | Dashboard staging validation |
| CSV Schema | Implicit | `table_extraction_plan.md` | Table column definitions |

### 5.2 Master JSON Structure (task_schema.json)

```json
{
  "uid": 12345,
  "wbs": "37300.37500.37600",
  "outline_number": "1.2.3.4.5",
  "name": "Excavation Work",
  "type": "leaf",
  "is_summary": false,
  "is_milestone": false,

  "dates": {
    "plan": { "start": "2025-04-15", "end": "2025-05-30", "duration_days": 45 },
    "manual": { "start": "...", "end": "...", "duration_days": 45 },
    "sprint": { "start": "2025-04-01", "end": "2025-05-15", "duration_days": 44 },
    "actual": { "start": "2025-04-20", "end": null, "duration_days": null }
  },

  "progress": {
    "percent_complete": 65,
    "is_complete": false
  },

  "cost_plan_total": 125000.00,
  "cost_timeline": {
    "fy_period": { "start": "2025-04-01", "end": "2026-03-31" },
    "incoming": { "plan": {...}, "actual": {...} },
    "summary": { "plan_cost_in_fy": 125000, "actual_cost_in_fy": 81250 },
    "weekly_costs": [...]
  },

  "attributes": {
    "project_name": "Miraya",
    "zone": "NZ",
    "region": "NZ1",
    "tower": "Tower A",
    "floor": "Ground Floor",
    "main_category": "Structure",
    "sub_category": "Excavation",
    "trade_type": "Excavation",
    "slab_works": null,
    "context": "tower",
    "confidence": "high"
  }
}
```

### 5.3 Staging JSON Structure (Page 1)

```json
{
  "meta": {
    "generated_at": "2025-12-16T10:30:00Z",
    "data_version": "1.0",
    "currency_unit": "INR"
  },

  "controls": {
    "hierarchy_tree": {
      "MZ": { "MZ1": [{"id": "Horizon", "name": "Horizon"}, ...] },
      "NZ": { "NZ1": [...], "NZ2": [...] }
    },
    "time_modes": {
      "fy": { "label": "Financial Year", "start": "2025-04-01", "end": "2026-03-31" },
      "quarter": { "label": "Current Quarter", "start": "...", "end": "..." },
      "month": { "label": "Looking Glass", "start": "...", "end": "..." }
    }
  },

  "dashboard_data": {
    "ALL": {
      "kpi_gauges": {
        "aop": { "achieved_pct": 87.5, "status_color": "amber" },
        "sprint": { "achieved_pct": 92.0, "status_color": "green" }
      },
      "coc_trend": {
        "fy_series": [...],
        "quarter_series": [...],
        "month_series": [...]
      },
      "project_matrix": {
        "rows": [
          { "label": "MZ", "buckets": { "gt_120": 1, "100_120": 2, ... } }
        ]
      }
    },
    "ZONE_MZ": { ... },
    "PROJ_Horizon": { ... }
  }
}
```

---

## 6. Deployment Architecture

### 6.1 Current Deployment Model

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT MODEL                             │
└─────────────────────────────────────────────────────────────────┘

  ETL Pipeline                              Dashboard App
  ────────────                              ─────────────

  ┌─────────────┐      Static Files        ┌─────────────────────┐
  │   Python    │                          │   React Dashboard   │
  │   ETL       │ ─────▶ page1.json ─────▶ │                     │
  │   Runner    │                          │   (Vite + Mantine)  │
  └─────────────┘                          └─────────────────────┘
        │                                           │
        │                                           │
        ▼                                           ▼
  ┌─────────────┐                          ┌─────────────────────┐
  │  Local      │                          │   Web Server /      │
  │  Filesystem │                          │   CDN / S3          │
  └─────────────┘                          └─────────────────────┘
```

### 6.2 File Deployment

| Output | Destination | Update Frequency |
|--------|-------------|------------------|
| `page1.json` | `frontend/public/data/` | On schedule refresh |
| `page2.json` (future) | `frontend/public/data/` | On schedule refresh |
| CSV exports | Internal analysis | As needed |

### 6.3 Refresh Strategy

```
Manual Trigger:
  1. Receive updated XML files
  2. Run Stage 1: python runner.py --input-dir input/all-aop-baselines
  3. Run Stage 3: python runner_staging.py --page page1
  4. Copy staging JSON to frontend: cp output/staging/*.json frontend/public/data/
  5. Rebuild/redeploy frontend (if needed)
```

---

## 7. Error Handling & Monitoring

### 7.1 Error Handling Strategy

| Stage | Error Type | Handling |
|-------|-----------|----------|
| Stage 1 | XML parse error | Log and skip file, continue with others |
| Stage 1 | Missing required field | Use null, log warning |
| Stage 1 | LLM API failure | Retry with exponential backoff, fallback to "Unknown" |
| Stage 2 | JSON read error | Log and skip file |
| Stage 3 | Aggregation error | Log and fail early (data integrity critical) |

### 7.2 Logging

```
output/
└── logs/
    ├── etl_YYYYMMDD_HHMMSS.log   # Stage 1 execution log
    └── staging_YYYYMMDD.log       # Stage 3 execution log (future)
```

**Log Levels**:
- `INFO`: Processing progress, file counts
- `WARNING`: Missing optional fields, low match rates
- `ERROR`: Parse failures, API errors
- `DEBUG`: Detailed transformation steps

### 7.3 Quality Assurance

| Checkpoint | Validation |
|------------|------------|
| Stage 1 Output | Schema validation against `task_schema.json` |
| Stage 1 Output | Sample validation (100 tasks per project) |
| Stage 2 Output | Row count matches task count |
| Stage 3 Output | Schema validation against staging schema |
| Stage 3 Output | Key coverage (all filter combinations present) |

---

## 8. Security Considerations

### 8.1 Data Classification

| Data Type | Classification | Handling |
|-----------|----------------|----------|
| Project schedules | Business Confidential | Access controlled |
| Cost data | Business Confidential | No external exposure |
| Zone/Region mappings | Internal | Hardcoded in config |
| Dashboard output | Internal | Served to authenticated users |

### 8.2 Access Control

- **Source XML**: File system permissions
- **ETL outputs**: File system permissions
- **Dashboard**: Authentication via parent enterprise system (iframe)

### 8.3 LLM Integration

- API keys stored in environment variables
- No PII in prompts
- Task names may contain project details (acceptable for internal LLM)

---

## 9. Performance Characteristics

### 9.1 Stage 1 Performance

| Metric | Value |
|--------|-------|
| Total processing time | ~5-10 minutes (with LLM enrichment) |
| Largest file (Woodscapes) | ~30 seconds |
| Memory usage | <500MB |
| LLM calls | ~1000 batches (98k leaf tasks / 100 batch size) |

### 9.2 Stage 2 Performance

| Metric | Value |
|--------|-------|
| Total processing time | <30 seconds |
| Per-file average | ~2 seconds |

### 9.3 Stage 3 Performance (Expected)

| Metric | Target |
|--------|--------|
| Total processing time | <2 minutes |
| Memory usage | <1GB |
| Output file size | <5MB per page |

### 9.4 Dashboard Performance

| Metric | Target |
|--------|--------|
| Initial load | <3 seconds |
| Filter change | <100ms (instant) |
| Time mode switch | <100ms |

---

## 10. Extensibility

### 10.1 Adding New Dashboard Pages

1. Define page schema in `schemas/staging/pageN-name.json`
2. Create page-specific calculators in `src/staging/`
3. Register page in `runner_staging.py`
4. Create frontend components

### 10.2 Adding New Enrichments

1. Implement enrichment module in `src/`
2. Add CLI flag to `runner.py`
3. Update `task_schema.json` if new fields added
4. Update downstream stages as needed

### 10.3 Adding New Data Sources

1. Implement parser for new format
2. Map to existing `task_schema.json` structure
3. Integrate into Stage 1 pipeline

---

## 11. Future Roadmap

### 11.1 Planned Dashboard Pages

| Page | Status | Description |
|------|--------|-------------|
| Page 1: Executive Summary | In Progress | KPIs, trends, risk matrix |
| Page 2: TBD | Analysis | Under design |
| Page 3: TBD | Analysis | Under design |
| Page 4: TBD | Analysis | Under design |

### 11.2 Potential Enhancements

- **Real-time refresh**: Schedule-triggered ETL runs
- **Incremental processing**: Process only changed files
- **API endpoint**: Replace static files with REST API
- **Multi-tenant**: Support multiple organizations
- **Historical tracking**: Store snapshots for trend analysis

---

## 12. Related Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Stage 1 Specification | `docs/01-xml-to-json/spec.md` | Detailed Stage 1 requirements |
| Stage 2 Specification | `docs/02-json-to-csv/spec.md` | Detailed Stage 2 requirements |
| Stage 3 Specification | `docs/03-json-to-staging/spec.md` | Detailed Stage 3 requirements |
| Trade Type Enrichment Plan | `trade_type_enrichment_plan.md` | LLM classification approach |
| Trade Type Cheat Sheet | `trade-type-cheat-sheet.md` | 81 activity mappings → 42 trade types |
| Dashboard Frontend Spec | `../specs/001-page1-executive-summary/spec.md` | React dashboard requirements |
| Complete Documentation | `complete_documentation.md` | Field-level reference |

---

## Appendix A: Project-Zone Mapping

| Project (Canonical) | XML Filename | Zone | Region |
|---------------------|--------------|------|--------|
| Horizon | Azadnagar.xml | MZ | MZ1 |
| Reserve | Bigbull-Reserve.xml | MZ | MZ1 |
| Avenue 11 | OneM.xml | MZ | MZ1 |
| Miraya | Miraya.xml | NZ | NZ1 |
| Aristocrat | Aristocrat.xml | NZ | NZ1 |
| Zenith | Zenith.xml | NZ | NZ1 |
| Tropical Isle | Tropical Isle 146.xml | NZ | NZ2 |
| Jardinia | Jardinia.xml | NZ | NZ2 |
| Sec. 44, Noida | Riverine.xml | NZ | NZ2 |
| Ramaiah | Ramaiah.xml | SZ | SZ2 |
| Woodscapes | Woodscapes.xml | SZ | SZ1 |
| RGA 2 | RGA Land2.xml | SZ | SZ1 |
| BL Saha | BLSaha.xml | WEZ | Kolkata |

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **AOP** | Annual Operating Plan - baseline schedule for the financial year |
| **Sprint** | Accelerated "squeezed" schedule for bonus-eligible targets |
| **COC** | Cost of Construction |
| **COO** | Chief Operating Officer |
| **FY** | Financial Year (April 1 - March 31 in India) |
| **YTD** | Year to Date |
| **Leaf Task** | Work task with no children (actual work item) |
| **Parent Task** | Summary task containing child tasks |
| **Milestone** | Zero-duration marker task |
| **TimephasedData** | MS Project structure containing work distributed over time |
| **Staging JSON** | Pre-aggregated dashboard data |

---

**End of System Design Document**
