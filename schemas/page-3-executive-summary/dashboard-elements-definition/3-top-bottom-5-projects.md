\# Dashboard Element Definition: Top/Bottom 5 Projects (Sprint Execution)

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Top & Bottom 5 Projects (Sprint Physicals)  
\* \*\*Element ID:\*\* \`PG3-WIDGET-03\` (Top) & \`PG3-WIDGET-04\` (Bottom)  
\* \*\*Dashboard Page:\*\* Page 3 (Physical Progress)  
\* \*\*Element Type:\*\* Leaderboard Tables

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Recognize high performers and highlight projects requiring immediate intervention based on short-term goals.  
\* \*\*Key Questions Answered:\*\* "Who hit their floor counts this sprint?" "Who missed completely?"

\#\# 3\. Metric Definition  
\* \*\*Sorting Metric:\*\* \*\*% Achieve against Sprint\*\*.  
    \*   Formula: \`Actual Floors / Sprint Plan Floors\`.  
\* \*\*Columns:\*\*  
    \*   Project Name  
    \*   Sprint Plan (Count)  
    \*   Actual Completed (Count)  
    \*   % Achieve

\#\# 4\. Source Data Requirements  
\*   Same as Widget 01\.

\#\# 5\. Data Transformation Logic  
\* \*\*Filtering:\*\* Only include projects with a valid Sprint Plan (\> 0 floors planned).  
\* \*\*Ranking:\*\*  
    \*   Top 5: Sort Descending by %.  
    \*   Bottom 5: Sort Ascending by %.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* JSON Lists.  
\* \*\*Structure:\*\*  
  \`\`\`json  
  {  
    "top\_5": \[  
      {"project": "Project A", "plan": 4, "actual": 5, "pct": 125}  
    \],  
    "bottom\_5": \[  
      {"project": "Project B", "plan": 4, "actual": 1, "pct": 25}  
    \]  
  }  
