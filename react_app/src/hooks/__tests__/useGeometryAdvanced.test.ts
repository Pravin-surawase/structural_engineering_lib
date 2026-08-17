import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useBuildingGeometry } from '../../hooks/useGeometryAdvanced';

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

describe('useBuildingGeometry', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('uses the same typed visualization contract as FastAPI', async () => {
    const response = {
      success: true,
      data: {
        success: true,
        message: 'Generated geometry for 1 members',
        beams: [
          {
            beam_id: 'B1',
            story: 'GF',
            frame_type: 'beam',
            start: { x: 0, y: 0, z: 0 },
            end: { x: 6000, y: 0, z: 0 },
          },
        ],
        bounding_box: {
          min_x: 0,
          max_x: 6000,
          min_y: 0,
          max_y: 0,
          min_z: 0,
          max_z: 0,
        },
        center: { x: 3000, y: 0, z: 0 },
        metadata: {
          contract_scope: 'visualization_only',
          source_coordinate_basis: 'source_units',
          output_coordinate_units: 'mm',
          coordinate_scale_to_mm: 1000,
          input_member_count: 1,
          output_member_count: 1,
          filtered_member_count: 0,
        },
        warnings: [],
      },
    };
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(response), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    const { result } = renderHook(() => useBuildingGeometry(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.mutate({
        beams: [
          {
            id: 'B1',
            label: 'B1',
            story: 'GF',
            frame_type: 'beam',
            point1: { x: 0, y: 0, z: 0 },
            point2: { x: 6, y: 0, z: 0 },
            section: {
              width_mm: 300,
              depth_mm: 500,
              fck_mpa: 25,
              fy_mpa: 500,
              cover_mm: 40,
            },
          },
        ],
        unit_scale: 1000,
      });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.metadata.contract_scope).toBe('visualization_only');
    expect(result.current.data?.beams[0].end.x).toBe(6000);
    const request = fetchSpy.mock.calls[0][1] as RequestInit;
    expect(JSON.parse(request.body as string)).toEqual({
      beams: [
        {
          id: 'B1',
          label: 'B1',
          story: 'GF',
          frame_type: 'beam',
          point1: { x: 0, y: 0, z: 0 },
          point2: { x: 6, y: 0, z: 0 },
          section: {
            width_mm: 300,
            depth_mm: 500,
            fck_mpa: 25,
            fy_mpa: 500,
            cover_mm: 40,
          },
        },
      ],
      unit_scale: 1000,
    });
  });
});
