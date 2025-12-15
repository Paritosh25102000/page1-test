# Dashboard Element Definition: Global Filter & Timeline Panel

## 1. General Meta-Information
* **Element Name:** Global Dashboard Filters & Time Mode
* **Element ID:** `PG1-CTRL-01`
* **Dashboard Page:** Page 1 (Executive Summary)
* **Element Type:** Control Component (Dropdowns & Mode Switcher)

## 2. Business Context
* **Business Goal:** Allow the CCO to toggle between strategic long-term views (Financial Year) and tactical short-term views (Quarterly/Monthly looking glass), while filtering the organizational hierarchy.
* **Key Questions Answered:** N/A (Control Element).
* **Target Audience Action:** Switch from "FY View" (Macro trends) to "Monthly View" (Immediate operational bottlenecks).

## 3. Metric Definition
* **Hierarchy Inputs:**
    *   **Zone:** Top-level filter.
    *   **Region:** Filter based on Zone.
    *   **Project:** Filter based on Region.
* **Timeline Mode Inputs:**
    *   **FY (Default):** Current Financial Year (e.g., Apr 1, 2025 – Mar 31, 2026). Resolution: **Monthly**.
    *   **Quarter:** Current Calendar Quarter (e.g., Oct 1 – Dec 31). Resolution: **Weekly**.
    *   **Month (Looking Glass):** Dynamic range: Current Date minus 5 weeks to Current Date plus 5 weeks. Resolution: **Weekly**.

## 4. Source Data Requirements
* **Required JSON Objects:**
    *   `tasks.attributes.zone`
    *   `tasks.attributes.region`
    *   `tasks.attributes.project_name`
    *   `tasks.cost_timeline.fy_period` (To establish FY boundaries)

## 5. Data Transformation Logic
* **Hierarchy Logic:**
    *   Extract unique `Zone` -> `Region` -> `Project` tree.
* **Time Context Logic:**
    *   *FY Boundaries:* Hardcoded to 2025-04-01 to 2026-03-31 (based on schema `fy_period`).
    *   *Quarter Boundaries:* Calculate current date's quarter start/end.
    *   *Looking Glass Boundaries:* Calculate `Today - 35 days` (Start) and `Today + 35 days` (End).

## 6. Staging Dataset Structure
* **Output Format:** JSON Dictionary (Configuration Object)
* **Structure:**
  ```json
  {
    "filters": {
      "MZ": { "MZ1": ["Project A"], "Kolkata": ["Project B"] },
      "SZ": { "SZ1": ["Project C"] }
    },
    "time_modes": {
      "FY": { "start": "2025-04-01", "end": "2026-03-31", "granularity": "month" },
      "Quarter": { "start": "2025-10-01", "end": "2025-12-31", "granularity": "week" },
      "Month": { "start": "2025-11-10", "end": "2026-01-19", "granularity": "week" }
    }
  }

## 7. Visualization & UI Behavior
* **UI Type:** Cascading Dropdowns + 3-State Toggle Switch (FY / Qtr / Month).
* **Interaction:** Changing the "Time Mode" triggers a re-aggregation of the COC Trend chart (switching between Monthly sums and Weekly sums).