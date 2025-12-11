# Table Extraction Plan: Master JSON to CSV

## Overview

Extract specific data points from master JSON files (enriched task data) into CSV table format for analysis and reporting.

**Input:** JSON files from `etl-cco-dashboard/output/json/` (e.g., Miraya.json)
**Output:** CSV files in `etl-cco-dashboard/output/table/` (e.g., Miraya.csv)

---

## Target CSV Schema

### Column Mapping

| Column Name | Source Field | Data Type | Notes |
|-------------|--------------|-----------|-------|
| `code` | `outline_number` | string | Task hierarchy code (e.g., "1.1.1.2.3") |
| `title` | `name` | string | Task name |
| `tower` | `attributes.tower` | string | Tower identifier (e.g., "Tower A") |
| `floor` | `attributes.floor` | string | Floor identifier (e.g., "Ground Floor", "Floor 12") |
| `main_category` | `attributes.main_category` | string | Main work category |
| `sub_category` | `attributes.sub_category` | string | Sub work category |
| `trade_type` | `attributes.trade_type` | string | Trade/discipline type |
| `slab_works` | `attributes.slab_works` | string | Slab work classification |
| `cost_plan_total` | `cost_plan_total` | float | Total planned cost |
| `start_date_plan` | `dates.plan.start` | date | Planned start date (YYYY-MM-DD) |
| `end_date_plan` | `dates.plan.end` | date | Planned end date (YYYY-MM-DD) |
| `start_date_actual` | `dates.actual.start` | date | Actual start date (YYYY-MM-DD) |
| `end_date_actual` | `dates.actual.end` | date | Actual end date (YYYY-MM-DD) |
| `start_date_sprint` | `dates.sprint.start` | date | Sprint start date (YYYY-MM-DD) |
| `end_date_sprint` | `dates.sprint.end` | date | Sprint end date (YYYY-MM-DD) |
| `progress` | `progress.percent_complete` | integer | Progress percentage (0-100) |

### Sample Output Row

```csv
code,title,tower,floor,main_category,sub_category,trade_type,slab_works,cost_plan_total,start_date_plan,end_date_plan,start_date_actual,end_date_actual,start_date_sprint,end_date_sprint,progress
1.1.1.2.3,Excavation Completion of Tower B,Tower B,,,,,0.0,2025-04-15,2025-04-15,2025-04-15,2025-04-15,,,100
```

---

## Module Structure

```
etl-cco-dashboard/
├── src/
│   └── table_extractor.py      # NEW: JSON to CSV extraction logic
│
├── runner_table_extraction.py  # NEW: CLI runner for table extraction
│
└── output/
    └── table/                   # NEW: Generated CSV files
        ├── Miraya.csv
        ├── Aristocrat.csv
        └── ...
```

---

## Implementation Specification

### 1. `src/table_extractor.py` - Extraction Logic

**Purpose:** Extract and transform JSON task data to CSV rows

