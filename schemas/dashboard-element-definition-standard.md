### Dashboard Element Definition Standard (DEDS)

#### 1. General Meta-Information
*   **Element Name:** (e.g., "COC Trend Analysis", "Slab Cycle Bar Chart")
*   **Element ID:** (A unique code, e.g., `PG1-WIDGET-02`, for tracking in code)
*   **Dashboard Page:** (e.g., Page 1 - Executive Summary)
*   **Element Type:**
    *   *Visual Component* (Chart, Table, Gauge, KPI Card)
    *   *Control Component* (Global Filter, Toggle, Date Picker) - *Note: If this is a Control, sections 4 & 5 define what data populates the dropdown/toggle.*

#### 2. Business Context
*   **Business Goal:** What specific problem does this solve for the CCO? (e.g., "Identify cash flow bottlenecks by Zone.")
*   **Key Questions Answered:** What questions can the user answer by looking at this? (e.g., "Which region is consistently missing slab cycle targets?")
*   **Target Audience Action:** What should the CCO *do* based on this data? (e.g., "Drill down into the specific Project Manager performance.")

#### 3. Metric Definition
*   **Primary Metrics:** The core numbers being displayed (e.g., Cost of Construction (COC), Schedule Variance, Slab Cycle Days).
*   **Formula/Logic:** The mathematical definition in natural language.
    *   *Example:* `Slab Cycle = (Actual Finish Date of Floor N) - (Actual Finish Date of Floor N-1)`
*   **Dimensions/Groupings:** How is the data sliced? (e.g., By Zone, then by Region, then by Project).
*   **Time Context:** (e.g., YTD (Year-to-Date), Inception-to-Date, Forward-looking 3 months).

#### 4. Source Data Requirements (Mapping to JSON Schema)
*   **Required JSON Objects:** Which parts of the schema are needed?
    *   *Example:* `tasks.dates.actual`, `tasks.cost_timeline.weekly_costs`, `tasks.attributes.zone`
*   **Filters/Exclusions:** What raw data must be ignored?
    *   *Example:* "Exclude tasks where `is_summary = true` or `is_milestone = true`."
    *   *Example:* "Only include tasks where `attributes.trade_type = 'RCC'`."

#### 5. Data Transformation Logic (The ETL Instructions)
*   **Extraction & Cleaning:** Rules for handling nulls or missing dates (e.g., "If Actual Date is missing, exclude from calculation" vs "Use Projected Date").
*   **Aggregation Logic:** How to roll up the data.
    *   *Example:* "Sum `cost_timeline.weekly_costs.actual` grouped by `attributes.zone`."
*   **Derived Fields:** New data points created during processing.
    *   *Example:* Calculating "Gap Days" between two distinct tasks (e.g., Plaster vs. Blockwork).
*   **Cross-Reference Logic:** If the element requires comparing two different subsets of data (e.g., AOP Plan vs. Sprint Plan).

#### 6. Staging Dataset Structure (Target Output)
*   **Output Format:** The shape of the data required by the dashboard frontend (likely a flat CSV/JSON format optimized for the specific chart).
*   **Columns/Fields:**
    *   `Dimension_1` (e.g., Zone)
    *   `Dimension_2` (e.g., Month)
    *   `Metric_Value_1` (e.g., Planned Cost)
    *   `Metric_Value_2` (e.g., Actual Cost)

#### 7. Visualization & UI Behavior
*   **Chart Type:** (e.g., Stacked Bar, Line with Dual Axis, Heatmap Table).
*   **Sorting/Ranking:** (e.g., "Sort descending by Variance %").
*   **Color Logic:** (e.g., "Values < 85% = Red, 85-100% = Amber, >100% = Green").
*   **Interaction/Drill-down:** What happens when the user clicks? (e.g., "Clicking 'MZ' filters the 'Project List' table below to only show MZ projects").