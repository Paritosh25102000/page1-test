\#\#\# Artifact 5: Top 5 Projects (Recent Performance)

\`\`\`markdown  
\# Dashboard Element Definition: Top 5 Projects (Last 5 Typical Floors)

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Top 5 Recent Performers  
\* \*\*Element ID:\*\* \`PG2-WIDGET-04\`  
\* \*\*Dashboard Page:\*\* Page 2 (Slab Cycle Analysis)  
\* \*\*Element Type:\*\* Leaderboard Table

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Gamification of performance.  
\* \*\*Key Questions Answered:\*\* "Who are the fastest builders right now?"  
\* \*\*Target Audience Action:\*\* Benchmarking best practices.

\#\# 3\. Metric Definition  
\* \*\*Metric:\*\* \*\*Avg Cycle of Last 5 Typical Floors\*\*.  
\* \*\*Filter Context:\*\*  
    \*   The "Last 5" are selected relative to the \*\*End Date\*\* of the active Time Mode.  
    \*   \*Example (FY Mode):\* Last 5 floors completed before Mar 31, 2026 (essentially current status).  
    \*   \*Example (Quarter Mode):\* Last 5 floors completed before Dec 31, 2025\.  
\* \*\*Ranking:\*\* Top 5 projects with the lowest average.

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.dates.actual.end\` (Sorting)  
    \*   \`tasks.dates.actual.duration\_days\` (Averaging)  
    \*   \`tasks.attributes.tower\`  
    \*   \`tasks.attributes.slab\_works\` ("Typical" only)

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Grouping:\*\* Group data by \`project\_name\` \+ \`tower\`.  
\* \*\*Step 2: Time-Bound Sorting:\*\*  
    \*   Filter tasks where \`dates.actual.end\` \<= Time Mode End Date.  
    \*   Sort remaining tasks by \`dates.actual.end\` Descending.  
\* \*\*Step 3: Selection:\*\*  
    \*   Take the top 5 records (most recent) for each Tower.  
    \*   Calculate Mean \`duration\_days\` of these 5 records.  
\* \*\*Step 4: Global Ranking:\*\*  
    \*   Sort all Towers by the calculated mean. Keep top 5\.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* JSON Object (keyed by Time Mode).  
\* \*\*Structure:\*\*  
  \`\`\`json  
  {  
    "fy\_data": \[  
      { "rank": 1, "project": "Tropical Isle", "tower": "T1", "recent\_avg": 7.5 }  
    \],  
    "quarter\_data": \[ ... \]  
  }  
