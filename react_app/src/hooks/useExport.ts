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

export interface WorkbenchExportParams {
  checked_request: { identity: { member_id: string } } & Record<string, unknown>;
  checked_layout_id: string;
  format?: "html" | "json";
}

/**
 * Current Quick Beam inputs promoted through the checked workbench path before
 * an engineering artifact is emitted.  This is deliberately not a second cage
 * selector: the production workbench owns the physical layout selection and
 * validates that layout against these exact concurrent actions.
 */
export interface QuickBeamCheckedExportParams {
  source: "quick-beam";
  beam_id?: string;
  width: number;
  depth: number;
  span_length: number;
  clear_cover: number;
  fck: number;
  fy: number;
  moment: number;
  shear: number;
  stirrup_dia_mm: number;
  main_bar_dia_mm: number;
  effective_depth?: number;
  format?: "html" | "json";
}

function exportMemberId(params: ExportBeamParams | ExportReportParams | WorkbenchExportParams | QuickBeamCheckedExportParams): string {
  return "checked_request" in params
    ? params.checked_request.identity.member_id
    : params.beam_id || "BEAM-1";
}

export interface ExportBeamParams {
  beam_id?: string;
  width: number;
  depth: number;
  span_length: number;
  clear_cover?: number;
  fck: number;
  fy: number;
  ast_required: number;
  asc_required?: number;
  moment?: number;
  shear?: number;
  torsion?: number;
  include_serviceability?: boolean;
}

export interface ExportReportParams {
  beam_id?: string;
  width: number;
  depth: number;
  fck: number;
  fy: number;
  moment?: number;
  shear?: number;
  torsion?: number;
  ast_required?: number;
  ast_provided?: number;
  utilization?: number;
  is_safe?: boolean;
  effective_depth?: number;
  clear_cover?: number;
  stirrup_dia_mm?: number;
  main_bar_dia_mm?: number;
  include_serviceability?: boolean;
  span_mm?: number;
  support_condition?: string;
  crack_width_params?: import('../api/client').BeamDesignRequest['crack_width_params'];
  calculation_identity?: string;
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
  body: ExportBeamParams | ExportReportParams | BuildingExportParams | WorkbenchExportParams,
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

type CheckedWorkbenchResponse = {
  status: "PASS" | "HOLD";
  reason?: string;
  checked_request?: WorkbenchExportParams["checked_request"];
  checked_layout_id?: string;
};

async function checkedQuickBeamExportParams(
  params: QuickBeamCheckedExportParams,
): Promise<WorkbenchExportParams> {
  const memberId = params.beam_id || "quick-beam";
  const depth = params.effective_depth === undefined
    ? {
        effective_depth_basis: {
          clear_cover_mm: params.clear_cover,
          stirrup_diameter_mm: params.stirrup_dia_mm,
          tension_bar_diameter_mm: params.main_bar_dia_mm,
        },
      }
    : { d_mm: params.effective_depth };
  const response = await fetch(`${API_BASE_URL}/stream/batch-design`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify([{
      schema_version: "project-beam-design/v1",
      member_id: memberId,
      b_mm: params.width,
      D_mm: params.depth,
      mu_knm: params.moment,
      vu_kn: params.shear,
      fck_nmm2: params.fck,
      fy_nmm2: params.fy,
      ...depth,
      source_metadata: {
        span_mm: params.span_length,
        workbench_detailing: {
          clear_cover_mm: params.clear_cover,
          stirrup_diameter_mm: params.stirrup_dia_mm,
          tension_bar_diameter_mm: params.main_bar_dia_mm,
          story: "Quick Beam",
        },
      },
    }]),
  });
  if (!response.ok) {
    throw new Error(`Checked export preparation failed: ${response.statusText}`);
  }
  const body = await response.text();
  const event = body.split(/\r?\n\r?\n/).find((block) =>
    block.split(/\r?\n/).includes("event: design_result"),
  );
  if (!event) {
    throw new Error("Checked export preparation returned no workbench result.");
  }
  const data = event.split(/\r?\n/)
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trimStart())
    .join("\n");
  const payload = JSON.parse(data) as { workbench?: CheckedWorkbenchResponse };
  const workbench = payload.workbench;
  if (
    workbench?.status !== "PASS"
    || !workbench.checked_request
    || !workbench.checked_layout_id
  ) {
    throw new Error(`CHECKED_EXPORT_HOLD: ${workbench?.reason || "the current Quick Beam inputs cannot produce a checked physical layout."}`);
  }
  return {
    checked_request: workbench.checked_request,
    checked_layout_id: workbench.checked_layout_id,
    format: params.format,
  };
}

function showExportError(error: Error) {
  toast.error("Export Failed", error.message);
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * Download a Bar Bending Schedule CSV.
 *
 * @example
 * const { mutate, isPending } = useExportBBS();
 * mutate({ width: 300, depth: 450, span_length: 5000, fck: 25, fy: 500, ast_required: 500 });
 */
export function useExportBBS() {
  return useMutation({
    mutationFn: async (params: ExportBeamParams | WorkbenchExportParams | QuickBeamCheckedExportParams) => {
      const checked = "source" in params && params.source === "quick-beam"
        ? await checkedQuickBeamExportParams(params)
        : params;
      return fetchExport("bbs", checked, `BBS_${exportMemberId(checked)}.csv`);
    },
    mutationKey: ["export-bbs"],
    onSuccess: (filename) => {
      toast.success("Export Complete", `${filename} downloaded successfully`);
    },
    onError: showExportError,
  });
}

/**
 * Download a DXF drawing.
 *
 * @example
 * const { mutate, isPending } = useExportDXF();
 * mutate({ width: 300, depth: 450, span_length: 5000, fck: 25, fy: 500, ast_required: 500 });
 */
export function useExportDXF() {
  return useMutation({
    mutationFn: async (params: ExportBeamParams | WorkbenchExportParams | QuickBeamCheckedExportParams) => {
      const checked = "source" in params && params.source === "quick-beam"
        ? await checkedQuickBeamExportParams(params)
        : params;
      return fetchExport("dxf", checked, `${exportMemberId(checked)}.dxf`);
    },
    mutationKey: ["export-dxf"],
    onError: showExportError,
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
    mutationFn: async (params: ExportReportParams | WorkbenchExportParams | QuickBeamCheckedExportParams) => {
      const checked = "source" in params && params.source === "quick-beam"
        ? await checkedQuickBeamExportParams(params)
        : params;
      const fmt = checked.format || "html";
      const ext = fmt === "pdf" ? "pdf" : fmt === "html" ? "html" : "json";
      return fetchExport("report", checked, `Report_${exportMemberId(checked)}.${ext}`);
    },
    mutationKey: ["export-report"],
    onError: showExportError,
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

export type BuildingExportParams = {
  project_name?: string;
  format?: "html" | "pdf" | "csv";
} & ({ beams: BatchBeamRow[] } | { checked_beams: WorkbenchExportParams[] });

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
    onError: (error: Error) => toast.error("Export Failed", error.message),
  });
}
