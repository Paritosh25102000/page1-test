# Trade Type Enrichment Implementation Plan

## Overview

Enrich task attributes with **Trade Type**, **Sub-Category**, and **Main Category** using LLM-based classification of unique work activities extracted from project task hierarchies.

**Model**: Gemini Flash 2.5 via OpenRouter
**Approach**: One API call per project with batch classification
**Source**: `trade-type-cheat-sheet.md` (81 activity classifications)

---

## Problem Analysis

### Challenges

1. **Spatial vs Activity Naming**
   - Leaf tasks like "Floor 1", "Floor 2" under "Post pour" represent spatial divisions, not unique activities
   - The actual activity is "Post pour" (the parent)
   - Need to detect spatial patterns and traverse to parent for actual work name

2. **Common Area vs Private Area Distinction**
   - Same activity (e.g., "Flooring") appears in both flat finishing and common area finishing
   - Context from parent hierarchy determines if it's Tower or Common Area work
   - Impacts Sub-Category classification (e.g., "Flooring" vs "CA-Flooring")

3. **Hierarchical Context Required**
   - Parent chain provides critical context: Tower X → Floor Y → Activity Z
   - Common area indicators: "Staircase", "Lift", "Common area", "Basement" (when shared)
   - Tower indicators: "Flat", "Unit", "Apartment", Tower with floor numbers

4. **Unique Activity Extraction**
   - ~100K total tasks across 12 projects
   - Need to distill to ~100-500 unique activities per project
   - Must preserve context for accurate classification

---

## Architecture

### Phase 1: Unique Activity Extraction

**Input**: Enriched JSON files (with tower/floor attributes)
**Output**: List of unique activities with context per project

```python
{
  "project": "Miraya",
  "unique_activities": [
    {
      "activity_name": "Post pour",
      "context_type": "tower",  # or "common_area", "external", "infrastructure"
      "sample_parent_chain": "Tower A → Post pour → Floor 1",
      "sample_task_names": ["Floor 1", "Floor 2", "Floor 3"],
      "occurrence_count": 96,
      "towers": ["Tower A", "Tower B", "Tower C"],
      "floors": ["1st Floor", "2nd Floor", ..., "Terrace"]
    },
    {
      "activity_name": "Internal Block Work",
      "context_type": "tower",
      "sample_parent_chain": "Tower A → Floor 5 → Internal Block Work",
      "sample_task_names": ["Internal Block Work"],
      "occurrence_count": 150,
      "towers": ["Tower A", "Tower B", "Tower C"],
      "floors": ["1st Floor", ..., "32nd Floor"]
    },
    {
      "activity_name": "Staircase Flooring",
      "context_type": "common_area",
      "sample_parent_chain": "Common Area → Staircase → Flooring",
      "sample_task_names": ["Staircase Flooring", "Floor 1 to 2"],
      "occurrence_count": 30,
      "towers": null,
      "floors": null
    }
  ]
}
```

### Phase 2: LLM Classification

**Input**: Unique activities JSON per project
**Output**: Trade type classifications

```python
{
  "project": "Miraya",
  "classifications": [
    {
      "activity_name": "Post pour",
      "context_type": "tower",
      "trade_type": "Post Pour",
      "sub_category": "RCC",
      "main_category": "Civil Works- RCC",
      "confidence": "high"
    },
    {
      "activity_name": "Internal Block Work",
      "context_type": "tower",
      "trade_type": "Blockwork",
      "sub_category": "Tower Civil Finishes",
      "main_category": "Finishing",
      "confidence": "high"
    },
    {
      "activity_name": "Staircase Flooring",
      "context_type": "common_area",
      "trade_type": "CA-Flooring",
      "sub_category": "Common area finishes",
      "main_category": "Finishing",
      "confidence": "high"
    }
  ]
}
```

### Phase 3: Attribute Mapping

**Input**: Original tasks + Classifications
**Output**: Enriched tasks with trade type attributes

Map classifications back to individual tasks based on:
1. Match activity name from parent chain
2. Match context type (tower vs common area)
3. Apply trade_type, sub_category, main_category to task attributes

---

## Implementation Modules

### 1. `src/trade_type_extractor.py`