```python
#!/usr/bin/env python3
"""
Table Extractor: Convert master JSON files to CSV table format

Extracts specific data points from enriched master JSON files and outputs
to CSV format for analysis and reporting.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Optional
import logging


def extract_row(task: Dict) -> Optional[Dict]:
    """
    Extract CSV row data from a single task object.

    Args:
        task: Task dictionary from master JSON

    Returns:
        Dictionary with CSV column names as keys, or None if task should be skipped

    Extraction Rules:
        - Extract ALL tasks (parents, leaves, milestones)
        - Handle null/missing values gracefully
        - Return None for tasks that should be excluded (if any filtering needed)
    """
    # Extract dates safely
    plan_start = task.get('dates', {}).get('plan', {}).get('start')
    plan_end = task.get('dates', {}).get('plan', {}).get('end')
    actual_start = task.get('dates', {}).get('actual', {}).get('start')
    actual_end = task.get('dates', {}).get('actual', {}).get('end')
    sprint_start = task.get('dates', {}).get('sprint', {}).get('start')
    sprint_end = task.get('dates', {}).get('sprint', {}).get('end')

    # Extract attributes safely (may be null for parent tasks and milestones)
    attributes = task.get('attributes') or {}

    # Extract progress safely (may be null for parent tasks)
    progress = task.get('progress') or {}

    # Build CSV row
    row = {
        'code': task.get('outline_number', ''),
        'title': task.get('name', ''),
        'tower': attributes.get('tower') or '',
        'floor': attributes.get('floor') or '',
        'main_category': attributes.get('main_category') or '',
        'sub_category': attributes.get('sub_category') or '',
        'trade_type': attributes.get('trade_type') or '',
        'slab_works': attributes.get('slab_works') or '',
        'cost_plan_total': task.get('cost_plan_total') or '',
        'start_date_plan': plan_start or '',
        'end_date_plan': plan_end or '',
        'start_date_actual': actual_start or '',
        'end_date_actual': actual_end or '',
        'start_date_sprint': sprint_start or '',
        'end_date_sprint': sprint_end or '',
        'progress': progress.get('percent_complete') if progress else '',
    }

    return row


def extract_to_csv(
    json_file_path: str,
    output_csv_path: str,
    include_summary_tasks: bool = True,
    include_milestones: bool = True
) -> Dict:
    """
    Extract data from master JSON file and write to CSV.

    Args:
        json_file_path: Path to input JSON file (e.g., Miraya.json)
        output_csv_path: Path to output CSV file (e.g., Miraya.csv)
        include_summary_tasks: Whether to include parent/summary tasks
        include_milestones: Whether to include milestone tasks

    Returns:
        Statistics dictionary with extraction counts

    Example:
        stats = extract_to_csv(
            'output/json/Miraya.json',
            'output/table/Miraya.csv'
        )
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Extracting data from: {json_file_path}")

    # Load JSON
    with open(json_file_path, 'r') as f:
        tasks = json.load(f)

    # Extract rows
    rows = []
    summary_count = 0
    milestone_count = 0
    leaf_count = 0

    for task in tasks:
        # Check task type
        is_summary = task.get('is_summary', False)
        is_milestone = task.get('is_milestone', False)

        # Apply filters
        if is_summary and not include_summary_tasks:
            summary_count += 1
            continue

        if is_milestone and not include_milestones:
            milestone_count += 1
            continue

        # Extract row
        row = extract_row(task)
        if row:
            rows.append(row)

            # Count task types
            if is_summary:
                summary_count += 1
            elif is_milestone:
                milestone_count += 1
            else:
                leaf_count += 1

    # Write CSV
    if rows:
        # Define column order
        fieldnames = [
            'code',
            'title',
            'tower',
            'floor',
            'main_category',
            'sub_category',
            'trade_type',
            'slab_works',
            'cost_plan_total',
            'start_date_plan',
            'end_date_plan',
            'start_date_actual',
            'end_date_actual',
            'start_date_sprint',
            'end_date_sprint',
            'progress'
        ]

        with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        logger.info(f"✓ Wrote {len(rows)} rows to: {output_csv_path}")
    else:
        logger.warning(f"No rows extracted from {json_file_path}")

    # Return statistics
    return {
        'project': Path(json_file_path).stem,
        'total_tasks': len(tasks),
        'summary_tasks': summary_count,
        'milestones': milestone_count,
        'leaf_tasks': leaf_count,
        'rows_written': len(rows),
        'output_file': output_csv_path
    }


def batch_extract(
    json_dir: str,
    output_dir: str,
    include_summary_tasks: bool = True,
    include_milestones: bool = True
) -> List[Dict]:
    """
    Batch extract all JSON files in a directory to CSV.

    Args:
        json_dir: Directory containing master JSON files
        output_dir: Directory to write CSV files
        include_summary_tasks: Whether to include parent/summary tasks
        include_milestones: Whether to include milestone tasks

    Returns:
        List of statistics dictionaries for each project

    Example:
        stats = batch_extract(
            'output/json',
            'output/table'
        )
    """
    logger = logging.getLogger(__name__)
    results = []

    json_path = Path(json_dir)
    output_path = Path(output_dir)

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Process each JSON file
    for json_file in sorted(json_path.glob('*.json')):
        output_csv = output_path / f"{json_file.stem}.csv"

        try:
            stats = extract_to_csv(
                str(json_file),
                str(output_csv),
                include_summary_tasks=include_summary_tasks,
                include_milestones=include_milestones
            )
            results.append(stats)

            logger.info(f"✓ {stats['project']}: {stats['rows_written']} rows "
                       f"({stats['leaf_tasks']} leaf, {stats['summary_tasks']} summary, "
                       f"{stats['milestones']} milestone)")

        except Exception as e:
            logger.error(f"✗ Failed to extract {json_file.name}: {e}")
            results.append({
                'project': json_file.stem,
                'error': str(e)
            })

    return results


def generate_extraction_report(
    stats_list: List[Dict],
    output_path: str
) -> None:
    """
    Generate summary report of extraction process.

    Args:
        stats_list: List of statistics from batch_extract()
        output_path: Path to write report JSON file
    """
    report = {
        'total_projects': len(stats_list),
        'successful': sum(1 for s in stats_list if 'error' not in s),
        'failed': sum(1 for s in stats_list if 'error' in s),
        'total_rows': sum(s.get('rows_written', 0) for s in stats_list),
        'projects': stats_list
    }

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Extraction report saved to: {output_path}")


if __name__ == '__main__':
    # Quick test with Miraya.json
    import sys
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'output.csv'
        stats = extract_to_csv(json_file, output_file)
        print(json.dumps(stats, indent=2))
    else:
        print("Usage: python table_extractor.py <input.json> [output.csv]")
```

