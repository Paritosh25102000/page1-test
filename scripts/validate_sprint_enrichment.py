"""
Validate Sprint enrichment by checking 100 random tasks.

This script:
1. Samples 100 random tasks from the enriched JSON
2. Validates that Sprint dates were populated correctly
3. Compares Sprint vs AOP dates
4. Analyzes unmatched tasks
"""

import json
import random
from datetime import datetime
from collections import defaultdict


def parse_date(date_str):
    """Parse ISO date string to date object for comparison."""
    if not date_str:
        return None
    return datetime.fromisoformat(date_str).date()


def validate_enriched_json(json_path: str, sample_size: int = 100):
    """Validate Sprint enrichment quality."""

    print("Loading enriched JSON...")
    with open(json_path, 'r') as f:
        tasks = json.load(f)

    print(f"Total tasks: {len(tasks)}")

    # Filter to leaf tasks only (exclude summary tasks)
    leaf_tasks = [t for t in tasks if not t.get('is_summary', False)]
    print(f"Leaf tasks: {len(leaf_tasks)}")

    # Sample random tasks
    sample_size = min(sample_size, len(leaf_tasks))
    sample = random.sample(leaf_tasks, sample_size)

    # Analyze enrichment
    with_sprint = 0
    without_sprint = 0
    sprint_earlier = 0
    sprint_later = 0
    sprint_same = 0
    date_issues = []

    for task in sample:
        dates = task.get('dates', {})
        sprint_dates = dates.get('sprint')
        plan_dates = dates.get('plan')

        if sprint_dates:
            with_sprint += 1

            # Validate Sprint dates structure
            if not all(k in sprint_dates for k in ['start', 'finish', 'duration_days']):
                date_issues.append({
                    'uid': task.get('uid'),
                    'name': task.get('name'),
                    'issue': 'incomplete_sprint_dates',
                    'sprint_dates': sprint_dates
                })
                continue

            # Compare Sprint vs AOP finish dates
            plan_finish_str = plan_dates.get('finish') if plan_dates else None
            sprint_finish_str = sprint_dates.get('finish')

            if sprint_finish_str and plan_finish_str:
                sprint_finish = parse_date(sprint_finish_str)
                plan_finish = parse_date(plan_finish_str)

                if sprint_finish and plan_finish:
                    if sprint_finish < plan_finish:
                        sprint_earlier += 1
                    elif sprint_finish > plan_finish:
                        sprint_later += 1
                    else:
                        sprint_same += 1
        else:
            without_sprint += 1

    # Print results
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS (100 Random Tasks)")
    print("=" * 60)

    print(f"\nEnrichment Coverage:")
    print(f"  With Sprint dates:    {with_sprint}/{sample_size} ({with_sprint/sample_size*100:.1f}%)")
    print(f"  Without Sprint dates: {without_sprint}/{sample_size} ({without_sprint/sample_size*100:.1f}%)")

    if with_sprint > 0:
        total_compared = sprint_earlier + sprint_later + sprint_same
        print(f"\nSprint vs AOP Comparison ({total_compared} tasks with both dates):")
        if total_compared > 0:
            print(f"  Sprint earlier:  {sprint_earlier} ({sprint_earlier/total_compared*100:.1f}%)")
            print(f"  Sprint later:    {sprint_later} ({sprint_later/total_compared*100:.1f}%)")
            print(f"  Same date:       {sprint_same} ({sprint_same/total_compared*100:.1f}%)")
        else:
            print(f"  No tasks with both Plan and Sprint finish dates for comparison")

    if date_issues:
        print(f"\nDate Issues Found: {len(date_issues)}")
        for issue in date_issues[:5]:
            print(f"  - UID {issue['uid']}: {issue['issue']}")

    # Sample of enriched tasks
    print("\n" + "=" * 60)
    print("SAMPLE ENRICHED TASKS (First 10)")
    print("=" * 60)

    for task in sample[:10]:
        dates = task.get('dates', {})
        plan = dates.get('plan', {})
        sprint = dates.get('sprint')

        print(f"\nTask UID {task.get('uid')}: {task.get('name')}")
        print(f"  Outline: {task.get('outline_number')}")
        print(f"  AOP Plan:    {plan.get('start')} → {plan.get('finish')}")

        if sprint:
            print(f"  Sprint:      {sprint.get('start')} → {sprint.get('finish')}")

            # Calculate difference
            if sprint.get('finish') and plan.get('finish'):
                sprint_finish = parse_date(sprint['finish'])
                plan_finish = parse_date(plan['finish'])
                if sprint_finish and plan_finish:
                    delta = (sprint_finish - plan_finish).days
                    if delta < 0:
                        print(f"  Difference:  {abs(delta)} days EARLIER in Sprint")
                    elif delta > 0:
                        print(f"  Difference:  {delta} days LATER in Sprint")
                    else:
                        print(f"  Difference:  SAME DATE")
        else:
            print(f"  Sprint:      NOT MATCHED")

    return {
        'sample_size': sample_size,
        'with_sprint': with_sprint,
        'without_sprint': without_sprint,
        'sprint_earlier': sprint_earlier,
        'sprint_later': sprint_later,
        'sprint_same': sprint_same,
        'date_issues': date_issues
    }


def analyze_unmatched(json_path: str):
    """Analyze tasks that didn't get Sprint dates."""

    print("\n" + "=" * 60)
    print("UNMATCHED TASKS ANALYSIS")
    print("=" * 60)

    with open(json_path, 'r') as f:
        tasks = json.load(f)

    # Find unmatched tasks
    unmatched = []
    for task in tasks:
        if task.get('is_summary'):
            continue

        dates = task.get('dates', {})
        if not dates.get('sprint'):
            unmatched.append(task)

    print(f"\nTotal unmatched leaf tasks: {len(unmatched)}")

    if unmatched:
        # Group by reason
        no_outline = [t for t in unmatched if not t.get('outline_number')]
        has_outline = [t for t in unmatched if t.get('outline_number')]

        print(f"  No outline_number: {len(no_outline)}")
        print(f"  Has outline but not in Sprint: {len(has_outline)}")

        print("\nSample unmatched tasks:")
        for task in unmatched[:10]:
            print(f"  - UID {task.get('uid')}: {task.get('name')}")
            print(f"    Outline: {task.get('outline_number')}")
            print(f"    Is Summary: {task.get('is_summary')}")

    return unmatched


def main():
    json_path = "output/json/Miraya.json"

    print("=" * 60)
    print("Sprint Enrichment Validation - Miraya")
    print("=" * 60)

    # Set random seed for reproducibility
    random.seed(42)

    # Validate sample
    stats = validate_enriched_json(json_path)

    # Analyze unmatched
    unmatched = analyze_unmatched(json_path)

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    if stats['with_sprint'] >= 95:
        print("✅ PASSED: Sprint enrichment coverage is excellent (>95%)")
    elif stats['with_sprint'] >= 80:
        print("⚠️  WARNING: Sprint enrichment coverage is acceptable (80-95%)")
    else:
        print("❌ FAILED: Sprint enrichment coverage is too low (<80%)")

    print(f"\nCoverage: {stats['with_sprint']}/{stats['sample_size']} ({stats['with_sprint']/stats['sample_size']*100:.1f}%)")
    print(f"Unmatched tasks: {len(unmatched)}")

    if stats['date_issues']:
        print(f"\n⚠️  Date quality issues found: {len(stats['date_issues'])}")

if __name__ == "__main__":
    main()
