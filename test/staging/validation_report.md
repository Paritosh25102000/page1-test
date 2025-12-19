# Staging Data Validation Report

**Generated:** 2025-12-19T20:37:08.136716

## Summary

| Metric | Value |
|--------|-------|
| Total Checks | 410 |
| Passed | 410 |
| Failed | 0 |
| Warnings | 0 |
| Pass Rate | 100.0% |

## Results by Category

### ✅ Hierarchy Aggregation

- Passed: 36
- Failed: 0
- Warnings: 0

**Sample Checks:**

| Check | Status | Expected | Actual |
|-------|--------|----------|--------|
| ZONE→ALL fy plan costs | ✓ | 4.99T | 4.99T |
| ZONE→ALL fy actual costs | ✓ | 4.28T | 4.28T |
| ZONE→ALL quarter plan costs | ✓ | 1.71T | 1.71T |
| ZONE→ALL quarter actual costs | ✓ | 1.60T | 1.60T |
| ZONE→ALL month plan costs | ✓ | 1.15T | 1.15T |
| ... | | | +31 more |

### ✅ Time Slice Consistency

- Passed: 3
- Failed: 0
- Warnings: 0

**Sample Checks:**

| Check | Status | Expected | Actual |
|-------|--------|----------|--------|
| ALL FY series count | ✓ | 12 | 12 |
| ALL Quarter series count | ✓ | 12-15 weeks | 14 |
| ALL Month series count | ✓ | 9-12 weeks | 11 |

### ✅ Gauge Calculations

- Passed: 288
- Failed: 0
- Warnings: 0

**Sample Checks:**

| Check | Status | Expected | Actual |
|-------|--------|----------|--------|
| ALL aop fy achieved_pct | ✓ | 85.7% | 85.7% |
| ALL aop fy status_color | ✓ | amber | amber |
| ALL aop quarter achieved_pct | ✓ | 94.1% | 94.1% |
| ALL aop quarter status_color | ✓ | amber | amber |
| ALL aop month achieved_pct | ✓ | 98.8% | 98.8% |
| ... | | | +283 more |

### ✅ Cumulative Costs

- Passed: 72
- Failed: 0
- Warnings: 0

**Sample Checks:**

| Check | Status | Expected | Actual |
|-------|--------|----------|--------|
| ALL fy final cumulative plan | ✓ | 4.99T | 4.99T |
| ALL quarter final cumulative plan | ✓ | 1.71T | 1.71T |
| ALL month final cumulative plan | ✓ | 1.15T | 1.15T |
| ZONE_MZ fy final cumulative plan | ✓ | 1.89T | 1.89T |
| ZONE_MZ quarter final cumulative plan | ✓ | 615.57B | 615.57B |
| ... | | | +67 more |

### ✅ Matrix Bucket Consistency

- Passed: 5
- Failed: 0
- Warnings: 0

**Sample Checks:**

| Check | Status | Expected | Actual |
|-------|--------|----------|--------|
| ALL matrix bucket sum = total projects | ✓ | 13 | 13 |
| ZONE_MZ bucket sum = zone projects | ✓ | 3 | 3 |
| ZONE_NZ bucket sum = zone projects | ✓ | 6 | 6 |
| ZONE_SZ bucket sum = zone projects | ✓ | 3 | 3 |
| ZONE_WEZ bucket sum = zone projects | ✓ | 1 | 1 |

### ✅ Additional Cross-Checks

- Passed: 6
- Failed: 0
- Warnings: 0

**Sample Checks:**

| Check | Status | Expected | Actual |
|-------|--------|----------|--------|
| No negative costs | ✓ | 0 negative values | 0 negative values |
| Series dates in ascending order | ✓ | All ordered | 0 out of order |
| Achievement percentages in reasonable range (0-200%) | ✓ | All in range | 0 out of range |
| ALL fy gauge vs trend plan ratio | ✓ | 0.5-2.0 | 1.00 |
| ALL quarter gauge vs trend plan ratio | ✓ | 0.5-2.0 | 0.93 |
| ... | | | +1 more |

## Validation Rules

1. **Hierarchy Aggregation**: Sum of child nodes (PROJ→REG→ZONE→ALL) must match parent totals
2. **Time Slice Consistency**: FY has 12 months, Quarter ~13 weeks, Month ~10 weeks
3. **Gauge Calculations**: `achieved_pct = (actual / plan) * 100`, status colors match thresholds
4. **Cumulative Costs**: `cumm_plan[n] = sum(plan_cost[0:n+1])`
5. **Matrix Bucket Consistency**: Sum of bucket counts equals total projects
6. **Additional Checks**: Non-negative costs, date ordering, percentage bounds
