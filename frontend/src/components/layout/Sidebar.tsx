import { NavLink, Stack } from '@mantine/core';
import { useLocation, useNavigate } from 'react-router-dom';

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    {
      label: 'Executive Summary',
      icon: '📊',
      path: '/executive-summary',
    },
    {
      label: 'Slab Cycle Analysis',
      icon: '⚡',
      path: '/slab-cycle',
    },
    {
      label: 'Floor Achievement Analysis',
      icon: '🎯',
      path: '/floor-achievement',
    },
    {
      label: 'Finishing Activities',
      icon: '✨',
      path: '/finishing-activities',
    },
  ];

  return (
    <Stack gap="xs" p="md">
      {menuItems.map((item) => (
        <NavLink
          key={item.path}
          label={item.label}
          leftSection={<span>{item.icon}</span>}
          active={location.pathname === item.path}
          onClick={() => navigate(item.path)}
          style={{ borderRadius: 4 }}
        />
      ))}
    </Stack>
  );
}
