/**
 * ImportView - Batch import with dual CSV upload, preview table, and batch design.
 *
 * Step 1: Upload geometry + forces CSVs (or single combined CSV)
 * Step 2: Preview imported beams in table
 * Step 3: Navigate to building editor
 */
import React, { useState, useCallback, useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import type { BeamCSVRow } from '../../types/csv';
import { FileDropZone } from "../ui/FileDropZone";
import {
  FileSpreadsheet,
  ChevronDown,
  Play,
  Loader2,
  CheckCircle,
  Upload,
  Layers,
} from "lucide-react";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";
import { loadSampleData } from "../../api/client";
import { mapSampleBeamsToRows } from "../../utils/sampleData";
import { applyMaterialOverrides } from "../../utils/materialOverrides";
import { useDualCSVImport } from "../../hooks/useCSVImport";
import { WorkflowBreadcrumb } from "../ui/WorkflowBreadcrumb";
import { projectStagePath } from "../../app/navigation";
import { useWorkspaceStore } from "../../workspace/workspaceStore";

type ImportStep = "upload" | "preview";

export function ImportView() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [step, setStep] = useState<ImportStep>("upload");
  const [fck, setFck] = useState(25);
  const [fy, setFy] = useState(500);
  const [cover, setCover] = useState(40);
  const [stirrupDiameter, setStirrupDiameter] = useState(8);
  const [tensionBarDiameter, setTensionBarDiameter] = useState(16);
  const { beams, isImporting, error, setBeams, setError, setImporting } =
    useImportedBeamsStore();
  const materialOverrides = {
    fck,
    fy,
    cover,
    stirrupDiameter,
    tensionBarDiameter,
  };
  const initialMaterialOverridesRef = useRef(materialOverrides);
  const autoLoadSampleRef = useRef(searchParams.get("sample") === "true");
  const sampleLoadedRef = useRef(false);

  const handleLoadSample = async () => {
    setImporting(true);
    setError(null);
    try {
      const data = await loadSampleData();
      if (data.success && data.beams?.length) {
        const storeBeams: BeamCSVRow[] = applyMaterialOverrides(
          mapSampleBeamsToRows(data.beams, data.dataset),
          materialOverrides
        );
        setBeams(storeBeams);
        setStep("preview");
      } else {
        setError(data.message);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load sample data";
      setError(
        msg.includes("fetch") || msg.includes("network")
          ? "Cannot connect to backend server. Start it with: ./run.sh dev"
          : msg
      );
    } finally {
      setImporting(false);
    }
  };

  // Auto-load sample data when navigated with ?sample=true. State changes stay
  // in promise callbacks so the effect only synchronizes with the URL/API.
  useEffect(() => {
    if (!autoLoadSampleRef.current || sampleLoadedRef.current) return;
    sampleLoadedRef.current = true;

    void Promise.resolve()
      .then(() => {
        setImporting(true);
        setError(null);
        return loadSampleData();
      })
      .then((data) => {
        if (data.success && data.beams?.length) {
          const storeBeams: BeamCSVRow[] = applyMaterialOverrides(
            mapSampleBeamsToRows(data.beams, data.dataset),
            initialMaterialOverridesRef.current
          );
          setBeams(storeBeams);
          setStep("preview");
        } else {
          setError(data.message);
        }
      })
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : "Failed to load sample data";
        setError(
          msg.includes("fetch") || msg.includes("network")
            ? "Cannot connect to backend server. Start it with: ./run.sh dev"
            : msg
        );
      })
      .finally(() => {
        setImporting(false);
        setSearchParams((current) => {
          const next = new URLSearchParams(current);
          next.delete("sample");
          return next;
        }, { replace: true });
      });
  }, [setBeams, setError, setImporting, setSearchParams]);

  const handleFileImported = (count: number) => {
    if (count > 0) setStep("preview");
  };

  return (
    <div className="flex h-full flex-col bg-paper pt-14 text-ink [--focus-color:var(--color-cobalt)] [color-scheme:light]">
      <WorkflowBreadcrumb />

      {step === "upload" ? (
        <UploadStep
          fck={fck} setFck={setFck}
          fy={fy} setFy={setFy}
          cover={cover} setCover={setCover}
          stirrupDiameter={stirrupDiameter}
          setStirrupDiameter={setStirrupDiameter}
          tensionBarDiameter={tensionBarDiameter}
          setTensionBarDiameter={setTensionBarDiameter}
          onLoadSample={handleLoadSample}
          onFileImported={handleFileImported}
          isImporting={isImporting}
          error={error}
          materialOverrides={materialOverrides}
        />
      ) : (
        <PreviewStep
          beams={beams}
          onBack={() => setStep("upload")}
          onProceed={() => {
            const snapshot = useWorkspaceStore.getState().snapshot;
            navigate(
              snapshot
                ? projectStagePath(snapshot.projectId, "review")
                : "/workbench?recovery=project-required",
            );
          }}
        />
      )}
    </div>
  );
}

