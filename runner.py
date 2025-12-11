#!/usr/bin/env python3
"""
XML to JSON ETL Runner for CCO Dashboard

Converts Asta Powerproject XML files to JSON format according to
the master schema (task_schema.json) and mapping rules.

Usage:
    # Standard processing with enrichment (default)
    python runner.py                                    # Process all XML files with enrichment
    python runner.py --file Miraya.xml                  # Process single file with enrichment

    # Enrichment control
    python runner.py --no-enrich-zone-region            # Skip zone/region enrichment
    python runner.py --no-enrich-tower-floor            # Skip tower/floor enrichment
    python runner.py --no-enrich                        # Skip all enrichment

    # Trade type enrichment (LLM-based)
    python runner.py --enrich-trade-types --openrouter-api-key YOUR_KEY  # Enable LLM classification
    python runner.py --file Miraya.xml --enrich-trade-types              # Single file with trade types

    # Sprint schedule enrichment
    python runner.py --enrich-sprint                                      # Enrich with Sprint dates
    python runner.py --file Miraya.xml --enrich-sprint                   # Single file with Sprint dates
    python runner.py --enrich-sprint --sprint-dir ./custom/sprint/path   # Custom Sprint XML directory

    # Update existing outputs with enrichment
    python runner.py --enrich-only                      # Enrich existing JSON outputs
    python runner.py --enrich-only --enrich-zone-region # Only enrich zone/region
    python runner.py --enrich-only --enrich-tower-floor # Only enrich tower/floor

    # Other modes
    python runner.py --validate-only                    # Run validation on existing output
    python runner.py --dry-run                          # Parse and transform without saving
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Load .env file if it exists
def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.cost_timeline import calculate_cost_timeline
from src.enrichment import enrich_attributes
from src.task_builder import build_all_tasks
from src.trade_type_classifier import classify_activities_with_llm, get_classification_summary
from src.trade_type_extractor import extract_unique_activities, get_activity_summary
from src.trade_type_mapper import enrich_tasks_with_trade_types, get_enrichment_summary
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
from src.sprint_enrichment import enrich_sprint_dates


def process_single_file(
    xml_path: str,
    output_dir: str,
    dry_run: bool = False,
    sample_size: int = 10,
    enrich_zone_region: bool = True,
    enrich_tower_floor: bool = True,
    enrich_trade_types: bool = False,
    llm=None,
    cheat_sheet_path: str = None,
    enrich_sprint: bool = False,
    sprint_dir: str = None,
    logger=None,
) -> dict:
    """
    Process a single XML file.

    Args:
        xml_path: Path to XML file
        output_dir: Output directory
        dry_run: If True, don't save output files
        sample_size: Number of tasks for sample validation
        enrich_zone_region: Whether to enrich zone/region
        enrich_tower_floor: Whether to enrich tower/floor
        enrich_trade_types: Whether to enrich trade types using LLM
        llm: UniversalLLM instance for trade type classification
        cheat_sheet_path: Path to trade type cheat sheet
        enrich_sprint: Whether to enrich with Sprint schedule dates
        sprint_dir: Directory containing Sprint XML files
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

        # Apply spatial enrichment (zone/region/tower/floor)
        if enrich_zone_region or enrich_tower_floor:
            if logger:
                logger.debug("Enriching spatial attributes...")

            tasks = enrich_attributes(
                tasks=tasks,
                project_name=project_name,
                enrich_zone_region_flag=enrich_zone_region,
                enrich_tower_floor_flag=enrich_tower_floor,
            )

            if logger:
                enriched_count = sum(
                    1 for t in tasks
                    if t.get("attributes") and (
                        t["attributes"].get("zone") or
                        t["attributes"].get("tower") or
                        t["attributes"].get("floor")
                    )
                )
                logger.info(f"  Enriched {enriched_count} tasks with spatial attributes")

        # Apply trade type enrichment (LLM-based)
        if enrich_trade_types and llm and cheat_sheet_path:
            if logger:
                logger.info("  Enriching trade types with LLM...")

            try:
                # Extract unique activities
                unique_activities = extract_unique_activities(tasks, project_name)

                if logger:
                    logger.info(
                        f"  Extracted {unique_activities['unique_activity_count']} unique activities "
                        f"from {unique_activities['total_leaf_tasks']} leaf tasks"
                    )

                # Classify with LLM
                import asyncio
                classification_result = asyncio.run(
                    classify_activities_with_llm(
                        unique_activities, project_name, llm, cheat_sheet_path
                    )
                )

                if logger:
                    logger.info(
                        f"  Classified {classification_result['total_classified']} activities "
                        f"(high: {classification_result['confidence_distribution']['high']}, "
                        f"medium: {classification_result['confidence_distribution']['medium']}, "
                        f"low: {classification_result['confidence_distribution']['low']})"
                    )

                # Map classifications back to tasks
                enrichment_result = enrich_tasks_with_trade_types(
                    tasks, classification_result, project_name
                )

                stats["trade_type_enrichment"] = enrichment_result

                if logger:
                    logger.info(
                        f"  Enriched {enrichment_result['enrichment_stats']['enriched_tasks']} "
                        f"tasks with trade types ({enrichment_result['enrichment_rate']:.1%})"
                    )

            except Exception as e:
                if logger:
                    logger.error(f"  Trade type enrichment failed: {e}")
                stats["trade_type_error"] = str(e)

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

            # Enrich with Sprint dates if requested
            if enrich_sprint and sprint_dir:
                if logger:
                    logger.info(f"  Enriching with Sprint dates...")

                sprint_xml_path = os.path.join(sprint_dir, f"{project_name}.xml")

                if os.path.exists(sprint_xml_path):
                    try:
                        sprint_stats = enrich_sprint_dates(output_file, sprint_xml_path)
                        stats["sprint_enrichment"] = {
                            "matched": sprint_stats["matched"],
                            "unmatched": sprint_stats["unmatched"],
                            "match_rate": sprint_stats["match_rate"]
                        }
                        if logger:
                            logger.info(f"  Sprint: {sprint_stats['matched']}/{sprint_stats['aop_tasks']} "
                                      f"tasks matched ({sprint_stats['match_rate']:.1%})")
                    except Exception as e:
                        stats["errors"].append(f"Sprint enrichment failed: {e}")
                        if logger:
                            logger.error(f"  Sprint enrichment error: {e}")
                else:
                    if logger:
                        logger.warning(f"  Sprint XML not found: {sprint_xml_path}")

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


