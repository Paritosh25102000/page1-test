import { Box, Grid, Paper, Title, Stack } from '@mantine/core';
import { GlobalFilterPanel } from '@/components/filters/GlobalFilterPanel';
import { COCTrendChart } from '@/components/widgets/COCTrendChart';
import { KPIGauges } from '@/components/widgets/KPIGauges';
import { ProjectMatrix } from '@/components/widgets/ProjectMatrix';

export function DashboardShell() {
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
        <Title order={2}>Executive Summary</Title>

        {/* Global Filter Panel */}
        <Paper shadow="xs" p={{ base: 'xs', sm: 'md' }} withBorder>
          <GlobalFilterPanel />
        </Paper>

        {/* Main Dashboard Grid */}
        <Grid gutter={{ base: 'xs', sm: 'md' }}>
          {/* Left Column: COC Trend Chart */}
          <Grid.Col span={{ base: 12, md: 8 }}>
            <Paper
              shadow="xs"
              p={{ base: 'xs', sm: 'md' }}
              h={{ base: 300, sm: 400 }}
              withBorder
            >
              <COCTrendChart />
            </Paper>
          </Grid.Col>

          {/* Right Column: KPI Gauges */}
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Paper
              shadow="xs"
              p={{ base: 'xs', sm: 'md' }}
              h={{ base: 250, sm: 400 }}
              withBorder
            >
              <KPIGauges />
            </Paper>
          </Grid.Col>

          {/* Full Width: Project Achievement Matrix */}
          <Grid.Col span={12}>
            <Paper
              shadow="xs"
              p={{ base: 'xs', sm: 'md' }}
              withBorder
              style={{ overflowX: 'auto' }}
            >
              <ProjectMatrix />
            </Paper>
          </Grid.Col>
        </Grid>
      </Stack>
    </Box>
  );
}
