import { Box, Title, Stack, Paper, Grid } from '@mantine/core';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { usePage3Data } from '@/hooks/usePage3Data';
import { Page3FilterPanel } from '@/components/filters/Page3FilterPanel';
import { FloorAchievementTable } from '@/components/widgets/page3/FloorAchievementTable';
import { AchievementMatrix } from '@/components/widgets/page3/AchievementMatrix';
import { TopBottomProjectsCards } from '@/components/widgets/page3/TopBottomProjectsCards';

export function Page3Shell() {
  const { data, loading, error } = usePage3Data();

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
        <Title order={2}>Floor Achievement Analysis</Title>

        {/* Filter Panel */}
        <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
          <Page3FilterPanel />
        </Paper>

        {/* Main Grid */}
        <Grid gutter={{ base: 'xs', sm: 'md' }}>
          {/* Left: Floor Achievement Table */}
          <Grid.Col span={{ base: 12, md: 7 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
              <FloorAchievementTable data={nodeData.floor_achievement_table.rows} />
            </Paper>
          </Grid.Col>

          {/* Right: Achievement Matrix */}
          <Grid.Col span={{ base: 12, md: 5 }}>
            <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
              <AchievementMatrix data={nodeData.achievement_matrix.rows} />
            </Paper>
          </Grid.Col>

          {/* Bottom: Top & Bottom Projects */}
          <Grid.Col span={12}>
            <TopBottomProjectsCards
              topProjects={nodeData.top_projects}
              bottomProjects={nodeData.bottom_projects}
            />
          </Grid.Col>
        </Grid>
      </Stack>
    </Box>
  );
}
