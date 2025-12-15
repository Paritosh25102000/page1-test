\---

\#\#\# Artifact 2: Activity Slab Gap Charts  
The four bar charts at the top (Blockwork, Plaster, Toilet Flooring, Flat Flooring).

\`\`\`markdown  
\# Dashboard Element Definition: Activity Slab Gap Charts

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Activity Slab Gaps (Multiple Charts)  
\* \*\*Element ID:\*\* \`PG4-WIDGET-01\` (Blockwork), \`PG4-WIDGET-02\` (Plaster), \`PG4-WIDGET-03\` (Toilet), \`PG4-WIDGET-04\` (Flat Flooring)  
\* \*\*Dashboard Page:\*\* Page 4 (Finishing Gaps)  
\* \*\*Element Type:\*\* Bar Chart with Reference Lines

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Visualize the "Lag" between Structure and Finishes.  
\* \*\*Key Questions Answered:\*\* "Is Blockwork falling too far behind RCC?" (Gap \> Target). "Are we working too close to the structure?" (Gap \< Target, safety risk).  
\* \*\*Target Audience Action:\*\* If Gap \> 8-10 floors (typical limit), mobilize more finishing agencies.

\#\# 3\. Metric Definition  
\* \*\*Primary Metric:\*\* \*\*Average Gap (Floors)\*\*.  
    \*   Formula: \`Avg(Current Max RCC Floor \- Current Max Activity Floor)\`.  
    \*   \*Example:\* RCC is at Floor 20\. Blockwork is at Floor 12\. Gap \= 8\.  
\* \*\*Reference Metrics (Lines):\*\*  
    \*   \*\*PI0, PI1, PI3, PI5:\*\* These represent \*\*Performance Indices\*\* or \*\*Target Gaps\*\* defined by the CCO office (e.g., "Standard Gap should be 5 floors").  
\* \*\*Grouping:\*\* By Zone (MZ, WEZ, SZ, NZ).

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.attributes.trade\_type\`  
    \*   \`tasks.attributes.floor\`  
    \*   \`tasks.progress.is\_complete\`  
\* \*\*Trades Mapped:\*\*  
    \*   Structure \= \`Civil Works- RCC\` (Sub-category: RCC)  
    \*   Blockwork \= \`Blockwork\`  
    \*   Plaster \= \`Int Plaster\`  
    \*   Toilet \= \`Waterproofing\` or \`Flooring\` (Depends on specific "Toilet" tag availability)  
    \*   Flat Flooring \= \`Flooring\`

\#\# 5\. Data Transformation Logic  
\* \*\*Step 1: Determine Current Floor per Trade (Per Tower)\*\*  
    \*   Filter completed tasks (\`is\_complete\` \= true).  
    \*   Convert \`attributes.floor\` strings to integers (ETL Logic: "GF"=0, "Floor 1"=1, etc.).  
    \*   Find \`MAX(Floor Integer)\` for RCC vs. Specific Trade per Tower.  
\* \*\*Step 2: Calculate Gap\*\*  
    \*   \`Gap \= Max\_RCC\_Floor \- Max\_Trade\_Floor\`.  
\* \*\*Step 3: Aggregate by Zone\*\*  
    \*   Calculate Average Gap across all Towers/Projects in the Zone.

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* Array of Objects (one array per Widget ID).  
\* \*\*Structure:\*\*  
  \`\`\`json  
  \[  
    { "zone": "MZ", "avg\_gap": 5.0, "pi0": 8, "pi1": 6, "pi3": 4, "pi5": 3 },  
    { "zone": "WEZ", "avg\_gap": 7.2, "pi0": 8, "pi1": 6, "pi3": 4, "pi5": 3 }  
  \]

