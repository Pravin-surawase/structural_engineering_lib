/**
 * useBuildingGeometry Hook
 *
 * Fetches building-level 3D geometry from the library via API.
 * Uses the new /geometry/building endpoint which returns
 * instancing-ready geometry for React Three Fiber.
 */
import { useQuery, useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export interface BeamInstance {
  beamId: string;
  story: string;
  position: [number, number, number];
  rotation: [number, number, number];
  dimensions: [number, number, number]; // width, depth, span
  status: "pass" | "fail" | "warning" | "pending";
  utilizationRatio: number;
  color: [number, number, number, number]; // RGBA
}

export interface Building3DGeometry {
  beamCount: number;
  storyCount: number;
  bounds: {
    min: [number, number, number];
    max: [number, number, number];
  };
  cameraTarget: {
    x: number;
    y: number;
    z: number;
  };
  beams: BeamInstance[];
  metadata: {
    lod: string;
    generatedAt: string;
  };
}

export interface BuildingGeometryRequest {
  beams: Array<{
    id: string;
    story: string;
    width?: number;
    depth?: number;
    span?: number;
    startX?: number;
    startY?: number;
    endX?: number;
    endY?: number;
  }>;
  designResults?: Array<{
    beam_id: string;
    utilization_ratio?: number;
    pass?: boolean;
    warnings?: string[];
  }>;
  lod?: "low" | "medium" | "high";
  storyHeight?: number;
}

interface BuildingGeometryResponse {
  success: boolean;
  message: string;
  beam_count: number;
  story_count: number;
  bounds: {
    min: [number, number, number];
    max: [number, number, number];
  };
  camera_target: {
    x: number;
    y: number;
    z: number;
  };
  beams: BeamInstance[];
  metadata: Record<string, unknown>;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Fetch building 3D geometry from the API.
 *
 * This uses the library's building_to_3d_geometry() function
 * to compute instancing-ready geometry for React Three Fiber.
 */
async function fetchBuildingGeometry(
  request: BuildingGeometryRequest
): Promise<Building3DGeometry> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/building`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      beams: request.beams,
      design_results: request.designResults,
      lod: request.lod || "medium",
      story_height: request.storyHeight || 3000,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Building geometry failed: ${error.detail || response.status}`);
  }

  const data: BuildingGeometryResponse = await response.json();

  if (!data.success) {
    throw new Error(data.message || "Failed to generate building geometry");
  }

  return {
    beamCount: data.beam_count,
    storyCount: data.story_count,
    bounds: data.bounds,
    cameraTarget: data.camera_target,
    beams: data.beams,
    metadata: {
      lod: (data.metadata.lod as string) || "medium",
      generatedAt: (data.metadata.generatedAt as string) || new Date().toISOString(),
    },
  };
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * useBuildingGeometry - React Query hook for fetching building 3D geometry.
 *
 * Used for multi-beam 3D viewer with GPU instancing.
 * The library computes positions, rotations, and status colors.
 *
 * @example
 * ```tsx
 * const { data: building, isLoading } = useBuildingGeometry({
 *   beams: csvData.beams,
 *   designResults: results,
 *   lod: "medium",
 * });
 *
 * // Use building.beams for InstancedMesh
 * // Use building.cameraTarget for OrbitControls target
 * ```
 */
export function useBuildingGeometry(
  request: BuildingGeometryRequest | null,
  options?: { enabled?: boolean; refetchOnDesignChange?: boolean }
) {
  return useQuery({
    queryKey: ["buildingGeometry", request],
    queryFn: () => fetchBuildingGeometry(request!),
    enabled: Boolean(request?.beams?.length) && (options?.enabled ?? true),
    staleTime: options?.refetchOnDesignChange ? 0 : 1000 * 60, // 1 minute
    gcTime: 1000 * 60 * 15, // Keep in cache for 15 minutes
  });
}

/**
 * useBuildingGeometryMutation - Mutation hook for on-demand geometry.
 *
 * Use when you need manual control over when to fetch geometry.
 *
 * @example
 * ```tsx
 * const mutation = useBuildingGeometryMutation();
 *
 * const handleGenerateView = async () => {
 *   const geometry = await mutation.mutateAsync({
 *     beams: selectedBeams,
 *     lod: "high",
 *   });
 *   setViewerData(geometry);
 * };
 * ```
 */
export function useBuildingGeometryMutation() {
  return useMutation({
    mutationFn: fetchBuildingGeometry,
  });
}

export default useBuildingGeometry;
