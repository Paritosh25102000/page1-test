# Tasks: Page 1 Executive Summary Dashboard

**Input**: Design documents from `/specs/001-page1-executive-summary/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - test tasks omitted. Test structure is provided in plan.md if needed later.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend app**: `etl-cco-dashboard/frontend/src/`
- **Tests**: `etl-cco-dashboard/frontend/tests/`
- **Public assets**: `etl-cco-dashboard/frontend/public/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize Vite + React + TypeScript project in etl-cco-dashboard/frontend/
- [ ] T002 Install Mantine UI dependencies (@mantine/core, @mantine/hooks) in etl-cco-dashboard/frontend/package.json
- [ ] T003 [P] Install ApexCharts dependencies (apexcharts, react-apexcharts) in etl-cco-dashboard/frontend/package.json
- [ ] T004 [P] Install Tabler Icons (@tabler/icons-react) in etl-cco-dashboard/frontend/package.json
- [ ] T005 [P] Configure Vite with path aliases in etl-cco-dashboard/frontend/vite.config.ts
- [ ] T006 [P] Configure TypeScript strict mode in etl-cco-dashboard/frontend/tsconfig.json
- [ ] T007 Copy TypeScript interfaces from specs/001-page1-executive-summary/contracts/dashboard.ts to etl-cco-dashboard/frontend/src/types/dashboard.ts
- [ ] T008 Copy mock data from etl-cco-dashboard/schemas/page-1-executive-simmary/page1-mock-data.json to etl-cco-dashboard/frontend/public/data/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Configure MantineProvider with theme in etl-cco-dashboard/frontend/src/App.tsx
- [ ] T010 Create utility functions for data key construction in etl-cco-dashboard/frontend/src/utils/dataKeys.ts
- [ ] T011 [P] Create utility functions for gauge color thresholds in etl-cco-dashboard/frontend/src/utils/thresholds.ts
- [ ] T012 Create DashboardContext with state management (filters, timeMode, data) in etl-cco-dashboard/frontend/src/context/DashboardContext.tsx
- [ ] T013 Create useDashboardData hook for data fetching and key construction in etl-cco-dashboard/frontend/src/hooks/useDashboardData.ts
- [ ] T014 [P] Create LoadingSpinner component in etl-cco-dashboard/frontend/src/components/common/LoadingSpinner.tsx
- [ ] T015 [P] Create ErrorMessage component in etl-cco-dashboard/frontend/src/components/common/ErrorMessage.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Executive Summary at a Glance (Priority: P1) 🎯 MVP

**Goal**: CCO sees all four widgets with default "ALL" data on initial load

**Independent Test**: Load dashboard, verify Filter Panel, COC Trend, Gauges, and Matrix all render with mock data

### Implementation for User Story 1

- [ ] T016 [US1] Create DashboardShell layout component with grid structure in etl-cco-dashboard/frontend/src/components/layout/DashboardShell.tsx
- [ ] T017 [P] [US1] Create placeholder GlobalFilterPanel component in etl-cco-dashboard/frontend/src/components/filters/GlobalFilterPanel.tsx
- [ ] T018 [P] [US1] Create GaugeChart component with ApexCharts radialBar in etl-cco-dashboard/frontend/src/components/widgets/GaugeChart.tsx
- [ ] T019 [P] [US1] Create KPIGauges widget with AOP and Sprint gauges side-by-side in etl-cco-dashboard/frontend/src/components/widgets/KPIGauges.tsx
- [ ] T020 [P] [US1] Create COCTrendChart component with ApexCharts combo (bar+line) and dual Y-axes in etl-cco-dashboard/frontend/src/components/widgets/COCTrendChart.tsx
- [ ] T021 [P] [US1] Create MatrixCell component with heatmap styling in etl-cco-dashboard/frontend/src/components/widgets/MatrixCell.tsx
- [ ] T022 [US1] Create ProjectMatrix widget with Mantine Table in etl-cco-dashboard/frontend/src/components/widgets/ProjectMatrix.tsx
- [ ] T023 [US1] Wire DashboardShell to DashboardContext and render all widgets in etl-cco-dashboard/frontend/src/App.tsx
- [ ] T024 [US1] Configure main.tsx entry point with MantineProvider and DashboardContext in etl-cco-dashboard/frontend/src/main.tsx

