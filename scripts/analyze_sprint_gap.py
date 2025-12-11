"""
Analyze the gap between AOP baseline and Sprint schedule.

This script compares two schedule files and generates a gap analysis report.
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


def parse_xml_schedule(xml_path: str) -> dict:
    """Parse XML schedule and extract key information."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extract project info
    project_info = {
        'name': root.find('.//Name').text if root.find('.//Name') is not None else 'Unknown',
        'start_date': root.find('.//StartDate').text if root.find('.//StartDate') is not None else None,
        'finish_date': root.find('.//FinishDate').text if root.find('.//FinishDate') is not None else None,
    }

    # Extract tasks
    tasks = []
    for task_elem in root.findall('.//Task'):
        task_data = {}

        # Basic fields
        for field in ['UID', 'Name', 'Type', 'WBS', 'OutlineLevel']:
            elem = task_elem.find(field)
            task_data[field.lower()] = elem.text if elem is not None else None

        # Dates
        for date_field in ['Start', 'Finish', 'BaselineStart', 'BaselineFinish']:
            elem = task_elem.find(date_field)
            task_data[date_field.lower()] = elem.text if elem is not None else None

        # Duration
        duration_elem = task_elem.find('Duration')
        if duration_elem is not None:
            task_data['duration'] = duration_elem.text

        # Milestone flag
        milestone_elem = task_elem.find('Milestone')
        task_data['is_milestone'] = milestone_elem.text == '1' if milestone_elem is not None else False

        # Summary flag
        summary_elem = task_elem.find('Summary')
        task_data['is_summary'] = summary_elem.text == '1' if summary_elem is not None else False

        tasks.append(task_data)

    return {
        'project_info': project_info,
        'tasks': tasks,
        'task_count': len(tasks)
    }


def compare_schedules(aop_data: dict, sprint_data: dict) -> dict:
    """Compare AOP and Sprint schedules."""

    # Build lookup by UID for matching
    aop_by_uid = {task['uid']: task for task in aop_data['tasks'] if task.get('uid')}
    sprint_by_uid = {task['uid']: task for task in sprint_data['tasks'] if task.get('uid')}

    # Find matching tasks
    common_uids = set(aop_by_uid.keys()) & set(sprint_by_uid.keys())
    aop_only_uids = set(aop_by_uid.keys()) - set(sprint_by_uid.keys())
    sprint_only_uids = set(sprint_by_uid.keys()) - set(aop_by_uid.keys())

    # Analyze date differences for common tasks
    date_differences = []
    for uid in common_uids:
        aop_task = aop_by_uid[uid]
        sprint_task = sprint_by_uid[uid]

        # Skip summary tasks
        if aop_task.get('is_summary') or sprint_task.get('is_summary'):
            continue

        diff_record = {
            'uid': uid,
            'name': aop_task.get('name'),
            'is_milestone': aop_task.get('is_milestone'),
            'aop_start': aop_task.get('start'),
            'sprint_start': sprint_task.get('start'),
            'aop_finish': aop_task.get('finish'),
            'sprint_finish': sprint_task.get('finish'),
        }

        # Calculate date differences if dates exist
        if aop_task.get('start') and sprint_task.get('start'):
            try:
                aop_start = datetime.fromisoformat(aop_task['start'].replace('Z', '+00:00'))
                sprint_start = datetime.fromisoformat(sprint_task['start'].replace('Z', '+00:00'))
                diff_record['start_diff_days'] = (sprint_start - aop_start).days
            except:
                diff_record['start_diff_days'] = None

        if aop_task.get('finish') and sprint_task.get('finish'):
            try:
                aop_finish = datetime.fromisoformat(aop_task['finish'].replace('Z', '+00:00'))
                sprint_finish = datetime.fromisoformat(sprint_task['finish'].replace('Z', '+00:00'))
                diff_record['finish_diff_days'] = (sprint_finish - aop_finish).days
            except:
                diff_record['finish_diff_days'] = None

        date_differences.append(diff_record)

    # Calculate statistics
    start_diffs = [d['start_diff_days'] for d in date_differences if d.get('start_diff_days') is not None]
    finish_diffs = [d['finish_diff_days'] for d in date_differences if d.get('finish_diff_days') is not None]

    earlier_starts = sum(1 for d in start_diffs if d < 0)
    later_starts = sum(1 for d in start_diffs if d > 0)
    same_starts = sum(1 for d in start_diffs if d == 0)

    earlier_finishes = sum(1 for d in finish_diffs if d < 0)
    later_finishes = sum(1 for d in finish_diffs if d > 0)
    same_finishes = sum(1 for d in finish_diffs if d == 0)

    return {
        'common_tasks': len(common_uids),
        'aop_only_tasks': len(aop_only_uids),
        'sprint_only_tasks': len(sprint_only_uids),
        'date_differences': date_differences,
        'statistics': {
            'tasks_compared': len(date_differences),
            'start_date_analysis': {
                'earlier_in_sprint': earlier_starts,
                'later_in_sprint': later_starts,
                'same_date': same_starts,
                'avg_diff_days': sum(start_diffs) / len(start_diffs) if start_diffs else 0
            },
            'finish_date_analysis': {
                'earlier_in_sprint': earlier_finishes,
                'later_in_sprint': later_finishes,
                'same_date': same_finishes,
                'avg_diff_days': sum(finish_diffs) / len(finish_diffs) if finish_diffs else 0
            }
        }
    }


