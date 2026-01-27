/**
 * ImportView - CSV/Excel import view with drag-drop and sample loading.
 */
import { useState } from "react";
import { FileDropZone } from "./ui/FileDropZone";
import { Upload, FileSpreadsheet, ChevronDown, Play, ArrowLeft } from "lucide-react";
import { useImportedBeamsStore } from "../store/importedBeamsStore";
import { loadSampleData } from "../api/client";
import { mapSampleBeamsToRows } from "../utils/sampleData";
import { applyMaterialOverrides } from "../utils/materialOverrides";
import { useDualCSVImport } from "../hooks/useCSVImport";

interface ImportViewProps {
  onBack: () => void;
  onImportComplete: () => void;
}

export function ImportView({ onBack, onImportComplete }: ImportViewProps) {
  const [fck, setFck] = useState(25);
  const [fy, setFy] = useState(500);
  const [cover, setCover] = useState(40);
  const [geometryFile, setGeometryFile] = useState<File | null>(null);
  const [forcesFile, setForcesFile] = useState<File | null>(null);
  const {
    beams,
    isImporting,
    error,
    warnings,
    unmatchedBeams,
    unmatchedForces,
    setBeams,
    setError,
    setImporting,
  } = useImportedBeamsStore();
  const materialOverrides = { fck, fy, cover };
  const dualImport = useDualCSVImport();

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
        onImportComplete();
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sample data");
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="flex flex-col h-full p-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={onBack}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-white/60" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-white">Import Beams</h2>
          <p className="text-white/50">
            Upload CSV or use sample data
          </p>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6 flex-1">
        {/* Left: File Upload */}
        <div className="col-span-8">
          <FileDropZone
            onSuccess={(count) => {
              console.log(`Imported ${count} beams`);
              if (count > 0) onImportComplete();
            }}
            onError={(err) => console.error(err)}
            materialOverrides={materialOverrides}
          />

          {/* Sample Data Button */}
          <div className="mt-6 p-4 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileSpreadsheet className="w-5 h-5 text-blue-400" />
                <div>
                  <p className="text-white font-medium">Sample Building</p>
                  <p className="text-xs text-white/50">
                    154 beams from ETABS export
                  </p>
                </div>
              </div>
              <button
                onClick={handleLoadSample}
                disabled={isImporting}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                <Upload className="w-4 h-4" />
                Load Sample
              </button>
            </div>
          </div>

          {/* Import Status */}
          {beams.length > 0 && (
            <div className="mt-6 p-4 rounded-xl bg-green-500/10 border border-green-500/30">
              <p className="text-green-400 font-medium">
                ✓ {beams.length} beams imported
              </p>
              <button
                onClick={onImportComplete}
                className="mt-3 px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-500 rounded-lg transition-colors flex items-center gap-2"
              >
                <Play className="w-4 h-4" />
                View 3D Model
              </button>
            </div>
          )}

          {/* Dual CSV Import */}
          <div className="mt-6 p-4 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-white font-medium">Dual CSV Import</p>
                <p className="text-xs text-white/50">
                  Upload geometry + forces as separate files
                </p>
              </div>
              <button
                onClick={() => {
                  if (!geometryFile || !forcesFile) {
                    setError("Please select both geometry and forces CSV files");
                    return;
                  }
                  dualImport.importFiles(geometryFile, forcesFile, "auto", materialOverrides);
                }}
                disabled={isImporting || dualImport.isImporting}
                className="px-4 py-2 text-sm font-medium text-white bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                <Upload className="w-4 h-4" />
                Import Dual CSV
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <label className="block text-xs text-white/60">
                Geometry CSV
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setGeometryFile(e.target.files?.[0] || null)}
                  className="mt-2 block w-full text-xs text-white/70 file:mr-3 file:rounded-md file:border-0 file:bg-white/10 file:px-3 file:py-2 file:text-xs file:text-white"
                />
              </label>
              <label className="block text-xs text-white/60">
                Forces CSV
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setForcesFile(e.target.files?.[0] || null)}
                  className="mt-2 block w-full text-xs text-white/70 file:mr-3 file:rounded-md file:border-0 file:bg-white/10 file:px-3 file:py-2 file:text-xs file:text-white"
                />
              </label>
            </div>
          </div>

          {(warnings.length > 0 || unmatchedBeams.length > 0 || unmatchedForces.length > 0) && (
            <div className="mt-6 p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30">
              <p className="text-yellow-300 font-medium mb-2">Import Warnings</p>
              <ul className="text-xs text-yellow-200/80 space-y-1">
                {warnings.map((warning, idx) => (
                  <li key={`warn-${idx}`}>• {warning}</li>
                ))}
                {unmatchedBeams.length > 0 && (
                  <li>• {unmatchedBeams.length} beams missing forces</li>
                )}
                {unmatchedForces.length > 0 && (
                  <li>• {unmatchedForces.length} forces missing geometry</li>
                )}
              </ul>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30">
              <p className="text-red-400">{error}</p>
            </div>
          )}
        </div>

        {/* Right: Material Settings */}
        <div className="col-span-4">
          <div className="p-6 rounded-xl bg-white/5 border border-white/10">
            <h3 className="text-white font-semibold mb-4">Material Settings</h3>
            <p className="text-xs text-white/50 mb-6">
              Applied to all imported beams
            </p>

            <div className="space-y-4">
              <DropdownField
                label="Concrete Grade"
                value={fck}
                onChange={setFck}
                options={[20, 25, 30, 35, 40, 45, 50]}
                format={(v) => `M${v}`}
              />
              <DropdownField
                label="Steel Grade"
                value={fy}
                onChange={setFy}
                options={[415, 500, 550]}
                format={(v) => `Fe ${v}`}
              />
              <DropdownField
                label="Clear Cover"
                value={cover}
                onChange={setCover}
                options={[25, 30, 35, 40, 45, 50]}
                format={(v) => `${v} mm`}
              />
            </div>

            <div className="mt-6 pt-6 border-t border-white/10">
              <p className="text-xs text-white/40">
                Code: IS 456:2000
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface DropdownFieldProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  options: number[];
  format: (value: number) => string;
}

function DropdownField({ label, value, onChange, options, format }: DropdownFieldProps) {
  return (
    <div>
      <label className="block text-xs text-white/60 mb-2">{label}</label>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full px-3 py-2.5 text-sm text-white bg-white/5 border border-white/10 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500/50"
        >
          {options.map((opt) => (
            <option key={opt} value={opt} className="bg-zinc-900">
              {format(opt)}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40 pointer-events-none" />
      </div>
    </div>
  );
}
