"""
Enhanced report generator for COO Dashboard ETL pipeline.

Generates comprehensive pipeline reports combining Stage 1 and Stage 2 results.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_pipeline_report(
    project_name: str,
    json_output_path: str,
    csv_output_path: Optional[str] = None,
    qa_report_path: Optional[str] = None,
    summary_report_path: Optional[str] = None,
) -> dict:
    """
    Generate comprehensive pipeline report for a single project.

    Args:
        project_name: Name of the project
        json_output_path: Path to the JSON output file
        csv_output_path: Path to the CSV output file (optional)
        qa_report_path: Path to existing QA report (optional)
        summary_report_path: Path to summary report with enrichment stats (optional)

    Returns:
        Complete pipeline report dictionary
    """
    report = {
        "report_type": "pipeline_report",
        "report_version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "project": project_name,
        "stage1": {},
        "stage2": {},
        "enrichment": {},
        "validation": {},
        "output_files": {},
    }

    # Load JSON output for analysis
    tasks = []
    if os.path.exists(json_output_path):
        with open(json_output_path, "r") as f:
            tasks = json.load(f)

        json_size = os.path.getsize(json_output_path)
        report["output_files"]["json"] = {
            "path": json_output_path,
            "size_bytes": json_size,
            "size_human": _format_size(json_size),
        }

    # Stage 1: Task counts and classification
    report["stage1"] = _analyze_tasks(tasks)

    # Stage 2: CSV stats
    if csv_output_path and os.path.exists(csv_output_path):
        csv_size = os.path.getsize(csv_output_path)
        with open(csv_output_path, "r") as f:
            csv_lines = sum(1 for _ in f)

        report["stage2"] = {
            "csv_rows": csv_lines - 1,  # Exclude header
            "csv_rows_with_header": csv_lines,
        }
        report["output_files"]["csv"] = {
            "path": csv_output_path,
            "size_bytes": csv_size,
            "size_human": _format_size(csv_size),
        }

    # Enrichment stats from tasks
    report["enrichment"] = _analyze_enrichment(tasks)

    # Load QA report if available
    if qa_report_path and os.path.exists(qa_report_path):
        with open(qa_report_path, "r") as f:
            qa_report = json.load(f)
        report["validation"] = {
            "sample_size": qa_report.get("sample_size", 0),
            "sample_pass_rate": qa_report.get("sample_pass_rate", 0),
            "validation_issues_count": len(qa_report.get("validation_issues", [])),
            "sample_failures_count": len(qa_report.get("sample_failures", [])),
            "field_coverage": qa_report.get("field_coverage", {}),
        }

    # Load enrichment stats from summary report if available
    if summary_report_path and os.path.exists(summary_report_path):
        with open(summary_report_path, "r") as f:
            summary = json.load(f)

        # Find this project's results
        for result in summary.get("file_results", []):
            if result.get("project") == project_name:
                # Trade type enrichment - merge with task analysis
                if "trade_type_enrichment" in result:
                    tte = result["trade_type_enrichment"]
                    # Update trade_types with enrichment stats from summary
                    report["enrichment"]["trade_types"].update({
                        "enriched_tasks": tte.get("enrichment_stats", {}).get("enriched_tasks", 0),
                        "enrichment_rate": tte.get("enrichment_rate", 0),
                        "by_context": tte.get("enrichment_stats", {}).get("by_context", {}),
                        "by_confidence": tte.get("enrichment_stats", {}).get("by_confidence", {}),
                    })

                # Sprint enrichment
                if "sprint_enrichment" in result:
                    se = result["sprint_enrichment"]
                    report["enrichment"]["sprint"] = {
                        "matched": se.get("matched", 0),
                        "unmatched": se.get("unmatched", 0),
                        "match_rate": se.get("match_rate", 0),
                    }
                break

    return report


def _analyze_tasks(tasks: list) -> dict:
    """Analyze task list and return statistics."""
    stats = {
        "total_tasks": len(tasks),
        "parents": 0,
        "leaves": 0,
        "milestones": 0,
    }

    for task in tasks:
        if task.get("is_summary"):
            stats["parents"] += 1
        elif task.get("is_milestone"):
            stats["milestones"] += 1
        else:
            stats["leaves"] += 1

    return stats


def _analyze_enrichment(tasks: list) -> dict:
    """Analyze enrichment coverage from tasks."""
    enrichment = {
        "zone_region": {"enriched": 0, "total_applicable": 0},
        "tower_floor": {"with_tower": 0, "with_floor": 0, "total_applicable": 0},
        "trade_types": {"enriched": 0, "total_applicable": 0},
    }

    for task in tasks:
        attrs = task.get("attributes")
        if attrs is not None:
            enrichment["zone_region"]["total_applicable"] += 1
            enrichment["tower_floor"]["total_applicable"] += 1
            enrichment["trade_types"]["total_applicable"] += 1

            if attrs.get("zone") and attrs.get("region"):
                enrichment["zone_region"]["enriched"] += 1
            if attrs.get("tower"):
                enrichment["tower_floor"]["with_tower"] += 1
            if attrs.get("floor"):
                enrichment["tower_floor"]["with_floor"] += 1
            if attrs.get("trade_type"):
                enrichment["trade_types"]["enriched"] += 1

    # Calculate rates
    for key in enrichment:
        total = enrichment[key].get("total_applicable", 0)
        if total > 0:
            if key == "zone_region":
                enrichment[key]["rate"] = enrichment[key]["enriched"] / total
            elif key == "tower_floor":
                enrichment[key]["tower_rate"] = enrichment[key]["with_tower"] / total
                enrichment[key]["floor_rate"] = enrichment[key]["with_floor"] / total
            elif key == "trade_types":
                enrichment[key]["rate"] = enrichment[key]["enriched"] / total

    return enrichment


def _format_size(size_bytes: int) -> str:
    """Format bytes to human readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def generate_markdown_summary(report: dict) -> str:
    """
    Generate markdown summary from pipeline report.

    Args:
        report: Pipeline report dictionary

    Returns:
        Markdown formatted summary string
    """
    lines = []

    project = report.get("project", "Unknown")
    lines.append(f"# Pipeline Report: {project}")
    lines.append(f"\n**Generated**: {report.get('generated_at', 'N/A')}")
    lines.append("")

    # Stage 1 Results
    s1 = report.get("stage1", {})
    lines.append("## Stage 1 (XML to JSON) Results")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total tasks | {s1.get('total_tasks', 0):,} |")
    lines.append(f"| Parent tasks | {s1.get('parents', 0):,} |")
    lines.append(f"| Leaf tasks | {s1.get('leaves', 0):,} |")
    lines.append(f"| Milestones | {s1.get('milestones', 0):,} |")
    lines.append("")

    # Enrichment Results
    enrich = report.get("enrichment", {})
    lines.append("## Enrichment Results")
    lines.append("")
    lines.append("| Enrichment | Result |")
    lines.append("|------------|--------|")

    # Zone/Region
    zr = enrich.get("zone_region", {})
    zr_rate = zr.get("rate", 0)
    lines.append(f"| Zone/Region | {zr_rate:.1%} ({zr.get('enriched', 0):,}/{zr.get('total_applicable', 0):,} tasks) |")

    # Tower/Floor
    tf = enrich.get("tower_floor", {})
    tower_rate = tf.get("tower_rate", 0)
    floor_rate = tf.get("floor_rate", 0)
    lines.append(f"| Tower | {tower_rate:.1%} ({tf.get('with_tower', 0):,} tasks) |")
    lines.append(f"| Floor | {floor_rate:.1%} ({tf.get('with_floor', 0):,} tasks) |")

    # Trade Types
    tt = enrich.get("trade_types", {})
    if tt:
        # Use enrichment_rate from summary if available, else use rate from task analysis
        tt_rate = tt.get("enrichment_rate", tt.get("rate", 0))
        enriched = tt.get("enriched_tasks", tt.get("enriched", 0))
        total = tt.get("total_applicable", enriched)
        if total > 0:
            lines.append(f"| Trade Types (LLM) | {tt_rate:.1%} ({enriched:,}/{total:,} leaf tasks) |")

        # Additional trade type details if available
        if "by_context" in tt:
            ctx = tt["by_context"]
            ctx_str = ", ".join(f"{k}: {v}" for k, v in ctx.items() if v > 0)
            if ctx_str:
                lines.append(f"| - by context | {ctx_str} |")

        if "by_confidence" in tt:
            conf = tt["by_confidence"]
            conf_str = ", ".join(f"{k}: {v}" for k, v in conf.items() if v > 0)
            if conf_str:
                lines.append(f"| - by confidence | {conf_str} |")

    # Sprint
    sprint = enrich.get("sprint", {})
    if sprint:
        sprint_rate = sprint.get("match_rate", 0)
        lines.append(f"| Sprint Dates | {sprint_rate:.1%} ({sprint.get('matched', 0):,}/{sprint.get('matched', 0) + sprint.get('unmatched', 0):,} tasks) |")

    lines.append("")

    # Validation
    val = report.get("validation", {})
    if val:
        lines.append("## Validation Results")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Sample size | {val.get('sample_size', 0)} |")
        lines.append(f"| Sample pass rate | {val.get('sample_pass_rate', 0):.1%} |")
        lines.append(f"| Validation issues | {val.get('validation_issues_count', 0)} |")
        lines.append(f"| Sample failures | {val.get('sample_failures_count', 0)} |")
        lines.append("")

    # Stage 2 Results
    s2 = report.get("stage2", {})
    if s2:
        lines.append("## Stage 2 (JSON to CSV) Results")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| CSV rows | {s2.get('csv_rows', 0):,} |")
        lines.append("")

    # Output Files
    files = report.get("output_files", {})
    if files:
        lines.append("## Output Files")
        lines.append("")
        lines.append("| File | Size |")
        lines.append("|------|------|")
        for file_type, info in files.items():
            lines.append(f"| {info.get('path', file_type)} | {info.get('size_human', 'N/A')} |")
        lines.append("")

    return "\n".join(lines)


