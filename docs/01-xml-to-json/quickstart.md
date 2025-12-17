# Stage 1 Quickstart: XML to JSON Conversion

**Document Version**: 1.0
**Last Updated**: 2025-12-16

---

## Prerequisites

- Python 3.10+
- Virtual environment (recommended)

```bash
cd etl-cco-dashboard
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

## Basic Usage

### Process All XML Files

```bash
python runner.py
```

This will:
1. Parse all XML files from `input/all-aop-baselines/`
2. Transform to JSON per `task_schema.json`
3. Apply all enrichments (zone, region, tower, floor)
4. Validate output
5. Write to `output/json/`

### Process Single File

```bash
python runner.py --file Miraya.xml
```

### Specify Input Directory

```bash
python runner.py --input-dir /path/to/xml/files
```

---

## Enrichment Options

### Default (All Enrichments)

```bash
python runner.py  # Zone, region, tower, floor all enabled
```

### Skip Specific Enrichments

```bash
# Skip zone/region enrichment
python runner.py --no-enrich-zone-region

# Skip tower/floor enrichment
python runner.py --no-enrich-tower-floor

# Skip all enrichment
python runner.py --no-enrich
```

### Enrich Existing JSON Outputs

```bash
# Re-enrich previously generated JSON files
python runner.py --enrich-only

# Enrich only zone/region
python runner.py --enrich-only --enrich-zone-region

# Enrich only tower/floor
python runner.py --enrich-only --enrich-tower-floor
```

---

## Sprint Integration

### Include Sprint Dates During Processing

```bash
python runner.py --sprint-dir input/all-sprint-schedules
```

### Enrich Existing Outputs with Sprint Dates

```bash
python runner.py --enrich-sprint --sprint-dir input/all-sprint-schedules
```

---

## Validation Modes

### Validate Only (No Processing)

```bash
python runner.py --validate-only
```

### Dry Run (Parse Without Saving)

```bash
python runner.py --dry-run
```

### Set QA Sample Size

```bash
python runner.py --sample-size 100  # Default is 100
```

---

## Output Structure

```
output/
├── json/
│   ├── Horizon.json
│   ├── Reserve.json
│   ├── Avenue 11.json
│   ├── Miraya.json
│   ├── Aristocrat.json
│   ├── Zenith.json
│   ├── Tropical Isle.json
│   ├── Jardinia.json
│   ├── Sec. 44, Noida.json
│   ├── Ramaiah.json
│   ├── Woodscapes.json
│   ├── RGA 2.json
│   └── BL Saha.json
├── table/
│   └── {project}.csv              # Stage 2 CSV output
├── reports/
│   ├── qa_report_{project}.json   # Stage 1 QA report
│   ├── summary_report.json        # Stage 1 summary (all projects)
│   ├── pipeline_report_{project}.json  # Combined pipeline report
│   └── pipeline_report_{project}.md    # Human-readable report
└── logs/
    └── etl_YYYYMMDD_HHMMSS.log
```

---

## CLI Reference

```
python runner.py [OPTIONS]

Input Options:
  --input-dir DIR         XML input directory (default: input/all-aop-baselines)
  --file FILENAME         Process single XML file

Output Options:
  --output-dir DIR        Output directory (default: output)

Processing Modes:
  --dry-run              Parse and transform without saving
  --validate-only        Run validation on existing output

Enrichment Control:
  --no-enrich            Skip all enrichment
  --no-enrich-zone-region  Skip zone/region enrichment
  --no-enrich-tower-floor  Skip tower/floor enrichment
  --enrich-only          Enrich existing JSON outputs (no XML processing)
  --enrich-zone-region   With --enrich-only: enrich zone/region only
  --enrich-tower-floor   With --enrich-only: enrich tower/floor only
  --enrich-trade-types   Include LLM-based trade type classification

Sprint Integration:
  --sprint-dir DIR       Directory containing Sprint XML files
  --enrich-sprint        Enrich existing outputs with Sprint dates

Validation:
  --sample-size N        QA sample size per file (default: 100)

Logging:
  --verbose              Enable debug logging
```

---

## Examples

### Full Pipeline (Recommended)

```bash
# Process all files with all enrichments and Sprint integration
python runner.py \
  --input-dir input/all-aop-baselines \
  --sprint-dir input/all-sprint-schedules \
  --enrich-trade-types
