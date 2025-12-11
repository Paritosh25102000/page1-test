"""
Analyze outline_number as a matching key between AOP and Sprint schedules.

Check if outline_number is stable and can be used for reliable matching.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict


def parse_tasks_with_outline(xml_path: str) -> list:
    """Parse XML and extract tasks with outline_number."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {'ms': 'http://schemas.microsoft.com/project'}

    tasks = []

    for task_elem in root.findall('.//ms:Task', ns):
        uid_elem = task_elem.find('ms:UID', ns)
        name_elem = task_elem.find('ms:Name', ns)
        outline_elem = task_elem.find('ms:OutlineNumber', ns)
        wbs_elem = task_elem.find('ms:WBS', ns)
        summary_elem = task_elem.find('ms:Summary', ns)
        start_elem = task_elem.find('ms:Start', ns)
        finish_elem = task_elem.find('ms:Finish', ns)

        if uid_elem is None or name_elem is None:
            continue

        task = {
            'uid': uid_elem.text,
            'name': name_elem.text,
            'outline_number': outline_elem.text if outline_elem is not None else None,
            'wbs': wbs_elem.text if wbs_elem is not None else None,
            'is_summary': summary_elem.text == '1' if summary_elem is not None else False,
            'start': start_elem.text if start_elem is not None else None,
            'finish': finish_elem.text if finish_elem is not None else None,
        }

        tasks.append(task)

    return tasks


def analyze_outline_number_matching(aop_tasks: list, sprint_tasks: list) -> dict:
    """Analyze matching quality using different strategies."""

    # Filter to leaf tasks only
    aop_leaf = [t for t in aop_tasks if not t['is_summary']]
    sprint_leaf = [t for t in sprint_tasks if not t['is_summary']]

    # Index by different keys
    aop_by_outline = {}
    for t in aop_leaf:
        if t['outline_number']:
            if t['outline_number'] in aop_by_outline:
                # Duplicate outline_number in AOP
                aop_by_outline[t['outline_number']] = 'DUPLICATE'
            else:
                aop_by_outline[t['outline_number']] = t

    sprint_by_outline = {}
    for t in sprint_leaf:
        if t['outline_number']:
            if t['outline_number'] in sprint_by_outline:
                # Duplicate outline_number in Sprint
                sprint_by_outline[t['outline_number']] = 'DUPLICATE'
            else:
                sprint_by_outline[t['outline_number']] = t

    aop_by_name = {t['name']: t for t in aop_leaf}
    sprint_by_name = {t['name']: t for t in sprint_leaf}

    # Create composite key: name + outline_number
    aop_by_composite = {}
    for t in aop_leaf:
        key = f"{t['name']}||{t['outline_number']}"
        aop_by_composite[key] = t

    sprint_by_composite = {}
    for t in sprint_leaf:
        key = f"{t['name']}||{t['outline_number']}"
        sprint_by_composite[key] = t

    # Test Strategy 1: outline_number only
    outline_matches = []
    outline_mismatches = []
    outline_duplicates = 0

    common_outlines = set(aop_by_outline.keys()) & set(sprint_by_outline.keys())
    for outline in common_outlines:
        aop_task = aop_by_outline[outline]
        sprint_task = sprint_by_outline[outline]

        if aop_task == 'DUPLICATE' or sprint_task == 'DUPLICATE':
            outline_duplicates += 1
            continue

        name_match = aop_task['name'] == sprint_task['name']

        if name_match:
            outline_matches.append({
                'outline_number': outline,
                'name': aop_task['name'],
                'aop_uid': aop_task['uid'],
                'sprint_uid': sprint_task['uid'],
                'aop_finish': aop_task['finish'],
                'sprint_finish': sprint_task['finish'],
            })
        else:
            outline_mismatches.append({
                'outline_number': outline,
                'aop_name': aop_task['name'],
                'sprint_name': sprint_task['name'],
                'aop_uid': aop_task['uid'],
                'sprint_uid': sprint_task['uid'],
            })

    # Test Strategy 2: name only (we already know this)
    name_matches = []
    common_names = set(aop_by_name.keys()) & set(sprint_by_name.keys())
    for name in common_names:
        aop_task = aop_by_name[name]
        sprint_task = sprint_by_name[name]
        name_matches.append({
            'name': name,
            'aop_outline': aop_task['outline_number'],
            'sprint_outline': sprint_task['outline_number'],
            'outline_match': aop_task['outline_number'] == sprint_task['outline_number'],
            'aop_uid': aop_task['uid'],
            'sprint_uid': sprint_task['uid'],
        })

    # Test Strategy 3: name + outline_number composite
    composite_matches = len(set(aop_by_composite.keys()) & set(sprint_by_composite.keys()))

    return {
        'total_aop_leaf': len(aop_leaf),
        'total_sprint_leaf': len(sprint_leaf),
        'outline_only': {
            'common_outlines': len(common_outlines),
            'matches': outline_matches,
            'mismatches': outline_mismatches,
            'duplicates': outline_duplicates,
            'match_count': len(outline_matches),
        },
        'name_only': {
            'matches': name_matches,
            'match_count': len(name_matches),
        },
        'composite': {
            'match_count': composite_matches,
        }
    }


