import { useMutation } from '@tanstack/react-query';
import { analyzeLoads } from '../api/client';
import type { LoadAnalysisRequest, LoadAnalysisResponse } from '../api/client';

/**
 * Hook for computing BMD/SFD via the load analysis API.
 * Returns positions, BMD array, SFD array, and critical points.
 */
export function useLoadAnalysis() {
  return useMutation({
    mutationFn: (params: LoadAnalysisRequest) => analyzeLoads(params),
    mutationKey: ['load-analysis'],
  });
}

export type { LoadAnalysisRequest, LoadAnalysisResponse };
