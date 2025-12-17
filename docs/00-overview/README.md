# COO Dashboard ETL Pipeline Documentation

**Version**: 1.0
**Last Updated**: 2025-12-16

---

## Overview

This documentation covers the end-to-end ETL pipeline for the COO (Chief Operating Officer) Dashboard. The pipeline transforms construction project schedule data from Asta Powerproject XML exports into dashboard-ready JSON for real-time visualization.

---

## Quick Links

| Document | Description |
|----------|-------------|
| [SYSTEM_DESIGN.md](../SYSTEM_DESIGN.md) | End-to-end architecture and design |
| [GLOSSARY.md](./GLOSSARY.md) | Terms and definitions |

---

## Pipeline Stages

### Stage 1: XML to JSON
**Input**: Asta Powerproject XML files
**Output**: Master JSON (enriched task data)

**Enrichment includes**:
- Zone/Region lookup by project
- Tower/Floor extraction from hierarchy
- Trade Type classification via LLM (Gemini Flash 2.5)
- Sprint dates integration

- [Specification](../01-xml-to-json/spec.md)
- [Implementation Plan](../01-xml-to-json/plan.md)
- [Data Model](../01-xml-to-json/data-model.md)
- [Task List](../01-xml-to-json/tasks.md)
- [Quickstart Guide](../01-xml-to-json/quickstart.md)
- [Python Contracts](../01-xml-to-json/contracts/task_schema.py)
- [Trade Type Enrichment Plan](../../trade_type_enrichment_plan.md)

### Stage 2: JSON to CSV
**Input**: Master JSON files
**Output**: CSV tables for analysis

- [Specification](../02-json-to-csv/spec.md)
- [Implementation Plan](../02-json-to-csv/plan.md)
- [Data Model](../02-json-to-csv/data-model.md)
- [Task List](../02-json-to-csv/tasks.md)
- [Quickstart Guide](../02-json-to-csv/quickstart.md)
- [Python Contracts](../02-json-to-csv/contracts/csv_schema.py)

### Stage 3: JSON to Staging
**Input**: Master JSON files
**Output**: Pre-aggregated dashboard JSON

- [Specification](../03-json-to-staging/spec.md)
- [Implementation Plan](../03-json-to-staging/plan.md)
- [Data Model](../03-json-to-staging/data-model.md)
- [Task List](../03-json-to-staging/tasks.md)
- [Quickstart Guide](../03-json-to-staging/quickstart.md)
- [Python Contracts](../03-json-to-staging/contracts/staging_schema.py)
- **Widgets**:
  - [COC Trend Chart](../03-json-to-staging/widgets/coc-trend.md)
  - [KPI Gauges](../03-json-to-staging/widgets/kpi-gauges.md)
  - [Project Matrix](../03-json-to-staging/widgets/project-matrix.md)
  - [Global Filter](../03-json-to-staging/widgets/global-filter.md)

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          COO Dashboard ETL                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   XML Files          Master JSON          CSV Tables                    │
│   (13 files)         (enriched)           (flat export)                 │
│       │                  │                     │                        │
│       ▼                  ▼                     ▼                        │
│   ┌───────┐         ┌────────┐          ┌──────────┐                   │
│   │Stage 1│────────▶│ Stage 2│─────────▶│   CSV    │                   │
│   │XML→JSON│         │JSON→CSV│          │  Files   │                   │
│   └───────┘         └────────┘          └──────────┘                   │
│       │                  │                                              │
│       │             ┌────────┐          ┌──────────┐                   │
│       └────────────▶│ Stage 3│─────────▶│ Staging  │───▶ Dashboard     │
│                     │JSON→Stg│          │   JSON   │                   │
│                     └────────┘          └──────────┘                   │
│                          │                                              │
│                          ▼                                              │
│                   ┌────────────┐                                        │
│                   │  Pipeline  │  Combined reports from all stages      │
│                   │  Reports   │  (JSON + Markdown)                     │
│                   └────────────┘                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Projects

| Canonical Name | XML File | Zone | Region |
|----------------|----------|------|--------|
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

## Getting Started

### Prerequisites

- Python 3.10+
- Virtual environment

