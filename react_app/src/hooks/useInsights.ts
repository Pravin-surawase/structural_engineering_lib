/**
 * Insights + optimization hooks.
 */
import { useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface DashboardRequest {
  width: number;
  depth: number;
  span: number;
  moment: number;
  shear?: number;
  fck?: number;
  fy?: number;
  cover?: number;
  include_cost?: boolean;
  include_suggestions?: boolean;
  include_sensitivity?: boolean;
  include_constructability?: boolean;
}

export interface DashboardResponse {
  success: boolean;
  message: string;
  dashboard: Record<string, unknown> | null;
  warnings: string[];
}

export interface CodeChecksRequest {
  width: number;
  depth: number;
  span: number;
  moment: number;
  fck?: number;
  fy?: number;
  cover?: number;
}

export interface CodeChecksResponse {
  success: boolean;
  message: string;
  checks: Record<string, unknown> | null;
  warnings: string[];
}

export interface RebarSuggestionRequest {
  ast_required_mm2: number;
  width_mm: number;
  cover_mm?: number;
  stirrup_dia_mm?: number;
  allowed_dia_mm?: number[];
  max_layers?: number;
  agg_size_mm?: number;
  min_total_bars?: number;
  max_bars_per_layer?: number | null;
}

export interface RebarSuggestionItem {
  objective: string;
  count: number;
  diameter: number;
  layers: number;
  area_provided: number;
  spacing: number | null;
  remarks?: string | null;
  checks?: Record<string, unknown> | null;
}

export interface RebarSuggestionResponse {
  success: boolean;
  message: string;
  suggestions: RebarSuggestionItem[];
}

async function postDashboard(
  payload: DashboardRequest
): Promise<DashboardResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/insights/dashboard`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Dashboard failed: ${error.detail || response.status}`);
  }
  return response.json();
}

async function postCodeChecks(
  payload: CodeChecksRequest
): Promise<CodeChecksResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/insights/code-checks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Code checks failed: ${error.detail || response.status}`);
  }
  return response.json();
}

async function postRebarSuggestions(
  payload: RebarSuggestionRequest
): Promise<RebarSuggestionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/optimization/rebar/suggest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Rebar suggestions failed: ${error.detail || response.status}`);
  }
  return response.json();
}

export function useDashboardInsights() {
  return useMutation({
    mutationFn: (payload: DashboardRequest) => postDashboard(payload),
  });
}

export function useCodeChecks() {
  return useMutation({
    mutationFn: (payload: CodeChecksRequest) => postCodeChecks(payload),
  });
}

export function useRebarSuggestions() {
  return useMutation({
    mutationFn: (payload: RebarSuggestionRequest) => postRebarSuggestions(payload),
  });
}