**Checkpoint**: Dashboard loads with all four widgets showing "ALL" data. This is the MVP.

---

## Phase 4: User Story 2 - Filter Dashboard by Organizational Hierarchy (Priority: P1)

**Goal**: CCO can filter by Zone → Region → Project with cascading dropdowns

**Independent Test**: Select Zone, verify Region dropdown populates; select Region, verify Project dropdown populates; verify all widgets update

### Implementation for User Story 2

- [ ] T025 [US2] Create HierarchySelect component with cascading logic in etl-cco-dashboard/frontend/src/components/filters/HierarchySelect.tsx
- [ ] T026 [US2] Update GlobalFilterPanel to include Zone, Region, Project dropdowns in etl-cco-dashboard/frontend/src/components/filters/GlobalFilterPanel.tsx
- [ ] T027 [US2] Add filter change handlers to DashboardContext (SET_ZONE, SET_REGION, SET_PROJECT) in etl-cco-dashboard/frontend/src/context/DashboardContext.tsx
- [ ] T028 [US2] Implement cascading dropdown disable/enable logic based on parent selection in etl-cco-dashboard/frontend/src/components/filters/HierarchySelect.tsx
- [ ] T029 [US2] Implement child selection clearing when parent changes in etl-cco-dashboard/frontend/src/context/DashboardContext.tsx
- [ ] T030 [US2] Add console logging for filter changes in etl-cco-dashboard/frontend/src/context/DashboardContext.tsx

**Checkpoint**: Hierarchy filtering fully functional - Zone/Region/Project cascade correctly, widgets update

---

## Phase 5: User Story 3 - Switch Time Mode for Different Planning Horizons (Priority: P1)

**Goal**: CCO can toggle FY/Quarter/Month to change COC Trend Chart resolution

**Independent Test**: Switch to Quarter mode, verify chart shows weekly data; switch to Month, verify chart shows looking glass data

### Implementation for User Story 3

- [ ] T031 [US3] Create TimeModeToggle component with Mantine SegmentedControl in etl-cco-dashboard/frontend/src/components/filters/TimeModeToggle.tsx
- [ ] T032 [US3] Update GlobalFilterPanel to include TimeModeToggle in etl-cco-dashboard/frontend/src/components/filters/GlobalFilterPanel.tsx
- [ ] T033 [US3] Add SET_TIME_MODE action to DashboardContext in etl-cco-dashboard/frontend/src/context/DashboardContext.tsx
- [ ] T034 [US3] Update COCTrendChart to select correct series (fy_series, quarter_series, month_series) based on timeMode in etl-cco-dashboard/frontend/src/components/widgets/COCTrendChart.tsx

**Checkpoint**: Time mode switching works - chart updates resolution when toggling FY/Quarter/Month

---

## Phase 6: User Story 4 - Monitor Cost Trends via COC Trend Chart (Priority: P1)

**Goal**: COC Trend Chart displays bars (periodic) and lines (cumulative) with dual Y-axes

**Independent Test**: Verify chart shows 4 series (Plan bar, Actual bar, Cumm Plan line, Cumm Actual line) with proper axis configuration

### Implementation for User Story 4

