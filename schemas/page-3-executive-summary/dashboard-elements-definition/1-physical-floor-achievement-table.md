\# Dashboard Element Definition: Physical Floor Achievement Table

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Number of Floors Achievement Table  
\* \*\*Element ID:\*\* \`PG3-WIDGET-01\`  
\* \*\*Dashboard Page:\*\* Page 3 (Physical Progress)  
\* \*\*Element Type:\*\* Tree Table / Pivot Table

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Track the "Physical" output against the plan, distinct from financial progress.  
\* \*\*Key Questions Answered:\*\* "We planned to cast 10 slabs this month; how many did we actually cast?" "Is the West Zone meeting its production quotas?"  
\* \*\*Target Audience Action:\*\* Identify Regions where the \*physical\* count of delivered floors is lagging, even if the \*financial\* (COC) numbers look okay due to expensive non-slab work.

\#\# 3\. Metric Definition  
\* \*\*Unit of Measure:\*\* \*\*Count of Floors\*\* (Integer).  
\* \*\*Metrics:\*\*  
    \*   \*\*AOP Plan:\*\* Cumulative count of floors planned to be completed YTD (based on Baseline).  
    \*   \*\*Sprint Plan:\*\* Count of floors planned to be completed within the active Sprint window.  
    \*   \*\*Actual Completed:\*\* Actual count of floors completed in the respective period.  
    \*   \*\*% Achieve (AOP):\*\* \`Actual YTD / AOP Plan YTD\`.  
    \*   \*\*% Achieve (Sprint):\*\* \`Actual (Sprint Window) / Sprint Plan\`.  
\* \*\*Grouping:\*\* Zone \-\> Region \-\> Project.

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.attributes.floor\` (To identify floor tasks)  
    \*   \`tasks.dates.plan.end\` (AOP Dates)  
    \*   \`tasks.dates.sprint\` (Sprint Dates)  
    \*   \`tasks.dates.actual.end\` (Actual Dates)  
    \*   \`tasks.is\_summary\` (True, if tracking cycle completion)  
\* \*\*Filters:\*\*  
    \*   \*\*Essential Filter:\*\* \`attributes.main\_category\` \= "Civil Works- RCC" AND \`attributes.floor\` is not null. (Ensures we are counting main structural floors, not minor tasks).

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Identify "Floor" Tasks\*\*  
    \*   Filter dataset for tasks representing a full Floor Cycle (e.g., \`slab\_works\` is present).  
\* \*\*Step 2: Calculate AOP Counts (YTD)\*\*  
    \*   Count tasks where \`dates.plan.end\` \<= Current Date.  
\* \*\*Step 3: Calculate Sprint Counts\*\*  
    \*   Count tasks where \`dates.sprint.end\` is within current Sprint Window.  
\* \*\*Step 4: Calculate Actuals\*\*  
    \*   Count tasks where \`dates.actual.end\` is valid (completed).  
\* \*\*Step 5: Ratios\*\*  
    \*   Compute percentages. Handle Division by Zero (if Plan \= 0, and Actual \> 0, cap at 100% or show N/A).

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* Nested JSON for Tree Grid.  
\* \*\*Structure:\*\*  
  \`\`\`json  
  \[  
    {  
      "id": "ZONE\_MZ",  
      "name": "MZ",  
      "aop\_plan": 50,  
      "sprint\_plan": 10,  
      "actual\_completed": 45,  
      "pct\_aop": 90.0,  
      "pct\_sprint": 80.0,  
      "children": \[ ...Regions... \]  
    }  
  \]  