---

### 2. `runner_table_extraction.py` - CLI Runner

**Purpose:** Command-line interface for table extraction

```python
#!/usr/bin/env python3
"""
Table Extraction Runner

Extracts data from master JSON files to CSV table format.

Usage:
    # Extract single file
    python runner_table_extraction.py --file output/json/Miraya.json

    # Extract all files in directory
    python runner_table_extraction.py --input-dir output/json

    # Exclude summary tasks
    python runner_table_extraction.py --no-summary

    # Exclude milestones
    python runner_table_extraction.py --no-milestones

    # Custom output directory
    python runner_table_extraction.py --output-dir custom/path
"""

import argparse
import logging
from pathlib import Path
from src.table_extractor import extract_to_csv, batch_extract, generate_extraction_report


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    parser = argparse.ArgumentParser(
        description='Extract master JSON data to CSV table format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract single file
  python runner_table_extraction.py --file output/json/Miraya.json

  # Extract all files
  python runner_table_extraction.py --input-dir output/json

  # Leaf tasks only (exclude summary tasks and milestones)
  python runner_table_extraction.py --no-summary --no-milestones
        """
    )

    # Input arguments
    parser.add_argument(
        '--file',
        help='Extract single JSON file'
    )
    parser.add_argument(
        '--input-dir',
        default='output/json',
        help='Directory containing master JSON files (default: output/json)'
    )

    # Output arguments
    parser.add_argument(
        '--output-dir',
        default='output/table',
        help='Directory for CSV output files (default: output/table)'
    )

    # Filtering arguments
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Exclude summary/parent tasks from output'
    )
    parser.add_argument(
        '--no-milestones',
        action='store_true',
        help='Exclude milestone tasks from output'
    )

    # Report arguments
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate extraction report (default: True for batch mode)'
    )
    parser.add_argument(
        '--report-path',
        default='output/table/extraction_report.json',
        help='Path for extraction report (default: output/table/extraction_report.json)'
    )

    # Other arguments
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine inclusion flags
    include_summary = not args.no_summary
    include_milestones = not args.no_milestones

    logger.info("Table Extraction Configuration:")
    logger.info(f"  Include summary tasks: {include_summary}")
    logger.info(f"  Include milestones: {include_milestones}")
    logger.info(f"  Output directory: {args.output_dir}")

    # Execute
    if args.file:
        # Single file mode
        input_path = Path(args.file)
        output_path = output_dir / f"{input_path.stem}.csv"

        logger.info(f"\nExtracting single file: {args.file}")

        stats = extract_to_csv(
            str(input_path),
            str(output_path),
            include_summary_tasks=include_summary,
            include_milestones=include_milestones
        )

        print("\n" + "="*60)
        print("Extraction Complete")
        print("="*60)
        print(f"Project: {stats['project']}")
        print(f"Total tasks: {stats['total_tasks']}")
        print(f"  - Summary tasks: {stats['summary_tasks']}")
        print(f"  - Leaf tasks: {stats['leaf_tasks']}")
        print(f"  - Milestones: {stats['milestones']}")
        print(f"Rows written: {stats['rows_written']}")
        print(f"Output file: {stats['output_file']}")
        print("="*60)

    else:
        # Batch mode
        logger.info(f"\nExtracting all files from: {args.input_dir}")

        stats_list = batch_extract(
            args.input_dir,
            args.output_dir,
            include_summary_tasks=include_summary,
            include_milestones=include_milestones
        )

        # Generate report
        if args.report or len(stats_list) > 1:
            generate_extraction_report(stats_list, args.report_path)

        # Print summary
        print("\n" + "="*60)
        print("Batch Extraction Complete")
        print("="*60)
        print(f"Projects processed: {len(stats_list)}")
        print(f"Total rows written: {sum(s.get('rows_written', 0) for s in stats_list)}")
        print(f"Output directory: {args.output_dir}")

        # Show per-project summary
        print("\nPer-Project Summary:")
        for stats in stats_list:
            if 'error' in stats:
                print(f"  ✗ {stats['project']}: {stats['error']}")
            else:
                print(f"  ✓ {stats['project']}: {stats['rows_written']} rows")

        print("="*60)


if __name__ == '__main__':
    main()
```

