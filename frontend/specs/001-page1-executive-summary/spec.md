# Feature Specification: Page 1 Executive Summary Dashboard

**Feature Branch**: `001-page1-executive-summary`
**Created**: 2025-12-15
**Status**: Draft
**Input**: User description: "Page 1 Executive Summary Dashboard - Complete implementation including Global Filter Panel, COC Trend Chart, AOP/Sprint Gauges, and Project Achievement Matrix using Mantine UI with mock Context"

## Clarifications

### Session 2025-12-15

- Q: How should the dashboard handle loading and error states? → A: Basic loading indicators (spinners) per widget + simple error message if data fails
- Q: Should the dashboard include logging or analytics capabilities? → A: Console logging for development/debugging only (filter changes, errors)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Executive Summary at a Glance (Priority: P1)

As a Chief Construction Officer (CCO), I need to see an executive summary dashboard showing financial trends, schedule adherence, and portfolio risk so that I can quickly assess overall construction performance without drilling into details.

**Why this priority**: This is the core value proposition of the dashboard - providing immediate visibility into key metrics. Without this, the CCO has no single view of organizational health.

**Independent Test**: Can be fully tested by loading the dashboard and verifying all four widgets (Filter Panel, COC Trend, Gauges, Matrix) render with default data. Delivers immediate value by showing the "ALL" organizational view.

**Acceptance Scenarios**:

1. **Given** the dashboard loads for the first time, **When** the page renders, **Then** the user sees the Global Filter Panel, COC Trend Chart, AOP/Sprint Gauges, and Project Achievement Matrix all populated with data.

2. **Given** the dashboard is loaded, **When** no filters are selected, **Then** all widgets display aggregated data for the entire organization ("ALL" view).

3. **Given** the dashboard is loaded, **When** the user views the page, **Then** the Financial Year (FY) time mode is selected by default.

4. **Given** the dashboard is embedded in an iframe, **When** the page renders, **Then** the dashboard manages its own internal scrolling without relying on the parent window.

---

### User Story 2 - Filter Dashboard by Organizational Hierarchy (Priority: P1)

As a CCO, I need to filter the dashboard by Zone, Region, and Project so that I can drill down from organization-wide views to specific project performance.

**Why this priority**: Filtering is essential for the CCO to investigate specific areas of concern. All widgets depend on this filter state to show relevant data.

**Independent Test**: Can be tested by selecting hierarchy levels and verifying all widgets update to show filtered data.

**Acceptance Scenarios**:

1. **Given** the dashboard is loaded, **When** the user selects a Zone (e.g., MZ), **Then** all widgets update to show data for that zone only.

2. **Given** a Zone is selected, **When** the user selects a Region within that zone, **Then** all widgets update to show data for that region only.

3. **Given** a Zone and Region are selected, **When** the user selects a Project, **Then** all widgets update to show data for that specific project.

4. **Given** filters are applied, **When** the user clears the Zone selection, **Then** all child selections (Region, Project) are cleared and all widgets return to the "ALL" view.

5. **Given** the filter panel, **When** no Zone is selected, **Then** the Region dropdown is disabled; when no Region is selected, the Project dropdown is disabled.

---

### User Story 3 - Switch Time Mode for Different Planning Horizons (Priority: P1)

As a CCO, I need to toggle between Financial Year, Quarter, and Month views so that I can switch between strategic long-term planning and tactical short-term operational analysis.

**Why this priority**: Time mode changes how the COC Trend Chart displays data, enabling the CCO to answer different business questions at different time granularities.

**Independent Test**: Can be tested by switching time modes and verifying the COC Trend Chart updates its data resolution.

**Acceptance Scenarios**:

1. **Given** the dashboard is in FY mode (default), **When** the user views the COC Trend Chart, **Then** the chart displays monthly data points for the full financial year (April to March).

2. **Given** FY mode is active, **When** the user switches to Quarter mode, **Then** the COC Trend Chart updates to display weekly data points for the current quarter.

3. **Given** Quarter mode is active, **When** the user switches to Month mode (Looking Glass), **Then** the COC Trend Chart updates to display weekly data for +/- 5 weeks from the current date.

---

### User Story 4 - Monitor Cost Trends via COC Trend Chart (Priority: P1)

As a CCO, I need to visualize planned vs actual cost trends with both periodic and cumulative views so that I can identify whether spending aligns with the Annual Operating Plan (AOP).

**Why this priority**: The COC Trend Chart is the primary tool for answering "Are we spending according to plan?" - a core CCO concern.

**Independent Test**: Can be tested by verifying the chart renders with bars (periodic costs) and lines (cumulative costs) for both plan and actual values.

**Acceptance Scenarios**:

1. **Given** the COC Trend Chart is displayed, **When** the user views the chart, **Then** they see bars representing periodic costs (Plan and Actual) and lines representing cumulative costs (Plan and Actual).

2. **Given** the chart is in FY mode, **When** data is displayed, **Then** the X-axis shows month labels (e.g., "Apr-25", "May-25") with up to 12 data points.

