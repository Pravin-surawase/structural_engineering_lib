import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useImportedBeamsStore } from '../../../store/importedBeamsStore';
import { useWorkspaceStore } from '../../../workspace/workspaceStore';
import { Viewport3D } from '../Viewport3D';
import { ViewportOverlay } from '../ViewportOverlay';

const emptyCounts = {
  pass: 0,
  fail: 0,
  hold: 0,
  pending: 0,
  stale: 0,
  error: 0,
  not_evaluated: 0,
};

describe('ViewportOverlay', () => {
  beforeEach(() => {
    useWorkspaceStore.getState().reset();
    useImportedBeamsStore.setState({ beams: [], selectedId: null, selectedFloor: null });
  });

  it('keeps current selection evidence and inspection controls available in the DOM', () => {
    const onFloorChange = vi.fn();
    const onFit = vi.fn();
    render(
      <ViewportOverlay
        floors={['GF', '1F']}
        frameTypes={['beam', 'column']}
        selectedFloor={null}
        frameFilter="all"
        isolateSelection={false}
        showStatus
        showUtilization
        hasCurrentUtilization
        selected={{
          memberId: 'ETABS-101',
          label: 'B1',
          story: 'GF',
          frameType: 'beam',
          status: 'pass',
          utilization: 0.8,
        }}
        statusCounts={{ ...emptyCounts, pass: 1 }}
        geometryFailure={null}
        onFloorChange={onFloorChange}
        onFrameFilterChange={vi.fn()}
        onIsolateSelectionChange={vi.fn()}
        onShowStatusChange={vi.fn()}
        onShowUtilizationChange={vi.fn()}
        onFit={onFit}
      />,
    );

    expect(screen.getByTestId('viewport-selected-member')).toHaveTextContent('ETABS-101');
    expect(screen.getByTestId('viewport-selected-member')).toHaveTextContent('utilization 0.800');
    expect(screen.getByRole('region', { name: 'Current member status legend' })).toHaveTextContent('PASS');
    fireEvent.change(screen.getByLabelText('Viewport floor'), { target: { value: 'GF' } });
    fireEvent.click(screen.getByRole('button', { name: 'Fit selected' }));
    expect(onFloorChange).toHaveBeenCalledWith('GF');
    expect(onFit).toHaveBeenCalledOnce();
  });

  it('fails closed while preserving non-WebGL project status access', () => {
    useImportedBeamsStore.getState().setBeams([{
      id: 'B1',
      source_id: 'ETABS-101',
      story: 'GF',
      b: 300,
      D: 500,
      span: 6000,
      point1: undefined,
      point2: undefined,
    }]);

    render(<Viewport3D mode="building" forceMode />);

    expect(screen.getByTestId('geometry-space-v1-invalid')).toHaveTextContent(
      'Member ETABS-101 has incomplete identity, section, or source geometry.',
    );
    expect(screen.getByRole('region', { name: 'Current member status legend' })).toHaveTextContent(
      'Not evaluated',
    );
    expect(screen.getByText('3D rendering unavailable')).toBeInTheDocument();
  });
});
