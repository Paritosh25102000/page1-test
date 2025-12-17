# Stage 2 Implementation Plan: JSON to CSV Extraction

**Document Version**: 1.0
**Status**: Production (Implemented)
**Last Updated**: 2025-12-16

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        JSON to CSV Pipeline                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │ JSON Loader │───▶│Row Extractor│───▶│ CSV Writer  │                 │
│  │             │    │             │    │             │                 │
│  │ • load file │    │ • extract   │    │ • headers   │                 │
│  │ • parse     │    │ • transform │    │ • write rows│                 │
│  │ • validate  │    │ • filter    │    │ • encoding  │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Module Structure

```
etl-cco-dashboard/
├── runner_table_extraction.py    # CLI runner
│
├── src/
│   └── table_extractor.py        # Extraction logic
│
├── output/
│   ├── json/                     # Input (from Stage 1)
│   │   ├── Miraya.json
│   │   └── ...
│   │
│   └── table/                    # Output (CSV files)
│       ├── Miraya.csv
│       ├── Aristocrat.csv
│       └── extraction_report.json
```

---

## 3. Module Specifications

### 3.1 table_extractor.py - Core Logic

```python
def extract_row(task: Dict) -> Optional[Dict]:
    """
    Extract CSV row data from a single task.

    Args:
        task: Task dictionary from master JSON

    Returns:
        Dictionary with CSV column names as keys

    Field Mapping:
        code          <- outline_number
        title         <- name
        tower         <- attributes.tower
        floor         <- attributes.floor
        main_category <- attributes.main_category
        sub_category  <- attributes.sub_category
        trade_type    <- attributes.trade_type
        slab_works    <- attributes.slab_works
        cost_plan_total <- cost_plan_total
        start_date_plan <- dates.plan.start
        end_date_plan   <- dates.plan.end
        start_date_actual <- dates.actual.start
        end_date_actual   <- dates.actual.end
        start_date_sprint <- dates.sprint.start
        end_date_sprint   <- dates.sprint.end
        progress        <- progress.percent_complete
    """

def extract_to_csv(
    json_file_path: str,
    output_csv_path: str,
    include_summary_tasks: bool = True,
    include_milestones: bool = True
) -> Dict:
    """
    Extract data from master JSON to CSV.

    Args:
        json_file_path: Input JSON file path
        output_csv_path: Output CSV file path
        include_summary_tasks: Include parent/summary tasks
        include_milestones: Include milestone tasks

    Returns:
        Statistics dictionary:
        {
            "project": str,
            "total_tasks": int,
            "summary_tasks": int,
            "leaf_tasks": int,
            "milestones": int,
            "rows_written": int,
            "output_file": str
        }
    """

def batch_extract(
    json_dir: str,
    output_dir: str,
    include_summary_tasks: bool = True,
    include_milestones: bool = True
) -> List[Dict]:
    """
    Batch extract all JSON files to CSV.

    Returns:
        List of statistics dictionaries for each project
    """

def generate_extraction_report(
    stats_list: List[Dict],
    output_path: str
) -> None:
    """Generate summary report JSON."""
```

### 3.2 runner_table_extraction.py - CLI

```python
"""
Table Extraction Runner

Usage:
    # Extract single file
    python runner_table_extraction.py --file output/json/Miraya.json

    # Extract all files
    python runner_table_extraction.py --input-dir output/json

    # Exclude parent tasks
    python runner_table_extraction.py --no-summary

    # Exclude milestones
    python runner_table_extraction.py --no-milestones

    # Custom output directory
    python runner_table_extraction.py --output-dir custom/path
"""
```

---

## 4. Column Schema

### 4.1 Column Order (Fixed)