---

## Usage Examples

### Extract Single File

```bash
# Extract Miraya.json to Miraya.csv
python runner_table_extraction.py --file output/json/Miraya.json
```

**Output:**
```
output/table/Miraya.csv
```

### Extract All Files

```bash
# Extract all JSON files in output/json/ directory
python runner_table_extraction.py --input-dir output/json
```

**Output:**
```
output/table/
├── Miraya.csv
├── Aristocrat.csv
├── Horizon.csv
└── ...
```

### Extract Leaf Tasks Only

```bash
# Exclude summary tasks and milestones (leaf tasks only)
python runner_table_extraction.py --no-summary --no-milestones
```

### Custom Output Directory

```bash
# Specify custom output directory
python runner_table_extraction.py --output-dir reports/tables
```

### Generate Extraction Report

```bash
# Generate detailed extraction report
python runner_table_extraction.py --report --report-path output/table/report.json
```

---

## Data Handling Rules

### Null Value Handling

| Field | If Null | Output |
|-------|---------|--------|
| All string fields | `null` or missing | Empty string `""` |
| `cost_plan_total` | `null` | Empty string `""` |
| `progress` | `null` | Empty string `""` |
| Date fields | `null` | Empty string `""` |

### Task Type Filtering

| Task Type | Default Behavior | Flag to Exclude |
|-----------|------------------|-----------------|
| Summary (parent) tasks | Included | `--no-summary` |
| Milestone tasks | Included | `--no-milestones` |
| Leaf (work) tasks | Always included | N/A |

### Example Output with Nulls

```csv
code,title,tower,floor,main_category,sub_category,trade_type,slab_works,cost_plan_total,start_date_plan,end_date_plan,start_date_actual,end_date_actual,start_date_sprint,end_date_sprint,progress
1,Miraya | Sec 43,,,,,,,2025-01-02,2029-09-06,,,,
1.1.1.2.3,Excavation Completion of Tower B,Tower B,,,,,0.0,2025-04-15,2025-04-15,2025-04-15,2025-04-15,,,100
```

---

## Implementation Steps

### Step 1: Create `src/table_extractor.py`
- Implement `extract_row()` function
- Implement `extract_to_csv()` function
- Implement `batch_extract()` function
- Add unit tests for extraction logic

### Step 2: Create `runner_table_extraction.py`
- Implement CLI argument parsing
- Implement single-file extraction mode
- Implement batch extraction mode
- Add logging and progress reporting

### Step 3: Test with Miraya.json
- Extract single file
- Verify CSV column order
- Verify null handling
- Verify row count matches JSON task count

### Step 4: Batch Process All Files
- Extract all 12 project JSON files
- Generate extraction report
- Validate output consistency

### Step 5: Documentation
- Update README with usage examples
- Document CSV schema
- Add troubleshooting guide

---

## Testing Strategy

### Unit Tests

```python
# Test extract_row() with different task types
def test_extract_row_summary_task():
    task = {
        "outline_number": "1",
        "name": "Project Root",
        "is_summary": True,
        "attributes": None,
        "progress": None,
        "cost_plan_total": None,
        "dates": {"plan": {"start": "2025-01-01", "end": "2029-12-31"}}
    }
    row = extract_row(task)
    assert row['code'] == "1"
    assert row['tower'] == ""
    assert row['progress'] == ""

def test_extract_row_leaf_task():
    task = {
        "outline_number": "1.1.2.3",
        "name": "Excavation Work",
        "is_summary": False,
        "attributes": {"tower": "Tower A", "floor": "Ground Floor"},
        "progress": {"percent_complete": 50},
        "cost_plan_total": 12345.67,
        "dates": {
            "plan": {"start": "2025-01-15", "end": "2025-02-20"},
            "actual": {"start": "2025-01-20", "end": None}
        }
    }
    row = extract_row(task)
    assert row['tower'] == "Tower A"
    assert row['progress'] == 50
    assert row['cost_plan_total'] == 12345.67
```

