import { describe, expect, it } from 'vitest';

import type { BeamCSVRow } from '../../types/csv';
import { deriveBeamStatus } from '../beamStatus';

const beam = (overrides: Partial<BeamCSVRow> = {}): BeamCSVRow => ({
  id: 'B1',
  b: 300,
  D: 500,
  span: 5000,
  ...overrides,
});

describe('deriveBeamStatus', () => {
  it('preserves an explicit pending status after input changes', () => {
    expect(
      deriveBeamStatus(beam({ status: 'pending', is_valid: true, utilization: 0.4 })),
    ).toBe('pending');
  });

  it('uses an explicit design validity result before legacy utilization', () => {
    expect(deriveBeamStatus(beam({ is_valid: true, utilization: 1.2 }))).toBe('pass');
    expect(deriveBeamStatus(beam({ is_valid: false, utilization: 0.4 }))).toBe('fail');
  });

  it('supports legacy utilization-only rows', () => {
    expect(deriveBeamStatus(beam({ utilization: 1.01 }))).toBe('fail');
    expect(deriveBeamStatus(beam({ utilization: 0.95 }))).toBe('warning');
    expect(deriveBeamStatus(beam({ utilization: 0.7 }))).toBe('pass');
  });
});
