import { Group, Select, Text, Stack, Flex, SegmentedControl } from '@mantine/core';
import { useDashboard } from '@/context/DashboardContext';
import { usePage4Data } from '@/hooks/usePage4Data';

export function Page4FilterPanel() {
  const {
    state,
    setZone,
    setRegion,
    setProject,
    setPage4AlphaStatus,
    setPage4ReraStatus,
  } = useDashboard();
  const { filters, data, page4Filters } = state;
  const { data: page4Data } = usePage4Data();

  // Get available options from hierarchy tree (from page 1 data)
  const zones = data?.controls.hierarchy_tree
    ? Object.keys(data.controls.hierarchy_tree).map((id) => ({ value: id, label: id }))
    : [];

  const regions =
    filters.zone && data?.controls.hierarchy_tree?.[filters.zone]
      ? Object.keys(data.controls.hierarchy_tree[filters.zone]).map((id) => ({ value: id, label: id }))
      : [];

  const projects =
    filters.zone && filters.region && data?.controls.hierarchy_tree?.[filters.zone]?.[filters.region]
      ? data.controls.hierarchy_tree[filters.zone][filters.region].map((p) => ({
          value: p.id,
          label: p.name,
        }))
      : [];

  // Get RERA status options from page 4 data
  const reraStatuses = page4Data?.controls.rera_status
    ? page4Data.controls.rera_status.map((r) => ({ value: r.id, label: r.name }))
    : [{ value: 'all', label: 'All' }];

  return (
    <Stack gap="xs">
      <Text fw={500} size="sm">
        Filters
      </Text>
      <Flex
        gap="md"
        wrap="wrap"
        justify="space-between"
        align="flex-end"
        direction={{ base: 'column', sm: 'row' }}
      >
        {/* Common Hierarchy Dropdowns */}
        <Group gap="md" wrap="wrap">
          <Select
            label="Zone"
            placeholder="All Zones"
            data={zones}
            value={filters.zone}
            onChange={(value) => setZone(value)}
            clearable
            size="sm"
            w={{ base: '100%', sm: 150 }}
          />

          <Select
            label="Region"
            placeholder="All Regions"
            data={regions}
            value={filters.region}
            onChange={(value) => setRegion(value)}
            clearable
            disabled={!filters.zone}
            size="sm"
            w={{ base: '100%', sm: 150 }}
          />

          <Select
            label="Project"
            placeholder="All Projects"
            data={projects}
            value={filters.project}
            onChange={(value) => setProject(value)}
            clearable
            disabled={!filters.region}
            size="sm"
            w={{ base: '100%', sm: 200 }}
          />

          {/* Page 4 Specific: RERA Status */}
          <Select
            label="RERA Status"
            data={reraStatuses}
            value={page4Filters.reraStatus || 'all'}
            onChange={(value) => setPage4ReraStatus(value === 'all' ? null : value)}
            size="sm"
            w={{ base: '100%', sm: 180 }}
          />
        </Group>

        {/* Right side: Alpha Status */}
        <div>
          <Text size="xs" fw={500} mb={4}>
            Alpha Status
          </Text>
          <SegmentedControl
            size="sm"
            value={page4Filters.alphaStatus}
            onChange={(value) => setPage4AlphaStatus(value as 'alpha' | 'non-alpha' | 'all')}
            data={[
              { value: 'all', label: 'All' },
              { value: 'alpha', label: 'Alpha' },
              { value: 'non-alpha', label: 'Non-Alpha' },
            ]}
          />
        </div>
      </Flex>
    </Stack>
  );
}
