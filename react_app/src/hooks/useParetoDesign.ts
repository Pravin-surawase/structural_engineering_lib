/**
 * useParetoDesign — Hook for Pareto multi-objective beam optimization.
 *
 * Calls POST /api/v1/optimization/beam/pareto to find Pareto-optimal designs
 * balancing cost, weight, and utilization.
 */
import { useMutation } from "@tanstack/react-query";
import { optimizeParetoFront } from "../api/client";
import type { ParetoRequest, ParetoResponse } from "../api/client";

export function useParetoDesign() {
  return useMutation<ParetoResponse, Error, ParetoRequest>({
    mutationFn: optimizeParetoFront,
  });
}

export type { ParetoRequest, ParetoResponse };
