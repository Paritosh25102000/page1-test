import Chart from 'react-apexcharts';
import { Box } from '@mantine/core';
import type { ApexOptions } from 'apexcharts';
import { getColorForPercentage } from '@/utils/thresholds';

interface GaugeChartProps {
  value: number;
  title: string;
}

export function GaugeChart({ value, title }: GaugeChartProps) {
  const color = getColorForPercentage(value);

  const options: ApexOptions = {
    chart: {
      type: 'radialBar',
      sparkline: {
        enabled: true,
      },
      redrawOnParentResize: true,
    },
    plotOptions: {
      radialBar: {
        startAngle: -135,
        endAngle: 135,
        hollow: {
          size: '60%',
        },
        track: {
          background: '#e7e7e7',
          strokeWidth: '100%',
          margin: 5,
        },
        dataLabels: {
          name: {
            show: true,
            fontSize: '12px',
            fontWeight: 500,
            offsetY: 20,
            color: '#666',
          },
          value: {
            show: true,
            fontSize: '24px',
            fontWeight: 600,
            offsetY: -10,
            formatter: (val: number) => `${Math.round(val)}%`,
          },
        },
      },
    },
    fill: {
      type: 'solid',
      colors: [color],
    },
    stroke: {
      lineCap: 'round',
    },
    labels: [title],
  };

  const series = [Math.min(Math.max(value, 0), 100)]; // Clamp between 0-100

  return (
    <Box h="100%" w="100%">
      <Chart options={options} series={series} type="radialBar" height="100%" />
    </Box>
  );
}
