\---

\#\#\# Artifact 3: Finishing Activities Gap Table  
The detailed table at the bottom.

\`\`\`markdown  
\# Dashboard Element Definition: Finishing Activities Gap Table

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Detailed Gap Matrix  
\* \*\*Element ID:\*\* \`PG4-WIDGET-05\`  
\* \*\*Dashboard Page:\*\* Page 4 (Finishing Gaps)  
\* \*\*Element Type:\*\* Tree Table

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* A unified view of the production sequence health for the whole portfolio.  
\* \*\*Key Questions Answered:\*\* "Which specific project has a Blockwork gap of 14 floors?" (Drastic delay).

\#\# 3\. Metric Definition  
\* \*\*Rows:\*\* Hierarchy (Zone \-\> Region \-\> Project).  
\* \*\*Columns:\*\*  
    \*   \*\*Blockwork Gap:\*\* (Floors)  
    \*   \*\*Plaster Gap:\*\* (Floors)  
    \*   \*\*Toilet Flooring/Dado Gap:\*\* (Floors)  
    \*   \*\*Flat Flooring Gap:\*\* (Floors)  
\* \*\*Aggregation:\*\*  
    \*   Project Level: Simple difference (RCC \- Trade).  
    \*   Zone/Region Level: Average of child projects.

\#\# 4\. Source Data Requirements  
\*   Same as Widgets 01-04 (Floor Attributes, Trade Types, Progress).

\#\# 5\. Data Transformation Logic  
\*   \*\*Step 1:\*\* Calculate Gaps for every Project/Tower.  
\*   \*\*Step 2:\*\* Roll up averages to Region and Zone levels.  
\*   \*\*Step 3:\*\* Join all 4 metrics into a single row per entity.

\#\# 6\. Staging Dataset Structure  
\*   \*\*Output Format:\*\* Nested JSON.  
\*   \*\*Structure:\*\*  
    \`\`\`json  
    \[  
      {  
        "id": "ZONE\_MZ",  
        "name": "MZ",  
        "type": "Zone",  
        "blockwork\_gap": 5.0,  
        "plaster\_gap": 4.5,  
        "toilet\_gap": 6.0,  
        "flooring\_gap": 7.0,  
        "children": \[ ... \]  
      }  
    \]  
    \`\`\`

\#\# 7\. Visualization & UI Behavior  
\*   \*\*UI Type:\*\* Tree Table.  
\*   \*\*Conditional Formatting:\*\*  
    \*   Gap \> 10 (Red) \- Too slow.  
    \*   Gap \< 3 (Amber) \- Too close / risk of clash.  
    \*   Gap 3-10 (Green) \- Healthy.  