**Purpose**: Extract unique activities from project tasks

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
        Dictionary with unique_activities list
    """

def is_spatial_leaf(task_name: str) -> bool:
    """
    Detect if leaf task represents spatial division rather than activity.

    Patterns:
    - "Floor 1", "Floor 2", "1st Floor", "Ground Floor"
    - "Tower A", "Tower B"
    - "Unit 101", "Flat A"
    - Pure spatial names without activity context

    Returns:
        True if spatial, False if actual activity
    """

def extract_activity_from_parent(
    task: dict,
    tasks_by_wbs: dict[str, dict]
) -> tuple[str, list[str]]:
    """
    Traverse parent chain to find actual activity name.

    Returns:
        Tuple of (activity_name, parent_chain)
    """

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

    Indicators:
    - Tower: Has tower attribute, floor attribute, "flat", "unit"
    - Common Area: "staircase", "lift", "common", "lobby", "corridor"
    - External: "external", "site", "boundary", "road", "landscape"
    - Infrastructure: "STP", "WTP", "DG", "substation", "solar"

    Returns:
        Context type string
    """

def group_activities(
    activity_extractions: list[dict]
) -> dict[str, dict]:
    """
    Group extracted activities by (activity_name, context_type).

    Aggregates:
    - Occurrence count
    - Unique towers/floors
    - Sample parent chains
    - Sample task names

    Returns:
        Dictionary of unique activities
    """
```

### 2. `src/trade_type_classifier.py`

**Purpose**: Classify activities using LLM

```python
from src.llm_utils import UniversalLLM

def build_classification_prompt(
    unique_activities: dict,
    cheat_sheet: str
) -> str:
    """
    Build optimized prompt for LLM classification.

    Prompt Structure:
    1. System context: Construction project work classification
    2. Classification rules from cheat sheet
    3. Context type importance (tower vs common area)
    4. List of activities to classify with context
    5. Output format: JSON array

    Returns:
        Formatted prompt string
    """

async def classify_activities_with_llm(
    unique_activities: dict,
    project_name: str,
    llm: UniversalLLM,
    cheat_sheet_path: str
) -> dict:
    """
    Classify unique activities using Gemini Flash 2.5.

    Process:
    1. Load cheat sheet
    2. Build classification prompt
    3. Call LLM (one call per project)
    4. Parse JSON response
    5. Validate classifications against cheat sheet
    6. Return structured results

    Model: google/gemini-2.5-flash via OpenRouter
    Temperature: 0.2 (deterministic)

    Returns:
        Classification results dictionary
    """

def validate_classification(
    classification: dict,
    cheat_sheet_data: list[dict]
) -> dict:
    """
    Validate LLM output against cheat sheet.

    Checks:
    - Trade type exists in cheat sheet
    - Sub-category matches trade type
    - Main category matches sub-category

    Returns:
        Validated classification with confidence score
    """

def load_cheat_sheet(path: str) -> tuple[str, list[dict]]:
    """
    Load trade type cheat sheet.

    Returns:
        Tuple of (markdown_text, parsed_classifications)
    """
