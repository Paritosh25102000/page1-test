"""
Test script to enrich Miraya project with Sprint dates.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sprint_enrichment import enrich_sprint_dates

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    json_path = "output/json/Miraya.json"
    sprint_xml_path = "input/all-sprint-schedules/Miraya.xml"

    print("=" * 60)
    print("Sprint Enrichment - Miraya Project")
    print("=" * 60)

    stats = enrich_sprint_dates(json_path, sprint_xml_path)

    print("\n" + "=" * 60)
    print("ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"Project: {stats['project']}")
    print(f"Total AOP tasks: {stats['aop_tasks']}")
    print(f"Sprint dates available: {stats['sprint_dates_available']}")
    print(f"Matched: {stats['matched']}")
    print(f"Unmatched: {stats['unmatched']}")
    print(f"Match rate: {stats['match_rate']:.1%}")

    if stats['unmatched_tasks']:
        print(f"\nUnmatched tasks ({len(stats['unmatched_tasks'])}):")
        for task in stats['unmatched_tasks'][:10]:
            print(f"  - UID {task.get('uid')}: {task.get('name')} ({task.get('reason')})")
        if len(stats['unmatched_tasks']) > 10:
            print(f"  ... and {len(stats['unmatched_tasks']) - 10} more")

    print("\nEnriched JSON saved to:", json_path)

if __name__ == "__main__":
    main()
