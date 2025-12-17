"""
Stage 3: Staging Schema Contracts

Python dataclasses representing the staging JSON structure.
These contracts define the shape of data produced by Stage 3 ETL.

Usage:
    from docs.contracts.staging_schema import StagingData, NodeData

    # Validate output structure
    data = generate_staging_data(...)
    staging = StagingData(**data)  # Raises if invalid
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from datetime import datetime


# =============================================================================
# Enums / Literals
# =============================================================================

StatusColor = Literal["red", "amber", "green"]
TimeResolution = Literal["month", "week"]


# =============================================================================
# Meta & Controls
# =============================================================================

@dataclass
class Meta:
    """ETL run metadata."""
    generated_at: str  # ISO 8601 datetime
    data_version: str = "1.0"
    currency_unit: str = "INR"
    page: Optional[str] = None


@dataclass
class Project:
    """Project in hierarchy tree."""
    id: str
    name: str


@dataclass
class TimeMode:
    """Time mode configuration."""
    label: str
    start: str  # YYYY-MM-DD
    end: str    # YYYY-MM-DD
    resolution: TimeResolution


@dataclass
class TimeModes:
    """All time mode configurations."""
    fy: TimeMode
    quarter: TimeMode
    month: TimeMode


@dataclass
class Controls:
    """Dashboard filter controls."""
    hierarchy_tree: Dict[str, Dict[str, List[Project]]]
    time_modes: TimeModes


# =============================================================================
# Widget Data: KPI Gauges
# =============================================================================

@dataclass
class GaugeData:
    """Single gauge data (AOP or Sprint)."""
    achieved_pct: float
    status_color: StatusColor
    actual_ytd: Optional[float] = None
    plan_ytd: Optional[float] = None
    sprint_actual: Optional[float] = None
    sprint_plan: Optional[float] = None
    tasks_with_sprint: Optional[int] = None


@dataclass
class KPIGauges:
    """AOP and Sprint gauge data."""
    aop: GaugeData
    sprint: GaugeData


# =============================================================================
# Widget Data: COC Trend
# =============================================================================

@dataclass
class TrendPoint:
    """Single data point in trend series."""
    label: str           # X-axis label (e.g., "Apr-25", "Wk 14")
    sort_date: str       # YYYY-MM-DD for sorting
    plan_cost: Optional[float]    # Bar height
    actual_cost: Optional[float]  # Bar height
    cumm_plan: Optional[float] = None    # Line Y-value
    cumm_actual: Optional[float] = None  # Line Y-value


@dataclass
class COCTrend:
    """Cost trend data for all time modes."""
    fy_series: List[TrendPoint]       # Monthly data
    quarter_series: List[TrendPoint]  # Weekly data
    month_series: List[TrendPoint]    # Weekly data (+/- 5 weeks)


# =============================================================================
# Widget Data: Project Matrix
# =============================================================================

@dataclass
class Buckets:
    """Achievement bucket counts."""
    gt_120: int      # > 120%
    _100_120: int    # 100-120% (prefixed with _ due to Python naming)
    _85_100: int     # 85-100%
    _60_85: int      # 60-85%
    lt_60: int       # < 60%

    # JSON serialization uses different names
    def to_dict(self) -> Dict[str, int]:
        return {
            "gt_120": self.gt_120,
            "100_120": self._100_120,
            "85_100": self._85_100,
            "60_85": self._60_85,
            "lt_60": self.lt_60
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "Buckets":
        return cls(
            gt_120=data.get("gt_120", 0),
            _100_120=data.get("100_120", 0),
            _85_100=data.get("85_100", 0),
            _60_85=data.get("60_85", 0),
            lt_60=data.get("lt_60", 0)
        )


@dataclass
class MatrixRow:
    """Single row in project matrix."""
    label: str
    buckets: Buckets
    id: Optional[str] = None
    achievement_pct: Optional[float] = None


@dataclass
class ProjectMatrix:
    """Project achievement matrix."""
    rows: List[MatrixRow]


# =============================================================================
# Node Data (per filter key)
# =============================================================================

@dataclass
class NodeData:
    """Complete widget data for a single filter selection."""
    kpi_gauges: KPIGauges
    coc_trend: COCTrend
    project_matrix: ProjectMatrix


# =============================================================================
# Root: Staging Data
# =============================================================================

@dataclass
class StagingData:
    """
    Root staging data structure.

    This is the complete output of Stage 3 ETL.

    Example:
        data = StagingData(
            meta=Meta(generated_at="2025-12-16T10:30:00Z"),
            controls=Controls(...),
            dashboard_data={
                "ALL": NodeData(...),
                "ZONE_MZ": NodeData(...),
                ...
            }
        )
    """
    meta: Meta
    controls: Controls
    dashboard_data: Dict[str, NodeData]


# =============================================================================
# Helper Functions
# =============================================================================

def empty_buckets() -> Buckets:
    """Create empty bucket counts."""
    return Buckets(
        gt_120=0,
        _100_120=0,
        _85_100=0,
        _60_85=0,
        lt_60=0
    )


def get_status_color(percentage: float) -> StatusColor:
    """
    Determine gauge color based on achievement percentage.

    Thresholds:
        - Red: < 85%
        - Amber: 85% - 95%
        - Green: > 95%
    """
    if percentage < 85:
        return "red"
    elif percentage <= 95:
        return "amber"
    else:
        return "green"


def bucket_achievement(percentage: float) -> str:
    """
    Assign achievement percentage to bucket name.

    Returns bucket key as used in JSON (e.g., "gt_120", "85_100").
    """
    if percentage > 120:
        return "gt_120"
    elif percentage >= 100:
        return "100_120"
    elif percentage >= 85:
        return "85_100"
    elif percentage >= 60:
        return "60_85"
    else:
        return "lt_60"


# =============================================================================
# Type Aliases
# =============================================================================

# Filter key type
FilterKey = str  # "ALL" | "ZONE_{id}" | "REG_{id}" | "PROJ_{id}"

# Hierarchy tree type
HierarchyTree = Dict[str, Dict[str, List[Project]]]


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example: Create sample staging data
    sample_gauge = GaugeData(
        achieved_pct=87.5,
        status_color="amber",
        actual_ytd=125000000,
        plan_ytd=142857142.86
    )

    sample_trend_point = TrendPoint(
        label="Apr-25",
        sort_date="2025-04-01",
        plan_cost=12500000,
        actual_cost=11800000,
        cumm_plan=12500000,
        cumm_actual=11800000
    )

    sample_buckets = Buckets(
        gt_120=0,
        _100_120=1,
        _85_100=2,
        _60_85=1,
        lt_60=0
    )

    print("Bucket to dict:", sample_buckets.to_dict())
    print("Status color for 87.5:", get_status_color(87.5))
    print("Bucket for 73.2:", bucket_achievement(73.2))