3. **Given** the chart is in Quarter or Month mode, **When** data is displayed, **Then** the X-axis shows week labels (e.g., "Wk 14", "Wk 15").

4. **Given** the chart has dual Y-axes, **When** the user views the chart, **Then** one axis shows periodic cost values and the other shows cumulative cost values.

---

### User Story 5 - Assess Schedule Performance via Gauges (Priority: P1)

As a CCO, I need to see AOP Achievement and Sprint Achievement as visual gauges so that I can instantly understand whether we're on track for the year and meeting accelerated targets.

**Why this priority**: The gauges provide instant visual feedback on the two most critical performance indicators - long-term stability (AOP) and short-term acceleration (Sprint).

**Independent Test**: Can be tested by verifying both gauges render with percentage values and appropriate color coding.

**Acceptance Scenarios**:

1. **Given** the AOP/Sprint Gauges widget is displayed, **When** the user views the widget, **Then** they see two side-by-side semi-circle gauges labeled "AOP Achievement" and "Sprint Achievement".

2. **Given** a gauge displays a value below 85%, **When** the user views the gauge, **Then** the gauge is colored red.

3. **Given** a gauge displays a value between 85% and 95%, **When** the user views the gauge, **Then** the gauge is colored amber.

4. **Given** a gauge displays a value above 95%, **When** the user views the gauge, **Then** the gauge is colored green.

5. **Given** filters are applied, **When** the widgets update, **Then** the gauges reflect the AOP and Sprint achievement for the filtered scope only.

---

### User Story 6 - Identify At-Risk Projects via Achievement Matrix (Priority: P1)

As a CCO, I need to see a heatmap table showing project counts distributed across achievement buckets so that I can quickly identify how many projects are critically underperforming.

**Why this priority**: The matrix enables the CCO to perform portfolio health checks and identify the "<60%" column as the critical area requiring immediate attention.

**Independent Test**: Can be tested by verifying the matrix renders with rows (Zones) and columns (achievement buckets) with project counts and heatmap styling.

**Acceptance Scenarios**:

1. **Given** the Project Achievement Matrix is displayed, **When** the user views the matrix, **Then** they see a table with rows for each Zone and columns for achievement buckets: >120%, 100-120%, 85-100%, 60-85%, <60%.

2. **Given** the matrix is displayed, **When** cells contain project counts, **Then** cells are styled with heatmap colors based on count or threshold (red highlighting for <60% column).

3. **Given** the "ALL" view is active, **When** the matrix is displayed, **Then** rows represent Zones (MZ, WEZ, SZ, NZ).

4. **Given** a specific Zone is selected, **When** the matrix updates, **Then** rows represent Regions within that Zone.

5. **Given** a matrix cell is clicked, **When** the click event fires, **Then** the action is logged to the console (future: modal with project list).

---

### User Story 7 - Responsive Layout for Iframe Embedding (Priority: P2)

As a CCO accessing the dashboard through the legacy enterprise system, I need the dashboard to render correctly within an iframe so that I can use it alongside other enterprise tools.

**Why this priority**: The dashboard must work within the iframe constraint, but this is a non-functional requirement that supports the core user stories.

**Independent Test**: Can be tested by embedding the dashboard in an iframe and verifying responsive behavior at different viewport sizes.

**Acceptance Scenarios**:

1. **Given** the dashboard is embedded in an iframe, **When** the viewport is 1024px or wider, **Then** all widgets are visible without horizontal scrolling.

2. **Given** the dashboard is embedded in an iframe, **When** the viewport is between 768px and 1024px, **Then** the layout adjusts responsively while maintaining widget visibility.

3. **Given** any viewport size, **When** content overflows, **Then** the dashboard provides internal scrolling without affecting the parent window.

---

### Edge Cases

- What happens when a Zone has no Regions? The Region dropdown shows an empty state with a placeholder message.
- What happens when all projects in a bucket have 0 count? The cell displays "0" with neutral styling.
- What happens when COC Trend has missing data points? The chart renders available points and handles nulls gracefully (no bars/lines for null values).
- What happens when Sprint data is unavailable for a selection? The Sprint gauge shows 0% or a "No Data" indicator.
- How does the system handle rapid sequential filter changes? State updates are processed in order without race conditions.
- What happens when the mock data file is unavailable? The dashboard displays an error state without crashing.

## Requirements *(mandatory)*

### Functional Requirements

#### Global Filter Panel (PG1-CTRL-01)

- **FR-001**: System MUST display a Zone dropdown populated from the hierarchy tree data.
- **FR-002**: System MUST display a Region dropdown that cascades based on the selected Zone.
- **FR-003**: System MUST display a Project dropdown that cascades based on the selected Region.
- **FR-004**: System MUST display a time mode toggle with three options: FY, Quarter, and Month.
- **FR-005**: System MUST default to "ALL" view and "FY" time mode on initial load.
- **FR-006**: System MUST disable child dropdowns until their parent is selected.
- **FR-007**: System MUST clear child selections when a parent selection changes.

#### COC Trend Chart (PG1-WIDGET-01)

