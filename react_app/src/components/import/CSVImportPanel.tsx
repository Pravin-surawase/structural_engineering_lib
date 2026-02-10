/**
 * CSVImportPanel Component
 *
 * Drag-and-drop CSV import for multi-beam visualization.
 */
import { useCallback, useState } from 'react';
import type { DragEvent } from 'react';
import { useImportedBeamsStore } from '../../store/importedBeamsStore';
import { parseBeamCSV } from '../../types/csv';

export function CSVImportPanel() {
  const { beams, selectedId, selectBeam, setBeams, clearBeams, isImporting, error, setImporting, setError } =
    useImportedBeamsStore();
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    async (e: DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      setImporting(true);

      const file = e.dataTransfer.files[0];
      if (!file) {
        setError('No file dropped');
        return;
      }

      if (!file.name.endsWith('.csv')) {
        setError('Please drop a CSV file');
        return;
      }

      try {
        const text = await file.text();
        const parsedBeams = parseBeamCSV(text);
        setBeams(parsedBeams);
      } catch (err) {
        setError((err as Error).message);
      }
    },
    [setBeams, setImporting, setError]
  );

  const handleFileInput = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      setImporting(true);
      try {
        const text = await file.text();
        const parsedBeams = parseBeamCSV(text);
        setBeams(parsedBeams);
      } catch (err) {
        setError((err as Error).message);
      }
    },
    [setBeams, setImporting, setError]
  );

  return (
    <div className="p-3 flex flex-col gap-3 h-full overflow-y-auto bg-[#1e1e1e] text-[#e0e0e0]">
      <h3 className="m-0 text-sm text-[#888] uppercase tracking-wide">CSV Import</h3>

      {/* Drop zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center gap-2 transition-all cursor-pointer ${
          isDragging ? 'border-[#0078d4] bg-[#0078d4]/10' : 'border-[#444]'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <span className="text-[#888] text-[13px]">Drop CSV here</span>
        <span className="text-[11px] text-[#666]">or</span>
        <label className="text-[#0078d4] cursor-pointer text-[13px] hover:underline">
          Browse
          <input type="file" accept=".csv" onChange={handleFileInput} className="hidden" />
        </label>
      </div>

      {/* Loading state */}
      {isImporting && <div className="text-[#0078d4] text-center text-[13px]">Importing...</div>}

      {/* Error */}
      {error && <div className="text-red-500 p-2 bg-red-500/10 rounded text-xs">{error}</div>}

      {/* Imported beams list */}
      {beams.length > 0 && (
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs text-[#888]">
            <span>{beams.length} beams imported</span>
            <button
              className="bg-transparent border-none text-red-500 cursor-pointer text-[11px] px-1.5 py-0.5 hover:underline"
              onClick={clearBeams}
            >
              Clear
            </button>
          </div>
          <div className="flex flex-col gap-1 max-h-[200px] overflow-y-auto">
            {beams.slice(0, 20).map((beam) => (
              <div
                key={beam.id}
                className={`flex justify-between p-1.5 px-2 rounded cursor-pointer text-xs transition-colors ${
                  selectedId === beam.id
                    ? 'bg-[#0078d4]/30 border border-[#0078d4]'
                    : 'bg-[#2d2d2d] hover:bg-[#3a3a3a]'
                }`}
                onClick={() => selectBeam(beam.id)}
              >
                <span className="font-medium text-white">{beam.id}</span>
                <span className="text-[#888]">
                  {beam.b}×{beam.D}mm
                </span>
              </div>
            ))}
            {beams.length > 20 && (
              <div className="text-center text-[11px] text-[#666] p-1">+{beams.length - 20} more</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
