# Artifact 4: Project Achievement Matrix

## Dashboard Element Definition: No. of Projects based on YTD COC Achievement

## 1. General Meta-Information
* **Element Name:** Project Count Matrix by COC Achievement
* **Element ID:** `PG1-WIDGET-04`
* **Dashboard Page:** Page 1 (Executive Summary)
* **Element Type:** Heatmap Table

## 2. Business Context
* **Business Goal:** A portfolio health-check matrix that distributes projects into performance buckets.
* **Key Questions Answered:** "How many projects are critically failing (<60%)?" "Is the West Zone (WEZ) performing better than North Zone (NZ)?"
* **Target Audience Action:** The CCO looks for the column "<60%". If the number is > 0, they drill down to see *which* projects.

## 3. Metric Definition
* **Metric:** **YTD COC Achievement %** per Project.
    *   Formula: `Sum(Actual Cost YTD) / Sum(AOP Plan Cost YTD)`
* **Rows:** Zone (MZ, WEZ, SZ, NZ). *Note: If Global Filter selects a specific Zone, this table might filter to show Regions or just that single Zone row.*
* **Columns (Buckets):**
    *   > 120%
    *   100-120%
    *   85-100%
    *   60-85%
    *   < 60%

## 4. Source Data Requirements
* **Required JSON Objects:**
    *   `tasks.attributes.zone`
    *   `tasks.attributes.project_name`
    *   `tasks.cost_timeline.summary` (actual_cost_in_fy, plan_cost_in_fy)

## 5. Data Transformation Logic
* **Step 1: Aggregation per Project**
    *   Group all tasks by `project_name` (and `zone` attribute).
    *   Sum `actual_cost_in_fy` (YTD).
    *   Sum `plan_cost_in_fy` (YTD).
    *   Calculate Ratio: `Actual / Plan`.
* **Step 2: Bucket Assignment**
    *   Iterate through projects and assign a Bucket Label (e.g., "<60%") based on the Ratio.
* **Step 3: Pivot Table**
    *   Group by `Zone`.
    *   Count distinct `project_name` in each Bucket.

## 6. Staging Dataset Structure
* **Output Format:** CSV / Pandas DataFrame
* **Columns:**
    *   `Zone`
    *   `Bucket_GT_120` (Integer Count)
    *   `Bucket_100_120` (Integer Count)
    *   `Bucket_85_100` (Integer Count)
    *   `Bucket_60_85` (Integer Count)
    *   `Bucket_LT_60` (Integer Count)

## 7. Visualization & UI Behavior
* **Chart Type:** Table with Heatmap styling.
* **Drill-down:** Clicking a cell (e.g., "MZ | <60% : 2") triggers a popup list showing the names of those 2 projects.