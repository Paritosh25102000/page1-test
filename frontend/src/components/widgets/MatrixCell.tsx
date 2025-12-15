import { Box, Text, HoverCard, Stack, Anchor } from '@mantine/core';
import type { BucketKey, ProjectInfo } from '@/types/dashboard';
import { useDashboard } from '@/context/DashboardContext';

interface MatrixCellProps {
  value: number;
  bucketKey: BucketKey;
  rowId?: string;
  maxValue: number;
  projects?: ProjectInfo[];
}

export function MatrixCell({ value, bucketKey, rowId: _rowId, maxValue, projects }: MatrixCellProps) {
  const { setZone, setRegion, setProject, state } = useDashboard();

  // Calculate intensity for heatmap (0 to 1 scale)
  const intensity = maxValue > 0 ? value / maxValue : 0;

  // Determine if this is a critical bucket (<60%)
  const isCritical = bucketKey === 'lt_60';

  // Calculate background color based on intensity
  const getBackgroundColor = () => {
    if (value === 0) return 'transparent';
    if (isCritical) {
      // Red tones for critical bucket
      return `rgba(250, 82, 82, ${0.2 + intensity * 0.6})`;
    }
    // Blue tones for normal buckets
    return `rgba(34, 139, 230, ${0.1 + intensity * 0.5})`;
  };

  const handleProjectClick = (projectId: string) => {
    console.log(`[MatrixCell] Project clicked: ${projectId}`);

    // Find the project's zone and region from hierarchy tree
    const hierarchyTree = state.data?.controls.hierarchy_tree;
    if (!hierarchyTree) return;

    for (const [zoneId, regions] of Object.entries(hierarchyTree)) {
      for (const [regionId, projectList] of Object.entries(regions)) {
        const project = projectList.find((p) => p.id === projectId);
        if (project) {
          // Set filters to navigate to the project
          setZone(zoneId);
          // Need to wait for region options to populate, then set region and project
          setTimeout(() => {
            setRegion(regionId);
            setTimeout(() => {
              setProject(projectId);
            }, 50);
          }, 50);
          return;
        }
      }
    }
  };

  const tooltipContent = projects && projects.length > 0 ? (
    <Stack gap={4}>
      <Text size="xs" fw={600} c="white">Projects ({value}):</Text>
      {projects.map((project) => (
        <Anchor
          key={project.id}
          size="xs"
          c="white"
          onClick={(e) => {
            e.stopPropagation();
            handleProjectClick(project.id);
          }}
          style={{ cursor: 'pointer' }}
        >
          {project.name}
        </Anchor>
      ))}
    </Stack>
  ) : null;

  const cellContent = (
    <Box
      style={{
        backgroundColor: getBackgroundColor(),
        border: isCritical && value > 0 ? '2px solid #fa5252' : '1px solid #e9ecef',
        borderRadius: '4px',
        padding: '8px 12px',
        textAlign: 'center',
        cursor: value > 0 && projects?.length ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        minWidth: '50px',
      }}
      onMouseEnter={(e) => {
        if (value > 0) e.currentTarget.style.transform = 'scale(1.05)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'scale(1)';
      }}
    >
      <Text fw={value > 0 ? 600 : 400} size="sm" c={value === 0 ? 'dimmed' : isCritical ? 'red' : 'dark'}>
        {value}
      </Text>
    </Box>
  );

  if (tooltipContent && value > 0) {
    return (
      <HoverCard
        width={220}
        position="top"
        withArrow
        shadow="md"
        openDelay={100}
        closeDelay={200}
      >
        <HoverCard.Target>
          {cellContent}
        </HoverCard.Target>
        <HoverCard.Dropdown bg="dark.7" p="xs">
          {tooltipContent}
        </HoverCard.Dropdown>
      </HoverCard>
    );
  }

  return cellContent;
}
