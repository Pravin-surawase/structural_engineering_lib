/**
 * useExport Hook
 *
 * Provides hooks for downloading BBS (CSV), DXF, and Report (HTML/JSON)
 * from the /api/v1/export/* endpoints.
 */
import { useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

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
  format?: "html" | "json";
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
  body: ExportBeamParams | ExportReportParams,
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
      const ext = fmt === "html" ? "html" : "json";
      return fetchExport("report", params, `Report_${params.beam_id || "BEAM-1"}.${ext}`);
    },
    mutationKey: ["export-report"],
  });
}
