import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCSVFileImport, useCSVTextImport, useDualCSVImport } from '../../hooks/useCSVImport';
import { buildProjectBeamBatchRequest } from '../useBatchDesign';

// Mock the imported beams store
const mockSetBeams = vi.fn();
const mockSetImporting = vi.fn();
const mockSetError = vi.fn();
const explicitBasis = {
  fck: 25,
  fy: 500,
  cover: 40,
  stirrupDiameter: 8,
  tensionBarDiameter: 16,
};
const spanHeaderGuidance = 'Add a span_mm or Span (mm) column for millimetres, or a Span_m or Span (m) column for metres. Enter a finite positive span for every beam, then upload the CSV again.';

vi.mock('../../store/importedBeamsStore', () => ({
  useImportedBeamsStore: vi.fn(() => ({
    setBeams: mockSetBeams,
    setImporting: mockSetImporting,
    setError: mockSetError,
  })),
}));

vi.mock('../../utils/materialOverrides', () => ({
  applyMaterialOverrides: vi.fn((beams) => beams),
}));

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  };
}

describe('useCSVFileImport', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.restoreAllMocks();
  });

  it('returns expected API', () => {
    const { result } = renderHook(() => useCSVFileImport(), {
      wrapper: createWrapper(),
    });

    expect(result.current.importFile).toBeInstanceOf(Function);
    expect(result.current.isImporting).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.reset).toBeInstanceOf(Function);
  });

  it.each(['file', 'text', 'dual'] as const)('preserves explicit depth from %s import into design', async (transport) => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(new Response(JSON.stringify({
      success: true,
      data: {
        success: true, beam_count: 1, warnings: [], beams: [{
          id: 'B1', source_id: 'B1', width_mm: 300, depth_mm: 500, d_mm: 470,
          span_mm: 6000, fck_mpa: 25, fy_mpa: 500, cover_mm: 40,
          mu_knm: 100, vu_kn: 70,
        }],
      },
    }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
    const { result } = renderHook(() => ({
      file: useCSVFileImport(), text: useCSVTextImport(), dual: useDualCSVImport(),
    }), { wrapper: createWrapper() });
    const file = new File(['source'], 'beams.csv', { type: 'text/csv' });
    if (transport === 'file') result.current.file.importFile(file, 'generic', explicitBasis);
    else if (transport === 'text') result.current.text.importText('source', 'generic', explicitBasis);
    else result.current.dual.importFiles(file, file, 'generic', explicitBasis);
    await waitFor(() => expect(mockSetBeams).toHaveBeenCalled());
    const beam = mockSetBeams.mock.calls[0][0][0];
    expect(beam.d_mm).toBe(470);
    const request = buildProjectBeamBatchRequest(beam, { requestId: 'import-depth' });
    expect(request).toMatchObject({ D_mm: 500, d_mm: 470 });
    expect(request).not.toHaveProperty('effective_depth_basis');
  });

  it('imports file and updates store on success', async () => {
    const mockResponse = {
      success: true,
      message: 'Imported 2 beams',
      beam_count: 2,
      beams: [
        {
          id: 'B1',
          story: '1F',
          width_mm: 300,
          depth_mm: 450,
          span_mm: 4000,
          fck_mpa: 25,
          fy_mpa: 500,
          mu_knm: 50.0,
          vu_kn: 30.0,
          cover_mm: 40,
        },
      ],
      format_detected: 'generic',
      warnings: [],
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(mockResponse), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    const { result } = renderHook(() => useCSVFileImport(), {
      wrapper: createWrapper(),
    });

    const file = new File(['beam_id,width\nB1,300'], 'beams.csv', { type: 'text/csv' });
    result.current.importFile(file, 'generic', explicitBasis);

    await waitFor(() => {
      expect(mockSetBeams).toHaveBeenCalled();
    });

    expect(mockSetImporting).toHaveBeenCalledWith(true);
    expect(mockSetImporting).toHaveBeenCalledWith(false);
  });

  it('handles import error', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'Invalid CSV format' }), { status: 400 }),
    );

    const { result } = renderHook(() => useCSVFileImport(), {
      wrapper: createWrapper(),
    });

    const file = new File(['bad data'], 'bad.csv', { type: 'text/csv' });
    result.current.importFile(file, 'generic', explicitBasis);

    await waitFor(() => {
      expect(mockSetError).toHaveBeenCalledWith('Import failed: Invalid CSV format');
    });
  });

  it.each(['file', 'text', 'dual'] as const)('shows the source row in a rejected %s import', async (transport) => {
    const artifactRole = transport === 'dual' ? 'geometry' : 'combined';
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(new Response(JSON.stringify({
      success: false,
      error: {
        schema_version: 'structural-problem/v1',
        message: 'Request was rejected',
        details: {
          status: 'BLOCKED',
          issues: [{
            artifact_role: artifactRole,
            source_row_number: 2,
            message: "Field 'span_mm' is not a valid number",
          }],
        },
      },
    }), { status: 422 }));
    const { result } = renderHook(() => ({
      file: useCSVFileImport(), text: useCSVTextImport(), dual: useDualCSVImport(),
    }), { wrapper: createWrapper() });
    const file = new File(['source'], 'beams.csv', { type: 'text/csv' });
    if (transport === 'file') result.current.file.importFile(file, 'generic', explicitBasis);
    else if (transport === 'text') result.current.text.importText('source', 'generic', explicitBasis);
    else result.current.dual.importFiles(file, file, 'generic', explicitBasis);

    const prefix = transport === 'dual' ? 'Dual CSV import failed: Geometry CSV' : 'Import failed: CSV';
    await waitFor(() => expect(mockSetError).toHaveBeenCalledWith(`${prefix} row 2: Field 'span_mm' is not a valid number`));
    expect(mockSetError).not.toHaveBeenCalledWith(expect.stringContaining(spanHeaderGuidance));
    expect(mockSetBeams).not.toHaveBeenCalled();
  });

  it('adds span-header guidance when a combined CSV omits the required span column', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(new Response(JSON.stringify({
      success: false,
      error: {
        message: 'Request was rejected',
        details: {
          status: 'BLOCKED',
          issues: [{
            code: 'import.missing_required_header',
            path: 'combined.headers.span_mm',
            message: "Missing required combined field 'span_mm'",
            artifact_role: 'combined',
            source_row_number: null,
          }],
        },
      },
    }), { status: 422 }));
    const { result } = renderHook(() => useCSVFileImport(), { wrapper: createWrapper() });
    result.current.importFile(new File(['beam_id,b_mm\nB1,300'], 'beams.csv', { type: 'text/csv' }), 'generic', explicitBasis);

    await waitFor(() => expect(mockSetError).toHaveBeenCalledWith(
      `Import failed: Missing required combined field 'span_mm'. ${spanHeaderGuidance}`,
    ));
    expect(mockSetBeams).not.toHaveBeenCalled();
  });

  it('preserves the first row issue while adding span-header guidance from a later issue', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(new Response(JSON.stringify({
      success: false,
      error: {
        message: 'Request was rejected',
        details: {
          status: 'BLOCKED',
          issues: [
            {
              code: 'import.invalid_number',
              path: 'combined.rows[3].width_mm',
              message: "Field 'width_mm' is not a valid number",
              artifact_role: 'combined',
              source_row_number: 3,
            },
            {
              code: 'import.missing_required_header',
              path: 'combined.headers.span_mm',
              message: "Missing required combined field 'span_mm'",
              artifact_role: 'combined',
              source_row_number: null,
            },
          ],
        },
      },
    }), { status: 422 }));
    const { result } = renderHook(() => useCSVFileImport(), { wrapper: createWrapper() });
    result.current.importFile(new File(['beam_id,b_mm\nB1,bad'], 'beams.csv', { type: 'text/csv' }), 'generic', explicitBasis);

    await waitFor(() => expect(mockSetError).toHaveBeenCalledWith(
      `Import failed: CSV row 3: Field 'width_mm' is not a valid number. ${spanHeaderGuidance}`,
    ));
    expect(mockSetBeams).not.toHaveBeenCalled();
  });

  it('handles wrapped response and extracts beams correctly (regression: envelope mismatch)', async () => {
    // This is exactly what FastAPI returns — a WRAPPED response
    const wrappedResponse = {
      success: true,
      data: {
        success: true,
        message: 'Imported 3 beams',
        beam_count: 3,
        beams: [
          { id: 'B1', story: 'GF', width_mm: 300, depth_mm: 500, span_mm: 5000, fck_mpa: 25, fy_mpa: 500, mu_knm: 100, vu_kn: 50, cover_mm: 40 },
          { id: 'B2', story: 'GF', width_mm: 250, depth_mm: 450, span_mm: 4000, fck_mpa: 25, fy_mpa: 500, mu_knm: 80, vu_kn: 40, cover_mm: 40 },
          { id: 'B3', story: '1F', width_mm: 300, depth_mm: 500, span_mm: 6000, fck_mpa: 30, fy_mpa: 500, mu_knm: 150, vu_kn: 70, cover_mm: 40 },
        ],
        format_detected: 'generic',
        warnings: [],
      },
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(wrappedResponse), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    const { result } = renderHook(() => useCSVFileImport(), { wrapper: createWrapper() });
    const file = new File(['id,width\nB1,300'], 'beams.csv', { type: 'text/csv' });
    result.current.importFile(file, 'generic', explicitBasis);

    await waitFor(() => {
      expect(mockSetBeams).toHaveBeenCalled();
    });

    // Verify beams were correctly extracted and mapped
    const calledBeams = mockSetBeams.mock.calls[0][0];
    expect(Array.isArray(calledBeams)).toBe(true);
    expect(calledBeams.length).toBe(3);
    expect(calledBeams[0].id).toBe('B1');
    expect(calledBeams[0].b).toBe(300); // width_mm mapped to b
    expect(calledBeams[1].id).toBe('B2');
    expect(calledBeams[2].fck).toBe(30); // fck_mpa mapped to fck
  });
});
