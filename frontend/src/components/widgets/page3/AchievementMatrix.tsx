import { Title, Table, Text } from '@mantine/core';
import type { MatrixRow } from '@/types/page3';

interface AchievementMatrixProps {
  data: MatrixRow[];
}

interface CellProps {
  value: number;
  bucketKey: string;
}

function MatrixCell({ value, bucketKey }: CellProps) {
  if (value === 0) {
    return (
      <Table.Td ta="center" style={{ backgroundColor: '#f8f9fa' }}>
        <Text size="sm" c="dimmed">
          -
        </Text>
      </Table.Td>
    );
  }

  // Calculate color intensity based on value
  const maxValue = 6; // Reasonable max for color scaling
  const intensity = Math.min(value / maxValue, 1);

  let backgroundColor = '#f8f9fa';
  if (bucketKey === 'gt_120') {
    // Dark blue for over-achievement
    backgroundColor = `rgba(34, 139, 230, ${0.2 + intensity * 0.6})`;
  } else if (bucketKey === '100_120') {
    // Light blue
    backgroundColor = `rgba(34, 139, 230, ${0.1 + intensity * 0.4})`;
  } else if (bucketKey === '85_100') {
    // Green
    backgroundColor = `rgba(64, 192, 87, ${0.1 + intensity * 0.5})`;
  } else if (bucketKey === '60_85') {
    // Amber/yellow
    backgroundColor = `rgba(250, 176, 5, ${0.1 + intensity * 0.5})`;
  } else if (bucketKey === 'lt_60') {
    // Red
    backgroundColor = `rgba(250, 82, 82, ${0.2 + intensity * 0.6})`;
  }

  return (
    <Table.Td ta="center" style={{ backgroundColor }}>
      <Text size="sm" fw={600}>
        {value}
      </Text>
    </Table.Td>
  );
}

export function AchievementMatrix({ data }: AchievementMatrixProps) {
  const bucketLabels = [
    { key: 'gt_120', label: '>120%' },
    { key: '100_120', label: '100-120%' },
    { key: '85_100', label: '85-100%' },
    { key: '60_85', label: '60-85%' },
    { key: 'lt_60', label: '<60%' },
  ];

  return (
    <div>
      <Title order={4} mb="md">
        No. of Projects based on Achievement
      </Title>
      <Table striped withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Zone</Table.Th>
            {bucketLabels.map((bucket) => (
              <Table.Th key={bucket.key} ta="center">
                {bucket.label}
              </Table.Th>
            ))}
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {data.map((row) => (
            <Table.Tr key={row.id}>
              <Table.Td fw={600}>{row.label}</Table.Td>
              {bucketLabels.map((bucket) => (
                <MatrixCell
                  key={bucket.key}
                  value={row.buckets[bucket.key as keyof typeof row.buckets]}
                  bucketKey={bucket.key}
                />
              ))}
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </div>
  );
}
