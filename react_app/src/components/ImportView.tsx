/**
 * ImportView - CSV/Excel import view with drag-drop and sample loading.
 */
import { useState } from "react";
import { FileDropZone } from "./ui/FileDropZone";
import { Upload, FileSpreadsheet, ChevronDown, Play, ArrowLeft } from "lucide-react";
import { useImportedBeamsStore } from "../store/importedBeamsStore";

interface ImportViewProps {
  onBack: () => void;
  onImportComplete: () => void;
}

export function ImportView({ onBack, onImportComplete }: ImportViewProps) {
  const [fck, setFck] = useState(25);
  const [fy, setFy] = useState(500);
  const [cover, setCover] = useState(40);
  const { beams, isImporting, error } = useImportedBeamsStore();

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
                onClick={() => {
                  // TODO: Load sample data
                  console.log("Load sample data");
                }}
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
