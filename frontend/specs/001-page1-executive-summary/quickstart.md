# Quickstart: Page 1 Executive Summary Dashboard

**Feature**: 001-page1-executive-summary
**Date**: 2025-12-15

## Project Layout

The `etl-cco-dashboard/` directory contains two separate codebases:

```
etl-cco-dashboard/
├── src/                    # Python ETL scripts (existing)
│   ├── transformers.py
│   ├── xml_parser.py
│   ├── cost_timeline.py
│   └── validators.py
├── frontend/               # React dashboard (this feature)
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
└── schemas/                # Shared JSON schemas & mock data
```

**This quickstart focuses on the `frontend/` directory only.**

## Prerequisites

- Node.js 18.x or higher
- npm 9.x or higher (or pnpm/yarn)

## Project Setup

### 1. Initialize the Frontend Project

```bash
cd etl-cco-dashboard/frontend

# Create Vite + React + TypeScript project
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
```

### 2. Install Required Dependencies

```bash
# Mantine UI
npm install @mantine/core @mantine/hooks @emotion/react

# ApexCharts
npm install apexcharts react-apexcharts

# Tabler Icons (Mantine default)
npm install @tabler/icons-react

# Development dependencies
npm install -D @types/node vitest @testing-library/react @testing-library/jest-dom jsdom
```

### 3. Configure Vite

Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
  },
});
```

### 4. Configure TypeScript

Ensure `tsconfig.json` includes:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 5. Copy Mock Data

```bash
# Create public directory for static data
mkdir -p public/data

# Copy mock data file
cp ../schemas/page-1-executive-simmary/page1-mock-data.json public/data/
```

### 6. Copy Type Definitions

```bash
# Create types directory
mkdir -p src/types

# Copy generated TypeScript interfaces
cp ../../specs/001-page1-executive-summary/contracts/dashboard.ts src/types/
```

## Development

### Start Development Server

```bash
npm run dev
```

The dashboard will be available at `http://localhost:5173`

### Run Tests

```bash
npm run test
```

### Build for Production

```bash
npm run build
```

## Project Structure After Setup

```
etl-cco-dashboard/frontend/
├── public/
│   └── data/
│       └── page1-mock-data.json
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── types/
│   │   └── dashboard.ts
│   ├── context/
│   ├── hooks/
│   ├── components/
│   └── utils/
├── tests/
│   └── setup.ts
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Key Implementation Steps

1. **App Entry Point** (`src/main.tsx`): Wrap with MantineProvider
2. **Dashboard Context** (`src/context/DashboardContext.tsx`): Implement state management
3. **Data Hook** (`src/hooks/useDashboardData.ts`): Fetch and provide mock data
4. **Layout Shell** (`src/components/layout/DashboardShell.tsx`): Grid layout
5. **Filter Panel** (`src/components/filters/GlobalFilterPanel.tsx`): Cascading dropdowns
6. **Widgets**: COCTrendChart, KPIGauges, ProjectMatrix

## Iframe Embedding

For testing iframe behavior:

```html
<!-- test-iframe.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Dashboard Test</title>
  <style>
    body { margin: 0; padding: 20px; background: #f0f0f0; }
    iframe { border: 1px solid #ccc; }
  </style>
</head>
<body>
  <h1>Iframe Test</h1>
  <iframe
    src="http://localhost:5173"
    width="100%"
    height="800"
    style="max-width: 1400px;"
  ></iframe>
</body>
</html>
```

## Troubleshooting

### Mantine Styles Not Loading

Ensure MantineProvider wraps the app:

```tsx
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';

function App() {
  return (
    <MantineProvider>
      {/* Your app */}
    </MantineProvider>
  );
}
```

### ApexCharts SSR Issues

ApexCharts requires client-side rendering. If you see SSR errors, ensure dynamic import:

```tsx
import dynamic from 'next/dynamic'; // Only if using Next.js
// For Vite, regular imports work fine
```

### JSON Import Errors

Enable `resolveJsonModule` in tsconfig.json and import with type assertion:

```typescript
import mockData from '/data/page1-mock-data.json';
// or fetch dynamically
const data = await fetch('/data/page1-mock-data.json').then(r => r.json());
```
