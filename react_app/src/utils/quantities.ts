const STEEL_DENSITY_KG_PER_M3 = 7850;

/** Calculate longitudinal reinforcement weight from area and member length. */
export function calculateSteelWeightKg(areaMm2: number, lengthMm: number): number {
  if (areaMm2 <= 0 || lengthMm <= 0) return 0;
  return areaMm2 * lengthMm * STEEL_DENSITY_KG_PER_M3 / 1e9;
}
