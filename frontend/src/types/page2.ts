/**
 * TypeScript interfaces for Page 2: Slab Cycle Analysis
 */

export interface Page2Data {
  meta: {
    generated_at: string;
    data_version: string;
    page: string;
  };
  controls: {
    formwork_types: FormworkType[];
  };
  dashboard_data: {
    ALL: Page2NodeData;
  };
}

export interface FormworkType {
  id: string;
  name: string;
}

export interface Page2NodeData {
  region_slab_cycle: RegionSlabCycle[];
  technology_slab_cycle: TechnologySlabCycle[];
  slab_cycle_distribution: SlabCycleDistribution;
  top_projects: TopProject[];
}

export interface RegionSlabCycle {
  region_id: string;
  region_name: string;
  avg_slab_cycle: number;
}

export interface TechnologySlabCycle {
  technology: string;
  no_of_slabs: number;
  avg_slab_cycle: number;
}

export interface SlabCycleDistribution {
  rows: DistributionRow[];
}

export interface DistributionRow {
  label: string;
  type: 'zone' | 'region' | 'project';
  id: string;
  no_of_slabs: number;
  avg_slab_cycle: number;
  buckets: DistributionBuckets;
  children?: DistributionRow[];
}

export interface DistributionBuckets {
  upto_7: number;
  '7_10': number;
  '11_14': number;
  '15_20': number;
  '21_25': number;
  '26_30': number;
  gt_30: number;
}

export interface TopProject {
  rank: number;
  project: string;
  tower: string;
  slab_cycle: number;
}
