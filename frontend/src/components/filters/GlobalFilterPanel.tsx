import { Group, Select, Text, Stack, Flex } from '@mantine/core';
import { useDashboard } from '@/context/DashboardContext';
import { TimeModeToggle } from './TimeModeToggle';

export function GlobalFilterPanel() {
  const { state, setZone, setRegion, setProject, setTimeMode } = useDashboard();
  const { filters, timeMode, data } = state;

  // Get available options from hierarchy tree
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
        {/* Hierarchy Dropdowns */}
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
            w={{ base: '100%', sm: 180 }}
          />
        </Group>

        {/* Time Mode Toggle */}
        <TimeModeToggle value={timeMode} onChange={setTimeMode} />
      </Flex>
    </Stack>
  );
}
