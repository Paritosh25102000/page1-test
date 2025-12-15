import { Box, Text } from '@mantine/core';
import type { BucketKey } from '@/types/dashboard';

interface MatrixCellProps {
  value: number;
  bucketKey: BucketKey;
  rowId?: string;
  maxValue: number;
}

export function MatrixCell({ value, bucketKey, rowId, maxValue }: MatrixCellProps) {
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

  const handleClick = () => {
    console.log(`[MatrixCell] Clicked: bucket=${bucketKey}, rowId=${rowId}, value=${value}`);
  };

  return (
    <Box
      onClick={handleClick}
      style={{
        backgroundColor: getBackgroundColor(),
        border: isCritical && value > 0 ? '2px solid #fa5252' : '1px solid #e9ecef',
        borderRadius: '4px',
        padding: '8px 12px',
        textAlign: 'center',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        minWidth: '50px',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'scale(1.05)';
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
}
