# Stage 1 Implementation Plan: XML to JSON Conversion

**Document Version**: 1.0
**Status**: Production (Implemented)
**Last Updated**: 2025-12-16

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           XML to JSON Pipeline                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │ XML Parser  │───▶│ Transformer │───▶│Task Builder │                 │
│  │             │    │             │    │             │                 │
│  │ • iterparse │    │ • durations │    │ • classify  │                 │
│  │ • namespace │    │ • dates     │    │ • build obj │                 │
│  │ • extract   │    │ • booleans  │    │ • dates obj │                 │
│  └─────────────┘    └─────────────┘    └──────┬──────┘                 │
│                                               │                         │
│                                               ▼                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │ Enrichment  │◀───│Cost Timeline│◀───│   Tasks     │                 │
│  │             │    │             │    │             │                 │
│  │ • zone/reg  │    │ • weekly    │    │ • list of   │                 │
│  │ • tower/flr │    │ • incoming  │    │   task dict │                 │
│  │ • trade     │    │ • summary   │    │             │                 │
│  └──────┬──────┘    └─────────────┘    └─────────────┘                 │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────┐    ┌─────────────┐                                    │
│  │  Validator  │───▶│ JSON Output │                                    │
│  │             │    │             │                                    │
│  │ • schema    │    │ • per proj  │                                    │
│  │ • sample    │    │ • reports   │                                    │
│  │ • QA report │    │ • logs      │                                    │
│  └─────────────┘    └─────────────┘                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Module Structure

```
etl-cco-dashboard/
├── runner.py                     # Main entry point / CLI
├── task_schema.json              # Target JSON schema
├── xml_to_json_mapping.json      # Field mapping rules
│
├── src/
│   ├── __init__.py
│   ├── xml_parser.py             # XML parsing with streaming
│   ├── transformers.py           # Field transformation functions
│   ├── task_builder.py           # Task object construction
│   ├── cost_timeline.py          # Weekly cost calculations
│   ├── validators.py             # Schema validation & QA
│   ├── enrichment.py             # Zone, region, tower, floor
│   ├── sprint_enrichment.py      # Sprint dates integration
│   ├── trade_type_extractor.py   # Unique activity extraction
│   ├── trade_type_classifier.py  # LLM-based classification
│   ├── trade_type_mapper.py      # Map classifications to tasks
│   ├── llm_utils.py              # LLM client for OpenRouter API
│   └── utils.py                  # Shared utilities
│
├── project_name_mapping.json     # XML filename → canonical project name
│
├── input/                        # Input files (gitignored)
│   ├── all-aop-baselines/        # AOP baseline XML files
│   └── all-sprint-schedules/     # Sprint XML files
│
└── output/                       # Generated output (gitignored)
    ├── json/                     # Converted JSON files
    ├── reports/                  # QA and validation reports
    └── logs/                     # Processing logs
```

---

## 3. Module Specifications

### 3.1 xml_parser.py - XML Parsing

**Purpose**: Stream-parse large XML files, extract Tasks and Assignments

```python
def parse_xml_file(file_path: str) -> dict:
    """
    Parse XML and return structured data.

    Returns:
        {
            "project": {"name": str, "title": str, ...},
            "tasks": List[dict],
            "assignments": List[dict],
            "task_assignment_map": Dict[int, List[dict]]
        }

    Raises:
        ET.ParseError: If XML is malformed
        FileNotFoundError: If file does not exist
    """

def extract_tasks(root, namespace: dict) -> List[dict]:
    """Extract all Task elements as dictionaries."""

def extract_assignments(root, namespace: dict) -> List[dict]:
    """Extract all Assignment elements with TimephasedData."""

def build_task_assignment_map(assignments: List) -> Dict[int, List]:
    """Map TaskUID -> list of assignments for actual date derivation."""
```

**Key Considerations**:
- Use `xml.etree.ElementTree.iterparse` for memory efficiency
- Handle namespace: `{http://schemas.microsoft.com/project}`
- Extract TimephasedData Type=2 for actual dates

