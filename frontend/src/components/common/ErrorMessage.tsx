import { Center, Text, Stack } from '@mantine/core';
import { IconAlertTriangle } from '@tabler/icons-react';

interface ErrorMessageProps {
  message: string;
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <Center h="100%">
      <Stack align="center" gap="xs">
        <IconAlertTriangle size={32} color="var(--mantine-color-red-6)" />
        <Text c="red" size="sm">
          {message}
        </Text>
      </Stack>
    </Center>
  );
}
