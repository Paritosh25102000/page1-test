"""
Analyze UID-based matching between AOP and Sprint schedules.

Check if tasks with matching UIDs actually represent the same work
(same name, WBS, structure) or if UIDs got reused for different tasks.
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


def parse_tasks_by_uid(xml_path: str) -> dict:
    """Parse XML and extract tasks indexed by UID."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {'ms': 'http://schemas.microsoft.com/project'}

    tasks_by_uid = {}

    for task_elem in root.findall('.//ms:Task', ns):
        # Extract UID
        uid_elem = task_elem.find('ms:UID', ns)
        if uid_elem is None or not uid_elem.text:
            continue

        uid = uid_elem.text

        # Extract key fields for comparison
        task_data = {
            'uid': uid,
            'name': None,
            'wbs': None,
            'outline_level': None,
            'outline_number': None,
            'is_summary': False,
            'is_milestone': False,
            'start': None,
            'finish': None,
        }

        # Name
        name_elem = task_elem.find('ms:Name', ns)
        if name_elem is not None:
            task_data['name'] = name_elem.text

        # WBS
        wbs_elem = task_elem.find('ms:WBS', ns)
        if wbs_elem is not None:
            task_data['wbs'] = wbs_elem.text

        # Outline Level
        ol_elem = task_elem.find('ms:OutlineLevel', ns)
        if ol_elem is not None:
            task_data['outline_level'] = ol_elem.text

        # Outline Number
        on_elem = task_elem.find('ms:OutlineNumber', ns)
        if on_elem is not None:
            task_data['outline_number'] = on_elem.text

        # Summary flag
        summary_elem = task_elem.find('ms:Summary', ns)
        task_data['is_summary'] = summary_elem.text == '1' if summary_elem is not None else False

        # Milestone flag
        milestone_elem = task_elem.find('ms:Milestone', ns)
        task_data['is_milestone'] = milestone_elem.text == '1' if milestone_elem is not None else False

        # Dates
        start_elem = task_elem.find('ms:Start', ns)
        if start_elem is not None:
            task_data['start'] = start_elem.text

        finish_elem = task_elem.find('ms:Finish', ns)
        if finish_elem is not None:
            task_data['finish'] = finish_elem.text

        tasks_by_uid[uid] = task_data

    return tasks_by_uid


def compare_tasks_by_uid(aop_tasks: dict, sprint_tasks: dict) -> dict:
    """Compare tasks with matching UIDs."""

    common_uids = set(aop_tasks.keys()) & set(sprint_tasks.keys())
    aop_only_uids = set(aop_tasks.keys()) - set(sprint_tasks.keys())
    sprint_only_uids = set(sprint_tasks.keys()) - set(aop_tasks.keys())

    # Analyze matching UIDs
    exact_matches = []  # Same UID, same name, same WBS
    name_mismatches = []  # Same UID, different name
    wbs_mismatches = []  # Same UID, different WBS
    both_mismatches = []  # Same UID, different name AND WBS

    for uid in common_uids:
        aop_task = aop_tasks[uid]
        sprint_task = sprint_tasks[uid]

        name_match = aop_task['name'] == sprint_task['name']
        wbs_match = aop_task['wbs'] == sprint_task['wbs']

        if name_match and wbs_match:
            exact_matches.append({
                'uid': uid,
                'name': aop_task['name'],
                'wbs': aop_task['wbs'],
                'aop_start': aop_task['start'],
                'sprint_start': sprint_task['start'],
                'aop_finish': aop_task['finish'],
                'sprint_finish': sprint_task['finish'],
            })
        elif not name_match and not wbs_match:
            both_mismatches.append({
                'uid': uid,
                'aop_name': aop_task['name'],
                'sprint_name': sprint_task['name'],
                'aop_wbs': aop_task['wbs'],
                'sprint_wbs': sprint_task['wbs'],
            })
        elif not name_match:
            name_mismatches.append({
                'uid': uid,
                'aop_name': aop_task['name'],
                'sprint_name': sprint_task['name'],
                'wbs': aop_task['wbs'],
            })
        elif not wbs_match:
            wbs_mismatches.append({
                'uid': uid,
                'name': aop_task['name'],
                'aop_wbs': aop_task['wbs'],
                'sprint_wbs': sprint_task['wbs'],
            })

    return {
        'total_aop_tasks': len(aop_tasks),
        'total_sprint_tasks': len(sprint_tasks),
        'common_uids': len(common_uids),
        'aop_only_uids': len(aop_only_uids),
        'sprint_only_uids': len(sprint_only_uids),
        'exact_matches': exact_matches,
        'name_mismatches': name_mismatches,
        'wbs_mismatches': wbs_mismatches,
        'both_mismatches': both_mismatches,
    }


