import { useState } from 'react';
import { Title, Table, Text, ActionIcon, Group, Badge } from '@mantine/core';
import { IconChevronRight, IconChevronDown } from '@tabler/icons-react';
import type { AchievementRow } from '@/types/page3';

interface FloorAchievementTableProps {
  data: AchievementRow[];
}

interface RowProps {
  row: AchievementRow;
  level: number;
}

function getPercentageColor(pct: number): string {
  if (pct < 85) return 'red';
  if (pct < 95) return 'yellow';
  if (pct < 100) return 'green';
  return 'blue';
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
            {row.aop_plan}
          </Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm" fw={500}>
            {row.sprint_plan}
          </Text>
        </Table.Td>
        <Table.Td ta="center">
          <Text size="sm" fw={600}>
            {row.actual_completed}
          </Text>
        </Table.Td>
        <Table.Td ta="center">
          <Badge color={getPercentageColor(row.pct_aop)} size="sm">
            {row.pct_aop.toFixed(1)}%
          </Badge>
        </Table.Td>
        <Table.Td ta="center">
          <Badge color={getPercentageColor(row.pct_sprint)} size="sm">
            {row.pct_sprint.toFixed(1)}%
          </Badge>
        </Table.Td>
      </Table.Tr>

      {expanded &&
        hasChildren &&
        row.children!.map((child) => <TableRow key={child.id} row={child} level={level + 1} />)}
    </>
  );
}

export function FloorAchievementTable({ data }: FloorAchievementTableProps) {
  return (
    <div>
      <Title order={4} mb="md">
        Number of Floors
      </Title>
      <div style={{ overflowX: 'auto' }}>
        <Table striped withTableBorder withColumnBorders fontSize="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Zone / Region / Project</Table.Th>
              <Table.Th ta="center">AOP Plan</Table.Th>
              <Table.Th ta="center">Sprint Plan</Table.Th>
              <Table.Th ta="center">
                Actual
                <br />
                Completed
              </Table.Th>
              <Table.Th ta="center">
                % Achieve
                <br />
                against AOP
              </Table.Th>
              <Table.Th ta="center">
                % Achieve
                <br />
                against Sprint
              </Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.map((row) => (
              <TableRow key={row.id} row={row} level={0} />
            ))}
            <Table.Tr style={{ backgroundColor: '#e7f5ff', fontWeight: 600 }}>
              <Table.Td>Total</Table.Td>
              <Table.Td ta="center">
                {data.reduce((sum, row) => sum + row.aop_plan, 0)}
              </Table.Td>
              <Table.Td ta="center">
                {data.reduce((sum, row) => sum + row.sprint_plan, 0)}
              </Table.Td>
              <Table.Td ta="center">
                {data.reduce((sum, row) => sum + row.actual_completed, 0)}
              </Table.Td>
              <Table.Td ta="center">
                {(
                  (data.reduce((sum, row) => sum + row.actual_completed, 0) /
                    data.reduce((sum, row) => sum + row.aop_plan, 0)) *
                  100
                ).toFixed(1)}
                %
              </Table.Td>
              <Table.Td ta="center">
                {(
                  (data.reduce((sum, row) => sum + row.actual_completed, 0) /
                    data.reduce((sum, row) => sum + row.sprint_plan, 0)) *
                  100
                ).toFixed(1)}
                %
              </Table.Td>
            </Table.Tr>
          </Table.Tbody>
        </Table>
      </div>
    </div>
  );
}
