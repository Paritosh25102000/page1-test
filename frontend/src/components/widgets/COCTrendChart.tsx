import Chart from 'react-apexcharts';
import { Stack, Title, Box } from '@mantine/core';
import type { ApexOptions } from 'apexcharts';
import { useDashboard } from '@/context/DashboardContext';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import type { TrendPoint } from '@/types/dashboard';

export function COCTrendChart() {
  const { currentData, state } = useDashboard();
  const { timeMode } = state;

  if (state.loading) {
    return <LoadingSpinner />;
  }

  if (state.error) {
    return <ErrorMessage message={state.error} />;
  }

  if (!currentData?.coc_trend) {
    return <ErrorMessage message="No trend data available" />;
  }

  // Select the correct series based on time mode
  const seriesKey = timeMode === 'FY' ? 'fy_series' : timeMode === 'Quarter' ? 'quarter_series' : 'month_series';
  const trendData: TrendPoint[] = currentData.coc_trend[seriesKey] || [];

  const categories = trendData.map((point) => point.label);
  const planCostData = trendData.map((point) => point.plan_cost);
  const actualCostData = trendData.map((point) => point.actual_cost);
  const cummPlanData = trendData.map((point) => point.cumm_plan ?? null);
  const cummActualData = trendData.map((point) => point.cumm_actual ?? null);

  const options: ApexOptions = {
    chart: {
      type: 'line',
      toolbar: {
        show: false,
      },
      redrawOnParentResize: true,
    },
    stroke: {
      width: [0, 0, 2, 2],
      curve: 'smooth',
    },
    plotOptions: {
      bar: {
        columnWidth: '50%',
      },
    },
    colors: ['#228be6', '#40c057', '#1971c2', '#2f9e44'],
    xaxis: {
      categories,
      labels: {
        rotate: -45,
        style: {
          fontSize: '10px',
        },
      },
    },
    yaxis: [
      {
        title: {
          text: 'Periodic Cost',
        },
        labels: {
          formatter: (value: number) => (value ? `${(value / 1000000).toFixed(1)}M` : ''),
        },
      },
      {
        opposite: true,
        title: {
          text: 'Cumulative Cost',
        },
        labels: {
          formatter: (value: number) => (value ? `${(value / 1000000).toFixed(1)}M` : ''),
        },
      },
    ],
    legend: {
      position: 'top',
      horizontalAlign: 'center',
    },
    tooltip: {
      shared: true,
      intersect: false,
      y: {
        formatter: (value: number) => (value ? `₹${(value / 1000000).toFixed(2)}M` : '-'),
      },
    },
  };

  const series = [
    {
      name: 'Plan Cost',
      type: 'bar',
      data: planCostData,
    },
    {
      name: 'Actual Cost',
      type: 'bar',
      data: actualCostData,
    },
    {
      name: 'Cumm Plan',
      type: 'line',
      data: cummPlanData,
    },
    {
      name: 'Cumm Actual',
      type: 'line',
      data: cummActualData,
    },
  ];

  return (
    <Stack h="100%" gap={0}>
      <Title order={5} mb="xs">
        COC Trend ({timeMode === 'FY' ? 'Financial Year' : timeMode === 'Quarter' ? 'Quarterly' : 'Monthly'})
      </Title>
      <Box style={{ flex: 1 }}>
        <Chart options={options} series={series} type="line" height="100%" />
      </Box>
    </Stack>
  );
}
