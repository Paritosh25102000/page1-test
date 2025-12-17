# Stage 2 Quickstart: JSON to CSV Extraction

**Document Version**: 1.0
**Last Updated**: 2025-12-16

---

## Prerequisites

- Python 3.10+
- Stage 1 output JSON files in `output/json/`

---

## Basic Usage

### Extract All Files

```bash
python runner_table_extraction.py
```

This will:
1. Read all JSON files from `output/json/`
2. Extract 16-column CSV for each project
3. Write to `output/table/`
4. Generate extraction report

### Extract Single File

```bash
python runner_table_extraction.py --file output/json/Miraya.json
```

---

## Filtering Options

### Exclude Parent Tasks

```bash
python runner_table_extraction.py --no-summary
```

Excludes summary/parent tasks (is_summary = true).

### Exclude Milestones

```bash
python runner_table_extraction.py --no-milestones
```

Excludes milestone tasks (is_milestone = true).

### Leaf Tasks Only

```bash
python runner_table_extraction.py --no-summary --no-milestones
```

Only includes work (leaf) tasks.

---

## Output Configuration

### Custom Output Directory

```bash
python runner_table_extraction.py --output-dir reports/tables
```

### Generate Report

```bash
python runner_table_extraction.py --report
```

Report is generated at `output/table/extraction_report.json`.

---

## CLI Reference

```
python runner_table_extraction.py [OPTIONS]

Input Options:
  --file FILE          Extract single JSON file
  --input-dir DIR      Directory with JSON files (default: output/json)

Output Options:
  --output-dir DIR     Output directory (default: output/table)

Filtering Options:
  --no-summary         Exclude parent/summary tasks
  --no-milestones      Exclude milestone tasks

Report Options:
  --report             Generate extraction report
  --report-path PATH   Report file path

Other Options:
  --verbose            Enable debug logging
```

---

## Output Structure

```
output/table/
├── Miraya.csv
├── Aristocrat.csv
├── Horizon.csv
├── Reserve.csv
├── Avenue 11.csv
├── Zenith.csv
├── Tropical Isle.csv
├── Jardinia.csv
├── Sec. 44, Noida.csv
├── Ramaiah.csv
├── Woodscapes.csv
├── RGA 2.csv
├── BL Saha.csv
└── extraction_report.json
```

---

## CSV Columns

| Column | Description |
|--------|-------------|
| code | Task hierarchy code (outline_number) |
| title | Task name |
| tower | Tower identifier |
| floor | Floor identifier |
| main_category | Main work category |
| sub_category | Sub work category |
| trade_type | Trade/discipline type |
| slab_works | Slab classification |
| cost_plan_total | Total planned cost |
| start_date_plan | Planned start date |
| end_date_plan | Planned end date |
| start_date_actual | Actual start date |
| end_date_actual | Actual end date |
| start_date_sprint | Sprint start date |
| end_date_sprint | Sprint end date |
| progress | Percent complete (0-100) |

---

## Examples

### Quick Test

```bash
python runner_table_extraction.py --file output/json/Miraya.json
```

### Full Batch with Report

```bash
python runner_table_extraction.py --report --verbose
```

### Production Run (Leaf Tasks Only)

```bash
python runner_table_extraction.py \
  --no-summary \
  --no-milestones \
  --output-dir reports/tables \
  --report
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No JSON files found" | Wrong input directory | Check `--input-dir` path |
| Empty CSV | All tasks filtered | Check filter flags |
| Encoding errors | Non-UTF8 source | Re-run Stage 1 |

### Verify Output

```bash
# Check row count
wc -l output/table/Miraya.csv

# Preview first rows
head -5 output/table/Miraya.csv

# Verify columns
head -1 output/table/Miraya.csv | tr ',' '\n' | nl
```

---

## Next Steps

After Stage 2, CSV files can be:

1. Imported into Excel/Google Sheets
2. Loaded into BI tools (Tableau, Power BI)
3. Analyzed with pandas/Python

For dashboard data, see Stage 3: `docs/03-json-to-staging/`
