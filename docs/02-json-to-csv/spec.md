# Stage 2 Specification: JSON to CSV Extraction

**Document Version**: 1.0
**Status**: Production
**Last Updated**: 2025-12-16

---

## 1. Overview

### Purpose

Extract task data from Master JSON files into flat CSV format for analysis, reporting, and spreadsheet consumption.

### Scope

- **Input**: 12 JSON files from Stage 1 output (~110,000 tasks)
- **Output**: CSV files with 16 columns per task

### Use Cases

1. **Data Analysis**: Import into Excel/Google Sheets for ad-hoc analysis
2. **Reporting**: Generate project status reports
3. **Integration**: Feed data to external BI tools
4. **Backup**: Flat file archive of task data

---

## 2. User Stories

### US-001: Extract Task Data to CSV

**As a** project analyst
**I want to** export task data to CSV format
**So that** I can analyze it in spreadsheet tools

**Acceptance Criteria:**
- All specified columns extracted correctly
- Null values handled as empty strings
- UTF-8 encoding for international characters
- Standard CSV format (comma-delimited)

### US-002: Single File Extraction

**As a** data engineer
**I want to** extract a single project's data
**So that** I can test or update specific files

**Acceptance Criteria:**
- Accept single JSON file as input
- Output CSV with same project name
- Display extraction statistics

### US-003: Batch Extraction

**As a** operations manager
**I want to** extract all project files at once
**So that** I can update the entire dataset efficiently

**Acceptance Criteria:**
- Process all JSON files in directory
- Generate extraction report
- Handle errors gracefully per file

### US-004: Filter by Task Type

**As a** project planner
**I want to** exclude parent/summary tasks
**So that** I only see actionable work tasks

**Acceptance Criteria:**
- Option to exclude summary (parent) tasks
- Option to exclude milestone tasks
- Leaf tasks always included

### US-005: Generate Extraction Report

**As a** QA engineer
**I want** an extraction report
**So that** I can verify data completeness

**Acceptance Criteria:**
- Report includes row counts per project
- Report includes task type breakdown
- Report identifies any errors

---

## 3. Functional Requirements

### FR-001: Column Extraction

| ID | Requirement |
|----|-------------|
| FR-001.1 | Extract `outline_number` as `code` |
| FR-001.2 | Extract `name` as `title` |
| FR-001.3 | Extract `attributes.tower` as `tower` |
| FR-001.4 | Extract `attributes.floor` as `floor` |
| FR-001.5 | Extract `attributes.main_category` |
| FR-001.6 | Extract `attributes.sub_category` |
| FR-001.7 | Extract `attributes.trade_type` |
| FR-001.8 | Extract `attributes.slab_works` |
| FR-001.9 | Extract `cost_plan_total` |
| FR-001.10 | Extract all date fields (plan, actual, sprint) |
| FR-001.11 | Extract `progress.percent_complete` as `progress` |

### FR-002: Null Value Handling

| ID | Requirement |
|----|-------------|
| FR-002.1 | Convert `null` values to empty strings |
| FR-002.2 | Handle missing fields gracefully |
| FR-002.3 | Never output literal "null" string |

### FR-003: Task Type Filtering

| ID | Requirement |
|----|-------------|
| FR-003.1 | Support `--no-summary` to exclude parent tasks |
| FR-003.2 | Support `--no-milestones` to exclude milestones |
| FR-003.3 | Always include leaf tasks |

### FR-004: File Operations

| ID | Requirement |
|----|-------------|
| FR-004.1 | Create output directory if not exists |
| FR-004.2 | Overwrite existing CSV files |
| FR-004.3 | Use UTF-8 encoding |
| FR-004.4 | Use LF line endings |

---

## 4. Non-Functional Requirements

### NFR-001: Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001.1 | Single file extraction | < 5 seconds |
| NFR-001.2 | Batch extraction (13 files) | < 30 seconds |
| NFR-001.3 | Memory usage | < 500 MB |

### NFR-002: Compatibility

| ID | Requirement |
|----|-------------|
| NFR-002.1 | CSV loadable in Excel |
| NFR-002.2 | CSV loadable in Google Sheets |
| NFR-002.3 | CSV parseable by pandas |

### NFR-003: Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-003.1 | Data accuracy | 100% |
| NFR-003.2 | Row count match | Exact match to JSON |

---

## 5. Constraints

### Technical Constraints

1. **Dependencies**: Python standard library only (json, csv, pathlib)
2. **Input Format**: JSON files from Stage 1
3. **Output Format**: Standard CSV (RFC 4180)

### Business Constraints

1. **Column Order**: Fixed 16-column schema
2. **File Naming**: Match source JSON filename

---

## 6. Assumptions

1. Input JSON files are valid and complete
2. All tasks have `outline_number` field
3. Date fields are in YYYY-MM-DD format
4. Cost values are numeric (float)

---

## 7. Dependencies

### Upstream

- Stage 1: Master JSON files in `output/json/`

### Downstream

- External BI tools and spreadsheets
- Data analysis workflows

---

## 8. Success Criteria

- [ ] All 16 columns extracted correctly
- [ ] Null values handled as empty strings
- [ ] Single file and batch modes working
- [ ] Filtering options functional
- [ ] CSV files load in Excel/Sheets
- [ ] Extraction report generated
- [ ] All 13 projects processed successfully