### Integration Tests

```bash
# Test single file extraction
python runner_table_extraction.py --file output/json/Miraya.json

# Verify output
wc -l output/table/Miraya.csv  # Should match task count + 1 (header)
head -5 output/table/Miraya.csv  # Verify column headers and first rows
```

### Validation Checks

1. **Row count:** CSV rows = JSON tasks (excluding filtered tasks)
2. **Column count:** All CSV rows have 16 columns
3. **Null handling:** No literal "null" strings in CSV (empty strings instead)
4. **Date format:** All dates in YYYY-MM-DD format
5. **Character encoding:** UTF-8 encoding for special characters

---

## Output Specifications

### CSV File Format

- **Encoding:** UTF-8
- **Line endings:** LF (Unix-style)
- **Delimiter:** Comma (`,`)
- **Quoting:** Minimal (only when necessary for special characters)
- **Header:** First row contains column names

### File Naming Convention

```
{project_name}.csv
```

Examples:
- `Miraya.csv`
- `Aristocrat.csv`
- `Horizon.csv`

### Directory Structure

```
output/
└── table/
    ├── Miraya.csv
    ├── Aristocrat.csv
    ├── Horizon.csv
    ├── Reserve.csv
    ├── Avenue_11.csv
    ├── Zenith.csv
    ├── Tropical_Isle.csv
    ├── Jardinia.csv
    ├── Sec_44_Noida.csv
    ├── Ramaiah.csv
    ├── Woodscapes.csv
    ├── RGA_2.csv
    ├── BL_Saha.csv
    └── extraction_report.json
```

---

## Expected Output Stats (Miraya Example)

Based on Miraya.json structure:

```json
{
  "project": "Miraya",
  "total_tasks": 2849,
  "summary_tasks": 245,
  "leaf_tasks": 2600,
  "milestones": 4,
  "rows_written": 2849,
  "output_file": "output/table/Miraya.csv"
}
```

---

## Error Handling

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | JSON file not found | Verify input path exists |
| `JSONDecodeError` | Malformed JSON file | Validate JSON with linter |
| `PermissionError` | Cannot write to output | Check file/directory permissions |
| Empty CSV | All tasks filtered out | Review `--no-summary` and `--no-milestones` flags |

### Logging

- **INFO:** Progress updates, file processing
- **WARNING:** Missing expected fields, low row counts
- **ERROR:** File I/O errors, JSON parsing errors

---

## Future Enhancements

1. **Excel Output:** Add `--format xlsx` option for Excel output
2. **Column Selection:** Add `--columns` flag to select specific columns
3. **Filtering:** Add `--filter` option to filter by tower, floor, etc.
4. **Aggregation:** Add summary statistics per tower/floor
5. **Validation:** Add data quality checks (date consistency, cost validation)

---

## Success Criteria

- ✅ Extract all 16 specified columns correctly
- ✅ Handle null values as empty strings
- ✅ Support single-file and batch extraction
- ✅ Generate extraction report with statistics
- ✅ Process all 12 project files successfully
- ✅ CSV files load correctly in Excel/Google Sheets
- ✅ Execution time < 10 seconds for Miraya.json
- ✅ Memory usage < 500MB for largest file (Woodscapes.json)

---

## Dependencies

- **Python:** 3.8+
- **Standard Library:** json, csv, pathlib, logging, argparse
- **No external dependencies required**

---

## Estimated Implementation Time

| Task | Duration |
|------|----------|
| Implement `table_extractor.py` | 2 hours |
| Implement `runner_table_extraction.py` | 1 hour |
| Testing with Miraya.json | 30 minutes |
| Batch processing all files | 30 minutes |
| Documentation | 30 minutes |
| **Total** | **4.5 hours** |

---

## Notes

1. **Data Completeness:**
   - Summary tasks have null attributes and progress
   - Milestones have null attributes and null cost_timeline
   - Leaf tasks should have all fields populated (if enriched)

2. **Performance:**
   - Miraya.json (4.6MB): ~1 second extraction time
   - Woodscapes.json (largest): ~3 seconds extraction time
   - All 12 files: ~15 seconds total

3. **Character Encoding:**
   - Handle special characters in task names (e.g., "Excavation for isolated fottings of NTA")
   - UTF-8 encoding for international characters

4. **CSV Compatibility:**
   - Test with Excel, Google Sheets, and pandas
   - Ensure proper quoting for commas in task names

---

**End of Plan**
