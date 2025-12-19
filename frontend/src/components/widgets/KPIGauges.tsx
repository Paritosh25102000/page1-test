import { Stack, Title, SimpleGrid, Box } from '@mantine/core';
import { GaugeChart } from './GaugeChart';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { useDashboard } from '@/context/DashboardContext';
import type { TimeMode } from '@/types/dashboard';

export function KPIGauges() {
  const { currentData, state } = useDashboard();
  const { timeMode } = state;

  if (state.loading) {
    return <LoadingSpinner />;
  }

  if (state.error) {
    return <ErrorMessage message={state.error} />;
  }

  if (!currentData?.kpi_gauges) {
    return <ErrorMessage message="No gauge data available" />;
  }

  const { aop, sprint } = currentData.kpi_gauges;

  // Map UI time mode to data key
  const timeModeKey: 'fy' | 'quarter' | 'month' =
    timeMode === 'FY' ? 'fy' : timeMode === 'Quarter' ? 'quarter' : 'month';

  // Get time-mode specific gauge data
  const aopData = aop[timeModeKey];
  const sprintData = sprint[timeModeKey];

  if (!aopData || !sprintData) {
    return <ErrorMessage message="No gauge data for selected time mode" />;
  }

  return (
    <Stack h="100%" gap={0}>
      <Title order={5} mb="sm">
        Schedule Achievement ({timeMode})
      </Title>
      <SimpleGrid cols={2} spacing="xs" style={{ flex: 1 }}>
        <Box h="100%">
          <GaugeChart value={aopData.achieved_pct} title="AOP Achievement" />
        </Box>
        <Box h="100%">
          <GaugeChart value={sprintData.achieved_pct} title="Sprint Achievement" />
        </Box>
      </SimpleGrid>
    </Stack>
  );
}