### 3.2 transformers.py - Field Transformations

**Purpose**: Implement all transformation functions from mapping rules

```python
# Direct transformations
def parse_int(value: str) -> Optional[int]:
    """Parse integer from string."""

def parse_float(value: str) -> Optional[float]:
    """Parse float from string."""

def boolean_from_string(value: str) -> bool:
    """Convert '1'/'0' to boolean."""

def extract_date(datetime_str: str) -> Optional[str]:
    """Extract date from datetime: '2025-03-15T08:00:00' -> '2025-03-15'"""

# Duration conversion
def iso8601_duration_to_days(duration: str) -> Optional[float]:
    """Convert ISO 8601 duration to days: 'PT960H0M0S' -> 120.0"""

# Derived fields
def remove_last_segment(wbs: str) -> Optional[str]:
    """Derive parent WBS: '37300.37500' -> '37300'"""

# Actual date derivation
def derive_actual_start(timephased_data: List) -> Optional[str]:
    """Get earliest TimephasedData Type=2 Start."""

def derive_actual_end(timephased_data: List) -> Optional[str]:
    """Get latest TimephasedData Type=2 Finish."""

def calculate_duration_days(start: str, end: str) -> int | None:
    """Calculate calendar days between dates."""
```

### 3.3 task_builder.py - Task Object Construction

**Purpose**: Build target JSON objects according to schema

```python
def build_task(
    xml_task: dict,
    task_assignment_map: Dict[int, List[dict]],
    project_name: str,
    cost_timeline_builder: Callable
) -> dict:
    """Transform XML task to target schema format."""

def determine_task_type(xml_task: dict) -> str:
    """
    Return 'parent', 'leaf', or 'milestone'.

    Logic:
        - is_summary == true → 'parent'
        - is_milestone == true → 'milestone'
        - otherwise → 'leaf'
    """

def build_dates_object(
    xml_task: dict,
    assignments: List,
    task_type: str
) -> dict:
    """
    Build dates object: {plan, manual, sprint, actual}.

    Plan/Manual: From XML Task fields
    Sprint: null (populated later by sprint_enrichment)
    Actual:
        - Leaf: From TimephasedData
        - Milestone: From ActualStart/ActualFinish
        - Parent: null
    """

def build_progress_object(xml_task: dict, task_type: str) -> Optional[dict]:
    """
    Build progress: {percent_complete, is_complete}.

    Returns None for parent tasks.
    """

def build_attributes_placeholder(
    project_name: str,
    task_type: str
) -> Optional[dict]:
    """
    Build attributes with project_name, null for other fields.

    Returns None for parent and milestone tasks.
    """
```

**Task Type Behavior**:

| Type | attributes | progress | cost_plan_total | cost_timeline |
|------|------------|----------|-----------------|---------------|
| parent | null | null | null | null |
| milestone | null | object | 0 | null |
| leaf | object | object | number | object |

### 3.4 cost_timeline.py - Weekly Cost Calculations

**Purpose**: Calculate FY 2025-26 weekly cost breakdown

```python
FY_START = "2025-04-01"
FY_END = "2026-03-31"

def calculate_cost_timeline(
    cost_plan_total: float,
    plan_dates: dict,
    actual_dates: dict,
    is_complete: bool
) -> Optional[dict]:
    """
    Calculate full cost_timeline object.

    Returns None if:
        - cost_plan_total is 0 or None
        - Task has no overlap with FY period
    """

def calculate_incoming_cost(
    cost_total: float,
    duration_days: float,
    start_date: str,
    fy_start: str
) -> dict:
    """
    Calculate incoming cost before FY.

    Returns:
        {"days_before_fy": int, "cost": float}
    """

def generate_weekly_costs(
    cost_total: float,
    plan_dates: dict,
    actual_dates: dict,
    is_complete: bool,
    incoming_plan: float,
    incoming_actual: float
) -> List[dict]:
    """
    Generate weekly cost entries.

    Each entry:
        {
            "week_number": int,
            "week_start": str,  # Monday YYYY-MM-DD
            "week_end": str,    # Sunday YYYY-MM-DD
            "days_in_task": {"plan": int, "actual": int},
            "plan": {"cost": float, "accumulated": float},
            "actual": {"cost": float, "accumulated": float}
        }
    """

def get_week_boundaries(date: str) -> Tuple[str, str]:
    """Return (monday, sunday) for the week containing date."""
```

