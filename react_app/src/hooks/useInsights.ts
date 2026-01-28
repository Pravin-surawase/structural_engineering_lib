/**
 * useInsights Hook
 *
 * Provides hooks for dashboard aggregation, live code checks,
 * and rebar optimization suggestions.
 *
 * Uses the /api/v1/insights/* endpoints which wrap the
 * structural_lib.dashboard module.
 */
import { useMutation, useQuery } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export interface BeamResult {
  beam_id: string;
  story: string;
  is_valid: boolean;
  utilization: number;
  ast_provided: number;
  b_mm: number;
  D_mm: number;
  span_mm: number;
  warnings: string[];
}

export interface StoryStats {
  total: number;
  passed: number;
  failed: number;
}

export interface DashboardData {
  success: boolean;
  message: string;
  total_beams: number;
  passed: number;
  failed: number;
  pass_rate: number;
  warnings_count: number;
  avg_utilization: number;
  max_utilization: number;
  min_utilization: number;
  total_steel_kg: number;
  total_concrete_m3: number;
  critical_beams: string[];
  by_story: Record<string, StoryStats>;
}

export interface CheckDetail {
  name: string;
  clause: string;
  passed: boolean;
  value: number;
  limit: number;
  utilization?: number;
}

export interface CodeChecksResult {
  success: boolean;
  message: string;
  passed: boolean;
  checks: CheckDetail[];
  critical_failures: string[];
  warnings: string[];
  utilization: number;
  governing_check: string;
}

export interface SuggestionItem {
  id: string;
  title: string;
  description: string;
  impact: "LOW" | "MEDIUM" | "HIGH";
  savings_percent: number;
  suggested_config: {
    bar_count: number;
    bar_dia_mm: number;
    ast_provided_mm2: number;
    excess_mm2: number;
  };
  rationale: string;
}

export interface RebarSuggestionsResult {
  success: boolean;
  message: string;
  beam_id: string;
  suggestion_count: number;
  suggestions: SuggestionItem[];
  current_ast_mm2: number;
  min_ast_mm2: number;
  max_savings_percent: number;
}

// =============================================================================
// Dashboard Hook
// =============================================================================

interface DashboardRequest {
  results: BeamResult[];
}

async function fetchDashboard(
  request: DashboardRequest
): Promise<DashboardData> {
  const response = await fetch(`${API_BASE_URL}/api/v1/insights/dashboard`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Dashboard generation failed");
  }

  return response.json();
}

/**
 * Hook for generating dashboard summaries from beam results.
 *
 * @example
 * const { mutate, data, isPending } = useDashboardInsights();
 * mutate({ results: designedBeams });
 */
export function useDashboardInsights() {
  return useMutation({
    mutationFn: fetchDashboard,
    mutationKey: ["dashboard"],
  });
}

// =============================================================================
// Code Checks Hook
// =============================================================================

interface BeamParams {
  b_mm?: number;
  D_mm?: number;
  d_mm?: number;
  span_mm?: number;
  fck_mpa?: number;
  fy_mpa?: number;
  mu_knm?: number;
  vu_kn?: number;
}

interface RebarParams {
  ast_mm2?: number;
  bar_count?: number;
  bar_dia_mm?: number;
}

interface CodeChecksRequest {
  beam: BeamParams;
  config?: RebarParams | null;
}

async function fetchCodeChecks(
  request: CodeChecksRequest
): Promise<CodeChecksResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/insights/code-checks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Code checks failed");
  }

  return response.json();
}

/**
 * Hook for live IS 456 code checks during editing.
 *
 * @example
 * const { mutate, data, isPending } = useCodeChecks();
 * mutate({ beam: beamData, config: rebarConfig });
 */
export function useCodeChecks() {
  return useMutation({
    mutationFn: fetchCodeChecks,
    mutationKey: ["code-checks"],
  });
}

// =============================================================================
// Rebar Suggestions Hook
// =============================================================================

interface RebarSuggestRequest {
  beam_id?: string;
  ast_required: number;
  ast_provided?: number;
  bar_count?: number;
  bar_dia_mm?: number;
  b_mm?: number;
  cover_mm?: number;
}

async function fetchRebarSuggestions(
  request: RebarSuggestRequest
): Promise<RebarSuggestionsResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/insights/rebar-suggest`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Rebar suggestion failed");
  }

  return response.json();
}

/**
 * Hook for rebar optimization suggestions.
 *
 * @example
 * const { mutate, data, isPending } = useRebarSuggestions();
 * mutate({ ast_required: 500, b_mm: 300 });
 */
export function useRebarSuggestions() {
  return useMutation({
    mutationFn: fetchRebarSuggestions,
    mutationKey: ["rebar-suggestions"],
  });
}
