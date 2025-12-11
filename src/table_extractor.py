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
        'cost_plan_total': task.get('cost_plan_total') if task.get('cost_plan_total') is not None else '',
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
    with open(json_file_path, 'r', encoding='utf-8') as f:
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

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Extraction report saved to: {output_path}")


if __name__ == '__main__':
    # Quick test with command line arguments
    import sys
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'output.csv'
        stats = extract_to_csv(json_file, output_file)
        print(json.dumps(stats, indent=2))
    else:
        print("Usage: python table_extractor.py <input.json> [output.csv]")
