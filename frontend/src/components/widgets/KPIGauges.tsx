import { Stack, Title, SimpleGrid, Box } from '@mantine/core';
import { GaugeChart } from './GaugeChart';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { useDashboard } from '@/context/DashboardContext';

export function KPIGauges() {
  const { currentData, state } = useDashboard();

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

  return (
    <Stack h="100%" gap={0}>
      <Title order={5} mb="sm">
        Schedule Achievement
      </Title>
      <SimpleGrid cols={2} spacing="xs" style={{ flex: 1 }}>
        <Box h="100%">
          <GaugeChart value={aop.achieved_pct} title="AOP Achievement" />
        </Box>
        <Box h="100%">
          <GaugeChart value={sprint.achieved_pct} title="Sprint Achievement" />
        </Box>
      </SimpleGrid>
    </Stack>
  );
}
