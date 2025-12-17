# COO Dashboard ETL Glossary

**Version**: 1.0
**Last Updated**: 2025-12-16

---

## A

### Actual Dates
The dates when work actually started and finished on a task. For leaf tasks, derived from TimephasedData. For milestones, from ActualStart/ActualFinish fields.

### AOP (Annual Operating Plan)
The baseline schedule for the fiscal year. Contains planned dates and costs for all tasks.

### Attributes
Task metadata including project_name, zone, region, tower, floor, main_category, sub_category, trade_type, and slab_works.

---

## B

### Bucket
A performance category for the Project Achievement Matrix. Five buckets: >120%, 100-120%, 85-100%, 60-85%, <60%.

---

## C

### COO (Chief Operating Officer)
The primary user of the dashboard. Responsible for monitoring project portfolio performance.

### COC (Cost of Completion)
The cost trend showing planned vs actual cost burn over time.

### Cost Timeline
Weekly breakdown of planned and actual costs for a task within the financial year.

### Cumulative
Running total. In charts, cumulative lines show the accumulated cost from the start of the period.

---

## E

### Enrichment
The process of adding derived or looked-up attributes to tasks. Includes zone/region lookup, tower/floor extraction from hierarchy, and trade type classification.

---

## F

### Filter Key
A string identifying the current filter selection. Format: "ALL", "ZONE_{id}", "REG_{id}", or "PROJ_{id}".

### FY (Financial Year)
April 1 to March 31. For this pipeline: FY 2025-26 = 2025-04-01 to 2026-03-31.

---

## G

### Gauge
A semi-circle visualization showing achievement percentage. Used for AOP and Sprint KPIs.

---

## H

### Hierarchy
The organizational structure: Zone → Region → Project. Also refers to task hierarchy (WBS structure).

---

## I

### Incoming Cost
Cost incurred before the financial year start date. Calculated by prorating the total cost based on days before FY.

---

## L

### Leaf Task
A work task that has no children. Leaf tasks have attributes, progress, cost, and cost_timeline.

### Looking Glass
The "Month" time mode showing +/- 5 weeks from current date.

---

## M

### Master JSON
The primary output of Stage 1. Contains all task data enriched with attributes and cost timeline.

### Milestone
A zero-duration task marking a significant event. Has progress but no cost_timeline.

---

## N

### NodeData
The pre-aggregated widget data for a single filter selection. Contains kpi_gauges, coc_trend, and project_matrix.

---

## O

### Outline Number
Human-readable task hierarchy identifier (e.g., "1.2.3.4.5"). Used for Sprint schedule matching.

---

## P

### Parent Task
A summary task containing child tasks. Has null attributes, progress, and cost_timeline.

### Plan Dates
The scheduled/baseline dates for task start and finish.

### Pre-aggregation
Calculating all possible filter combinations upfront during staging generation, rather than at dashboard load time.

### Progress
Task completion status: percent_complete (0-100) and is_complete (boolean).

---

## R

### Region
Organizational subdivision within a zone. Examples: MZ1, NZ1, NZ2, SZ1, Kolkata.

---

## S

### Slab Works
Classification: Typical, Non-typical, or Non-slab. Relates to floor construction type.

### Sprint
An accelerated schedule for bonus-eligible targets. ~2 years more aggressive than AOP.

### Staging JSON
The pre-aggregated output for dashboard consumption. Contains controls and dashboard_data.

### Summary Task
See Parent Task.

---

## T

### Task
A unit of work in the project schedule. Three types: parent, leaf, milestone.

### Time Mode
The date range and resolution for charts. Three modes: FY (monthly), Quarter (weekly), Month (weekly).

### TimephasedData
XML element containing actual work data by time period. Type=2 indicates actual work.

### Trade Type
Work discipline classification. Examples: Reinforcement, Electrical, Blockwork, Plumbing.

Classified via LLM (Gemini Flash 2.5) using a 3-phase approach:
1. Extract unique activities from task hierarchy
2. Classify via LLM with cheat sheet reference
3. Map classifications back to individual tasks

**Prefixes**:
- No prefix: Tower/apartment work (e.g., Blockwork, Flooring)
- CA-: Common Area work (e.g., CA-Blockwork, CA-Flooring)
- Ext-: External work (e.g., Ext-Plaster, Ext-Electrical)

### Trade Type Cheat Sheet
Reference document (`trade-type-cheat-sheet.md`) containing 81 activity-to-trade-type mappings across 42 unique trade types, used by the LLM for consistent classification.

---

## U

### UID
Unique identifier from XML source (Task/UID). Unique within each project file.

---

## W

### WBS (Work Breakdown Structure)
Hierarchical code identifying task position (e.g., "37300.37500.51900"). Derived from XML WBS field.

### Weekly Costs
Array of cost entries for each week within the financial year. Contains plan and actual costs.

---

## Z

### Zone
Top-level organizational region. Values: MZ (Maharashtra), NZ (North), SZ (South), WEZ (West & East).

---

## Abbreviations

| Abbreviation | Full Form |
|--------------|-----------|
| AOP | Annual Operating Plan |
| COO | Chief Operating Officer |
| COC | Cost of Completion |
| FY | Financial Year |
| JSON | JavaScript Object Notation |
| KPI | Key Performance Indicator |
| MEP | Mechanical, Electrical, Plumbing |
| RCC | Reinforced Cement Concrete |
| UID | Unique Identifier |
| WBS | Work Breakdown Structure |
| XML | Extensible Markup Language |
| YTD | Year to Date |

---

## Zone Codes

| Code | Zone Name |
|------|-----------|
| MZ | Maharashtra Zone |
| NZ | North Zone |
| SZ | South Zone |
| WEZ | West & East Zone |

---

## Region Codes

| Code | Region Name |
|------|-------------|
| MZ1 | Maharashtra Region 1 |
| NZ1 | North Region 1 |
| NZ2 | North Region 2 |
| SZ1 | South Region 1 |
| SZ2 | South Region 2 |
| Kolkata | Kolkata Region |

---

## Color Codes

### Gauge Status

| Color | Range | Meaning |
|-------|-------|---------|
| Red | < 85% | Critical - significantly behind |
| Amber | 85-95% | Warning - slightly behind |
| Green | > 95% | On track or ahead |

### Matrix Buckets

| Bucket | Color | Meaning |
|--------|-------|---------|
| > 120% | Light green | Over-performing |
| 100-120% | Green | On track |
| 85-100% | Amber | Acceptable |
| 60-85% | Orange | Needs attention |
| < 60% | Red | Critical |