```

### 3. `src/trade_type_mapper.py`

**Purpose**: Map classifications back to individual tasks

```python
def map_classifications_to_tasks(
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
       - Populate trade_type, sub_category, main_category
    3. Handle unclassified tasks (set to null or "Unknown")

    Returns:
        Tasks with populated trade type attributes
    """

def determine_task_activity(
    task: dict,
    tasks_by_wbs: dict[str, dict]
) -> tuple[str, str]:
    """
    Determine activity name and context for a single task.

    Uses same logic as extraction phase.

    Returns:
        Tuple of (activity_name, context_type)
    """

def find_matching_classification(
    activity_name: str,
    context_type: str,
    classifications: list[dict]
) -> dict | None:
    """
    Find classification for activity+context.

    Returns:
        Classification dict or None
    """
```

### 4. `src/llm_utils.py` (Enhanced)

**Purpose**: LLM interface utilities (already exists, may need minor updates)

```python
# Already implemented in reference file:
# - UniversalLLM class
# - OpenRouter integration
# - Gemini model support
# - Retry handling
# - Cost tracking

# Potential additions:
def setup_gemini_flash() -> UniversalLLM:
    """
    Setup Gemini Flash 2.5 via OpenRouter.

    Returns:
        Configured UniversalLLM instance
    """
```

### 5. Enhanced `runner.py`

**Purpose**: CLI integration for trade type enrichment

```python
# New arguments:
parser.add_argument(
    '--enrich-trade-types',
    action='store_true',
    help='Enrich existing JSON outputs with trade types using LLM'
)

parser.add_argument(
    '--trade-type-model',
    default='google/gemini-2.5-flash',
    help='LLM model for trade type classification'
)

parser.add_argument(
    '--cheat-sheet',
    default='./trade-type-cheat-sheet.md',
    help='Path to trade type cheat sheet'
)

# New function:
async def enrich_trade_types(
    output_dir: str,
    model: str,
    cheat_sheet_path: str,
    logger=None
) -> dict:
    """
    Enrich all projects with trade type classifications.

    Process:
    1. For each project JSON:
       a. Extract unique activities
       b. Classify with LLM (one call per project)
       c. Map classifications to tasks
       d. Save updated JSON
    2. Generate enrichment report

    Returns:
        Enrichment statistics
    """
```

---

## Prompt Engineering Strategy

### System Prompt

```
You are a construction work classification expert specializing in high-rise residential projects.
Your task is to classify construction activities into trade types, sub-categories, and main categories
based on the provided cheat sheet.

Key Classification Rules:
1. Context matters: The same activity name may have different classifications based on context
   - Tower context (flats/apartments): Use Tower-specific trade types
   - Common area context: Use CA- (Common Area) prefixed trade types
   - External context: Use Ext- prefixed trade types

2. Common Area Indicators:
   - Staircase, Lift, Lobby, Corridor, Basement (shared spaces)
   - CA- prefix in trade type (e.g., CA-Flooring, CA-Blockwork)

3. Tower/Flat Indicators:
   - Activities within apartment units
   - No CA- prefix (e.g., Flooring, Blockwork, Internal Plaster)

4. Activity Synonyms:
   - "Blockwork" = "Block Work" = "Internal Block Work"
   - "Plaster" = "Plastering" = "Plaster Application"
   - Match semantic meaning, not exact text

5. Output Format: JSON array with exact fields
```

### User Prompt Template

```
Project: {project_name}

Classify the following construction activities using the trade type cheat sheet provided below.
For each activity, provide:
- trade_type: Exact match from cheat sheet
- sub_category: Exact match from cheat sheet
- main_category: Exact match from cheat sheet
- confidence: "high", "medium", or "low"

Activities to classify:

{activity_list}

Trade Type Cheat Sheet:

{cheat_sheet}

Output Format (JSON array):
[
  {
    "activity_name": "Post pour",
    "context_type": "tower",
    "trade_type": "Post Pour",
    "sub_category": "RCC",
    "main_category": "Civil Works- RCC",
    "confidence": "high",
    "reasoning": "Direct match from cheat sheet"
  },
  ...
]

IMPORTANT:
- Return ONLY the JSON array, no additional text
- Match trade_type, sub_category, main_category exactly as shown in cheat sheet
- Use context_type to distinguish between Tower and Common Area activities
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Input: Enriched JSON (with tower/floor attributes)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Extract Unique Activities                                │
│    - Identify spatial vs activity leaves                    │
│    - Traverse parents for actual work names                 │
│    - Determine context (tower/common area/external)         │
│    - Group by activity + context                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LLM Classification (One call per project)                │
│    - Build optimized prompt with cheat sheet                │
│    - Call Gemini Flash 2.5 via OpenRouter                   │
│    - Parse JSON response                                    │
│    - Validate against cheat sheet                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Map Classifications to Tasks                             │
│    - Determine activity for each task                       │
│    - Find matching classification                           │
│    - Populate trade_type, sub_category, main_category       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Output: Fully enriched JSON with all attributes          │
│    - zone, region, tower, floor (from Phase 1)              │
│    - trade_type, sub_category, main_category (from Phase 2) │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Order

### Phase 1: Core Extraction (Day 1)
1. Implement `trade_type_extractor.py`
2. Implement spatial detection logic
3. Implement parent traversal
4. Implement context type determination
5. Test extraction on Miraya (smallest project)

### Phase 2: LLM Integration (Day 1-2)
6. Set up `llm_utils.py` with Gemini Flash 2.5
7. Implement `trade_type_classifier.py`
8. Design and test prompt with sample data
9. Implement cheat sheet parsing and validation

### Phase 3: Mapping & Integration (Day 2)
10. Implement `trade_type_mapper.py`
11. Integrate with runner.py CLI
12. Test end-to-end on single project

### Phase 4: Batch Processing & Validation (Day 2-3)
13. Process all 12 projects
14. Generate classification report
15. Manual QA on sample classifications
16. Refine prompt if needed

---

## Testing Strategy

### Unit Tests

```python
# test_trade_type_extractor.py
def test_is_spatial_leaf():
    assert is_spatial_leaf("Floor 1") == True
    assert is_spatial_leaf("Internal Block Work") == False
    assert is_spatial_leaf("Tower A") == True
    assert is_spatial_leaf("Post pour") == False

def test_determine_context_type():
    # Test with tower context
    # Test with common area context
    # Test with external context

# test_trade_type_classifier.py
def test_validate_classification():
    # Test valid classification
    # Test invalid trade type
    # Test mismatched category hierarchy
```

### Integration Tests

```python
# Test full pipeline on Miraya
def test_end_to_end_miraya():
    # 1. Load Miraya.json
    # 2. Extract unique activities
    # 3. Mock LLM response
    # 4. Map to tasks
    # 5. Verify attributes populated
```

### Manual QA

1. **Sample 50 random tasks per project**
2. **Verify**:
   - Trade type makes sense for activity
   - Sub-category matches context (Tower vs CA)
   - Main category is correct
3. **Check edge cases**:
   - Spatial leaf handling
   - Common area detection
   - External work classification

---

## Expected Outcomes

### Statistics Per Project

```json
{
  "project": "Miraya",
  "total_tasks": 2849,
  "tasks_with_trade_type": 2527,
  "unique_activities_found": 45,
  "classification_confidence": {
    "high": 42,
    "medium": 3,
    "low": 0
  },
  "context_breakdown": {
    "tower": 35,
    "common_area": 8,
    "external": 2,
    "infrastructure": 0
  },
  "trade_type_coverage": {
    "RCC": 450,
    "Tower Civil Finishes": 680,
    "Tower Finishing": 890,
    "Tower MEP": 350,
    "Common area finishes": 120,
    "Common area-MEP": 37
  }
}
```

### Classification Report

```
test/trade_type_enrichment_report.md
├── Summary statistics
├── Unique activities per project
├── LLM performance metrics
│   ├── API calls made
│   ├── Total cost
│   ├── Average latency
│   └── Classification confidence distribution
├── Coverage analysis
│   ├── Tasks enriched vs total
│   ├── Trade type distribution
│   └── Category distribution
└── Quality assurance
    ├── Sample validations
    ├── Edge cases handled
    └── Known issues
```

---

## Cost Estimation

**Model**: Gemini Flash 2.5 (via OpenRouter)
**Pricing**: ~$0.10 per million input tokens, ~$0.40 per million output tokens

**Per Project**:
- Unique activities: ~50-150
- Cheat sheet: ~1,500 tokens
- Prompt: ~2,500 tokens total
- Response: ~5,000 tokens
- **Cost per project**: ~$0.002

**Total for 12 projects**: ~$0.024 (~2.4 cents)

---

## Error Handling

### LLM Failures
- Retry logic via `RetryHandler` (up to 3 attempts)
- Fallback to manual classification file if LLM unavailable
- Log failed classifications for manual review

### Missing Matches
- Track activities with no cheat sheet match
- Generate "unknown" classification report
- Allow manual override via config file

### Invalid JSON Response
- Validate JSON structure
- Retry with clarified prompt
- Fall back to line-by-line parsing if needed

---

## Configuration

### Environment Variables

```bash
# .env
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=fallback_key_here  # Optional fallback
```

### Config File (Optional)

```json
{
  "trade_type_enrichment": {
    "model": "google/gemini-2.5-flash",
    "temperature": 0.2,
    "max_retries": 3,
    "cheat_sheet_path": "./trade-type-cheat-sheet.md",
    "manual_overrides": {
      "Miraya": {
        "OC Application": {
          "trade_type": "Misc",
          "sub_category": "Miscellaneous",
          "main_category": "Finishing"
        }
      }
    }
  }
}
```

---

## Success Criteria

1. ✅ **Extraction Accuracy**: 95%+ of activities correctly identified
2. ✅ **Classification Accuracy**: 90%+ trade types match expected (manual QA)
3. ✅ **Context Detection**: 95%+ correct tower vs common area distinction
4. ✅ **Coverage**: 85%+ of leaf tasks enriched with trade types
5. ✅ **Performance**: <30 seconds per project for full enrichment
6. ✅ **Cost Efficiency**: <$0.05 total for all 12 projects

---

## Future Enhancements

1. **Caching**: Cache activity classifications across projects for similar activities
2. **Learning**: Store validated classifications to improve future runs
3. **Fuzzy Matching**: Handle activity name variations better
4. **Confidence Scoring**: Use LLM to provide confidence scores for classifications
5. **Batch Optimization**: Classify multiple projects in single LLM call if similar

---

## References

- Trade Type Cheat Sheet: `trade-type-cheat-sheet.md`
- LLM Utils Reference: `source_data/asta-source-cco-dashboard/sdd-input/llm_utils.py`
- Enriched Data: `output/json/*.json`
- Implementation Plan Phase 1: `etl_implementation_plan.md`
