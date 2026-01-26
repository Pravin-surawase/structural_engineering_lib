/**
 * useRebarValidation Hook
 *
 * Validates rebar configuration against IS 456 requirements via API.
 * Uses the /geometry/rebar/validate endpoint.
 */
import { useQuery, useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export type WarningSeverity = "error" | "warning" | "info";

export interface RebarWarning {
  code: string;
  message: string;
  severity: WarningSeverity;
  clause?: string;
  suggestion?: string;
}

export interface RebarValidationResult {
  isValid: boolean;
  errors: RebarWarning[];
  warnings: RebarWarning[];
  computed: {
    astProvided: number;
    astRequired?: number;
    utilizationRatio?: number;
    clearSpacing: number;
    effectiveDepth: number;
    steelRatio: number;
  };
}

export interface RebarValidationRequest {
  beamWidth: number;
  beamDepth: number;
  cover?: number;
  bottomBars?: Array<[number, number]>;  // [(count, diameter), ...]
  topBars?: Array<[number, number]>;
  stirrupDia?: number;
  stirrupSpacing?: number;
  isSeismic?: boolean;
  astRequired?: number;  // Optional: to check against provided
}

interface RebarValidationResponse {
  success: boolean;
  is_valid: boolean;
  errors: Array<{
    code: string;
    message: string;
    severity: string;
    clause?: string;
    suggestion?: string;
  }>;
  warnings: Array<{
    code: string;
    message: string;
    severity: string;
    clause?: string;
    suggestion?: string;
  }>;
  computed: {
    ast_provided: number;
    ast_required?: number;
    utilization_ratio?: number;
    clear_spacing: number;
    effective_depth: number;
    steel_ratio: number;
  };
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Validate rebar configuration via API.
 */
async function validateRebarConfig(
  request: RebarValidationRequest
): Promise<RebarValidationResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/rebar/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      beam_width: request.beamWidth,
      beam_depth: request.beamDepth,
      cover: request.cover || 40,
      bottom_bars: request.bottomBars || [],
      top_bars: request.topBars || [],
      stirrup_dia: request.stirrupDia || 8,
      stirrup_spacing: request.stirrupSpacing || 150,
      is_seismic: request.isSeismic || false,
      ast_required: request.astRequired,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Rebar validation failed: ${error.detail || response.status}`);
  }

  const data: RebarValidationResponse = await response.json();

  return {
    isValid: data.is_valid,
    errors: data.errors.map(e => ({
      code: e.code,
      message: e.message,
      severity: e.severity as WarningSeverity,
      clause: e.clause,
      suggestion: e.suggestion,
    })),
    warnings: data.warnings.map(w => ({
      code: w.code,
      message: w.message,
      severity: w.severity as WarningSeverity,
      clause: w.clause,
      suggestion: w.suggestion,
    })),
    computed: {
      astProvided: data.computed.ast_provided,
      astRequired: data.computed.ast_required,
      utilizationRatio: data.computed.utilization_ratio,
      clearSpacing: data.computed.clear_spacing,
      effectiveDepth: data.computed.effective_depth,
      steelRatio: data.computed.steel_ratio,
    },
  };
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * useRebarValidation - React Query hook for rebar validation.
 *
 * Validates bar configuration against IS 456 / IS 13920 requirements.
 * Returns errors, warnings, and computed values.
 *
 * @example
 * ```tsx
 * const { data: validation } = useRebarValidation({
 *   beamWidth: 300,
 *   beamDepth: 450,
 *   bottomBars: [[3, 16], [2, 12]],
 *   topBars: [[2, 12]],
 *   astRequired: 520,
 * });
 *
 * if (!validation?.isValid) {
 *   showErrors(validation.errors);
 * }
 * ```
 */
export function useRebarValidation(
  request: RebarValidationRequest | null,
  options?: { enabled?: boolean; validateOnChange?: boolean }
) {
  return useQuery({
    queryKey: ["rebarValidation", request],
    queryFn: () => validateRebarConfig(request!),
    enabled: Boolean(request?.beamWidth && request?.beamDepth) && (options?.enabled ?? true),
    staleTime: options?.validateOnChange ? 0 : 1000 * 30, // 30 seconds
    gcTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * useRebarValidationMutation - Mutation hook for on-demand validation.
 *
 * Use in rebar editor for live validation as user changes bars.
 *
 * @example
 * ```tsx
 * const mutation = useRebarValidationMutation();
 *
 * const handleBarChange = async (newBars: BarConfig[]) => {
 *   const result = await mutation.mutateAsync({
 *     beamWidth: 300,
 *     beamDepth: 450,
 *     bottomBars: newBars,
 *   });
 *   setValidation(result);
 * };
 * ```
 */
export function useRebarValidationMutation() {
  return useMutation({
    mutationFn: validateRebarConfig,
  });
}

/**
 * Utility: Get severity color for UI display.
 */
export function getWarningColor(severity: WarningSeverity): string {
  switch (severity) {
    case "error":
      return "#ef4444"; // red-500
    case "warning":
      return "#f59e0b"; // amber-500
    case "info":
      return "#3b82f6"; // blue-500
    default:
      return "#6b7280"; // gray-500
  }
}

export default useRebarValidation;
