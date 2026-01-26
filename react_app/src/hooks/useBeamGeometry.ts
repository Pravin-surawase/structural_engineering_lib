/**
 * useBeamGeometry Hook
 *
 * Fetches full 3D geometry from the library via API.
 * Uses the new /geometry/beam/full endpoint which returns
 * accurate rebar positions and stirrup paths from the library's
 * geometry_3d.beam_to_3d_geometry() function.
 */
import { useQuery } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export interface RebarSegment {
  start: Point3D;
  end: Point3D;
  diameter: number;
  type: string;
  length: number;
}

export interface RebarPath {
  barId: string;
  segments: RebarSegment[];
  diameter: number;
  barType: "bottom" | "top" | "side" | "bent_up";
  zone: "start" | "mid" | "end" | "full";
  totalLength: number;
}

export interface StirrupLoop {
  positionX: number;
  path: Point3D[];
  diameter: number;
  legs: number;
  hookType: "90" | "135";
  perimeter: number;
}

export interface Beam3DGeometry {
  beamId: string;
  story: string;
  dimensions: {
    b: number;
    D: number;
    span: number;
  };
  concreteOutline: Point3D[];
  rebars: RebarPath[];
  stirrups: StirrupLoop[];
  metadata: {
    cover: number;
    ldTension: number;
    ldCompression: number;
    lapLength: number;
    isSeismic: boolean;
    isValid: boolean;
    remarks: string[];
  };
  version: string;
}

export interface BeamGeometryRequest {
  beam_id?: string;
  story?: string;
  width: number;
  depth: number;
  span: number;
  fck?: number;
  fy?: number;
  ast_start?: number;
  ast_mid?: number;
  ast_end?: number;
  stirrup_dia?: number;
  stirrup_spacing_start?: number;
  stirrup_spacing_mid?: number;
  stirrup_spacing_end?: number;
  cover?: number;
  is_seismic?: boolean;
}

interface GeometryResponse {
  success: boolean;
  message: string;
  geometry: Beam3DGeometry | null;
  warnings: string[];
}

/**
 * Fetch full 3D geometry from the API.
 *
 * This uses the library's geometry_3d module to compute
 * accurate bar positions based on IS 456 detailing rules.
 */
async function fetchBeamGeometry(
  params: BeamGeometryRequest
): Promise<Beam3DGeometry> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/beam/full`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Geometry failed: ${error.detail || response.status}`);
  }

  const data: GeometryResponse = await response.json();

  if (!data.success || !data.geometry) {
    throw new Error(data.message || "Failed to generate geometry");
  }

  return data.geometry;
}

/**
 * useBeamGeometry - React Query hook for fetching 3D beam geometry.
 *
 * Replaces manual bar position calculations in Viewport3D.tsx.
 * The library computes accurate positions based on:
 * - Bar count and diameter
 * - Clear cover requirements
 * - Spacing per IS 456 Cl 26.3.2
 * - Layer distribution for multi-layer bars
 *
 * @example
 * ```tsx
 * const { data: geometry, isLoading } = useBeamGeometry({
 *   width: 300,
 *   depth: 450,
 *   span: 4000,
 *   ast_start: 500,
 *   ast_mid: 400,
 *   ast_end: 500,
 * });
 *
 * // Use geometry.rebars and geometry.stirrups for rendering
 * ```
 */
export function useBeamGeometry(
  params: BeamGeometryRequest | null,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: ["beamGeometry", params],
    queryFn: () => fetchBeamGeometry(params!),
    enabled: Boolean(params) && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 5, // 5 minutes - geometry doesn't change
    gcTime: 1000 * 60 * 30, // Keep in cache for 30 minutes
  });
}

export default useBeamGeometry;
