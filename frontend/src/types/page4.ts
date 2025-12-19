/**
 * TypeScript interfaces for Page 4: Finishing Activities Slab Gaps
 */

export interface Page4Data {
  meta: {
    generated_at: string;
    data_version: string;
    page: string;
  };
  controls: {
    alpha_status: AlphaStatus[];
    rera_status: ReraStatus[];
  };
  dashboard_data: {
    ALL: Page4NodeData;
  };
}

export interface AlphaStatus {
  id: string;
  name: string;
}

export interface ReraStatus {
  id: string;
  name: string;
}

export interface Page4NodeData {
  slab_gap_charts: SlabGapCharts;
  finishing_table: FinishingTable;
}

export interface SlabGapCharts {
  blockwork: SlabGapData;
  internal_plaster: SlabGapData;
  toilet_flooring: SlabGapData;
  flat_flooring: SlabGapData;
}

export interface SlabGapData {
  chart_data: ZoneGapData[];
}

export interface ZoneGapData {
  zone: string;
  avg_gap: number;
  percentiles: {
    p10: number;
    p11: number;
    p13: number;
    p15: number;
  };
}

export interface FinishingTable {
  rows: FinishingRow[];
}

export interface FinishingRow {
  label: string;
  type: 'zone' | 'region' | 'project';
  id: string;
  blockwork: number;
  plaster: number;
  toilet_flooring: number;
  flat_flooring: number;
  children?: FinishingRow[];
}
