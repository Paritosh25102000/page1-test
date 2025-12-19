import { Title, Table, Paper, Stack, Badge } from '@mantine/core';
import type { RankedProject } from '@/types/page3';

interface TopBottomProjectsCardsProps {
  topProjects: RankedProject[];
  bottomProjects: RankedProject[];
}

interface ProjectCardProps {
  title: string;
  projects: RankedProject[];
  colorScheme: 'green' | 'red';
}

function ProjectCard({ title, projects, colorScheme }: ProjectCardProps) {
  const rows = projects.map((project) => (
    <Table.Tr key={project.rank}>
      <Table.Td fw={500}>{project.project}</Table.Td>
      <Table.Td ta="center">{project.sprint_plan}</Table.Td>
      <Table.Td ta="center" fw={600}>
        {project.actual_completed}
      </Table.Td>
      <Table.Td ta="right">
        <Badge color={colorScheme} size="sm">
          {project.pct_sprint.toFixed(1)}%
        </Badge>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <div>
      <Title order={4} mb="md" c={`${colorScheme}.7`}>
        {title}
      </Title>
      <Table striped highlightOnHover withTableBorder withColumnBorders fontSize="sm">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Project</Table.Th>
            <Table.Th ta="center">
              Sprint
              <br />
              Plan
            </Table.Th>
            <Table.Th ta="center">
              Actual
              <br />
              Completed
            </Table.Th>
            <Table.Th ta="right">
              % Achieve
              <br />
              against Sprint
            </Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </div>
  );
}

export function TopBottomProjectsCards({ topProjects, bottomProjects }: TopBottomProjectsCardsProps) {
  return (
    <Stack gap="md">
      <Paper
        shadow="xs"
        p={{ base: 'xs', sm: 'md' }}
        withBorder
        style={{ borderColor: 'var(--mantine-color-green-3)' }}
      >
        <ProjectCard title="Top 5 Projects" projects={topProjects} colorScheme="green" />
      </Paper>

      <Paper
        shadow="xs"
        p={{ base: 'xs', sm: 'md' }}
        withBorder
        style={{ borderColor: 'var(--mantine-color-red-3)' }}
      >
        <ProjectCard title="Bottom 5 Projects" projects={bottomProjects} colorScheme="red" />
      </Paper>
    </Stack>
  );
}
