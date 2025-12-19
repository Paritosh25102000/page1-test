import { Title } from '@mantine/core';
import ReactApexChart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';
import type { ZoneGapData } from '@/types/page4';

interface SlabGapChartProps {
  title: string;
  data: ZoneGapData[];
}

export function SlabGapChart({ title, data }: SlabGapChartProps) {
  const chartOptions: ApexOptions = {
    chart: {
      type: 'bar',
      toolbar: { show: false },
      fontFamily: 'inherit',
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '50%',
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
      formatter: (val) => Math.round(val as number).toString(),
    },
    xaxis: {
      categories: data.map((item) => item.zone),
      labels: {
        style: {
          fontSize: '11px',
        },
      },
    },
    yaxis: {
      title: {
        text: 'Slab Gap (Floors)',
        style: {
          fontSize: '12px',
        },
      },
      max: 16,
      labels: {
        formatter: (val) => Math.round(val).toString(),
      },
    },
    colors: ['#228BE6'],
    annotations: {
      yaxis: [
        {
          y: data[0]?.percentiles.p10 || 0,
          borderColor: '#FA5252',
          label: {
            text: 'PI0',
            style: {
              color: '#fff',
              background: '#FA5252',
              fontSize: '10px',
            },
          },
        },
        {
          y: data[0]?.percentiles.p11 || 0,
          borderColor: '#FD7E14',
          label: {
            text: 'PI1',
            style: {
              color: '#fff',
              background: '#FD7E14',
              fontSize: '10px',
            },
          },
        },
        {
          y: data[0]?.percentiles.p13 || 0,
          borderColor: '#74C0FC',
          label: {
            text: 'PI3',
            style: {
              color: '#fff',
              background: '#74C0FC',
              fontSize: '10px',
            },
          },
        },
        {
          y: data[0]?.percentiles.p15 || 0,
          borderColor: '#AE3EC9',
          label: {
            text: 'PI5',
            style: {
              color: '#fff',
              background: '#AE3EC9',
              fontSize: '10px',
            },
          },
        },
      ],
    },
    tooltip: {
      y: {
        formatter: (val) => `${val} floors`,
      },
    },
    grid: {
      strokeDashArray: 4,
    },
  };

  const series = [
    {
      name: 'Avg. Gap',
      data: data.map((item) => item.avg_gap),
    },
  ];

  return (
    <div>
      <Title order={5} mb="md">
        {title}
      </Title>
      <ReactApexChart options={chartOptions} series={series} type="bar" height={250} />
    </div>
  );
}
