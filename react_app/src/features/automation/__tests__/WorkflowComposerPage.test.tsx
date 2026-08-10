import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { WorkflowComposerPage } from '../WorkflowComposerPage';

const TEMPLATE = {
  schema_version: '1.0',
  workflow_id: 'is456.beam.review',
  workflow_version: '1.0.0',
  title: 'Beam workflow',
  capability_id: 'is456.beam.design',
  steps: ['input', 'validate', 'design', 'review', 'export'].map((step_id, index) => ({
    step_id,
    handler_id: `approved.${step_id}`,
    position: index + 1,
  })),
  bindings: [],
  limits: { max_steps: 5, max_definition_bytes: 16384, max_input_bytes: 32768, max_output_bytes: 262144, max_timeout_ms: 2000, max_concurrency: 1, max_project_members: 1, max_batch_items: 1, max_cached_runs: 128 },
} as const;

const clientMocks = vi.hoisted(() => ({
  fetchTemplate: vi.fn(),
  validate: vi.fn(),
  run: vi.fn(),
  cancel: vi.fn(),
}));

vi.mock('../client', () => ({
  fetchBeamWorkflowTemplate: clientMocks.fetchTemplate,
  validateBeamWorkflow: clientMocks.validate,
  runBeamWorkflow: clientMocks.run,
  cancelBeamWorkflow: clientMocks.cancel,
}));

vi.mock('../../catalog/CatalogBeamInputPanel', () => ({
  CatalogBeamInputPanel: () => <div data-testid="catalog-inputs">Catalogue inputs</div>,
}));

beforeEach(() => {
  clientMocks.fetchTemplate.mockResolvedValue(TEMPLATE);
  clientMocks.validate.mockResolvedValue({ valid: true, workflow_id: 'is456.beam.review', normalized_definition: TEMPLATE, normalized_inputs: {} });
  clientMocks.run.mockResolvedValue({
    run_id: 'beam-test',
    workflow_id: 'is456.beam.review',
    status: 'REVIEW_REQUIRED',
    steps: TEMPLATE.steps.slice(0, 4).map((step) => ({ step_id: step.step_id, status: 'COMPLETED' })),
    export: null,
    audit: { review_stop: 'USER_REVIEW_ACKNOWLEDGEMENT_REQUIRED' },
    definition_hash: 'a',
    input_hash: 'b',
    idempotent_replay: false,
  });
  clientMocks.cancel.mockResolvedValue(true);
});

describe('WorkflowComposerPage', () => {
  it('renders the fixed ordered template and validates it', async () => {
    render(<WorkflowComposerPage />);

    expect(await screen.findByText('approved.input')).toBeInTheDocument();
    expect(screen.getByText('approved.export')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Preview validation' }));
    await waitFor(() => expect(clientMocks.validate).toHaveBeenCalledOnce());
    expect(screen.getByText(/Validated against/)).toBeInTheDocument();
  });

  it('shows the review stop returned by the runner', async () => {
    render(<WorkflowComposerPage />);
    await screen.findByText('approved.input');

    fireEvent.click(screen.getByRole('button', { name: 'Run sample' }));
    expect(await screen.findByText('Run REVIEW_REQUIRED')).toBeInTheDocument();
    expect(screen.getByText(/USER_REVIEW_ACKNOWLEDGEMENT_REQUIRED/)).toBeInTheDocument();
  });

  it('cancels the active request through the runner before aborting locally', async () => {
    clientMocks.run.mockImplementation(
      (_definition, _inputs, _runId, _reviewed, signal: AbortSignal) =>
        new Promise((_resolve, reject) => {
          signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
        }),
    );
    render(<WorkflowComposerPage />);
    await screen.findByText('approved.input');

    fireEvent.click(screen.getByRole('button', { name: 'Run sample' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Cancel' }));

    await waitFor(() => expect(clientMocks.cancel).toHaveBeenCalledOnce());
    expect(await screen.findByText(/Cancellation requested/)).toBeInTheDocument();
  });
});
