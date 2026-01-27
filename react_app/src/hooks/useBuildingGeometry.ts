/**
 * useBuildingGeometry Hook
 *
 * Fetches building-level 3D geometry from the API.
 * Returns line segments for all beams suitable for wireframe rendering.
 *
 * Uses /api/v1/geometry/building endpoint which wraps
 * structural_lib.visualization.geometry_3d.building_to_3d_geometry()
 */
import { useQuery, useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export interface BuildingBeam {
  beamId: string;
  story: string;
  frameType: "beam" | "column" | "brace";
  start: Point3D;
  end: Point3D;
}

export interface BoundingBox {
  min_x: number;
  max_x: number;
  min_y: number;
  max_y: number;
  min_z: number;
  max_z: number;
}

export interface Building3DGeometry {
  beams: BuildingBeam[];
  boundingBox: BoundingBox;
  center: Point3D;
  metadata: {
    unitScale: number;
    beamCount: number;
  };
}

export interface BuildingGeometryRequest {
  /** List of beam dicts with id, story, point1, point2 */
  beams: Array<{
    id: string;
    story?: string;
    frame_type?: string;
    point1?: Point3D;
    point2?: Point3D;
  }>;
  /** Scale factor (default: 1000 converts m to mm) */
  unit_scale?: number;
  /** Filter by frame types */
  include_frame_types?: string[];
}

interface GeometryResponse {
  success: boolean;
  message: string;
  beams: BuildingBeam[];
  boundingBox: BoundingBox;
  center: Point3D;
  metadata: Record<string, unknown>;
  warnings: string[];
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Fetch building 3D geometry from the API.
 */
async function fetchBuildingGeometry(
  request: BuildingGeometryRequest
): Promise<Building3DGeometry> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/building`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Building geometry failed: ${error.detail || response.status}`);
  }

  const data: GeometryResponse = await response.json();

  if (!data.success) {
    throw new Error(data.message || "Failed to generate building geometry");
  }

  return {
    beams: data.beams,
    boundingBox: data.boundingBox,
    center: data.center,
    metadata: {
      unitScale: (data.metadata?.unitScale as number) ?? 1000,
      beamCount: data.beams.length,
    },
  };
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * useBuildingGeometry - React Query hook for fetching building 3D geometry.
 *
 * Converts imported beam data to line segments for 3D visualization.
 * Returns center and bounding box for camera framing.
 *
 * @example
 * ```tsx
 * const { data: buildingGeom, isLoading } = useBuildingGeometry(
 *   { beams: importedBeams, unit_scale: 1.0 },
 *   { enabled: importedBeams.length > 0 }
 * );
 *
 * // Use buildingGeom.beams for Line rendering
 * // Use buildingGeom.center for camera target
 * ```
 */
export function useBuildingGeometry(
  request: BuildingGeometryRequest | null,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: ["buildingGeometry", request],
    queryFn: () => fetchBuildingGeometry(request!),
    enabled: Boolean(request?.beams?.length) && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 5, // 5 minutes - geometry doesn't change
    gcTime: 1000 * 60 * 30, // Keep in cache for 30 minutes
  });
}

/**
 * useBuildingGeometryMutation - For on-demand geometry generation.
 *
 * Use when you need imperative control over when to fetch geometry.
 */
export function useBuildingGeometryMutation() {
  return useMutation({
    mutationFn: fetchBuildingGeometry,
  });
}

export default useBuildingGeometry;
