\#\#\# Artifact 4: Detailed Slab Matrix

\`\`\`markdown  
\# Dashboard Element Definition: Slab Cycle Frequency Matrix

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Detailed Slab Cycle Matrix  
\* \*\*Element ID:\*\* \`PG2-WIDGET-03\`  
\* \*\*Dashboard Page:\*\* Page 2 (Slab Cycle Analysis)  
\* \*\*Element Type:\*\* Heatmap Table

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Identify consistency and variance in cycle times.  
\* \*\*Key Questions Answered:\*\* "In this Quarter, how many slabs took \>30 days?" "Are the outliers coming from a specific project?"

\#\# 3\. Metric Definition  
\* \*\*Rows:\*\* Hierarchy (Zone \-\> Region \-\> Project).  
\* \*\*Summary Columns:\*\* Total Slabs, Avg Cycle.  
\* \*\*Bucket Columns:\*\* Count of slabs falling into duration buckets (Upto 7, 7-10, 11-14, 15-20, 21-25, 26-30, \>30 Days).  
\* \*\*Time Context:\*\* Data restricted to the selected Time Mode.

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.dates.actual.duration\_days\`  
    \*   \`tasks.dates.actual.end\` (Time Filter)  
    \*   \`tasks.attributes\` (Zone/Region/Project)

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Time Filtering:\*\*  
    \*   Exclude any task where \`dates.actual.end\` is outside the selected Time Mode range.  
\* \*\*Step 2: Bucketing:\*\*  
    \*   For each valid task, check \`duration\_days\`:  
        \*   If \<= 7 \-\> Bucket "upto\_7".  
        \*   If \> 7 AND \<= 10 \-\> Bucket "7\_10".  
        \*   ...etc.  
\* \*\*Step 3: Aggregation:\*\*  
    \*   Group by Project. Sum counts per bucket. Calculate weighted average duration.  
    \*   Roll up Project totals to Region and Zone levels.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* JSON Object (keyed by Time Mode).  
\* \*\*Structure:\*\*  
  \`\`\`json  
  {  
    "fy\_data": \[  
      {  
        "row\_id": "PROJ\_123",  
        "name": "Tropical Isle",  
        "total\_slabs": 45,  
        "avg\_cycle": 12,  
        "buckets": { "upto\_7": 0, "7\_10": 15, "gt\_30": 0 }  
      }  
    \],  
    "quarter\_data": \[ ... \]  
  }  