/* ---- Upload Step ---- */

interface UploadStepProps {
  fck: number; setFck: (v: number) => void;
  fy: number; setFy: (v: number) => void;
  cover: number; setCover: (v: number) => void;
  stirrupDiameter: number; setStirrupDiameter: (v: number) => void;
  tensionBarDiameter: number; setTensionBarDiameter: (v: number) => void;
  onLoadSample: () => void;
  onFileImported: (count: number) => void;
  isImporting: boolean;
  error: string | null;
  materialOverrides: {
    fck: number;
    fy: number;
    cover: number;
    stirrupDiameter: number;
    tensionBarDiameter: number;
  };
}

function UploadStep({ fck, setFck, fy, setFy, cover, setCover, stirrupDiameter, setStirrupDiameter, tensionBarDiameter, setTensionBarDiameter, onLoadSample, onFileImported, isImporting, error, materialOverrides }: UploadStepProps) {
  const [importMode, setImportMode] = useState<"single" | "dual">("single");
  const [singleFormat, setSingleFormat] = useState<"auto" | "etabs" | "safe" | "staad" | "generic">("auto");
  const [geometryFile, setGeometryFile] = useState<File | null>(null);
  const [forcesFile, setForcesFile] = useState<File | null>(null);
  const { importFiles, isImporting: isDualImporting, error: dualError, data: dualData } = useDualCSVImport();

  // Transition to preview step when dual import completes successfully
  React.useEffect(() => {
    if (dualData?.success && dualData.beam_count > 0) {
      onFileImported(dualData.beam_count);
    }
  }, [dualData, onFileImported]);

  const handleDualImport = useCallback(() => {
    if (!geometryFile || !forcesFile) return;
    importFiles(geometryFile, forcesFile, "auto", materialOverrides);
  }, [geometryFile, forcesFile, importFiles, materialOverrides]);

  // Auto-trigger dual import when both files are set
  const handleGeometryFile = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setGeometryFile(file);
  }, []);
  const handleForcesFile = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setForcesFile(file);
  }, []);

  const displayError = error || dualError?.message;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col items-stretch gap-6 overflow-y-auto px-4 py-6 sm:px-6 lg:flex-row lg:items-start">
      {/* Left: Upload zones */}
      <div className="max-w-3xl flex-1 space-y-5">
        <div>
          <h1 className="mb-1 text-2xl font-semibold tracking-tight text-ink">Import Beam Data</h1>
          <p className="max-w-xl text-sm leading-6 text-ink/65">Choose one combined file or pair geometry with forces. StructLib keeps source rows visible before design begins.</p>
        </div>

        {/* Import mode tabs */}
        <div className="flex w-full gap-1 rounded-xl border border-ink/10 bg-white/70 p-1 sm:w-fit">
          <button
            type="button"
            aria-pressed={importMode === "single"}
            onClick={() => setImportMode("single")}
            className={`px-4 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1.5 ${
              importMode === "single"
                ? "bg-cobalt text-white shadow-sm"
                : "text-ink/60 hover:bg-paper hover:text-ink"
            }`}
          >
            <Upload className="w-3.5 h-3.5" />
            Single CSV
          </button>
          <button
            type="button"
            aria-pressed={importMode === "dual"}
            onClick={() => setImportMode("dual")}
            className={`px-4 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1.5 ${
              importMode === "dual"
                ? "bg-cobalt text-white shadow-sm"
                : "text-ink/60 hover:bg-paper hover:text-ink"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Dual CSV (Geometry + Forces)
          </button>
        </div>

        {importMode === "single" ? (
          /* Single CSV mode */
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <p className="mb-2 text-xs font-semibold text-ink/75">Geometry + forces in one CSV</p>
              <label className="mb-2 block text-xs text-ink/65" htmlFor="single-import-format">
                Format
              </label>
              <select
                id="single-import-format"
                value={singleFormat}
                onChange={(event) => setSingleFormat(event.target.value as typeof singleFormat)}
                className="mb-3 w-full rounded-lg border border-ink/15 bg-white px-3 py-2 text-xs text-ink"
              >
                <option value="auto">Auto (requires one unique match)</option>
                <option value="generic">Generic combined CSV</option>
                <option value="etabs">ETABS</option>
                <option value="safe">SAFE</option>
                <option value="staad">STAAD</option>
              </select>
              {singleFormat === "generic" ? (
                <p className="mb-3 text-xs leading-relaxed text-ink/80">
                  Include a positive span for each beam. Use <code>span_mm</code> for millimetres or <code>Span_m</code> for metres.
                </p>
              ) : null}
              <FileDropZone
                onSuccess={onFileImported}
                onError={(err) => console.error(err)}
                materialOverrides={materialOverrides}
                formatHint={singleFormat}
              />
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold text-ink/75">Or explore a maintained sample</p>
              <button
                onClick={onLoadSample}
                disabled={isImporting}
                className="flex min-h-40 w-full flex-col items-center justify-center gap-3 rounded-sm border border-dashed border-cobalt/30 bg-cobalt/[0.03] transition-colors hover:bg-cobalt/[0.08] disabled:opacity-50"
              >
                {isImporting ? (
                  <Loader2 className="h-8 w-8 animate-spin text-cobalt" />
                ) : (
                  <>
                    <FileSpreadsheet className="h-8 w-8 text-cobalt" />
                    <div className="text-center">
                      <p className="text-sm font-semibold text-ink">Sample Building</p>
                      <p className="text-[11px] text-ink/60">Bundled ETABS sample</p>
                    </div>
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* Dual CSV mode */
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {/* Geometry file */}
              <DualFileZone
                label="1. Geometry CSV"
                description="Beam IDs, widths, depths, spans, coordinates"
                file={geometryFile}
                onFileChange={handleGeometryFile}
                accept=".csv"
                inputId="geometry-csv-input"
              />
              {/* Forces file */}
              <DualFileZone
                label="2. Forces CSV"
                description="Beam IDs, moments (Mu), shears (Vu)"
                file={forcesFile}
                onFileChange={handleForcesFile}
                accept=".csv"
                inputId="forces-csv-input"
              />
            </div>

            {/* Import button */}
            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={handleDualImport}
                disabled={!geometryFile || !forcesFile || isDualImporting}
                className="flex items-center gap-2 rounded-xl bg-cobalt px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-cobalt-hover disabled:bg-ink/15 disabled:text-ink/40"
              >
                {isDualImporting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                {isDualImporting ? "Importing..." : "Import & Merge"}
              </button>
              {geometryFile && forcesFile && !isDualImporting && (
                <p className="text-xs text-ink/60">
                  Ready: {geometryFile.name} + {forcesFile.name}
                </p>
              )}
            </div>

            {/* Sample data button */}
            <div className="border-t border-ink/10 pt-2">
              <button
                onClick={onLoadSample}
                disabled={isImporting}
                className="flex items-center gap-1.5 text-xs font-semibold text-cobalt hover:text-cobalt-hover"
              >
                <FileSpreadsheet className="w-3.5 h-3.5" />
                Or load the bundled ETABS sample building
              </button>
            </div>
          </div>
        )}

        {displayError && (
          <div className="rounded-xl border border-rose-300 bg-rose-50 p-3" role="alert">
            <p className="text-sm text-rose-800">{displayError}</p>
          </div>
        )}
      </div>

      {/* Right: Material settings */}
      <div className="w-full shrink-0 lg:w-64">
        <div className="rounded-2xl border border-ink/10 bg-white/75 p-5 shadow-sm">
          <h3 className="mb-1 text-sm font-semibold text-ink">Material Settings</h3>
          <p className="mb-4 text-[10px] text-ink/60">Applied to all imported beams</p>

          <div className="space-y-3">
            <DropdownField label="Concrete Grade" value={fck} onChange={setFck} options={[20, 25, 30, 35, 40, 45, 50]} format={(v) => `M${v}`} />
            <DropdownField label="Steel Grade" value={fy} onChange={setFy} options={[415, 500, 550]} format={(v) => `Fe ${v}`} />
            <DropdownField label="Clear Cover" value={cover} onChange={setCover} options={[25, 30, 35, 40, 45, 50]} format={(v) => `${v} mm`} />
            <DropdownField label="Stirrup Diameter" value={stirrupDiameter} onChange={setStirrupDiameter} options={[6, 8, 10, 12]} format={(v) => `${v} mm`} />
            <DropdownField label="Tension Bar Diameter" value={tensionBarDiameter} onChange={setTensionBarDiameter} options={[12, 16, 20, 25, 32]} format={(v) => `${v} mm`} />
          </div>

          <div className="mt-4 border-t border-ink/10 pt-4">
            <p className="text-[10px] text-ink/55">Engineering basis: IS 456:2000</p>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---- Preview Step ---- */

interface PreviewStepProps {
  beams: BeamCSVRow[];
  onBack: () => void;
  onProceed: () => void;
}

function PreviewStep({ beams, onBack, onProceed }: PreviewStepProps) {
  const stories = [...new Set(beams.map((b) => b.story).filter(Boolean))];
  const invalidGeometry = beams.filter((beam) => beam.b <= 0 || beam.D <= 0 || beam.span <= 0);
  const missingForces = beams.filter((beam) => {
    const moments = [beam.Mu_start, beam.Mu_mid, beam.Mu_end, beam.mu_envelope];
    const shears = [beam.Vu_start, beam.Vu_end, beam.vu_envelope];
    return !moments.some((value) => typeof value === "number" && Math.abs(value) > 0)
      && !shears.some((value) => typeof value === "number" && Math.abs(value) > 0);
  });
  const sourceIds = beams.map((beam) => beam.source_id ?? beam.id);
  const duplicateSourceCount = sourceIds.length - new Set(sourceIds).size;
  const reviewBlocked = invalidGeometry.length > 0 || duplicateSourceCount > 0;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col overflow-hidden px-4 py-5 sm:px-6">
      {/* Header */}
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.18em] text-cobalt">Review before design</p>
          <h1 className="text-2xl font-semibold tracking-tight text-ink">Imported members</h1>
          <p className="mt-1 text-sm text-ink/65">
            {beams.length} beams across {stories.length} stories
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="px-4 py-2 text-sm font-medium text-ink/60 transition-colors hover:text-ink">
            Back
          </button>
          <button
            onClick={onProceed}
            disabled={reviewBlocked}
            className="flex items-center gap-2 rounded-xl bg-cobalt px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-cobalt-hover disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Play className="w-4 h-4" />
            Open review
          </button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
        <SummaryCard label="Total Beams" value={beams.length.toString()} />
        <SummaryCard label="Stories" value={stories.length.toString()} />
        <SummaryCard label="With 3D Pos" value={beams.filter((b: BeamCSVRow) => b.point1).length.toString()} />
        <SummaryCard label="Format" value="ETABS" />
      </div>

      {(reviewBlocked || missingForces.length > 0) ? (
        <div
          className={`mb-4 rounded-xl border p-3 text-sm ${
            reviewBlocked
              ? "border-rose-300 bg-rose-50 text-rose-900"
              : "border-amber-300 bg-amber-50 text-amber-900"
          }`}
          role={reviewBlocked ? "alert" : "status"}
        >
          {invalidGeometry.length > 0 ? `${invalidGeometry.length} members have invalid dimensions. ` : null}
          {duplicateSourceCount > 0 ? `${duplicateSourceCount} duplicate source identities must be corrected. ` : null}
          {missingForces.length > 0
            ? `${missingForces.length} members have no non-zero design forces; they may be reviewed but remain not evaluated.`
            : null}
        </div>
      ) : null}

      {/* Preview table */}
      <div className="flex-1 overflow-auto rounded-2xl border border-ink/10 bg-white shadow-sm">
        <table className="min-w-[760px] w-full text-xs">
          <thead className="sticky top-0 bg-paper/95 backdrop-blur">
            <tr className="border-b border-ink/10">
              {["Source ID", "Label", "Story", "Width", "Depth", "Span", "Mu_mid", "Vu_start", "fck", "fy"].map((h) => (
                <th key={h} className="px-3 py-3 text-left font-semibold text-ink/60">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {beams.slice(0, 50).map((b: BeamCSVRow, i: number) => (
              <tr key={b.id || i} className="border-b border-ink/5 transition-colors hover:bg-cobalt/[0.03]">
                <td className="px-3 py-2.5 font-mono font-medium text-ink">{b.source_id ?? b.id}</td>
                <td className="px-3 py-2.5 font-mono text-ink/75">{b.id}</td>
                <td className="px-3 py-2.5 text-ink/65">{b.story || "-"}</td>
                <td className="px-3 py-2.5 text-ink/65">{b.b} mm</td>
                <td className="px-3 py-2.5 text-ink/65">{b.D} mm</td>
                <td className="px-3 py-2.5 text-ink/65">{b.span} mm</td>
                <td className="px-3 py-2.5 text-ink/65">{b.Mu_mid?.toFixed(1) || "-"}</td>
                <td className="px-3 py-2.5 text-ink/65">{b.Vu_start?.toFixed(1) || "-"}</td>
                <td className="px-3 py-2.5 text-ink/65">{b.fck || 25}</td>
                <td className="px-3 py-2.5 text-ink/65">{b.fy || 500}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {beams.length > 50 && (
          <p className="py-3 text-center text-xs text-ink/55">
            Showing 50 of {beams.length} beams. Full data in Building Editor.
          </p>
        )}
      </div>
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-ink/10 bg-white/75 p-3">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-ink/55">{label}</p>
      <p className="mt-1 text-lg font-semibold text-ink">{value}</p>
    </div>
  );
}

function DropdownField({ label, value, onChange, options, format }: {
  label: string; value: number; onChange: (value: number) => void; options: number[]; format: (value: number) => string;
}) {
  return (
    <label className="block min-w-0">
      <span className="mb-1 block text-xs font-medium text-ink/75">{label}</span>
      <span className="relative block">
        <select
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="min-h-10 w-full cursor-pointer appearance-none rounded-sm border border-ink/25 bg-white py-1.5 pr-7 pl-2.5 text-sm text-ink"
        >
          {options.map((opt) => (
            <option key={opt} value={opt}>{format(opt)}</option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink/65" aria-hidden="true" />
      </span>
    </label>
  );
}

/** File picker zone for dual CSV mode */
function DualFileZone({ label, description, file, onFileChange, accept, inputId }: {
  label: string;
  description: string;
  file: File | null;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  accept: string;
  inputId: string;
}) {
  return (
    <div>
      <p className="mb-2 text-xs font-semibold text-ink/75">{label}</p>
      <input type="file" accept={accept} onChange={onFileChange} id={inputId} aria-label={label} className="peer sr-only" />
      <label
        htmlFor={inputId}
        className={`flex min-h-36 cursor-pointer flex-col items-center justify-center gap-2 rounded-sm border border-dashed p-3 text-center peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-cobalt ${
          file
            ? "border-emerald-400 bg-emerald-50"
            : "border-ink/15 bg-white hover:border-cobalt/45 hover:bg-cobalt/[0.03]"
        }`}
      >
        {file ? (
          <>
            <CheckCircle className="h-6 w-6 text-emerald-700" />
            <p className="max-w-full break-all text-sm font-medium text-emerald-800">{file.name}</p>
            <p className="text-[10px] text-ink/55">Click to replace</p>
          </>
        ) : (
          <>
            <Upload className="h-6 w-6 text-cobalt" aria-hidden="true" />
            <p className="px-4 text-center text-xs text-ink/65">{description}</p>
            <p className="text-[10px] text-ink/55">Click to browse</p>
          </>
        )}
      </label>
    </div>
  );
}
