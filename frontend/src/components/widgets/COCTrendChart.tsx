import Chart from 'react-apexcharts';
import { Stack, Title, Box } from '@mantine/core';
import type { ApexOptions } from 'apexcharts';
import { useDashboard } from '@/context/DashboardContext';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { formatIndianCurrency, formatIndianAxisLabel } from '@/utils/indianFormat';
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

  // Convert sort_date to display format (DD-MMM) for Quarter/Month views
  const formatDateLabel = (sortDate: string): string => {
    const date = new Date(sortDate);
    const day = date.getDate().toString().padStart(2, '0');
    const month = date.toLocaleString('en-US', { month: 'short' });
    return `${day}-${month}`;
  };

  // Use sort_date for Quarter/Month, label for FY
  const categories = trendData.map((point) =>
    timeMode === 'FY' ? point.label : formatDateLabel(point.sort_date)
  );
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
        rotateAlways: true,
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
          formatter: (value: number) => formatIndianAxisLabel(value),
        },
      },
      {
        opposite: true,
        title: {
          text: 'Cumulative Cost',
        },
        labels: {
          formatter: (value: number) => formatIndianAxisLabel(value),
        },
      },
    ],
    legend: {
      position: 'top',
      horizontalAlign: 'center',
      floating: false,
      offsetY: 0,
      height: 30,
      itemMargin: {
        horizontal: 12,
        vertical: 0,
      },
      markers: {
        size: 6,
        offsetX: -2,
      },
      fontSize: '11px',
    },
    tooltip: {
      shared: true,
      intersect: false,
      y: {
        formatter: (value: number) => formatIndianCurrency(value),
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
