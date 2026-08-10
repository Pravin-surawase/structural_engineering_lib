import { beforeEach, describe, it, expect, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { DesignView } from '../../components/design/DesignView';

const mockDesignInputs = vi.hoisted(() => ({
  width: 300,
  depth: 450,
  moment: 150,
  shear: 80,
  torsion: 0,
  fck: 25,
  fy: 500,
  include_serviceability: false,
}));

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn(() => vi.fn()),
  useSearchParams: vi.fn(() => [new URLSearchParams(), vi.fn()]),
}));

// Mock useLiveDesign
vi.mock('../../hooks/useLiveDesign', () => ({
  useLiveDesign: vi.fn(() => ({
    state: {
      result: null,
      inputRevision: 1,
      resultRevision: null,
      resultLifecycle: 'not_evaluated',
      exportEligible: false,
      isDesigning: false,
      isConnected: true,
      isLoadingGeometry: false,
      connectionStatus: 'disconnected',
      latency: null,
      error: null,
      geometry: null,
      isFallbackActive: true,
      transportExplanation: 'Verified HTTP mode.',
    },
    actions: {
      triggerDesign: vi.fn(),
      updateInputs: vi.fn(),
      updateLength: vi.fn(),
      reconnect: vi.fn(),
      reset: vi.fn(),
    },
  })),
}));

// Mock useInsights hooks
vi.mock('../../hooks/useInsights', () => ({
  useCodeChecks: vi.fn(() => ({ mutate: vi.fn(), data: null })),
  useRebarSuggestions: vi.fn(() => ({ mutate: vi.fn(), data: null })),
}));

// Mock export hooks (they use useMutation which requires QueryClientProvider)
vi.mock('../../hooks/useExport', () => ({
  useExportBBS: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useExportDXF: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useExportReport: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

// Mock load analysis hook
vi.mock('../../hooks/useLoadAnalysis', () => ({
  useLoadAnalysis: vi.fn(() => ({ mutate: vi.fn(), data: null, isPending: false })),
}));

// Mock Viewport3D (Three.js cannot run in jsdom)
vi.mock('../../components/viewport/Viewport3D', () => ({
  Viewport3D: () => React.createElement('div', { 'data-testid': 'viewport-3d' }, 'Viewport3D'),
}));

// Mock ConnectionStatus
vi.mock('../../components/ui/ConnectionStatus', () => ({
  ConnectionStatus: ({ status }: { status: string }) =>
    React.createElement('span', { 'data-testid': 'connection-status' }, status),
}));

vi.mock('../../features/catalog/CatalogBeamInputPanel', () => ({
  CatalogBeamInputPanel: () => React.createElement(
    'div',
    { 'data-testid': 'catalog-beam-inputs' },
    React.createElement('input', { 'aria-label': 'Width in mm' }),
    React.createElement('input', { 'aria-label': 'Depth in mm' }),
    React.createElement('input', { 'aria-label': 'Moment (Mu) in kN m' }),
    React.createElement('input', { 'aria-label': 'Shear (Vu) in kN' }),
    React.createElement('select', { 'aria-label': 'Concrete in N/mm2' }),
    React.createElement('select', { 'aria-label': 'Steel in N/mm2' }),
  ),
}));

// Mock design store
vi.mock('../../store/designStore', () => ({
  useDesignStore: vi.fn(() => ({
    inputs: mockDesignInputs,
    length: 4000,
  })),
}));

describe('DesignView', () => {
  beforeEach(() => {
    mockDesignInputs.include_serviceability = false;
  });

  it('renders without crashing', () => {
    render(React.createElement(DesignView));
    expect(screen.getByRole('heading', { name: 'Quick beam design' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Beam inputs' })).toBeInTheDocument();
  });

  it('renders connection status', () => {
    render(React.createElement(DesignView));
    expect(screen.getByTestId('connection-status')).toBeInTheDocument();
  });

  it('renders auto design toggle', () => {
    render(React.createElement(DesignView));
    expect(screen.getByText('Auto Design')).toBeInTheDocument();
  });

  it('renders 3D viewport', () => {
    render(React.createElement(DesignView));
    expect(screen.getByTestId('viewport-3d')).toBeInTheDocument();
  });

  it('keeps one primary design action and common inputs visible', () => {
    render(React.createElement(DesignView));
    expect(screen.getAllByRole('button', { name: 'Design beam' })).toHaveLength(1);
    expect(screen.getByLabelText('Width in mm')).toBeInTheDocument();
    expect(screen.getByLabelText('Moment (Mu) in kN·m')).toBeInTheDocument();
    expect(screen.getByLabelText('Torsion (Tu) in kN·m')).toHaveValue(0);
    fireEvent.click(screen.getByRole('button', { name: 'Serviceability' }));
    expect(screen.getByLabelText(/Include maintained Level-A/)).not.toBeChecked();
    expect(screen.getByText('Not evaluated')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Compare options' })).toBeDisabled();
  });

  it('offers only maintained serviceability exposure classes', () => {
    mockDesignInputs.include_serviceability = true;
    render(React.createElement(DesignView));
    fireEvent.click(screen.getByRole('button', { name: 'Serviceability' }));

    const exposure = screen.getByLabelText('Exposure') as HTMLSelectElement;
    expect(Array.from(exposure.options, (option) => option.value)).toEqual([
      'mild',
      'moderate',
      'severe',
      'very_severe',
    ]);
  });

  it('renders one schema-owned control per field in catalogue mode', () => {
    render(React.createElement(DesignView, { inputMode: 'catalog' }));
    expect(screen.getAllByLabelText('Shear (Vu) in kN')).toHaveLength(1);
    expect(screen.getAllByLabelText('Concrete in N/mm2')).toHaveLength(1);
    expect(screen.queryByLabelText('Load Calculator')).not.toBeInTheDocument();
  });
});
