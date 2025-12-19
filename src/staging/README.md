# Staging ETL Package

**Package**: `src.staging`
**Purpose**: Transform Master JSON task data into pre-aggregated staging JSON for dashboard consumption

---

## Quick Start

```bash
# Generate staging data for Page 1
python runner_staging.py

# With verbose logging
python runner_staging.py --verbose

# Validate existing output
python runner_staging.py --validate-only
```

---

## Architecture

### Data Flow

```
Master JSON (output/json/*.json)
    ↓
[Load All Projects] → 111,832 tasks
    ↓
[Build Hierarchy] → Zone → Region → Project tree
    ↓
[Generate Filter Keys] → 24 keys (ALL, ZONE_*, REG_*, PROJ_*)
    ↓
[For Each Filter Key]
    ├─ [Filter Tasks] → Subset for this filter
    ├─ [Calculate KPI Gauges] → AOP & Sprint achievement
    ├─ [Calculate COC Trend] → FY, Quarter, Month series
    └─ [Calculate Project Matrix] → Achievement buckets
    ↓
[Assemble Output] → staging/page1-executive-summary.json
    ↓
[Validate] → Structure & data integrity checks
```

---

## Modules

### Core Infrastructure

- **`time_utils.py`** - Date/time calculations for FY, Quarter, Month
- **`hierarchy_builder.py`** - Extract organizational hierarchy from tasks

### Calculators

- **`kpi_calculator.py`** - AOP and Sprint achievement gauges
- **`coc_trend_calculator.py`** - Cost of Construction trend series
- **`matrix_calculator.py`** - Project achievement bucket distribution

### Integration

- **`aggregator.py`** - Main orchestration and coordination
- **`validators.py`** - Output validation and quality checks

---

## API Reference

### aggregator.generate_staging_data()

```python
from src.staging.aggregator import generate_staging_data

data = generate_staging_data(
    json_dir="output/json",
    page="page1",
    current_date=None  # Optional: override "today" for testing
)
```

**Returns**: Complete staging data structure

### kpi_calculator.calculate_kpi_gauges()

```python
from src.staging.kpi_calculator import calculate_kpi_gauges

gauges = calculate_kpi_gauges(filtered_tasks, current_date=None)
# Returns: {"aop": {...}, "sprint": {...}}
```

### coc_trend_calculator.calculate_coc_trend()

```python
from src.staging.coc_trend_calculator import calculate_coc_trend

trend = calculate_coc_trend(filtered_tasks, current_date=None)
# Returns: {"fy_series": [...], "quarter_series": [...], "month_series": [...]}
```

### matrix_calculator.calculate_project_matrix()

```python
from src.staging.matrix_calculator import calculate_project_matrix

matrix = calculate_project_matrix(filtered_tasks, hierarchy, filter_key)
# Returns: {"rows": [...]}
```

---

## Output Schema

### Top Level

```typescript
{
  meta: {
    generated_at: string;      // ISO 8601 timestamp
    data_version: string;       // "1.0"
    currency_unit: string;      // "INR"
    page: string;              // "page1"
  },
  controls: {
    hierarchy_tree: HierarchyTree;
    time_modes: TimeModes;
  },
  dashboard_data: Record<DataKey, NodeData>;
}
```

### Node Data (per filter key)

```typescript
{
  kpi_gauges: {
    aop: {
      achieved_pct: number;
      status_color: "red" | "amber" | "green";
      actual: number;
      plan: number;
      tasks_with_sprint: number;
    },
    sprint: { /* same structure */ }
  },
  coc_trend: {
    fy_series: TrendPoint[];      // 12 months
    quarter_series: TrendPoint[]; // ~14 weeks
    month_series: TrendPoint[];   // ~11 weeks
  },
  project_matrix: {
    rows: MatrixRow[];
  }
}
```

---

## Performance

### Benchmarks (111,832 tasks, 13 projects)

| Metric | Value |
|--------|-------|
| **Processing Time** | 2.4 seconds |
| **Output File Size** | 261 KB |
| **Memory Usage** | <500 MB |
| **Filter Keys** | 24 |
| **Throughput** | ~46,600 tasks/second |

### Optimization Notes

- Uses weekly cost aggregation (already computed in Master JSON)
- Pre-aggregates all filter combinations (faster than on-demand)
- Minimal memory footprint via streaming aggregation
- No external dependencies (pure Python stdlib)

