"""
Attribute enrichment for task data.

Provides zone/region mapping and hierarchical tower/floor extraction.
"""

import re
from typing import Any


# Project name aliases (XML file name -> canonical project name)
PROJECT_NAME_ALIASES = {
    "Azadnagar": "Horizon",
    "Bigbull-Reserve": "Reserve",
    "OneM": "Avenue 11",
    "Miraya": "Miraya",
    "Aristocrat": "Aristocrat",
    "Zenith": "Zenith",
    "Tropical Isle 146": "Tropical Isle",
    "Jardinia": "Jardinia",
    "Riverine": "Sec. 44, Noida",
    "Ramaiah": "Ramaiah",
    "Woodscapes": "Woodscapes",
    "RGA Land2": "RGA 2",
    "BLSaha": "BL Saha",
}

# Zone/Region mapping (using canonical project names)
ZONE_REGION_MAP = {
    "Horizon": {"zone": "MZ", "region": "MZ1"},
    "Reserve": {"zone": "MZ", "region": "MZ1"},
    "Avenue 11": {"zone": "MZ", "region": "MZ1"},
    "Miraya": {"zone": "NZ", "region": "NZ1"},
    "Aristocrat": {"zone": "NZ", "region": "NZ1"},
    "Zenith": {"zone": "NZ", "region": "NZ1"},
    "Tropical Isle": {"zone": "NZ", "region": "NZ2"},
    "Jardinia": {"zone": "NZ", "region": "NZ2"},
    "Sec. 44, Noida": {"zone": "NZ", "region": "NZ2"},
    "Ramaiah": {"zone": "SZ", "region": "SZ2"},
    "Woodscapes": {"zone": "SZ", "region": "SZ1"},
    "RGA 2": {"zone": "SZ", "region": "SZ1"},
    "BL Saha": {"zone": "WEZ", "region": "Kolkata"},
}


def get_canonical_project_name(file_project_name: str) -> str:
    """
    Convert XML file-based project name to canonical name.

    Args:
        file_project_name: Project name from XML file

    Returns:
        Canonical project name for zone/region lookup
    """
    return PROJECT_NAME_ALIASES.get(file_project_name, file_project_name)


def extract_tower(task_name: str) -> tuple[str | None, int]:
    """
    Extract tower identifier from task name.

    Priority: "Tower" patterns take precedence over "Block" patterns
    Returns tower name and priority level (lower number = higher priority)

    Patterns (in priority order):
    1. Tower A, Tower 1, Tower-A, TOWER A (priority 1)
    2. T1, T2, T-1 (priority 2)
    3. Block A, Block 1, BLOCK-A (priority 3)
    4. Building 1, Building A (priority 4)

    Args:
        task_name: Task name to search

    Returns:
        Tuple of (tower_identifier, priority) or (None, 999) if not found
    """
    if not task_name:
        return None, 999

    # Priority 1: Tower patterns
    tower_pattern = re.search(
        r'\b[Tt][Oo][Ww][Ee][Rr][\s\-_]*([A-Za-z0-9]+)\b', task_name
    )
    if tower_pattern:
        return f"Tower {tower_pattern.group(1)}", 1

    # Priority 2: T1, T2 patterns (but not "TO", "THE", etc.)
    t_pattern = re.search(r'\b[Tt][\s\-_]*(\d+)\b', task_name)
    if t_pattern:
        return f"T{t_pattern.group(1)}", 2

    # Priority 3: Block patterns
    block_pattern = re.search(
        r'\b[Bb][Ll][Oo][Cc][Kk][\s\-_]*([A-Za-z0-9]+)\b', task_name
    )
    if block_pattern:
        return f"Block {block_pattern.group(1)}", 3

    # Priority 4: Building patterns
    building_pattern = re.search(
        r'\b[Bb][Uu][Ii][Ll][Dd][Ii][Nn][Gg][\s\-_]*([A-Za-z0-9]+)\b', task_name
    )
    if building_pattern:
        return f"Building {building_pattern.group(1)}", 4

    return None, 999


