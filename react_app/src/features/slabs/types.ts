export type SlabWorkflowMode = 'simply-supported' | 'continuous' | 'two-way';

export type SlabRequestValue = string | number | boolean;
export type SlabWorkflowRequest = Record<string, SlabRequestValue>;
export type SlabWorkflowResult = Record<string, unknown>;

export interface SlabWorkflowState {
  request: SlabWorkflowRequest;
  result: SlabWorkflowResult | null;
  requestRevision: number;
  resultRevision: number | null;
}