---

## Configuration

### Financial Year

Edit `src/staging/time_utils.py`:

```python
FY_START = "2025-04-01"
FY_END = "2026-03-31"
```

### Gauge Color Thresholds

Edit `src/staging/kpi_calculator.py`:

```python
def get_status_color(percentage: float) -> str:
    if percentage < 85:      # Red threshold
        return "red"
    elif percentage <= 95:   # Amber threshold
        return "amber"
    else:
        return "green"
```

### Achievement Buckets

Edit `src/staging/matrix_calculator.py`:

```python
def bucket_achievement(percentage: float) -> str:
    if percentage > 120:      # Over-performing
        return "gt_120"
    elif percentage >= 100:   # On track
        return "100_120"
    # ... etc
```

---

## Testing

### Integration Test

```bash
# Test with single project
cp output/json/Miraya.json output/json-test/
python runner_staging.py --input-dir output/json-test --dry-run

# Test with all projects
python runner_staging.py --dry-run
```

### Validation

```bash
# Validate structure
python runner_staging.py --validate-only

# Inspect output
python -c "
import json
with open('output/staging/page1-executive-summary.json') as f:
    data = json.load(f)
    print(f'Filter keys: {len(data[\"dashboard_data\"])}')
    print(f'ALL AOP: {data[\"dashboard_data\"][\"ALL\"][\"kpi_gauges\"][\"aop\"][\"achieved_pct\"]}%')
"
```

---

## Troubleshooting

### Issue: AttributeError on task.get()

**Cause**: Some tasks have `None` attributes (summary/parent tasks)

**Solution**: Use defensive attribute access:
```python
(task.get("attributes") or {}).get("zone")
```

### Issue: Empty series in COC Trend

**Cause**: No weekly cost data in Master JSON

**Solution**: Verify Master JSON has `cost_timeline.weekly_costs` populated

### Issue: Missing filter keys

**Cause**: Projects not properly grouped by zone/region

**Solution**: Check `attributes.zone` and `attributes.region` in Master JSON

---

## Design Decisions

### Why Pre-Aggregate All Filters?

**Decision**: Compute all 24 filter combinations upfront (261 KB)

**Rationale**:
- On-demand would require full dataset load per request (slow)
- 261 KB is negligible compared to Master JSON size (~120 MB)
- Dashboard needs instant response (<100ms)
- Trade-off: 2.4s generation time vs sub-second query time

### Why Exclude Summary Tasks?

**Decision**: Only leaf tasks contribute to cost calculations

**Rationale**:
- Summary task costs are sum of children (would double-count)
- Milestone tasks have zero duration/cost
- Matches Master JSON schema design (`attributes: null` for summaries)

### Why Use Weekly Aggregation?

**Decision**: Leverage existing weekly cost timeline from Master JSON

**Rationale**:
- Weekly data already computed by Phase 1 ETL
- Sufficient granularity for dashboard visualization
- Easy to aggregate into months (FY view) or filter by week (Quarter/Month)

---

## Future Enhancements

### Priority 1: Testing
- [ ] Unit tests for all calculator modules
- [ ] Integration tests with fixtures
- [ ] JSON Schema validation

### Priority 2: Features
- [ ] Sprint-specific cost prorating
- [ ] Custom date range support
- [ ] Multiple FY support
- [ ] Delta generation (incremental updates)

### Priority 3: Performance
- [ ] Parallel filter key processing
- [ ] Caching for repeated runs
- [ ] Streaming JSON output

---

## Maintenance

### Adding New Dashboard Pages

1. Update `runner_staging.py`:
   ```python
   page_files = {
       'page1': 'page1-executive-summary.json',
       'page2': 'page2-your-new-page.json'  # Add here
   }
   ```

2. Create schema: `schemas/page-2-your-page/page2_schema.json`

3. Implement calculators in `src/staging/`

4. Test with `python runner_staging.py --page page2`

### Updating Hierarchy

Hierarchy is auto-generated from Master JSON `attributes.zone/region/project_name`.

To add/remove projects:
1. Update Master JSON with correct attributes
2. Regenerate: `python runner_staging.py`

---

## Support

For issues or questions:
- Check `docs/03-json-to-staging/IMPLEMENTATION_SUMMARY.md`
- Review `docs/03-json-to-staging/plan.md` for design details
- Consult task schema: `task_schema.json`
