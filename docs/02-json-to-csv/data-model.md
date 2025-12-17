# Stage 2 Data Model: JSON to CSV

**Document Version**: 1.0
**Status**: Production
**Last Updated**: 2025-12-16

---

## 1. Input Schema (Master JSON Task)

The input is a list of Task objects from Stage 1. Each task follows the structure defined in `task_schema.json`.

```json
{
  "uid": 51912,
  "id": 2501,
  "wbs": "37300.37500.51900",
  "outline_number": "1.1.1.2.3",
  "name": "Block Work Ground Floor",
  "parent_wbs": "37300.37500",
  "is_summary": false,
  "is_milestone": false,
  "dates": {
    "plan": {"start": "2025-04-15", "end": "2025-05-20", "duration_days": 35},
    "manual": {"start": "2025-04-15", "end": "2025-05-20", "duration_days": 35},
    "sprint": {"start": "2025-04-10", "end": "2025-05-10", "duration_days": 30},
    "actual": {"start": "2025-04-18", "end": null, "duration_days": null}
  },
  "attributes": {
    "project_name": "Miraya",
    "zone": "NZ",
    "region": "NZ1",
    "tower": "Tower 1",
    "floor": "Ground Floor",
    "main_category": "Finishing",
    "sub_category": "Tower Civil Finishes",
    "trade_type": "Blockwork",
    "slab_works": "Non-slab"
  },
  "progress": {"percent_complete": 45, "is_complete": false},
  "cost_plan_total": 125000.00,
  "cost_timeline": {...}
}
```

---

## 2. Output Schema (CSV Row)

### Column Definition

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| code | string | outline_number | Task hierarchy code |
| title | string | name | Task name |
| tower | string | attributes.tower | Tower identifier |
| floor | string | attributes.floor | Floor identifier |
| main_category | string | attributes.main_category | Main work category |
| sub_category | string | attributes.sub_category | Sub work category |
| trade_type | string | attributes.trade_type | Trade/discipline |
| slab_works | string | attributes.slab_works | Slab classification |
| cost_plan_total | float | cost_plan_total | Total planned cost |
| start_date_plan | date | dates.plan.start | Planned start |
| end_date_plan | date | dates.plan.end | Planned end |
| start_date_actual | date | dates.actual.start | Actual start |
| end_date_actual | date | dates.actual.end | Actual end |
| start_date_sprint | date | dates.sprint.start | Sprint start |
| end_date_sprint | date | dates.sprint.end | Sprint end |
| progress | integer | progress.percent_complete | % complete |

---

## 3. Field Mapping

### 3.1 Direct Mapping

| CSV Column | JSON Path |
|------------|-----------|
| code | `outline_number` |
| title | `name` |
| cost_plan_total | `cost_plan_total` |

### 3.2 Nested Mapping (attributes)

| CSV Column | JSON Path |
|------------|-----------|
| tower | `attributes.tower` |
| floor | `attributes.floor` |
| main_category | `attributes.main_category` |
| sub_category | `attributes.sub_category` |
| trade_type | `attributes.trade_type` |
| slab_works | `attributes.slab_works` |

### 3.3 Nested Mapping (dates)

| CSV Column | JSON Path |
|------------|-----------|
| start_date_plan | `dates.plan.start` |
| end_date_plan | `dates.plan.end` |
| start_date_actual | `dates.actual.start` |
| end_date_actual | `dates.actual.end` |
| start_date_sprint | `dates.sprint.start` |
| end_date_sprint | `dates.sprint.end` |

### 3.4 Nested Mapping (progress)

| CSV Column | JSON Path |
|------------|-----------|
| progress | `progress.percent_complete` |

---

## 4. Transformation Rules

### 4.1 Null Handling

```python
def transform_value(value):
    """Transform value for CSV output."""
    if value is None:
        return ""
    return value
```

### 4.2 Safe Nested Access

