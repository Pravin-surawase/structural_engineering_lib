/**
 * useCrossSectionGeometry Hook
 *
 * Fetches 2D cross-section geometry from the library via API.
 * Uses the /geometry/cross-section endpoint for editor views.
 */
import { useQuery, useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export interface RebarPosition {
  y: number;
  z: number;
  diameter: number;
  layer: number;
}

export interface StirrupVertex {
  y: number;
  z: number;
}

export interface CrossSectionGeometry {
  width: number;
  depth: number;
  cover: number;
  rebars: RebarPosition[];
  stirrupPath: StirrupVertex[];
}

export interface CrossSectionRequest {
  width: number;
  depth: number;
  cover?: number;
  bottomBars?: Array<[number, number]>;  // [(count, diameter), ...]
  topBars?: Array<[number, number]>;
  stirrupDia?: number;
}

interface CrossSectionResponse {
  success: boolean;
  width: number;
  depth: number;
  cover: number;
  rebars: Array<{ y: number; z: number; diameter: number }>;
  stirrup_path: Array<{ y: number; z: number }>;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Fetch 2D cross-section geometry from the API.
 */
async function fetchCrossSectionGeometry(
  request: CrossSectionRequest
): Promise<CrossSectionGeometry> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/cross-section`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      width: request.width,
      depth: request.depth,
      cover: request.cover || 40,
      bottom_bars: request.bottomBars || [],
      top_bars: request.topBars || [],
      stirrup_dia: request.stirrupDia || 8,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Cross-section generation failed: ${error.detail || response.status}`);
  }

  const data: CrossSectionResponse = await response.json();

  return {
    width: data.width,
    depth: data.depth,
    cover: data.cover,
    rebars: data.rebars.map((r, i) => ({ ...r, layer: Math.floor(i / 4) })),
    stirrupPath: data.stirrup_path,
  };
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * useCrossSectionGeometry - React Query hook for 2D cross-section.
 *
 * Used for rebar editor overlay and cross-section views.
 * The library computes bar positions following IS 456 spacing rules.
 *
 * @example
 * ```tsx
 * const { data: section } = useCrossSectionGeometry({
 *   width: 300,
 *   depth: 450,
 *   bottomBars: [[3, 16], [2, 12]], // 3x16mm + 2x12mm
 *   topBars: [[2, 12]],
 * });
 *
 * // Draw section.rebars as circles on canvas
 * // Draw section.stirrupPath as closed polygon
 * ```
 */
export function useCrossSectionGeometry(
  request: CrossSectionRequest | null,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: ["crossSectionGeometry", request],
    queryFn: () => fetchCrossSectionGeometry(request!),
    enabled: Boolean(request?.width && request?.depth) && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes
  });
}

/**
 * useCrossSectionMutation - Mutation hook for on-demand generation.
 *
 * Use in editor when user changes bar configuration.
 */
export function useCrossSectionMutation() {
  return useMutation({
    mutationFn: fetchCrossSectionGeometry,
  });
}

export default useCrossSectionGeometry;
