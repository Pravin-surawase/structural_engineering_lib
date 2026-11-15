/**
 * Maps Quick Beam's physical effective-depth basis to the legacy Pareto
 * endpoint field, whose `cover_mm` is a D-d screening offset.
 */
export function resolveComparisonDepthOffsetMm({
  depthMm,
  effectiveDepthMm,
  clearCoverMm,
  stirrupDiameterMm,
  mainBarDiameterMm,
}: {
  depthMm: number;
  effectiveDepthMm?: number;
  clearCoverMm: number;
  stirrupDiameterMm: number;
  mainBarDiameterMm: number;
}): number {
  return effectiveDepthMm === undefined
    ? clearCoverMm + stirrupDiameterMm + mainBarDiameterMm / 2
    : depthMm - effectiveDepthMm;
}