**Calculation Rules**:
- Plan rate: `cost_plan_total / duration_plan_days`
- Actual rate (complete): `cost_plan_total / duration_actual_days`
- Actual rate (incomplete): Use plan rate
- Weeks run Monday-Sunday

### 3.5 enrichment.py - Attribute Enrichment

**Purpose**: Enrich task attributes with zone, region, tower, floor

```python
# Project name aliases (XML filename → canonical name)
PROJECT_NAME_ALIASES = {
    "Azadnagar": "Horizon",
    "Bigbull-Reserve": "Reserve",
    "OneM": "Avenue 11",
    # ... etc
}

# Zone/Region mapping
ZONE_REGION_MAP = {
    "Horizon": {"zone": "MZ", "region": "MZ1"},
    "Reserve": {"zone": "MZ", "region": "MZ1"},
    "Avenue 11": {"zone": "MZ", "region": "MZ1"},
    # ... etc
}

def get_canonical_project_name(file_project_name: str) -> str:
    """Convert XML file-based project name to canonical name."""

def enrich_zone_region(tasks: List[dict], project_name: str) -> List[dict]:
    """Enrich tasks with zone and region based on project name."""

def extract_tower(task_name: str) -> Optional[str]:
    """
    Extract tower identifier from task name.

    Patterns: "Tower A", "Tower 1", "T1"
    Excludes: Block, Building, descriptive terms
    """

def extract_floor(task_name: str) -> Optional[str]:
    """
    Extract floor identifier from task name.

    Patterns: "Ground Floor", "1st Floor", "Floor 12", "Terrace"
    Normalizes: B1 → Basement 1
    """

def build_task_hierarchy(tasks: List[dict]) -> Dict[str, dict]:
    """Build WBS hierarchy mapping."""

def enrich_tower_floor(tasks: List[dict]) -> List[dict]:
    """
    Enrich tasks with tower and floor by traversing parent hierarchy.

    Algorithm:
        1. Build WBS → task mapping
        2. For each leaf task, walk up parent chain
        3. Extract tower from first matching ancestor
        4. Extract floor from first matching ancestor
    """

def enrich_attributes(
    tasks: List[dict],
    project_name: str,
    enrich_zone_region_flag: bool = True,
    enrich_tower_floor_flag: bool = True
) -> List[dict]:
    """Master enrichment function."""
```

### 3.6 sprint_enrichment.py - Sprint Integration

**Purpose**: Integrate Sprint dates from separate XML files

```python
def parse_sprint_schedule(xml_path: str) -> Dict[str, Dict]:
    """
    Parse Sprint XML and extract task dates by outline_number.

    Returns:
        {
            "1.1.4.2.3": {"start": "...", "finish": "...", "duration_days": 67},
            ...
        }
    """

def match_sprint_to_aop(
    aop_tasks: List[Dict],
    sprint_dates: Dict[str, Dict]
) -> Dict:
    """
    Match Sprint dates to AOP tasks by outline_number.

    Returns statistics dict with match counts.
    """

def enrich_sprint_dates(
    json_output_path: str,
    sprint_xml_path: str,
    save_output: bool = True
) -> Dict:
    """Main enrichment function: Load AOP JSON, match Sprint dates, save."""

def batch_enrich_sprint(
    json_output_dir: str,
    sprint_xml_dir: str,
    file_mapping: Optional[Dict[str, str]] = None
) -> List[Dict]:
    """Batch enrich multiple projects with Sprint dates."""
```

### 3.7 trade_type_extractor.py - Unique Activity Extraction

**Purpose**: Extract unique work activities from project task hierarchies

