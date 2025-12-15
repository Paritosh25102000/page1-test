import type { StatusColor } from '@/types/dashboard';

/**
 * Gauge threshold configuration
 */
export const GAUGE_THRESHOLDS = {
  RED_MAX: 85,
  AMBER_MAX: 95,
} as const;

/**
 * Get status color based on percentage
 * - Red: < 85%
 * - Amber: 85% - 95%
 * - Green: > 95%
 */
export function getStatusColor(pct: number): StatusColor {
  if (pct < GAUGE_THRESHOLDS.RED_MAX) return 'red';
  if (pct < GAUGE_THRESHOLDS.AMBER_MAX) return 'amber';
  return 'green';
}

/**
 * Get hex color code for status
 */
export function getStatusHexColor(status: StatusColor): string {
  switch (status) {
    case 'red':
      return '#fa5252';
    case 'amber':
      return '#fab005';
    case 'green':
      return '#40c057';
  }
}

/**
 * Get hex color code for a percentage value
 */
export function getColorForPercentage(pct: number): string {
  return getStatusHexColor(getStatusColor(pct));
}
