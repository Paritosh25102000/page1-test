import { Select, type SelectProps } from '@mantine/core';

interface HierarchySelectProps extends Omit<SelectProps, 'data'> {
  options: { value: string; label: string }[];
  parentValue: string | null;
  onValueChange: (value: string | null) => void;
}

/**
 * Cascading dropdown component for hierarchy selection.
 * Automatically disables when parent value is not selected.
 */
export function HierarchySelect({
  options,
  parentValue,
  onValueChange,
  label,
  placeholder,
  value,
  ...rest
}: HierarchySelectProps) {
  // Disable if parent is not selected (except for root level where parentValue is undefined)
  const isDisabled = parentValue === null && rest.disabled !== false;

  return (
    <Select
      label={label}
      placeholder={placeholder}
      data={options}
      value={value as string | null}
      onChange={onValueChange}
      clearable
      disabled={isDisabled}
      size="sm"
      w={150}
      {...rest}
    />
  );
}
