import { useState } from 'react';
import { Title, Table, Text, ActionIcon, Group } from '@mantine/core';
import { IconChevronRight, IconChevronDown } from '@tabler/icons-react';
import type { FinishingRow } from '@/types/page4';

interface FinishingActivitiesTableProps {
  data: FinishingRow[];
}

interface RowProps {
  row: FinishingRow;
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
            {row.blockwork.toFixed(1)}
          </Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm" fw={500}>
            {row.plaster.toFixed(1)}
          </Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm" fw={500}>
            {row.toilet_flooring.toFixed(1)}
          </Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm" fw={500}>
            {row.flat_flooring.toFixed(1)}
          </Text>
        </Table.Td>
      </Table.Tr>

      {expanded &&
        hasChildren &&
        row.children!.map((child) => <TableRow key={child.id} row={child} level={level + 1} />)}
    </>
  );
}

export function FinishingActivitiesTable({ data }: FinishingActivitiesTableProps) {
  return (
    <div>
      <Title order={4} mb="md">
        Finishing Activities Slab Gaps
      </Title>
      <div style={{ overflowX: 'auto' }}>
        <Table striped withTableBorder withColumnBorders fontSize="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Zone / Region / Project</Table.Th>
              <Table.Th ta="center">Blockwork</Table.Th>
              <Table.Th ta="center">Plaster</Table.Th>
              <Table.Th ta="center">
                Toilet flooring /
                <br />
                dado
              </Table.Th>
              <Table.Th ta="center">Flat Flooring</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.map((row) => (
              <TableRow key={row.id} row={row} level={0} />
            ))}
            <Table.Tr style={{ backgroundColor: '#e7f5ff', fontWeight: 600 }}>
              <Table.Td>Total</Table.Td>
              <Table.Td ta="center">
                {(data.reduce((sum, row) => sum + row.blockwork, 0) / data.length).toFixed(1)}
              </Table.Td>
              <Table.Td ta="center">
                {(data.reduce((sum, row) => sum + row.plaster, 0) / data.length).toFixed(1)}
              </Table.Td>
              <Table.Td ta="center">
                {(data.reduce((sum, row) => sum + row.toilet_flooring, 0) / data.length).toFixed(1)}
              </Table.Td>
              <Table.Td ta="center">
                {(data.reduce((sum, row) => sum + row.flat_flooring, 0) / data.length).toFixed(1)}
              </Table.Td>
            </Table.Tr>
          </Table.Tbody>
        </Table>
      </div>
    </div>
  );
}
