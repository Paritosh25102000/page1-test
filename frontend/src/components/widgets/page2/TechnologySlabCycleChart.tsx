import { Title } from '@mantine/core';
import ReactApexChart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';
import type { TechnologySlabCycle } from '@/types/page2';

interface TechnologySlabCycleChartProps {
  data: TechnologySlabCycle[];
}

export function TechnologySlabCycleChart({ data }: TechnologySlabCycleChartProps) {
  // Shorten technology names for better display
  const shortNames = data.map((item) => {
    const name = item.technology;
    if (name.includes('Aluform Typical')) return 'Aluform Typical';
    if (name.includes('Conventional')) return 'Conventional';
    if (name.includes('Non-Typical')) return 'Aluform Non-Typical';
    if (name.includes('2nd set')) return 'Aluform 2nd set';
    if (name.includes('1st set')) return 'Aluform 1st set';
    if (name.includes('Con +')) return 'Con + Aluform';
    return name;
  });

  const chartOptions: ApexOptions = {
    chart: {
      type: 'line',
      toolbar: { show: false },
      fontFamily: 'inherit',
    },
    stroke: {
      width: [0, 3],
      curve: 'smooth',
    },
    plotOptions: {
      bar: {
        columnWidth: '50%',
        borderRadius: 4,
      },
    },
    dataLabels: {
      enabled: true,
      enabledOnSeries: [1],
      style: {
        fontSize: '11px',
      },
    },
    xaxis: {
      categories: shortNames,
      labels: {
        style: {
          fontSize: '10px',
        },
        rotate: -45,
        rotateAlways: true,
      },
    },
    yaxis: [
      {
        title: {
          text: 'No of Slabs',
          style: {
            fontSize: '12px',
          },
        },
        labels: {
          formatter: (val) => Math.round(val).toString(),
        },
      },
      {
        opposite: true,
        title: {
          text: 'Avg Slab Cycle (Days)',
          style: {
            fontSize: '12px',
          },
        },
        labels: {
          formatter: (val) => Math.round(val).toString(),
        },
      },
    ],
    colors: ['#228BE6', '#FD7E14'],
    legend: {
      position: 'top',
      horizontalAlign: 'left',
    },
    tooltip: {
      shared: true,
      intersect: false,
      y: [
        {
          formatter: (val) => `${val} slabs`,
        },
        {
          formatter: (val) => `${val} days`,
        },
      ],
    },
    grid: {
      strokeDashArray: 4,
    },
  };

  const series = [
    {
      name: 'No of Slabs',
      type: 'column',
      data: data.map((item) => item.no_of_slabs),
    },
    {
      name: 'Average of Slab Cycle',
      type: 'line',
      data: data.map((item) => item.avg_slab_cycle),
    },
  ];

  return (
    <div>
      <Title order={4} mb="md">
        Technology-wise Slab Cycle Avg & No. of Slabs
      </Title>
      <ReactApexChart options={chartOptions} series={series} type="line" height={320} />
    </div>
  );
}
