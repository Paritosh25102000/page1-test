import { Title, Table } from '@mantine/core';
import type { TopProject } from '@/types/page2';

interface TopProjectsCardProps {
  data: TopProject[];
}

export function TopProjectsCard({ data }: TopProjectsCardProps) {
  const rows = data.map((project) => (
    <Table.Tr key={project.rank}>
      <Table.Td fw={500}>{project.project}</Table.Td>
      <Table.Td>{project.tower}</Table.Td>
      <Table.Td ta="right" fw={600} c="green.7">
        {project.slab_cycle} days
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <div>
      <Title order={4} mb="md" c="green.7">
        Top 5 Projects / Tower
      </Title>
      <Title order={6} mb="sm" fw={500} c="dimmed">
        (Based on Slab Cycle of last 5 Typical floors)
      </Title>
      <Table striped highlightOnHover withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Project</Table.Th>
            <Table.Th>Tower</Table.Th>
            <Table.Th ta="right">Slab Cycle</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </div>
  );
}
