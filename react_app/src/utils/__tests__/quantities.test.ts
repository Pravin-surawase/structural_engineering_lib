import { describe, expect, it } from 'vitest';

import { calculateSteelWeightKg } from '../quantities';

describe('calculateSteelWeightKg', () => {
  it('converts reinforcement area and beam length to total kilograms', () => {
    expect(calculateSteelWeightKg(1000, 5000)).toBeCloseTo(39.25);
  });

  it('returns zero for missing or non-positive quantities', () => {
    expect(calculateSteelWeightKg(0, 5000)).toBe(0);
    expect(calculateSteelWeightKg(1000, 0)).toBe(0);
  });
});
