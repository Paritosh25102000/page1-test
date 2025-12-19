import { useEffect, useState } from 'react';
import type { Page4Data } from '@/types/page4';

export function usePage4Data() {
  const [data, setData] = useState<Page4Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch('/data/page4-finishing-gaps.json');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const jsonData: Page4Data = await response.json();
        setData(jsonData);
        setError(null);
      } catch (err) {
        console.error('Failed to load Page 4 data:', err);
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
