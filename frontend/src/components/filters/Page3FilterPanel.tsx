import { Group, Select, Text, Stack, Flex } from '@mantine/core';
import { useDashboard } from '@/context/DashboardContext';
import { TimeModeToggle } from './TimeModeToggle';
import { usePage3Data } from '@/hooks/usePage3Data';

export function Page3FilterPanel() {
  const { state, setZone, setRegion, setProject, setTimeMode, setPage3Activity } = useDashboard();
  const { filters, timeMode, data, page3Filters } = state;
  const { data: page3Data } = usePage3Data();

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

  // Get activities from page 3 data
  const activities = page3Data?.controls.activities
    ? page3Data.controls.activities.map((a) => ({ value: a.id, label: a.name }))
    : [{ value: 'all', label: 'All Activities' }];

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

          {/* Page 3 Specific: Activity */}
          <Select
            label="Activity"
            data={activities}
            value={page3Filters.activity || 'all'}
            onChange={(value) => setPage3Activity(value === 'all' ? null : value)}
            size="sm"
            w={{ base: '100%', sm: 180 }}
          />
        </Group>

        {/* Right side: Time Mode */}
        <TimeModeToggle value={timeMode} onChange={setTimeMode} />
      </Flex>
    </Stack>
  );
}
