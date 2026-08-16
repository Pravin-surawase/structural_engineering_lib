export interface MaterialOverrides {
  fck?: number;
  fy?: number;
  cover?: number;
  stirrupDiameter?: number;
  tensionBarDiameter?: number;
}

export function applyMaterialOverrides<T extends {
  fck?: number;
  fy?: number;
  cover?: number;
  stirrup_diameter_mm?: number;
  tension_bar_diameter_mm?: number;
}>(
  beams: T[],
  overrides?: MaterialOverrides
): T[] {
  if (!overrides) return beams;

  const { fck, fy, cover, stirrupDiameter, tensionBarDiameter } = overrides;
  if (
    fck === undefined
    && fy === undefined
    && cover === undefined
    && stirrupDiameter === undefined
    && tensionBarDiameter === undefined
  ) return beams;

  return beams.map((beam) => ({
    ...beam,
    ...(fck !== undefined ? { fck } : {}),
    ...(fy !== undefined ? { fy } : {}),
    ...(cover !== undefined ? { cover } : {}),
    ...(stirrupDiameter !== undefined
      ? { stirrup_diameter_mm: stirrupDiameter }
      : {}),
    ...(tensionBarDiameter !== undefined
      ? { tension_bar_diameter_mm: tensionBarDiameter }
      : {}),
  }));
}
