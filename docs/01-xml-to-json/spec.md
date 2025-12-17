# Stage 1 Specification: XML to JSON Conversion

**Document Version**: 1.0
**Status**: Production
**Last Updated**: 2025-12-16

---

## 1. Overview

### Purpose

Transform Asta Powerproject XML schedule files into structured JSON format suitable for downstream processing (CSV extraction and dashboard staging).

### Scope

- **Input**: 13 XML files (~171 MB, ~110,000 tasks)
- **Output**: JSON files conforming to `task_schema.json`
- **Enrichment**: Zone, region, tower, floor, and trade type attributes

### Source Projects

| Project | XML File | Tasks (approx) |
|---------|----------|----------------|
| Horizon | Azadnagar.xml | 8,500 |
| Reserve | Bigbull-Reserve.xml | 9,200 |
| Avenue 11 | OneM.xml | 8,800 |
| Miraya | Miraya.xml | 2,849 |
| Aristocrat | Aristocrat.xml | 7,500 |
| Zenith | Zenith.xml | 6,800 |
| Tropical Isle | Tropical Isle 146.xml | 5,400 |
| Jardinia | Jardinia.xml | 6,200 |
| Sec. 44, Noida | Riverine.xml | 4,800 |
| Ramaiah | Ramaiah.xml | 7,100 |
| Woodscapes | Woodscapes.xml | 23,494 |
| RGA 2 | RGA Land2.xml | 8,900 |
| BL Saha | BLSaha.xml | 4,200 |

---

## 2. User Stories

### US-001: Parse XML Schedule Files

**As a** data engineer
**I want to** parse Asta Powerproject XML files
**So that** I can extract task data for transformation

**Acceptance Criteria:**
- Parse all 13 XML files without errors
- Handle XML namespace correctly
- Extract Tasks and Assignments elements
- Support streaming for large files (>20MB)

### US-002: Transform Task Data

**As a** data engineer
**I want to** transform XML task data to JSON schema
**So that** downstream systems can consume standardized data

**Acceptance Criteria:**
- Map all XML fields per `xml_to_json_mapping.json`
- Convert durations from ISO 8601 to days
- Classify tasks as parent/leaf/milestone
- Handle null values appropriately

### US-003: Calculate Cost Timeline

**As a** dashboard developer
**I want to** have weekly cost breakdown for FY 2025-26
**So that** I can visualize cost burn rates

**Acceptance Criteria:**
- Calculate plan costs from task start/end and total cost
- Calculate actual costs from actual dates (if complete)
- Generate weekly entries (Monday-Sunday)
- Track incoming costs before FY start

### US-004: Derive Actual Dates

**As a** project analyst
**I want** actual dates derived from TimephasedData
**So that** I see true work dates, not rolled-up summaries

**Acceptance Criteria:**
- Extract actual start from earliest TimephasedData Type=2
- Extract actual end from latest TimephasedData Type=2
- Fall back to Task-level ActualStart/ActualFinish for milestones
- Handle tasks with no actual work (null dates)

### US-005: Enrich Zone/Region Attributes

**As a** COO
**I want** tasks tagged with zone and region
**So that** I can filter by organizational hierarchy

**Acceptance Criteria:**
- Map XML filename to canonical project name
- Lookup zone/region from master mapping
- Apply to all tasks in project
- Store canonical name in `attributes.project_name`

### US-006: Enrich Tower/Floor Attributes

**As a** project manager
**I want** tasks tagged with tower and floor
**So that** I can filter by physical location

**Acceptance Criteria:**
- Extract tower from parent task hierarchy
- Extract floor from parent task hierarchy
- Normalize basement values (B1 → Basement 1)
- Apply only to leaf tasks

### US-007: Enrich Trade Types

**As a** data analyst
**I want** tasks categorized by trade type
**So that** I can analyze work by discipline

**Acceptance Criteria:**
- Classify tasks by main_category, sub_category, trade_type, slab_works
- Use LLM (Gemini Flash 2.5 via OpenRouter) for classification
- Extract unique activities per project (~50-150 per project)
- Detect context type (tower vs common_area vs external)
- Reference trade-type-cheat-sheet.md for classification rules
- Support ~30 trade types with CA- (Common Area) prefixes
- Achieve >85% coverage on leaf tasks
- Handle edge cases with context-aware classification

### US-008: Validate Output

**As a** data engineer
**I want** validation against source XML
**So that** I can ensure data integrity

**Acceptance Criteria:**
- Validate against JSON schema
- Sample compare output to source XML
- Report field coverage statistics
- Generate QA reports per project

### US-009: Enrich Sprint Dates

**As a** project planner
**I want** Sprint schedule dates integrated
**So that** I can compare AOP vs Sprint timelines

**Acceptance Criteria:**
- Parse separate Sprint XML files
- Match by outline_number (99.5% stable)
- Populate `dates.sprint` object
- Report match rate statistics

---

## 3. Functional Requirements

### FR-001: XML Parsing

| ID | Requirement |
|----|-------------|
| FR-001.1 | Parse XML files using iterparse for memory efficiency |
| FR-001.2 | Handle namespace `{http://schemas.microsoft.com/project}` |
| FR-001.3 | Extract all Task elements with required fields |
| FR-001.4 | Extract Assignment elements with TimephasedData |
| FR-001.5 | Build TaskUID → Assignments mapping |

