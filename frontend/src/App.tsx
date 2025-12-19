import { MantineProvider, createTheme } from '@mantine/core';
import '@mantine/core/styles.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardProvider } from '@/context/DashboardContext';
import { AppLayout } from '@/components/layout/AppLayout';
import { Page1Shell } from '@/components/layout/Page1Shell';
import { Page2Shell } from '@/components/layout/Page2Shell';
import { Page3Shell } from '@/components/layout/Page3Shell';
import { Page4Shell } from '@/components/layout/Page4Shell';
import { useDashboardData } from '@/hooks/useDashboardData';

// Custom theme configuration
const theme = createTheme({
  primaryColor: 'blue',
  colors: {
    // Custom status colors for gauges
    statusRed: ['#fff5f5', '#ffe3e3', '#ffc9c9', '#ffa8a8', '#ff8787', '#ff6b6b', '#fa5252', '#f03e3e', '#e03131', '#c92a2a'],
    statusAmber: ['#fff9db', '#fff3bf', '#ffec99', '#ffe066', '#ffd43b', '#fcc419', '#fab005', '#f59f00', '#f08c00', '#e67700'],
    statusGreen: ['#ebfbee', '#d3f9d8', '#b2f2bb', '#8ce99a', '#69db7c', '#51cf66', '#40c057', '#37b24d', '#2f9e44', '#2b8a3e'],
  },
});

function DashboardContent() {
  // Initialize data fetching
  useDashboardData();

  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Navigate to="/executive-summary" replace />} />
        <Route path="executive-summary" element={<Page1Shell />} />
        <Route path="slab-cycle" element={<Page2Shell />} />
        <Route path="floor-achievement" element={<Page3Shell />} />
        <Route path="finishing-activities" element={<Page4Shell />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <MantineProvider theme={theme} defaultColorScheme="light">
      <BrowserRouter>
        <DashboardProvider>
          <DashboardContent />
        </DashboardProvider>
      </BrowserRouter>
    </MantineProvider>
  );
}

export default App;
