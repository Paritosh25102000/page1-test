#!/usr/bin/env python3
"""
Script to update sprint field names in all output JSON files.

Changes 'finish' to 'end' in sprint date objects to maintain consistency
with other date range objects (plan, manual, actual) which all use 'end'.

Usage:
    python scripts/fix_sprint_field_names.py

This will update all JSON files in output/json/ directory.
"""

import json
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fix_sprint_field_in_task(task: dict) -> bool:
    """
    Fix sprint field name in a single task.

    Args:
        task: Task dictionary

    Returns:
        True if field was updated, False otherwise
    """
    if not isinstance(task, dict):
        return False

    dates = task.get('dates')
    if not dates or not isinstance(dates, dict):
        return False

    sprint = dates.get('sprint')
    if not sprint or not isinstance(sprint, dict):
        return False

    # Check if 'finish' exists
    if 'finish' in sprint:
        # Rename 'finish' to 'end'
        sprint['end'] = sprint.pop('finish')
        return True

    return False


def fix_sprint_fields_in_file(json_path: Path) -> dict:
    """
    Update sprint field names in a single JSON file.

    Args:
        json_path: Path to JSON file

    Returns:
        Statistics dict with update counts
    """
    logger.info(f"Processing {json_path.name}...")

    # Read file
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Process all tasks
    updated_count = 0
    total_tasks = len(data) if isinstance(data, list) else 0

    if isinstance(data, list):
        for task in data:
            if fix_sprint_field_in_task(task):
                updated_count += 1

    # Write back only if changes were made
    if updated_count > 0:
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"✓ {json_path.name}: Updated {updated_count} sprint fields")
    else:
        logger.info(f"○ {json_path.name}: No sprint fields to update")

    return {
        'file': json_path.name,
        'total_tasks': total_tasks,
        'updated_count': updated_count
    }


def main():
    """Main function to process all JSON files."""
    # Define output directory
    output_dir = Path(__file__).parent.parent / 'output' / 'json'

    if not output_dir.exists():
        logger.error(f"Output directory not found: {output_dir}")
        return

    # Find all JSON files
    json_files = list(output_dir.glob('*.json'))

    if not json_files:
        logger.warning(f"No JSON files found in {output_dir}")
        return

    logger.info(f"Found {len(json_files)} JSON files to process")
    logger.info("-" * 60)

    # Process each file
    results = []
    for json_file in sorted(json_files):
        try:
            stats = fix_sprint_fields_in_file(json_file)
            results.append(stats)
        except Exception as e:
            logger.error(f"✗ Failed to process {json_file.name}: {e}")
            results.append({
                'file': json_file.name,
                'error': str(e)
            })

    # Summary
    logger.info("-" * 60)
    logger.info("Summary:")
    total_updated = sum(r.get('updated_count', 0) for r in results)
    total_files_updated = sum(1 for r in results if r.get('updated_count', 0) > 0)
    total_files = len(results)

    logger.info(f"Files processed: {total_files}")
    logger.info(f"Files updated: {total_files_updated}")
    logger.info(f"Total sprint fields updated: {total_updated}")

    # List files with updates
    if total_files_updated > 0:
        logger.info("\nFiles with updates:")
        for r in results:
            if r.get('updated_count', 0) > 0:
                logger.info(f"  - {r['file']}: {r['updated_count']} fields")


if __name__ == '__main__':
    main()