```python
def extract_unique_activities(tasks: list[dict], project_name: str) -> dict:
    """
    Extract unique work activities from project tasks.

    Algorithm:
    1. Identify leaf tasks (non-summary, non-milestone)
    2. For each leaf task:
       - Check if task name is spatial (Floor X, Tower Y, etc.)
       - If spatial: traverse to parent for actual activity name
       - Extract context from parent chain (tower, common area, external)
    3. Group by activity name + context type
    4. Collect occurrence stats and sample information

    Returns:
        {
            "project": str,
            "unique_activities": [
                {
                    "activity_name": "Post pour",
                    "context_type": "tower",
                    "sample_parent_chain": "Tower A → Post pour → Floor 1",
                    "occurrence_count": 96
                }
            ]
        }
    """

def is_spatial_leaf(task_name: str) -> bool:
    """
    Detect if leaf task represents spatial division rather than activity.
    Patterns: "Floor 1", "Tower A", "Unit 101"
    """

def extract_activity_from_parent(
    task: dict,
    tasks_by_wbs: dict[str, dict]
) -> tuple[str, list[str]]:
    """Traverse parent chain to find actual activity name."""

def determine_context_type(
    task: dict,
    parent_chain: list[str],
    tasks_by_wbs: dict[str, dict]
) -> str:
    """
    Determine activity context from parent hierarchy.

    Context Types:
    - "tower": Flat/apartment finishing (has tower+floor context)
    - "common_area": Shared spaces (staircase, lift, lobby, basement)
    - "external": Site work, external services
    - "infrastructure": MEP infrastructure (STP, WTP, DG, Substation)
    """
```

### 3.8 trade_type_classifier.py - LLM Classification

**Purpose**: Classify activities using Gemini Flash 2.5 via OpenRouter

```python
def classify_activities_with_llm(
    unique_activities: dict,
    project_name: str,
    llm: UniversalLLM,
    cheat_sheet_path: str
) -> dict:
    """
    Classify unique activities using Gemini Flash 2.5.

    Process:
    1. Load cheat sheet (trade-type-cheat-sheet.md)
    2. Build classification prompt with context
    3. Call LLM (one call per project, ~50-150 activities)
    4. Parse JSON response
    5. Validate against cheat sheet

    Model: google/gemini-2.5-flash via OpenRouter
    Temperature: 0.2 (deterministic)

    Returns:
        {
            "project": str,
            "classifications": [
                {
                    "activity_name": "Post pour",
                    "context_type": "tower",
                    "trade_type": "Post Pour",
                    "sub_category": "RCC",
                    "main_category": "Civil Works- RCC",
                    "confidence": "high"
                }
            ]
        }
    """

def build_classification_prompt(
    unique_activities: dict,
    cheat_sheet: str
) -> str:
    """Build optimized prompt for LLM classification."""

def validate_classification(
    classification: dict,
    cheat_sheet_data: list[dict]
) -> dict:
    """Validate LLM output against cheat sheet."""
```

### 3.9 trade_type_mapper.py - Classification Mapping

**Purpose**: Map LLM classifications back to individual tasks

```python
def enrich_tasks_with_trade_types(
    tasks: list[dict],
    classifications: dict,
    unique_activities: dict
) -> list[dict]:
    """
    Apply trade type classifications to individual tasks.

    Algorithm:
    1. Build activity lookup: task → (activity_name, context_type)
    2. For each task with attributes:
       - Determine its activity and context
       - Find matching classification
       - Populate trade_type, sub_category, main_category, slab_works
    3. Handle unclassified tasks (set to null or "Unknown")

    Returns:
        Tasks with populated trade type attributes
    """

def determine_task_activity(
    task: dict,
    tasks_by_wbs: dict[str, dict]
) -> tuple[str, str]:
    """Determine activity name and context for a single task."""

def find_matching_classification(
    activity_name: str,
    context_type: str,
    classifications: list[dict]
) -> dict | None:
    """Find classification for activity+context."""
```

### 3.10 llm_utils.py - LLM Client

**Purpose**: Universal LLM client for OpenRouter API

