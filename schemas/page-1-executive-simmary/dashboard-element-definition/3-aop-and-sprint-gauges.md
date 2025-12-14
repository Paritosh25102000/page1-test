# Artifact 3: AOP & Sprint Gauges

## Dashboard Element Definition: AOP & Sprint Achievement Gauges

## 1. General Meta-Information
* **Element Name:** AOP / Sprint Performance Gauges
* **Element ID:** `PG1-WIDGET-03`
* **Dashboard Page:** Page 1 (Executive Summary)
* **Element Type:** Gauge / Donut Chart

## 2. Business Context
* **Business Goal:** Compare long-term stability (AOP) against short-term acceleration/bonus targets (Sprint).
* **Key Questions Answered:** "Are we on track for the year?" (AOP) vs "Are we meeting the accelerated 'Squeezed AOP' targets?" (Sprint).
* **Target Audience Action:** High Sprint Achievement + Low AOP Achievement = Recovery is working. Low Sprint Achievement = Immediate intervention needed.

## 3. Metric Definition
* **Metric 1: AOP Achievement %**
    *   Formula: `(Total Actual Cost YTD / Total AOP Plan Cost YTD) * 100`
    *   Context: Always considers the Financial Year YTD, regardless of the "Timeline" filter.
* **Metric 2: Sprint Achievement %**
    *   Definition: Achievement against the "Squeezed" schedule.
    *   Formula: `(Total Actual Cost during active Sprint / Total Plan Cost derived from Sprint Dates) * 100`
    *   *Note:* "Plan Cost derived from Sprint Dates" assumes the task's total value is now spread over the shorter `dates.sprint` duration.

## 4. Source Data Requirements
* **Required JSON Objects:**
    *   `tasks.cost_timeline.summary` (For AOP totals)
    *   `tasks.dates.sprint` (To identify if a task is in a sprint and its duration)
    *   `tasks.cost_plan_total`
    *   `tasks.attributes` (For Global Filtering)

## 5. Data Transformation Logic
* **Filter:** Apply Global Filters (Zone/Region/Project) to all calculations.
* **AOP Calculation:**
    *   Sum `cost_timeline.summary.actual_cost_in_fy` / Sum `cost_timeline.summary.plan_cost_in_fy` (YTD basis).
* **Sprint Calculation:**
    *   **Filter Scope:** Select only tasks where `dates.sprint.start` is not null.
    *   **Sprint Plan Cost:** For each task, calculate daily burn rate: `cost_plan_total / dates.sprint.duration_days`. Multiply by `days_elapsed_in_sprint`.
    *   **Sprint Actual Cost:** Sum `cost_timeline.weekly_costs.actual` specifically for weeks falling within the sprint window.
    *   **Ratio:** Total Sprint Actuals / Total Sprint Plan.

## 6. Staging Dataset Structure
* **Output Format:** JSON Object
* **Structure:**
  ```json
  {
    "AOP_Gauge": {
      "value_percent": 87.5,
      "status_color": "Amber"
    },
    "Sprint_Gauge": {
      "value_percent": 92.0,
      "status_color": "Green"
    }
  }

## 7. Visualization & UI Behavior
* **Chart Type:** Semi-Circle Gauge.
* **Thresholds:**

* < 85%: Red
* 85-95%: Amber
* 95%: Green
