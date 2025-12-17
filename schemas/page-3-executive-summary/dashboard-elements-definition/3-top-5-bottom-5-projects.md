\#\#\# Artifact 3: Top 5 / Bottom 5 Projects

\`\`\`markdown  
\# Dashboard Element Definition: Top/Bottom 5 Projects (Sprint Execution)

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Top & Bottom 5 Projects (Sprint Physicals)  
\* \*\*Element ID:\*\* \`PG3-WIDGET-03\` (Top) & \`PG3-WIDGET-04\` (Bottom)  
\* \*\*Dashboard Page:\*\* Page 3 (Physical Progress)  
\* \*\*Element Type:\*\* Leaderboard Tables

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Highlight best and worst execution for the selected period.  
\* \*\*Key Questions Answered:\*\* "Who is winning the Q3 Sprint?" "Who failed to deliver any floors this Month?"

\#\# 3\. Metric Definition  
\* \*\*Sorting Metric:\*\* \*\*% Achieve against Sprint (Period)\*\*.  
    \*   Formula: \`Actual Floors (Window) / Sprint Plan Floors (Window)\`.  
\* \*\*Columns:\*\*  
    \*   Project Name  
    \*   Sprint Plan (Count)  
    \*   Actual Completed (Count)  
    \*   % Achieve

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.attributes.project\_name\`  
    \*   \`tasks.attributes.floor\`  
    \*   \`tasks.dates.sprint.end\`  
    \*   \`tasks.dates.actual.end\`

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Filtering:\*\*  
    \*   Calculate metrics per project for the selected Time Mode (FY/Qtr/Month).  
    \*   \*\*Crucial:\*\* Exclude projects where \`Sprint Plan (Window) \== 0\`. (We don't want to rank projects that had nothing to do).  
\* \*\*Step 2: Ranking:\*\*  
    \*   \*\*Top 5:\*\* Sort Descending by %.  
    \*   \*\*Bottom 5:\*\* Sort Ascending by %.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* JSON Object (keyed by Time Mode).  
\* \*\*Structure:\*\*  
  \`\`\`json  
  {  
    "fy\_data": {  
      "top\_5": \[ {"project": "Proj A", "plan": 10, "actual": 12, "pct": 120} \],  
      "bottom\_5": \[ {"project": "Proj B", "plan": 10, "actual": 2, "pct": 20} \]  
    },  
    "quarter\_data": { ... }  
  }  