```

### Quick Test

```bash
# Process smallest file in dry-run mode
python runner.py --file Miraya.xml --dry-run
```

### Re-enrich Existing Data

```bash
# Add Sprint dates to existing JSON files
python runner.py --enrich-sprint --sprint-dir input/all-sprint-schedules

# Re-run tower/floor enrichment
python runner.py --enrich-only --enrich-tower-floor
```

### Production Run

```bash
# Full processing with verbose logging
python runner.py \
  --input-dir input/all-aop-baselines \
  --sprint-dir input/all-sprint-schedules \
  --sample-size 200 \
  --verbose
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "XML file not found" | Wrong input directory | Check `--input-dir` path |
| "No assignments found" | TimephasedData missing | Normal for some tasks |
| Memory error | Large file | Increase system memory |
| Low Sprint match rate | Outline numbers changed | Verify Sprint XML version |

### Checking Logs

```bash
# View latest log
tail -100 output/logs/etl_*.log

# Search for errors
grep -i error output/logs/etl_*.log
```

### Validating Output

```bash
# View QA report
cat output/reports/qa_report_Miraya.json | python -m json.tool

# Check summary
cat output/reports/summary_report.json | python -m json.tool
```

---

## Project Name Mapping

| XML Filename | Canonical Name |
|--------------|----------------|
| Azadnagar.xml | Horizon |
| Bigbull-Reserve.xml | Reserve |
| OneM.xml | Avenue 11 |
| Miraya.xml | Miraya |
| Aristocrat.xml | Aristocrat |
| Zenith.xml | Zenith |
| Tropical Isle 146.xml | Tropical Isle |
| Jardinia.xml | Jardinia |
| Riverine.xml | Sec. 44, Noida |
| Ramaiah.xml | Ramaiah |
| Woodscapes.xml | Woodscapes |
| RGA Land2.xml | RGA 2 |
| BLSaha.xml | BL Saha |

---

## Trade Type Enrichment (LLM-Based)

Trade type classification uses Gemini Flash 2.5 via OpenRouter API.

### API Key Setup

**Option 1: Environment Variable**
```bash
export OPENROUTER_API_KEY=your_api_key_here
python runner.py --enrich-trade-types
```

**Option 2: Command Line**
```bash
python runner.py --enrich-trade-types --openrouter-api-key your_api_key_here
```

**Option 3: .env File**
Create a `.env` file in the `etl-cco-dashboard` directory:
```
OPENROUTER_API_KEY=your_api_key_here
```

### Usage

```bash
# Single file with trade types
python runner.py --file Miraya.xml --enrich-trade-types

# All files with trade types
python runner.py --enrich-trade-types

# Full pipeline with all enrichments
python runner.py \
  --sprint-dir input/all-sprint-schedules \
  --enrich-trade-types
```

### Cost Estimate

- ~$0.002 per project (50-150 unique activities per project)
- Total cost for all 13 projects: ~$0.03

---

## Pipeline Reports

After running Stage 2, comprehensive pipeline reports are generated automatically. These combine results from Stage 1 (JSON) and Stage 2 (CSV) into a unified view.

### Viewing Reports

```bash
# View markdown report (human-readable)
cat output/reports/pipeline_report_Miraya.md

# View JSON report (machine-readable)
cat output/reports/pipeline_report_Miraya.json | python -m json.tool
```

### Report Contents

Each pipeline report includes:

| Section | Description |
|---------|-------------|
| Stage 1 Results | Task counts (total, parents, leaves, milestones) |
| Enrichment | Coverage rates for zone, tower, floor, trade types, sprint |
| Validation | Sample pass rate, validation issues |
| Stage 2 Results | CSV row counts |
| Output Files | File paths and sizes |

### Controlling Report Generation

```bash
# Generate reports (default behavior)
python runner_table_extraction.py --pipeline-report

# Skip report generation
python runner_table_extraction.py --no-pipeline-report
```

---

## Next Steps

After running Stage 1:

1. **Stage 2**: Extract tables → `python runner_table_extraction.py`
2. **Stage 3**: Generate staging → `python staging_generator.py`

See `docs/02-json-to-csv/` and `docs/03-json-to-staging/` for details.
