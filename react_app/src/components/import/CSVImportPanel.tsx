/**
 * CSVImportPanel Component
 *
 * Drag-and-drop CSV import for multi-beam visualization.
 */
import { useCallback, useState } from 'react';
import type { DragEvent } from 'react';
import { useImportedBeamsStore } from '../../store/importedBeamsStore';
import { parseBeamCSV } from '../../types/csv';
import './CSVImportPanel.css';

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
    <div className="csv-import-panel">
      <h3>CSV Import</h3>

      {/* Drop zone */}
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <span>Drop CSV here</span>
        <span className="or">or</span>
        <label className="file-input-label">
          Browse
          <input type="file" accept=".csv" onChange={handleFileInput} />
        </label>
      </div>

      {/* Loading state */}
      {isImporting && <div className="loading">Importing...</div>}

      {/* Error */}
      {error && <div className="error">{error}</div>}

      {/* Imported beams list */}
      {beams.length > 0 && (
        <div className="beams-list">
          <div className="list-header">
            <span>{beams.length} beams imported</span>
            <button className="clear-btn" onClick={clearBeams}>
              Clear
            </button>
          </div>
          <div className="list-items">
            {beams.slice(0, 20).map((beam) => (
              <div
                key={beam.id}
                className={`beam-item ${selectedId === beam.id ? 'selected' : ''}`}
                onClick={() => selectBeam(beam.id)}
              >
                <span className="beam-id">{beam.id}</span>
                <span className="beam-dims">
                  {beam.b}×{beam.D}mm
                </span>
              </div>
            ))}
            {beams.length > 20 && (
              <div className="more-items">+{beams.length - 20} more</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
