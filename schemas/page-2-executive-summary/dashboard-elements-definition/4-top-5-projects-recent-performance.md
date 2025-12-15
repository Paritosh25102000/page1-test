  
\---

\#\#\# Artifact 5: Top 5 Projects (Recent Performance)  
The Bottom-Right Table.

\`\`\`markdown  
\# Dashboard Element Definition: Top 5 Projects (Last 5 Typical Floors)

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Top 5 Recent Performers  
\* \*\*Element ID:\*\* \`PG2-WIDGET-04\`  
\* \*\*Dashboard Page:\*\* Page 2 (Slab Cycle Analysis)  
\* \*\*Element Type:\*\* Leaderboard Table

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Gamification and recognition of current best performers.  
\* \*\*Key Questions Answered:\*\* "Who is constructing the fastest \*right now\*?"  
\* \*\*Target Audience Action:\*\* Benchmarking – "Go ask the Tropical Isle team how they are achieving 8-day cycles."

\#\# 3\. Metric Definition  
\* \*\*Metric:\*\* \*\*Avg Cycle of Last 5 Typical Floors\*\*.  
    \*   Logic: Identify the 5 most recently completed "Typical" floors for each Tower. Average their duration.  
\* \*\*Ranking:\*\* Ascending Order (Lowest Cycle Time \= Rank 1).  
\* \*\*Limit:\*\* Top 5 entries.

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.dates.actual.end\` (To sort by recency)  
    \*   \`tasks.dates.actual.duration\_days\`  
    \*   \`tasks.attributes.tower\`  
    \*   \`tasks.attributes.slab\_works\` ("Typical" only)

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Filter & Sort\*\*  
    \*   Filter: \`slab\_works\` \= "Typical".  
    \*   Group by: \`project\_name\` \+ \`tower\`.  
    \*   Sort slabs within group by \`actual.end\` (Descending).  
\* \*\*Step 2: Slice & Average\*\*  
    \*   Take top 5 records per Tower.  
    \*   Calculate Average Duration.  
\* \*\*Step 3: Global Rank\*\*  
    \*   Sort all Towers by the calculated Average.  
    \*   Take top 5\.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* Array of Objects.  
\* \*\*Structure:\*\*  
  \`\`\`json  
  \[  
    {  
      "rank": 1,  
      "project": "Tropical Isle",  
      "tower": "Tower A",  
      "recent\_avg": 7.5  
    },  
    {  
      "rank": 2,  
      "project": "Zenith",  
      "tower": "Tower 1",  
      "recent\_avg": 8.0  
    }  
  \]

