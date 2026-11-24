import { beforeEach, describe, it, expect, vi } from 'vitest';
import { act, fireEvent, render, screen } from '@testing-library/react';
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

const mockLoadAnalysis = vi.hoisted(() => ({
  mutate: vi.fn(),
  data: null as null | {
    max_bm_knm: number;
    min_bm_knm: number;
    max_sf_kn: number;
    min_sf_kn: number;
    bmd_knm: number[];
    sfd_kn: number[];
  },
  isPending: false,
  error: null as Error | null,
}));

const mockActions = vi.hoisted(() => ({
  triggerDesign: vi.fn(),
  updateInputs: vi.fn(),
  updateLength: vi.fn(),
  reconnect: vi.fn(),
  reset: vi.fn(),
}));
const mockLiveState = vi.hoisted(() => ({
  result: null as Record<string, unknown> | null,
  inputRevision: 1,
  resultRevision: null as number | null,
  resultLifecycle: 'not_evaluated' as 'not_evaluated' | 'current',
  exportEligible: false,
  isDesigning: false,
  isConnected: true,
  isLoadingGeometry: false,
  connectionStatus: 'disconnected',
  latency: null,
  error: null as string | null,
  inputErrors: { width: null as string | null, span: null as string | null },
  geometry: null,
  isFallbackActive: true,
  transportExplanation: 'Verified HTTP mode.',
}));
let mockLength = 4000;

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => React.createElement('a', { href: to }, children),
  useNavigate: vi.fn(() => vi.fn()),
  useSearchParams: vi.fn(() => [new URLSearchParams(), vi.fn()]),
}));

// Mock useLiveDesign
vi.mock('../../hooks/useLiveDesign', () => ({
  useLiveDesign: vi.fn(() => ({
    state: mockLiveState,
    actions: mockActions,
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
  useLoadAnalysis: vi.fn(() => mockLoadAnalysis),
}));

// Mock Viewport3D (Three.js cannot run in jsdom)
vi.mock('../../components/viewport/Viewport3D', () => ({
  Viewport3D: () => React.createElement('div', { 'data-testid': 'viewport-3d' }, 'Viewport3D'),
}));

vi.mock('../../components/design/ParetoPanel', () => ({
  ParetoPanel: () => React.createElement('button', {}, 'Find Alternatives'),
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
    length: mockLength,
  })),
}));