### FR-002: Field Transformation

| ID | Requirement |
|----|-------------|
| FR-002.1 | Convert ISO 8601 duration (PT{H}H0M0S) to days |
| FR-002.2 | Extract date portion from datetime (T truncation) |
| FR-002.3 | Parse boolean from string ("1"/"0") |
| FR-002.4 | Derive parent_wbs by removing last segment |
| FR-002.5 | Handle null/missing values per schema |

### FR-003: Task Classification

| ID | Requirement |
|----|-------------|
| FR-003.1 | Classify as "parent" if is_summary == true |
| FR-003.2 | Classify as "milestone" if is_milestone == true |
| FR-003.3 | Classify as "leaf" if neither parent nor milestone |
| FR-003.4 | Set appropriate null fields per task type |

### FR-004: Cost Timeline

| ID | Requirement |
|----|-------------|
| FR-004.1 | FY period: 2025-04-01 to 2026-03-31 |
| FR-004.2 | Calculate plan rate: cost_total / duration_days |
| FR-004.3 | Calculate actual rate based on completion status |
| FR-004.4 | Generate weekly entries (Monday-Sunday) |
| FR-004.5 | Track incoming cost before FY start |
| FR-004.6 | Maintain accumulated totals |

### FR-005: Attribute Enrichment

| ID | Requirement |
|----|-------------|
| FR-005.1 | Lookup zone/region by project name |
| FR-005.2 | Extract tower from parent hierarchy |
| FR-005.3 | Extract floor from parent hierarchy |
| FR-005.4 | Normalize basement values |

### FR-005A: Trade Type Enrichment (LLM-Based)

| ID | Requirement |
|----|-------------|
| FR-005A.1 | Extract unique activities from task hierarchy per project |
| FR-005A.2 | Detect spatial leaves (Floor X, Tower Y) and traverse to parent for activity name |
| FR-005A.3 | Determine context type: tower, common_area, external, infrastructure |
| FR-005A.4 | Classify activities via LLM (Gemini Flash 2.5) with cheat sheet reference |
| FR-005A.5 | Validate classifications against trade-type-cheat-sheet.md |
| FR-005A.6 | Map classifications back to individual tasks by activity + context |
| FR-005A.7 | Populate main_category, sub_category, trade_type, slab_works attributes |
| FR-005A.8 | Handle CA- (Common Area) prefix for common area activities |

### FR-006: Sprint Integration

| ID | Requirement |
|----|-------------|
| FR-006.1 | Parse Sprint XML with existing parser |
| FR-006.2 | Match tasks by outline_number |
| FR-006.3 | Populate dates.sprint object |
| FR-006.4 | Handle unmatched tasks (leave sprint null) |

### FR-007: Validation

| ID | Requirement |
|----|-------------|
| FR-007.1 | Validate against JSON schema |
| FR-007.2 | Sample compare to source XML |
| FR-007.3 | Generate QA report per project |
| FR-007.4 | Calculate field coverage statistics |

---

## 4. Non-Functional Requirements

### NFR-001: Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001.1 | Process single file | < 60 seconds |
| NFR-001.2 | Process all 13 files | < 15 minutes |
| NFR-001.3 | Memory usage | < 2 GB peak |

### NFR-002: Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-002.1 | Schema validation pass rate | 100% |
| NFR-002.2 | Sample validation pass rate | > 98% |
| NFR-002.3 | No data loss during transformation | 100% |

### NFR-003: Maintainability

| ID | Requirement |
|----|-------------|
| NFR-003.1 | Modular code structure |
| NFR-003.2 | Logging at INFO and DEBUG levels |
| NFR-003.3 | Configuration via mapping files |

---

## 5. Constraints

### Technical Constraints

1. **XML Format**: Asta Powerproject export format (MS Project compatible)
2. **Python Version**: 3.10+
3. **Memory**: Streaming required for files > 20MB
4. **Dependencies**: Minimal external dependencies

### Business Constraints

1. **FY Period**: Fixed at 2025-04-01 to 2026-03-31
2. **Project List**: Fixed 13 projects
3. **Attribute Values**: Constrained to schema enums

---

## 6. Assumptions

1. XML files are valid MS Project XML exports
2. Task UIDs are unique within each file
3. outline_number is stable across schedule versions
4. TimephasedData Type=2 represents actual work
5. Cost is linearly distributed over duration

---

## 7. Dependencies

### Upstream

- XML files from Asta Powerproject exports
- Sprint XML files for sprint date integration
- Zone/Region master data mapping

### Downstream

- Stage 2: JSON to CSV extraction
- Stage 3: JSON to Staging transformation

---

## 8. Success Criteria

- [ ] All 13 XML files processed without errors
- [ ] 100% schema validation pass rate
- [ ] >98% sample validation pass rate
- [ ] Zone/region enriched for all projects
- [ ] Tower/floor enriched for >80% of leaf tasks
- [ ] Trade types enriched for >85% of leaf tasks
- [ ] Sprint dates matched for >40% of tasks
- [ ] QA reports generated for all projects
