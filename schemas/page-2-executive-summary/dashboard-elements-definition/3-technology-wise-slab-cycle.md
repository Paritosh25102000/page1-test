\#\#\# Artifact 3: Technology-wise Slab Cycle

\`\`\`markdown  
\# Dashboard Element Definition: Technology-wise Slab Cycle Avg & No of Slabs

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Tech Wise Performance  
\* \*\*Element ID:\*\* \`PG2-WIDGET-02\`  
\* \*\*Dashboard Page:\*\* Page 2 (Slab Cycle Analysis)  
\* \*\*Element Type:\*\* Combo Chart (Bar \+ Line)

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Assess the speed and volume of production based on construction methodology (Aluform vs Conventional) within the selected timeframe.  
\* \*\*Key Questions Answered:\*\* "How many slabs did we cast using Aluform this Quarter?" "Is the Aluform cycle time holding steady at 15 days in the recent Month view?"

\#\# 3\. Metric Definition  
\* \*\*Metric 1 (Bar):\*\* \*\*No of Slabs\*\*.  
    \*   Count of slabs completed within the Time Window.  
\* \*\*Metric 2 (Line):\*\* \*\*Average Slab Cycle\*\*.  
    \*   Mean duration of slabs completed within the Time Window.  
\* \*\*Dimension (X-Axis):\*\* Technology Category (derived from Trade Type \+ Slab Type).

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.attributes.trade\_type\`  
    \*   \`tasks.attributes.slab\_works\`  
    \*   \`tasks.dates.actual.end\` (Time Window Filter)  
    \*   \`tasks.dates.actual.duration\_days\` (Metric Calculation)

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Categorization:\*\*  
    \*   Create "Technology Label":  
        \*   If \`trade\_type\` contains "AL" AND \`slab\_works\`="Typical" \-\> "Aluform Typical".  
        \*   If \`trade\_type\` contains "Conventional" \-\> "Conventional".  
        \*   (Add other mappings as found in data).  
\* \*\*Step 2: Time Filtering:\*\*  
    \*   Apply FY / Quarter / Month date ranges to \`dates.actual.end\`.  
\* \*\*Step 3: Aggregation:\*\*  
    \*   Group by "Technology Label".  
    \*   Count distinct tasks (Slab Count).  
    \*   Average \`duration\_days\`.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* JSON Object (keyed by Time Mode).  
\* \*\*Structure:\*\*  
  \`\`\`json  
  {  
    "fy\_data": \[  
      { "tech": "Aluform Typical", "count": 243, "avg\_cycle": 16 },  
      { "tech": "Conventional", "count": 17, "avg\_cycle": 31 }  
    \],  
    "quarter\_data": \[  
      { "tech": "Aluform Typical", "count": 60, "avg\_cycle": 15 },  
      { "tech": "Conventional", "count": 4, "avg\_cycle": 30 }  
    \],  
    "month\_data": \[  
      { "tech": "Aluform Typical", "count": 20, "avg\_cycle": 14 },  
      { "tech": "Conventional", "count": 1, "avg\_cycle": 28 }  
    \]  
  }