def extract_floor(task_name: str) -> str | None:
    """
    Extract floor identifier from task name.

    Patterns:
    - Ground Floor, GF, Ground, G/F
    - 1st Floor, 2nd Floor, 3rd Floor, etc.
    - Floor 1, Floor 2, Floor 12, etc.
    - First Floor, Second Floor, Third Floor
    - Terrace, Terrace Floor
    - Basement, Basement 1, B1, B2

    Args:
        task_name: Task name to search

    Returns:
        Floor identifier or None
    """
    if not task_name:
        return None

    # Ground floor patterns
    if re.search(r'\b[Gg]([Rr][Oo][Uu][Nn][Dd])?[\s\-_/]*[Ff]([Ll][Oo][Oo][Rr])?\b', task_name):
        return "Ground Floor"

    # Terrace patterns
    if re.search(r'\b[Tt][Ee][Rr][Rr][Aa][Cc][Ee]', task_name):
        return "Terrace"

    # Numbered floor patterns: 1st, 2nd, 3rd, 4th-9th, 10th+
    ordinal_pattern = re.search(
        r'\b(\d+)(?:st|nd|rd|th)[\s\-_]*[Ff]([Ll][Oo][Oo][Rr])?\b', task_name
    )
    if ordinal_pattern:
        num = ordinal_pattern.group(1)
        suffix = get_ordinal_suffix(int(num))
        return f"{num}{suffix} Floor"

    # Floor N patterns
    floor_pattern = re.search(
        r'\b[Ff][Ll][Oo][Oo][Rr][\s\-_]*(\d+)\b', task_name
    )
    if floor_pattern:
        return f"Floor {floor_pattern.group(1)}"

    # Word-based ordinals: First, Second, Third, etc.
    word_ordinals = {
        r'\b[Ff][Ii][Rr][Ss][Tt]': "1st",
        r'\b[Ss][Ee][Cc][Oo][Nn][Dd]': "2nd",
        r'\b[Tt][Hh][Ii][Rr][Dd]': "3rd",
        r'\b[Ff][Oo][Uu][Rr][Tt][Hh]': "4th",
        r'\b[Ff][Ii][Ff][Tt][Hh]': "5th",
    }
    for pattern, ordinal in word_ordinals.items():
        if re.search(pattern + r'[\s\-_]*[Ff]([Ll][Oo][Oo][Rr])?', task_name):
            return f"{ordinal} Floor"

    # Basement patterns
    basement_pattern = re.search(
        r'\b[Bb]([Aa][Ss][Ee][Mm][Ee][Nn][Tt])?[\s\-_]*(\d*)\b', task_name
    )
    if basement_pattern and basement_pattern.group(1):  # Must have "basement" word
        num = basement_pattern.group(2)
        if num:
            return f"Basement {num}"
        return "Basement"

    # B1, B2 patterns (only if clearly basement context)
    b_pattern = re.search(r'\b[Bb](\d+)\b', task_name)
    if b_pattern and "floor" not in task_name.lower():
        return f"B{b_pattern.group(1)}"

    return None


def get_ordinal_suffix(n: int) -> str:
    """Get ordinal suffix for a number (st, nd, rd, th)."""
    if 10 <= n % 100 <= 20:
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def build_task_hierarchy(tasks: list[dict]) -> dict[str, dict]:
    """
    Build WBS hierarchy mapping.

    Args:
        tasks: List of task dictionaries

    Returns:
        Dictionary mapping WBS -> task dict for quick lookup
    """
    hierarchy = {}
    for task in tasks:
        wbs = task.get("wbs")
        if wbs:
            hierarchy[wbs] = task
    return hierarchy


def find_parent_by_wbs(hierarchy: dict[str, dict], parent_wbs: str) -> dict | None:
    """
    Find parent task by WBS.

    Args:
        hierarchy: WBS -> task mapping
        parent_wbs: Parent WBS to find

    Returns:
        Parent task dict or None
    """
    return hierarchy.get(parent_wbs)


