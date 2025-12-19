import { Title } from '@mantine/core';
import ReactApexChart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';
import type { RegionSlabCycle } from '@/types/page2';

interface RegionSlabCycleChartProps {
  data: RegionSlabCycle[];
}

export function RegionSlabCycleChart({ data }: RegionSlabCycleChartProps) {
  const chartOptions: ApexOptions = {
    chart: {
      type: 'bar',
      toolbar: { show: false },
      fontFamily: 'inherit',
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '60%',
        borderRadius: 4,
        dataLabels: {
          position: 'top',
        },
      },
    },
    dataLabels: {
      enabled: true,
      offsetY: -20,
      style: {
        fontSize: '11px',
        colors: ['#304758'],
      },
    },
    xaxis: {
      categories: data.map((item) => item.region_name),
      labels: {
        style: {
          fontSize: '11px',
        },
      },
    },
    yaxis: {
      title: {
        text: 'Average Slab Cycle (Days)',
        style: {
          fontSize: '12px',
        },
      },
      labels: {
        formatter: (val) => Math.round(val).toString(),
      },
    },
    colors: ['#228BE6'],
    tooltip: {
      y: {
        formatter: (val) => `${val} days`,
      },
    },
    grid: {
      strokeDashArray: 4,
    },
  };

  const series = [
    {
      name: 'Avg Slab Cycle',
      data: data.map((item) => item.avg_slab_cycle),
    },
  ];

  return (
    <div>
      <Title order={4} mb="md">
        Region-wise Slab Cycle Average
      </Title>
      <ReactApexChart options={chartOptions} series={series} type="bar" height={320} />
    </div>
  );
}
