import { useEffect, useState } from 'react';
import type { Page2Data } from '@/types/page2';

export function usePage2Data() {
  const [data, setData] = useState<Page2Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch('/data/page2-slab-cycle.json');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const jsonData: Page2Data = await response.json();
        setData(jsonData);
        setError(null);
      } catch (err) {
        console.error('Failed to load Page 2 data:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setData(null);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return { data, loading, error };
}
