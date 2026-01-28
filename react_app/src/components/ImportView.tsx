/**
 * ImportView - Batch import with dual CSV upload, preview table, and batch design.
 *
 * Step 1: Upload geometry + forces CSVs (or single combined CSV)
 * Step 2: Preview imported beams in table
 * Step 3: Navigate to building editor
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileDropZone } from "./ui/FileDropZone";
import {
  FileSpreadsheet,
  ChevronDown,
  Play,
  ArrowRight,
  Loader2,
  CheckCircle,
} from "lucide-react";
import { useImportedBeamsStore } from "../store/importedBeamsStore";
import { loadSampleData } from "../api/client";
import { mapSampleBeamsToRows } from "../utils/sampleData";
import { applyMaterialOverrides } from "../utils/materialOverrides";

type ImportStep = "upload" | "preview";

export function ImportView() {
  const navigate = useNavigate();
  const [step, setStep] = useState<ImportStep>("upload");
  const [fck, setFck] = useState(25);
  const [fy, setFy] = useState(500);
  const [cover, setCover] = useState(40);
  const { beams, isImporting, error, setBeams, setError, setImporting } =
    useImportedBeamsStore();
  const materialOverrides = { fck, fy, cover };

  const handleLoadSample = async () => {
    setImporting(true);
    setError(null);
    try {
      const data = await loadSampleData();
      if (data.success) {
        const storeBeams = applyMaterialOverrides(
          mapSampleBeamsToRows(data.beams),
          materialOverrides
        );
        setBeams(storeBeams as any);
        setStep("preview");
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load sample data"
      );
    } finally {
      setImporting(false);
    }
  };

  const handleFileImported = (count: number) => {
    if (count > 0) setStep("preview");
  };

  return (
    <div className="h-screen pt-14 flex flex-col bg-zinc-950">
      {/* Step indicator */}
      <div className="px-6 pt-4 pb-2 flex items-center gap-3">
        <StepPill active={step === "upload"} done={step === "preview"} label="1. Upload" />
        <ArrowRight className="w-4 h-4 text-white/20" />
        <StepPill active={step === "preview"} done={false} label="2. Preview & Design" />
        <ArrowRight className="w-4 h-4 text-white/20" />
        <StepPill active={false} done={false} label="3. Building Editor" />
      </div>

      {step === "upload" ? (
        <UploadStep
          fck={fck} setFck={setFck}
          fy={fy} setFy={setFy}
          cover={cover} setCover={setCover}
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
          onProceed={() => navigate("/editor")}
        />
      )}
    </div>
  );
}