def generate_markdown_report(aop_data: dict, sprint_data: dict, comparison: dict, output_path: str):
    """Generate markdown report of the gap analysis."""

    report_lines = [
        "# Sprint vs AOP Schedule Gap Analysis - Miraya",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Executive Summary",
        "",
        "This analysis compares the Sprint schedule against the AOP baseline schedule for the Miraya project.",
        "Sprint schedules are tighter than AOP baselines - teams receive bonuses for meeting Sprint targets.",
        "",
        "## Schedule Overview",
        "",
        "### AOP Baseline",
        f"- **Project Start:** {aop_data['project_info'].get('start_date', 'N/A')}",
        f"- **Project Finish:** {aop_data['project_info'].get('finish_date', 'N/A')}",
        f"- **Total Tasks:** {aop_data['task_count']}",
        "",
        "### Sprint Schedule",
        f"- **Project Start:** {sprint_data['project_info'].get('start_date', 'N/A')}",
        f"- **Project Finish:** {sprint_data['project_info'].get('finish_date', 'N/A')}",
        f"- **Total Tasks:** {sprint_data['task_count']}",
        "",
        "## Task Comparison",
        "",
        f"- **Tasks in Both Schedules:** {comparison['common_tasks']}",
        f"- **Tasks Only in AOP:** {comparison['aop_only_tasks']}",
        f"- **Tasks Only in Sprint:** {comparison['sprint_only_tasks']}",
        f"- **Tasks Analyzed (leaf tasks):** {comparison['statistics']['tasks_compared']}",
        "",
        "## Date Analysis",
        "",
        "### Start Date Comparison",
        "",
        f"- **Earlier in Sprint:** {comparison['statistics']['start_date_analysis']['earlier_in_sprint']} tasks",
        f"- **Later in Sprint:** {comparison['statistics']['start_date_analysis']['later_in_sprint']} tasks",
        f"- **Same Date:** {comparison['statistics']['start_date_analysis']['same_date']} tasks",
        f"- **Average Difference:** {comparison['statistics']['start_date_analysis']['avg_diff_days']:.1f} days",
        "",
        "**Interpretation:** Negative = Sprint earlier than AOP, Positive = Sprint later than AOP",
        "",
        "### Finish Date Comparison",
        "",
        f"- **Earlier in Sprint:** {comparison['statistics']['finish_date_analysis']['earlier_in_sprint']} tasks",
        f"- **Later in Sprint:** {comparison['statistics']['finish_date_analysis']['later_in_sprint']} tasks",
        f"- **Same Date:** {comparison['statistics']['finish_date_analysis']['same_date']} tasks",
        f"- **Average Difference:** {comparison['statistics']['finish_date_analysis']['avg_diff_days']:.1f} days",
        "",
        "## Top Tasks with Significant Differences",
        "",
        "### Tasks Finishing Earlier in Sprint (Top 10)",
        "",
    ]

    # Sort by finish date difference
    sorted_by_finish = sorted(
        [d for d in comparison['date_differences'] if d.get('finish_diff_days') is not None],
        key=lambda x: x['finish_diff_days']
    )

    report_lines.append("| UID | Task Name | AOP Finish | Sprint Finish | Days Earlier |")
    report_lines.append("|-----|-----------|------------|---------------|--------------|")

    for task in sorted_by_finish[:10]:
        if task['finish_diff_days'] < 0:
            report_lines.append(
                f"| {task['uid']} | {task['name'][:50]} | {task['aop_finish'][:10]} | "
                f"{task['sprint_finish'][:10]} | {abs(task['finish_diff_days'])} |"
            )

    report_lines.extend([
        "",
        "### Tasks Finishing Later in Sprint (Top 10)",
        "",
        "| UID | Task Name | AOP Finish | Sprint Finish | Days Later |",
        "|-----|-----------|------------|---------------|------------|",
    ])

    for task in sorted_by_finish[-10:]:
        if task['finish_diff_days'] > 0:
            report_lines.append(
                f"| {task['uid']} | {task['name'][:50]} | {task['aop_finish'][:10]} | "
                f"{task['sprint_finish'][:10]} | {task['finish_diff_days']} |"
            )

    report_lines.extend([
        "",
        "## Key Findings",
        "",
        f"1. **Schedule Compression:** Sprint schedule shows {'earlier' if comparison['statistics']['finish_date_analysis']['avg_diff_days'] < 0 else 'later'} completion dates on average",
        f"2. **Task Coverage:** {comparison['common_tasks']/max(aop_data['task_count'], sprint_data['task_count'], 1)*100:.1f}% of tasks are common between schedules",
        "3. **Aspiration Target:** Sprint represents the incentivized target for team bonuses",
        "",
        "## Recommendations for ETL Integration",
        "",
        "1. **Add Sprint Schedule Layer:** Process sprint XMLs alongside AOP baselines",
        "2. **Track Schedule Type:** Add `schedule_type` field ('aop' vs 'sprint') to differentiate",
        "3. **Calculate Variance:** Store delta between AOP and Sprint dates as `sprint_variance_days`",
        "4. **Dashboard Display:** Show both schedules with variance indicators for bonus tracking",
        "5. **Data Structure:** Consider nested structure or separate sprint_dates object within tasks",
        ""
    ])

    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f"Report generated: {output_path}")


def main():
    # Paths
    aop_path = "input/all-aop-baselines/Miraya.xml"
    sprint_path = "input/all-sprint-schedules/Miraya.xml"
    output_path = "test/sprint_vs_aop_gap_analysis.md"

    print("Parsing AOP baseline...")
    aop_data = parse_xml_schedule(aop_path)

    print("Parsing Sprint schedule...")
    sprint_data = parse_xml_schedule(sprint_path)

    print("Comparing schedules...")
    comparison = compare_schedules(aop_data, sprint_data)

    print("Generating report...")
    generate_markdown_report(aop_data, sprint_data, comparison, output_path)

    print("Done!")


if __name__ == "__main__":
    main()