```python
class UniversalLLM:
    """
    Simple LLM interface for OpenRouter API.

    Attributes:
        api_key: OpenRouter API key
        model: Model identifier (default: google/gemini-2.5-flash)
        base_url: OpenRouter API endpoint
    """

    def __init__(self, api_key: str = None, model: str = "google/gemini-2.5-flash"):
        """
        Initialize the LLM interface.

        Args:
            api_key: OpenRouter API key (falls back to OPENROUTER_API_KEY env var)
            model: Model to use

        Raises:
            ValueError: If no API key provided or found in environment
            ImportError: If openai package not installed
        """

    async def ainvoke(self, messages: list[dict]) -> AIMessage:
        """
        Async invoke the LLM.

        Args:
            messages: List of {"role": str, "content": str} dicts

        Returns:
            AIMessage with response content

        Raises:
            Exception: On API errors (re-raised from OpenAI client)
        """

class AIMessage:
    """Simple message container for LLM responses."""
    content: str
```

**Configuration**:
- Temperature: 0.2 (deterministic/consistent responses)
- Model: google/gemini-2.5-flash via OpenRouter
- Supports `.env` file loading for API key

### 3.11 validators.py - QA and Validation

**Purpose**: Validate output against schema and source XML

```python
def validate_task_structure(task: dict) -> list[str]:
    """Validate task has all required fields, return list of errors."""

def validate_task_types(tasks: list[dict]) -> dict:
    """Validate task type consistency (parent/leaf/milestone)."""

def sample_validation(
    output_tasks: list[dict],
    xml_file_path: str,
    sample_size: int = 100
) -> dict:
    """Compare random sample of output tasks against source XML."""

def calculate_field_coverage(tasks: list[dict]) -> dict:
    """Calculate coverage statistics for nullable fields."""

def generate_qa_report(
    project_name: str,
    total_tasks: int,
    type_validation: dict,
    sample_results: dict,
    field_coverage: dict
) -> dict:
    """
    Generate comprehensive QA report.

    Returns:
        {
            "project": str,
            "total_tasks": int,
            "parents": int,
            "leaves": int,
            "milestones": int,
            "sample_size": int,
            "sample_pass_rate": float,
            "validation_issues": List,
            "sample_failures": List,
            "field_coverage": Dict[str, float]
        }
    """
```

### 3.12 runner.py - CLI Entry Point

**Purpose**: CLI interface and orchestration

```python
"""
XML to JSON ETL Runner for COO Dashboard

Usage:
    # Standard processing with enrichment
    python runner.py                          # All files
    python runner.py --file Miraya.xml        # Single file

    # Enrichment control
    python runner.py --no-enrich-zone-region  # Skip zone/region
    python runner.py --no-enrich-tower-floor  # Skip tower/floor
    python runner.py --no-enrich              # Skip all enrichment

    # Trade type enrichment (LLM-based)
    python runner.py --enrich-trade-types                  # Enable LLM classification
    python runner.py --enrich-trade-types --openrouter-api-key YOUR_KEY
    python runner.py --file Miraya.xml --enrich-trade-types

    # Update existing outputs
    python runner.py --enrich-only            # Enrich existing JSON

    # Sprint integration
    python runner.py --sprint-dir input/all-sprint-schedules
    python runner.py --enrich-sprint --sprint-dir ...

    # Validation
    python runner.py --validate-only          # Validate existing
    python runner.py --dry-run                # Parse without saving
"""
```

---

## 8. Error Handling

### 8.1 Module-Level Error Behavior

| Module | Exception Types | Behavior |
|--------|----------------|----------|
| xml_parser | `ET.ParseError`, `FileNotFoundError` | Re-raises to caller |
| transformers | None | Returns `None` for invalid inputs |
| task_builder | None | Graceful degradation with null fields |
| cost_timeline | None | Returns `None` for invalid/zero-cost tasks |
| enrichment | None | Skips unknown projects silently |
| validators | None | Returns validation results dict |
| trade_type_classifier | `ValueError` | Raises on JSON parse failure |
| llm_utils | `ValueError`, `ImportError`, API errors | Re-raises to caller |
| sprint_enrichment | `FileNotFoundError`, `json.JSONDecodeError` | Logged, continues with other files |

