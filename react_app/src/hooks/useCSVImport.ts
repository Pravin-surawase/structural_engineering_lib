/**
 * useCSVImport Hook
 *
 * Handles CSV file and text import using the library's adapter system.
 * Uses the new /import/csv and /import/csv/text endpoints which
 * leverage GenericCSVAdapter, ETABSAdapter, SAFEAdapter, etc.
 *
 * This replaces the duplicate parseBeamCSV() function in types/csv.ts
 * with proper library-backed parsing that handles:
 * - 40+ column name variations (case-insensitive)
 * - Unit conversions (m→mm, kN-m→kN·m)
 * - Intelligent column mapping
 */
import { useMutation } from "@tanstack/react-query";
import { useImportedBeamsStore } from "../store/importedBeamsStore";
import { applyMaterialOverrides, type MaterialOverrides } from "../utils/materialOverrides";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ImportedBeam {
  beam_id: string;
  story: string;
  width_mm: number;
  depth_mm: number;
  span_mm: number;
  fck_mpa: number;
  fy_mpa: number;
  moment_start_knm?: number;
  moment_mid_knm?: number;
  moment_end_knm?: number;
  shear_start_kn?: number;
  shear_end_kn?: number;
  cover_mm: number;
  unit_source?: string;
}

export interface DesignedBeam extends ImportedBeam {
  design?: {
    ast_required?: number;
    ast_provided?: number;
    bar_count?: number;
    bar_diameter?: number;
    stirrup_diameter?: number;
    stirrup_spacing?: number;
    is_valid?: boolean;
    utilization?: number;
    remarks?: string[];
  };
}

interface CSVImportResponse {
  success: boolean;
  message: string;
  beam_count: number;
  beams: ImportedBeam[];
  column_mapping: Record<string, string>;
  warnings: string[];
}

interface DualCSVImportResponse {
  success: boolean;
  message: string;
  beam_count: number;
  beams: Array<ImportedBeam & { point1?: { x: number; y: number; z: number }; point2?: { x: number; y: number; z: number } }>;
  format_detected: string;
  warnings: string[];
  unmatched_beams: string[];
  unmatched_forces: string[];
}

interface BatchDesignResponse {
  success: boolean;
  message: string;
  total: number;
  successful: number;
  failed: number;
  results: DesignedBeam[];
  warnings: string[];
}

/**
 * Import CSV from file upload.
 */
async function importCSVFile(
  file: File,
  format: string = "auto"
): Promise<CSVImportResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("format", format);

  const response = await fetch(`${API_BASE_URL}/api/v1/import/csv`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Import failed: ${error.detail || response.status}`);
  }

  return response.json();
}

/**
 * Import CSV from text (clipboard paste).
 */
async function importCSVText(
  text: string,
  format: string = "auto"
): Promise<CSVImportResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/import/csv/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, format }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Import failed: ${error.detail || response.status}`);
  }

  return response.json();
}

/**
 * Import dual CSV files (geometry + forces).
 */
