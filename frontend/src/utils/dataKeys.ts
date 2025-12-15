import type { FilterState, DataKey } from '@/types/dashboard';

/**
 * Construct data key from filter state
 * Pattern: "ALL" | "ZONE_{id}" | "REG_{id}" | "PROJ_{id}"
 */
export function buildDataKey(filters: FilterState): DataKey {
  if (filters.project) return `PROJ_${filters.project}`;
  if (filters.region) return `REG_${filters.region}`;
  if (filters.zone) return `ZONE_${filters.zone}`;
  return 'ALL';
}

/**
 * Parse a data key back into its type and ID
 */
export function parseDataKey(key: DataKey): { type: 'ALL' | 'ZONE' | 'REG' | 'PROJ'; id: string | null } {
  if (key === 'ALL') return { type: 'ALL', id: null };

  const [type, ...idParts] = key.split('_');
  const id = idParts.join('_');

  return {
    type: type as 'ZONE' | 'REG' | 'PROJ',
    id: id || null,
  };
}
