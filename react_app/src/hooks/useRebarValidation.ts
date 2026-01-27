/**
 * useRebarValidation Hook
 *
 * Validates and applies rebar configurations via the API.
 * Uses /api/v1/geometry/rebar/validate and /api/v1/geometry/rebar/apply endpoints.
 *
 * These endpoints wrap structural_lib.rebar module functions:
 * - validate_rebar_config(): Check bar count, spacing per IS 456
 * - apply_rebar_config(): Validate + generate geometry preview
 */
import { useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export interface BeamParams {
  /** Beam width b (mm) */
  b_mm?: number;
  width?: number;
  /** Beam depth D (mm) */
  D_mm?: number;
  depth?: number;
  /** Clear cover (mm) */
  cover_mm?: number;
  cover?: number;
  /** Span (mm) */
  span_mm?: number;
  span?: number;
}

export interface RebarConfig {
  /** Number of bars */
  bar_count: number;
  /** Bar diameter (mm) */
  bar_dia_mm: number;
  /** Stirrup diameter (mm) */
  stirrup_dia_mm?: number;
  /** Number of layers */
  layers?: number;
  /** True for top bars */
  is_top?: boolean;
  /** Stirrup spacings (mm) */
  stirrup_spacing_start?: number;
  stirrup_spacing_mid?: number;
  stirrup_spacing_end?: number;
  /** Aggregate size for spacing check */
  agg_size_mm?: number;
}

export interface ValidationResult {
  success: boolean;
  ok: boolean;
  errors: string[];
  warnings: string[];
  details: {
    b_mm?: number;
    D_mm?: number;
    cover_mm?: number;
    stirrup_dia_mm?: number;
    bar_count?: number;
    bar_dia_mm?: number;
    layers?: number;
    spacing_mm?: number | null;
  };
}

export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export interface RebarSegment {
  start: Point3D;
  end: Point3D;
  diameter: number;
}

export interface RebarPath {
  barId: string;
  segments: RebarSegment[];
  diameter: number;
  barType: string;
}

export interface StirrupLoop {
  positionX: number;
  path: Point3D[];
  diameter: number;
  legs: number;
  hookType: string;
}

export interface ApplyResult {
  success: boolean;
  message: string;
  ast_provided_mm2: number | null;
  validation: ValidationResult["details"];
  geometry: {
    rebars: RebarPath[];
    stirrups: StirrupLoop[];
    metadata: Record<string, unknown>;
  } | null;
}

interface RebarRequest {
  beam: BeamParams;
  config: RebarConfig;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Validate a rebar configuration without applying.
 */
async function validateRebarConfig(
  request: RebarRequest
): Promise<ValidationResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/rebar/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Validation failed: ${error.detail || response.status}`);
  }

  return response.json();
}

/**
 * Apply a rebar configuration and get geometry preview.
 */
async function applyRebarConfig(
  request: RebarRequest
): Promise<ApplyResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/rebar/apply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Apply failed: ${error.detail || response.status}`);
  }

  return response.json();
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * useRebarValidation - Mutation hook for validating rebar config.
 *
 * Use for real-time validation as user edits bar count/diameter.
 *
 * @example
 * ```tsx
 * const { mutate: validate, data: result, isLoading } = useRebarValidation();
 *
 * // Validate on change
 * validate({
 *   beam: { b_mm: 300, D_mm: 450, cover_mm: 40 },
 *   config: { bar_count: 4, bar_dia_mm: 16 }
 * });
 *
 * // Show errors/warnings
 * if (result && !result.ok) {
 *   result.errors.forEach(err => console.error(err));
 * }
 * ```
 */
export function useRebarValidation() {
  return useMutation({
    mutationFn: validateRebarConfig,
  });
}

/**
 * useRebarApply - Mutation hook for applying rebar config.
 *
 * Validates first, then returns geometry for preview.
 *
 * @example
 * ```tsx
 * const { mutate: apply, data: result, isLoading } = useRebarApply();
 *
 * // Apply configuration
 * apply({
 *   beam: { b_mm: 300, D_mm: 450, cover_mm: 40, span_mm: 5000 },
 *   config: { bar_count: 4, bar_dia_mm: 16, stirrup_dia_mm: 8 }
 * });
 *
 * // Use result.geometry for 3D preview
 * if (result?.success && result.geometry) {
 *   console.log(`Ast provided: ${result.ast_provided_mm2} mm²`);
 * }
 * ```
 */
export function useRebarApply() {
  return useMutation({
    mutationFn: applyRebarConfig,
  });
}

export default useRebarValidation;
