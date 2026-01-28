/**
 * CSV Import Types
 *
 * Types for CSV beam data import and multi-beam visualization.
 *
 * NOTE: For CSV parsing, use the useCSVFileImport or useCSVTextImport hooks
 * which call the library's adapter system via API. The library's
 * GenericCSVAdapter supports 40+ column name variations.
 *
 * @see hooks/useCSVImport.ts
 */

/**
 * 3D Point for beam endpoint positions.
 * Coordinates are in meters (from ETABS/structural model).
 */
export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export interface BeamCSVRow {
  id: string;
  story?: string;
  b: number;      // width in mm
  D: number;      // depth in mm
  span: number;   // span in mm
  fck?: number;   // concrete grade N/mm²
  fy?: number;    // steel grade N/mm²
  Mu_start?: number;  // moment at start kN·m
  Mu_mid?: number;    // moment at mid kN·m
  Mu_end?: number;    // moment at end kN·m
  Vu_start?: number;  // shear at start kN
  Vu_end?: number;    // shear at end kN
  cover?: number;     // cover in mm

  // Envelope values for design (computed from start/mid/end)
  mu_envelope?: number;  // max(|Mu_start|, |Mu_mid|, |Mu_end|) kN·m
  vu_envelope?: number;  // max(|Vu_start|, |Vu_end|) kN

  // 3D position for building visualization (optional)
  point1?: Point3D;   // start point (from ETABS geometry)
  point2?: Point3D;   // end point (from ETABS geometry)

  // Design status for color-coding in 3D view
  status?: 'pending' | 'designing' | 'pass' | 'fail' | 'warning';

  // Design results (added after batch design)
  ast_required?: number;    // Required steel area mm²
  asc_required?: number;    // Required compression steel mm²
  ast_provided?: number;    // Provided steel area mm²
  utilization?: number;     // Utilization ratio (0-1+)
  bar_count?: number;
  bar_diameter?: number;
  stirrup_diameter?: number;
  stirrup_spacing?: number;
  is_valid?: boolean;
  remarks?: string[];
}

export interface ImportedBeamsState {
  beams: BeamCSVRow[];
  selectedId: string | null;
  isImporting: boolean;
  error: string | null;
}

/**
 * @deprecated Use useCSVFileImport or useCSVTextImport hooks instead.
 * These hooks call the library's adapter system which handles:
 * - 40+ column name variations (case-insensitive)
 * - Unit conversions (m→mm, kN-m→kN·m)
 * - Intelligent column mapping
 * - ETABS, SAFE, STAAD format detection
 */
export function parseBeamCSV(_csvText: string): BeamCSVRow[] {
  console.warn(
    'parseBeamCSV is deprecated. Use useCSVFileImport or useCSVTextImport hooks instead.'
  );
  throw new Error(
    'parseBeamCSV is deprecated. Use useCSVFileImport or useCSVTextImport hooks instead. ' +
    'See hooks/useCSVImport.ts for the API-backed implementation.'
  );
}
