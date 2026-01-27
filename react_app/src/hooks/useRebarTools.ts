/**
 * Rebar validation/apply hooks.
 */
import { useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface BeamDimensions {
  width_mm: number;
  depth_mm: number;
  cover_mm?: number;
  span_mm?: number;
}

export interface RebarConfig {
  bar_count: number;
  bar_dia_mm: number;
  stirrup_dia_mm?: number;
  layers?: number;
  is_top?: boolean;
  stirrup_spacing_start?: number;
  stirrup_spacing_mid?: number;
  stirrup_spacing_end?: number;
  agg_size_mm?: number;
}

export interface RebarValidationResult {
  success: boolean;
  message: string;
  validation: Record<string, unknown>;
  warnings: string[];
}

export interface RebarApplyResult {
  success: boolean;
  message: string;
  validation: Record<string, unknown> | null;
  geometry: Record<string, unknown> | null;
  warnings: string[];
}

async function postRebarValidate(
  beam: BeamDimensions,
  config: RebarConfig
): Promise<RebarValidationResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/rebar/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ beam, config }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Rebar validation failed: ${error.detail || response.status}`);
  }

  return response.json();
}

async function postRebarApply(
  beam: BeamDimensions,
  config: RebarConfig
): Promise<RebarApplyResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/rebar/apply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ beam, config }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Rebar apply failed: ${error.detail || response.status}`);
  }

  return response.json();
}

export function useRebarValidation() {
  return useMutation({
    mutationFn: ({
      beam,
      config,
    }: {
      beam: BeamDimensions;
      config: RebarConfig;
    }) => postRebarValidate(beam, config),
  });
}

export function useRebarApply() {
  return useMutation({
    mutationFn: ({
      beam,
      config,
    }: {
      beam: BeamDimensions;
      config: RebarConfig;
    }) => postRebarApply(beam, config),
  });
}
