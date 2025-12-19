import { useEffect, useState } from 'react';
import type { Page3Data } from '@/types/page3';

export function usePage3Data() {
  const [data, setData] = useState<Page3Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch('/data/page3-floor-achievement.json');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const jsonData: Page3Data = await response.json();
        setData(jsonData);
        setError(null);
      } catch (err) {
        console.error('Failed to load Page 3 data:', err);
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
