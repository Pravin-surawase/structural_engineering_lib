/**
 * FileDropZone Component
 *
 * Drag-and-drop file upload for CSV import.
 * Uses the useCSVFileImport hook which calls the library's
 * adapter system for intelligent column mapping.
 */
import React, { useCallback, useState } from "react";
import { useCSVFileImport } from "../../hooks/useCSVImport";
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
}

export function FileDropZone({
  accept = ".csv",
  maxSize = 10 * 1024 * 1024, // 10MB
  onSuccess,
  onError,
  className = "",
}: FileDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const { importFile, isImporting, data, error: importError } = useCSVFileImport();
  const { beams, error: storeError } = useImportedBeamsStore();

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

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
      const validationError = validateFile(file);
      if (validationError) {
        onError?.(validationError);
        return;
      }

      importFile(file);
    },
    [importFile, validateFile, onError]
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
      className={`file-drop-zone ${isDragging ? "dragging" : ""} ${isImporting ? "importing" : ""} ${className}`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      style={{
        border: `2px dashed ${isDragging ? "#3b82f6" : "#d1d5db"}`,
        borderRadius: "8px",
        padding: "32px",
        textAlign: "center",
        backgroundColor: isDragging ? "#eff6ff" : "#f9fafb",
        cursor: isImporting ? "wait" : "pointer",
        transition: "all 0.2s ease",
      }}
    >
      <input
        type="file"
        accept={accept}
        onChange={handleFileInput}
        disabled={isImporting}
        id="file-drop-input"
        style={{ display: "none" }}
      />

      <label
        htmlFor="file-drop-input"
        style={{
          cursor: isImporting ? "wait" : "pointer",
          display: "block",
        }}
      >
        {isImporting ? (
          <div className="importing-state">
            <svg
              className="animate-spin"
              style={{
                width: "48px",
                height: "48px",
                margin: "0 auto",
                animation: "spin 1s linear infinite",
              }}
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                style={{ opacity: 0.25 }}
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                style={{ opacity: 0.75 }}
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <p style={{ marginTop: "12px", color: "#6b7280" }}>
              Importing CSV...
            </p>
          </div>
        ) : (
          <div className="ready-state">
            <svg
              style={{
                width: "48px",
                height: "48px",
                margin: "0 auto",
                color: isDragging ? "#3b82f6" : "#9ca3af",
              }}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
              />
            </svg>
            <p style={{ marginTop: "12px", color: "#374151", fontWeight: 500 }}>
              {isDragging ? "Drop CSV file here" : "Drag & drop CSV file"}
            </p>
            <p style={{ marginTop: "4px", color: "#6b7280", fontSize: "14px" }}>
              or click to browse
            </p>
          </div>
        )}
      </label>

      {/* Success state */}
      {data?.success && beams.length > 0 && !isImporting && (
        <div
          style={{
            marginTop: "16px",
            padding: "12px",
            backgroundColor: "#d1fae5",
            borderRadius: "6px",
            color: "#065f46",
          }}
        >
          <p style={{ fontWeight: 500 }}>
            ✓ Imported {beams.length} beams
          </p>
          {data.warnings && data.warnings.length > 0 && (
            <p style={{ fontSize: "12px", marginTop: "4px" }}>
              {data.warnings.length} warning(s)
            </p>
          )}
        </div>
      )}

      {/* Error state */}
      {displayError && (
        <div
          style={{
            marginTop: "16px",
            padding: "12px",
            backgroundColor: "#fee2e2",
            borderRadius: "6px",
            color: "#991b1b",
          }}
        >
          <p>{displayError}</p>
        </div>
      )}

      {/* Format info */}
      <div
        style={{
          marginTop: "16px",
          color: "#9ca3af",
          fontSize: "12px",
        }}
      >
        Supports: Generic CSV, ETABS, SAFE, STAAD formats
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .file-drop-zone:hover:not(.importing) {
          border-color: #3b82f6;
          background-color: #eff6ff;
        }
      `}</style>
    </div>
  );
}

export default FileDropZone;
