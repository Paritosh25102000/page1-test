#!/usr/bin/env python3
"""
Staging ETL Runner

Generates pre-aggregated staging JSON for dashboard pages.

Usage:
    python runner_staging.py                    # Generate Page 1
    python runner_staging.py --page page1       # Explicit page
    python runner_staging.py --dry-run          # Preview without saving
    python runner_staging.py --validate-only    # Validate existing output
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

from src.staging.aggregator import generate_staging_data
from src.staging.validators import validate_staging_output


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    parser = argparse.ArgumentParser(
        description='Generate staging JSON for dashboard'
    )

    parser.add_argument(
        '--page',
        default='page1',
        help='Dashboard page to generate (default: page1)'
    )
    parser.add_argument(
        '--input-dir',
        default='output/json',
        help='Directory containing Master JSON files'
    )
    parser.add_argument(
        '--output-dir',
        default='output/staging',
        help='Directory for staging output'
    )
    parser.add_argument(
        '--current-date',
        help='Override current date (YYYY-MM-DD) for testing'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate but do not save output'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Validate existing output without regenerating'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Output file mapping
    page_files = {
        'page1': 'page1-executive-summary.json'
    }

    output_file = page_files.get(args.page)
    if not output_file:
        logger.error(f"Unknown page: {args.page}")
        return 1

    output_path = Path(args.output_dir) / output_file

    # Validate-only mode
    if args.validate_only:
        logger.info(f"Validating existing output: {output_path}")
        with open(output_path, 'r') as f:
            data = json.load(f)
        errors = validate_staging_output(data, args.page)
        if errors:
            logger.error(f"Validation errors: {errors}")
            return 1
        logger.info("Validation passed")
        return 0

    # Generate staging data
    logger.info(f"Generating staging data for {args.page}")
    start_time = datetime.now()

    data = generate_staging_data(
        json_dir=args.input_dir,
        page=args.page,
        current_date=args.current_date
    )

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"Generated in {elapsed:.1f} seconds")

    # Summary
    filter_count = len(data.get('dashboard_data', {}))
    logger.info(f"Filter keys generated: {filter_count}")

    # Save output
    if not args.dry_run:
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved to: {output_path}")

        # File size
        size_mb = output_path.stat().st_size / (1024 * 1024)
        logger.info(f"File size: {size_mb:.2f} MB")
    else:
        logger.info("Dry run - output not saved")

    return 0


if __name__ == '__main__':
    exit(main())
