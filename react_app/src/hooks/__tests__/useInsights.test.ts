/**
 * Tests for useInsights hooks — Dashboard, Code Checks, Rebar Suggestions.
 *
 * Each hook wraps a useMutation calling the /api/v1/insights/* endpoints.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useDashboardInsights,
  useCodeChecks,
  useRebarSuggestions,
} from '../../hooks/useInsights';
import {
  dashboardResponse,
  codeChecksResponse,
  rebarSuggestResponse,
} from '../../test/api-fixtures';

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

function mockFetch(body: unknown) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  );
}

function mockFetchError(status: number, detail: string) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
    new Response(JSON.stringify({ detail }), {
      status,
      headers: { 'Content-Type': 'application/json' },
    })
  );
}

describe('useDashboardInsights', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('returns dashboard data on success', async () => {
    mockFetch(dashboardResponse);
    const { result } = renderHook(() => useDashboardInsights(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      results: [
        {
          beam_id: 'B1',
          story: 'GF',
          is_valid: true,
          utilization: 0.78,
          ast_provided: 942,
          b_mm: 300,
          D_mm: 500,
          span_mm: 5000,
          warnings: [],
        },
      ],
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(dashboardResponse);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/insights/dashboard',
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('throws on API failure', async () => {
    mockFetchError(422, 'Invalid beam results');
    const { result } = renderHook(() => useDashboardInsights(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ results: [] });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toContain('Invalid beam results');
  });
});

describe('useCodeChecks', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('returns code check results on success', async () => {
    mockFetch(codeChecksResponse);
    const { result } = renderHook(() => useCodeChecks(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      beam: { b_mm: 300, D_mm: 500, fck_mpa: 25, fy_mpa: 500, mu_knm: 150 },
      config: { ast_mm2: 942, bar_count: 3, bar_dia_mm: 20 },
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(codeChecksResponse);
    expect(result.current.data?.checks).toHaveLength(
      codeChecksResponse.checks.length
    );
    expect(globalThis.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/insights/code-checks',
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('throws on code check failure', async () => {
    mockFetchError(400, 'Code checks failed');
    const { result } = renderHook(() => useCodeChecks(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ beam: {} });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toContain('Code checks failed');
  });
});

describe('useRebarSuggestions', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('returns rebar suggestions on success', async () => {
    mockFetch(rebarSuggestResponse);
    const { result } = renderHook(() => useRebarSuggestions(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      ast_required: 850,
      b_mm: 300,
      cover_mm: 40,
      beam_id: 'B1',
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(rebarSuggestResponse);
    expect(result.current.data?.suggestions.length).toBeGreaterThan(0);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/insights/rebar-suggest',
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('throws on suggestion failure', async () => {
    mockFetchError(500, 'Rebar suggestion failed');
    const { result } = renderHook(() => useRebarSuggestions(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ ast_required: -100 });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toContain('Rebar suggestion failed');
  });
});
