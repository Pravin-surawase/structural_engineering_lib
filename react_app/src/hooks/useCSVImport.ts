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
    mutationFn: ({ file, format }: { file: File; format?: string }) =>
      importCSVFile(file, format),
    onMutate: () => {
      setImporting(true);
      setError(null);
    },
    onSuccess: (data) => {
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
        setBeams(beams as any); // Type cast for compatibility
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
    importFile: (file: File, format?: string) =>
      mutation.mutate({ file, format }),
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
    mutationFn: ({ text, format }: { text: string; format?: string }) =>
      importCSVText(text, format),
    onMutate: () => {
      setImporting(true);
      setError(null);
    },
    onSuccess: (data) => {
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
        setBeams(beams as any);
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
    importText: (text: string, format?: string) =>
      mutation.mutate({ text, format }),
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
