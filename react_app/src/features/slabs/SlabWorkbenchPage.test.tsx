import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SlabWorkbenchPage } from './SlabWorkbenchPage';

const { designSlabWorkflowMock } = vi.hoisted(() => ({
  designSlabWorkflowMock: vi.fn(),
}));

vi.mock('./client', () => ({
  designSlabWorkflow: designSlabWorkflowMock,
}));

describe('SlabWorkbenchPage', () => {
  beforeEach(() => designSlabWorkflowMock.mockReset());

  it('runs the built-in continuous route and invalidates a stale passport', async () => {
    designSlabWorkflowMock.mockResolvedValue({
      flexure: {
        input: {
          coefficients: {
            method: 'built_in_exact',
            table_id: 'IS456_TABLE_12_13',
          },
        },
        positive_midspan: { factored_moment_knm_per_m: 10.6875 },
        negative_support: { factored_moment_knm_per_m: 12.825 },
      },
      shear: { tau_v_n_per_mm2: 0.31 },
      serviceability: { utilization: 0.94 },
    });

    render(<SlabWorkbenchPage />);

    expect(screen.getByText(/flat slabs, drops, column strips/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /run slab design/i }));

    expect(await screen.findByText('10.688')).toBeInTheDocument();
    expect(screen.getByText(/is456_table_12_13 · built_in_exact/i)).toBeInTheDocument();
    expect(designSlabWorkflowMock).toHaveBeenCalledWith(
      'continuous',
      expect.objectContaining({ number_of_spans: 3 }),
      expect.any(AbortSignal),
    );

    const download = screen.getByRole('button', { name: /download passport/i });
    expect(download).toBeEnabled();
    fireEvent.change(screen.getByRole('spinbutton', { name: /effective span/i }), {
      target: { value: '3200' },
    });
    expect(screen.getByText(/inputs changed after this response/i)).toBeInTheDocument();
    expect(screen.getByText('stale')).toBeInTheDocument();
    expect(download).toBeDisabled();
  });

  it('switches to the oriented two-way built-in workflow', () => {
    render(<SlabWorkbenchPage />);

    fireEvent.click(screen.getByRole('button', { name: /two-way panel/i }));

    expect(screen.getByRole('spinbutton', { name: /short x span/i })).toHaveValue(4000);
    expect(screen.getByText(/physical edges resolve the table 26\/27 case/i)).toBeInTheDocument();
    expect(screen.getByText(/physical edges • middle and edge strips/i)).toBeInTheDocument();
  });
});
