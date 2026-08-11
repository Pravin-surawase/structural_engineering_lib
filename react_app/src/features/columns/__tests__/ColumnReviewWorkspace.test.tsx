import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { ColumnReviewBundle } from '../types';
import { ColumnReviewWorkspace } from '../ColumnReviewWorkspace';

const { reviewRectangularColumnMock } = vi.hoisted(() => ({
  reviewRectangularColumnMock: vi.fn(),
}));

vi.mock('../api', () => ({
  reviewRectangularColumn: reviewRectangularColumnMock,
}));

const SAFE_BUNDLE: ColumnReviewBundle = {
  design: {
    Pu_kN: 800,
    Mux_applied_kNm: 120,
    Muy_applied_kNm: 40,
    Mux_design_kNm: 120,
    Muy_design_kNm: 40,
    Mux_min_kNm: 20.8,
    Muy_min_kNm: 16,
    Ma_x_kNm: null,
    Ma_y_kNm: null,
    is_safe: true,
    classification: 'SHORT',
    classification_x: 'SHORT',
    classification_y: 'SHORT',
    le_x_mm: 1950,
    le_y_mm: 1950,
    slenderness_x: 4.333,
    slenderness_y: 6.5,
    emin_x_mm: 26,
    emin_y_mm: 20,
    governing_check: 'biaxial',
    checks: { biaxial: { interaction_ratio: 0.7152, is_safe: true, clause_ref: 'Cl. 39.6' } },
    clause_refs: ['Cl. 25.2', 'Cl. 25.1.2', 'Cl. 25.4', 'Cl. 39.6'],
    warnings: [],
  },
  detailing: {
    b_mm: 300,
    D_mm: 450,
    Ag_mm2: 135000,
    num_bars: 8,
    bar_dia_mm: 20,
    Asc_provided_mm2: 2513.27,
    steel_ratio: 0.018617,
    min_steel_ok: true,
    max_steel_ok: true,
    min_bars_ok: true,
    min_bar_dia_ok: true,
    bar_spacing_mm: 145,
    bar_spacing_ok: true,
    tie_dia_mm: 8,
    tie_dia_required_mm: 6,
    tie_spacing_mm: 300,
    max_tie_spacing_mm: 300,
    tie_spacing_ok: true,
    cross_ties_needed: false,
    is_valid: true,
    clause_ref: 'Cl. 26.5.3',
    warnings: [],
  },
};

const SLENDER_BUNDLE: ColumnReviewBundle = {
  ...SAFE_BUNDLE,
  design: {
    ...SAFE_BUNDLE.design,
    Mux_design_kNm: 142.5,
    Muy_design_kNm: 54.25,
    Ma_x_kNm: 22.5,
    Ma_y_kNm: 14.25,
    classification: 'SLENDER',
    classification_x: 'SLENDER',
    classification_y: 'SLENDER',
    le_x_mm: 6000,
    le_y_mm: 6000,
    slenderness_x: 13.333,
    slenderness_y: 20,
    governing_check: 'long_column',
    checks: {
      long_column: {
        interaction_ratio: 0.82,
        is_safe: true,
        clause_ref: 'Cl. 39.7',
      },
    },
    clause_refs: [...SAFE_BUNDLE.design.clause_refs, 'Cl. 39.7'],
  },
};

beforeEach(() => {
  reviewRectangularColumnMock.mockReset();
});

