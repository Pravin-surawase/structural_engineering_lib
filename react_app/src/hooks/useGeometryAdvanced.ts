/**
 * useGeometryAdvanced Hook
 *
 * Provides hooks for building-level and cross-section geometry.
 *
 * Uses the /api/v1/geometry/* endpoints which wrap
 * structural_lib.visualization.geometry_3d functions.
 */
import { useMutation } from "@tanstack/react-query";
import { unwrapResponse } from '../api/client';

import { API_BASE_URL } from '../config';

// =============================================================================
// Types
// =============================================================================

export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export interface BuildingBeamInput {
  id: string;
  label: string;
  story: string;
  frame_type: "beam" | "column" | "brace";
  point1: Point3D;
  point2: Point3D;
  section: {
    width_mm: number;
    depth_mm: number;
    fck_mpa: number;
    fy_mpa: number;
    cover_mm: number;
  };
}

export interface BuildingBeamResult {
  beam_id: string;
  story: string;
  frame_type: "beam" | "column" | "brace";
  start: Point3D;
  end: Point3D;
}

export interface BuildingGeometryResponse {
  success: boolean;
  message: string;
  beams: BuildingBeamResult[];
  bounding_box: {
    min_x: number;
    max_x: number;
    min_y: number;
    max_y: number;
    min_z: number;
    max_z: number;
  };
  center: Point3D;
  metadata: {
    contract_scope: "visualization_only";
    source_coordinate_basis: "source_units";
    output_coordinate_units: "mm";
    coordinate_scale_to_mm: number;
    input_member_count: number;
    output_member_count: number;
    filtered_member_count: number;
    [key: string]: unknown;
  };
  warnings: string[];
}

export interface CrossSectionRequest {
  width: number;
  depth: number;
  cover?: number;
  tension_bars?: number;
  compression_bars?: number;
  bar_dia?: number;
  stirrup_dia?: number;
}

export interface CrossSectionResponse {
  success: boolean;
  message: string;
  outline: Point3D[];
  tension_bars: Point3D[];
  compression_bars: Point3D[];
  stirrup_path: Point3D[];
  dimensions: {
    width_mm: number;
    depth_mm: number;
    cover_mm: number;
    bar_dia_mm: number;
    stirrup_dia_mm: number;
  };
  warnings: string[];
}

// =============================================================================
// Building Geometry Hook
// =============================================================================

interface BuildingGeometryRequest {
  beams: BuildingBeamInput[];
  unit_scale?: number;
  include_frame_types?: Array<"beam" | "column" | "brace">;
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

  return response.json().then(unwrapResponse<BuildingGeometryResponse>);
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

  return response.json().then(unwrapResponse<CrossSectionResponse>);
}

/**
 * Hook for generating cross-section geometry for 2D visualization.
 *
 * @example
 * const { mutate, data, isPending } = useCrossSectionGeometry();
 * mutate({ width: 300, depth: 500, tension_bars: 4, bar_dia: 16 });
 */
export function useCrossSectionGeometry() {
  return useMutation({
    mutationFn: fetchCrossSectionGeometry,
    mutationKey: ["cross-section-geometry"],
  });
}