### 8.2 Graceful Degradation

The pipeline is designed to continue processing even when some enrichments fail:

1. **Missing Sprint XML**: Logs warning, skips Sprint enrichment for that project
2. **Trade type classification fails**: Logs error, task attributes remain null
3. **Invalid API key**: Logs error, returns exit code 1
4. **Single file processing error**: Logs error, continues with other files

### 8.3 Trade Type Classification: Batching and Retry

**Batch Processing** (for large activity counts):
- Default batch size: 500 activities per LLM call
- Projects with >500 unique activities are automatically split
- Results are combined after all batches complete

**Retry Logic** (for invalid classifications):
- Classifications are validated against the cheat sheet
- Invalid trade types (not in cheat sheet) trigger automatic retry
- Retry includes additional instruction for exact matching
- Failed retries retain original invalid classification with `validation_status: "invalid"`

---

## 4. Data Flow

### 4.1 Processing Pipeline

```
XML File
    │
    ▼
┌─────────────────┐
│ 1. Parse XML    │  xml_parser.parse_xml_file()
│    - Tasks      │
│    - Assignments│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Transform    │  transformers.*
│    - Dates      │
│    - Durations  │
│    - Booleans   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Build Tasks  │  task_builder.build_task()
│    - Classify   │
│    - Structure  │
│    - Dates obj  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Cost Timeline│  cost_timeline.calculate_cost_timeline()
│    - Weekly     │
│    - Incoming   │
│    - Summary    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Enrichment   │  enrichment.enrich_attributes()
│    - Zone/Reg   │  sprint_enrichment.enrich_sprint_dates()
│    - Tower/Flr  │  trade_type_*.py (LLM)
│    - Trade Type │
│    - Sprint     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. Validate     │  validators.*
│    - Schema     │
│    - Sample     │
└────────┬────────┘
         │
         ▼
    JSON Output
```

### 4.2 Output Structure

```
output/
├── json/
│   ├── Horizon.json         # From Azadnagar.xml
│   ├── Reserve.json         # From Bigbull-Reserve.xml
│   ├── Avenue 11.json       # From OneM.xml
│   ├── Miraya.json
│   ├── Aristocrat.json
│   ├── Zenith.json
│   ├── Tropical Isle.json
│   ├── Jardinia.json
│   ├── Sec. 44, Noida.json  # From Riverine.xml
│   ├── Ramaiah.json
│   ├── Woodscapes.json
│   ├── RGA 2.json           # From RGA Land2.xml
│   └── BL Saha.json         # From BLSaha.xml
│
├── reports/
│   ├── qa_report_Miraya.json
│   ├── qa_report_Aristocrat.json
│   ├── summary_report.json
│   └── validation_errors.json
│
└── logs/
    └── etl_20251209_143022.log
```

---

## 5. Reference Data

### 5.1 Zone/Region Mapping

| Project | Zone | Region |
|---------|------|--------|
| Horizon | MZ | MZ1 |
| Reserve | MZ | MZ1 |
| Avenue 11 | MZ | MZ1 |
| Miraya | NZ | NZ1 |
| Aristocrat | NZ | NZ1 |
| Zenith | NZ | NZ1 |
| Tropical Isle | NZ | NZ2 |
| Jardinia | NZ | NZ2 |
| Sec. 44, Noida | NZ | NZ2 |
| Ramaiah | SZ | SZ2 |
| Woodscapes | SZ | SZ1 |
| RGA 2 | SZ | SZ1 |
| BL Saha | WEZ | Kolkata |

### 5.2 Tower Extraction Patterns

**Included**:
- `Tower A`, `Tower B`, `Tower 1`, `Tower 2`
- `T1`, `T2`, `T3`
- `TOWER-A`, `TOWER-B`

**Excluded**:
- Block Work, Block A (non-spatial)
- Building Certification (non-spatial)
- Tower Area, Tower Completion (descriptive)
- Tower Ground, Tower Raft (construction phases)

