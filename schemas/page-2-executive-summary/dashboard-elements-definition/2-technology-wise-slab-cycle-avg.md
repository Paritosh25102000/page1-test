  
\---

\#\#\# Artifact 3: Technology-wise Slab Cycle  
The Top-Right Combo Chart.

\`\`\`markdown  
\# Dashboard Element Definition: Technology-wise Slab Cycle Avg & No of Slabs

\#\# 1\. General Meta-Information  
\* \*\*Element Name:\*\* Tech Wise Performance  
\* \*\*Element ID:\*\* \`PG2-WIDGET-02\`  
\* \*\*Dashboard Page:\*\* Page 2 (Slab Cycle Analysis)  
\* \*\*Element Type:\*\* Combo Chart (Bar \+ Line)

\#\# 2\. Business Context  
\* \*\*Business Goal:\*\* Validate if advanced technologies (Aluform) are delivering the expected speed benefits over Conventional methods.  
\* \*\*Key Questions Answered:\*\* "Are we getting the speed ROI from Aluform?" "How many slabs are we doing with conventional vs. modern tech?"  
\* \*\*Target Audience Action:\*\* If Aluform cycle time is close to Conventional, investigate site logistics or training issues.

\#\# 3\. Metric Definition  
\* \*\*Metric 1 (Bar):\*\* \*\*No of Slabs\*\*.  
    \*   Count of completed slab cycles.  
\* \*\*Metric 2 (Line):\*\* \*\*Average Slab Cycle\*\*.  
    \*   Mean duration of those cycles.  
\* \*\*Dimension (X-Axis):\*\* Formwork Type / Technology.  
    \*   Categories: "Aluform Typical", "Conventional", "Aluform Non-Typical", "Aluform 1st Set up", etc.

\#\# 4\. Source Data Requirements  
\* \*\*Required JSON Objects:\*\*  
    \*   \`tasks.attributes.trade\_type\` (Mapped to Technology)  
    \*   \`tasks.dates.actual.duration\_days\`  
\* \*\*Filters:\*\*  
    \*   Global Filters applied.

\#\# 5\. Data Transformation Logic  
\* \*\*Categorization:\*\*  
    \*   Create composite keys for X-Axis if needed (e.g., Technology \+ Slab Type).  
    \*   \*Example:\* If \`trade\_type\`="Shuttering- AL" AND \`slab\_works\`="Typical" \-\> "Aluform Typical".  
\* \*\*Aggregation:\*\*  
    \*   Group by Categorized Technology.  
    \*   Count distinct IDs (No of Slabs).  
    \*   Average \`duration\_days\` (Avg Cycle).

\#\# 6\. Staging Dataset Structure  
\* \*\*Output Format:\*\* Array of Objects.  
\* \*\*Structure:\*\*  
  \`\`\`json  
  \[  
    { "tech": "Aluform Typical", "count": 243, "avg\_cycle": 16 },  
    { "tech": "Conventional", "count": 17, "avg\_cycle": 31 }  
  \]  