async function importDualCSVFiles(
  geometryFile: File,
  forcesFile: File,
  format: string = "auto"
): Promise<DualCSVImportResponse> {
  const formData = new FormData();
  formData.append("geometry_file", geometryFile);
  formData.append("forces_file", forcesFile);
  const url = new URL(`${API_BASE_URL}/api/v1/import/dual-csv`);
  if (format) {
    url.searchParams.set("format_hint", format);
  }

  const response = await fetch(url.toString(), {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Dual CSV import failed: ${error.detail || response.status}`);
  }

  return response.json();
}

/**
 * Batch design all imported beams.
 */
async function batchDesign(
  beams: ImportedBeam[]
): Promise<BatchDesignResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/import/batch-design`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ beams }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Batch design failed: ${error.detail || response.status}`);
  }

  return response.json();
}

/**
 * useCSVImport - Hook for importing CSV files.
 *
 * Uses the library's adapter system which supports:
 * - Generic CSV (40+ column mappings)
 * - ETABS column export format
 * - SAFE beam schedule format
 * - STAAD Pro output format
 *
 * @example
 * ```tsx
 * const { importFile, isImporting } = useCSVFileImport();
 *
 * const handleDrop = (file: File) => {
 *   importFile(file);
 * };
 * ```
 */
export function useCSVFileImport() {
  const { setBeams, setImporting, setError } = useImportedBeamsStore();

  const mutation = useMutation({
    mutationFn: ({ file, format }: { file: File; format?: string; overrides?: MaterialOverrides }) =>
      importCSVFile(file, format),
    onMutate: () => {
      setImporting(true);
      setError(null);
    },
    onSuccess: (data, variables) => {
      setImporting(false);
      if (data.success) {
        // Convert to store format
        const beams = data.beams.map((b) => ({
          id: b.beam_id,
          story: b.story,
          b: b.width_mm,
          D: b.depth_mm,
          span: b.span_mm,
          fck: b.fck_mpa,
          fy: b.fy_mpa,
          Mu_start: b.moment_start_knm,
          Mu_mid: b.moment_mid_knm,
          Mu_end: b.moment_end_knm,
          Vu_start: b.shear_start_kn,
          Vu_end: b.shear_end_kn,
          cover: b.cover_mm,
        }));
        const overrideBeams = applyMaterialOverrides(beams, variables?.overrides);
        setBeams(overrideBeams as any); // Type cast for compatibility
      } else {
        setError(data.message);
      }
    },
    onError: (error: Error) => {
      setImporting(false);
      setError(error.message);
    },
  });

  return {
    importFile: (file: File, format?: string, overrides?: MaterialOverrides) =>
      mutation.mutate({ file, format, overrides }),
    isImporting: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  };
}

/**
 * useCSVTextImport - Hook for importing CSV from text/clipboard.
 *
 * @example
 * ```tsx
 * const { importText } = useCSVTextImport();
 *
 * const handlePaste = (text: string) => {
 *   importText(text);
 * };
 * ```
 */
export function useCSVTextImport() {
  const { setBeams, setImporting, setError } = useImportedBeamsStore();

  const mutation = useMutation({
    mutationFn: ({ text, format }: { text: string; format?: string; overrides?: MaterialOverrides }) =>
      importCSVText(text, format),
    onMutate: () => {
      setImporting(true);
      setError(null);
    },
    onSuccess: (data, variables) => {
      setImporting(false);
      if (data.success) {
        const beams = data.beams.map((b) => ({
          id: b.beam_id,
          story: b.story,
          b: b.width_mm,
          D: b.depth_mm,
          span: b.span_mm,
          fck: b.fck_mpa,
          fy: b.fy_mpa,
          Mu_start: b.moment_start_knm,
          Mu_mid: b.moment_mid_knm,
          Mu_end: b.moment_end_knm,
          Vu_start: b.shear_start_kn,
          Vu_end: b.shear_end_kn,
          cover: b.cover_mm,
        }));
        const overrideBeams = applyMaterialOverrides(beams, variables?.overrides);
        setBeams(overrideBeams as any);
      } else {
        setError(data.message);
      }
    },
    onError: (error: Error) => {
      setImporting(false);
      setError(error.message);
    },
  });

  return {
    importText: (text: string, format?: string, overrides?: MaterialOverrides) =>
      mutation.mutate({ text, format, overrides }),
    isImporting: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  };
}

/**
 * useDualCSVImport - Hook for dual CSV (geometry + forces) import.
 */
export function useDualCSVImport() {
  const { setBeams, setImporting, setError } = useImportedBeamsStore();

  const mutation = useMutation({
    mutationFn: ({
      geometryFile,
      forcesFile,
      format,
    }: {
      geometryFile: File;
      forcesFile: File;
      format?: string;
      overrides?: MaterialOverrides;
    }) => importDualCSVFiles(geometryFile, forcesFile, format),
    onMutate: () => {
      setImporting(true);
      setError(null);
    },
    onSuccess: (data, variables) => {
      setImporting(false);
      if (data.success) {
        const beams = data.beams.map((b) => ({
          id: b.beam_id,
          story: b.story,
          b: b.width_mm,
          D: b.depth_mm,
          span: b.span_mm,
          fck: b.fck_mpa,
          fy: b.fy_mpa,
          Mu_mid: b.moment_mid_knm ?? b.moment_start_knm ?? b.moment_end_knm ?? 0,
          Vu_start: b.shear_start_kn ?? b.shear_end_kn ?? 0,
          Vu_end: b.shear_end_kn ?? b.shear_start_kn ?? 0,
          cover: b.cover_mm,
          point1: b.point1,
          point2: b.point2,
        }));
        const overrideBeams = applyMaterialOverrides(beams, variables?.overrides);
        setBeams(overrideBeams as any);
      } else {
        setError(data.message);
      }
    },
    onError: (error: Error) => {
      setImporting(false);
      setError(error.message);
    },
  });

  return {
    importFiles: (
      geometryFile: File,
      forcesFile: File,
      format?: string,
      overrides?: MaterialOverrides
    ) => mutation.mutate({ geometryFile, forcesFile, format, overrides }),
    isImporting: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  };
}

/**
 * useBatchDesign - Hook for running design on all imported beams.
 *
 * @example
 * ```tsx
 * const { runBatchDesign } = useBatchDesign();
 *
 * const handleDesignAll = () => {
 *   runBatchDesign(beams);
 * };
 * ```
 */
export function useBatchDesign() {
  const mutation = useMutation({
    mutationFn: batchDesign,
  });

  return {
    runBatchDesign: mutation.mutate,
    isDesigning: mutation.isPending,
    error: mutation.error,
    results: mutation.data,
    reset: mutation.reset,
  };
}

export default useCSVFileImport;
