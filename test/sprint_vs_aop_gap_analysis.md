# Sprint vs AOP Schedule Gap Analysis - Miraya

**Generated:** 2025-12-11 00:50:56

## Executive Summary

This analysis compares the Sprint schedule against the AOP baseline schedule for the Miraya project.
Sprint schedules are tighter than AOP baselines - teams receive bonuses for meeting Sprint targets.

## Schedule Overview

### AOP Baseline
- **Project Start:** None
- **Project Finish:** None
- **Total Tasks:** 0

### Sprint Schedule
- **Project Start:** None
- **Project Finish:** None
- **Total Tasks:** 0

## Task Comparison

- **Tasks in Both Schedules:** 0
- **Tasks Only in AOP:** 0
- **Tasks Only in Sprint:** 0
- **Tasks Analyzed (leaf tasks):** 0

## Date Analysis

### Start Date Comparison

- **Earlier in Sprint:** 0 tasks
- **Later in Sprint:** 0 tasks
- **Same Date:** 0 tasks
- **Average Difference:** 0.0 days

**Interpretation:** Negative = Sprint earlier than AOP, Positive = Sprint later than AOP

### Finish Date Comparison

- **Earlier in Sprint:** 0 tasks
- **Later in Sprint:** 0 tasks
- **Same Date:** 0 tasks
- **Average Difference:** 0.0 days

## Top Tasks with Significant Differences

### Tasks Finishing Earlier in Sprint (Top 10)

| UID | Task Name | AOP Finish | Sprint Finish | Days Earlier |
|-----|-----------|------------|---------------|--------------|

### Tasks Finishing Later in Sprint (Top 10)

| UID | Task Name | AOP Finish | Sprint Finish | Days Later |
|-----|-----------|------------|---------------|------------|

## Key Findings

1. **Schedule Compression:** Sprint schedule shows later completion dates on average
2. **Task Coverage:** 0.0% of tasks are common between schedules
3. **Aspiration Target:** Sprint represents the incentivized target for team bonuses

## Recommendations for ETL Integration

1. **Add Sprint Schedule Layer:** Process sprint XMLs alongside AOP baselines
2. **Track Schedule Type:** Add `schedule_type` field ('aop' vs 'sprint') to differentiate
3. **Calculate Variance:** Store delta between AOP and Sprint dates as `sprint_variance_days`
4. **Dashboard Display:** Show both schedules with variance indicators for bonus tracking
5. **Data Structure:** Consider nested structure or separate sprint_dates object within tasks
