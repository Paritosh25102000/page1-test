"""
Stage 1: Task Schema Contracts

Python dataclasses representing the Master JSON task structure.
These contracts define the shape of data produced by Stage 1 ETL.

Usage:
    from docs.contracts.task_schema import Task, Dates, Attributes

    # Validate task structure
    task = build_task(xml_task, assignments, project_name)
    validated = Task(**task)  # Raises if invalid
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from datetime import date


# =============================================================================
# Enums / Literals
# =============================================================================

TaskType = Literal["parent", "leaf", "milestone"]

Zone = Literal["MZ", "NZ", "SZ", "WEZ"]

Region = Literal["MZ1", "NZ1", "NZ2", "SZ1", "SZ2", "Kolkata"]

ProjectName = Literal[
    "Horizon", "Reserve", "Avenue 11", "Miraya", "Aristocrat", "Zenith",
    "Tropical Isle", "Jardinia", "Sec. 44, Noida", "Ramaiah",
    "Woodscapes", "RGA 2", "BL Saha"
]

MainCategory = Literal["Civil Works- RCC", "MEP", "Finishing", "Infra"]

SubCategory = Literal[
    "RCC", "Tower MEP", "Tower Civil Finishes", "Tower Finishing",
    "Common area finishes", "Common area-MEP", "Ext MEP",
    "BRM-Security", "Miscellaneous", "Ext Infra", "NTA RCC"
]

TradeType = Literal[
    "Reinforcement", "Shuttering- Conventional", "Shuttering- AL",
    "Electrical", "Concreting", "Post Pour", "Blockwork", "Railing",
    "Waterproofing", "Plumbing", "Door", "Int Plaster", "Paint",
    "Flooring", "False Ceiling", "CA-Blockwork", "Lift", "CA-Railing",
    "CA-Flooring", "CA-Door", "CA-Electrical", "CA-Int Plaster",
    "CA-Paint", "CA-PHE", "CA-Fire-fighting & FAPA", "CA-HVAC",
    "Ext Electrical", "BRM-Security", "Ext Fire fighting & FAPA",
    "Ext PHE", "Ext Paint", "CP Sanitary", "Misc", "Ext Plaster",
    "STP", "OWC", "WTP", "Solar", "Ext Infra", "NTA RCC", "NTA Finishing"
]

SlabWorks = Literal["Typical", "Non-typical", "Non-slab"]


# =============================================================================
# Date Objects
# =============================================================================

@dataclass
class DateRange:
    """Date range with start, end, and duration."""
    start: Optional[str] = None  # YYYY-MM-DD
    end: Optional[str] = None    # YYYY-MM-DD
    duration_days: Optional[float] = None


@dataclass
class SprintDateRange:
    """Sprint date range with start, end, and duration.

    Note: Sprint uses 'end' to match the standard date range terminology.
    """
    start: Optional[str] = None   # YYYY-MM-DD
    end: Optional[str] = None     # YYYY-MM-DD
    duration_days: Optional[float] = None


@dataclass
class Dates:
    """All date-related fields."""
    plan: DateRange
    manual: DateRange
    sprint: Optional[SprintDateRange] = None
    actual: Optional[DateRange] = None


# =============================================================================
# Attributes
# =============================================================================

@dataclass
class Attributes:
    """Task attributes from enrichment."""
    project_name: ProjectName
    zone: Zone
    region: Region
    tower: Optional[str] = None
    floor: Optional[str] = None
    main_category: Optional[MainCategory] = None
    sub_category: Optional[SubCategory] = None
    trade_type: Optional[TradeType] = None
    slab_works: Optional[SlabWorks] = None


# =============================================================================
# Progress
# =============================================================================

@dataclass
class Progress:
    """Task completion status."""
    percent_complete: int  # 0-100
    is_complete: bool


# =============================================================================
# Cost Timeline
# =============================================================================

@dataclass
class FYPeriod:
    """Financial year period."""
    start: str = "2025-04-01"
    end: str = "2026-03-31"


@dataclass
class IncomingCostEntry:
    """Cost incurred before FY start."""
    days_before_fy: int
    cost: float


@dataclass
class IncomingCost:
    """Plan and actual incoming costs."""
    plan: IncomingCostEntry
    actual: IncomingCostEntry


@dataclass
class CostEntry:
    """Cost for a period with accumulated total."""
    cost: float
    accumulated: float


@dataclass
class DaysInTask:
    """Days overlapping with task in a week."""
    plan: int  # 0-7
    actual: int  # 0-7


@dataclass
class WeeklyCost:
    """Cost breakdown for a single week."""
    week_number: int
    week_start: str  # Monday YYYY-MM-DD
    week_end: str    # Sunday YYYY-MM-DD
    days_in_task: DaysInTask
    plan: CostEntry
    actual: CostEntry


@dataclass
class CostSummary:
    """Aggregated cost summary for the task."""
    total_weeks_in_fy: int
    plan_cost_in_fy: float
    actual_cost_in_fy: float
    plan_cost_before_fy: float
    actual_cost_before_fy: float


@dataclass
class CostTimeline:
    """Weekly cost breakdown for FY."""
    fy_period: FYPeriod
    incoming_cost: IncomingCost
    weekly_costs: List[WeeklyCost]
    summary: CostSummary


# =============================================================================
# Task (Root Entity)
# =============================================================================

@dataclass
class Task:
    """
    Root task entity.

    Represents a single task from the Asta Powerproject XML
    transformed to the master JSON schema.

    Example:
        task = Task(
            uid=51912,
            id=2501,
            wbs="37300.37500.51900",
            outline_number="2.7.3.5.1.4.13",
            name="Block Work Ground Floor",
            parent_wbs="37300.37500",
            is_summary=False,
            is_milestone=False,
            dates=Dates(...),
            attributes=Attributes(...),
            progress=Progress(...),
            cost_plan_total=125000.00,
            cost_timeline=CostTimeline(...)
        )
    """
    # Identity
    uid: int
    id: int
    wbs: str
    outline_number: str
    name: str

    # Hierarchy
    parent_wbs: Optional[str]

    # Flags
    is_summary: bool
    is_milestone: bool

    # Dates
    dates: Dates

    # Attributes (null for parent/milestone)
    attributes: Optional[Attributes]

    # Progress (null for parent)
    progress: Optional[Progress]

    # Cost (null for parent)
    cost_plan_total: Optional[float]
    cost_timeline: Optional[CostTimeline]


# =============================================================================
# Helper Functions
# =============================================================================

def determine_task_type(is_summary: bool, is_milestone: bool) -> TaskType:
    """
    Determine task type from flags.

    Returns:
        'parent' if is_summary
        'milestone' if is_milestone
        'leaf' otherwise
    """
    if is_summary:
        return "parent"
    elif is_milestone:
        return "milestone"
    else:
        return "leaf"


def empty_date_range() -> DateRange:
    """Create empty date range."""
    return DateRange(start=None, end=None, duration_days=None)


def get_zone_region(project_name: str) -> tuple[Zone, Region]:
    """
    Get zone and region for a project.

    Args:
        project_name: Canonical project name

    Returns:
        Tuple of (zone, region)

    Raises:
        KeyError: If project not found
    """
    ZONE_REGION_MAP = {
        "Horizon": ("MZ", "MZ1"),
        "Reserve": ("MZ", "MZ1"),
        "Avenue 11": ("MZ", "MZ1"),
        "Miraya": ("NZ", "NZ1"),
        "Aristocrat": ("NZ", "NZ1"),
        "Zenith": ("NZ", "NZ1"),
        "Tropical Isle": ("NZ", "NZ2"),
        "Jardinia": ("NZ", "NZ2"),
        "Sec. 44, Noida": ("NZ", "NZ2"),
        "Ramaiah": ("SZ", "SZ2"),
        "Woodscapes": ("SZ", "SZ1"),
        "RGA 2": ("SZ", "SZ1"),
        "BL Saha": ("WEZ", "Kolkata"),
    }
    return ZONE_REGION_MAP[project_name]


def get_canonical_project_name(file_name: str) -> ProjectName:
    """
    Get canonical project name from XML filename.

    Args:
        file_name: XML filename (without extension)

    Returns:
        Canonical project name

    Raises:
        KeyError: If filename not found
    """
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
    return PROJECT_NAME_ALIASES.get(file_name, file_name)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example: Create sample task
    sample_dates = Dates(
        plan=DateRange(start="2025-04-15", end="2025-05-20", duration_days=35),
        manual=DateRange(start="2025-04-15", end="2025-05-20", duration_days=35),
        sprint=SprintDateRange(start="2025-04-10", end="2025-05-10", duration_days=30),
        actual=DateRange(start="2025-04-18", end=None, duration_days=None)
    )

    sample_attrs = Attributes(
        project_name="Miraya",
        zone="NZ",
        region="NZ1",
        tower="Tower 1",
        floor="Ground Floor",
        main_category="Finishing",
        sub_category="Tower Civil Finishes",
        trade_type="Blockwork",
        slab_works="Non-slab"
    )

    sample_progress = Progress(percent_complete=45, is_complete=False)

    print("Task type for parent:", determine_task_type(True, False))
    print("Task type for milestone:", determine_task_type(False, True))
    print("Task type for leaf:", determine_task_type(False, False))
    print("Zone/Region for Miraya:", get_zone_region("Miraya"))
    print("Canonical name for 'Azadnagar':", get_canonical_project_name("Azadnagar"))
