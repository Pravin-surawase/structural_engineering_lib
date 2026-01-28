/**
 * useGeometryAdvanced Hook
 *
 * Provides hooks for building-level and cross-section geometry.
 *
 * Uses the /api/v1/geometry/* endpoints which wrap
 * structural_lib.visualization.geometry_3d functions.
 */
import { useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export interface BuildingBeamInput {
  beam_id: string;
  story: string;
  point1: Point3D;
  point2: Point3D;
  width_mm: number;
  depth_mm: number;
  is_valid?: boolean;
  utilization?: number;
}

export interface BuildingBeamResult {
  beam_id: string;
  start: [number, number, number];
  end: [number, number, number];
  width_m: number;
  depth_m: number;
  status: string;
}

export interface BuildingGeometryResponse {
  success: boolean;
  message: string;
  beam_count: number;
  beams: BuildingBeamResult[];
  bounding_box: {
    min_x: number;
    max_x: number;
    min_y: number;
    max_y: number;
    min_z: number;
    max_z: number;
  };
  center: [number, number, number];
  suggested_camera_distance: number;
}

export interface CrossSectionRequest {
  width_mm: number;
  depth_mm: number;
  cover_mm?: number;
  top_bars?: number;
  top_dia_mm?: number;
  bottom_bars?: number;
  bottom_dia_mm?: number;
  stirrup_dia_mm?: number;
  layers?: number;
}

export interface BarPosition {
  center: [number, number];
  radius: number;
  is_top: boolean;
  layer: number;
}

export interface CrossSectionResponse {
  success: boolean;
  message: string;
  outline: {
    width_mm: number;
    depth_mm: number;
    corners: [[number, number], [number, number], [number, number], [number, number]];
  };
  bars: BarPosition[];
  stirrup: {
    outer_corners: [[number, number], [number, number], [number, number], [number, number]];
    diameter_mm: number;
  };
  neutral_axis_mm?: number;
  compression_zone_mm?: number;
}

// =============================================================================
// Building Geometry Hook
// =============================================================================

interface BuildingGeometryRequest {
  beams: BuildingBeamInput[];
  lod?: "low" | "medium" | "high" | "auto";
  floor_height_m?: number;
}

async function fetchBuildingGeometry(
  request: BuildingGeometryRequest
): Promise<BuildingGeometryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/building`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Building geometry generation failed");
  }

  return response.json();
}

/**
 * Hook for generating building-level 3D geometry.
 *
 * @example
 * const { mutate, data, isPending } = useBuildingGeometry();
 * mutate({ beams: importedBeams });
 */
export function useBuildingGeometry() {
  return useMutation({
    mutationFn: fetchBuildingGeometry,
    mutationKey: ["building-geometry"],
  });
}

// =============================================================================
// Cross-Section Geometry Hook
// =============================================================================

async function fetchCrossSectionGeometry(
  request: CrossSectionRequest
): Promise<CrossSectionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/cross-section`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Cross-section generation failed");
  }

  return response.json();
}

/**
 * Hook for generating cross-section geometry for 2D visualization.
 *
 * @example
 * const { mutate, data, isPending } = useCrossSectionGeometry();
 * mutate({ width_mm: 300, depth_mm: 500, bottom_bars: 4, bottom_dia_mm: 16 });
 */
export function useCrossSectionGeometry() {
  return useMutation({
    mutationFn: fetchCrossSectionGeometry,
    mutationKey: ["cross-section-geometry"],
  });
}
