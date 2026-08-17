import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { BuildingGravityReviewPage } from './BuildingGravityReviewPage';

const { definitionMock, runMock } = vi.hoisted(() => ({
  definitionMock: vi.fn(),
  runMock: vi.fn(),
}));

vi.mock('./client', () => ({
  getGravityWorkflowDefinition: definitionMock,
  runGravityWorkflow: runMock,
}));

const envelope = (status: 'PASS' | 'FAIL' | 'HOLD') => ({
  overall_status: status,
  qualified_review_required: true,
  review_status: 'QUALIFIED_REVIEW_REQUIRED',
  issues: status === 'HOLD' ? [{ code: 'BASIS_MISSING', path: '$.components.F1', message: 'External basis missing' }] : [],
});

function bundle() {
  return {
    schema_version: 'gravity-workflow-run-bundle/v1',
    workflow_result: {
      schema_version: 'gravity-workflow-result/v1',
      model_hash: '1'.repeat(64),
      load_model_hash: '2'.repeat(64),
      ledger_hash: '3'.repeat(64),
      workflow_result_hash: '4'.repeat(64),
      result_envelope: envelope('HOLD'),
      components: [
        { component_id: 'B1', kind: 'BEAM', canonical_function: 'design_beam_is456', result_envelope: envelope('PASS'), result: {} },
        { component_id: 'B2', kind: 'BEAM', canonical_function: 'design_beam_is456', result_envelope: envelope('FAIL'), result: {} },
        { component_id: 'F1', kind: 'FOOTING', canonical_function: 'design_concentric_isolated_footing_is456', result_envelope: envelope('HOLD'), result: null },
      ],
      actions: [
        {
          action_id: 'action:ULS_1_5_DL_LL:F1',
          component_id: 'F1',
          kind: 'FOOTING',
          combination_id: 'ULS_1_5_DL_LL',
          area_load_kn_m2: null,
          line_load_kn_m: null,
          moment_knm: null,
          shear_kn: null,
          axial_kn: 101.25,
        },
      ],
      limitations: ['No lateral loads.'],
    },
    calculation_book: {
      schema_version: 'gravity-calculation-book/v1',
      workflow_result_hash: '4'.repeat(64),
      reconciliation: {
        all_balanced: true,
        boundary_count: 26,
        maximum_absolute_residual_kn: 0,
        balance_tolerance_kn: 1e-9,
        accepted_entry_count: 41,
        blocked_entry_count: 0,
      },
      approved_exclusions: [],
      limitations: [],
      issues: [],
      review_disposition: 'QUALIFIED_REVIEW_REQUIRED',
    },
  };
}

describe('BuildingGravityReviewPage', () => {
  beforeEach(() => {
    definitionMock.mockReset();
    runMock.mockReset();
    definitionMock.mockResolvedValue({
      schema_version: 'gravity-workflow-definition/v1',
      capability_id: 'building.gravity.dead-live.v1',
      title: 'Building Gravity Workflow V1',
      summary: 'Bounded gravity workflow',
      accepted_topology: ['one slab', 'two beams'],
      component_adapters: {},
      product_surfaces: {},
      exclusions: [],
      qualified_review_required: true,
    });
  });

  it('blocks malformed JSON before contacting the calculation API', async () => {
    render(<BuildingGravityReviewPage />);
    fireEvent.change(screen.getByLabelText(/GravityWorkflowRequestV1 JSON/i), {
      target: { value: '{bad json' },
    });
    fireEvent.click(screen.getByRole('button', { name: /run gravity review/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/INPUT BLOCKED/i);
    expect(runMock).not.toHaveBeenCalled();
  });

  it('shows aggregate and per-component truth with exact actions and review hold', async () => {
    runMock.mockResolvedValue(bundle());
    render(<BuildingGravityReviewPage />);
    fireEvent.change(screen.getByLabelText(/GravityWorkflowRequestV1 JSON/i), {
      target: { value: '{"schema_version":"gravity-workflow-request/v1"}' },
    });
    fireEvent.click(screen.getByRole('button', { name: /run gravity review/i }));

    expect(await screen.findByText('26 load boundaries · residual 0 kN')).toBeInTheDocument();
    expect(screen.getAllByText('HOLD').length).toBeGreaterThan(0);
    expect(screen.getAllByText('PASS').length).toBeGreaterThan(0);
    expect(screen.getAllByText('FAIL').length).toBeGreaterThan(0);
    expect(screen.getByText('101.250 kN')).toBeInTheDocument();
    expect(screen.getAllByText(/QUALIFIED REVIEW REQUIRED/i).length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: /download calculation book/i })).toBeEnabled();
    expect(runMock).toHaveBeenCalledWith(
      { schema_version: 'gravity-workflow-request/v1' },
    );
  });
});
