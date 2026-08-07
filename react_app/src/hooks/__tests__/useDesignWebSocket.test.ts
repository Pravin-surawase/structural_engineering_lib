import { describe, expect, it } from 'vitest';

import { normalizeWebSocketDesignResult } from '../useDesignWebSocket';

describe('normalizeWebSocketDesignResult', () => {
  it('preserves the complete design response contract', () => {
    const result = normalizeWebSocketDesignResult({
      success: true,
      message: 'Design complete',
      flexure: {
        ast_required: 1036,
        ast_min: 222,
        ast_max: 5400,
        xu: 167,
        xu_max: 192,
        is_under_reinforced: true,
        moment_capacity: 162,
        asc_required: 0,
      },
      shear: {
        tau_v: 0.66,
        tau_c: 0.48,
        tau_c_max: 3.1,
        asv_required: 0.22,
        stirrup_spacing: 300,
        sv_max: 300,
        shear_capacity: 92,
      },
      ast_total: 1036,
      asc_total: 0,
      utilization_ratio: 0.926,
      effective_depth_used: 402,
      warnings: [],
    });

    expect(result.success).toBe(true);
    expect(result.utilization_ratio).toBe(0.926);
    expect(result.flexure.moment_capacity).toBe(162);
    expect(result.effective_depth_used).toBe(402);
    expect(result.shear?.tau_c_max).toBe(3.1);
    expect(result.shear?.shear_capacity).toBe(92);
  });

  it('continues to read legacy WebSocket field names', () => {
    const result = normalizeWebSocketDesignResult({
      flexure: { ast_required: 900, mu_lim: 140, is_safe: true },
      shear: { tv: 0.7, tc: 0.5, spacing: 250 },
    });

    expect(result.success).toBe(true);
    expect(result.flexure.moment_capacity).toBe(140);
    expect(result.shear?.tau_v).toBe(0.7);
    expect(result.shear?.stirrup_spacing).toBe(250);
  });
});
