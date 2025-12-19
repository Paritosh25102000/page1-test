import { createContext, useContext, useReducer, useMemo, type ReactNode } from 'react';
import type {
  DashboardData,
  DashboardState,
  DashboardAction,
  FilterState,
  TimeModeState,
  NodeData,
  Page2Filters,
  Page3Filters,
  Page4Filters,
} from '@/types/dashboard';
import { buildDataKey } from '@/utils/dataKeys';

const initialFilterState: FilterState = {
  zone: null,
  region: null,
  project: null,
};

const initialPage2Filters: Page2Filters = {
  typicalMode: 'all',
  formworkType: null,
};

const initialPage3Filters: Page3Filters = {
  activity: null,
};

const initialPage4Filters: Page4Filters = {
  alphaStatus: 'all',
  reraStatus: null,
};

const initialState: DashboardState = {
  filters: initialFilterState,
  timeMode: 'FY',
  page2Filters: initialPage2Filters,
  page3Filters: initialPage3Filters,
  page4Filters: initialPage4Filters,
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

    // Page 2 actions
    case 'SET_PAGE2_TYPICAL_MODE':
      return {
        ...state,
        page2Filters: {
          ...state.page2Filters,
          typicalMode: action.payload,
        },
      };

    case 'SET_PAGE2_FORMWORK_TYPE':
      return {
        ...state,
        page2Filters: {
          ...state.page2Filters,
          formworkType: action.payload,
        },
      };

    case 'RESET_PAGE2_FILTERS':
      return {
        ...state,
        page2Filters: initialPage2Filters,
      };

    // Page 3 actions
    case 'SET_PAGE3_ACTIVITY':
      return {
        ...state,
        page3Filters: {
          ...state.page3Filters,
          activity: action.payload,
        },
      };

    case 'RESET_PAGE3_FILTERS':
      return {
        ...state,
        page3Filters: initialPage3Filters,
      };

    // Page 4 actions
    case 'SET_PAGE4_ALPHA_STATUS':
      return {
        ...state,
        page4Filters: {
          ...state.page4Filters,
          alphaStatus: action.payload,
        },
      };

    case 'SET_PAGE4_RERA_STATUS':
      return {
        ...state,
        page4Filters: {
          ...state.page4Filters,
          reraStatus: action.payload,
        },
      };

    case 'RESET_PAGE4_FILTERS':
      return {
        ...state,
        page4Filters: initialPage4Filters,
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
  // Page 2 actions
  setPage2TypicalMode: (mode: 'typical' | 'non-typical' | 'all') => void;
  setPage2FormworkType: (type: string | null) => void;
  resetPage2Filters: () => void;
  // Page 3 actions
  setPage3Activity: (activity: string | null) => void;
  resetPage3Filters: () => void;
  // Page 4 actions
  setPage4AlphaStatus: (status: 'alpha' | 'non-alpha' | 'all') => void;
  setPage4ReraStatus: (status: string | null) => void;
  resetPage4Filters: () => void;
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
      // Page 2 actions
      setPage2TypicalMode: (mode) => dispatch({ type: 'SET_PAGE2_TYPICAL_MODE', payload: mode }),
      setPage2FormworkType: (type) => dispatch({ type: 'SET_PAGE2_FORMWORK_TYPE', payload: type }),
      resetPage2Filters: () => dispatch({ type: 'RESET_PAGE2_FILTERS' }),
      // Page 3 actions
      setPage3Activity: (activity) => dispatch({ type: 'SET_PAGE3_ACTIVITY', payload: activity }),
      resetPage3Filters: () => dispatch({ type: 'RESET_PAGE3_FILTERS' }),
      // Page 4 actions
      setPage4AlphaStatus: (status) => dispatch({ type: 'SET_PAGE4_ALPHA_STATUS', payload: status }),
      setPage4ReraStatus: (status) => dispatch({ type: 'SET_PAGE4_RERA_STATUS', payload: status }),
      resetPage4Filters: () => dispatch({ type: 'RESET_PAGE4_FILTERS' }),
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
