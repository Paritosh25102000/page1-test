\#\#\# Artifact 2: Project Achievement Matrix (Physical)

\`\`\`markdown  
\# Dashboard Element Definition: Project Count Matrix (Sprint Physicals)

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Project Count Matrix (Physical Activity)  
\* \*\*Element ID:\*\* \`PG3-WIDGET-02\`  
\* \*\*Dashboard Page:\*\* Page 3 (Physical Progress)  
\* \*\*Element Type:\*\* Heatmap Table

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Quantify portfolio risk based on production targets.  
\* \*\*Key Questions Answered:\*\* "In this Quarter, how many projects missed their Sprint Physical targets (\<60%)?"  
\* \*\*Differentiation:\*\* Focuses specifically on the \*\*Sprint Plan\*\* (Accelerated Target) as the denominator.

\#\# 3\. Metric Definition  
\* \*\*Primary Metric:\*\* \*\*Sprint Achievement % (Period)\*\*.  
    \*   Formula: \`(Actual Floors in Time Window / Sprint Plan Floors in Time Window) \* 100\`.  
\* \*\*Buckets:\*\*  
    \*   \> 120%  
    \*   100-120%  
    \*   85-100%  
    \*   60-85%  
    \*   \< 60%  
\* \*\*Rows:\*\* Zone.

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.attributes.zone\`  
    \*   \`tasks.attributes.project\_name\`  
    \*   \`tasks.attributes.floor\`  
    \*   \`tasks.dates.sprint.end\`  
    \*   \`tasks.dates.actual.end\`

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Calculate Project Ratios (Per Mode):\*\*  
    \*   Iterate through all projects.  
    \*   Apply Time Window filter to Sprint Dates and Actual Dates.  
    \*   Calculate Ratio: \`Count(Actuals in Window) / Count(Sprint Plans in Window)\`.  
\* \*\*Step 2: Assign Buckets:\*\*  
    \*   If Ratio is N/A (No plan), exclude or bucket as "No Plan".  
    \*   Else, assign to \>120%, 100-120%, etc.  
\* \*\*Step 3: Aggregation:\*\*  
    \*   Group by Zone. Count projects per bucket.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* JSON Object (keyed by Time Mode).  
\* \*\*Structure:\*\*  
  \`\`\`json  
  {  
    "fy\_data": \[  
      {  
        "zone\_label": "MZ",  
        "buckets": {  
          "gt\_120": 2,  
          "100\_120": 4,  
          "85\_100": 1,  
          "60\_85": 3,  
          "lt\_60": 0  
        }  
      }  
    \],  
    "quarter\_data": \[ ... \]  
  }  
