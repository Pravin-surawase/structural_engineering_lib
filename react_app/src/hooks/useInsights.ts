/**
 * useInsights — Dashboard, Code Checks, and Rebar Suggestions hooks
 *
 * @example
 * const { data: dashboard } = useDashboard(designResult);
 * const { data: checks } = useCodeChecks(beam, config);
 * const { data: suggestions } = useRebarSuggestions(beam, astRequired);
 */
import { useQuery, useMutation, type UseQueryResult, type UseMutationResult } from '@tanstack/react-query';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

// =============================================================================
// Types
// =============================================================================

export interface BeamParams {
  b_mm: number;
  D_mm: number;
  cover_mm: number;
  span_mm: number;
  fck: number;
  fy: number;
  stirrup_dia_mm: number;
  agg_size_mm: number;
}

export interface RebarConfig {
  bar_count: number;
  bar_dia_mm: number;
  layers: number;
  stirrup_dia_mm: number;
}

export interface DesignResult {
  id?: string;
  beam_id?: string;
  mu_knm?: number;
  vu_kn?: number;
  ast_mm2?: number;
  status?: string;
  utilization?: number;
  moment_capacity_knm?: number;
  shear_capacity_kn?: number;
  messages?: string[];
  [key: string]: unknown;
}

// Dashboard types
export interface UtilizationData {
  moment: number;
  shear: number;
  overall: number;
}

export interface SteelData {
  astRequired: number;
  astProvided: number;
  ratioPercent: number;
}

export interface CapacityData {
  momentKnm: number;
  shearKn: number;
}

export interface AppliedData {
  momentKnm: number;
  shearKn: number;
}

export interface CodeChecksData {
  passed: number;
  total: number;
  critical: string[];
}

export interface DashboardResponse {
  beamId: string;
  status: 'pass' | 'fail' | 'warning';
  utilization: UtilizationData;
  steel: SteelData;
  capacity: CapacityData;
  applied: AppliedData;
  codeChecks: CodeChecksData;
  messages: string[];
}

// Code checks types
export interface SingleCodeCheck {
  clause: string;
  description: string;
  passed: boolean;
  value: number | null;
  limit: number | null;
  message: string;
}

export interface CodeChecksResponse {
  overallPass: boolean;
  checks: SingleCodeCheck[];
  errors: string[];
  warnings: string[];
  passCount: number;
  failCount: number;
}

// Rebar suggestions types
export interface RebarSuggestion {
  barCount: number;
  barDia: number;
  layers: number;
  astProvided: number;
  utilization: number;
  costIndex: number;
  spacingOk: boolean;
  message: string;
}

export interface RebarSuggestResponse {
  success: boolean;
  suggestions: RebarSuggestion[];
  target_ast_mm2: number;
  message: string;
}

// =============================================================================
// API Functions
// =============================================================================

async function fetchDashboard(
  designResult: DesignResult,
  beamParams?: BeamParams
): Promise<DashboardResponse> {
  const response = await fetch(`${API_BASE}/api/v1/insights/dashboard`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      design_result: designResult,
      beam_params: beamParams,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Dashboard generation failed' }));
    throw new Error(error.detail || 'Dashboard generation failed');
  }

  return response.json();
}

async function fetchCodeChecks(
  beam: BeamParams,
  config: RebarConfig
): Promise<CodeChecksResponse> {
  const response = await fetch(`${API_BASE}/api/v1/insights/code-checks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ beam, config }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Code checks failed' }));
    throw new Error(error.detail || 'Code checks failed');
  }

  return response.json();
}

async function fetchRebarSuggestions(
  beam: BeamParams,
  astRequired: number,
  options?: { minBars?: number; maxLayers?: number; maxOptions?: number }
): Promise<RebarSuggestResponse> {
  const response = await fetch(`${API_BASE}/api/v1/insights/rebar-suggest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      beam,
      ast_required_mm2: astRequired,
      min_bars: options?.minBars ?? 2,
      max_layers: options?.maxLayers ?? 2,
      max_options: options?.maxOptions ?? 5,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Rebar suggestions failed' }));
    throw new Error(error.detail || 'Rebar suggestions failed');
  }

  return response.json();
}

// =============================================================================
// Query Hooks
// =============================================================================

/**
 * Fetch dashboard data for a design result.
 *
 * @param designResult - Design result from design_beam_is456
 * @param beamParams - Optional beam parameters for context
 * @param enabled - Whether to enable the query
 */
export function useDashboard(
  designResult: DesignResult | null,
  beamParams?: BeamParams,
  enabled = true
): UseQueryResult<DashboardResponse, Error> {
  return useQuery({
    queryKey: ['dashboard', designResult?.id ?? 'default', beamParams],
    queryFn: () => fetchDashboard(designResult!, beamParams),
    enabled: enabled && designResult !== null,
    staleTime: 30_000, // 30 seconds
    gcTime: 5 * 60_000, // 5 minutes
  });
}

/**
 * Fetch live code checks for beam + rebar config.
 *
 * @param beam - Beam parameters
 * @param config - Rebar configuration
 * @param enabled - Whether to enable the query
 */
export function useCodeChecks(
  beam: BeamParams | null,
  config: RebarConfig | null,
  enabled = true
): UseQueryResult<CodeChecksResponse, Error> {
  return useQuery({
    queryKey: ['code-checks', beam, config],
    queryFn: () => fetchCodeChecks(beam!, config!),
    enabled: enabled && beam !== null && config !== null,
    staleTime: 10_000, // 10 seconds
    refetchOnWindowFocus: false,
  });
}

/**
 * Fetch rebar suggestions for given requirements.
 *
 * @param beam - Beam parameters
 * @param astRequired - Required steel area (mm²)
 * @param options - Additional options (minBars, maxLayers, maxOptions)
 * @param enabled - Whether to enable the query
 */
export function useRebarSuggestions(
  beam: BeamParams | null,
  astRequired: number | null,
  options?: { minBars?: number; maxLayers?: number; maxOptions?: number },
  enabled = true
): UseQueryResult<RebarSuggestResponse, Error> {
  return useQuery({
    queryKey: ['rebar-suggestions', beam, astRequired, options],
    queryFn: () => fetchRebarSuggestions(beam!, astRequired!, options),
    enabled: enabled && beam !== null && astRequired !== null && astRequired > 0,
    staleTime: 60_000, // 1 minute
  });
}

// =============================================================================
// Mutation Hooks
// =============================================================================

/**
 * Mutation hook for on-demand dashboard generation.
 */
export function useDashboardMutation(): UseMutationResult<
  DashboardResponse,
  Error,
  { designResult: DesignResult; beamParams?: BeamParams }
> {
  return useMutation({
    mutationFn: ({ designResult, beamParams }) => fetchDashboard(designResult, beamParams),
  });
}

/**
 * Mutation hook for on-demand code checks.
 */
export function useCodeChecksMutation(): UseMutationResult<
  CodeChecksResponse,
  Error,
  { beam: BeamParams; config: RebarConfig }
> {
  return useMutation({
    mutationFn: ({ beam, config }) => fetchCodeChecks(beam, config),
  });
}

/**
 * Mutation hook for on-demand rebar suggestions.
 */
export function useRebarSuggestionsMutation(): UseMutationResult<
  RebarSuggestResponse,
  Error,
  {
    beam: BeamParams;
    astRequired: number;
    options?: { minBars?: number; maxLayers?: number; maxOptions?: number };
  }
> {
  return useMutation({
    mutationFn: ({ beam, astRequired, options }) =>
      fetchRebarSuggestions(beam, astRequired, options),
  });
}
