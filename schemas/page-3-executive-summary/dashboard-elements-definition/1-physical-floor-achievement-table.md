\# Dashboard Element Definition: Physical Floor Achievement Table

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Number of Floors Achievement Table  
\* \*\*Element ID:\*\* \`PG3-WIDGET-01\`  
\* \*\*Dashboard Page:\*\* Page 3 (Physical Progress)  
\* \*\*Element Type:\*\* Tree Table / Pivot Table

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Track physical output (Volume) against both the Standard Schedule (AOP) and the Accelerated Schedule (Sprint) within specific time windows.  
\* \*\*Key Questions Answered:\*\* "We planned 4 floors this Quarter; did we deliver them?" "Is the 'Sprint' target higher than the 'AOP' target for this month?"  
\* \*\*Target Audience Action:\*\* Identify Projects where \`Actual \< Plan\` for the current Quarter, indicating slippage that will impact the FY bottom line.

\#\# 3\. Metric Definition  
\* \*\*Unit of Measure:\*\* \*\*Count of Floors\*\* (Integer).  
\* \*\*Time Context:\*\* Dynamic based on \`PG1-CTRL-01\` (FY / Quarter / Month).  
\* \*\*Metrics:\*\*  
    \*   \*\*AOP Plan (Period):\*\* Count of floors scheduled to finish within the selected Time Window (based on \`dates.plan\`).  
    \*   \*\*Sprint Plan (Period):\*\* Count of floors scheduled to finish within the selected Time Window (based on \`dates.sprint\`).  
    \*   \*\*Actual Completed (Period):\*\* Count of floors actually finished within the selected Time Window (based on \`dates.actual\`).  
    \*   \*\*% Achieve (AOP):\*\* \`Actual (Period) / AOP Plan (Period)\`.  
    \*   \*\*% Achieve (Sprint):\*\* \`Actual (Period) / Sprint Plan (Period)\`.  
\* \*\*Grouping:\*\* Zone \-\> Region \-\> Project.

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.attributes.zone\`  
    \*   \`tasks.attributes.region\`  
    \*   \`tasks.attributes.project\_name\`  
    \*   \`tasks.attributes.main\_category\` (Filter: "Civil Works- RCC")  
    \*   \`tasks.attributes.floor\` (Filter: Is Not Null; ensures we count \*floors\*, not sub-activities)  
    \*   \`tasks.dates.plan.end\` (For AOP Counts)  
    \*   \`tasks.dates.sprint.end\` (For Sprint Counts)  
    \*   \`tasks.dates.actual.end\` (For Actual Counts)

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Filter "Floor" Tasks:\*\*  
    \*   Keep only tasks where \`main\_category\`="Civil Works- RCC" AND \`floor\` is not null.  
\* \*\*Step 2: Time Window Logic (Per Mode):\*\*  
    \*   \*\*FY Mode:\*\* Window \= Apr 1, 2025 to Mar 31, 2026\.  
    \*   \*\*Quarter Mode:\*\* Window \= Current Quarter Dates (e.g., Oct 1 \- Dec 31).  
    \*   \*\*Month Mode:\*\* Window \= Today \+/- 5 Weeks.  
\* \*\*Step 3: Counting (Per Mode):\*\*  
    \*   \`AOP\_Count\`: Count tasks where \`dates.plan.end\` falls inside Window.  
    \*   \`Sprint\_Count\`: Count tasks where \`dates.sprint.end\` falls inside Window.  
    \*   \`Actual\_Count\`: Count tasks where \`dates.actual.end\` falls inside Window.  
\* \*\*Step 4: Ratios:\*\*  
    \*   Calculate percentages. If Plan \= 0, handle Division by Zero (return null or 0).

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* JSON Object (keyed by Time Mode).  
\* \*\*Structure:\*\*  
  \`\`\`json  
  {  
    "fy\_data": \[  
      {  
        "id": "ZONE\_MZ",  
        "name": "MZ",  
        "type": "Zone",  
        "aop\_plan": 50,  
        "sprint\_plan": 55,  
        "actual\_completed": 45,  
        "pct\_aop": 90.0,  
        "pct\_sprint": 81.8,  
        "children": \[ ...Regions... \]  
      }  
    \],  
    "quarter\_data": \[ ... \]  
  }

