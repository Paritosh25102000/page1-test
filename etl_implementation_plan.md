# ETL Plan: XML to JSON Conversion for CCO Dashboard

## Overview

Create a modular Python ETL pipeline that converts Asta Powerproject XML files to JSON format according to the master schema (`task_schema.json`) and mapping rules (`xml_to_json_mapping.json`).

**Location:** `/Users/alexanderbankov/Documents/Projects/easybim_data/etl-cco-dashboard/`

**Source:** 12 XML files in `../source_data/asta-source-cco-dashboard/all-aop-baselines/` (171 MB, ~110,000 tasks)

**Target:** JSON files conforming to `task_schema.json`

---

## Module Structure

```
etl-cco-dashboard/
├── task_schema.json              # (existing) Target schema
├── xml_to_json_mapping.json      # (existing) Mapping rules
├── sample_tasks.json             # (existing) Sample output
├── complete_documentation.md     # (existing) Documentation
│
├── src/                          # NEW: ETL source code
│   ├── __init__.py
│   ├── xml_parser.py             # XML parsing with streaming
│   ├── transformers.py           # Field transformation functions
│   ├── task_builder.py           # Task object construction
│   ├── cost_timeline.py          # Weekly cost calculations
│   ├── validators.py             # Schema validation & QA
│   └── utils.py                  # Shared utilities
│
├── runner.py                     # NEW: Main entry point / CLI
│
└── output/                       # NEW: Generated output (gitignored)
    ├── json/                     # Converted JSON files
    ├── reports/                  # QA and validation reports
    └── logs/                     # Processing logs
```

---

## Module Specifications

### 1. `src/xml_parser.py` - XML Parsing

**Purpose:** Stream-parse large XML files, extract Tasks and Assignments

```python
# Key functions:
def parse_xml_file(file_path: str) -> dict:
    """Parse XML and return structured data with tasks, assignments, project metadata"""

def extract_tasks(root, namespace: dict) -> list[dict]:
    """Extract all Task elements as dictionaries"""

def extract_assignments(root, namespace: dict) -> list[dict]:
    """Extract all Assignment elements with TimephasedData"""

def build_task_assignment_map(assignments: list) -> dict[int, list]:
    """Map TaskUID -> list of assignments for actual date derivation"""
```

**Key considerations:**
- Use `xml.etree.ElementTree.iterparse` for memory efficiency
- Handle namespace: `{http://schemas.microsoft.com/project}`
- Extract TimephasedData Type=2 for actual dates

---

### 2. `src/transformers.py` - Field Transformations

**Purpose:** Implement all transformation functions from mapping rules

```python
# Direct transformations:
def parse_int(value: str) -> int | None
def parse_float(value: str) -> float | None
def boolean_from_string(value: str) -> bool
def extract_date(datetime_str: str) -> str | None  # "2025-03-15T08:00:00" -> "2025-03-15"

# Duration conversion:
def iso8601_duration_to_days(duration: str) -> float | None  # "PT960H0M0S" -> 120.0

# Derived fields:
def remove_last_segment(wbs: str) -> str | None  # "37300.37500" -> "37300"

# Actual date derivation:
def derive_actual_start(timephased_data: list) -> str | None
def derive_actual_end(timephased_data: list) -> str | None
def calculate_duration_days(start: str, end: str) -> int | None
```

---

### 3. `src/task_builder.py` - Task Object Construction

**Purpose:** Build target JSON objects according to schema

```python
def build_task(
    xml_task: dict,
    assignments: list[dict],
    project_name: str
) -> dict:
    """Transform XML task to target schema format"""

def determine_task_type(xml_task: dict) -> str:
    """Return 'parent', 'leaf', or 'milestone'"""

def build_dates_object(xml_task: dict, assignments: list, task_type: str) -> dict:
    """Build dates: {plan, manual, sprint, actual}"""

def build_progress_object(xml_task: dict, task_type: str) -> dict | None:
    """Build progress: {percent_complete, is_complete} or None for parents"""

def build_attributes_placeholder(project_name: str, task_type: str) -> dict | None:
    """Build attributes with project_name, null for other fields (external master data)"""
```

**Task type logic:**
- `is_summary == true` → Parent (null: attributes, progress, cost_plan_total, cost_timeline)
- `is_milestone == true` → Milestone (null: attributes, cost_timeline; has progress)
- Otherwise → Leaf (has all fields)

---

### 4. `src/cost_timeline.py` - Weekly Cost Calculations

**Purpose:** Calculate FY 2025-26 weekly cost breakdown

```python
FY_START = "2025-04-01"
FY_END = "2026-03-31"

def calculate_cost_timeline(
    cost_plan_total: float,
    plan_dates: dict,
    actual_dates: dict,
    is_complete: bool
) -> dict | None:
    """Calculate full cost_timeline object or None if not applicable"""

def calculate_incoming_cost(
    cost_total: float,
    duration_days: float,
    start_date: str,
    fy_start: str
) -> dict:
    """Calculate {days_before_fy, cost} for incoming costs"""

def generate_weekly_costs(
    cost_total: float,
    plan_dates: dict,
    actual_dates: dict,
    is_complete: bool,
    incoming_plan: float,
    incoming_actual: float
) -> list[dict]:
    """Generate weekly cost entries with accumulated values"""

def get_week_boundaries(date: str) -> tuple[str, str]:
    """Return (monday, sunday) for the week containing date"""
```

**Calculation rules:**
- Plan: `cost_plan_total / duration_plan_days * days_in_week`
- Actual (complete): `cost_plan_total / duration_actual_days * days_in_week`
- Actual (incomplete): Use plan rate
- Weeks run Monday-Sunday