describe('ColumnReviewWorkspace', () => {
  it('states the bounded check semantics, units, assumptions, and held scope', () => {
    render(<ColumnReviewWorkspace onExport={vi.fn()} />);

    expect(screen.getByText('Rectangular tied-column check and review')).toBeInTheDocument();
    expect(screen.getByText(/Supplied-section adequacy check only/)).toBeInTheDocument();
    expect(screen.getByText(/symmetric two-face, two-layer reinforcement/)).toBeInTheDocument();
    expect(screen.getByText(/does not automatically design the member or reinforcement/)).toBeInTheDocument();
    expect(screen.getByText(/Leaving both values for an axis blank uses the maintained equal-end-moment fallback/)).toBeInTheDocument();
    expect(screen.getByLabelText('End moment M1x')).toHaveValue(null);
  });

  it('shows review-complete classification, eccentricity, detailing, and revision identity', async () => {
    const user = userEvent.setup();
    reviewRectangularColumnMock.mockResolvedValue(SAFE_BUNDLE);
    render(<ColumnReviewWorkspace onExport={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: 'Check supplied column' }));

    expect(reviewRectangularColumnMock).toHaveBeenCalledWith(expect.objectContaining({
      M1x_kNm: null,
      M2x_kNm: null,
      M1y_kNm: null,
      M2y_kNm: null,
    }));
    expect(await screen.findByText('CHECK PASSED')).toBeInTheDocument();
    expect(screen.getByText('x SHORT · y SHORT')).toBeInTheDocument();
    expect(screen.getByText('x 26.00 mm · y 20.00 mm')).toBeInTheDocument();
    expect(screen.getByText('8-T20')).toBeInTheDocument();
    expect(screen.getByText(/Qualified structural-engineering review is required/)).toBeInTheDocument();
    expect(screen.getAllByText(/column-v1-/)).toHaveLength(2);
    expect(screen.getByRole('button', { name: 'Export current review packet' })).toBeEnabled();
  });

  it('submits explicit slender end moments and reviews returned additional moments', async () => {
    const user = userEvent.setup();
    const onExport = vi.fn();
    reviewRectangularColumnMock.mockResolvedValue(SLENDER_BUNDLE);
    render(<ColumnReviewWorkspace onExport={onExport} />);

    await user.type(screen.getByLabelText('End moment M1x'), '30');
    await user.type(screen.getByLabelText('End moment M2x'), '80');
    await user.type(screen.getByLabelText('End moment M1y'), '20');
    await user.type(screen.getByLabelText('End moment M2y'), '60');
    await user.click(screen.getByRole('button', { name: 'Check supplied column' }));

    expect(reviewRectangularColumnMock).toHaveBeenCalledWith(expect.objectContaining({
      M1x_kNm: 30,
      M2x_kNm: 80,
      M1y_kNm: 20,
      M2y_kNm: 60,
    }));
    expect(await screen.findByText('CHECK PASSED')).toBeInTheDocument();
    expect(screen.getByText('Slender-column check with additional moments')).toBeInTheDocument();
    expect(screen.getByText('x 22.50 · y 14.25 kN·m')).toBeInTheDocument();
    const exportButton = screen.getByRole('button', { name: 'Export current review packet' });
    expect(exportButton).toBeEnabled();

    await user.click(exportButton);
    expect(onExport).toHaveBeenCalledWith(expect.objectContaining({ decision: 'PASS' }));
  });

  it('keeps an inadequate result explicit and holds export', async () => {
    const user = userEvent.setup();
    reviewRectangularColumnMock.mockResolvedValue({
      ...SAFE_BUNDLE,
      design: {
        ...SAFE_BUNDLE.design,
        is_safe: false,
        checks: { biaxial: { interaction_ratio: 1.42, is_safe: false } },
      },
    });
    render(<ColumnReviewWorkspace onExport={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: 'Check supplied column' }));

    expect(await screen.findByText('CHECK FAILED')).toBeInTheDocument();
    expect(screen.getByText('1.4200')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Export current review packet' })).toBeDisabled();
    expect(screen.getByText(/Export held until both adequacy/)).toBeInTheDocument();
  });

  it('marks a prior result stale and blocks export after any input revision', async () => {
    const user = userEvent.setup();
    const onExport = vi.fn();
    reviewRectangularColumnMock.mockResolvedValue(SAFE_BUNDLE);
    render(<ColumnReviewWorkspace onExport={onExport} />);

    await user.click(screen.getByRole('button', { name: 'Check supplied column' }));
    expect(await screen.findByText('CHECK PASSED')).toBeInTheDocument();
    const exportButton = screen.getByRole('button', { name: 'Export current review packet' });
    expect(exportButton).toBeEnabled();

    await user.clear(screen.getByLabelText('Member label'));
    await user.type(screen.getByLabelText('Member label'), 'C2');

    expect(screen.getByText('RESULT STALE')).toBeInTheDocument();
    expect(exportButton).toBeDisabled();
    expect(screen.getByText(/Export blocked because the result does not match/)).toBeInTheDocument();
    expect(onExport).not.toHaveBeenCalled();
  });

  it('fails closed to HOLD and clears a prior exportable result when the API request fails', async () => {
    const user = userEvent.setup();
    reviewRectangularColumnMock
      .mockResolvedValueOnce(SAFE_BUNDLE)
      .mockRejectedValueOnce(new Error('Backend unavailable'));
    render(<ColumnReviewWorkspace onExport={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: 'Check supplied column' }));
    expect(await screen.findByText('CHECK PASSED')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Export current review packet' })).toBeEnabled();

    await user.click(screen.getByRole('button', { name: 'Check supplied column' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('HOLD — Backend unavailable');
    expect(screen.queryByRole('button', { name: 'Export current review packet' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Check supplied column' })).toBeEnabled();
  });
});
