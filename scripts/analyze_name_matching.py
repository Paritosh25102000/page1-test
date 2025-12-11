"""
Analyze name-based fuzzy matching between AOP and Sprint schedules.

Since UID matching completely fails (0% exact matches), test alternative
matching strategies based on task name similarity.
"""

import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from collections import defaultdict


def parse_tasks_for_matching(xml_path: str) -> list:
    """Parse XML and extract tasks with key matching fields."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {'ms': 'http://schemas.microsoft.com/project'}

    tasks = []

    for task_elem in root.findall('.//ms:Task', ns):
        uid_elem = task_elem.find('ms:UID', ns)
        name_elem = task_elem.find('ms:Name', ns)
        wbs_elem = task_elem.find('ms:WBS', ns)
        summary_elem = task_elem.find('ms:Summary', ns)
        start_elem = task_elem.find('ms:Start', ns)
        finish_elem = task_elem.find('ms:Finish', ns)

        if uid_elem is None or name_elem is None:
            continue

        task = {
            'uid': uid_elem.text,
            'name': name_elem.text,
            'wbs': wbs_elem.text if wbs_elem is not None else None,
            'is_summary': summary_elem.text == '1' if summary_elem is not None else False,
            'start': start_elem.text if start_elem is not None else None,
            'finish': finish_elem.text if finish_elem is not None else None,
        }

        tasks.append(task)

    return tasks


def name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity ratio between two task names (0.0 to 1.0)."""
    if not name1 or not name2:
        return 0.0
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()


def find_best_matches(aop_tasks: list, sprint_tasks: list, threshold: float = 0.8) -> dict:
    """
    Find best name-based matches between AOP and Sprint tasks.

    Args:
        aop_tasks: List of AOP tasks
        sprint_tasks: List of Sprint tasks
        threshold: Minimum similarity ratio (0.0 to 1.0)

    Returns:
        Dictionary with matching statistics
    """
    print(f"Matching with threshold: {threshold:.1%}")

    # Index sprint tasks by name for faster lookup
    sprint_by_name = {t['name']: t for t in sprint_tasks}

    exact_name_matches = []
    fuzzy_matches = []
    no_matches = []

    # For each AOP task, find best Sprint match
    for aop_task in aop_tasks:
        # Skip summary tasks
        if aop_task['is_summary']:
            continue

        aop_name = aop_task['name']

        # First try exact name match
        if aop_name in sprint_by_name:
            sprint_task = sprint_by_name[aop_name]
            exact_name_matches.append({
                'aop_uid': aop_task['uid'],
                'sprint_uid': sprint_task['uid'],
                'name': aop_name,
                'aop_wbs': aop_task['wbs'],
                'sprint_wbs': sprint_task['wbs'],
                'wbs_match': aop_task['wbs'] == sprint_task['wbs'],
                'similarity': 1.0,
                'aop_finish': aop_task['finish'],
                'sprint_finish': sprint_task['finish'],
            })
            continue

        # Otherwise, find best fuzzy match
        best_match = None
        best_similarity = 0.0

        for sprint_task in sprint_tasks:
            if sprint_task['is_summary']:
                continue

            similarity = name_similarity(aop_name, sprint_task['name'])
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = sprint_task

        if best_similarity >= threshold and best_match:
            fuzzy_matches.append({
                'aop_uid': aop_task['uid'],
                'sprint_uid': best_match['uid'],
                'aop_name': aop_name,
                'sprint_name': best_match['name'],
                'aop_wbs': aop_task['wbs'],
                'sprint_wbs': best_match['wbs'],
                'wbs_match': aop_task['wbs'] == best_match['wbs'],
                'similarity': best_similarity,
                'aop_finish': aop_task['finish'],
                'sprint_finish': best_match['finish'],
            })
        else:
            no_matches.append({
                'uid': aop_task['uid'],
                'name': aop_name,
                'wbs': aop_task['wbs'],
                'best_similarity': best_similarity,
                'best_match_name': best_match['name'] if best_match else None,
            })

    return {
        'exact_name_matches': exact_name_matches,
        'fuzzy_matches': fuzzy_matches,
        'no_matches': no_matches,
        'total_matched': len(exact_name_matches) + len(fuzzy_matches),
        'total_aop_leaf_tasks': len([t for t in aop_tasks if not t['is_summary']]),
    }