### 5.3 Floor Extraction Patterns

**Patterns**:
- Ground Floor, GF
- 1st Floor, 2nd Floor, Floor 1, Floor 12
- First Floor, Second Floor
- Terrace, Terrace Floor
- Basement, Basement 1, B1, B2

**Normalization**:
- B1 → Basement 1
- B2 → Basement 2
- Basement 01 → Basement 1

---

## 6. Implementation Status

### Phase 1-7: Core ETL - COMPLETE

| Phase | Module | Status |
|-------|--------|--------|
| 1 | Infrastructure | Done |
| 2 | XML Parser | Done |
| 3 | Task Builder | Done |
| 4 | Cost Timeline | Done |
| 5 | Validation | Done |
| 6 | Runner/CLI | Done |
| 7 | Zone/Region/Tower/Floor Enrichment | Done |

### Phase 8: Sprint Integration - COMPLETE

| Task | Status |
|------|--------|
| Sprint parser | Done |
| Matching logic | Done |
| Enrichment function | Done |
| Batch processing | Done |
| CLI integration | Done |

### Phase 9: Trade Type Enrichment (LLM) - COMPLETE

| Task | Status |
|------|--------|
| trade_type_extractor.py - Unique activity extraction | Done |
| trade_type_classifier.py - LLM classification | Done |
| trade_type_mapper.py - Map to tasks | Done |
| Cheat sheet reference (trade-type-cheat-sheet.md) | Done |
| CLI integration (--enrich-trade-types) | Done |
| Context type detection (tower/common_area) | Done |
| OpenRouter/Gemini Flash 2.5 integration | Done |

---

## 7. Performance Benchmarks

| File | Tasks | Parse Time | Transform Time | Total |
|------|-------|------------|----------------|-------|
| Miraya.xml | 2,849 | 2s | 5s | ~10s |
| Woodscapes.xml | 23,494 | 15s | 45s | ~60s |
| All 13 files | ~110,000 | - | - | ~10 min |

**Memory Usage**: Peak ~1.5 GB for largest file

---

## 9. Configuration Files

### 9.1 project_name_mapping.json

Maps XML filenames (without extension) to canonical project names used in output:

```json
{
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
    "BLSaha": "BL Saha"
}
```

**Usage**: Loaded by `utils.get_project_name_from_file()` and duplicated in `enrichment.PROJECT_NAME_ALIASES` for zone/region lookup.

**Note**: The `enrichment.py` module contains a duplicate mapping (`PROJECT_NAME_ALIASES`) to avoid file I/O during enrichment. Keep both in sync when adding projects.

---

## 10. Pipeline Reporting

### 10.1 Overview

The pipeline reporting system generates comprehensive reports after each pipeline stage, combining results from multiple processing steps into a unified view. Reports are generated in both JSON (machine-readable) and Markdown (human-readable) formats.

**Design Principle**: The reporting system is designed to be extended across all 3 ETL phases:
- **Phase 1** (XML→JSON): Stage 1 results + enrichment statistics
- **Phase 2** (JSON→CSV): Adds Stage 2 extraction statistics
- **Phase 3** (JSON→Staging): Will add aggregation and widget statistics

### 10.2 Module: report_generator.py

**Purpose**: Generate comprehensive pipeline reports combining results from multiple stages.

**Location**: `src/report_generator.py`

