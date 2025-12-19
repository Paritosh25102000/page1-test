/**
 * TypeScript interfaces for Page 3: Floor Achievement Analysis
 */

export interface Page3Data {
  meta: {
    generated_at: string;
    data_version: string;
    page: string;
  };
  controls: {
    activities: Activity[];
  };
  dashboard_data: {
    ALL: Page3NodeData;
  };
}

export interface Activity {
  id: string;
  name: string;
}

export interface Page3NodeData {
  floor_achievement_table: FloorAchievementTable;
  achievement_matrix: AchievementMatrix;
  top_projects: RankedProject[];
  bottom_projects: RankedProject[];
}

export interface FloorAchievementTable {
  rows: AchievementRow[];
}

export interface AchievementRow {
  label: string;
  type: 'zone' | 'region' | 'project';
  id: string;
  aop_plan: number;
  sprint_plan: number;
  actual_completed: number;
  pct_aop: number;
  pct_sprint: number;
  children?: AchievementRow[];
}

export interface AchievementMatrix {
  rows: MatrixRow[];
}

export interface MatrixRow {
  label: string;
  id: string;
  buckets: {
    gt_120: number;
    '100_120': number;
    '85_100': number;
    '60_85': number;
    lt_60: number;
  };
}

export interface RankedProject {
  rank: number;
  project: string;
  sprint_plan: number;
  actual_completed: number;
  pct_sprint: number;
}