---

### 5. `src/validators.py` - QA and Validation

**Purpose:** Validate output against schema and source XML

```python
def validate_against_schema(task: dict, schema: dict) -> list[str]:
    """Validate task against JSON schema, return list of errors"""

def sample_validation(
    output_tasks: list[dict],
    xml_file_path: str,
    sample_size: int = 10
) -> dict:
    """Compare random sample of output tasks against source XML"""

def generate_qa_report(
    project_name: str,
    total_tasks: int,
    validation_results: dict,
    sample_results: dict
) -> dict:
    """Generate comprehensive QA report"""
```

**Sample validation checks:**
- WBS matches
- Name matches
- Plan dates match (after transformation)
- Duration matches (after conversion)
- Percent complete matches
- Cost matches

---

### 6. `src/utils.py` - Shared Utilities

```python
def setup_logging(log_dir: str, project_name: str) -> logging.Logger
def load_json_file(path: str) -> dict
def save_json_file(data: dict, path: str, indent: int = 2)
def ensure_directory(path: str)
def get_xml_files(directory: str) -> list[str]
```

---

### 7. `runner.py` - Main Entry Point

**Purpose:** CLI interface and orchestration

```python
#!/usr/bin/env python3
"""
XML to JSON ETL Runner for CCO Dashboard

Usage:
    python runner.py                     # Process all XML files
    python runner.py --file Miraya.xml   # Process single file
    python runner.py --validate-only     # Run validation on existing output
    python runner.py --dry-run           # Parse and transform without saving
"""

import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='XML to JSON ETL for CCO Dashboard')
    parser.add_argument('--file', help='Process single XML file')
    parser.add_argument('--input-dir', default='../source_data/asta-source-cco-dashboard/all-aop-baselines')
    parser.add_argument('--output-dir', default='./output')
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--sample-size', type=int, default=10, help='QA sample size per file')

    args = parser.parse_args()

    # 1. Setup
    # 2. Load schema and mapping
    # 3. Process XML files
    # 4. Run QA validation
    # 5. Generate reports
    # 6. Print summary

def process_single_file(xml_path: str, output_dir: str, schema: dict) -> dict:
    """Process one XML file, return stats"""

def run_qa_validation(output_dir: str, xml_dir: str, sample_size: int) -> dict:
    """Run sample validation on all output files"""
```

**Output structure:**
```
output/
├── json/
│   ├── Miraya.json
│   ├── Aristocrat.json
│   └── ...
├── reports/
│   ├── qa_report_Miraya.json
│   ├── qa_report_Aristocrat.json
│   ├── summary_report.json
│   └── validation_errors.json
└── logs/
    └── etl_run_20251209_143022.log
```

---

## Implementation Order

### Phase 1: Core Infrastructure
1. Create `src/` directory structure
2. Implement `src/utils.py`
3. Implement `src/transformers.py` (all transformation functions)
4. Write unit tests for transformers

### Phase 2: XML Parsing
5. Implement `src/xml_parser.py`
6. Test with Miraya.xml (smallest file, 2,849 tasks)

### Phase 3: Task Building
7. Implement `src/task_builder.py`
8. Test task type classification (parent/leaf/milestone)
9. Verify output matches `sample_tasks.json` structure

### Phase 4: Cost Timeline
10. Implement `src/cost_timeline.py`
11. Test weekly calculations with known inputs
12. Verify accumulated cost logic

### Phase 5: Validation & QA
13. Implement `src/validators.py`
14. Create sample validation comparing output to source XML

### Phase 6: Runner & Integration
15. Implement `runner.py` with CLI
16. End-to-end test with single file
17. Process all 12 files
18. Generate final QA reports

---

## QA/Testing Strategy

### Sample Validation (per file)
- Randomly select 100 tasks from output
- For each task:
  - Re-parse source XML to find matching Task by UID
  - Compare transformed fields:
    - `wbs` == XML WBS
    - `name` == XML Name
    - `dates.plan.start` == XML Start[:10]
    - `dates.plan.duration_days` == XML Duration (converted)
    - `progress.percent_complete` == XML PercentComplete
    - `cost_plan_total` == XML FixedCost
  - Log mismatches

### Report Output
```json
{
  "project": "Miraya",
  "total_tasks": 2849,
  "parents": 245,
  "leaves": 2600,
  "milestones": 4,
  "sample_size": 10,
  "sample_pass_rate": 1.0,
  "validation_errors": [],
  "field_coverage": {
    "dates.actual.start": 0.87,
    "cost_timeline": 0.91
  }
}
```

---

## Critical Files to Reference

| File | Purpose |
|------|---------|
| `task_schema.json` | Target JSON schema - validation reference |
| `xml_to_json_mapping.json` | Field mapping rules - transformation logic |
| `sample_tasks.json` | Expected output format - visual reference |
| `complete_documentation.md` | ETL pipeline section - code patterns |

---

## Notes

1. **Attributes handling:** Only `project_name` is derived from filename. Other attributes (zone, region, etc.) come from external master data - set to `null` in this ETL, to be enriched separately.

2. **Sprint dates:** Always `null` in this ETL (comes from separate sprint XML files).

3. **Actual dates for leaf tasks:** Derived from TimephasedData Type=2 in Assignments, NOT from Task.ActualStart/ActualFinish.

4. **Memory:** Use iterparse for large files (Woodscapes.xml is 28MB, 23,494 tasks).

5. **Cost timeline:** Only calculated for leaf tasks with cost_plan_total > 0 and valid dates.
