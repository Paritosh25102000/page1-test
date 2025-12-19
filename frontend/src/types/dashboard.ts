/**
 * TypeScript interfaces for Page 1 Executive Summary Dashboard
 * Generated from: page1-executive-summary.json schema
 * Date: 2025-12-15
 */

// =============================================================================
// Root Types
// =============================================================================

export interface DashboardData {
  meta: Meta;
  controls: Controls;
  dashboard_data: Record<DataKey, NodeData>;
}

export interface Meta {
  generated_at: string; // ISO 8601 datetime
  data_version?: string;
  currency_unit?: string; // Default: "INR"
}

// =============================================================================
// Controls (Filter & Time Configuration)
// =============================================================================

export interface Controls {
  hierarchy_tree: HierarchyTree;
  time_modes: TimeModes;
}

/**
 * Nested Zone → Region → Project structure
 * Example: { "MZ": { "MZ1": [{ id: "Horizon", name: "Horizon" }] } }
 */
export type HierarchyTree = Record<string, Record<string, Project[]>>;

export interface Project {
  id: string;
  name: string;
}

export interface TimeModes {
  fy: TimeMode;
  quarter: TimeMode;
  month: TimeMode;
}

export interface TimeMode {
  label: string;
  start: string; // YYYY-MM-DD
  end: string; // YYYY-MM-DD
  resolution: 'month' | 'week';
}

// =============================================================================
// Data Keys
// =============================================================================

/**
 * Pattern for dashboard_data keys:
 * - "ALL" - Global aggregate
 * - "ZONE_{id}" - Zone-level aggregate (e.g., "ZONE_MZ")
 * - "REG_{id}" - Region-level aggregate (e.g., "REG_MZ1")
 * - "PROJ_{id}" - Project-level data (e.g., "PROJ_Horizon")
 */
export type DataKey = string;

// =============================================================================
// Node Data (Per Filter Selection)
// =============================================================================

export interface NodeData {
  kpi_gauges: KPIGauges;
  coc_trend: COCTrend;
  project_matrix: ProjectMatrix;
}

// =============================================================================
// KPI Gauges (PG1-WIDGET-03)
// =============================================================================

export interface KPIGauges {
  aop: TimeModeGaugeData;
  sprint: TimeModeGaugeData;
}

/**
 * Gauge data structured by time mode
 */
export interface TimeModeGaugeData {
  fy: GaugeData;
  quarter: GaugeData;
  month: GaugeData;
}

export interface GaugeData {
  achieved_pct: number;
  status_color: StatusColor;
  actual: number;
  plan: number;
  tasks_with_sprint: number;
}

export type StatusColor = 'red' | 'amber' | 'green';

// =============================================================================
// COC Trend (PG1-WIDGET-01)
// =============================================================================

export interface COCTrend {
  fy_series: TrendPoint[];
  quarter_series: TrendPoint[];
  month_series: TrendPoint[];
}

export interface TrendPoint {
  label: string; // X-axis label (e.g., "Apr-25", "Wk 14")
  sort_date: string; // ISO date for sorting
  plan_cost: number | null;
  actual_cost: number | null;
  cumm_plan?: number | null;
  cumm_actual?: number | null;
}

// =============================================================================
// Project Matrix (PG1-WIDGET-04)
// =============================================================================

export interface ProjectMatrix {
  rows: MatrixRow[];
}

export interface MatrixRow {
  label: string; // Row header (Zone or Region name)
  id?: string; // ID for drill-down
  buckets: Buckets;
  projects?: BucketProjects; // Project names per bucket for tooltips
}

export interface Buckets {
  gt_120: number;
  '100_120': number;
  '85_100': number;
  '60_85': number;
  lt_60: number;
}

export interface ProjectInfo {
  id: string;
  name: string;
}

export interface BucketProjects {
  gt_120?: ProjectInfo[];
  '100_120'?: ProjectInfo[];
  '85_100'?: ProjectInfo[];
  '60_85'?: ProjectInfo[];
  lt_60?: ProjectInfo[];
}

// =============================================================================
// Frontend State Types
// =============================================================================

export interface FilterState {
  zone: string | null;
  region: string | null;
  project: string | null;
}

export type TimeModeState = 'FY' | 'Quarter' | 'Month';

export interface DashboardState {
  filters: FilterState;
  timeMode: TimeModeState;
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
}

// =============================================================================
// Action Types (for Context Reducer)
// =============================================================================

export type DashboardAction =
  | { type: 'SET_ZONE'; payload: string | null }
  | { type: 'SET_REGION'; payload: string | null }
  | { type: 'SET_PROJECT'; payload: string | null }
  | { type: 'SET_TIME_MODE'; payload: TimeModeState }
  | { type: 'SET_DATA'; payload: DashboardData }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESET_FILTERS' };

// =============================================================================
// Utility Types
// =============================================================================

/**
 * Bucket column keys for matrix display
 */
export type BucketKey = keyof Buckets;

/**
 * Bucket display configuration
 */
export interface BucketConfig {
  key: BucketKey;
  label: string;
  isCritical: boolean;
}

export const BUCKET_CONFIGS: BucketConfig[] = [
  { key: 'gt_120', label: '>120%', isCritical: false },
  { key: '100_120', label: '100-120%', isCritical: false },
  { key: '85_100', label: '85-100%', isCritical: false },
  { key: '60_85', label: '60-85%', isCritical: false },
  { key: 'lt_60', label: '<60%', isCritical: true },
];

/**
 * Gauge threshold configuration
 */
export const GAUGE_THRESHOLDS = {
  RED_MAX: 85,
  AMBER_MAX: 95,
} as const;

/**
 * Get status color based on percentage
 */
export function getStatusColor(pct: number): StatusColor {
  if (pct < GAUGE_THRESHOLDS.RED_MAX) return 'red';
  if (pct < GAUGE_THRESHOLDS.AMBER_MAX) return 'amber';
  return 'green';
}

/**
 * Construct data key from filter state
 */
export function buildDataKey(filters: FilterState): DataKey {
  if (filters.project) return `PROJ_${filters.project}`;
  if (filters.region) return `REG_${filters.region}`;
  if (filters.zone) return `ZONE_${filters.zone}`;
  return 'ALL';
}