- [ ] T035 [US4] Configure ApexCharts dual Y-axis (periodic left, cumulative right) in etl-cco-dashboard/frontend/src/components/widgets/COCTrendChart.tsx
- [ ] T036 [US4] Add Plan Cost bar series styling (color, opacity) in etl-cco-dashboard/frontend/src/components/widgets/COCTrendChart.tsx
- [ ] T037 [US4] Add Actual Cost bar series styling in etl-cco-dashboard/frontend/src/components/widgets/COCTrendChart.tsx
- [ ] T038 [US4] Add Cumulative Plan line series with second Y-axis in etl-cco-dashboard/frontend/src/components/widgets/COCTrendChart.tsx
- [ ] T039 [US4] Add Cumulative Actual line series with second Y-axis in etl-cco-dashboard/frontend/src/components/widgets/COCTrendChart.tsx
- [ ] T040 [US4] Handle null values in trend data (skip bars/lines for null) in etl-cco-dashboard/frontend/src/components/widgets/COCTrendChart.tsx

**Checkpoint**: COC Trend Chart is fully styled with all four series and dual axes

---

## Phase 7: User Story 5 - Assess Schedule Performance via Gauges (Priority: P1)

**Goal**: AOP and Sprint gauges show percentages with color-coded thresholds

**Independent Test**: Verify gauges display correct percentages and colors (red < 85%, amber 85-95%, green > 95%)

### Implementation for User Story 5

- [ ] T041 [US5] Configure ApexCharts radialBar for semi-circle gauge in etl-cco-dashboard/frontend/src/components/widgets/GaugeChart.tsx
- [ ] T042 [US5] Implement dynamic color based on percentage using thresholds utility in etl-cco-dashboard/frontend/src/components/widgets/GaugeChart.tsx
- [ ] T043 [US5] Add percentage label display in gauge center in etl-cco-dashboard/frontend/src/components/widgets/GaugeChart.tsx
- [ ] T044 [US5] Add gauge title labels ("AOP Achievement", "Sprint Achievement") in etl-cco-dashboard/frontend/src/components/widgets/KPIGauges.tsx
- [ ] T045 [US5] Connect KPIGauges to context data (kpi_gauges.aop, kpi_gauges.sprint) in etl-cco-dashboard/frontend/src/components/widgets/KPIGauges.tsx

**Checkpoint**: Gauges display correctly with proper colors matching threshold rules

---

## Phase 8: User Story 6 - Identify At-Risk Projects via Achievement Matrix (Priority: P1)

**Goal**: Matrix shows project counts by bucket with heatmap styling and red highlight for <60%

**Independent Test**: Verify matrix shows Zone rows, bucket columns, project counts, and red styling on lt_60 column

### Implementation for User Story 6

- [ ] T046 [US6] Configure Mantine Table structure with bucket column headers in etl-cco-dashboard/frontend/src/components/widgets/ProjectMatrix.tsx
- [ ] T047 [US6] Implement heatmap cell styling based on count value in etl-cco-dashboard/frontend/src/components/widgets/MatrixCell.tsx
- [ ] T048 [US6] Add red border/highlight styling for lt_60 column cells in etl-cco-dashboard/frontend/src/components/widgets/MatrixCell.tsx
- [ ] T049 [US6] Implement row switching (Zones vs Regions) based on filter state in etl-cco-dashboard/frontend/src/components/widgets/ProjectMatrix.tsx
- [ ] T050 [US6] Add click handler with console.log for cell clicks in etl-cco-dashboard/frontend/src/components/widgets/MatrixCell.tsx
- [ ] T051 [US6] Connect ProjectMatrix to context data (project_matrix.rows) in etl-cco-dashboard/frontend/src/components/widgets/ProjectMatrix.tsx

**Checkpoint**: Matrix displays with heatmap styling, red <60% column, and click logging

---

## Phase 9: User Story 7 - Responsive Layout for Iframe Embedding (Priority: P2)

**Goal**: Dashboard works in iframe with responsive layout 768px-1920px

**Independent Test**: Embed in iframe, resize to 768px, verify all widgets visible and internal scrolling works

### Implementation for User Story 7

