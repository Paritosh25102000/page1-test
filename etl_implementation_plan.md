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
│   ├── enrichment.py             # Attribute enrichment (zone, region, tower, floor)
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

### 7. `src/enrichment.py` - Attribute Enrichment

**Purpose:** Enrich task attributes with zone, region, tower, and floor information

```python
# Project name aliases (XML file name -> canonical project name)
PROJECT_NAME_ALIASES = {
    "Azadnagar": "Horizon",
    "Bigbull-Reserve": "Reserve",
    "OneM": "Avenue 11",
    "Miraya": "Miraya",
    "Aristocrat": "Aristocrat",
    "Zenith": "Zenith",
    "Tropical Isle 146": "Tropical Isle",
    "Jardinia": "Jardinia",
    "Riverine": "Sec. 44, Noida",
    "Ramaiah": "Ramaiah",
    "Woodscapes": "Woodscapes",
    "RGA Land2": "RGA 2",
    "BLSaha": "BL Saha",
}

# Zone/Region mapping (using canonical project names)
ZONE_REGION_MAP = {
    "Horizon": {"zone": "MZ", "region": "MZ1"},
    "Reserve": {"zone": "MZ", "region": "MZ1"},
    "Avenue 11": {"zone": "MZ", "region": "MZ1"},
    "Miraya": {"zone": "NZ", "region": "NZ1"},
    "Aristocrat": {"zone": "NZ", "region": "NZ1"},
    "Zenith": {"zone": "NZ", "region": "NZ1"},
    "Tropical Isle": {"zone": "NZ", "region": "NZ2"},
    "Jardinia": {"zone": "NZ", "region": "NZ2"},
    "Sec. 44, Noida": {"zone": "NZ", "region": "NZ2"},
    "Ramaiah": {"zone": "SZ", "region": "SZ2"},
    "Woodscapes": {"zone": "SZ", "region": "SZ1"},
    "RGA 2": {"zone": "SZ", "region": "SZ1"},
    "BL Saha": {"zone": "WEZ", "region": "Kolkata"},
}

def get_canonical_project_name(file_project_name: str) -> str:
    """
    Convert XML file-based project name to canonical name.

    Args:
        file_project_name: Project name from XML file

    Returns:
        Canonical project name for zone/region lookup
    """

def enrich_zone_region(tasks: list[dict], project_name: str) -> list[dict]:
    """
    Enrich tasks with zone and region based on project name.

    Args:
        tasks: List of task dictionaries
        project_name: Name of the project

    Returns:
        Tasks with zone/region enriched in attributes
    """

def find_parent_by_wbs(tasks: list[dict], parent_wbs: str) -> dict | None:
    """Find parent task by WBS"""

def extract_tower(task_name: str) -> str | None:
    """
    Extract tower identifier from task name.
    Looks for patterns like "Tower A", "Tower 1", "T1", etc.

    Excludes:
    - Block/Building patterns (not spatial structures)
    - Descriptive tower names (Area, Completion, Drop, Finishing, Ground, Raft, Structure)

    Returns:
        Tower identifier or None
    """

def extract_floor(task_name: str) -> str | None:
    """
    Extract floor identifier from task name.
    Looks for patterns like "Ground Floor", "1st Floor", "Floor 12", "Terrace", etc.

    Returns:
        Floor identifier or None
    """

def build_task_hierarchy(tasks: list[dict]) -> dict[str, dict]:
    """
    Build WBS hierarchy mapping.

    Returns:
        Dictionary mapping WBS -> {parent_wbs, ancestors, children}
    """

def enrich_tower_floor(tasks: list[dict]) -> list[dict]:
    """
    Enrich tasks with tower and floor attributes by traversing parent hierarchy.

    For each leaf task:
    - Walk up parent chain via parent_wbs
    - Extract tower from first parent containing tower pattern
    - Extract floor from first parent containing floor pattern
    - Populate attributes.tower and attributes.floor

    Args:
        tasks: List of task dictionaries

    Returns:
        Tasks with tower/floor enriched in attributes
    """

def enrich_attributes(
    tasks: list[dict],
    project_name: str,
    enrich_zone_region_flag: bool = True,
    enrich_tower_floor_flag: bool = True
) -> list[dict]:
    """
    Master enrichment function.

    Args:
        tasks: List of task dictionaries
        project_name: Name of the project
        enrich_zone_region_flag: Whether to enrich zone/region
        enrich_tower_floor_flag: Whether to enrich tower/floor

    Returns:
        Enriched tasks
    """
```