| # | Column Name | Source Field | Type |
|---|-------------|--------------|------|
| 1 | code | outline_number | string |
| 2 | title | name | string |
| 3 | tower | attributes.tower | string |
| 4 | floor | attributes.floor | string |
| 5 | main_category | attributes.main_category | string |
| 6 | sub_category | attributes.sub_category | string |
| 7 | trade_type | attributes.trade_type | string |
| 8 | slab_works | attributes.slab_works | string |
| 9 | cost_plan_total | cost_plan_total | float |
| 10 | start_date_plan | dates.plan.start | date |
| 11 | end_date_plan | dates.plan.end | date |
| 12 | start_date_actual | dates.actual.start | date |
| 13 | end_date_actual | dates.actual.end | date |
| 14 | start_date_sprint | dates.sprint.start | date |
| 15 | end_date_sprint | dates.sprint.end | date |
| 16 | progress | progress.percent_complete | integer |

### 4.2 Field Extraction Logic

```python
# Safe nested access pattern
def safe_get(obj, *keys, default=''):
    """Safely get nested dictionary values."""
    for key in keys:
        if obj is None:
            return default
        obj = obj.get(key)
    return obj if obj is not None else default

# Example usage
tower = safe_get(task, 'attributes', 'tower')
plan_start = safe_get(task, 'dates', 'plan', 'start')
```

---

## 5. Data Handling

### 5.1 Null Value Rules

| Scenario | Output |
|----------|--------|
| Field is `null` | Empty string `""` |
| Field is missing | Empty string `""` |
| Nested object is `null` | Empty string `""` |
| Number is `null` | Empty string `""` |

### 5.2 Task Type Handling

| Task Type | is_summary | is_milestone | Default Included |
|-----------|------------|--------------|------------------|
| Parent | true | false | Yes |
| Milestone | false | true | Yes |
| Leaf | false | false | Yes (always) |

### 5.3 Character Encoding

- **Input**: UTF-8 JSON
- **Output**: UTF-8 CSV
- **Line endings**: LF (Unix)
- **BOM**: None

---

## 6. CLI Arguments

```
python runner_table_extraction.py [OPTIONS]

Input Options:
  --file FILE           Extract single JSON file
  --input-dir DIR       Directory containing JSON files (default: output/json)

Output Options:
  --output-dir DIR      Output directory for CSV (default: output/table)

Filtering Options:
  --no-summary          Exclude parent/summary tasks
  --no-milestones       Exclude milestone tasks

Reporting Options:
  --report              Generate extraction report
  --report-path PATH    Path for report (default: output/table/extraction_report.json)

Other Options:
  --verbose             Enable debug logging
```

---

## 7. Output Examples

### 7.1 Sample CSV Output

```csv
code,title,tower,floor,main_category,sub_category,trade_type,slab_works,cost_plan_total,start_date_plan,end_date_plan,start_date_actual,end_date_actual,start_date_sprint,end_date_sprint,progress
1.1.1.2.3,Excavation Work,Tower A,Ground Floor,Civil Works- RCC,RCC,Concreting,Typical,125000.00,2025-04-15,2025-05-20,2025-04-18,,2025-04-10,2025-05-10,45
1.1.1.2.4,Foundation Pour,Tower A,Ground Floor,Civil Works- RCC,RCC,Concreting,Typical,200000.00,2025-05-21,2025-06-15,,,,,0
```

### 7.2 Sample Report

```json
{
  "total_projects": 12,
  "successful": 12,
  "failed": 0,
  "total_rows": 109876,
  "projects": [
    {
      "project": "Miraya",
      "total_tasks": 2849,
      "summary_tasks": 245,
      "leaf_tasks": 2600,
      "milestones": 4,
      "rows_written": 2849,
      "output_file": "output/table/Miraya.csv"
    }
  ]
}
```

---

## 8. Implementation Status

| Task | Status |
|------|--------|
| `extract_row()` function | Complete |
| `extract_to_csv()` function | Complete |
| `batch_extract()` function | Complete |
| CLI argument parsing | Complete |
| Single file mode | Complete |
| Batch mode | Complete |
| Filtering options | Complete |
| Report generation | Complete |

---

## 9. Performance

| Metric | Value |
|--------|-------|
| Miraya.json (2,849 tasks) | ~1 second |
| Woodscapes.json (23,494 tasks) | ~3 seconds |
| All 12 files | ~15 seconds |
| Memory usage | < 200 MB |
