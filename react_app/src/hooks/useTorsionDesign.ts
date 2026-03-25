/**
 * useTorsionDesign — React hook for torsion design via API.
 *
 * Calls POST /api/v1/design/beam/torsion (IS 456 Cl 41).
 */
import { useMutation } from "@tanstack/react-query";
import { designBeamTorsion } from "../api/client";
import type { TorsionDesignRequest, TorsionDesignResponse } from "../api/client";

export function useTorsionDesign() {
  return useMutation<TorsionDesignResponse, Error, TorsionDesignRequest>({
    mutationFn: designBeamTorsion,
  });
}

export type { TorsionDesignRequest, TorsionDesignResponse };
