import { useEffect } from 'react';
import type { DashboardData } from '@/types/dashboard';
import { useDashboard } from '@/context/DashboardContext';

const DATA_URL = '/data/page1-mock-data.json';

export function useDashboardData() {
  const { state, dispatch } = useDashboard();

  useEffect(() => {
    // Skip if data is already loaded
    if (state.data) return;

    const fetchData = async () => {
      dispatch({ type: 'SET_LOADING', payload: true });

      try {
        const response = await fetch(DATA_URL);
        if (!response.ok) {
          throw new Error(`Failed to fetch dashboard data: ${response.status} ${response.statusText}`);
        }

        const data: DashboardData = await response.json();
        dispatch({ type: 'SET_DATA', payload: data });
        console.log('[useDashboardData] Data loaded successfully');
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error loading data';
        console.error('[useDashboardData] Error:', message);
        dispatch({ type: 'SET_ERROR', payload: message });
      }
    };

    fetchData();
  }, [state.data, dispatch]);

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
  };
}
