import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { DesignView } from '../../components/design/DesignView';

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn(() => vi.fn()),
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

// Mock torsion design hook
vi.mock('../../hooks/useTorsionDesign', () => ({
  useTorsionDesign: vi.fn(() => ({ mutate: vi.fn(), data: null, isPending: false })),
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

// Mock design store
vi.mock('../../store/designStore', () => ({
  useDesignStore: vi.fn(() => ({
    inputs: { width: 300, depth: 450, moment: 150, shear: 80, fck: 25, fy: 500 },
    length: 4000,
  })),
}));

describe('DesignView', () => {
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
    expect(screen.getByText('Not evaluated')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Compare options' })).toBeDisabled();
  });
});