def save_pipeline_report(
    project_name: str,
    output_dir: str,
    json_output_path: str,
    csv_output_path: Optional[str] = None,
    qa_report_path: Optional[str] = None,
    summary_report_path: Optional[str] = None,
) -> tuple[str, str]:
    """
    Generate and save pipeline report in JSON and Markdown formats.

    Args:
        project_name: Name of the project
        output_dir: Directory to save reports
        json_output_path: Path to the JSON output file
        csv_output_path: Path to the CSV output file (optional)
        qa_report_path: Path to existing QA report (optional)
        summary_report_path: Path to summary report (optional)

    Returns:
        Tuple of (json_report_path, markdown_report_path)
    """
    # Generate report
    report = generate_pipeline_report(
        project_name=project_name,
        json_output_path=json_output_path,
        csv_output_path=csv_output_path,
        qa_report_path=qa_report_path,
        summary_report_path=summary_report_path,
    )

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON report
    json_report_path = os.path.join(output_dir, f"pipeline_report_{project_name}.json")
    with open(json_report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Generate and save markdown summary
    markdown = generate_markdown_summary(report)
    md_report_path = os.path.join(output_dir, f"pipeline_report_{project_name}.md")
    with open(md_report_path, "w") as f:
        f.write(markdown)

    return json_report_path, md_report_path
