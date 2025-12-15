\---

\#\#\# Artifact 2: Project Achievement Matrix (Physical)  
The Top-Right Heatmap.

\`\`\`markdown  
\# Dashboard Element Definition: Project Count based on Physical Achievement

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Project Count Matrix (Physical Activity)  
\* \*\*Element ID:\*\* \`PG3-WIDGET-02\`  
\* \*\*Dashboard Page:\*\* Page 3 (Physical Progress)  
\* \*\*Element Type:\*\* Heatmap Table

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Quantify portfolio risk based on production targets.  
\* \*\*Key Questions Answered:\*\* "How many projects are missing their Sprint targets?"  
\* \*\*Differentiation:\*\* unlike Page 1 (Cost), this focuses on \*\*Sprint Achievement\*\* (Tactical production).

\#\# 3\. Metric Definition  
\* \*\*Primary Metric:\*\* \*\*Sprint Achievement %\*\*.  
    \*   Formula: \`(Actual Floors Completed in Sprint / Planned Floors in Sprint) \* 100\`.  
\* \*\*Buckets:\*\*  
    \*   \> 120%  
    \*   100-120%  
    \*   85-100%  
    \*   60-85%  
    \*   \< 60%  
\* \*\*Rows:\*\* Zone.

\#\# 4\. Source Data Requirements  
\*   Same as Widget 01 (Sprint Plan vs Actual Counts).

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Project Level Calculation\*\*  
    \*   For each project: Calculate \`Sprint\_Floors\_Actual / Sprint\_Floors\_Plan\`.  
\* \*\*Step 2: Bucket & Count\*\*  
    \*   Assign project to bucket.  
    \*   Group by Zone and Count.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* CSV / Pandas DataFrame.  
\* \*\*Columns:\*\* \`Zone\`, \`\>120%\`, \`100-120%\`, etc.

\#\# 7\. Visualization & UI Behavior  
\* \*\*UI Type:\*\* Heatmap Table.  
\* \*\*Interaction:\*\* Drill-down to list projects in the bucket.  
