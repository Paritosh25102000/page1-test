import { Center, Loader, type LoaderProps } from '@mantine/core';

interface LoadingSpinnerProps {
  size?: LoaderProps['size'];
}

export function LoadingSpinner({ size = 'md' }: LoadingSpinnerProps) {
  return (
    <Center h="100%">
      <Loader size={size} />
    </Center>
  );
}
