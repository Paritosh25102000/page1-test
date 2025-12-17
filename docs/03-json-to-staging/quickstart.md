# Stage 3: JSON → Staging Quickstart

**Stage**: 03-json-to-staging
**Prerequisites**: Stage 1 output (Master JSON files in `output/json/`)

---

## Quick Start

### 1. Verify Prerequisites

```bash
# Ensure Master JSON files exist
ls output/json/
# Should show: Miraya.json, Horizon.json, etc. (13 files)

# Check Python environment
python --version  # Should be 3.8+
```

### 2. Generate Staging Data

```bash
# Generate Page 1 staging (default)
python runner_staging.py

# Explicit page selection
python runner_staging.py --page page1
```

### 3. Verify Output

```bash
# Check output file
ls -la output/staging/
# Should show: page1-executive-summary.json

# Validate structure
python -c "import json; d = json.load(open('output/staging/page1-executive-summary.json')); print(f'Filter keys: {len(d[\"dashboard_data\"])}')"
# Should show: Filter keys: ~23
```

---

## Usage Examples

### Basic Generation

```bash
# Generate Page 1 staging data
python runner_staging.py
```

**Output**:
```
2025-12-16 10:30:00 - INFO - Generating staging data for page1
2025-12-16 10:30:01 - INFO - Loaded 110424 total tasks
2025-12-16 10:30:02 - INFO - Generated 23 filter keys
2025-12-16 10:30:45 - INFO - Generated in 45.2 seconds
2025-12-16 10:30:45 - INFO - Saved to: output/staging/page1-executive-summary.json
2025-12-16 10:30:45 - INFO - File size: 2.34 MB
```

### Custom Input Directory

```bash
# Use different input directory
python runner_staging.py --input-dir /path/to/json/files
```

### Dry Run (Preview)

```bash
# Generate but don't save
python runner_staging.py --dry-run

# Shows statistics without writing file
```

### Validate Existing Output

```bash
# Validate existing staging file
python runner_staging.py --validate-only
```

### Test with Specific Date

```bash
# Override "today" for testing
python runner_staging.py --current-date 2025-12-01
```

### Verbose Output

```bash
# Enable debug logging
python runner_staging.py --verbose
```

---

## CLI Reference

```
usage: runner_staging.py [-h] [--page PAGE] [--input-dir INPUT_DIR]
                         [--output-dir OUTPUT_DIR] [--current-date CURRENT_DATE]
                         [--dry-run] [--validate-only] [--verbose]

Generate staging JSON for dashboard

options:
  -h, --help            show this help message and exit
  --page PAGE           Dashboard page to generate (default: page1)
  --input-dir INPUT_DIR
                        Directory containing Master JSON files (default: output/json)
  --output-dir OUTPUT_DIR
                        Directory for staging output (default: output/staging)
  --current-date CURRENT_DATE
                        Override current date (YYYY-MM-DD) for testing
  --dry-run             Generate but do not save output
  --validate-only       Validate existing output without regenerating
  --verbose             Enable verbose logging
```

---

## Output Structure

### Page 1 Output File

**Location**: `output/staging/page1-executive-summary.json`

**Structure**:
```json
{
  "meta": {
    "generated_at": "2025-12-16T10:30:00.000Z",
    "data_version": "1.0",
    "currency_unit": "INR"
  },
  "controls": {
    "hierarchy_tree": { /* Zone → Region → Project tree */ },
    "time_modes": { /* FY, Quarter, Month configs */ }
  },
  "dashboard_data": {
    "ALL": { /* Global aggregate */ },
    "ZONE_MZ": { /* Zone aggregate */ },
    "REG_MZ1": { /* Region aggregate */ },
    "PROJ_Horizon": { /* Project data */ }
    /* ... ~23 keys total */
  }
}
```

### Filter Keys

| Key Pattern | Example | Description |
|-------------|---------|-------------|
| `ALL` | `ALL` | Global aggregate |
| `ZONE_{id}` | `ZONE_MZ` | Zone aggregate |
| `REG_{id}` | `REG_MZ1` | Region aggregate |
| `PROJ_{id}` | `PROJ_Horizon` | Project data |

---

## Deployment

### Copy to Frontend

```bash
# Copy staging JSON to frontend public folder
cp output/staging/page1-executive-summary.json frontend/public/data/
```

### Full Refresh Workflow

```bash
# 1. Run Stage 1 (if source XML changed)
python runner.py --input-dir input/all-aop-baselines --enrich-trade-types

# 2. Run Stage 3
python runner_staging.py --page page1

# 3. Deploy to frontend
cp output/staging/page1-executive-summary.json frontend/public/data/

# 4. (Optional) Rebuild frontend
cd frontend && npm run build
```

---

## Troubleshooting

### Common Issues

**Issue**: `FileNotFoundError: output/json/` not found

**Solution**: Run Stage 1 first to generate Master JSON files:
```bash
python runner.py --input-dir input/all-aop-baselines
```

---

**Issue**: Memory error with large datasets

**Solution**: The staging module processes tasks incrementally. If still experiencing issues:
```bash
# Process with explicit memory limits (Linux)
ulimit -v 2000000  # 2GB limit
python runner_staging.py
```

---

**Issue**: Slow processing (>5 minutes)

**Solution**: Check for:
1. Large number of tasks with cost timeline data
2. Disk I/O bottleneck (use SSD)
3. Consider processing pages in sequence rather than parallel

---

**Issue**: Output validation fails

**Solution**: Check validation errors:
```bash
python runner_staging.py --validate-only --verbose
```

Common causes:
- Missing attributes (zone/region) in Master JSON
- Invalid cost timeline data
- Schema version mismatch

---

## Performance Expectations

| Metric | Target | Typical |
|--------|--------|---------|
| Processing time | <2 min | 45-90 sec |
| Memory usage | <1 GB | 400-600 MB |
| Output file size | <5 MB | 2-3 MB |
| Filter keys | ~23 | 23 |

---

## Next Steps

After generating staging data:

1. **Verify in browser**: Load `page1-executive-summary.json` in browser dev tools
2. **Test with frontend**: Start dashboard and verify data loads
3. **Check filter keys**: Ensure all filter combinations work

See also:
- [spec.md](./spec.md) - Full specification
- [data-model.md](./data-model.md) - Entity definitions
- [tasks.md](./tasks.md) - Implementation tasks
