/**
 * CSV Import Types
 *
 * Types for CSV beam data import and multi-beam visualization.
 */

export interface BeamCSVRow {
  id: string;
  story?: string;
  width: number;
  depth: number;
  length: number;
  moment?: number;
  shear?: number;
  x?: number; // Position X in scene
  y?: number; // Position Y in scene
  z?: number; // Position Z in scene
}

export interface ImportedBeamsState {
  beams: BeamCSVRow[];
  selectedId: string | null;
  isImporting: boolean;
  error: string | null;
}

/**
 * Parse CSV text to BeamCSVRow array.
 * Handles common column variations.
 */
export function parseBeamCSV(csvText: string): BeamCSVRow[] {
  const lines = csvText.trim().split('\n');
  if (lines.length < 2) {
    throw new Error('CSV must have header and at least one data row');
  }

  const headers = lines[0].toLowerCase().split(',').map((h) => h.trim());

  // Column mapping (flexible naming)
  const colMap = {
    id: findColumn(headers, ['id', 'beam_id', 'beamid', 'name']),
    story: findColumn(headers, ['story', 'floor', 'level']),
    width: findColumn(headers, ['width', 'b', 'b_mm', 'width_mm']),
    depth: findColumn(headers, ['depth', 'd', 'd_mm', 'depth_mm', 'overall_depth']),
    length: findColumn(headers, ['length', 'span', 'l', 'l_mm', 'span_mm']),
    moment: findColumn(headers, ['moment', 'mu', 'mu_knm', 'moment_knm']),
    shear: findColumn(headers, ['shear', 'vu', 'vu_kn', 'shear_kn']),
    x: findColumn(headers, ['x', 'pos_x', 'position_x']),
    y: findColumn(headers, ['y', 'pos_y', 'position_y']),
    z: findColumn(headers, ['z', 'pos_z', 'position_z']),
  };

  if (colMap.width === -1 || colMap.depth === -1) {
    throw new Error('CSV must have width and depth columns');
  }

  const beams: BeamCSVRow[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map((v) => v.trim());
    if (values.length < 2) continue; // Skip empty lines

    const beam: BeamCSVRow = {
      id: colMap.id !== -1 ? values[colMap.id] : `BEAM-${i}`,
      story: colMap.story !== -1 ? values[colMap.story] : undefined,
      width: parseFloat(values[colMap.width]) || 300,
      depth: parseFloat(values[colMap.depth]) || 450,
      length: colMap.length !== -1 ? parseFloat(values[colMap.length]) || 4000 : 4000,
      moment: colMap.moment !== -1 ? parseFloat(values[colMap.moment]) : undefined,
      shear: colMap.shear !== -1 ? parseFloat(values[colMap.shear]) : undefined,
      x: colMap.x !== -1 ? parseFloat(values[colMap.x]) : (i - 1) * 2,
      y: colMap.y !== -1 ? parseFloat(values[colMap.y]) : 0,
      z: colMap.z !== -1 ? parseFloat(values[colMap.z]) : 0,
    };

    beams.push(beam);
  }

  return beams;
}

function findColumn(headers: string[], candidates: string[]): number {
  for (const candidate of candidates) {
    const idx = headers.indexOf(candidate);
    if (idx !== -1) return idx;
  }
  return -1;
}
