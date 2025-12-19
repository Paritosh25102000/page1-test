# Research: Page 1 Executive Summary Dashboard

**Feature**: 001-page1-executive-summary
**Date**: 2025-12-15

## Technology Decisions

### 1. React Framework Setup

**Decision**: Vite + React 18 + TypeScript

**Rationale**:
- Vite provides fast HMR and build times, ideal for dashboard development
- React 18 offers concurrent features for responsive UI
- TypeScript ensures type safety with the JSON schema

**Alternatives considered**:
- Create React App: Slower builds, being deprecated
- Next.js: Overkill for iframe-embedded SPA, adds server complexity

### 2. UI Component Library

**Decision**: Mantine UI v7

**Rationale**:
- Product context explicitly specifies Mantine UI
- Native TypeScript support
- Built-in responsive grid system
- Select and SegmentedControl components match filter panel requirements
- Table component suitable for heatmap matrix

**Alternatives considered**:
- Material UI: Heavier bundle, more complex theming
- Chakra UI: Less enterprise-focused styling

### 3. Charting Library

**Decision**: ApexCharts (react-apexcharts)

**Rationale**:
- Product context explicitly specifies ApexCharts
- Supports combo charts (bar + line) for COC Trend
- Supports radial/gauge charts for KPI gauges
- Dual Y-axis support built-in
- Good responsive behavior

**Alternatives considered**:
- Recharts: Less gauge support
- Chart.js: Requires plugins for dual-axis and gauges
- D3: Too low-level for this use case

### 4. State Management

**Decision**: React Context API

**Rationale**:
- Product context recommends Context API due to flat, pre-aggregated data
- No complex async flows or derived state
- Simple filter state + time mode = minimal state shape
- Avoids unnecessary dependencies (Redux, Zustand)

**Alternatives considered**:
- Redux Toolkit: Overkill for this state shape
- Zustand: Good but unnecessary given simple state

### 5. Testing Strategy

**Decision**: Vitest + React Testing Library

**Rationale**:
- Vitest is Vite-native, fast, compatible with Jest API
- React Testing Library promotes testing user behavior
- Good mocking support for context and data

**Alternatives considered**:
- Jest: Requires additional config with Vite
- Cypress: E2E is out of scope for initial implementation

## Best Practices Research

### Mantine UI Patterns

1. **MantineProvider**: Wrap app root, configure theme colors for gauge thresholds
2. **Select component**: Use `data` prop with `{ value, label }` format for dropdowns
3. **SegmentedControl**: Use for time mode toggle (FY/Quarter/Month)
4. **Table component**: Use with custom cell renderers for heatmap styling
5. **Grid/SimpleGrid**: Use for responsive widget layout
6. **Loader component**: Use for widget loading states

### ApexCharts Patterns

1. **Combo Chart**: Set `type: 'line'` on chart, override individual series types
2. **Dual Y-Axis**: Configure `yaxis` as array with `opposite: true` for second axis
3. **Radial Bar**: Use `type: 'radialBar'` with `plotOptions.radialBar.startAngle/endAngle` for semi-circle
4. **Color thresholds**: Use `colors` callback function based on value
5. **Responsive**: Set `chart.redrawOnParentResize: true`

### React Context Patterns

1. **Provider pattern**: Create context with custom hook `useDashboard()`
2. **Reducer pattern**: Use reducer for complex state updates (filter changes)
3. **Memoization**: Memoize context value to prevent unnecessary rerenders
4. **Data key derivation**: Compute data key in context based on filter state

### Iframe Embedding Patterns

1. **CSS isolation**: Use `overflow: auto` on root container
2. **No viewport scrolling**: Avoid `100vh` - use `100%` height
3. **Self-contained scrolling**: Each widget or the shell manages own overflow
4. **No reliance on parent**: Avoid `window.parent` references

## Data Flow Design

```
┌─────────────────────────────────────────────────────────────┐
│                    DashboardContext                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ filterState │  │  timeMode   │  │ dashboardData (JSON)│ │
│  │ {zone,      │  │ 'FY' |      │  │ {meta, controls,    │ │
│  │  region,    │  │ 'Quarter' | │  │  dashboard_data}    │ │
│  │  project}   │  │ 'Month'     │  │                     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                     │            │
│         └────────────────┼─────────────────────┘            │
│                          │                                  │
│                   ┌──────▼──────┐                           │
│                   │ dataKey     │                           │
│                   │ "ALL" |     │                           │
│                   │ "ZONE_MZ" | │                           │
│                   │ "REG_MZ1" | │                           │
│                   │ "PROJ_X"   │                           │
│                   └──────┬──────┘                           │
│                          │                                  │
│                   ┌──────▼──────┐                           │
│                   │ currentData │  ← dashboard_data[dataKey]│
│                   │ {kpi_gauges,│                           │
│                   │  coc_trend, │                           │
│                   │  project_   │                           │
│                   │  matrix}    │                           │
│                   └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │COCTrendChart│  │ KPIGauges  │  │ProjectMatrix│
   │ coc_trend   │  │ kpi_gauges │  │project_matrix│
   │ + timeMode  │  │            │  │            │
   └────────────┘  └────────────┘  └────────────┘
```

## Resolved Questions

| Question | Resolution |
|----------|------------|
| How to handle cascading dropdowns? | Derive options from `controls.hierarchy_tree` based on parent selection |
| How to construct data keys? | Pattern: "ALL", "ZONE_{zone}", "REG_{region}", "PROJ_{project}" |
| How to handle null cost values? | ApexCharts handles nulls natively (gap in line, no bar) |
| How to apply gauge colors? | Use threshold helper: <85% red, 85-95% amber, >95% green |
| How to style matrix heatmap? | CSS background intensity based on count, red border for <60% column |
