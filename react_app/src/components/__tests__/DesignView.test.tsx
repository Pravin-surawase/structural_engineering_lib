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
      isDesigning: false,
      connectionStatus: 'disconnected',
      latency: null,
      error: null,
    },
    actions: {
      updateInputs: vi.fn(),
      updateLength: vi.fn(),
      reconnect: vi.fn(),
    },
  })),
}));

// Mock useInsights hooks
vi.mock('../../hooks/useInsights', () => ({
  useCodeChecks: vi.fn(() => ({ mutate: vi.fn(), data: null })),
  useRebarSuggestions: vi.fn(() => ({ mutate: vi.fn(), data: null })),
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
    expect(screen.getByText('Beam Design')).toBeInTheDocument();
    expect(screen.getByText('IS 456:2000')).toBeInTheDocument();
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
});
