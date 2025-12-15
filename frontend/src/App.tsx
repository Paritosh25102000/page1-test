import { MantineProvider, createTheme } from '@mantine/core';
import '@mantine/core/styles.css';
import { DashboardProvider } from '@/context/DashboardContext';
import { DashboardShell } from '@/components/layout/DashboardShell';
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

  return <DashboardShell />;
}

function App() {
  return (
    <MantineProvider theme={theme} defaultColorScheme="light">
      <DashboardProvider>
        <DashboardContent />
      </DashboardProvider>
    </MantineProvider>
  );
}

export default App;
