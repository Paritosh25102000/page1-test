\#\#\# Artifact 2: Region-wise Slab Cycle Avg

\`\`\`markdown  
\# Dashboard Element Definition: Region-wise Slab Cycle Avg

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Average Slab Cycle by Region  
\* \*\*Element ID:\*\* \`PG2-WIDGET-01\`  
\* \*\*Dashboard Page:\*\* Page 2 (Slab Cycle Analysis)  
\* \*\*Element Type:\*\* Bar Chart

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Compare operational speed across regions within the selected time window.  
\* \*\*Key Questions Answered:\*\* "In the current quarter, which region is the slowest?" "Has the West Zone improved its average in the last month compared to the FY average?"  
\* \*\*Target Audience Action:\*\* Identify regions exceeding the 15-day (Aluform) or 25-day (Conventional) cycle benchmarks.

\#\# 3\. Metric Definition  
\* \*\*Primary Metric:\*\* \*\*Average Slab Cycle (Days)\*\*.  
    \*   Formula: \`Sum(Actual Duration of Slabs Completed in Time Window) / Count(Slabs Completed in Time Window)\`.  
\* \*\*Grouping:\*\* By Region.  
\* \*\*Time Context:\*\* Dynamic based on \`PG2-CTRL-01\` selection (FY / Quarter / Month).

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.dates.actual.end\` (To filter by Time Window)  
    \*   \`tasks.dates.actual.duration\_days\` (To calculate average)  
    \*   \`tasks.attributes.region\` (For grouping)  
    \*   \`tasks.attributes.slab\_works\` (For Slab Type filter)  
    \*   \`tasks.attributes.trade\_type\` (For Formwork filter)  
    \*   \`tasks.attributes.main\_category\` (Must be "Civil Works- RCC")

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Filtering:\*\*  
    \*   Filter by \`attributes.main\_category\` \== "Civil Works- RCC".  
    \*   Filter by \`attributes.slab\_works\` (Typical/Non-typical based on control).  
    \*   Filter by \`attributes.trade\_type\` (Formwork based on control).  
\* \*\*Step 2: Time Window Application:\*\*  
    \*   \*\*FY Mode:\*\* Include tasks where \`dates.actual.end\` is between Apr 1, 2025 and Mar 31, 2026\.  
    \*   \*\*Quarter Mode:\*\* Include tasks where \`dates.actual.end\` is within current quarter dates.  
    \*   \*\*Month Mode:\*\* Include tasks where \`dates.actual.end\` is within \+/- 5 weeks of today.  
\* \*\*Step 3: Aggregation:\*\*  
    \*   Group valid tasks by \`region\`.  
    \*   Calculate Mean \`duration\_days\`.  
    \*   Round to nearest whole number.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* JSON Object (pre-calculated for all time modes).  
\* \*\*Structure:\*\*  
  \`\`\`json  
  {  
    "fy\_data": \[  
      { "region": "Pune 1", "avg\_cycle": 36 },  
      { "region": "NCR1", "avg\_cycle": 29 }  
    \],  
    "quarter\_data": \[  
      { "region": "Pune 1", "avg\_cycle": 34 },  
      { "region": "NCR1", "avg\_cycle": 28 }  
    \],  
    "month\_data": \[  
      { "region": "Pune 1", "avg\_cycle": 32 },  
      { "region": "NCR1", "avg\_cycle": 25 }  
    \]  
  }

