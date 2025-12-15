\---

\#\#\# Artifact 4: Detailed Slab Matrix

The Bottom-Left Heatmap Table.

\`\`\`markdown

\# Dashboard Element Definition: Slab Cycle Frequency Matrix

\#\# 1\. General Meta-Information

\* \*\*Element Name:\*\* Detailed Slab Cycle Matrix

\* \*\*Element ID:\*\* \`PG2-WIDGET-03\`

\* \*\*Dashboard Page:\*\* Page 2 (Slab Cycle Analysis)

\* \*\*Element Type:\*\* Tree Table / Pivot Table

\#\# 2\. Business Context

\* \*\*Business Goal:\*\* Granular breakdown of cycle times to identify consistency. A low average is good, but high variance is bad.

\* \*\*Key Questions Answered:\*\* "Which project has the most slabs taking \>30 days?" "Is the average consistent, or are there outliers?"

\* \*\*Target Audience Action:\*\* Focus on the "\>30 Days" and "26-30 Days" columns to identify bottlenecks.

\#\# 3\. Metric Definition

\* \*\*Rows:\*\* Hierarchy (Zone \-\> Region \-\> Project).

\* \*\*Summary Columns:\*\*

    \*   \*\*No. of Slabs:\*\* Total count.

    \*   \*\*Avg. Slab Cycle:\*\* Mean duration.

\* \*\*Distribution Columns (Buckets):\*\*

    \*   Upto 7 Days

    \*   7-10 Days

    \*   11-14 Days

    \*   15-20 Days

    \*   21-25 Days

    \*   26-30 Days

    \*   \>30 Days

\#\# 4\. Source Data Requirements

\* \*\*Required JSON Objects:\*\*

    \*   \`tasks.dates.actual.duration\_days\`

    \*   \`tasks.attributes\` (Zone/Region/Project)

\#\# 5\. Data Transformation Logic

\* \*\*Step 1: Calculate Per-Slab Metrics\*\*

    \*   For every completed slab task:

        \*   Get Duration.

        \*   Assign to Bucket (e.g., Duration=9 \-\> "7-10 Days").

\* \*\*Step 2: Aggregate Rows\*\*

    \*   Group by Hierarchy (Zone/Region/Project).

    \*   Count Slabs in each Bucket.

    \*   Calculate Overall Weighted Average.

\#\# 6\. Staging Dataset Structure

\* \*\*Output Format:\*\* Nested JSON or Flat List with Parent IDs.

\* \*\*Structure:\*\*

  \`\`\`json

  \[

    {

      "row\_id": "PROJ\_123",

      "name": "Tropical Isle",

      "parent\_id": "REG\_NZ1",

      "total\_slabs": 45,

      "avg\_cycle": 12,

      "buckets": {

        "upto\_7": 0,

        "7\_10": 15,

        "11\_14": 20,

        "15\_20": 10,

        "21\_25": 0,

        "26\_30": 0,

        "gt\_30": 0

      }

    }

  \]  
