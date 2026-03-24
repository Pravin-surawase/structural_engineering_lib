import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useBeamGeometry } from '../../hooks/useBeamGeometry';
import type { BeamGeometryRequest } from '../../hooks/useBeamGeometry';

// Create a wrapper with QueryClientProvider
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  };
}

const mockParams: BeamGeometryRequest = {
  width: 300,
  depth: 450,
  span: 4000,
  ast_start: 500,
  ast_mid: 400,
  ast_end: 500,
};

describe('useBeamGeometry', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('does not fetch when params is null', () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    const { result } = renderHook(
      () => useBeamGeometry(null),
      { wrapper: createWrapper() },
    );

    expect(result.current.isFetching).toBe(false);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('does not fetch when enabled is false', () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    const { result } = renderHook(
      () => useBeamGeometry(mockParams, { enabled: false }),
      { wrapper: createWrapper() },
    );

    expect(result.current.isFetching).toBe(false);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('fetches geometry when params provided', async () => {
    const mockGeometry = {
      beamId: 'B1',
      story: '1F',
      dimensions: { b: 300, D: 450, span: 4000 },
      concreteOutline: [],
      rebars: [],
      stirrups: [],
      metadata: { cover: 40, ldTension: 600, ldCompression: 400, lapLength: 500, isSeismic: false, isValid: true, remarks: [] },
      version: '1.0',
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({
        success: true,
        message: 'ok',
        geometry: mockGeometry,
        warnings: [],
      }), { status: 200, headers: { 'Content-Type': 'application/json' } }),
    );

    const { result } = renderHook(
      () => useBeamGeometry(mockParams),
      { wrapper: createWrapper() },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockGeometry);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/geometry/beam/full',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('handles API error', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'Invalid dimensions' }), { status: 400 }),
    );

    const { result } = renderHook(
      () => useBeamGeometry(mockParams),
      { wrapper: createWrapper() },
    );

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toContain('Invalid dimensions');
  });
});
