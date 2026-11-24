/**
 * FileDropZone Component
 *
 * Drag-and-drop file upload for CSV import.
 * Uses the useCSVFileImport hook which calls the library's
 * adapter system for intelligent column mapping.
 */
import { FileUp, Loader2 } from "lucide-react";
import React, { useCallback, useState } from "react";
import { useCSVFileImport } from "../../hooks/useCSVImport";
import type { MaterialOverrides } from "../../utils/materialOverrides";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";

interface FileDropZoneProps {
  /** Accepted file types (default: .csv) */
  accept?: string;
  /** Max file size in bytes (default: 10MB) */
  maxSize?: number;
  /** Called after successful import */
  onSuccess?: (beamCount: number) => void;
  /** Called on error */
  onError?: (error: string) => void;
  /** Custom class name */
  className?: string;
  /** Material overrides applied after import */
  materialOverrides?: MaterialOverrides;
  /** Explicit adapter selection, or auto when the artifact is unambiguous. */
  formatHint?: "auto" | "etabs" | "safe" | "staad" | "generic";
}

export function FileDropZone({
  accept = ".csv",
  maxSize = 10 * 1024 * 1024, // 10MB
  onSuccess,
  onError,
  className = "",
  materialOverrides,
  formatHint = "auto",
}: FileDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const { importFile, isImporting, data, error: importError } = useCSVFileImport();
  const { beams, error: storeError, isImporting: storeIsImporting } = useImportedBeamsStore();
  const isBusy = isImporting || storeIsImporting;

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isBusy) setIsDragging(true);
  }, [isBusy]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const validateFile = useCallback(
    (file: File): string | null => {
      // Check file type
      const extension = file.name.toLowerCase().split(".").pop();
      const acceptedTypes = accept.split(",").map((t) => t.trim().replace(".", ""));
      if (!acceptedTypes.includes(extension || "")) {
        return `Invalid file type. Accepted: ${accept}`;
      }

      // Check file size
      if (file.size > maxSize) {
        const maxMB = (maxSize / 1024 / 1024).toFixed(1);
        return `File too large. Maximum size: ${maxMB}MB`;
      }

      return null;
    },
    [accept, maxSize]
  );

  const processFile = useCallback(
    (file: File) => {
      if (isBusy) return;
      const validationError = validateFile(file);
      if (validationError) {
        onError?.(validationError);
        return;
      }

      importFile(file, formatHint, materialOverrides);
    },
    [importFile, isBusy, validateFile, onError, materialOverrides, formatHint]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = Array.from(e.dataTransfer.files);
      if (files.length === 0) return;

      // Only process first file
      processFile(files[0]);
    },
    [processFile]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (!files || files.length === 0) return;

      processFile(files[0]);

      // Reset input so same file can be selected again
      e.target.value = "";
    },
    [processFile]
  );

  // Trigger success callback when import completes
  React.useEffect(() => {
    if (data?.success && data.beam_count > 0) {
      onSuccess?.(data.beam_count);
    }
  }, [data, onSuccess]);

  // Trigger error callback
  React.useEffect(() => {
    const errorMessage = importError?.message || storeError;
    if (errorMessage) {
      onError?.(errorMessage);
    }
  }, [importError, storeError, onError]);

  const displayError = importError?.message || storeError;

  return (
    <div
      className={className}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <input
        id="file-drop-input"
        type="file"
        accept={accept}
        onChange={handleFileInput}
        disabled={isBusy}
        aria-label="Choose CSV file"
        className="peer sr-only"
      />
      <label
        htmlFor="file-drop-input"
        className={
          "flex min-h-40 flex-col items-center justify-center gap-2 rounded-sm border border-dashed p-4 text-center text-ink peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-cobalt " +
          (isDragging ? "border-cobalt bg-cobalt/10" : "border-ink/25 bg-white hover:border-cobalt") +
          (isBusy ? " cursor-wait" : " cursor-pointer")
        }
      >
        {isBusy ? (
          <span role="status" className="flex flex-col items-center gap-2 text-sm text-ink">
            <Loader2 size={25} className="animate-spin text-cobalt" aria-hidden="true" />
            Importing CSV…
          </span>
        ) : (
          <>
            <FileUp size={26} className="text-cobalt" aria-hidden="true" />
            <span className="text-sm font-semibold">{isDragging ? "Drop CSV file here" : "Choose CSV file"}</span>
            <span className="text-xs text-ink/75">You can also drag and drop a file.</span>
          </>
        )}
      </label>
      {data?.success && beams.length > 0 && !isBusy ? (
        <p className="mt-2 text-sm text-emerald-800" role="status">
          Imported {beams.length} {beams.length === 1 ? 'beam' : 'beams'}{data.warnings?.length ? ` · ${data.warnings.length} warning(s)` : ""}
        </p>
      ) : null}
      {displayError ? (
        <p className="mt-2 rounded-sm border border-rose-300 bg-rose-50 p-3 text-sm text-rose-900" role="alert">{displayError}</p>
      ) : null}
    </div>
  );
}

export default FileDropZone;
