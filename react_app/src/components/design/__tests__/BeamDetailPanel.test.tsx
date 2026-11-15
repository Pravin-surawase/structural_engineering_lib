import { fireEvent, render, screen } from '@testing-library/react';
import { useState } from 'react';
import { describe, expect, it, vi } from 'vitest';
import type { BeamCSVRow } from '../../../types/csv';
import { BeamDetailPanel } from '../BeamDetailPanel';

const store = vi.hoisted(() => ({
  beams: [] as BeamCSVRow[],
  error: null as string | null,
  setBeams: vi.fn(),
}));
const startBatchDesign = vi.hoisted(() => vi.fn());

vi.mock('../../../hooks/useBeamGeometry', () => ({
  useBeamGeometry: () => ({ data: null, isPending: false }),
}));
vi.mock('../../../hooks', () => ({
  useExportBBS: () => ({ mutate: vi.fn(), isPending: false }),
  useExportDXF: () => ({ mutate: vi.fn(), isPending: false }),
  useExportReport: () => ({ mutate: vi.fn(), isPending: false }),
}));
vi.mock('../../../hooks/useBatchDesign', () => ({
  useBatchDesign: () => ({ startBatchDesign, status: 'idle' }),
}));
vi.mock('../../../store/importedBeamsStore', () => ({
  useImportedBeamsStore: Object.assign(() => undefined, {
    getState: () => store,
  }),
}));
vi.mock('../../../workspace/workspaceStore', () => ({
  useWorkspaceStore: Object.assign(() => null, { getState: () => ({ snapshot: null }) }),
}));
vi.mock('../../../workspace/resultRecords', () => ({
  currentWorkbenchLayout: () => null,
}));
vi.mock('../../viewport/Viewport3D', () => ({ Viewport3D: () => null }));

const beam = (id: string, label: string): BeamCSVRow => ({
  id,
  source_id: label,
  story: 'GF',
  b: 300,
  D: 450,
  span: 5000,
  ast_required: 500,
});

function SelectedPanel({ first, second }: { first: BeamCSVRow; second: BeamCSVRow }) {
  const [selected, setSelected] = useState(first);
  return (
    <>
      <button onClick={() => setSelected(first)}>Select A</button>
      <button onClick={() => setSelected(second)}>Select B</button>
      <BeamDetailPanel beam={selected} onClose={vi.fn()} />
    </>
  );
}

describe('BeamDetailPanel reinforcement edits', () => {
  it('does not transfer an open A draft to B when the visible labels repeat', () => {
    const first = beam('member-a', 'Repeated beam label');
    const second = beam('member-b', 'Repeated beam label');
    store.beams = [first, second];
    store.error = null;
    store.setBeams.mockClear();
    startBatchDesign.mockClear();

    render(<SelectedPanel first={first} second={second} />);
    fireEvent.click(screen.getByRole('button', { name: 'Edit Rebar' }));
    fireEvent.change(screen.getByLabelText('Bar Count'), { target: { value: '6' } });
    fireEvent.click(screen.getByRole('button', { name: 'Select B' }));

    expect(screen.queryByText('Override Reinforcement')).not.toBeInTheDocument();
    expect(store.setBeams).not.toHaveBeenCalled();
    expect(startBatchDesign).not.toHaveBeenCalled();
  });

  it('saves a deliberate B edit to B even when its source label repeats', () => {
    const first = beam('member-a', 'Repeated beam label');
    const second = beam('member-b', 'Repeated beam label');
    store.beams = [first, second];
    store.error = null;
    store.setBeams.mockClear();
    startBatchDesign.mockClear();

    render(<SelectedPanel first={first} second={second} />);
    fireEvent.click(screen.getByRole('button', { name: 'Select B' }));
    fireEvent.click(screen.getByRole('button', { name: 'Edit Rebar' }));
    fireEvent.change(screen.getByLabelText('Bar Count'), { target: { value: '6' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save and check' }));

    const updated = store.setBeams.mock.calls[0][0] as BeamCSVRow[];
    expect(updated.find((item) => item.id === first.id)).toEqual(first);
    expect(updated.find((item) => item.id === second.id)).toMatchObject({
      id: second.id,
      requested_bar_count: 6,
      status: 'pending',
    });
    expect(startBatchDesign).toHaveBeenCalledWith([
      expect.objectContaining({ id: second.id, requested_bar_count: 6 }),
    ]);
  });
});