- [ ] T052 [US7] Configure DashboardShell with Mantine Grid/SimpleGrid for responsive layout in etl-cco-dashboard/frontend/src/components/layout/DashboardShell.tsx
- [ ] T053 [US7] Add CSS for iframe-safe scrolling (overflow: auto, no 100vh) in etl-cco-dashboard/frontend/src/components/layout/DashboardShell.tsx
- [ ] T054 [US7] Configure responsive breakpoints for widget sizing (768px, 1024px) in etl-cco-dashboard/frontend/src/components/layout/DashboardShell.tsx
- [ ] T055 [US7] Add responsive styling to GlobalFilterPanel (stack on mobile) in etl-cco-dashboard/frontend/src/components/filters/GlobalFilterPanel.tsx
- [ ] T056 [US7] Verify ApexCharts redrawOnParentResize is enabled in etl-cco-dashboard/frontend/src/components/widgets/COCTrendChart.tsx

**Checkpoint**: Dashboard is fully responsive and works correctly in iframe

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T057 [P] Add loading states to all widgets using LoadingSpinner in etl-cco-dashboard/frontend/src/components/widgets/
- [ ] T058 [P] Add error states to all widgets using ErrorMessage in etl-cco-dashboard/frontend/src/components/widgets/
- [ ] T059 Add error logging for data fetch failures in etl-cco-dashboard/frontend/src/hooks/useDashboardData.ts
- [ ] T060 [P] Configure ApexCharts theme colors to match Mantine theme in etl-cco-dashboard/frontend/src/App.tsx
- [ ] T061 Verify empty state handling (no regions, zero counts) across all widgets
- [ ] T062 Run quickstart.md validation - test full setup from scratch

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 (Phase 3): No dependencies on other stories - **MVP TARGET**
  - US2-US6 (Phase 4-8): Can proceed in parallel after US1, or sequentially
  - US7 (Phase 9): Can be done anytime after Foundational, lower priority
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (View Dashboard) | Foundational | Phase 2 complete |
| US2 (Filter Hierarchy) | US1 (uses GlobalFilterPanel) | T017 complete |
| US3 (Time Mode) | US1, US2 (uses GlobalFilterPanel) | T026 complete |
| US4 (COC Trend Detail) | US1 (uses COCTrendChart) | T020 complete |
| US5 (Gauges Detail) | US1 (uses KPIGauges) | T019 complete |
| US6 (Matrix Detail) | US1 (uses ProjectMatrix) | T022 complete |
| US7 (Responsive) | US1 (uses DashboardShell) | T016 complete |

### Parallel Opportunities

**Within Phase 1 (Setup)**:
- T003, T004, T005, T006 can run in parallel

**Within Phase 2 (Foundational)**:
- T011, T014, T015 can run in parallel

**Within User Story 1 (Phase 3)**:
- T017, T018, T019, T020, T021 can run in parallel (different components)

**Across User Stories**:
- After Foundational, US4, US5, US6 can be done in parallel (different widgets)
- US7 can be done in parallel with any other story

---

## Parallel Example: User Story 1

```bash
# Launch all independent widget components together:
Task: "Create placeholder GlobalFilterPanel component in .../GlobalFilterPanel.tsx"
Task: "Create GaugeChart component in .../GaugeChart.tsx"
Task: "Create KPIGauges widget in .../KPIGauges.tsx"
Task: "Create COCTrendChart component in .../COCTrendChart.tsx"
Task: "Create MatrixCell component in .../MatrixCell.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Load dashboard, verify all 4 widgets render
5. Deploy/demo if ready - CCO can view "ALL" data

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → **MVP: Basic dashboard view**
3. Add User Story 2 → Hierarchy filtering enabled
4. Add User Story 3 → Time mode switching enabled
5. Add User Stories 4-6 → Widget polish and detail
6. Add User Story 7 → Responsive/iframe polish
7. Each story adds value without breaking previous stories

### Suggested MVP Scope

**Minimal Demo**: Phase 1 + Phase 2 + Phase 3 (User Story 1)
- Total tasks: 24 tasks (T001-T024)
- Delivers: Dashboard with all widgets showing "ALL" data
- Test: Load page, verify 4 widgets visible with mock data

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths relative to: `etl-cco-dashboard/frontend/`
