import { SegmentedControl, Text, Stack } from '@mantine/core';
import type { TimeModeState } from '@/types/dashboard';

interface TimeModeToggleProps {
  value: TimeModeState;
  onChange: (value: TimeModeState) => void;
}

/**
 * Time mode toggle component using Mantine SegmentedControl.
 * Allows switching between FY, Quarter, and Month views.
 */
export function TimeModeToggle({ value, onChange }: TimeModeToggleProps) {
  return (
    <Stack gap={4}>
      <Text size="sm" fw={500}>
        Time Mode
      </Text>
      <SegmentedControl
        value={value}
        onChange={(val) => onChange(val as TimeModeState)}
        data={[
          { label: 'FY', value: 'FY' },
          { label: 'Quarter', value: 'Quarter' },
          { label: 'Month', value: 'Month' },
        ]}
        size="sm"
      />
    </Stack>
  );
}
