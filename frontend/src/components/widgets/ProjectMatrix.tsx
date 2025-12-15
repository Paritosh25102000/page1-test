import { Stack, Title, Table, Text } from '@mantine/core';
import { MatrixCell } from './MatrixCell';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { useDashboard } from '@/context/DashboardContext';
import { BUCKET_CONFIGS, type BucketKey, type MatrixRow } from '@/types/dashboard';

export function ProjectMatrix() {
  const { currentData, state } = useDashboard();
  const { filters } = state;

  if (state.loading) {
    return <LoadingSpinner />;
  }

  if (state.error) {
    return <ErrorMessage message={state.error} />;
  }

  if (!currentData?.project_matrix?.rows) {
    return <ErrorMessage message="No matrix data available" />;
  }

  const rows: MatrixRow[] = currentData.project_matrix.rows;

  // Calculate max value for heatmap intensity
  const maxValue = Math.max(
    ...rows.flatMap((row) =>
      BUCKET_CONFIGS.map((bucket) => row.buckets[bucket.key] || 0)
    ),
    1
  );

  // Determine context label based on filter level
  const getContextLabel = () => {
    if (filters.zone && filters.region) return 'Projects';
    if (filters.zone) return 'Regions';
    return 'Zones';
  };

  return (
    <Stack gap="xs">
      <Title order={5}>Project Achievement Matrix ({getContextLabel()})</Title>
      <Table highlightOnHover withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>
              <Text fw={600} size="sm">
                {getContextLabel()}
              </Text>
            </Table.Th>
            {BUCKET_CONFIGS.map((bucket) => (
              <Table.Th key={bucket.key} style={{ textAlign: 'center' }}>
                <Text
                  fw={600}
                  size="sm"
                  c={bucket.isCritical ? 'red' : undefined}
                >
                  {bucket.label}
                </Text>
              </Table.Th>
            ))}
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {rows.map((row) => (
            <Table.Tr key={row.label}>
              <Table.Td>
                <Text fw={500} size="sm">
                  {row.label}
                </Text>
              </Table.Td>
              {BUCKET_CONFIGS.map((bucket) => (
                <Table.Td key={bucket.key} style={{ padding: '4px' }}>
                  <MatrixCell
                    value={row.buckets[bucket.key] || 0}
                    bucketKey={bucket.key as BucketKey}
                    rowId={row.id}
                    maxValue={maxValue}
                    projects={row.projects?.[bucket.key]}
                  />
                </Table.Td>
              ))}
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </Stack>
  );
}
