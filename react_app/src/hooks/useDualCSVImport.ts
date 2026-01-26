/**
 * useDualCSVImport Hook
 *
 * Handles dual-CSV import (geometry + forces) via API.
 * Uses the library's csv_import module for parsing and merging.
 */
import { useState, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export type CSVFormat = "ram_concept" | "etabs" | "safe" | "auto";
export type WarningSeverity = "error" | "warning" | "info";

export interface ImportWarning {
  code: string;
  message: string;
  severity: WarningSeverity;
  rowIndex?: number;
  column?: string;
}

export interface BeamData {
  id: string;
  story: string;
  width: number;
  depth: number;
  span: number;
  fck: number;
  fy: number;
  Mu_start?: number;
  Mu_mid?: number;
  Mu_end?: number;
  Vu_start?: number;
  Vu_end?: number;
  Tu?: number;
  cover?: number;
}

export interface ImportResult {
  success: boolean;
  beams: BeamData[];
  beamCount: number;
  warnings: ImportWarning[];
  metadata: {
    geometryFormat: string;
    forcesFormat: string;
    mergedCount: number;
    unmatchedGeometry: string[];
    unmatchedForces: string[];
  };
}

export interface DualCSVImportRequest {
  geometryFile: File;
  forcesFile: File;
  format?: CSVFormat;
  defaultFck?: number;
  defaultFy?: number;
}

export interface DualImportState {
  status: "idle" | "uploading" | "parsing" | "merging" | "complete" | "error";
  progress: number;
  result: ImportResult | null;
  error: string | null;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Upload and parse dual CSV files via API.
 */
async function uploadDualCSV(
  request: DualCSVImportRequest
): Promise<ImportResult> {
  const formData = new FormData();
  formData.append("geometry_file", request.geometryFile);
  formData.append("forces_file", request.forcesFile);
  formData.append("format", request.format || "auto");
  formData.append("default_fck", String(request.defaultFck || 25));
  formData.append("default_fy", String(request.defaultFy || 500));

  const response = await fetch(`${API_BASE_URL}/api/v1/imports/dual-csv`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`CSV import failed: ${error.detail || response.status}`);
  }

  const data = await response.json();

  return {
    success: data.success,
    beams: data.beams,
    beamCount: data.beam_count,
    warnings: data.warnings.map((w: Record<string, unknown>) => ({
      code: w.code,
      message: w.message,
      severity: w.severity as WarningSeverity,
      rowIndex: w.row_index as number | undefined,
      column: w.column as string | undefined,
    })),
    metadata: {
      geometryFormat: data.metadata.geometry_format,
      forcesFormat: data.metadata.forces_format,
      mergedCount: data.metadata.merged_count,
      unmatchedGeometry: data.metadata.unmatched_geometry || [],
      unmatchedForces: data.metadata.unmatched_forces || [],
    },
  };
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * useDualCSVImport - Hook for dual-file CSV import workflow.
 *
 * Manages file selection, upload, and parsing state.
 * Uses the library's csv_import module for consistent parsing.
 *
 * @example
 * ```tsx
 * const {
 *   state,
 *   uploadFiles,
 *   reset,
 * } = useDualCSVImport();
 *
 * const handleFiles = (geom: File, forces: File) => {
 *   uploadFiles({
 *     geometryFile: geom,
 *     forcesFile: forces,
 *   });
 * };
 *
 * if (state.status === "complete") {
 *   setBeams(state.result.beams);
 * }
 * ```
 */
export function useDualCSVImport() {
  const [state, setState] = useState<DualImportState>({
    status: "idle",
    progress: 0,
    result: null,
    error: null,
  });

  const mutation = useMutation({
    mutationFn: uploadDualCSV,
    onMutate: () => {
      setState({
        status: "uploading",
        progress: 10,
        result: null,
        error: null,
      });
    },
    onSuccess: (result) => {
      setState({
        status: "complete",
        progress: 100,
        result,
        error: null,
      });
    },
    onError: (error) => {
      setState({
        status: "error",
        progress: 0,
        result: null,
        error: error instanceof Error ? error.message : String(error),
      });
    },
  });

  const uploadFiles = useCallback(
    (request: DualCSVImportRequest) => {
      mutation.mutate(request);
    },
    [mutation]
  );

  const reset = useCallback(() => {
    setState({
      status: "idle",
      progress: 0,
      result: null,
      error: null,
    });
    mutation.reset();
  }, [mutation]);

  return {
    state,
    uploadFiles,
    reset,
    isLoading: mutation.isPending,
  };
}

/**
 * useDualCSVImportMutation - Simple mutation hook.
 *
 * Use when you just want the mutation without state management.
 */
export function useDualCSVImportMutation() {
  return useMutation({
    mutationFn: uploadDualCSV,
  });
}

export default useDualCSVImport;
