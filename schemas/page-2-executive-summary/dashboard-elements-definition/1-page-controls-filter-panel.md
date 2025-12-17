\# Dashboard Element Definition: Operational Filters & Time Mode

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Operational Filters & Time Mode  
\* \*\*Element ID:\*\* \`PG2-CTRL-01\`  
\* \*\*Dashboard Page:\*\* Page 2 (Slab Cycle Analysis)  
\* \*\*Element Type:\*\* Control Component (Dropdowns, Toggles, Mode Switcher)

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Allow the CCO to analyze operational speed (Slab Cycle) through different time lenses (Strategic vs. Tactical) and operational filters (Methodology).  
\* \*\*Key Questions Answered:\*\* N/A (Control Element).  
\* \*\*Target Audience Action:\*\* Switch Time Mode to "Month" to see if recent site interventions have improved cycle times compared to the "FY" average.

\#\# 3\. Metric Definition  
\* \*\*Hierarchy Inputs:\*\* Zone \-\> Region \-\> Project.  
\* \*\*Timeline Mode Inputs:\*\*  
    \*   \*\*FY (Default):\*\* Current Financial Year (Apr 1 – Mar 31). Resolution: Aggregate over full year.  
    \*   \*\*Quarter:\*\* Current Calendar Quarter (e.g., Oct 1 – Dec 31). Resolution: Aggregate over quarter.  
    \*   \*\*Month (Looking Glass):\*\* Window of Today \- 5 weeks to Today \+ 5 weeks. Resolution: Aggregate over specific window.  
\* \*\*Operational Inputs:\*\*  
    \*   \*\*Slab Type:\*\* Toggle \["Typical", "Non-Typical"\]. Default: "Typical".  
    \*   \*\*Formwork Type:\*\* Dropdown \["All", "Aluform", "Conventional"\].

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.attributes.zone\`  
    \*   \`tasks.attributes.region\`  
    \*   \`tasks.attributes.project\_name\`  
    \*   \`tasks.attributes.trade\_type\` (To derive Formwork options)  
    \*   \`tasks.attributes.slab\_works\` (To derive Slab Type options)  
    \*   \`tasks.dates.actual.end\` (To validate data availability for Time Modes)

\#\# 5\. Data Transformation Logic  
\* \*\*Hierarchy Logic:\*\* Extract unique tree of Zone \-\> Region \-\> Project.  
\* \*\*Formwork Mapping:\*\* Scan \`attributes.trade\_type\` for distinct values like "Shuttering- AL", "Shuttering- Conventional" and map to simplified UI options ("Aluform", "Conventional").  
\* \*\*Timeline Logic:\*\*  
    \*   Define FY Start/End (Fixed: 2025-04-01 to 2026-03-31).  
    \*   Define Quarter Start/End based on Current Date.  
    \*   Define Looking Glass Start/End (Today \+/- 35 days).

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* JSON Dictionary (Configuration Object).  
\* \*\*Structure:\*\*  
  \`\`\`json  
  {  
    "filter\_options": {  
      "slab\_types": \["Typical", "Non-Typical"\],  
      "formwork\_types": \["Aluform", "Conventional", "Table Form"\],  
      "time\_modes": {  
        "fy": { "label": "Financial Year", "start": "2025-04-01", "end": "2026-03-31" },  
        "quarter": { "label": "Q3", "start": "2025-10-01", "end": "2025-12-31" },  
        "month": { "label": "Rolling", "start": "2025-11-15", "end": "2026-01-20" }  
      }  
    }  
  }  
