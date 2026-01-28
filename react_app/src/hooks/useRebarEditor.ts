/**
 * useRebarEditor Hook
 *
 * Provides hooks for rebar validation and application.
 *
 * Uses the /api/v1/rebar/* endpoints which wrap
 * structural_lib.rebar functions for IS 456 compliant checks.
 */
import { useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export interface BeamParams {
  width: number;    // mm
  depth: number;    // mm
  cover?: number;   // mm, default 40
  span?: number;    // mm, default 5000
}

export interface RebarConfig {
  bar_count: number;
  bar_dia: number;           // mm
  stirrup_dia?: number;      // mm, default 8
  layers?: number;           // default 1
  is_top?: boolean;          // default false
  stirrup_spacing_start?: number;  // mm, default 150
  stirrup_spacing_mid?: number;    // mm, default 200
  stirrup_spacing_end?: number;    // mm, default 150
  agg_size?: number;         // mm, default 20
}

export interface ValidationDetail {
  ok: boolean;
  errors: string[];
  warnings: string[];
  details: {
    min_spacing_mm?: number;
    actual_spacing_mm?: number;
    bars_per_layer?: number;
    ast_provided_mm2?: number;
    clear_gap_mm?: number;
  };
}

export interface RebarValidateResponse {
  success: boolean;
  message: string;
  validation: ValidationDetail;
}

export interface RebarApplyResponse {
  success: boolean;
  message: string;
  ast_provided_mm2: number | null;
  validation: ValidationDetail;
  geometry: {
    bar_positions?: Array<{
      center_y_mm: number;
      center_z_mm: number;
      diameter_mm: number;
      layer: number;
    }>;
    stirrup_corners?: Array<[number, number]>;
  } | null;
}

// =============================================================================
// Rebar Validation Hook
// =============================================================================

interface RebarValidateRequest {
  beam: BeamParams;
  config: RebarConfig;
}

async function fetchRebarValidation(
  request: RebarValidateRequest
): Promise<RebarValidateResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/rebar/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Rebar validation failed");
  }

  return response.json();
}

/**
 * Hook for validating rebar configuration against IS 456.
 *
 * @example
 * const { mutate, data, isPending } = useRebarValidation();
 * mutate({
 *   beam: { width: 300, depth: 500 },
 *   config: { bar_count: 4, bar_dia: 16 }
 * });
 */
export function useRebarValidation() {
  return useMutation({
    mutationFn: fetchRebarValidation,
    mutationKey: ["rebar-validation"],
  });
}

// =============================================================================
// Rebar Apply Hook
// =============================================================================

interface RebarApplyRequest {
  beam: BeamParams;
  config: RebarConfig;
}

async function fetchRebarApply(
  request: RebarApplyRequest
): Promise<RebarApplyResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/rebar/apply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Rebar apply failed");
  }

  return response.json();
}

/**
 * Hook for applying rebar configuration and getting geometry preview.
 *
 * Returns both validation results and geometry for visualization.
 *
 * @example
 * const { mutate, data, isPending } = useRebarApply();
 * mutate({
 *   beam: { width: 300, depth: 500 },
 *   config: { bar_count: 4, bar_dia: 16, stirrup_dia: 8 }
 * });
 */
export function useRebarApply() {
  return useMutation({
    mutationFn: fetchRebarApply,
    mutationKey: ["rebar-apply"],
  });
}