describe('DesignView', () => {
  beforeEach(() => {
    mockDesignInputs.include_serviceability = false;
    mockLength = 4000;
    mockLoadAnalysis.data = null;
    mockLoadAnalysis.error = null;
    mockLoadAnalysis.mutate.mockReset();
    mockLoadAnalysis.mutate.mockImplementation((_request: unknown, options?: { onSuccess?: (data: NonNullable<typeof mockLoadAnalysis.data>) => void }) => {
      if (mockLoadAnalysis.data) options?.onSuccess?.(mockLoadAnalysis.data);
    });
    mockActions.updateInputs.mockReset();
    mockActions.updateLength.mockReset();
    mockActions.triggerDesign.mockReset();
    Object.assign(mockLiveState, {
      result: null,
      inputRevision: 1,
      resultRevision: null,
      resultLifecycle: 'not_evaluated',
      exportEligible: false,
      inputErrors: { width: null, span: null },
    });
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
    expect(screen.queryByRole('button', { name: 'Compare options' })).not.toBeInTheDocument();
  });

  it.each(['manual', 'catalog'] as const)('keeps the exact span editable in %s mode', (inputMode) => {
    mockLength = 5123;
    render(<DesignView inputMode={inputMode} />);
    const span = screen.getByLabelText('Span in m');
    expect(span).toHaveValue(5.123);
    fireEvent.change(span, { target: { value: '5.234' } });
    expect(mockActions.updateLength).toHaveBeenCalledWith(5234);
  });

  it('moves focus between beam inputs and the result', () => {
    render(<DesignView />);

    fireEvent.click(screen.getByRole('button', { name: 'View result' }));
    expect(screen.getByRole('region', { name: 'Beam result' })).toHaveFocus();
    fireEvent.click(screen.getByRole('button', { name: 'Edit inputs' }));
    expect(screen.getByRole('region', { name: 'Beam inputs' })).toHaveFocus();
  });

  it('keeps comparison independent of check details and holds it when the result is stale', () => {
    Object.assign(mockLiveState, currentPassingState());
    const { rerender } = render(<DesignView />);
    const compare = screen.getByRole('button', { name: 'Compare options' });
    fireEvent.click(compare);
    expect(compare).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('button', { name: 'Find Alternatives' })).toBeVisible();

    fireEvent.click(screen.getByRole('button', { name: 'Show checks and evidence' }));
    fireEvent.click(screen.getByRole('button', { name: 'Hide checks and evidence' }));
    expect(screen.getByRole('button', { name: 'Find Alternatives' })).toBeVisible();

    mockLiveState.exportEligible = false;
    rerender(<DesignView />);
    expect(screen.queryByRole('button', { name: 'Find Alternatives' })).not.toBeInTheDocument();
    expect(screen.getByText('Run a current passing design to compare options.')).toBeVisible();
    fireEvent.click(compare);
    expect(compare).toBeDisabled();
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

  it('holds a hogging load result instead of transferring it as bottom tension', () => {
    mockLoadAnalysis.data = {
      max_bm_knm: 0,
      min_bm_knm: -90,
      max_sf_kn: 60,
      min_sf_kn: 0,
      bmd_knm: [-90, 0],
      sfd_kn: [60, 0],
    };
    render(React.createElement(DesignView));
    fireEvent.click(screen.getByLabelText('Load Calculator'));
    fireEvent.click(screen.getByRole('button', { name: /compute/i }));
    expect(screen.getByRole('button', { name: /use values/i })).toBeDisabled();
    expect(screen.getByText(/Transfer held/)).toHaveTextContent('-90.0 kN·m of hogging');
    expect(screen.getAllByText('-90.0').length).toBeGreaterThan(0);
  });

  it('transfers the positive simply-supported control with its shear magnitude', () => {
    mockLoadAnalysis.data = {
      max_bm_knm: 22.5,
      min_bm_knm: 0,
      max_sf_kn: 30,
      min_sf_kn: -30,
      bmd_knm: [0, 22.5, 0],
      sfd_kn: [30, 0, -30],
    };
    render(React.createElement(DesignView));
    fireEvent.click(screen.getByLabelText('Load Calculator'));
    fireEvent.click(screen.getByRole('button', { name: /compute/i }));
    fireEvent.click(screen.getByRole('button', { name: /use values/i }));
    expect(mockActions.updateInputs).toHaveBeenCalledWith({ moment: 22.5, shear: 30 });
  });

  it('preserves unrounded positive actions when transferring the diagram', () => {
    mockLoadAnalysis.data = {
      max_bm_knm: 22.546,
      min_bm_knm: 0,
      max_sf_kn: 30.123,
      min_sf_kn: -30.123,
      bmd_knm: [0, 22.546, 0],
      sfd_kn: [30.123, 0, -30.123],
    };
    render(React.createElement(DesignView));
    fireEvent.click(screen.getByLabelText('Load Calculator'));
    fireEvent.click(screen.getByRole('button', { name: /compute/i }));
    fireEvent.click(screen.getByRole('button', { name: /use values/i }));
    expect(mockActions.updateInputs).toHaveBeenCalledWith({ moment: 22.546, shear: 30.123 });
  });

  it('only transfers the newest matching load-calculator response', () => {
    const callbacks: Array<(data: NonNullable<typeof mockLoadAnalysis.data>) => void> = [];
    mockLoadAnalysis.mutate.mockImplementation((_request: unknown, options?: { onSuccess?: (data: NonNullable<typeof mockLoadAnalysis.data>) => void }) => {
      if (options?.onSuccess) callbacks.push(options.onSuccess);
    });
    render(React.createElement(DesignView));
    fireEvent.click(screen.getByLabelText('Load Calculator'));
    fireEvent.click(screen.getByRole('button', { name: /compute/i }));
    act(() => callbacks[0]({ max_bm_knm: 22.5, min_bm_knm: 0, max_sf_kn: 30, min_sf_kn: -30, bmd_knm: [0, 22.5, 0], sfd_kn: [30, 0, -30] }));
    fireEvent.change(screen.getByLabelText('w in kN/m'), { target: { value: '30' } });
    expect(screen.getByRole('button', { name: /use values/i })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: /compute/i }));
    fireEvent.change(screen.getByLabelText('w in kN/m'), { target: { value: '40' } });
    fireEvent.click(screen.getByRole('button', { name: /compute/i }));

    act(() => callbacks[2]({ max_bm_knm: 45, min_bm_knm: 0, max_sf_kn: 60, min_sf_kn: -60, bmd_knm: [0, 45, 0], sfd_kn: [60, 0, -60] }));
    act(() => callbacks[1]({ max_bm_knm: 33.75, min_bm_knm: 0, max_sf_kn: 45, min_sf_kn: -45, bmd_knm: [0, 33.75, 0], sfd_kn: [45, 0, -45] }));

    fireEvent.click(screen.getByRole('button', { name: /use values/i }));
    expect(mockActions.updateInputs).toHaveBeenCalledWith({ moment: 45, shear: 60 });
  });

  it('holds a diagram after the design span changes until it is recomputed', () => {
    mockLoadAnalysis.data = {
      max_bm_knm: 40,
      min_bm_knm: 0,
      max_sf_kn: 40,
      min_sf_kn: -40,
      bmd_knm: [0, 40, 0],
      sfd_kn: [40, 0, -40],
    };
    const { rerender } = render(React.createElement(DesignView));
    fireEvent.click(screen.getByLabelText('Load Calculator'));
    fireEvent.click(screen.getByRole('button', { name: /compute/i }));
    mockLength = 5000;
    rerender(React.createElement(DesignView));
    expect(screen.getByRole('button', { name: /use values/i })).toBeDisabled();
    expect(screen.getByText(/inputs changed after this diagram/i)).toBeInTheDocument();
  });

  it('keeps the previous diagram stale when recalculation fails', () => {
    mockLoadAnalysis.data = {
      max_bm_knm: 40,
      min_bm_knm: 0,
      max_sf_kn: 40,
      min_sf_kn: -40,
      bmd_knm: [0, 40, 0],
      sfd_kn: [40, 0, -40],
    };
    const { rerender } = render(React.createElement(DesignView));
    fireEvent.click(screen.getByLabelText('Load Calculator'));
    fireEvent.click(screen.getByRole('button', { name: /compute/i }));
    expect(screen.getByRole('button', { name: /use values/i })).toBeEnabled();

    fireEvent.change(screen.getByLabelText('w in kN/m'), { target: { value: '40' } });
    mockLoadAnalysis.mutate.mockImplementationOnce(() => {
      mockLoadAnalysis.error = new Error('Request failed');
    });
    fireEvent.click(screen.getByRole('button', { name: /compute/i }));
    rerender(React.createElement(DesignView));
    expect(screen.getByText(/load calculation failed/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /use values/i })).toBeDisabled();
    expect(mockActions.updateInputs).not.toHaveBeenCalled();
  });

  it.each([
    { field: 'Span in m', key: 'span', error: 'Span must be greater than 0 m.', action: 'updateLength', value: 0 },
    { field: 'Width in mm', key: 'width', error: 'Width must be greater than 0 mm.', action: 'updateInputs', value: { width: 0 } },
  ] as const)(
    'blocks $field from design and export when validation fails despite a current PASS result',
    ({ field, key, error, action, value }) => {
      Object.assign(mockLiveState, currentPassingState());
      const { rerender } = render(React.createElement(DesignView));
      const input = screen.getByLabelText(field);
      const recalculate = screen.getByRole('button', { name: 'Recalculate' });
      const download = screen.getByRole('button', { name: 'Export' });
      expect(recalculate).toBeEnabled();
      expect(download).toBeEnabled();

      fireEvent.change(input, { target: { value: '0' } });
      expect(mockActions[action]).toHaveBeenCalledWith(value);
      mockLiveState.inputErrors[key] = error;
      rerender(React.createElement(DesignView));

      expect(input).toHaveAccessibleDescription(error);
      expect(input).toHaveAttribute('aria-invalid', 'true');
      expect(recalculate).toBeDisabled();
      expect(download).toBeDisabled();
    },
  );
});

function currentPassingState() {
  const inputHash = 'i'.repeat(64);
  const calculationIdentity = 'c'.repeat(64);
  return {
    result: {
      success: true,
      message: 'Current passing result',
      flexure: { ast_required: 400, xu: 100, moment_capacity: 200 },
      ast_total: 500,
      asc_total: 0,
      utilization_ratio: 0.8,
      governing_utilization: 0.8,
      holds: [],
      evidence: {
        support_status: 'SUPPORTED',
        status: 'PASS',
        exact_utilization: 0.8,
        margin: 0.2,
        normalized_input_hash: inputHash,
        calculation_identity: calculationIdentity,
        governing_check: 'flexure',
      },
      result_envelope: {
        overall_status: 'PASS',
        engineering_status: 'PASS',
        result_identity: {
          library_version: '0.31.1',
          input_hash: inputHash,
          calculation_identity: calculationIdentity,
        },
      },
    },
    resultRevision: 1,
    resultLifecycle: 'current',
    exportEligible: true,
  };
}
