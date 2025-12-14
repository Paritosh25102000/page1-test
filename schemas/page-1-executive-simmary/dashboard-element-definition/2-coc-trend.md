# Artifact 2: COC Trend (Cost of Construction)

## Dashboard Element Definition: COC Trend Analysis

## 1. General Meta-Information
* **Element Name:** COC Trend (Cost of Construction)
* **Element ID:** `PG1-WIDGET-01`
* **Dashboard Page:** Page 1 (Executive Summary)
* **Element Type:** Combo Chart (Bar + Line)

## 2. Business Context
* **Business Goal:** Visualize the planned vs. actual cash burn rate at the specific resolution relevant to the user (Macro vs. Tactical).
* **Key Questions Answered:** "Are we spending according to the AOP?" (FY Mode) or "Did we hit the production targets last week?" (Month Mode).
* **Target Audience Action:** Monitor the gap between the Blue Line (Cumm Actual) and Green Line (Cumm Plan).

## 3. Metric Definition
* **Primary Metrics:**
    *   **Period Cost (Bar):** Sum of cost for the specific bucket (Month or Week).
    *   **Cumulative Cost (Line):** Running total from the start of the selected Timeline View.
* **Dimensions:**
    *   **Plan:** Based on `cost_timeline.weekly_costs.plan`.
    *   **Actual:** Based on `cost_timeline.weekly_costs.actual`.
* **Time Context:** Dynamic based on `PG1-CTRL-01` selection (FY, Quarter, or Month).

## 4. Source Data Requirements
* **Required JSON Objects:**
    *   `tasks.cost_timeline.weekly_costs`
    *   `tasks.attributes` (For filtering by Zone/Region)
* **Filters:**
    *   Apply Global Filter (Zone/Region/Project).
    *   Exclude tasks with no cost data.

## 5. Data Transformation Logic
* **Step 1: Filter Data**
    *   Apply Zone/Region/Project filters.
* **Step 2: Aggregate by Week (Base Layer)**
    *   Sum `weekly_costs.plan.cost` and `weekly_costs.actual.cost` for all tasks, grouped by `week_start`.
    *   *Note:* Ensure aggregation respects the Schema's Monday-Sunday definition.
* **Step 3: Apply View Mode Logic**
    *   **If Mode = FY:**
        *   Map weeks to Months (Prorate logic: if a week splits across months, divide cost by 7 and allocate days).
        *   Sum costs by Month.
    *   **If Mode = Quarter OR Month:**
        *   Filter the Weekly Aggregated data to the specific start/end dates defined in `PG1-CTRL-01`.
        *   Keep resolution as Weekly.
* **Step 4: Calculate Cumulative**
    *   Calculate running total of the Plan and Actual columns within the filtered dataset.

## 6. Staging Dataset Structure
* **Output Format:** CSV / Pandas DataFrame
* **Columns:**
    *   `Period_Label` (e.g., "Apr-25" for FY, or "Wk-15" for Q/M)
    *   `Sort_Date` (Date format for sorting)
    *   `Plan_Cost` (Float)
    *   `Actual_Cost` (Float)
    *   `Cumm_Plan_Cost` (Float)
    *   `Cumm_Actual_Cost` (Float)

## 7. Visualization & UI Behavior
* **Chart Type:** Dual-Axis Combo.
    *   Bars: Period Cost.
    *   Lines: Cumulative Cost.
* **Dynamic Resolution:**
    *   FY Mode: X-Axis = Months (12 bars max).
    *   Qtr Mode: X-Axis = Weeks (13 bars max).
    *   Month Mode: X-Axis = Weeks (11 bars: 5 back, current, 5 forward).