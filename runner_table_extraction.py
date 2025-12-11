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
