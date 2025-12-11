# Sprint vs AOP Schedule Gap Analysis - Miraya

**Generated:** 2025-12-11 09:25:24

## Executive Summary

This analysis compares the Sprint schedule against the AOP baseline schedule for the Miraya project.
Sprint schedules are tighter than AOP baselines - teams receive bonuses for meeting Sprint targets.

## Schedule Overview

### AOP Baseline
- **Project Start:** 2025-12-02T00:00:00
- **Project Finish:** 2031-09-17T17:00:00
- **Total Tasks:** 2849

### Sprint Schedule
- **Project Start:** 2025-12-03T00:00:00
- **Project Finish:** 2029-07-19T17:00:00
- **Total Tasks:** 2847

## Task Comparison

- **Tasks in Both Schedules:** 1444
- **Tasks Only in AOP:** 1405
- **Tasks Only in Sprint:** 1403
- **Tasks Analyzed (leaf tasks):** 1148

## Date Analysis

### Start Date Comparison

- **Earlier in Sprint:** 1109 tasks
- **Later in Sprint:** 39 tasks
- **Same Date:** 0 tasks
- **Average Difference:** -260.7 days

**Interpretation:** Negative = Sprint earlier than AOP, Positive = Sprint later than AOP

### Finish Date Comparison

- **Earlier in Sprint:** 1107 tasks
- **Later in Sprint:** 41 tasks
- **Same Date:** 0 tasks
- **Average Difference:** -259.4 days

## Top Tasks with Significant Differences

### Tasks Finishing Earlier in Sprint (Top 10)

| UID | Task Name | AOP Finish | Sprint Finish | Days Earlier |
|-----|-----------|------------|---------------|--------------|
| 2394 | Offer to possession | 2029-08-10 | 2025-06-08 | 1524 |
| 4326 | Offer to possession | 2029-07-30 | 2025-06-08 | 1513 |
| 2390 | Split AC Units installation | 2029-03-13 | 2025-05-22 | 1391 |
| 4322 | Split AC Units installation | 2029-03-02 | 2025-06-05 | 1366 |
| 2392 | Wooden Flooring | 2029-02-16 | 2025-05-27 | 1361 |
| 4324 | Wooden Flooring | 2029-02-05 | 2025-06-04 | 1342 |
| 2386 | Electrical Fixtures And Fittings installations | 2028-12-18 | 2025-05-28 | 1300 |
| 2388 | Final Coat Paint Internal | 2028-10-04 | 2025-05-24 | 1229 |
| 454 | Landscape | 2028-09-12 | 2025-05-06 | 1225 |
| 456 | Hardscape | 2028-09-12 | 2025-05-09 | 1222 |

### Tasks Finishing Later in Sprint (Top 10)

| UID | Task Name | AOP Finish | Sprint Finish | Days Later |
|-----|-----------|------------|---------------|------------|
| 1085 | Putty primer coat | 2025-11-04 | 2026-04-03 | 150 |
| 6177 | 14th Floor | 2026-10-09 | 2027-03-11 | 153 |
| 6185 | 18th Floor | 2026-12-21 | 2027-05-30 | 160 |
| 6181 | 16th Floor | 2026-10-23 | 2027-04-10 | 169 |
| 5390 | False Cieling panel fixing | 2026-04-21 | 2026-10-11 | 173 |
| 6189 | 20th Floor | 2027-01-04 | 2027-07-14 | 191 |
| 6183 | 17th Floor | 2026-10-30 | 2027-05-10 | 192 |
| 6199 | 25th Floor | 2027-02-08 | 2027-10-05 | 239 |
| 165 | Surface dressing & compaction for grade slab area | 2025-06-22 | 2026-05-11 | 323 |
| 169 | TC & TB | 2025-05-04 | 2026-05-31 | 392 |

## Key Findings

1. **Schedule Compression:** Sprint schedule shows earlier completion dates on average
2. **Task Coverage:** 50.7% of tasks are common between schedules
3. **Aspiration Target:** Sprint represents the incentivized target for team bonuses

## Recommendations for ETL Integration

1. **Add Sprint Schedule Layer:** Process sprint XMLs alongside AOP baselines
2. **Track Schedule Type:** Add `schedule_type` field ('aop' vs 'sprint') to differentiate
3. **Calculate Variance:** Store delta between AOP and Sprint dates as `sprint_variance_days`
4. **Dashboard Display:** Show both schedules with variance indicators for bonus tracking
5. **Data Structure:** Consider nested structure or separate sprint_dates object within tasks
