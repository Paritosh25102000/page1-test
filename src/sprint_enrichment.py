"""
Sprint Schedule Enrichment Module

Enriches existing AOP baseline JSON outputs with Sprint schedule dates.
Sprint schedules are stored in separate XML files with identical structure.

Gap analysis findings (Miraya project):
- UID matching: 0% (UIDs completely reassigned)
- Name matching: Unusable (massive duplicates: 122x "Reinforcement", 122x "Shuttering")
- outline_number matching: 99.5% (2518/2531 tasks matched)
"""

from pathlib import Path
import logging
import json
from typing import Dict, List, Optional
from src.xml_parser import parse_xml_file
from src.transformers import extract_date, iso8601_duration_to_days


def parse_sprint_schedule(xml_path: str) -> Dict[str, Dict]:
    """
    Parse Sprint XML file and extract task dates by outline_number.

    Args:
        xml_path: Path to Sprint XML file

    Returns:
        Dictionary mapping outline_number -> {start, end, duration_days}

    Example:
        {
            "1.1.4.2.3.1.4.13": {
                "start": "2025-10-10",
                "end": "2025-12-15",
                "duration_days": 67
            },
            ...
        }

    Note:
        Gap analysis showed outline_number is 99.5% stable across schedules,
        while UIDs are completely reassigned (0% stable).
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Parsing Sprint schedule: {xml_path}")

    # Use existing XML parser (fully compatible)
    parsed_data = parse_xml_file(xml_path)

    # Build Sprint dates lookup by outline_number
    sprint_dates = {}

    for task in parsed_data['tasks']:
        # Get outline_number (stable identifier across schedules)
        outline_number = task.get('outline_number')

        if not outline_number:
            continue

        # Extract and transform dates (reuse existing transformers)
        start = extract_date(task.get('start'))
        end = extract_date(task.get('finish'))
        duration_iso = task.get('duration')
        duration_days = iso8601_duration_to_days(duration_iso) if duration_iso else None

        if start and end:
            sprint_dates[outline_number] = {
                'start': start,
                'end': end,
                'duration_days': duration_days
            }

    logger.info(f"Extracted {len(sprint_dates)} Sprint task dates")
    return sprint_dates


def match_sprint_to_aop(
    aop_tasks: List[Dict],
    sprint_dates: Dict[str, Dict]
) -> Dict:
    """
    Match Sprint dates to AOP tasks by outline_number.

    Args:
        aop_tasks: List of AOP task dictionaries from JSON output
        sprint_dates: Sprint dates lookup from parse_sprint_schedule()

    Returns:
        Statistics dict with match counts

    Note:
        Matching is done by outline_number. Gap analysis showed 99.5% match rate
        (2518 out of 2531 leaf tasks in Miraya). outline_number is stable across
        schedules, unlike UID (0% stable) or name (massive duplicates).
    """
    logger = logging.getLogger(__name__)

    matched = 0
    unmatched = 0
    unmatched_tasks = []

    for task in aop_tasks:
        # Match by outline_number
        outline_number = task.get('outline_number')
        if not outline_number:
            unmatched += 1
            unmatched_tasks.append({
                'uid': task.get('uid'),
                'name': task.get('name'),
                'reason': 'no_outline_number'
            })
            continue

        if outline_number not in sprint_dates:
            unmatched += 1
            unmatched_tasks.append({
                'uid': task.get('uid'),
                'name': task.get('name'),
                'outline_number': outline_number,
                'reason': 'not_in_sprint'
            })
            continue

        # Populate sprint dates in task
        if task.get('dates'):
            task['dates']['sprint'] = sprint_dates[outline_number]
            matched += 1

    logger.info(f"Matched {matched} tasks, {unmatched} unmatched ({matched/(matched+unmatched)*100:.1f}%)")

    if unmatched_tasks:
        logger.warning(f"Unmatched tasks: {len(unmatched_tasks)}")
        for task in unmatched_tasks[:5]:
            logger.warning(f"  - {task}")

    return {
        'matched': matched,
        'unmatched': unmatched,
        'unmatched_tasks': unmatched_tasks,
        'match_rate': matched / (matched + unmatched) if (matched + unmatched) > 0 else 0
    }


def enrich_sprint_dates(
    json_output_path: str,
    sprint_xml_path: str,
    save_output: bool = True
) -> Dict:
    """
    Main enrichment function: Load AOP JSON, match Sprint dates, save enriched output.

    Args:
        json_output_path: Path to existing AOP JSON output file
        sprint_xml_path: Path to Sprint XML schedule file
        save_output: Whether to save enriched JSON (False for dry-run)

    Returns:
        Statistics dictionary

    Example usage:
        stats = enrich_sprint_dates(
            'output/json/Miraya.json',
            'input/all-sprint-schedules/Miraya.xml'
        )
    """
    logger = logging.getLogger(__name__)

    # 1. Load existing AOP JSON output
    logger.info(f"Loading AOP baseline JSON: {json_output_path}")
    with open(json_output_path, 'r') as f:
        aop_data = json.load(f)

    # 2. Parse Sprint XML
    sprint_dates = parse_sprint_schedule(sprint_xml_path)

    # 3. Match and enrich
    logger.info(f"Matching Sprint dates to AOP tasks by outline_number")
    match_stats = match_sprint_to_aop(aop_data, sprint_dates)

    # 4. Save enriched output
    if save_output:
        logger.info(f"Saving Sprint-enriched JSON: {json_output_path}")
        with open(json_output_path, 'w') as f:
            json.dump(aop_data, f, indent=2)

    # 5. Return statistics
    project_name = Path(json_output_path).stem
    return {
        'project': project_name,
        'aop_tasks': len(aop_data),
        'sprint_dates_available': len(sprint_dates),
        **match_stats
    }


def batch_enrich_sprint(
    json_output_dir: str,
    sprint_xml_dir: str,
    file_mapping: Optional[Dict[str, str]] = None
) -> List[Dict]:
    """
    Batch enrich multiple projects with Sprint dates.

    Args:
        json_output_dir: Directory containing AOP JSON outputs
        sprint_xml_dir: Directory containing Sprint XML files
        file_mapping: Optional custom mapping {json_filename: sprint_xml_filename}
                     If None, assumes matching filenames (e.g., Miraya.json -> Miraya.xml)

    Returns:
        List of statistics dictionaries for each project

    Example:
        stats = batch_enrich_sprint(
            'output/json',
            'input/all-sprint-schedules'
        )
    """
    logger = logging.getLogger(__name__)
    results = []

    json_dir = Path(json_output_dir)
    sprint_dir = Path(sprint_xml_dir)

    for json_file in json_dir.glob('*.json'):
        # Determine Sprint XML filename
        if file_mapping and json_file.stem in file_mapping:
            sprint_filename = file_mapping[json_file.stem]
        else:
            sprint_filename = f"{json_file.stem}.xml"

        sprint_file = sprint_dir / sprint_filename

        if not sprint_file.exists():
            logger.warning(f"Sprint XML not found for {json_file.name}: {sprint_file}")
            continue

        # Enrich single project
        try:
            stats = enrich_sprint_dates(
                str(json_file),
                str(sprint_file)
            )
            results.append(stats)
            logger.info(f"✓ {stats['project']}: {stats['matched']}/{stats['aop_tasks']} "
                       f"tasks matched ({stats['match_rate']:.1%})")
        except Exception as e:
            logger.error(f"✗ Failed to enrich {json_file.name}: {e}")
            results.append({
                'project': json_file.stem,
                'error': str(e)
            })

    return results
