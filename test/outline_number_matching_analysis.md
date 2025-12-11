# Outline Number Matching Analysis - Miraya

## Overview

- **Total AOP Leaf Tasks:** 2531
- **Total Sprint Leaf Tasks:** 2529

## Matching Strategy Comparison

| Strategy | Matches | Match Rate | Notes |
|----------|---------|------------|-------|
| **Outline Number Only** | 2517 | 99.4% | 10 name mismatches, 0 duplicates |
| **Name Only** | 265 | 10.5% | Already tested - 100% reliable |
| **Name + Outline (Composite)** | 2518 | 99.5% | Strictest matching |

## Outline Number Stability Analysis

For 265 tasks with matching names:

- **Outline Number Stable:** 265 (100.0%)
- **Outline Number Changed:** 0 (0.0%)

## Outline Number Reuse (Different Tasks)

Found 10 cases where same outline_number refers to different tasks:

| Outline | AOP Task | Sprint Task | AOP UID | Sprint UID |
|---------|----------|-------------|---------|------------|
| 1.1.4.2.3.1.24.13 | Aluminium door-window fixing | Putty primer coat | 3833 | 3812 |
| 1.1.4.2.3.1.24.7 | Internal Plaster | IPS flooring work | 3819 | 3797 |
| 1.1.4.2.3.1.24.12 | Electrical wiring work | Aluminium door-window fixing | 3831 | 3809 |
| 1.1.4.2.3.1.24.16 | Painting 1st coat | False Cieling panel fixing | 3840 | 3818 |
| 1.1.4.2.3.1.24.11 | Living dinning flooring | Electrical wiring work | 3828 | 3807 |
| 1.1.4.2.3.1.24.9 | Toilet dado work | Toilet flooring work | 3823 | 3802 |
| 1.1.4.2.3.1.24.10 | Toilet flooring work | Living dinning flooring | 3826 | 3804 |
| 1.1.4.2.3.1.24.8 | IPS flooring work | Toilet dado work | 3821 | 3799 |
| 1.1.4.2.3.1.24.15 | Prehung door fixing | Painting 1st coat | 3838 | 3816 |
| 1.1.4.2.3.1.24.14 | Putty primer coat | Prehung door fixing | 3836 | 3814 |

## Sample: Outline Number Matches (Same Outline, Same Name)

| Outline | Name | AOP UID | Sprint UID | AOP Finish | Sprint Finish |
|---------|------|---------|------------|------------|---------------|
| 1.1.4.2.3.1.4.13 | Putty primer coat | 3093 | 3057 | 2026-09-20 | 2026-03-30 |
| 1.1.4.1.3.1.29.4 | Internal Plumbing Works | 2073 | 2047 | 2027-09-01 | 2026-10-17 |
| 1.1.4.2.3.1.19.5 | Waterproofing | 3625 | 3603 | 2027-05-12 | 2026-08-14 |
| 1.1.4.1.3.1.23.12 | Aluminium door-window fixing | 1863 | 1837 | 2027-09-25 | 2027-01-14 |
| 1.1.3.1.1.1.2 | ATT | 191 | 177 | 2026-07-06 | 2025-10-26 |
| 1.1.4.3.2.1.5.1 | Reinforcement | 4474 | 4436 | 2026-05-24 | 2025-12-22 |
| 1.1.4.1.3.1.1.3 | Fire sprinkler pipe fixing | 1026 | 994 | 2026-07-12 | 2026-01-08 |
| 1.1.4.3.1.2.1.1 | Reinforcement | 4347 | 4320 | 2025-08-14 | 2025-06-05 |
| 1.1.4.3.3.1.24.12 | Aluminium door-window fixing | 5801 | 5761 | 2027-10-20 | 2027-01-22 |
| 1.1.2.1.2.1 | Excavation from 2m till 4m | 138 | 132 | 2025-03-20 | 2025-03-20 |
| 1.1.4.1.3.4.21 | 21st Floor | 2253 | 2227 | 2027-04-25 | 2026-05-25 |
| 1.1.4.1.3.4.31 | 31st Floor | 2273 | 2247 | 2027-07-04 | 2026-08-03 |
| 1.1.4.1.3.1.24.8 | Toilet dado work | 1891 | 1865 | 2027-08-19 | 2026-10-20 |
| 1.1.4.1.3.4.15 | 15th Floor | 2241 | 2215 | 2027-03-14 | 2026-04-13 |
| 1.1.4.1.5.3 | Final coat of painting | 2361 | 2335 | 2028-03-07 | 2027-04-23 |

## Recommendation

⚠️ **Name matching recommended, outline unreliable**

- Name matching: 10.5%
- Outline matching: 99.4%