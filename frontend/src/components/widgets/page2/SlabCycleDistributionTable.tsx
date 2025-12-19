import { useState } from 'react';
import { Title, Table, Text, ActionIcon, Group } from '@mantine/core';
import { IconChevronRight, IconChevronDown } from '@tabler/icons-react';
import type { DistributionRow } from '@/types/page2';

interface SlabCycleDistributionTableProps {
  data: DistributionRow[];
}

interface RowProps {
  row: DistributionRow;
  level: number;
}

function TableRow({ row, level }: RowProps) {
  const [expanded, setExpanded] = useState(false);
  const hasChildren = row.children && row.children.length > 0;

  const indent = level * 20;

  const labelStyle = {
    paddingLeft: `${indent}px`,
    fontWeight: row.type === 'zone' ? 700 : row.type === 'region' ? 600 : 500,
  };

  return (
    <>
      <Table.Tr style={{ backgroundColor: row.type === 'zone' ? '#f8f9fa' : undefined }}>
        <Table.Td style={labelStyle}>
          <Group gap="xs" wrap="nowrap">
            {hasChildren ? (
              <ActionIcon
                size="sm"
                variant="subtle"
                onClick={() => setExpanded(!expanded)}
                aria-label={expanded ? 'Collapse' : 'Expand'}
              >
                {expanded ? <IconChevronDown size={16} /> : <IconChevronRight size={16} />}
              </ActionIcon>
            ) : (
              <div style={{ width: 28 }} />
            )}
            <Text size="sm">{row.label}</Text>
          </Group>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm" fw={500}>
            {row.no_of_slabs}
          </Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm" fw={500}>
            {row.avg_slab_cycle}
          </Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm">{row.buckets.upto_7}</Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm">{row.buckets['7_10']}</Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm">{row.buckets['11_14']}</Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm">{row.buckets['15_20']}</Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm">{row.buckets['21_25']}</Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm">{row.buckets['26_30']}</Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm">{row.buckets.gt_30}</Text>
        </Table.Td>
      </Table.Tr>

      {expanded &&
        hasChildren &&
        row.children!.map((child) => <TableRow key={child.id} row={child} level={level + 1} />)}
    </>
  );
}

export function SlabCycleDistributionTable({ data }: SlabCycleDistributionTableProps) {
  return (
    <div>
      <Title order={4} mb="md">
        Slab Cycle Distribution
      </Title>
      <div style={{ overflowX: 'auto' }}>
        <Table striped withTableBorder withColumnBorders fontSize="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Zone / Region / Project</Table.Th>
              <Table.Th ta="center">
                No. of
                <br />
                Slabs
              </Table.Th>
              <Table.Th ta="center">
                Avg.
                <br />
                Slab Cycle
              </Table.Th>
              <Table.Th ta="center">
                Upto 7<br />
                Days
              </Table.Th>
              <Table.Th ta="center">
                7-10
                <br />
                Days
              </Table.Th>
              <Table.Th ta="center">
                11-14
                <br />
                Days
              </Table.Th>
              <Table.Th ta="center">
                15-20
                <br />
                Days
              </Table.Th>
              <Table.Th ta="center">
                21-25
                <br />
                Days
              </Table.Th>
              <Table.Th ta="center">
                26-30
                <br />
                Days
              </Table.Th>
              <Table.Th ta="center">
                {'>'}30
                <br />
                Days
              </Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.map((row) => (
              <TableRow key={row.id} row={row} level={0} />
            ))}
          </Table.Tbody>
        </Table>
      </div>
    </div>
  );
}
