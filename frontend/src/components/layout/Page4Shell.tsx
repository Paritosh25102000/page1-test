import { Box, Title, Stack, Paper, Grid } from '@mantine/core';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { usePage4Data } from '@/hooks/usePage4Data';
import { Page4FilterPanel } from '@/components/filters/Page4FilterPanel';
import { SlabGapChart } from '@/components/widgets/page4/SlabGapChart';
import { FinishingActivitiesTable } from '@/components/widgets/page4/FinishingActivitiesTable';

export function Page4Shell() {
  const { data, loading, error } = usePage4Data();

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
        <Title order={2}>Finishing Activities</Title>

        {/* Filter Panel */}
        <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
          <Page4FilterPanel />
        </Paper>

        {/* Charts Grid - Top Row */}
        <Grid gutter={{ base: 'xs', sm: 'md' }}>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
              <SlabGapChart
                title="Blockwork Slab Gaps"
                data={nodeData.slab_gap_charts.blockwork.chart_data}
              />
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 6 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
              <SlabGapChart
                title="Internal Plaster Slab Gaps"
                data={nodeData.slab_gap_charts.internal_plaster.chart_data}
              />
            </Paper>
          </Grid.Col>
        </Grid>

        {/* Charts Grid - Second Row */}
        <Grid gutter={{ base: 'xs', sm: 'md' }}>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
              <SlabGapChart
                title="Toilet Flooring Slab Gaps"
                data={nodeData.slab_gap_charts.toilet_flooring.chart_data}
              />
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 6 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
              <SlabGapChart
                title="Flat Flooring Slab Gaps"
                data={nodeData.slab_gap_charts.flat_flooring.chart_data}
              />
            </Paper>
          </Grid.Col>
        </Grid>

        {/* Table - Bottom */}
        <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
          <FinishingActivitiesTable data={nodeData.finishing_table.rows} />
        </Paper>
      </Stack>
    </Box>
  );
}
