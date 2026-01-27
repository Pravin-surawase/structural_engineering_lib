/**
 * Building and cross-section geometry hooks.
 */
import { useMutation, useQuery } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export interface BuildingBeamInput {
  beam_id: string;
  story?: string;
  frame_type?: string;
  point1: Point3D;
  point2: Point3D;
  width_mm?: number;
  depth_mm?: number;
  fck_mpa?: number;
  fy_mpa?: number;
  cover_mm?: number;
}

export interface BuildingGeometryRequest {
  beams: BuildingBeamInput[];
  unit_scale?: number;
  include_frame_types?: string[];
}

export interface BuildingBeam {
  beamId: string;
  story: string;
  frameType: string;
  start: Point3D;
  end: Point3D;
}

export interface BuildingGeometry {
  beams: BuildingBeam[];
  boundingBox: Record<string, number>;
  center: Point3D;
  metadata: Record<string, unknown>;
  version: string;
}

interface BuildingGeometryResponse {
  success: boolean;
  message: string;
  geometry: BuildingGeometry | null;
  warnings: string[];
}

export interface CrossSectionRequest {
  width_mm: number;
  depth_mm: number;
  cover_mm?: number;
  bar_count: number;
  bar_dia_mm: number;
  stirrup_dia_mm?: number;
  layers?: number;
  is_top?: boolean;
}

export interface CrossSectionGeometry {
  width_mm: number;
  depth_mm: number;
  cover_mm: number;
  outline: Point3D[];
  stirrup: Point3D[];
  bars: Point3D[];
  metadata: Record<string, unknown>;
  version: string;
}

interface CrossSectionResponse {
  success: boolean;
  message: string;
  geometry: CrossSectionGeometry | null;
  warnings: string[];
}

async function fetchBuildingGeometry(
  params: BuildingGeometryRequest
): Promise<BuildingGeometry> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/building`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Building geometry failed: ${error.detail || response.status}`);
  }

  const data: BuildingGeometryResponse = await response.json();
  if (!data.success || !data.geometry) {
    throw new Error(data.message || "Failed to generate building geometry");
  }

  return data.geometry;
}

async function fetchCrossSectionGeometry(
  params: CrossSectionRequest
): Promise<CrossSectionGeometry> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/cross-section`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Cross-section failed: ${error.detail || response.status}`);
  }

  const data: CrossSectionResponse = await response.json();
  if (!data.success || !data.geometry) {
    throw new Error(data.message || "Failed to generate cross-section geometry");
  }

  return data.geometry;
}

export function useBuildingGeometry(
  params: BuildingGeometryRequest | null,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: ["buildingGeometry", params],
    queryFn: () => fetchBuildingGeometry(params!),
    enabled: Boolean(params) && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 30,
  });
}

export function useCrossSectionGeometry() {
  return useMutation({
    mutationFn: (params: CrossSectionRequest) => fetchCrossSectionGeometry(params),
  });
}
