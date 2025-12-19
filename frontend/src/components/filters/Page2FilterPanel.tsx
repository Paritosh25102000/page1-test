import { Group, Select, Text, Stack, Flex, SegmentedControl } from '@mantine/core';
import { useDashboard } from '@/context/DashboardContext';
import { TimeModeToggle } from './TimeModeToggle';
import { usePage2Data } from '@/hooks/usePage2Data';

export function Page2FilterPanel() {
  const {
    state,
    setZone,
    setRegion,
    setProject,
    setTimeMode,
    setPage2TypicalMode,
    setPage2FormworkType,
  } = useDashboard();
  const { filters, timeMode, data, page2Filters } = state;
  const { data: page2Data } = usePage2Data();

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

  // Get formwork types from page 2 data
  const formworkTypes = page2Data?.controls.formwork_types
    ? [
        { value: 'all', label: 'All' },
        ...page2Data.controls.formwork_types.map((f) => ({ value: f.id, label: f.name })),
      ]
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

          {/* Page 2 Specific: Formwork Type */}
          <Select
            label="Formwork Type"
            data={formworkTypes}
            value={page2Filters.formworkType || 'all'}
            onChange={(value) => setPage2FormworkType(value === 'all' ? null : value)}
            size="sm"
            w={{ base: '100%', sm: 200 }}
          />
        </Group>

        {/* Right side: Time Mode + Typical Mode */}
        <Group gap="md" wrap="wrap">
          {/* Page 2 Specific: Typical/Non-Typical Toggle */}
          <div>
            <Text size="xs" fw={500} mb={4}>
              Floor Type
            </Text>
            <SegmentedControl
              size="sm"
              value={page2Filters.typicalMode}
              onChange={(value) =>
                setPage2TypicalMode(value as 'typical' | 'non-typical' | 'all')
              }
              data={[
                { value: 'all', label: 'All' },
                { value: 'typical', label: 'Typical' },
                { value: 'non-typical', label: 'Non-Typical' },
              ]}
            />
          </div>

          <TimeModeToggle value={timeMode} onChange={setTimeMode} />
        </Group>
      </Flex>
    </Stack>
  );
}
