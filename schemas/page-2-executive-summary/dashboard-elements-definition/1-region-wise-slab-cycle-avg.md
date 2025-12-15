  
\---

\#\#\# Artifact 2: Region-wise Slab Cycle Avg  
The Top-Left Bar Chart.

\`\`\`markdown  
\# Dashboard Element Definition: Region-wise Slab Cycle Avg

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Average Slab Cycle by Region  
\* \*\*Element ID:\*\* \`PG2-WIDGET-01\`  
\* \*\*Dashboard Page:\*\* Page 2 (Slab Cycle Analysis)  
\* \*\*Element Type:\*\* Bar Chart

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Compare operational speed across different geographical regions.  
\* \*\*Key Questions Answered:\*\* "Is Pune constructing faster than Kolkata?" "Which region is dragging down the Zone's average?"  
\* \*\*Target Audience Action:\*\* Investigate regions with high average cycle times (\> 20 days for typical floors).

\#\# 3\. Metric Definition  
\* \*\*Primary Metric:\*\* \*\*Average Slab Cycle (Days)\*\*.  
    \*   Formula: \`Sum(Duration of all completed Slabs in Region) / Count(Completed Slabs in Region)\`.  
\* \*\*Grouping:\*\* By Region.  
\* \*\*Ordering:\*\* Descending order of Cycle Time (Slowest on left) OR defined geographical order.

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.dates.actual.duration\_days\`  
    \*   \`tasks.attributes.region\`  
    \*   \`tasks.attributes.slab\_works\` (For filtering)  
\* \*\*Filter Scope:\*\*  
    \*   Include only completed tasks representing a "Floor Cycle".  
    \*   Apply Global Filters (Time, Slab Type, Formwork).

\#\# 5\. Data Transformation Logic  
\* \*\*Identification of Slab Cycle:\*\*  
    \*   \*Assumption:\* The Master Data identifies specific summary tasks as the "Slab Cycle" node.  
    \*   Filter: Tasks where \`is\_summary\`=True AND \`attributes.main\_category\`="Civil Works- RCC" AND \`attributes.floor\` is not null.  
\* \*\*Aggregation:\*\*  
    \*   Group by \`region\`.  
    \*   Calculate Mean of \`actual.duration\_days\`.  
    \*   Round to nearest integer (e.g., 36 days).

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* Array of Objects.  
\* \*\*Structure:\*\*  
  \`\`\`json  
  \[  
    { "region": "Pune 1", "avg\_cycle": 36 },  
    { "region": "Kolkata", "avg\_cycle": 34 },  
    { "region": "NCR1", "avg\_cycle": 29 }  
  \]  