```bash
cd etl-coo-dashboard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Full Pipeline

```bash
# Stage 1: XML to JSON
python runner.py --input-dir input/all-aop-baselines

# Stage 2: JSON to CSV
python runner_table_extraction.py

# Stage 3: JSON to Staging (to be implemented)
python staging_generator.py
```

---

## Directory Structure

```
etl-coo-dashboard/
├── docs/
│   ├── 00-overview/          # This documentation
│   │   ├── README.md
│   │   └── GLOSSARY.md
│   ├── 01-xml-to-json/       # Stage 1 documentation
│   ├── 02-json-to-csv/       # Stage 2 documentation
│   └── 03-json-to-staging/   # Stage 3 documentation
│
├── src/                      # Source code
│   ├── xml_parser.py         # XML parsing
│   ├── transformers.py       # Field transformations
│   ├── task_builder.py       # Task object construction
│   ├── cost_timeline.py      # Weekly cost calculations
│   ├── enrichment.py         # Zone/region/tower/floor
│   ├── sprint_enrichment.py  # Sprint dates integration
│   ├── trade_type_*.py       # Trade type classification (LLM)
│   ├── llm_utils.py          # OpenRouter API client
│   ├── validators.py         # Schema validation & QA
│   ├── table_extractor.py    # JSON to CSV extraction
│   └── report_generator.py   # Pipeline report generation
│
├── input/                    # Input files (gitignored)
│   ├── all-aop-baselines/    # AOP baseline XML files
│   └── all-sprint-schedules/ # Sprint XML files
│
├── output/                   # Output files (gitignored)
│   ├── json/                 # Stage 1: Master JSON
│   ├── table/                # Stage 2: CSV exports
│   ├── staging/              # Stage 3: Dashboard JSON
│   ├── reports/              # Pipeline reports
│   └── logs/                 # Processing logs
│
├── runner.py                 # Stage 1 CLI
├── runner_table_extraction.py # Stage 2 CLI
├── SYSTEM_DESIGN.md          # Architecture document
└── task_schema.json          # Master JSON schema
```

---

## Pipeline Reporting

The pipeline includes a comprehensive reporting system that combines results from all stages into unified reports. Reports are generated in both JSON (machine-readable) and Markdown (human-readable) formats.

### Report Contents

| Section | Stage 1 | Stage 2 | Stage 3 |
|---------|---------|---------|---------|
| Task counts | ✓ | ✓ | ✓ |
| Enrichment coverage | ✓ | ✓ | ✓ |
| Validation results | ✓ | ✓ | ✓ |
| CSV extraction stats | - | ✓ | ✓ |
| Aggregation stats | - | - | ✓ (planned) |
| Output file sizes | ✓ | ✓ | ✓ |

### Report Generation

Pipeline reports are generated automatically after Stage 2 extraction:

```bash
# Stage 1: XML to JSON
python runner.py --input-dir input/all-aop-baselines

# Stage 2: JSON to CSV (generates pipeline reports)
python runner_table_extraction.py

# View report
cat output/reports/pipeline_report_Miraya.md
```

### Report Files

```
output/reports/
├── qa_report_{project}.json           # Stage 1 QA validation
├── summary_report.json                # Stage 1 summary (all projects)
├── pipeline_report_{project}.json     # Combined pipeline report
└── pipeline_report_{project}.md       # Human-readable report
```

### Example Report Output

```markdown
# Pipeline Report: Ramaiah

## Stage 1 (XML to JSON) Results
| Metric | Value |
|--------|-------|
| Total tasks | 1,408 |
| Parent tasks | 249 |
| Leaf tasks | 1,155 |

## Enrichment Results
| Enrichment | Result |
|------------|--------|
| Zone/Region | 100.0% |
| Trade Types | 100.0% |
| Sprint Dates | 65.3% |

## Output Files
| File | Size |
|------|------|
| output/json/Ramaiah.json | 2.1 MB |
| output/table/Ramaiah.csv | 169.5 KB |
```

For detailed documentation, see [Pipeline Reporting in plan.md](../01-xml-to-json/plan.md#10-pipeline-reporting).

---

## Support

- **Documentation Issues**: Update relevant doc file
- **Bug Reports**: Check logs in `output/logs/`
- **Feature Requests**: Update spec.md for relevant stage
