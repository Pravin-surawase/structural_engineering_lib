export interface MaterialOverrides {
  fck?: number;
  fy?: number;
  cover?: number;
}

export function applyMaterialOverrides<T extends { fck?: number; fy?: number; cover?: number }>(
  beams: T[],
  overrides?: MaterialOverrides
): T[] {
  if (!overrides) return beams;

  const { fck, fy, cover } = overrides;
  if (fck === undefined && fy === undefined && cover === undefined) return beams;

  return beams.map((beam) => ({
    ...beam,
    ...(fck !== undefined ? { fck } : {}),
    ...(fy !== undefined ? { fy } : {}),
    ...(cover !== undefined ? { cover } : {}),
  }));
}