**Enrichment Logic:**

1. **Zone/Region:** Direct lookup by project name
2. **Tower/Floor:** Hierarchical extraction
   - Build task hierarchy from WBS structure
   - For each leaf task, walk up parent chain
   - Extract tower from ancestor names (patterns: "Tower X", "Block X")
   - Extract floor from ancestor names (patterns: "Ground Floor", "Floor N", "Terrace")
   - Apply to leaf task attributes

**Pattern Matching Examples:**
- Tower: `Tower A`, `Tower 1`, `Tower 01`, `T1`, `T2`
  - **Excluded Patterns:** Block, Building (not spatial structures)
  - **Excluded Descriptive:** Tower Area, Tower Completion, Tower Drop, Tower Finishing, Tower Ground, Tower Raft, Tower Structure
  - Only extract actual tower identifiers (numeric or alphabetic)
- Floor: `Ground Floor`, `1st Floor`, `Floor 12`, `Terrace`
  - **Basement Normalization:** B1→Basement 1, B2→Basement 2, Basement 01→Basement 1

---

### 8. `runner.py` - Main Entry Point

**Purpose:** CLI interface and orchestration

```python
#!/usr/bin/env python3
"""
XML to JSON ETL Runner for CCO Dashboard

Usage:
    # Standard processing with enrichment (default)
    python runner.py                                    # Process all XML files with enrichment
    python runner.py --file Miraya.xml                  # Process single file with enrichment

    # Enrichment control
    python runner.py --no-enrich-zone-region            # Skip zone/region enrichment
    python runner.py --no-enrich-tower-floor            # Skip tower/floor enrichment
    python runner.py --no-enrich                        # Skip all enrichment

    # Update existing outputs with enrichment
    python runner.py --enrich-only                      # Enrich existing JSON outputs
    python runner.py --enrich-only --enrich-zone-region # Only enrich zone/region
    python runner.py --enrich-only --enrich-tower-floor # Only enrich tower/floor

    # Other modes
    python runner.py --validate-only                    # Run validation on existing output
    python runner.py --dry-run                          # Parse and transform without saving
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
    parser.add_argument('--sample-size', type=int, default=100, help='QA sample size per file')

    # Enrichment arguments
    parser.add_argument('--enrich-only', action='store_true',
                       help='Enrich existing JSON outputs (no XML processing)')
    parser.add_argument('--no-enrich', action='store_true',
                       help='Skip all enrichment')
    parser.add_argument('--enrich-zone-region', action='store_true',
                       help='Enrich only zone/region (use with --enrich-only)')
    parser.add_argument('--enrich-tower-floor', action='store_true',
                       help='Enrich only tower/floor (use with --enrich-only)')
    parser.add_argument('--no-enrich-zone-region', action='store_true',
                       help='Skip zone/region enrichment')
    parser.add_argument('--no-enrich-tower-floor', action='store_true',
                       help='Skip tower/floor enrichment')

    args = parser.parse_args()

    # 1. Setup
    # 2. Load schema and mapping
    # 3. Process XML files (or load existing JSON if --enrich-only)
    # 4. Apply enrichment (unless --no-enrich)
    # 5. Run QA validation
    # 6. Generate reports
    # 7. Print summary

def process_single_file(xml_path: str, output_dir: str, schema: dict, enrich_flags: dict) -> dict:
    """Process one XML file, apply enrichment, return stats"""

def enrich_existing_outputs(output_dir: str, enrich_flags: dict) -> dict:
    """Enrich existing JSON outputs with attributes"""

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

### Phase 7: Attribute Enrichment
19. Implement `src/enrichment.py`
20. Create zone/region mapping lookup
21. Implement tower extraction with pattern matching
22. Implement floor extraction with pattern matching
23. Build hierarchical enrichment (walk parent chain)
24. Add enrichment CLI arguments to `runner.py`
25. Test enrichment with sample projects
26. Run enrichment on all existing outputs
27. Validate enriched attributes

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

1. **Attributes handling:**
   - `project_name`: Derived from filename
   - `zone` and `region`: Enriched via lookup table based on project name (Phase 7)
   - `tower` and `floor`: Enriched via hierarchical parent traversal (Phase 7)
   - Other attributes (if any): Set to `null`, to be enriched from external sources

2. **Sprint dates:** Always `null` in this ETL (comes from separate sprint XML files).

3. **Actual dates for leaf tasks:** Derived from TimephasedData Type=2 in Assignments, NOT from Task.ActualStart/ActualFinish.

4. **Memory:** Use iterparse for large files (Woodscapes.xml is 28MB, 23,494 tasks).

5. **Cost timeline:** Only calculated for leaf tasks with cost_plan_total > 0 and valid dates.

6. **Enrichment by default:** The pipeline applies all enrichments by default. Use `--no-enrich-*` flags to skip specific enrichments during processing.

7. **Retroactive enrichment:** Existing JSON outputs can be enriched using `--enrich-only` mode without re-processing XML files.

---

## Enrichment Reference

### Zone/Region Mapping Table

| Canonical Name | XML File Name | Zone | Region |
|----------------|---------------|------|--------|
| Horizon | Azadnagar | MZ | MZ1 |
| Reserve | Bigbull-Reserve | MZ | MZ1 |
| Avenue 11 | OneM | MZ | MZ1 |
| Miraya | Miraya | NZ | NZ1 |
| Aristocrat | Aristocrat | NZ | NZ1 |
| Zenith | Zenith | NZ | NZ1 |
| Tropical Isle | Tropical Isle 146 | NZ | NZ2 |
| Jardinia | Jardinia | NZ | NZ2 |
| Sec. 44, Noida | Riverine | NZ | NZ2 |
| Ramaiah | Ramaiah | SZ | SZ2 |
| Woodscapes | Woodscapes | SZ | SZ1 |
| RGA 2 | RGA Land2 | SZ | SZ1 |
| BL Saha | BLSaha | WEZ | Kolkata |

**Mapping Logic:**
1. Convert XML file name to canonical project name using `PROJECT_NAME_ALIASES`
2. Lookup zone/region using canonical name in `ZONE_REGION_MAP`
3. Apply to all tasks (parent and leaf) for the project
4. Store canonical name in `attributes.project_name`

### Tower/Floor Pattern Examples

**Tower Patterns:**
```
Tower A, Tower B, Tower 1, Tower 2, Tower 01, Tower 02
T1, T2, T3
TOWER-A, TOWER-B
```

**Excluded from Tower Extraction:**
```
Block Work, Block A (not spatial structures)
Building Certification, Building 1 (not spatial structures)
Tower Area, Tower Completion, Tower Drop, Tower Finishing (descriptive, not identifiers)
Tower Ground, Tower Raft, Tower Structure (construction phases, not identifiers)
```

**Floor Patterns:**
```
Ground Floor, GF
1st Floor, 2nd Floor, 3rd Floor, ...
Floor 1, Floor 2, Floor 12, ...
First Floor, Second Floor, Third Floor
Terrace, Terrace Floor
Basement, Basement 1, Basement 2, Basement 3
```

**Floor Normalization:**
```
B1 → Basement 1
B2 → Basement 2
B3 → Basement 3
Basement 01 → Basement 1
Basement 02 → Basement 2
Basement 03 → Basement 3
```

**Extraction Rules:**
1. Walk up parent hierarchy from leaf task
2. Extract only valid tower patterns (Tower X, T1, etc.), skip Block/Building/Descriptive patterns
3. Extract first matching floor pattern encountered
4. Normalize basement values: B1→Basement 1, Basement 01→Basement 1
5. Only apply to leaf tasks with non-null attributes

**Tower Extraction Example:**
```
Parent Chain: Project → Block Work → Tower 1 → Floor 2 → Leaf Task
Result: tower = "Tower 1" (Block Work ignored as non-spatial)
```