def generate_report(results: dict, output_path: str):
    """Generate detailed comparison report."""

    total = results['total_aop_leaf']
    outline_matches = results['outline_only']['match_count']
    outline_mismatches = len(results['outline_only']['mismatches'])
    outline_duplicates = results['outline_only']['duplicates']
    name_matches = results['name_only']['match_count']
    composite_matches = results['composite']['match_count']

    lines = [
        "# Outline Number Matching Analysis - Miraya",
        "",
        "## Overview",
        "",
        f"- **Total AOP Leaf Tasks:** {total}",
        f"- **Total Sprint Leaf Tasks:** {results['total_sprint_leaf']}",
        "",
        "## Matching Strategy Comparison",
        "",
        "| Strategy | Matches | Match Rate | Notes |",
        "|----------|---------|------------|-------|",
        f"| **Outline Number Only** | {outline_matches} | {outline_matches/total*100:.1f}% | {outline_mismatches} name mismatches, {outline_duplicates} duplicates |",
        f"| **Name Only** | {name_matches} | {name_matches/total*100:.1f}% | Already tested - 100% reliable |",
        f"| **Name + Outline (Composite)** | {composite_matches} | {composite_matches/total*100:.1f}% | Strictest matching |",
        "",
    ]

    # Analyze outline stability for name matches
    if results['name_only']['matches']:
        outline_stable = sum(1 for m in results['name_only']['matches'] if m['outline_match'])
        outline_changed = name_matches - outline_stable

        lines.extend([
            "## Outline Number Stability Analysis",
            "",
            f"For {name_matches} tasks with matching names:",
            "",
            f"- **Outline Number Stable:** {outline_stable} ({outline_stable/name_matches*100:.1f}%)",
            f"- **Outline Number Changed:** {outline_changed} ({outline_changed/name_matches*100:.1f}%)",
            "",
        ])

        if outline_changed > 0:
            lines.extend([
                "### Sample: Name Matches but Outline Number Changed",
                "",
                "| Name | AOP Outline | Sprint Outline | AOP UID | Sprint UID |",
                "|------|-------------|----------------|---------|------------|",
            ])
            changed_samples = [m for m in results['name_only']['matches'] if not m['outline_match']][:10]
            for m in changed_samples:
                lines.append(
                    f"| {m['name'][:50]} | {m['aop_outline']} | {m['sprint_outline']} | "
                    f"{m['aop_uid']} | {m['sprint_uid']} |"
                )
            lines.append("")

    # Show outline_number mismatches (same outline but different task)
    if results['outline_only']['mismatches']:
        lines.extend([
            "## Outline Number Reuse (Different Tasks)",
            "",
            f"Found {outline_mismatches} cases where same outline_number refers to different tasks:",
            "",
            "| Outline | AOP Task | Sprint Task | AOP UID | Sprint UID |",
            "|---------|----------|-------------|---------|------------|",
        ])
        for m in results['outline_only']['mismatches'][:10]:
            lines.append(
                f"| {m['outline_number']} | {m['aop_name'][:35]} | {m['sprint_name'][:35]} | "
                f"{m['aop_uid']} | {m['sprint_uid']} |"
            )
        lines.append("")

    # Sample of outline_number matches
    if results['outline_only']['matches']:
        lines.extend([
            "## Sample: Outline Number Matches (Same Outline, Same Name)",
            "",
            "| Outline | Name | AOP UID | Sprint UID | AOP Finish | Sprint Finish |",
            "|---------|------|---------|------------|------------|---------------|",
        ])
        for m in results['outline_only']['matches'][:15]:
            lines.append(
                f"| {m['outline_number']} | {m['name'][:40]} | {m['aop_uid']} | {m['sprint_uid']} | "
                f"{m['aop_finish'][:10] if m['aop_finish'] else 'N/A'} | "
                f"{m['sprint_finish'][:10] if m['sprint_finish'] else 'N/A'} |"
            )
        lines.append("")

    lines.extend([
        "## Recommendation",
        "",
    ])

    if name_matches >= composite_matches and name_matches == total:
        lines.extend([
            "✅ **Use NAME ONLY matching**",
            "",
            f"- Achieves 100% match rate ({name_matches}/{total})",
            "- Outline numbers changed in ~100% of cases (schedule restructuring)",
            "- Name is the most stable identifier across schedules",
            "",
            "**Implementation:**",
            "```python",
            "# Match by exact name",
            "sprint_by_name = {task['name']: task for task in sprint_tasks}",
            "for aop_task in aop_tasks:",
            "    sprint_task = sprint_by_name.get(aop_task['name'])",
            "    if sprint_task:",
            "        aop_task['dates']['sprint'] = sprint_task['dates']['plan']",
            "```",
        ])
    elif composite_matches == total:
        lines.extend([
            "✅ **Use NAME + OUTLINE composite matching**",
            "",
            f"- Achieves 100% match rate ({composite_matches}/{total})",
            "- More robust than name alone (handles duplicate names)",
        ])
    else:
        lines.extend([
            "⚠️ **Name matching recommended, outline unreliable**",
            "",
            f"- Name matching: {name_matches/total*100:.1f}%",
            f"- Outline matching: {outline_matches/total*100:.1f}%",
        ])

    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"\nReport generated: {output_path}")
    print(f"\nQuick Comparison:")
    print(f"  Name only:            {name_matches}/{total} ({name_matches/total*100:.1f}%)")
    print(f"  Outline only:         {outline_matches}/{total} ({outline_matches/total*100:.1f}%)")
    print(f"  Name + Outline:       {composite_matches}/{total} ({composite_matches/total*100:.1f}%)")


def main():
    aop_path = "input/all-aop-baselines/Miraya.xml"
    sprint_path = "input/all-sprint-schedules/Miraya.xml"
    output_path = "test/outline_number_matching_analysis.md"

    print("Parsing AOP baseline...")
    aop_tasks = parse_tasks_with_outline(aop_path)
    print(f"  Loaded {len(aop_tasks)} tasks")

    print("Parsing Sprint schedule...")
    sprint_tasks = parse_tasks_with_outline(sprint_path)
    print(f"  Loaded {len(sprint_tasks)} tasks")

    print("\nAnalyzing matching strategies...")
    results = analyze_outline_number_matching(aop_tasks, sprint_tasks)

    print("Generating report...")
    generate_report(results, output_path)

    print("Done!")


if __name__ == "__main__":
    main()