def get_ancestor_chain(task: dict, hierarchy: dict[str, dict]) -> list[dict]:
    """
    Get all ancestors of a task by walking up parent_wbs chain.

    Args:
        task: Task to get ancestors for
        hierarchy: WBS -> task mapping

    Returns:
        List of ancestor tasks (from immediate parent to root)
    """
    ancestors = []
    current = task
    max_depth = 100  # Safety limit

    while max_depth > 0:
        parent_wbs = current.get("parent_wbs")
        if not parent_wbs:
            break

        parent = find_parent_by_wbs(hierarchy, parent_wbs)
        if not parent:
            break

        ancestors.append(parent)
        current = parent
        max_depth -= 1

    return ancestors


def enrich_zone_region(tasks: list[dict], project_name: str) -> list[dict]:
    """
    Enrich tasks with zone and region based on project name.

    Args:
        tasks: List of task dictionaries
        project_name: Name of the project (from XML file)

    Returns:
        Tasks with zone/region enriched in attributes
    """
    # Get canonical project name
    canonical_name = get_canonical_project_name(project_name)

    # Lookup zone/region
    zone_region = ZONE_REGION_MAP.get(canonical_name)

    if not zone_region:
        # Unknown project, skip enrichment
        return tasks

    # Enrich all tasks
    for task in tasks:
        if task.get("attributes") is not None:
            task["attributes"]["zone"] = zone_region["zone"]
            task["attributes"]["region"] = zone_region["region"]
            # Also update project_name to canonical name
            task["attributes"]["project_name"] = canonical_name

    return tasks


def enrich_tower_floor(tasks: list[dict]) -> list[dict]:
    """
    Enrich tasks with tower and floor attributes by traversing parent hierarchy.

    For each leaf task:
    - Walk up parent chain via parent_wbs
    - Extract tower from ancestors (prioritize "Tower" over "Block")
    - Extract floor from first parent containing floor pattern
    - Populate attributes.tower and attributes.floor

    Args:
        tasks: List of task dictionaries

    Returns:
        Tasks with tower/floor enriched in attributes
    """
    # Build hierarchy for quick parent lookup
    hierarchy = build_task_hierarchy(tasks)

    # Enrich each task
    for task in tasks:
        # Only enrich tasks with non-null attributes
        if task.get("attributes") is None:
            continue

        # Get ancestor chain
        ancestors = get_ancestor_chain(task, hierarchy)

        # Extract tower (with priority)
        best_tower = None
        best_priority = 999

        # Check task itself first
        tower, priority = extract_tower(task.get("name", ""))
        if tower and priority < best_priority:
            best_tower = tower
            best_priority = priority

        # Check ancestors
        for ancestor in ancestors:
            tower, priority = extract_tower(ancestor.get("name", ""))
            if tower and priority < best_priority:
                best_tower = tower
                best_priority = priority

        if best_tower:
            task["attributes"]["tower"] = best_tower

        # Extract floor (first match)
        floor = extract_floor(task.get("name", ""))
        if not floor:
            for ancestor in ancestors:
                floor = extract_floor(ancestor.get("name", ""))
                if floor:
                    break

        if floor:
            task["attributes"]["floor"] = floor

    return tasks


def enrich_attributes(
    tasks: list[dict],
    project_name: str,
    enrich_zone_region_flag: bool = True,
    enrich_tower_floor_flag: bool = True,
) -> list[dict]:
    """
    Master enrichment function.

    Args:
        tasks: List of task dictionaries
        project_name: Name of the project (from XML file)
        enrich_zone_region_flag: Whether to enrich zone/region
        enrich_tower_floor_flag: Whether to enrich tower/floor

    Returns:
        Enriched tasks
    """
    if enrich_zone_region_flag:
        tasks = enrich_zone_region(tasks, project_name)

    if enrich_tower_floor_flag:
        tasks = enrich_tower_floor(tasks)

    return tasks
