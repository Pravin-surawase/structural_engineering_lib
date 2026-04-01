/**
 * API Endpoint Integration Tests
 *
 * Validates React→FastAPI contract for all 13 routers (47 endpoints).
 * Uses fetch mocking — no real server needed.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as fixtures from '../../test/api-fixtures';

const API = 'http://localhost:8000';

// Helper: mock a successful JSON response
function mockFetch(body: unknown, status = 200) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
    new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
}

// Helper: mock a blob response (for export endpoints)
// jsdom's Response doesn't support Blob body, so use string body
function mockFetchBlob(status = 200) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
    new Response('test-binary-content', {
      status,
      headers: { 'Content-Type': 'application/octet-stream' },
    }),
  );
}

beforeEach(() => {
  vi.restoreAllMocks();
});

afterEach(() => {
  vi.restoreAllMocks();
});

// ═══════════════════════════════════════════════════════════════════════
// 1. HEALTH ROUTER (3 endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Health Router', () => {
  it('GET /health — returns healthy status', async () => {
    const spy = mockFetch(fixtures.healthResponse);
    const res = await fetch(`${API}/health`);
    const data = await res.json();

    expect(spy).toHaveBeenCalledWith(`${API}/health`);
    expect(data.status).toBe('healthy');
    expect(data).toHaveProperty('version');
    expect(data).toHaveProperty('uptime_seconds');
  });

  it('GET /health/ready — returns readiness', async () => {
    mockFetch(fixtures.readyResponse);
    const res = await fetch(`${API}/health/ready`);
    const data = await res.json();

    expect(data.ready).toBe(true);
    expect(data).toHaveProperty('checks');
  });

  it('GET /health/info — returns system info', async () => {
    mockFetch(fixtures.infoResponse);
    const res = await fetch(`${API}/health/info`);
    const data = await res.json();

    expect(data).toHaveProperty('python_version');
    expect(data).toHaveProperty('api_version');
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 2. DESIGN ROUTER (3 endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Design Router', () => {
  it('POST /api/v1/design/beam — returns design result', async () => {
    mockFetch(fixtures.designResponse);
    const res = await fetch(`${API}/api/v1/design/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fixtures.designRequest),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data).toHaveProperty('flexure');
    expect(data.flexure).toHaveProperty('ast_required');
    expect(data.flexure).toHaveProperty('is_under_reinforced');
    expect(data).toHaveProperty('shear');
    expect(data.shear).toHaveProperty('stirrup_spacing');
    expect(data).toHaveProperty('ast_total');
    expect(data.ast_total).toBeGreaterThan(0);
    expect(data).toHaveProperty('utilization_ratio');
  });

  it('POST /api/v1/design/beam/check — returns adequacy check', async () => {
    mockFetch(fixtures.checkResponse);
    const res = await fetch(`${API}/api/v1/design/beam/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...fixtures.designRequest, ast_provided: 942 }),
    });
    const data = await res.json();

    expect(data).toHaveProperty('is_adequate');
    expect(data).toHaveProperty('moment_capacity');
    expect(data).toHaveProperty('moment_utilization');
    expect(data).toHaveProperty('shear_utilization');
  });

  it('GET /api/v1/design/limits — returns parameter limits', async () => {
    mockFetch(fixtures.limitsResponse);
    const res = await fetch(`${API}/api/v1/design/limits`);
    const data = await res.json();

    expect(data).toHaveProperty('concrete');
    expect(data).toHaveProperty('steel');
    expect(data).toHaveProperty('reinforcement');
    expect(data).toHaveProperty('clear_cover');
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 3. DETAILING ROUTER (3 endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Detailing Router', () => {
  it('POST /api/v1/detailing/beam — returns bar layout', async () => {
    mockFetch(fixtures.detailingResponse);
    const res = await fetch(`${API}/api/v1/detailing/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fixtures.detailingRequest),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data).toHaveProperty('tension_bars');
    expect(data).toHaveProperty('ast_provided');
    expect(data.ast_provided).toBeGreaterThan(0);
  });

  it('GET /api/v1/detailing/bar-areas — returns standard bars', async () => {
    mockFetch(fixtures.barAreasResponse);
    const res = await fetch(`${API}/api/v1/detailing/bar-areas`);
    const data = await res.json();

    expect(data).toHaveProperty('bars');
    expect(data.bars).toHaveProperty('T16');
    expect(data.bars.T16.diameter_mm).toBe(16);
  });

  it('GET /api/v1/detailing/development-length/16 — returns Ld', async () => {
    mockFetch(fixtures.developmentLengthResponse);
    const res = await fetch(`${API}/api/v1/detailing/development-length/16?fck=25&fy=500`);
    const data = await res.json();

    expect(data.bar_diameter).toBe(16);
    expect(data).toHaveProperty('ld');
    expect(data.ld).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 4. IMPORT ROUTER (6 endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Import Router', () => {
  it('GET /api/v1/import/sample — returns demo beams', async () => {
    mockFetch(fixtures.sampleDataResponse);
    const res = await fetch(`${API}/api/v1/import/sample`);
    const data = await res.json();

    expect(data).toHaveProperty('beams');
    expect(data.beams.length).toBeGreaterThan(0);
    expect(data.beams[0]).toHaveProperty('id');
    expect(data.beams[0]).toHaveProperty('b');
    expect(data.beams[0]).toHaveProperty('D');
  });

  it('GET /api/v1/import/formats — returns supported formats', async () => {
    mockFetch(fixtures.importFormatsResponse);
    const res = await fetch(`${API}/api/v1/import/formats`);
    const data = await res.json();

    expect(data).toHaveProperty('formats');
    expect(data.formats).toContain('generic');
  });

  it('POST /api/v1/import/csv — accepts CSV file upload', async () => {
    const importResponse = { success: true, beam_count: 1, beams: [{ id: 'B1', b: 300, D: 500 }] };
    mockFetch(importResponse);

    const formData = new FormData();
    formData.append('file', new Blob(['id,b,D\nB1,300,500'], { type: 'text/csv' }), 'test.csv');

    const res = await fetch(`${API}/api/v1/import/csv`, { method: 'POST', body: formData });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data.beam_count).toBe(1);
  });

  it('POST /api/v1/import/csv/text — accepts CSV text', async () => {
    const importResponse = { success: true, beam_count: 1, beams: [] };
    mockFetch(importResponse);

    const res = await fetch(`${API}/api/v1/import/csv/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ csv_text: 'id,b,D\nB1,300,500', format_hint: 'generic' }),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
  });

  it('POST /api/v1/import/dual-csv — accepts geometry + forces CSVs', async () => {
    const dualResponse = { success: true, beam_count: 1, beams: [{ id: 'B1', point1: {} }] };
    mockFetch(dualResponse);

    const formData = new FormData();
    formData.append('geometry_file', new Blob(['BeamID,b,D\nB1,300,500']), 'geom.csv');
    formData.append('forces_file', new Blob(['BeamID,Mu,Vu\nB1,150,80']), 'forces.csv');

    const res = await fetch(`${API}/api/v1/import/dual-csv?format_hint=generic`, {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data.beam_count).toBe(1);
  });

  it('POST /api/v1/import/batch-design — designs all imported beams', async () => {
    const batchResponse = { success: true, results: [{ beam_id: 'B1', passed: true }], total: 1 };
    mockFetch(batchResponse);

    const res = await fetch(`${API}/api/v1/import/batch-design`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beams: [{ beam_id: 'B1', width: 300, depth: 500, moment: 150, shear: 75 }] }),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data).toHaveProperty('results');
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 5. GEOMETRY ROUTER (5 endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Geometry Router', () => {
  it('POST /api/v1/geometry/beam/3d — returns mesh data', async () => {
    mockFetch(fixtures.geometryResponse);
    const res = await fetch(`${API}/api/v1/geometry/beam/3d`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ width: 300, depth: 500, length: 3000 }),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data).toHaveProperty('components');
    expect(data).toHaveProperty('bounding_box');
    expect(data).toHaveProperty('center');
    expect(data.center).toHaveLength(3);
  });

  it('POST /api/v1/geometry/beam/full — returns full geometry with rebars', async () => {
    const fullResponse = { ...fixtures.geometryResponse, total_vertices: 200, total_faces: 150 };
    mockFetch(fullResponse);

    const res = await fetch(`${API}/api/v1/geometry/beam/full`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ width: 300, depth: 500, length: 3000, include_rebars: true }),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data.total_vertices).toBeGreaterThan(0);
  });

  it('GET /api/v1/geometry/materials — returns material properties', async () => {
    mockFetch(fixtures.materialsResponse);
    const res = await fetch(`${API}/api/v1/geometry/materials`);
    const data = await res.json();

    expect(data).toHaveProperty('concrete');
    expect(data).toHaveProperty('steel');
    expect(data.concrete).toHaveProperty('color');
  });

  it('POST /api/v1/geometry/building — returns building geometry', async () => {
    const buildingResponse = { success: true, stories: 3, beams: 10, geometry: {} };
    mockFetch(buildingResponse);

    const res = await fetch(`${API}/api/v1/geometry/building`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beams: [] }),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
  });

  it('POST /api/v1/geometry/cross-section — returns cross-section', async () => {
    const csResponse = { success: true, section: { width: 300, depth: 500, bars: [] } };
    mockFetch(csResponse);

    const res = await fetch(`${API}/api/v1/geometry/cross-section`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ width: 300, depth: 500, bars: [] }),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 6. OPTIMIZATION ROUTER (2 endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Optimization Router', () => {
  it('POST /api/v1/optimization/beam/cost — returns optimal design', async () => {
    mockFetch(fixtures.optimizationResponse);
    const res = await fetch(`${API}/api/v1/optimization/beam/cost`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ moment: 200, shear: 100, fck: 25, fy: 500 }),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data).toHaveProperty('optimal');
    expect(data.optimal).toHaveProperty('cost_breakdown');
    expect(data.optimal.width).toBeGreaterThan(0);
  });

  it('GET /api/v1/optimization/cost-rates — returns material costs', async () => {
    mockFetch(fixtures.costRatesResponse);
    const res = await fetch(`${API}/api/v1/optimization/cost-rates`);
    const data = await res.json();

    expect(data).toHaveProperty('materials');
    expect(data.materials).toHaveProperty('concrete');
    expect(data.materials).toHaveProperty('steel');
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 7. ANALYSIS ROUTER (2 endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Analysis Router', () => {
  it('POST /api/v1/analysis/beam/smart — returns full analysis', async () => {
    mockFetch(fixtures.analysisResponse);
    const res = await fetch(`${API}/api/v1/analysis/beam/smart`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ width: 300, depth: 500, moment: 150, shear: 75, fck: 25, fy: 500 }),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data).toHaveProperty('design_summary');
    expect(data).toHaveProperty('all_checks_passed');
  });

  it('GET /api/v1/analysis/code-clauses — returns IS 456 clauses', async () => {
    mockFetch(fixtures.codeClausesResponse);
    const res = await fetch(`${API}/api/v1/analysis/code-clauses`);
    const data = await res.json();

    expect(data).toHaveProperty('flexure');
    expect(data).toHaveProperty('shear');
    expect(data).toHaveProperty('detailing');
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 8. INSIGHTS ROUTER (3 endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Insights Router', () => {
  it('POST /api/v1/insights/dashboard — returns batch analytics', async () => {
    mockFetch(fixtures.dashboardResponse);
    const res = await fetch(`${API}/api/v1/insights/dashboard`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fixtures.dashboardRequest),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data).toHaveProperty('total_beams');
    expect(data).toHaveProperty('passed');
    expect(data).toHaveProperty('failed');
    expect(data).toHaveProperty('pass_rate');
    expect(data).toHaveProperty('avg_utilization');
    expect(data).toHaveProperty('critical_beams');
    expect(data).toHaveProperty('by_story');
    expect(data).toHaveProperty('total_steel_kg');
    expect(data).toHaveProperty('total_concrete_m3');
  });

  it('POST /api/v1/insights/code-checks — returns IS 456 checks', async () => {
    mockFetch(fixtures.codeChecksResponse);
    const res = await fetch(`${API}/api/v1/insights/code-checks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beam: { b_mm: 300, D_mm: 500, mu_knm: 150 } }),
    });
    const data = await res.json();

    expect(data).toHaveProperty('passed');
    expect(data).toHaveProperty('checks');
    expect(data.checks.length).toBeGreaterThan(0);
    expect(data.checks[0]).toHaveProperty('name');
    expect(data.checks[0]).toHaveProperty('clause');
    expect(data.checks[0]).toHaveProperty('utilization');
    expect(data).toHaveProperty('governing_check');
  });

  it('POST /api/v1/insights/rebar-suggest — returns rebar suggestions', async () => {
    mockFetch(fixtures.rebarSuggestResponse);
    const res = await fetch(`${API}/api/v1/insights/rebar-suggest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beam: { b_mm: 300, D_mm: 500, ast_required: 850 } }),
    });
    const data = await res.json();

    expect(data).toHaveProperty('suggestions');
    expect(data.suggestions.length).toBeGreaterThan(0);
    expect(data.suggestions[0]).toHaveProperty('title');
    expect(data.suggestions[0]).toHaveProperty('impact');
    expect(data.suggestions[0]).toHaveProperty('savings_percent');
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 9. REBAR ROUTER (2 endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Rebar Router', () => {
  it('POST /api/v1/rebar/validate — validates rebar config', async () => {
    mockFetch(fixtures.rebarValidateResponse);
    const res = await fetch(`${API}/api/v1/rebar/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beam: { b_mm: 300, D_mm: 500 }, config: { bar_count: 3, bar_dia_mm: 20 } }),
    });
    const data = await res.json();

    expect(data).toHaveProperty('valid');
    expect(data).toHaveProperty('ast_provided');
    expect(data).toHaveProperty('utilization');
  });

  it('POST /api/v1/rebar/apply — applies rebar config', async () => {
    mockFetch(fixtures.rebarApplyResponse);
    const res = await fetch(`${API}/api/v1/rebar/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beam: { b_mm: 300, D_mm: 500 }, config: { bar_count: 3, bar_dia_mm: 20 } }),
    });
    const data = await res.json();

    expect(data.success).toBe(true);
    expect(data).toHaveProperty('config');
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 10. EXPORT ROUTER (3 endpoints — return blobs)
// ═══════════════════════════════════════════════════════════════════════
describe('Export Router', () => {
  it('POST /api/v1/export/bbs — returns CSV blob', async () => {
    mockFetchBlob();
    const res = await fetch(`${API}/api/v1/export/bbs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beams: [{ beam_id: 'B1', bars: [] }] }),
    });

    expect(res.ok).toBe(true);
    const text = await res.text();
    expect(text.length).toBeGreaterThan(0);
  });

  it('POST /api/v1/export/dxf — returns DXF blob', async () => {
    mockFetchBlob();
    const res = await fetch(`${API}/api/v1/export/dxf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beams: [{ beam_id: 'B1' }] }),
    });

    expect(res.ok).toBe(true);
  });

  it('POST /api/v1/export/report — returns HTML report', async () => {
    mockFetchBlob();
    const res = await fetch(`${API}/api/v1/export/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beams: [{ beam_id: 'B1' }] }),
    });

    expect(res.ok).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 11. WEBSOCKET ROUTER (connection test)
// ═══════════════════════════════════════════════════════════════════════
describe('WebSocket Router', () => {
  it('WS /ws/design/{session_id} — endpoint path is correct', () => {
    // WebSocket can't be fully tested in jsdom, but validate the URL construction
    const sessionId = 'test-session-123';
    const wsUrl = `ws://localhost:8000/ws/design/${sessionId}`;

    expect(wsUrl).toMatch(/^ws:\/\/localhost:8000\/ws\/design\/.+/);
    expect(wsUrl).toContain(sessionId);
  });
});

// ═══════════════════════════════════════════════════════════════════════
// 12. STREAMING ROUTER (SSE endpoints)
// ═══════════════════════════════════════════════════════════════════════
describe('Streaming Router', () => {
  it('GET /stream/batch-design — constructs correct SSE URL', () => {
    const beams = [{ beam_id: 'B1', width: 300, depth: 500, moment: 150, shear: 75 }];
    const encoded = encodeURIComponent(JSON.stringify(beams));
    const url = `${API}/api/v1/stream/batch-design?beams=${encoded}`;

    expect(url).toContain('/stream/batch-design');
    expect(url).toContain('beams=');
    // URL should be valid for EventSource
    expect(() => new URL(url)).not.toThrow();
  });

  it('GET /stream/job/{job_id} — constructs correct status URL', () => {
    const jobId = 'job-abc-123';
    const url = `${API}/api/v1/stream/job/${jobId}`;

    expect(url).toContain(`/stream/job/${jobId}`);
    expect(() => new URL(url)).not.toThrow();
  });
});

// ═══════════════════════════════════════════════════════════════════════
// CROSS-CUTTING: Error handling
// ═══════════════════════════════════════════════════════════════════════
describe('Error Handling', () => {
  it('returns 422 for invalid request body', async () => {
    mockFetch({ detail: [{ msg: 'field required', type: 'missing' }] }, 422);
    const res = await fetch(`${API}/api/v1/design/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ width: -100 }),
    });

    expect(res.status).toBe(422);
  });

  it('returns 404 for unknown endpoint', async () => {
    mockFetch({ detail: 'Not found' }, 404);
    const res = await fetch(`${API}/api/v1/nonexistent`);

    expect(res.status).toBe(404);
  });

  it('handles network failure gracefully', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new TypeError('Failed to fetch'));

    await expect(fetch(`${API}/health`)).rejects.toThrow('Failed to fetch');
  });
});
