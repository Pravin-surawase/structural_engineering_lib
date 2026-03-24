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
          beam_id: 'B1',
          story: '1F',
          width_mm: 300,
          depth_mm: 450,
          span_mm: 4000,
          fck_mpa: 25,
          fy_mpa: 500,
          cover_mm: 40,
        },
      ],
      column_mapping: {},
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
});