function StepPill({ active, done, label }: { active: boolean; done: boolean; label: string }) {
  return (
    <div className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
      active ? "bg-blue-500/20 text-blue-400 border border-blue-500/30" :
      done ? "bg-green-500/20 text-green-400 border border-green-500/30" :
      "bg-white/5 text-white/30 border border-white/8"
    }`}>
      {done && <CheckCircle className="w-3 h-3 inline mr-1" />}
      {label}
    </div>
  );
}

/* ---- Upload Step ---- */

interface UploadStepProps {
  fck: number; setFck: (v: number) => void;
  fy: number; setFy: (v: number) => void;
  cover: number; setCover: (v: number) => void;
  onLoadSample: () => void;
  onFileImported: (count: number) => void;
  isImporting: boolean;
  error: string | null;
  materialOverrides: { fck: number; fy: number; cover: number };
}

function UploadStep({ fck, setFck, fy, setFy, cover, setCover, onLoadSample, onFileImported, isImporting, error, materialOverrides }: UploadStepProps) {
  return (
    <div className="flex-1 flex items-start justify-center px-6 pt-8 gap-6 overflow-y-auto">
      {/* Left: Upload zones */}
      <div className="flex-1 max-w-2xl space-y-5">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Import Beam Data</h2>
          <p className="text-sm text-white/40">Upload CSV from ETABS, SAFE, STAAD, or generic format</p>
        </div>

        {/* Drop zones */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-white/50 mb-2">Geometry + Forces (Single CSV)</p>
            <FileDropZone
              onSuccess={onFileImported}
              onError={(err) => console.error(err)}
              materialOverrides={materialOverrides}
            />
          </div>
          <div>
            <p className="text-xs text-white/50 mb-2">Or use sample data</p>
            <button
              onClick={onLoadSample}
              disabled={isImporting}
              className="w-full h-full min-h-[160px] rounded-2xl border-2 border-dashed border-white/10 hover:border-blue-500/30 bg-white/[0.02] hover:bg-blue-500/5 transition-all flex flex-col items-center justify-center gap-3 disabled:opacity-50"
            >
              {isImporting ? (
                <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
              ) : (
                <>
                  <FileSpreadsheet className="w-8 h-8 text-blue-400" />
                  <div className="text-center">
                    <p className="text-sm text-white font-medium">Sample Building</p>
                    <p className="text-[11px] text-white/40">154 beams from ETABS</p>
                  </div>
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
      </div>

      {/* Right: Material settings */}
      <div className="w-64 shrink-0">
        <div className="p-5 rounded-xl bg-white/[0.03] border border-white/8">
          <h3 className="text-sm text-white font-semibold mb-1">Material Settings</h3>
          <p className="text-[10px] text-white/40 mb-4">Applied to all imported beams</p>

          <div className="space-y-3">
            <DropdownField label="Concrete Grade" value={fck} onChange={setFck} options={[20, 25, 30, 35, 40, 45, 50]} format={(v) => `M${v}`} />
            <DropdownField label="Steel Grade" value={fy} onChange={setFy} options={[415, 500, 550]} format={(v) => `Fe ${v}`} />
            <DropdownField label="Clear Cover" value={cover} onChange={setCover} options={[25, 30, 35, 40, 45, 50]} format={(v) => `${v} mm`} />
          </div>

          <div className="mt-4 pt-4 border-t border-white/8">
            <p className="text-[10px] text-white/30">Code: IS 456:2000</p>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---- Preview Step ---- */

interface PreviewStepProps {
  beams: any[];
  onBack: () => void;
  onProceed: () => void;
}

function PreviewStep({ beams, onBack, onProceed }: PreviewStepProps) {
  const stories = [...new Set(beams.map((b) => b.story).filter(Boolean))];

  return (
    <div className="flex-1 flex flex-col px-6 py-4 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-white">Preview Import</h2>
          <p className="text-sm text-white/40">
            {beams.length} beams across {stories.length} stories
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="px-4 py-2 text-sm text-white/50 hover:text-white/80 transition-colors">
            Back
          </button>
          <button
            onClick={onProceed}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl transition-colors flex items-center gap-2"
          >
            <Play className="w-4 h-4" />
            Open Building Editor
          </button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <SummaryCard label="Total Beams" value={beams.length.toString()} />
        <SummaryCard label="Stories" value={stories.length.toString()} />
        <SummaryCard label="With 3D Pos" value={beams.filter((b: any) => b.point1).length.toString()} />
        <SummaryCard label="Format" value="ETABS" />
      </div>

      {/* Preview table */}
      <div className="flex-1 overflow-auto rounded-xl border border-white/8 bg-white/[0.02]">
        <table className="w-full text-xs">
          <thead className="sticky top-0 bg-zinc-900/95 backdrop-blur">
            <tr className="border-b border-white/8">
              {["ID", "Story", "Width", "Depth", "Span", "Mu_mid", "Vu_start", "fck", "fy"].map((h) => (
                <th key={h} className="px-3 py-2.5 text-left text-white/50 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {beams.slice(0, 50).map((b: any, i: number) => (
              <tr key={b.id || i} className="border-b border-white/5 hover:bg-white/[0.03] transition-colors">
                <td className="px-3 py-2 text-white/80 font-mono">{b.id}</td>
                <td className="px-3 py-2 text-white/60">{b.story || "-"}</td>
                <td className="px-3 py-2 text-white/60">{b.b} mm</td>
                <td className="px-3 py-2 text-white/60">{b.D} mm</td>
                <td className="px-3 py-2 text-white/60">{b.span} mm</td>
                <td className="px-3 py-2 text-white/60">{b.Mu_mid?.toFixed(1) || "-"}</td>
                <td className="px-3 py-2 text-white/60">{b.Vu_start?.toFixed(1) || "-"}</td>
                <td className="px-3 py-2 text-white/60">{b.fck || 25}</td>
                <td className="px-3 py-2 text-white/60">{b.fy || 500}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {beams.length > 50 && (
          <p className="text-center py-3 text-xs text-white/30">
            Showing 50 of {beams.length} beams. Full data in Building Editor.
          </p>
        )}
      </div>
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-3 rounded-xl bg-white/[0.03] border border-white/8">
      <p className="text-[10px] text-white/40 uppercase tracking-wider">{label}</p>
      <p className="text-lg font-bold text-white mt-1">{value}</p>
    </div>
  );
}

function DropdownField({ label, value, onChange, options, format }: {
  label: string; value: number; onChange: (value: number) => void; options: number[]; format: (value: number) => string;
}) {
  return (
    <div>
      <label className="block text-[10px] text-white/50 mb-1">{label}</label>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full px-2.5 py-1.5 text-xs text-white bg-white/[0.04] border border-white/8 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500/50"
        >
          {options.map((opt) => (
            <option key={opt} value={opt} className="bg-zinc-900">{format(opt)}</option>
          ))}
        </select>
        <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/30 pointer-events-none" />
      </div>
    </div>
  );
}
