import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCSVFileImport } from '../../hooks/useCSVImport';

// Mock the imported beams store
const mockSetBeams = vi.fn();
const mockSetImporting = vi.fn();
const mockSetError = vi.fn();

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
    result.current.importFile(file);

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
    result.current.importFile(file);

    await waitFor(() => {
      expect(mockSetError).toHaveBeenCalled();
    });
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
    result.current.importFile(file);

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
