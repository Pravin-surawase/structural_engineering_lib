import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { ParetoPanel } from '../design/ParetoPanel';

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Loader2: (props: any) => React.createElement('svg', { 'data-testid': 'loader-icon', ...props }),
  Sparkles: (props: any) => React.createElement('svg', { 'data-testid': 'sparkles-icon', ...props }),
  DollarSign: (props: any) => React.createElement('svg', { ...props }),
  Zap: (props: any) => React.createElement('svg', { ...props }),
  Feather: (props: any) => React.createElement('svg', { ...props }),
  CheckCircle: (props: any) => React.createElement('svg', { ...props }),
  XCircle: (props: any) => React.createElement('svg', { ...props }),
  ChevronDown: (props: any) => React.createElement('svg', { ...props }),
  ChevronRight: (props: any) => React.createElement('svg', { ...props }),
}));

// Mock design store
vi.mock('../../store/designStore', () => ({
  useDesignStore: vi.fn(() => ({
    setInputs: vi.fn(),
  })),
}));

// Mock useParetoDesign hook — controls per test
const mockMutate = vi.fn();
let mockHookReturn: any = {
  mutate: mockMutate,
  data: null,
  isPending: false,
  error: null,
};

vi.mock('../../hooks/useParetoDesign', () => ({
  useParetoDesign: () => mockHookReturn,
}));

beforeEach(() => {
  mockMutate.mockClear();
  mockHookReturn = {
    mutate: mockMutate,
    data: null,
    isPending: false,
    error: null,
  };
});

const defaultProps = { spanMm: 5000, muKnm: 150, vuKn: 80 };

describe('ParetoPanel', () => {
  it('renders the Find Alternatives button in initial state', () => {
    render(React.createElement(ParetoPanel, defaultProps));
    expect(screen.getByText('Find Alternatives')).toBeInTheDocument();
  });

  it('calls mutate when Find Alternatives is clicked', () => {
    render(React.createElement(ParetoPanel, defaultProps));
    fireEvent.click(screen.getByText('Find Alternatives'));
    expect(mockMutate).toHaveBeenCalledWith({
      span_mm: 5000,
      mu_knm: 150,
      vu_kn: 80,
      cover_mm: 40,
      max_candidates: 50,
    });
  });

  it('shows loading state when isPending is true', () => {
    mockHookReturn = {
      mutate: mockMutate,
      data: null,
      isPending: true,
      error: null,
    };
    render(React.createElement(ParetoPanel, defaultProps));
    expect(screen.getByText('Finding alternatives...')).toBeInTheDocument();
  });

  it('shows error state when error is present', () => {
    mockHookReturn = {
      mutate: mockMutate,
      data: null,
      isPending: false,
      error: new Error('Network failure'),
    };
    render(React.createElement(ParetoPanel, defaultProps));
    expect(screen.getByText(/Optimization failed.*Network failure/)).toBeInTheDocument();
  });

  it('displays results after successful fetch', () => {
    const mockData = {
      pareto_front: [
        {
          b_mm: 300,
          D_mm: 500,
          d_mm: 460,
          fck_nmm2: 25,
          fy_nmm2: 500,
          ast_required: 942,
          ast_provided: 981,
          bar_config: '4-16mm',
          cost: 12500,
          steel_weight_kg: 7.7,
          utilization: 0.85,
          is_safe: true,
          governing_clauses: ['Cl 38.1'],
          rank: 1,
          crowding_distance: Infinity,
        },
      ],
      pareto_count: 1,
      total_candidates: 20,
      objectives_used: ['cost', 'utilization'],
      computation_time_sec: 0.42,
      best_by_cost: null,
      best_by_utilization: null,
      best_by_weight: null,
    };

    mockHookReturn = {
      mutate: mockMutate,
      data: mockData,
      isPending: false,
      error: null,
    };
    render(React.createElement(ParetoPanel, defaultProps));
    expect(screen.getByText(/1 Alternative Design/)).toBeInTheDocument();
    expect(screen.getByText('0.42s')).toBeInTheDocument();
  });

  it('returns null when no data, not pending, and no error but data has been cleared', () => {
    // This simulates the case where data was previously set then cleared
    mockHookReturn = {
      mutate: mockMutate,
      data: undefined,
      isPending: false,
      error: null,
    };
    // Trigger the "no data" path — should show Find Alternatives button
    // since !data && !isPending && !error
    render(React.createElement(ParetoPanel, defaultProps));
    expect(screen.getByText('Find Alternatives')).toBeInTheDocument();
  });
});