def generate_report(results: dict, output_path: str):
    """Generate markdown report of name-based matching analysis."""

    exact = len(results['exact_name_matches'])
    fuzzy = len(results['fuzzy_matches'])
    unmatched = len(results['no_matches'])
    total = results['total_aop_leaf_tasks']
    matched = results['total_matched']

    lines = [
        "# Name-Based Task Matching Analysis - Miraya",
        "",
        "## Overview",
        "",
        f"- **Total AOP Leaf Tasks:** {total}",
        f"- **Successfully Matched:** {matched} ({matched/total*100:.1f}%)",
        f"  - Exact name matches: {exact} ({exact/total*100:.1f}%)",
        f"  - Fuzzy matches: {fuzzy} ({fuzzy/total*100:.1f}%)",
        f"- **Unmatched:** {unmatched} ({unmatched/total*100:.1f}%)",
        "",
        "## Matching Quality",
        "",
    ]

    # Analyze WBS consistency for matches
    if results['exact_name_matches']:
        wbs_matches = sum(1 for m in results['exact_name_matches'] if m['wbs_match'])
        lines.append(f"**Exact Name Matches ({exact} tasks):**")
        lines.append(f"- WBS also matches: {wbs_matches} ({wbs_matches/exact*100:.1f}%)")
        lines.append(f"- WBS differs: {exact - wbs_matches} ({(exact-wbs_matches)/exact*100:.1f}%)")
        lines.append("")

    if results['fuzzy_matches']:
        wbs_matches_fuzzy = sum(1 for m in results['fuzzy_matches'] if m['wbs_match'])
        avg_similarity = sum(m['similarity'] for m in results['fuzzy_matches']) / len(results['fuzzy_matches'])
        lines.append(f"**Fuzzy Matches ({fuzzy} tasks):**")
        lines.append(f"- Average name similarity: {avg_similarity:.1%}")
        lines.append(f"- WBS also matches: {wbs_matches_fuzzy} ({wbs_matches_fuzzy/fuzzy*100:.1f}%)")
        lines.append("")

    # Sample exact matches
    if results['exact_name_matches']:
        lines.extend([
            "## Sample Exact Name Matches",
            "",
            "| Name | AOP UID | Sprint UID | WBS Match | AOP Finish | Sprint Finish |",
            "|------|---------|------------|-----------|------------|---------------|",
        ])
        for match in results['exact_name_matches'][:15]:
            wbs_icon = "✓" if match['wbs_match'] else "✗"
            lines.append(
                f"| {match['name'][:40]} | {match['aop_uid']} | {match['sprint_uid']} | "
                f"{wbs_icon} | {match['aop_finish'][:10] if match['aop_finish'] else 'N/A'} | "
                f"{match['sprint_finish'][:10] if match['sprint_finish'] else 'N/A'} |"
            )
        lines.append("")

    # Sample fuzzy matches
    if results['fuzzy_matches']:
        lines.extend([
            "## Sample Fuzzy Matches",
            "",
            "| AOP Name | Sprint Name | Similarity | AOP Finish | Sprint Finish |",
            "|----------|-------------|------------|------------|---------------|",
        ])
        for match in sorted(results['fuzzy_matches'], key=lambda x: x['similarity'], reverse=True)[:15]:
            lines.append(
                f"| {match['aop_name'][:35]} | {match['sprint_name'][:35]} | "
                f"{match['similarity']:.1%} | "
                f"{match['aop_finish'][:10] if match['aop_finish'] else 'N/A'} | "
                f"{match['sprint_finish'][:10] if match['sprint_finish'] else 'N/A'} |"
            )
        lines.append("")

    # Sample unmatched
    if results['no_matches']:
        lines.extend([
            "## Sample Unmatched Tasks",
            "",
            "| AOP Name | Best Match Found | Similarity |",
            "|----------|------------------|------------|",
        ])
        for task in results['no_matches'][:15]:
            lines.append(
                f"| {task['name'][:45]} | {task['best_match_name'][:40] if task['best_match_name'] else 'N/A'} | "
                f"{task['best_similarity']:.1%} |"
            )
        lines.append("")

    lines.extend([
        "## Conclusion",
        "",
        f"**Name-based matching achieves {matched/total*100:.1f}% match rate**",
        "",
    ])

    if matched / total >= 0.8:
        lines.append("✅ **RECOMMENDED:** Name-based fuzzy matching is viable for Sprint enrichment.")
        lines.append("")
        lines.append(f"Expected result: {matched} out of {total} tasks will get Sprint dates populated.")
    elif matched / total >= 0.6:
        lines.append("⚠️ **MODERATE:** Name-based matching provides decent coverage but ~40% will remain unmatched.")
    else:
        lines.append("❌ **NOT RECOMMENDED:** Name-based matching has low coverage.")

    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"\nReport generated: {output_path}")
    print(f"\nSummary:")
    print(f"  Match rate: {matched/total*100:.1f}% ({matched}/{total})")
    print(f"  Exact: {exact}, Fuzzy: {fuzzy}, Unmatched: {unmatched}")


def main():
    aop_path = "input/all-aop-baselines/Miraya.xml"
    sprint_path = "input/all-sprint-schedules/Miraya.xml"
    output_path = "test/name_matching_analysis.md"

    print("Parsing AOP baseline...")
    aop_tasks = parse_tasks_for_matching(aop_path)
    print(f"  Loaded {len(aop_tasks)} tasks")

    print("Parsing Sprint schedule...")
    sprint_tasks = parse_tasks_for_matching(sprint_path)
    print(f"  Loaded {len(sprint_tasks)} tasks")

    print("\nFinding best matches...")
    results = find_best_matches(aop_tasks, sprint_tasks, threshold=0.85)

    print("Generating report...")
    generate_report(results, output_path)

    print("Done!")


if __name__ == "__main__":
    main()
