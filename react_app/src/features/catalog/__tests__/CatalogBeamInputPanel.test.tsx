import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { CatalogBeamInputPanel } from '../CatalogBeamInputPanel';

const CATALOG = {
  schema_version: '1.0',
  catalog_version: '1.0.0',
  code_edition: 'IS 456:2000',
  compatible_versions: ['1.0', '1.0.0'],
  capabilities: [{
    capability_id: 'is456.beam.design',
    capability_version: '1.0.0',
    element: 'beam',
    title: 'IS 456 beam design',
    summary: 'One beam',
    semantic_workflow_id: 'design_beam_is456',
    service_adapter_id: 'fastapi.design_beam.v1',
    request_schema_id: 'fastapi.BeamDesignRequest.v1',
    result_schema_id: 'fastapi.BeamDesignResponse.v1',
    status_semantic_ref: 'workflows.design_beam_is456.statuses.is_ok',
    fields: [
      { field_id: 'b_mm', transport_name: 'width', semantic_ref: 'workflows.design_beam_is456.fields.b_mm', label: 'Width', group: 'Dimensions', widget: 'number', unit: 'mm', required: true, default: 300, minimum: 150, maximum: 2000, choices: [] },
      { field_id: 'D_mm', transport_name: 'depth', semantic_ref: 'workflows.design_beam_is456.fields.D_mm', label: 'Depth', group: 'Dimensions', widget: 'number', unit: 'mm', required: true, default: 500, minimum: 250, maximum: 3000, choices: [] },
      { field_id: 'mu_knm', transport_name: 'moment', semantic_ref: 'workflows.design_beam_is456.fields.mu_knm', label: 'Moment (Mu)', group: 'Design forces', widget: 'number', unit: 'kN m', required: true, default: 150, minimum: 0, maximum: 2000, choices: [] },
      { field_id: 'vu_kn', transport_name: 'shear', semantic_ref: 'workflows.design_beam_is456.fields.vu_kn', label: 'Shear (Vu)', group: 'Design forces', widget: 'number', unit: 'kN', required: true, default: 75, minimum: 0, maximum: 1000, choices: [] },
      { field_id: 'fck_nmm2', transport_name: 'fck', semantic_ref: 'workflows.design_beam_is456.fields.fck_nmm2', label: 'Concrete', group: 'Materials', widget: 'select', unit: 'N/mm2', required: true, default: 25, minimum: null, maximum: null, choices: [20, 25, 30] },
      { field_id: 'fy_nmm2', transport_name: 'fy', semantic_ref: 'workflows.design_beam_is456.fields.fy_nmm2', label: 'Steel', group: 'Materials', widget: 'select', unit: 'N/mm2', required: true, default: 500, minimum: null, maximum: null, choices: [415, 500, 550] },
    ],
    prerequisites: [],
    next_actions: [],
    visualization_affordances: [],
    examples: [],
    limitations: ['Qualified review required.'],
    qualified_review_required: true,
  }],
};

const VALUES = { width: 300, depth: 500, moment: 150, shear: 75, fck: 25, fy: 500 };

afterEach(() => vi.unstubAllGlobals());

describe('CatalogBeamInputPanel', () => {
  it('renders curated fields and sends canonical transport changes', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, data: CATALOG }),
    }));
    const onChange = vi.fn();
    render(<CatalogBeamInputPanel values={VALUES} onChange={onChange} onUseManual={vi.fn()} />);

    const width = await screen.findByLabelText('Width in mm');
    fireEvent.change(width, { target: { value: '350' } });
    expect(onChange).toHaveBeenCalledWith('width', 350);
    expect(screen.getByText(/Catalogue 1.0.0/)).toBeInTheDocument();
  });

  it('shows the reviewed manual escape hatch on contract failure', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    const onUseManual = vi.fn();
    render(<CatalogBeamInputPanel values={VALUES} onChange={vi.fn()} onUseManual={onUseManual} />);

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: 'Use reviewed manual form' }));
    expect(onUseManual).toHaveBeenCalledOnce();
  });
});