```python
def generate_pipeline_report(
    project_name: str,
    json_output_path: str,
    csv_output_path: Optional[str] = None,
    qa_report_path: Optional[str] = None,
    summary_report_path: Optional[str] = None,
) -> dict:
    """
    Generate comprehensive pipeline report for a single project.

    Args:
        project_name: Name of the project
        json_output_path: Path to the JSON output file (Stage 1)
        csv_output_path: Path to the CSV output file (Stage 2)
        qa_report_path: Path to existing QA report
        summary_report_path: Path to summary report with enrichment stats

    Returns:
        Complete pipeline report dictionary with structure:
        {
            "report_type": "pipeline_report",
            "report_version": "1.0",
            "generated_at": "ISO timestamp",
            "project": str,
            "stage1": {...},      # Task counts
            "stage2": {...},      # CSV stats
            "enrichment": {...},  # Enrichment coverage
            "validation": {...},  # QA results
            "output_files": {...} # File paths and sizes
        }
    """

def generate_markdown_summary(report: dict) -> str:
    """
    Generate markdown summary from pipeline report.

    Returns formatted markdown with tables for:
    - Stage 1 Results (task counts)
    - Enrichment Results (zone, tower, floor, trade type, sprint)
    - Validation Results (sample pass rate, issues)
    - Stage 2 Results (CSV rows)
    - Output Files (paths and sizes)
    """

def save_pipeline_report(
    project_name: str,
    output_dir: str,
    json_output_path: str,
    csv_output_path: Optional[str] = None,
    qa_report_path: Optional[str] = None,
    summary_report_path: Optional[str] = None,
) -> tuple[str, str]:
    """
    Generate and save pipeline report in JSON and Markdown formats.

    Returns:
        Tuple of (json_report_path, markdown_report_path)
    """
```

### 10.3 Report Schema

```json
{
  "report_type": "pipeline_report",
  "report_version": "1.0",
  "generated_at": "2025-12-17T15:05:22.253540",
  "project": "Ramaiah",
  "stage1": {
    "total_tasks": 1408,
    "parents": 249,
    "leaves": 1155,
    "milestones": 4
  },
  "stage2": {
    "csv_rows": 1408,
    "csv_rows_with_header": 1409
  },
  "enrichment": {
    "zone_region": {
      "enriched": 1155,
      "total_applicable": 1155,
      "rate": 1.0
    },
    "tower_floor": {
      "with_tower": 1155,
      "with_floor": 975,
      "total_applicable": 1155,
      "tower_rate": 1.0,
      "floor_rate": 0.844
    },
    "trade_types": {
      "enriched": 1155,
      "total_applicable": 1155,
      "rate": 1.0,
      "by_context": {
        "tower": 795,
        "common_area": 360
      },
      "by_confidence": {
        "high": 905,
        "medium": 65,
        "low": 185
      }
    },
    "sprint": {
      "matched": 919,
      "unmatched": 489,
      "match_rate": 0.653
    }
  },
  "validation": {
    "sample_size": 100,
    "sample_pass_rate": 1.0,
    "validation_issues_count": 0,
    "sample_failures_count": 0,
    "field_coverage": {
      "dates.actual.start": 0.01,
      "dates.actual.end": 0.0,
      "cost_timeline": 0.58,
      "attributes": 0.82,
      "progress": 0.82
    }
  },
  "output_files": {
    "json": {
      "path": "output/json/Ramaiah.json",
      "size_bytes": 2199316,
      "size_human": "2.1 MB"
    },
    "csv": {
      "path": "output/table/Ramaiah.csv",
      "size_bytes": 173560,
      "size_human": "169.5 KB"
    }
  }
}
```

### 10.4 Integration Points

**Stage 2 Runner** (`runner_table_extraction.py`):
- Pipeline reports are generated automatically after CSV extraction
- Controlled via `--pipeline-report` (default: enabled) and `--no-pipeline-report` flags
- Reports saved to `output/reports/pipeline_report_{project}.json` and `.md`

**Future Integration** (Stage 3):
- `stage3` section will be added to the report schema
- Aggregation statistics (tasks per zone, tasks per trade type, etc.)
- Widget-specific metrics

### 10.5 Output Files

```
output/reports/
├── qa_report_{project}.json      # Stage 1 QA report
├── summary_report.json           # Stage 1 summary (all projects)
├── pipeline_report_{project}.json # Combined pipeline report (JSON)
└── pipeline_report_{project}.md   # Combined pipeline report (Markdown)
```

### 10.6 CLI Flags

**Stage 2 (`runner_table_extraction.py`)**:
```
--pipeline-report      Generate comprehensive pipeline report (default: True)
--no-pipeline-report   Skip pipeline report generation
```