```python
def extract_row(task: dict) -> dict:
    """Extract CSV row from task."""
    # Handle potentially null nested objects
    dates = task.get('dates') or {}
    plan = dates.get('plan') or {}
    actual = dates.get('actual') or {}
    sprint = dates.get('sprint') or {}
    attributes = task.get('attributes') or {}
    progress = task.get('progress') or {}

    return {
        'code': task.get('outline_number', ''),
        'title': task.get('name', ''),
        'tower': attributes.get('tower') or '',
        'floor': attributes.get('floor') or '',
        'main_category': attributes.get('main_category') or '',
        'sub_category': attributes.get('sub_category') or '',
        'trade_type': attributes.get('trade_type') or '',
        'slab_works': attributes.get('slab_works') or '',
        'cost_plan_total': task.get('cost_plan_total') or '',
        'start_date_plan': plan.get('start') or '',
        'end_date_plan': plan.get('end') or '',
        'start_date_actual': actual.get('start') or '',
        'end_date_actual': actual.get('end') or '',
        'start_date_sprint': sprint.get('start') or '',
        'end_date_sprint': sprint.get('end') or '',
        'progress': progress.get('percent_complete') if progress else '',
    }
```

---

## 5. Task Type Behavior

### 5.1 Parent/Summary Tasks

- `is_summary` = true
- `attributes` = null
- `progress` = null
- `cost_plan_total` = null
- **Result**: All attribute columns empty, progress empty

### 5.2 Milestone Tasks

- `is_milestone` = true
- `attributes` = null
- `progress` = object (has percent_complete)
- `cost_plan_total` = 0
- **Result**: Attribute columns empty, progress populated

### 5.3 Leaf Tasks

- `is_summary` = false, `is_milestone` = false
- All fields populated (if enriched)
- **Result**: Full row data

---

## 6. Sample Outputs

### 6.1 Parent Task Row

```csv
code,title,tower,floor,main_category,sub_category,trade_type,slab_works,cost_plan_total,start_date_plan,end_date_plan,start_date_actual,end_date_actual,start_date_sprint,end_date_sprint,progress
1,Miraya | Sec 43,,,,,,,,2025-01-02,2029-09-06,,,,,
```

### 6.2 Leaf Task Row

```csv
code,title,tower,floor,main_category,sub_category,trade_type,slab_works,cost_plan_total,start_date_plan,end_date_plan,start_date_actual,end_date_actual,start_date_sprint,end_date_sprint,progress
1.1.1.2.3,Block Work,Tower 1,Ground Floor,Finishing,Tower Civil Finishes,Blockwork,Non-slab,125000.00,2025-04-15,2025-05-20,2025-04-18,,,2025-04-10,2025-05-10,45
```

### 6.3 Milestone Row

```csv
code,title,tower,floor,main_category,sub_category,trade_type,slab_works,cost_plan_total,start_date_plan,end_date_plan,start_date_actual,end_date_actual,start_date_sprint,end_date_sprint,progress
1.99,Project Handover,,,,,,,,2029-09-06,2029-09-06,,,,,0
```

---

## 7. Validation Rules

### 7.1 Row Count Validation

```python
# CSV rows (excluding header) should equal JSON tasks
assert csv_rows == len(json_tasks)
```

### 7.2 Column Count Validation

```python
# Each row should have exactly 16 columns
for row in csv_rows:
    assert len(row) == 16
```

### 7.3 No Literal Nulls

```python
# CSV should never contain literal "null" strings
for row in csv_rows:
    for value in row:
        assert value != "null"
```

---

## 8. Statistics Schema

```python
@dataclass
class ExtractionStats:
    """Statistics for single file extraction."""
    project: str
    total_tasks: int
    summary_tasks: int
    leaf_tasks: int
    milestones: int
    rows_written: int
    output_file: str

@dataclass
class BatchStats:
    """Statistics for batch extraction."""
    total_projects: int
    successful: int
    failed: int
    total_rows: int
    projects: List[ExtractionStats]
```
