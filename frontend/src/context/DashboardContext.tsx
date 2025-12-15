import { createContext, useContext, useReducer, useMemo, type ReactNode } from 'react';
import type {
  DashboardData,
  DashboardState,
  DashboardAction,
  FilterState,
  TimeModeState,
  NodeData,
} from '@/types/dashboard';
import { buildDataKey } from '@/utils/dataKeys';

const initialFilterState: FilterState = {
  zone: null,
  region: null,
  project: null,
};

const initialState: DashboardState = {
  filters: initialFilterState,
  timeMode: 'FY',
  data: null,
  loading: true,
  error: null,
};

function dashboardReducer(state: DashboardState, action: DashboardAction): DashboardState {
  switch (action.type) {
    case 'SET_ZONE':
      console.log('[DashboardContext] SET_ZONE:', action.payload);
      return {
        ...state,
        filters: {
          zone: action.payload,
          region: null, // Clear child selections when parent changes
          project: null,
        },
      };

    case 'SET_REGION':
      console.log('[DashboardContext] SET_REGION:', action.payload);
      return {
        ...state,
        filters: {
          ...state.filters,
          region: action.payload,
          project: null, // Clear child selection when parent changes
        },
      };

    case 'SET_PROJECT':
      console.log('[DashboardContext] SET_PROJECT:', action.payload);
      return {
        ...state,
        filters: {
          ...state.filters,
          project: action.payload,
        },
      };

    case 'SET_TIME_MODE':
      console.log('[DashboardContext] SET_TIME_MODE:', action.payload);
      return {
        ...state,
        timeMode: action.payload,
      };

    case 'SET_DATA':
      return {
        ...state,
        data: action.payload,
        loading: false,
        error: null,
      };

    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };

    case 'SET_ERROR':
      console.error('[DashboardContext] SET_ERROR:', action.payload);
      return {
        ...state,
        error: action.payload,
        loading: false,
      };

    case 'RESET_FILTERS':
      console.log('[DashboardContext] RESET_FILTERS');
      return {
        ...state,
        filters: initialFilterState,
      };

    default:
      return state;
  }
}

interface DashboardContextValue {
  state: DashboardState;
  dispatch: React.Dispatch<DashboardAction>;
  currentData: NodeData | null;
  dataKey: string;
  setZone: (zone: string | null) => void;
  setRegion: (region: string | null) => void;
  setProject: (project: string | null) => void;
  setTimeMode: (mode: TimeModeState) => void;
  resetFilters: () => void;
}

const DashboardContext = createContext<DashboardContextValue | null>(null);

interface DashboardProviderProps {
  children: ReactNode;
  initialData?: DashboardData;
}

export function DashboardProvider({ children, initialData }: DashboardProviderProps) {
  const [state, dispatch] = useReducer(dashboardReducer, {
    ...initialState,
    data: initialData || null,
    loading: !initialData,
  });

  const dataKey = useMemo(() => buildDataKey(state.filters), [state.filters]);

  const currentData = useMemo(() => {
    if (!state.data) return null;
    return state.data.dashboard_data[dataKey] || null;
  }, [state.data, dataKey]);

  const value = useMemo<DashboardContextValue>(
    () => ({
      state,
      dispatch,
      currentData,
      dataKey,
      setZone: (zone) => dispatch({ type: 'SET_ZONE', payload: zone }),
      setRegion: (region) => dispatch({ type: 'SET_REGION', payload: region }),
      setProject: (project) => dispatch({ type: 'SET_PROJECT', payload: project }),
      setTimeMode: (mode) => dispatch({ type: 'SET_TIME_MODE', payload: mode }),
      resetFilters: () => dispatch({ type: 'RESET_FILTERS' }),
    }),
    [state, currentData, dataKey]
  );

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboard(): DashboardContextValue {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  return context;
}