def enrich_existing_outputs(
    output_dir: str,
    enrich_zone_region: bool = True,
    enrich_tower_floor: bool = True,
    logger=None,
) -> dict:
    """
    Enrich existing JSON outputs with attributes.

    Args:
        output_dir: Output directory with JSON files
        enrich_zone_region: Whether to enrich zone/region
        enrich_tower_floor: Whether to enrich tower/floor
        logger: Logger instance

    Returns:
        Dictionary with enrichment results
    """
    results = {"projects": [], "total_enriched": 0}

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
            logger.info(f"Enriching {project_name}...")

        try:
            # Load output JSON
            tasks = load_json_file(str(json_file))

            # Apply enrichment
            tasks = enrich_attributes(
                tasks=tasks,
                project_name=project_name,
                enrich_zone_region_flag=enrich_zone_region,
                enrich_tower_floor_flag=enrich_tower_floor,
            )

            # Count enriched tasks
            enriched_count = sum(
                1 for t in tasks
                if t.get("attributes") and (
                    t["attributes"].get("zone") or
                    t["attributes"].get("tower") or
                    t["attributes"].get("floor")
                )
            )

            # Save enriched output
            save_json_file(tasks, str(json_file))

            results["projects"].append({
                "project": project_name,
                "total_tasks": len(tasks),
                "enriched_tasks": enriched_count,
            })
            results["total_enriched"] += enriched_count

            if logger:
                logger.info(f"  Enriched {enriched_count}/{len(tasks)} tasks")

        except Exception as e:
            if logger:
                logger.error(f"  Error enriching {project_name}: {e}")
            results["projects"].append({
                "project": project_name,
                "error": str(e),
            })

    return results


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

    # Enrichment arguments
    parser.add_argument(
        "--enrich-only",
        action="store_true",
        help="Enrich existing JSON outputs (no XML processing)",
    )
    parser.add_argument(
        "--no-enrich", action="store_true", help="Skip all enrichment"
    )
    parser.add_argument(
        "--enrich-zone-region",
        action="store_true",
        help="Enrich only zone/region (use with --enrich-only)",
    )
    parser.add_argument(
        "--enrich-tower-floor",
        action="store_true",
        help="Enrich only tower/floor (use with --enrich-only)",
    )
    parser.add_argument(
        "--no-enrich-zone-region",
        action="store_true",
        help="Skip zone/region enrichment",
    )
    parser.add_argument(
        "--no-enrich-tower-floor",
        action="store_true",
        help="Skip tower/floor enrichment",
    )
    parser.add_argument(
        "--enrich-trade-types",
        action="store_true",
        help="Enable trade type enrichment using LLM",
    )
    parser.add_argument(
        "--openrouter-api-key",
        help="OpenRouter API key for LLM classification",
    )
    parser.add_argument(
        "--cheat-sheet",
        default="./trade-type-cheat-sheet.md",
        help="Path to trade type cheat sheet (default: ./trade-type-cheat-sheet.md)",
    )
    parser.add_argument(
        "--enrich-sprint",
        action="store_true",
        help="Enrich with Sprint schedule dates",
    )
    parser.add_argument(
        "--sprint-dir",
        default="./input/all-sprint-schedules",
        help="Directory containing Sprint XML files (default: ./input/all-sprint-schedules)",
    )

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    input_dir = (script_dir / args.input_dir).resolve()
    output_dir = (script_dir / args.output_dir).resolve()
    sprint_dir = (script_dir / args.sprint_dir).resolve() if args.enrich_sprint else None

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

    # Determine enrichment flags
    if args.enrich_only:
        # When using --enrich-only, default to both unless specific flags are set
        if args.enrich_zone_region or args.enrich_tower_floor:
            enrich_zone_region_flag = args.enrich_zone_region
            enrich_tower_floor_flag = args.enrich_tower_floor
        else:
            # Default: enrich both
            enrich_zone_region_flag = True
            enrich_tower_floor_flag = True
    else:
        # Normal processing mode
        if args.no_enrich:
            enrich_zone_region_flag = False
            enrich_tower_floor_flag = False
        else:
            enrich_zone_region_flag = not args.no_enrich_zone_region
            enrich_tower_floor_flag = not args.no_enrich_tower_floor

    # Log enrichment settings
    enrichments_enabled = []
    if enrich_zone_region_flag:
        enrichments_enabled.append("zone/region")
    if enrich_tower_floor_flag:
        enrichments_enabled.append("tower/floor")
    if args.enrich_sprint:
        enrichments_enabled.append("sprint")

    # Initialize LLM for trade type enrichment
    llm = None
    cheat_sheet_path = None
    enrich_trade_types_flag = args.enrich_trade_types

    if enrich_trade_types_flag:
        # Check for API key
        api_key = args.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logger.error(
                "Trade type enrichment requires OpenRouter API key. "
                "Provide --openrouter-api-key or set OPENROUTER_API_KEY environment variable."
            )
            return 1

        # Check for cheat sheet
        script_dir = Path(__file__).parent
        cheat_sheet_path = (script_dir / args.cheat_sheet).resolve()

        if not cheat_sheet_path.exists():
            logger.error(f"Cheat sheet not found: {cheat_sheet_path}")
            return 1

        # Initialize LLM
        try:
            from src.llm_utils import UniversalLLM

            llm = UniversalLLM(
                api_key=api_key, model="google/gemini-2.5-flash"
            )
            enrichments_enabled.append("trade_types (LLM)")
            logger.info(f"Initialized LLM for trade type enrichment")
            logger.info(f"Cheat sheet: {cheat_sheet_path}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return 1

    if enrichments_enabled:
        logger.info(f"Enrichment enabled: {', '.join(enrichments_enabled)}")
    else:
        logger.info("Enrichment disabled")

    # Enrich only mode
    if args.enrich_only:
        logger.info("Running enrichment only...")
        results = enrich_existing_outputs(
            str(output_dir),
            enrich_zone_region_flag,
            enrich_tower_floor_flag,
            logger,
        )
        logger.info(
            f"Enrichment complete. Total enriched: {results['total_enriched']}"
        )
        return 0

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
            enrich_zone_region=enrich_zone_region_flag,
            enrich_tower_floor=enrich_tower_floor_flag,
            enrich_trade_types=enrich_trade_types_flag,
            llm=llm,
            cheat_sheet_path=str(cheat_sheet_path) if cheat_sheet_path else None,
            enrich_sprint=args.enrich_sprint,
            sprint_dir=str(sprint_dir) if sprint_dir else None,
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
