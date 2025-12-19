import { Box, Title, Stack, Paper, Grid } from '@mantine/core';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { usePage2Data } from '@/hooks/usePage2Data';
import { Page2FilterPanel } from '@/components/filters/Page2FilterPanel';
import { RegionSlabCycleChart } from '@/components/widgets/page2/RegionSlabCycleChart';
import { TechnologySlabCycleChart } from '@/components/widgets/page2/TechnologySlabCycleChart';
import { SlabCycleDistributionTable } from '@/components/widgets/page2/SlabCycleDistributionTable';
import { TopProjectsCard } from '@/components/widgets/page2/TopProjectsCard';

export function Page2Shell() {
  const { data, loading, error } = usePage2Data();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!data) {
    return <ErrorMessage message="No data available" />;
  }

  const nodeData = data.dashboard_data.ALL;

  return (
    <Box
      p={{ base: 'xs', sm: 'md' }}
      style={{
        minHeight: '100%',
        overflow: 'auto',
        backgroundColor: 'var(--mantine-color-gray-0)',
      }}
    >
      <Stack gap="md" maw={1920} mx="auto">
        <Title order={2}>Slab Cycle Analysis</Title>

        {/* Filter Panel */}
        <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
          <Page2FilterPanel />
        </Paper>

        {/* Top Row: Charts */}
        <Grid gutter={{ base: 'xs', sm: 'md' }}>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} h={400} withBorder>
              <RegionSlabCycleChart data={nodeData.region_slab_cycle} />
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 6 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} h={400} withBorder>
              <TechnologySlabCycleChart data={nodeData.technology_slab_cycle} />
            </Paper>
          </Grid.Col>
        </Grid>

        {/* Bottom Row: Table and Top Projects */}
        <Grid gutter={{ base: 'xs', sm: 'md' }}>
          <Grid.Col span={{ base: 12, md: 8 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
              <SlabCycleDistributionTable data={nodeData.slab_cycle_distribution.rows} />
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 4 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
              <TopProjectsCard data={nodeData.top_projects} />
            </Paper>
          </Grid.Col>
        </Grid>
      </Stack>
    </Box>
  );
}
