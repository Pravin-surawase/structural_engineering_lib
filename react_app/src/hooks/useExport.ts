/**
 * useExport Hook
 *
 * Provides hooks for downloading BBS (CSV), DXF, and Report (HTML/JSON)
 * from the /api/v1/export/* endpoints.
 */
import { useMutation } from "@tanstack/react-query";
import { toast } from "../components/ui/Toast";

import { API_BASE_URL } from '../config';

// =============================================================================
// Types
// =============================================================================

export interface ExportBeamParams {
  beam_id?: string;
  width: number;
  depth: number;
  span_length?: number;
  clear_cover?: number;
  fck: number;
  fy: number;
  ast_required: number;
  asc_required?: number;
  moment?: number;
  shear?: number;
}

export interface ExportReportParams {
  beam_id?: string;
  width: number;
  depth: number;
  fck: number;
  fy: number;
  moment?: number;
  shear?: number;
  ast_required?: number;
  ast_provided?: number;
  utilization?: number;
  is_safe?: boolean;
  format?: "html" | "json" | "pdf";
}

// =============================================================================
// Helpers
// =============================================================================

/** Trigger a browser file download from a Blob. */
function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function fetchExport(
  endpoint: string,
  body: ExportBeamParams | ExportReportParams | BuildingExportParams,
  filename: string
): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/v1/export/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Export failed: ${response.statusText}`);
  }

  const blob = await response.blob();
  downloadBlob(blob, filename);
  return filename;
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * Download a Bar Bending Schedule CSV.
 *
 * @example
 * const { mutate, isPending } = useExportBBS();
 * mutate({ width: 300, depth: 450, fck: 25, fy: 500, ast_required: 500 });
 */
export function useExportBBS() {
  return useMutation({
    mutationFn: (params: ExportBeamParams) =>
      fetchExport("bbs", params, `BBS_${params.beam_id || "BEAM-1"}.csv`),
    mutationKey: ["export-bbs"],
    onSuccess: (filename) => {
      toast.success("Export Complete", `${filename} downloaded successfully`);
    },
    onError: (error: Error) => {
      toast.error("Export Failed", error.message);
    },
  });
}

/**
 * Download a DXF drawing.
 *
 * @example
 * const { mutate, isPending } = useExportDXF();
 * mutate({ width: 300, depth: 450, fck: 25, fy: 500, ast_required: 500 });
 */
export function useExportDXF() {
  return useMutation({
    mutationFn: (params: ExportBeamParams) =>
      fetchExport("dxf", params, `${params.beam_id || "BEAM-1"}.dxf`),
    mutationKey: ["export-dxf"],
  });
}

/**
 * Download a design report (HTML or JSON).
 *
 * @example
 * const { mutate, isPending } = useExportReport();
 * mutate({ width: 300, depth: 450, fck: 25, fy: 500, format: "html" });
 */
export function useExportReport() {
  return useMutation({
    mutationFn: (params: ExportReportParams) => {
      const fmt = params.format || "html";
      const ext = fmt === "pdf" ? "pdf" : fmt === "html" ? "html" : "json";
      return fetchExport("report", params, `Report_${params.beam_id || "BEAM-1"}.${ext}`);
    },
    mutationKey: ["export-report"],
  });
}


// =============================================================================
// Building / Batch Export
// =============================================================================

export interface BatchBeamRow {
  beam_id: string;
  story?: string;
  width: number;
  depth: number;
  span_length?: number;
  fck?: number;
  fy?: number;
  moment?: number;
  shear?: number;
  ast_required?: number;
  ast_provided?: number;
  asc_required?: number;
  bar_count?: number;
  bar_diameter?: number;
  stirrup_diameter?: number;
  stirrup_spacing?: number;
  utilization?: number;
  is_safe?: boolean;
  status?: string;
}

export interface BuildingExportParams {
  project_name?: string;
  beams: BatchBeamRow[];
  format?: "html" | "pdf" | "csv";
}

/**
 * Download a building-level summary report (HTML, PDF, or CSV).
 */
export function useExportBuildingSummary() {
  return useMutation({
    mutationFn: (params: BuildingExportParams) => {
      const fmt = params.format || "html";
      const ext = fmt === "pdf" ? "pdf" : fmt === "csv" ? "csv" : "html";
      return fetchExport(
        "building-summary",
        params,
        `Building_Summary.${ext}`
      );
    },
    mutationKey: ["export-building-summary"],
  });
}
