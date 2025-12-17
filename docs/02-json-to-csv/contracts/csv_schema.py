"""
Stage 2: CSV Schema Contracts

Python dataclasses representing the CSV output structure.
These contracts define the shape of data produced by Stage 2 ETL.

Usage:
    from docs.contracts.csv_schema import CSVRow, ExtractionStats

    # Create CSV row
    row = CSVRow(
        code="1.1.1.2.3",
        title="Block Work",
        tower="Tower 1",
        ...
    )
"""

from dataclasses import dataclass
from typing import Optional, List


# =============================================================================
# CSV Row Schema
# =============================================================================

@dataclass
class CSVRow:
    """
    Single row in the output CSV.

    All fields are strings (CSV format).
    Null/missing values are represented as empty strings.
    """
    code: str              # outline_number
    title: str             # name
    tower: str             # attributes.tower
    floor: str             # attributes.floor
    main_category: str     # attributes.main_category
    sub_category: str      # attributes.sub_category
    trade_type: str        # attributes.trade_type
    slab_works: str        # attributes.slab_works
    cost_plan_total: str   # cost_plan_total (as string for CSV)
    start_date_plan: str   # dates.plan.start
    end_date_plan: str     # dates.plan.end
    start_date_actual: str # dates.actual.start
    end_date_actual: str   # dates.actual.end
    start_date_sprint: str # dates.sprint.start
    end_date_sprint: str   # dates.sprint.end
    progress: str          # progress.percent_complete (as string for CSV)


# Column order for CSV output
CSV_COLUMNS = [
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


# =============================================================================
# Extraction Statistics
# =============================================================================

@dataclass
class ExtractionStats:
    """Statistics for single file extraction."""
    project: str
    total_tasks: int
    summary_tasks: int
    leaf_tasks: int
    milestones: int
    rows_written: int
    output_file: str


@dataclass
class BatchStats:
    """Statistics for batch extraction."""
    total_projects: int
    successful: int
    failed: int
    total_rows: int
    projects: List[ExtractionStats]


# =============================================================================
# Helper Functions
# =============================================================================

def safe_get(obj, *keys, default=''):
    """
    Safely get nested dictionary values.

    Args:
        obj: Root dictionary
        *keys: Keys to traverse
        default: Default value if not found

    Returns:
        Value at path or default

    Example:
        tower = safe_get(task, 'attributes', 'tower')
    """
    for key in keys:
        if obj is None:
            return default
        obj = obj.get(key) if isinstance(obj, dict) else None
    return obj if obj is not None else default


def extract_csv_row(task: dict) -> CSVRow:
    """
    Extract CSV row from task dictionary.

    Args:
        task: Task dictionary from master JSON

    Returns:
        CSVRow dataclass instance
    """
    # Handle potentially null nested objects
    dates = task.get('dates') or {}
    plan = dates.get('plan') or {}
    actual = dates.get('actual') or {}
    sprint = dates.get('sprint') or {}
    attributes = task.get('attributes') or {}
    progress = task.get('progress') or {}

    return CSVRow(
        code=task.get('outline_number', ''),
        title=task.get('name', ''),
        tower=attributes.get('tower') or '',
        floor=attributes.get('floor') or '',
        main_category=attributes.get('main_category') or '',
        sub_category=attributes.get('sub_category') or '',
        trade_type=attributes.get('trade_type') or '',
        slab_works=attributes.get('slab_works') or '',
        cost_plan_total=str(task.get('cost_plan_total', '')) if task.get('cost_plan_total') is not None else '',
        start_date_plan=plan.get('start') or '',
        end_date_plan=plan.get('end') or '',
        start_date_actual=actual.get('start') or '',
        end_date_actual=actual.get('end') or '',
        start_date_sprint=sprint.get('start') or '',
        end_date_sprint=sprint.get('end') or '',
        progress=str(progress.get('percent_complete', '')) if progress.get('percent_complete') is not None else '',
    )


def row_to_dict(row: CSVRow) -> dict:
    """
    Convert CSVRow to dictionary for csv.DictWriter.

    Args:
        row: CSVRow instance

    Returns:
        Dictionary with column names as keys
    """
    return {
        'code': row.code,
        'title': row.title,
        'tower': row.tower,
        'floor': row.floor,
        'main_category': row.main_category,
        'sub_category': row.sub_category,
        'trade_type': row.trade_type,
        'slab_works': row.slab_works,
        'cost_plan_total': row.cost_plan_total,
        'start_date_plan': row.start_date_plan,
        'end_date_plan': row.end_date_plan,
        'start_date_actual': row.start_date_actual,
        'end_date_actual': row.end_date_actual,
        'start_date_sprint': row.start_date_sprint,
        'end_date_sprint': row.end_date_sprint,
        'progress': row.progress,
    }


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example: Create sample CSV row
    sample_task = {
        "outline_number": "1.1.1.2.3",
        "name": "Block Work Ground Floor",
        "attributes": {
            "tower": "Tower 1",
            "floor": "Ground Floor",
            "main_category": "Finishing",
            "sub_category": "Tower Civil Finishes",
            "trade_type": "Blockwork",
            "slab_works": "Non-slab"
        },
        "cost_plan_total": 125000.00,
        "dates": {
            "plan": {"start": "2025-04-15", "end": "2025-05-20"},
            "actual": {"start": "2025-04-18", "end": None},
            "sprint": {"start": "2025-04-10", "end": "2025-05-10"}
        },
        "progress": {"percent_complete": 45}
    }

    row = extract_csv_row(sample_task)
    print("CSV Row:")
    print(f"  code: {row.code}")
    print(f"  title: {row.title}")
    print(f"  tower: {row.tower}")
    print(f"  progress: {row.progress}")

    print("\nAs dict:")
    print(row_to_dict(row))
