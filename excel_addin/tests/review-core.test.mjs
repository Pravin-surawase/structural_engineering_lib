import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";
import fs from "node:fs";
import test from "node:test";
import { ETABS_REVIEW_TABLES, projectCalculationReview, validateReviewRows } from "../review-core.mjs";

const fixture = () => JSON.parse(fs.readFileSync(new URL("./fixtures/calculation-review-reinforcement-v2.json", import.meta.url), "utf8"));
test("Python-produced review fixture projects complete same-row signed evidence", async () => {
  const transport = fixture();
  const projection = await projectCalculationReview(transport, { cryptoImpl: webcrypto });
  const source = JSON.parse(JSON.parse(transport.dossier_json).request.artifacts.find((artifact) => artifact.kind === "DEMAND").canonical_json.value);
  const stations = new Map(source.request.baseline.results.flatMap((result) => result.stations).map((row) => [row.station_id, row]));
  assert.equal(Object.keys(projection.tables).length, 16);
  assert.equal(projection.tables.json.map((row) => row[5]).join(""), transport.dossier_json);
  assert.equal(projection.tables.patterns.length, 1);
  assert.equal(projection.tables.cases.length, 2);
  assert.equal(projection.tables.combinations.length, 2);
  assert.equal(projection.tables.factors.length, 4);
  for (const row of projection.tables.governing) {
    const station = stations.get(row[8]);
    assert.deepEqual(row.slice(15), [station.p_kn, station.v2_kn, station.v3_kn, station.t_knm, station.m2_knm, station.m3_knm]);
    assert.equal(row[9], station.selection.name);
  }
  assert.equal(projection.tables.checks.length, 12);
  assert.ok(projection.tables.checks.some((row) => row[2] === "serviceability" && row[3] !== "PRESENT"));
  assert.equal(projection.projectedRows, validateReviewRows(projection.tables));
  for (const [key, spec] of Object.entries(ETABS_REVIEW_TABLES)) assert.ok(projection.tables[key].every((row) => row.length === spec.headers.length));
});

for (const field of ["dossier_content_sha256", "dossier_utf8_bytes", "request_json", "scope_json"]) test(`Review rejects corrupted ${field} before publication`, async () => {
  const value = fixture();
  value[field] = field.endsWith("bytes") ? 1 : "changed";
  await assert.rejects(projectCalculationReview(value, { cryptoImpl: webcrypto }), /mismatch|verification/);
});

test("Review never accepts a professional-approval claim or silent truncation", async () => {
  const value = fixture();
  value.professional_approval = "APPROVED";
  await assert.rejects(projectCalculationReview(value, { cryptoImpl: webcrypto }), /approval claim/);
  const projection = await projectCalculationReview(fixture(), { cryptoImpl: webcrypto });
  projection.tables.comments[0][5] = "x".repeat(30001);
  assert.throws(() => validateReviewRows(projection.tables), /limit exceeded/);
});