- **FR-008**: System MUST display a combo chart with bars (periodic costs) and lines (cumulative costs).
- **FR-009**: System MUST show four data series: Plan Cost (bar), Actual Cost (bar), Cumulative Plan (line), Cumulative Actual (line).
- **FR-010**: System MUST use dual Y-axes: one for periodic costs, one for cumulative costs.
- **FR-011**: System MUST display monthly resolution when FY mode is selected.
- **FR-012**: System MUST display weekly resolution when Quarter or Month mode is selected.
- **FR-013**: System MUST update chart data when filters or time mode change.

#### AOP & Sprint Gauges (PG1-WIDGET-03)

- **FR-014**: System MUST display two semi-circle gauges side-by-side: AOP Achievement and Sprint Achievement.
- **FR-015**: System MUST show percentage values on each gauge.
- **FR-016**: System MUST color gauges based on thresholds: Red (<85%), Amber (85-95%), Green (>95%).
- **FR-017**: System MUST update gauge values when filters change.

#### Project Achievement Matrix (PG1-WIDGET-04)

- **FR-018**: System MUST display a table with heatmap-styled cells.
- **FR-019**: System MUST show rows for Zones (or Regions when Zone is selected).
- **FR-020**: System MUST show columns for achievement buckets: >120%, 100-120%, 85-100%, 60-85%, <60%.
- **FR-021**: System MUST display project counts in each cell.
- **FR-022**: System MUST apply heatmap styling with intensity based on count or threshold.
- **FR-023**: System MUST highlight the <60% column with red styling to indicate critical projects.
- **FR-024**: System MUST log cell clicks to the console (placeholder for future drill-down modal).

#### Dashboard Context & Data

- **FR-025**: System MUST maintain a shared context holding current filter state (zone, region, project) and time mode.
- **FR-026**: System MUST construct data keys based on selections: "ALL", "ZONE_{ID}", "REG_{ID}", or "PROJ_{ID}".
- **FR-027**: System MUST load data from a pre-aggregated mock JSON file.
- **FR-028**: System MUST provide the appropriate data subset to each widget based on current filter state.

#### Layout & Responsiveness

- **FR-029**: System MUST render all four widgets (Filter Panel, COC Trend, Gauges, Matrix) on a single page.
- **FR-030**: System MUST manage internal scrolling without relying on parent window scrolling.
- **FR-031**: System MUST maintain usability at viewport widths of 768px and above.
- **FR-032**: System MUST display a loading indicator (spinner) within each widget while data is being loaded.
- **FR-033**: System MUST display a user-friendly error message within the affected widget if data loading fails.
- **FR-034**: System MUST log filter changes and errors to the browser console for development debugging purposes.

### Key Entities

- **Zone**: Top-level organizational unit (e.g., MZ, WEZ, SZ, NZ). Used for highest-level data aggregation.
- **Region**: Mid-level organizational unit belonging to a Zone. Contains multiple projects.
- **Project**: Individual construction project with id and name. Lowest level of the hierarchy.
- **Time Mode**: Viewing perspective - FY (Financial Year, monthly), Quarter (current quarter, weekly), Month (Looking Glass +/- 5 weeks, weekly).
- **Control State**: Current selections including zone, region, project, and timeMode values.
- **COC Trend Point**: Data point containing label, sort date, plan cost, actual cost, cumulative plan, and cumulative actual.
- **KPI Gauges**: AOP and Sprint achievement percentages with status colors.
- **Project Matrix Row**: Row containing label, id, and bucket counts (gt_120, 100_120, 85_100, 60_85, lt_60).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Dashboard loads and displays all four widgets within 3 seconds on standard broadband connection.
- **SC-002**: Filter changes update all widgets within 500ms (perceived instant response).
- **SC-003**: Time mode switches update the COC Trend Chart within 500ms.
- **SC-004**: Users can complete a full filter sequence (Zone → Region → Project) in under 10 seconds.
- **SC-005**: CCO can identify the count of critically underperforming projects (<60%) within 5 seconds of viewing the dashboard.
- **SC-006**: Dashboard renders correctly and is fully usable at viewport widths from 768px to 1920px.
- **SC-007**: 100% of valid hierarchy paths are navigable through the cascading dropdowns.
- **SC-008**: All gauge color thresholds (Red/Amber/Green) are correctly applied based on percentage values.
- **SC-009**: CCO can switch between strategic (FY) and tactical (Month) views in a single click.

## Assumptions

- The mock data follows the schema defined in `page1-executive-summary.json`.
- The dashboard is embedded in an iframe within a legacy enterprise system.
- The mock data file is available at `etl-cco-dashboard/schemas/page-1-executive-simmary/page1-mock-data.json`.
- Currency is displayed in INR (Indian Rupees) as specified in the data schema.
- Financial Year runs from April 1 to March 31 (Indian fiscal year).
- The DashboardContext will be created to hold shared state across all widgets.
- Mantine UI components will be used for dropdowns, toggles, and tables.
- ApexCharts will be used for the COC Trend Chart and gauges.
- No authentication or authorization is required for this page (handled by parent system).
- Click handlers on matrix cells will log to console only; modal functionality is out of scope for initial implementation.
