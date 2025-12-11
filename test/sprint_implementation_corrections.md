# Sprint Implementation Plan Corrections

**Date:** 2025-12-11
**Issue:** Implementation plan referenced non-existent `unique_task_id` field

## Problem Discovery

The initial Phase 8 implementation plan specified using `unique_task_id` as the primary matching field between AOP and Sprint schedules. However, investigation revealed:

### What Exists in XML
- Extended Attribute `Unique_Task_ID` (FieldID 188743731, alias for Text1)
- Example values found: "9700549"
- Present in both AOP and Sprint XML files

### What's in JSON Output
```json
{
  "uid": 31,
  "id": 1,
  "wbs": "37300",
  "outline_number": "1",
  "name": "Miraya | Sec 43",
  ...
}
```

**Key Finding:** The current ETL (`xml_parser.py`) does NOT extract ExtendedAttributes, including `Unique_Task_ID`. Only `uid` and `wbs` are available as identifiers in the JSON output.

## Corrections Made

Updated Phase 8 implementation plan to use **UID-based matching** instead:

### Function Signature Changes

**Before:**
```python
def parse_sprint_schedule(xml_path: str) -> Dict[str, Dict]:
    """Parse Sprint XML and extract dates by Unique_Task_ID."""
    # Extracted unique_task_id from ExtendedAttribute
```

**After:**
```python
def parse_sprint_schedule(xml_path: str) -> Dict[str, Dict]:
    """Parse Sprint XML and extract dates by UID."""
    # Extract uid (which is already in JSON output)
```

**Before:**
```python
def match_sprint_to_aop(
    aop_tasks: List[Dict],
    sprint_dates: Dict[str, Dict],
    matching_strategy: str = 'unique_id'  # ❌ Field doesn't exist in JSON
) -> Dict:
```

**After:**
```python
def match_sprint_to_aop(
    aop_tasks: List[Dict],
    sprint_dates: Dict[str, Dict]  # ✅ Always use UID
) -> Dict:
```

### Implementation Changes

1. **Removed `matching_strategy` parameter** from all functions
2. **Changed dictionary keys** from `unique_task_id` to `uid` (as string)
3. **Updated docstrings** to reflect UID-based matching
4. **Added note** about expected match rate (50.7% based on gap analysis)

## Match Rate Expectations

Based on Sprint vs AOP gap analysis for Miraya:
- **Total AOP Tasks:** 2849
- **Total Sprint Tasks:** 2847
- **Common UIDs:** 1444 (50.7%)

Expected enrichment result: ~50% of AOP tasks will get Sprint dates populated.

## Alternative Approaches (Future Consideration)

If higher match rates are needed, could explore:

1. **Extract Unique_Task_ID from XML**
   - Modify `xml_parser.py` to extract ExtendedAttributes
   - Add to JSON output schema
   - Re-run ETL for all projects
   - Use as primary matching field

2. **WBS-based matching**
   - Match by WBS code instead of UID
   - May provide better coverage if WBS is more stable across schedules

3. **Hybrid matching**
   - Try UID first, fall back to WBS for unmatched tasks
   - Risk of incorrect matches if WBS restructured

## Recommendation

Proceed with **UID-based matching** as specified in corrected implementation plan:
- Simplest approach
- No ETL pipeline changes required
- 50% match rate acceptable for MVP
- Can enhance later if needed