def generate_report(comparison: dict, output_path: str):
    """Generate detailed markdown report."""

    total_common = comparison['common_uids']
    exact = len(comparison['exact_matches'])
    name_only = len(comparison['name_mismatches'])
    wbs_only = len(comparison['wbs_mismatches'])
    both = len(comparison['both_mismatches'])

    lines = [
        "# UID-Based Task Matching Analysis - Miraya",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Overview",
        "",
        f"- **Total AOP Tasks:** {comparison['total_aop_tasks']}",
        f"- **Total Sprint Tasks:** {comparison['total_sprint_tasks']}",
        f"- **Common UIDs:** {total_common} ({total_common/comparison['total_aop_tasks']*100:.1f}%)",
        f"- **AOP-Only UIDs:** {comparison['aop_only_uids']}",
        f"- **Sprint-Only UIDs:** {comparison['sprint_only_uids']}",
        "",
        "## Matching Quality for Common UIDs",
        "",
        f"Out of {total_common} tasks with matching UIDs:",
        "",
        f"- **Exact Matches** (same name, same WBS): {exact} ({exact/total_common*100:.1f}%)",
        f"- **Name Mismatch Only**: {name_only} ({name_only/total_common*100:.1f}%)",
        f"- **WBS Mismatch Only**: {wbs_only} ({wbs_only/total_common*100:.1f}%)",
        f"- **Both Name & WBS Mismatch**: {both} ({both/total_common*100:.1f}%)",
        "",
    ]

    # Show samples of each category
    if comparison['both_mismatches']:
        lines.extend([
            "## Sample: Same UID, Different Task (Name & WBS Mismatch)",
            "",
            "These are cases where the UID was reused for completely different work:",
            "",
            "| UID | AOP Name | Sprint Name | AOP WBS | Sprint WBS |",
            "|-----|----------|-------------|---------|------------|",
        ])
        for task in comparison['both_mismatches'][:10]:
            lines.append(
                f"| {task['uid']} | {task['aop_name'][:40]} | {task['sprint_name'][:40]} | "
                f"{task['aop_wbs']} | {task['sprint_wbs']} |"
            )
        lines.append("")

    if comparison['name_mismatches']:
        lines.extend([
            "## Sample: Same UID & WBS, Different Name",
            "",
            "These might be minor name changes or renamed tasks:",
            "",
            "| UID | AOP Name | Sprint Name | WBS |",
            "|-----|----------|-------------|-----|",
        ])
        for task in comparison['name_mismatches'][:10]:
            lines.append(
                f"| {task['uid']} | {task['aop_name'][:40]} | {task['sprint_name'][:40]} | "
                f"{task['wbs']} |"
            )
        lines.append("")

    if comparison['wbs_mismatches']:
        lines.extend([
            "## Sample: Same UID & Name, Different WBS",
            "",
            "These are tasks that were restructured in the WBS:",
            "",
            "| UID | Name | AOP WBS | Sprint WBS |",
            "|-----|------|---------|------------|",
        ])
        for task in comparison['wbs_mismatches'][:10]:
            lines.append(
                f"| {task['uid']} | {task['name'][:40]} | {task['aop_wbs']} | "
                f"{task['sprint_wbs']} |"
            )
        lines.append("")

    # Sample of exact matches
    if comparison['exact_matches']:
        lines.extend([
            "## Sample: Exact Matches (Good for Sprint Enrichment)",
            "",
            "These tasks have matching UID, name, and WBS - safe to enrich with Sprint dates:",
            "",
            "| UID | Name | WBS | AOP Finish | Sprint Finish |",
            "|-----|------|-----|------------|---------------|",
        ])
        for task in comparison['exact_matches'][:10]:
            lines.append(
                f"| {task['uid']} | {task['name'][:40]} | {task['wbs']} | "
                f"{task['aop_finish'][:10] if task['aop_finish'] else 'N/A'} | "
                f"{task['sprint_finish'][:10] if task['sprint_finish'] else 'N/A'} |"
            )
        lines.append("")

    lines.extend([
        "## Conclusion",
        "",
        f"**UID Matching Quality:** {exact}/{total_common} tasks ({exact/total_common*100:.1f}%) are exact matches",
        "",
        "### Implications for Sprint Enrichment:",
        "",
    ])

    if exact / total_common >= 0.9:
        lines.append("✅ **HIGH QUALITY** - UIDs reliably represent the same work. Safe to use UID-based matching.")
    elif exact / total_common >= 0.7:
        lines.append("⚠️ **MODERATE QUALITY** - Most UIDs match, but ~30% are mismatched. Consider validation.")
    else:
        lines.append("❌ **LOW QUALITY** - UIDs were heavily reused. UID-based matching is unreliable.")
        lines.append("")
        lines.append("**Recommendation:** Need alternative matching strategy (e.g., name + WBS similarity)")

    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Report generated: {output_path}")
    print(f"\nQuick Summary:")
    print(f"  Common UIDs: {total_common}")
    print(f"  Exact matches: {exact} ({exact/total_common*100:.1f}%)")
    print(f"  Mismatches: {name_only + wbs_only + both} ({(name_only + wbs_only + both)/total_common*100:.1f}%)")


def main():
    # Paths
    aop_path = "input/all-aop-baselines/Miraya.xml"
    sprint_path = "input/all-sprint-schedules/Miraya.xml"
    output_path = "test/uid_matching_analysis.md"

    print("Parsing AOP baseline by UID...")
    aop_tasks = parse_tasks_by_uid(aop_path)

    print("Parsing Sprint schedule by UID...")
    sprint_tasks = parse_tasks_by_uid(sprint_path)

    print("Comparing tasks...")
    comparison = compare_tasks_by_uid(aop_tasks, sprint_tasks)

    print("Generating report...")
    generate_report(comparison, output_path)

    print("Done!")


if __name__ == "__main__":
    main()
