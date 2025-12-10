#!/usr/bin/env python3
"""
XML to JSON ETL Runner for CCO Dashboard

Converts Asta Powerproject XML files to JSON format according to
the master schema (task_schema.json) and mapping rules.

Usage:
    python runner.py                        # Process all XML files
    python runner.py --file Miraya.xml      # Process single file
    python runner.py --validate-only        # Run validation on existing output
    python runner.py --dry-run              # Parse and transform without saving
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.cost_timeline import calculate_cost_timeline
from src.task_builder import build_all_tasks
from src.utils import (
    ensure_directory,
    get_project_name_from_file,
    get_xml_files,
    load_json_file,
    save_json_file,
    setup_logging,
)
from src.validators import (
    calculate_field_coverage,
    generate_qa_report,
    sample_validation,
    validate_task_types,
)
from src.xml_parser import parse_xml_file


def process_single_file(
    xml_path: str,
    output_dir: str,
    dry_run: bool = False,
    sample_size: int = 10,
    logger=None,
) -> dict:
    """
    Process a single XML file.

    Args:
        xml_path: Path to XML file
        output_dir: Output directory
        dry_run: If True, don't save output files
        sample_size: Number of tasks for sample validation
        logger: Logger instance

    Returns:
        Dictionary with processing stats
    """
    project_name = get_project_name_from_file(xml_path)

    if logger:
        logger.info(f"Processing {project_name}...")

    stats = {
        "project": project_name,
        "xml_file": xml_path,
        "status": "success",
        "tasks_processed": 0,
        "errors": [],
    }

    try:
        # Parse XML
        if logger:
            logger.debug(f"Parsing XML: {xml_path}")

        xml_data = parse_xml_file(xml_path)

        tasks_raw = xml_data["tasks"]
        task_assignment_map = xml_data["task_assignment_map"]

        stats["tasks_found"] = len(tasks_raw)

        if logger:
            logger.info(f"  Found {len(tasks_raw)} tasks")

        # Build transformed tasks
        if logger:
            logger.debug("Transforming tasks...")

        tasks = build_all_tasks(
            tasks=tasks_raw,
            task_assignment_map=task_assignment_map,
            project_name=project_name,
            cost_timeline_builder=calculate_cost_timeline,
        )

        stats["tasks_processed"] = len(tasks)

        # Run validation
        if logger:
            logger.debug("Running validation...")

        type_validation = validate_task_types(tasks)
        field_coverage = calculate_field_coverage(tasks)

        stats["parents"] = type_validation["parents"]
        stats["leaves"] = type_validation["leaves"]
        stats["milestones"] = type_validation["milestones"]
        stats["type_issues"] = len(type_validation["issues"])

        if logger:
            logger.info(
                f"  Types: {type_validation['parents']} parents, "
                f"{type_validation['leaves']} leaves, "
                f"{type_validation['milestones']} milestones"
            )

        # Sample validation against source XML
        sample_results = sample_validation(tasks, xml_path, sample_size)
        stats["sample_pass_rate"] = sample_results["pass_rate"]

        if logger:
            logger.info(
                f"  Sample validation: {sample_results['passed']}/{sample_results['sample_size']} passed"
            )

        # Generate QA report
        qa_report = generate_qa_report(
            project_name=project_name,
            total_tasks=len(tasks),
            type_validation=type_validation,
            sample_results=sample_results,
            field_coverage=field_coverage,
        )

        if not dry_run:
            # Save output JSON
            json_dir = os.path.join(output_dir, "json")
            ensure_directory(json_dir)

            output_file = os.path.join(json_dir, f"{project_name}.json")
            save_json_file(tasks, output_file)

            stats["output_file"] = output_file

            if logger:
                logger.info(f"  Saved: {output_file}")

            # Save QA report
            reports_dir = os.path.join(output_dir, "reports")
            ensure_directory(reports_dir)

            report_file = os.path.join(reports_dir, f"qa_report_{project_name}.json")
            save_json_file(qa_report, report_file)

            if logger:
                logger.debug(f"  QA report: {report_file}")

    except Exception as e:
        stats["status"] = "error"
        stats["errors"].append(str(e))
        if logger:
            logger.error(f"  Error: {e}")

    return stats


def run_validation_only(
    output_dir: str, xml_dir: str, sample_size: int = 10, logger=None
) -> dict:
    """
    Run validation on existing output files.

    Args:
        output_dir: Output directory with JSON files
        xml_dir: Directory with source XML files
        sample_size: Number of tasks for sample validation
        logger: Logger instance

    Returns:
        Dictionary with validation results
    """
    results = {"projects": [], "total_issues": 0}

    json_dir = os.path.join(output_dir, "json")
    if not os.path.exists(json_dir):
        if logger:
            logger.error(f"JSON directory not found: {json_dir}")
        return results

    # Find all JSON files
    json_files = sorted(Path(json_dir).glob("*.json"))

    for json_file in json_files:
        project_name = json_file.stem

        if logger:
            logger.info(f"Validating {project_name}...")

        # Load output JSON
        tasks = load_json_file(str(json_file))

        # Find corresponding XML
        xml_file = os.path.join(xml_dir, f"{project_name}.xml")
        if not os.path.exists(xml_file):
            if logger:
                logger.warning(f"  XML file not found: {xml_file}")
            continue

        # Run validation
        type_validation = validate_task_types(tasks)
        sample_results = sample_validation(tasks, xml_file, sample_size)
        field_coverage = calculate_field_coverage(tasks)

        qa_report = generate_qa_report(
            project_name=project_name,
            total_tasks=len(tasks),
            type_validation=type_validation,
            sample_results=sample_results,
            field_coverage=field_coverage,
        )

        results["projects"].append(qa_report)
        results["total_issues"] += len(type_validation["issues"])

        if logger:
            logger.info(
                f"  Sample pass rate: {sample_results['pass_rate']:.0%}, "
                f"Issues: {len(type_validation['issues'])}"
            )

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="XML to JSON ETL for CCO Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", help="Process single XML file")
    parser.add_argument(
        "--input-dir",
        default="../source_data/asta-source-cco-dashboard/all-aop-baselines",
        help="Input directory containing XML files",
    )
    parser.add_argument(
        "--output-dir", default="./output", help="Output directory for JSON files"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run validation on existing output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and transform without saving",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="QA sample size per file (default: 100)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    input_dir = (script_dir / args.input_dir).resolve()
    output_dir = (script_dir / args.output_dir).resolve()

    # Setup logging
    logs_dir = os.path.join(output_dir, "logs")
    logger = setup_logging(logs_dir, "etl")

    if args.verbose:
        import logging

        logger.setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("CCO Dashboard ETL - XML to JSON Conversion")
    logger.info("=" * 60)
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")

    # Validate only mode
    if args.validate_only:
        logger.info("Running validation only...")
        results = run_validation_only(
            str(output_dir), str(input_dir), args.sample_size, logger
        )
        logger.info(f"Validation complete. Total issues: {results['total_issues']}")
        return 0 if results["total_issues"] == 0 else 1

    # Get files to process
    if args.file:
        # Single file mode
        if os.path.isabs(args.file):
            xml_files = [args.file]
        else:
            xml_files = [str(input_dir / args.file)]
    else:
        # All files mode
        try:
            xml_files = get_xml_files(str(input_dir))
        except FileNotFoundError as e:
            logger.error(str(e))
            return 1

    if not xml_files:
        logger.error("No XML files found")
        return 1

    logger.info(f"Found {len(xml_files)} XML files to process")

    # Process files
    all_stats = []
    success_count = 0
    error_count = 0

    for xml_file in xml_files:
        stats = process_single_file(
            xml_path=xml_file,
            output_dir=str(output_dir),
            dry_run=args.dry_run,
            sample_size=args.sample_size,
            logger=logger,
        )
        all_stats.append(stats)

        if stats["status"] == "success":
            success_count += 1
        else:
            error_count += 1

    # Generate summary report
    summary = {
        "run_timestamp": datetime.now().isoformat(),
        "input_directory": str(input_dir),
        "output_directory": str(output_dir),
        "dry_run": args.dry_run,
        "total_files": len(xml_files),
        "successful": success_count,
        "errors": error_count,
        "total_tasks_processed": sum(s.get("tasks_processed", 0) for s in all_stats),
        "file_results": all_stats,
    }

    if not args.dry_run:
        reports_dir = os.path.join(output_dir, "reports")
        ensure_directory(reports_dir)
        summary_file = os.path.join(reports_dir, "summary_report.json")
        save_json_file(summary, summary_file)
        logger.info(f"Summary report: {summary_file}")

    # Print summary
    logger.info("=" * 60)
    logger.info("Processing Complete")
    logger.info("=" * 60)
    logger.info(f"Files processed: {success_count}/{len(xml_files)}")
    logger.info(f"Total tasks: {summary['total_tasks_processed']}")

    if error_count > 0:
        logger.warning(f"Errors: {error_count}")
        for stats in all_stats:
            if stats.get("errors"):
                logger.warning(f"  {stats['project']}: {stats['errors']}")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
