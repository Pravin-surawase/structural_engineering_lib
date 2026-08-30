import { sha256Hex } from "./taskpane-core.mjs";

export const REVIEW_LIMITS = Object.freeze({ bytes: 64 * 1024 * 1024, rows: 50000, cell: 30000, chunk: 15000 });
const spec = (suffix, headers) => Object.freeze({ sheetName: `ETABS_W3_${suffix}`, tableName: `tbl_ETABS_W3_${suffix}_V1`, headers: Object.freeze(headers) });
export const ETABS_REVIEW_TABLES = Object.freeze({
  summary: spec("Identity", ["Field", "State", "Value", "Reason"]),
  patterns: spec("Patterns", ["Pattern ID", "Name", "Raw type", "Type", "Self-weight multiplier", "Source ordinal"]),
  cases: spec("Cases", ["Case ID", "Name", "Raw type", "Subtype", "Design type", "Raw auto", "Auto state", "Auto", "Parameter kind", "Status ID"]),
  caseLoads: spec("CaseLoads", ["Case ID", "Ordinal", "Load type", "Load name", "Factor", "Evidence"]),
  combinations: spec("Combinations", ["Combination ID", "Name", "Raw type", "Type", "Purpose state", "Purpose", "Definition SHA-256"]),
  factors: spec("Factors", ["Combination ID", "Ordinal", "Source kind", "Source ID", "Source name", "Factor", "Evidence"]),
  statuses: spec("Statuses", ["Status ID", "Case ID", "Raw code", "State", "Getter", "Signature SHA-256", "Observed UTC"]),
  selections: spec("Selections", ["Selection ID", "Kind", "Name", "Selected state", "Selected", "Case status state", "Case status ID", "Combination state", "Combination ID"]),
  scenarios: spec("Scenarios", ["Scenario ID", "Revision", "Purpose", "Selection ID", "Station domain", "Required components", "Rule IDs", "Retained rows", "Members"]),
  governing: spec("Governing", ["Reference ID", "Scenario ID", "Member ID", "Component", "Sign", "Rule ID", "Governing value", "Concurrent", "Action row ID", "Selection name", "Object station (mm)", "Element", "Element station (mm)", "Step type", "Step number", "P (kN)", "V2 (kN)", "V3 (kN)", "T (kN.m)", "M2 (kN.m)", "M3 (kN.m)"]),
  checks: spec("Checks", ["Row ID", "Scenario ID", "Check", "Outcome state", "Outcome", "Reason", "Utilization state", "Utilization", "Clauses", "Canonical result SHA-256"]),
  holds: spec("Holds", ["Source", "State", "Reason", "Detail"]),
  attestations: spec("Attestations", ["Attestation ID", "Revision", "Dossier SHA-256", "Identity ID", "Claimed name", "Claimed role", "Decision", "Comments", "UTC", "Supersedes state", "Supersedes ID"]),
  comments: spec("Comments", ["Comment ID", "Dossier SHA-256", "Revision", "Target ID", "Disposition", "Comment", "Reviewer label", "UTC"]),
  revisions: spec("Revisions", ["Dossier SHA-256", "Revision", "Created UTC", "Supersedes state", "Supersedes SHA-256", "Content SHA-256"]),
  json: spec("JSON", ["Chunk ID", "Content SHA-256", "Index", "Count", "UTF-8 bytes", "Canonical dossier JSON chunk"]),
});

const STATES = new Set(["PRESENT", "UNAVAILABLE", "NOT_REQUESTED", "NOT_APPLICABLE", "BLOCKED"]);
function evidence(value) {
  if (!value || !STATES.has(value.state) || (value.state === "PRESENT") !== (value.value !== null && value.value !== undefined)) throw new Error("Invalid five-state evidence value.");
  return [value.state, value.state === "PRESENT" ? value.value : null, value.reason_code ?? ""];
}
function same(left, right) {
  const ordered = (value) => Array.isArray(value) ? value.map(ordered) : value && typeof value === "object" ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, ordered(value[key])])) : value;
  return JSON.stringify(ordered(left)) === JSON.stringify(ordered(right));
}
async function verifyText(text, digest, cryptoImpl) {
  if (typeof text !== "string" || !/^[a-f0-9]{64}$/.test(digest ?? "") || await sha256Hex(new TextEncoder().encode(text), { cryptoImpl }) !== digest) throw new Error("Review artifact SHA-256 verification failed.");
  return JSON.parse(text);
}
function list(value, label) {
  if (!Array.isArray(value)) throw new Error(`Missing complete ${label}.`);
  return value;
}
function oneIdMap(rows, field) {
  const map = new Map(rows.map((row) => [row[field], row]));
  if (map.size !== rows.length || rows.some((row) => typeof row[field] !== "string" || !row[field])) throw new Error(`Duplicate or missing ${field}.`);
  return map;
}
function nonempty(rows, width) { return rows.length ? rows : [Array(width).fill(null)]; }

export function validateReviewRows(tables) {
  let count = 0;
  for (const [key, definition] of Object.entries(ETABS_REVIEW_TABLES)) {
    for (const row of list(tables[key], key)) {
      if (!Array.isArray(row) || row.length !== definition.headers.length) throw new Error(`Invalid ${key} row width.`);
      for (const value of row) {
        if (value !== null && !["string", "number", "boolean"].includes(typeof value)) throw new Error(`Invalid ${key} cell type.`);
        if (typeof value === "number" && !Number.isFinite(value)) throw new Error(`Invalid ${key} number.`);
        if (typeof value === "string" && value.length > REVIEW_LIMITS.cell) throw new Error(`Review ${key} cell limit exceeded; nothing may be truncated.`);
      }
    }
    count += tables[key].length;
  }
  if (count > REVIEW_LIMITS.rows) throw new Error("Complete review exceeds 50,000 rows; nothing may be truncated.");
  return count;
}

export async function projectCalculationReview(transport, { cryptoImpl = globalThis.crypto } = {}) {
  if (transport?.schema_version !== "calculation-review-transport/v1" || transport.professional_approval !== "NOT_PROVIDED" || transport.signature_verification !== "NOT_PROVIDED") throw new Error("Unsupported review transport or approval claim.");
  const bytes = new TextEncoder().encode(transport.dossier_json ?? "");
  if (bytes.length !== transport.dossier_utf8_bytes || bytes.length > REVIEW_LIMITS.bytes) throw new Error("Review byte count/limit mismatch.");
  const dossier = await verifyText(transport.dossier_json, transport.dossier_content_sha256, cryptoImpl);
  if (dossier.schema_version !== "calculation-dossier/v1") throw new Error("Expected a provider-neutral calculation dossier.");
  const request = await verifyText(transport.request_json, dossier.dossier_sha256, cryptoImpl);
  const scope = await verifyText(transport.scope_json, dossier.scope_sha256, cryptoImpl);
  if (!same(request, dossier.request) || !same(scope, request.scope)) throw new Error("Dossier/request/scope binding mismatch.");
  const identity = request.identity;
  const artifacts = new Map();
  const identityFields = { MODEL: "model_file_sha256", CATALOGUE: "catalogue_sha256", DEMAND: "demand_sha256", CALCULATION: "calculation_sha256", REPORT: "report_sha256", WORKBOOK: "workbook_sha256", SURROGATE: "surrogate_sha256", CALIBRATION: "calibration_sha256", OPTIMIZATION: "optimization_sha256", GOVERNING_CANDIDATE: "governing_candidate_sha256" };
  for (const item of list(request.artifacts, "artifacts")) {
    const linked = identity[identityFields[item.kind]];
    if (artifacts.has(item.kind) || !linked || item.sha256 !== (typeof linked === "string" ? linked : evidence(linked)[1])) throw new Error("Dossier artifact identity mismatch.");
    const state = evidence(item.canonical_json);
    artifacts.set(item.kind, state[0] === "PRESENT" ? await verifyText(item.canonical_json.value, item.sha256, cryptoImpl) : null);
  }
  const catalogue = artifacts.get("CATALOGUE");
  const demand = artifacts.get("DEMAND");
  const calculation = artifacts.get("CALCULATION");
  if (catalogue?.schema_version !== "etabs-result-catalogue/v1" || demand?.schema_version !== "beam-demand-review/v1" || !calculation) throw new Error("Complete catalogue/demand/calculation review artifacts are required.");
  const { snapshot, request: source } = demand;
  if (!same(source.catalogue, catalogue) || !same(snapshot.scenario, source.scenario) || snapshot.catalogue_sha256 !== catalogue.catalogue_sha256 || snapshot.baseline_sha256 !== source.baseline.baseline_sha256 || snapshot.model_identity_sha256 !== identity.model_identity_sha256) throw new Error("Demand source identity mismatch.");
  const selections = oneIdMap(list(catalogue.result_selections, "selections"), "selection_id");
  const patterns = list(catalogue.load_patterns, "patterns");
  const cases = list(catalogue.load_cases, "cases");
  const combos = list(catalogue.response_combinations, "combinations");
  const statuses = list(catalogue.analysis_statuses, "statuses");
  const stationRows = list(source.baseline.results, "beam forces").flatMap((beam) => list(beam.stations, "stations"));
  const stations = oneIdMap(stationRows, "station_id");
  const scenario = snapshot.scenario;
  const selected = scenario.included_selection_ids.map((id) => { if (!selections.has(id)) throw new Error("Scenario selection missing."); return selections.get(id); });
  const retained = stationRows.filter((row) => selected.some((selection) => selection.kind === row.selection.kind && selection.name === row.selection.name) && (!scenario.member_ids.length || scenario.member_ids.includes(row.member_id)));
  if (retained.length !== snapshot.retained_action_row_count || new Set(retained.map((row) => row.member_id)).size !== snapshot.member_count) throw new Error("Complete signed station/member counts do not reconcile.");
  const rowsById = oneIdMap(retained, "station_id");
  const tables = {
    summary: [["Publication", "PRESENT", "COMMITTED", "Accepted only after complete readback"], ["Dossier SHA-256", "PRESENT", dossier.dossier_sha256, ""], ["Revision", "PRESENT", request.revision, ""], ["Dossier content SHA-256", "PRESENT", transport.dossier_content_sha256, ""], ["Dossier state", "PRESENT", dossier.state, "Claimed review state; not professional approval"], ["Software status", "PRESENT", request.software_status, ""], ["Professional approval", "NOT_APPLICABLE", "NOT_PROVIDED", "No engineering/construction approval"], ["Signature verification", "NOT_REQUESTED", "NOT_PROVIDED", "External provider/signature acceptance remains separate"], ["Source freshness", "PRESENT", "SAVED_EVIDENCE_ONLY", "No current ETABS/model state is inferred"], ...Object.entries(identity).map(([key, value]) => typeof value === "object" ? [key, ...evidence(value)] : [key, "PRESENT", value, ""]), ["Native catalogue SHA-256", "PRESENT", catalogue.catalogue_sha256, "Canonical artifact content digest is separate"], ["Native demand SHA-256", "PRESENT", snapshot.snapshot_sha256, "Canonical artifact content digest is separate"]],
    patterns: patterns.map((row) => [row.pattern_id, row.name, row.raw_type, row.normalized_type, row.self_weight_multiplier, row.source_ordinal]),
    cases: cases.map((row) => [row.case_id, row.name, row.raw_type, row.raw_subtype, row.raw_design_type, row.raw_auto_flag, ...evidence(row.is_auto).slice(0, 2), row.parameters.parameter_kind, row.analysis_status_id]),
    caseLoads: cases.flatMap((row) => (row.parameters.load_items ?? []).map((load) => [row.case_id, load.ordinal, load.load_type, load.load_name, load.scale_factor, load.evidence_reference])),
    combinations: combos.map((row) => [row.combination_id, row.name, row.raw_type, row.normalized_type, ...evidence(row.design_purpose).slice(0, 2), row.definition_sha256]),
    factors: combos.flatMap((row) => row.factors.map((factor, index) => { if (factor.ordinal !== index) throw new Error("Ordered combination factors are invalid."); return [row.combination_id, factor.ordinal, factor.source_kind, factor.source_id, factor.source_name, factor.scale_factor, factor.evidence_reference]; })),
    statuses: statuses.map((row) => [row.status_id, row.case_id, row.raw_status_code, row.state, row.getter_identity, row.signature_identity, row.observed_at_utc]),
    selections: [...selections.values()].map((row) => [row.selection_id, row.kind, row.name, ...evidence(row.selected_for_output).slice(0, 2), ...evidence(row.case_status_id).slice(0, 2), ...evidence(row.combination_definition_id).slice(0, 2)]),
    scenarios: selected.map((row) => [scenario.scenario_id, scenario.revision, scenario.purpose, row.selection_id, scenario.station_domain, scenario.required_components.join(" | "), scenario.envelope_rule_ids.join(" | "), snapshot.retained_action_row_count, snapshot.member_count]),
    governing: list(snapshot.governing_references, "governing references").flatMap((ref) => ref.action_row_ids.map((id) => {
      const row = rowsById.get(id);
      if (!row || row.member_id !== ref.member_id || ref.scenario_id !== scenario.scenario_id || (ref.is_concurrent && ref.action_row_ids.length !== 1)) throw new Error("Governing reference does not resolve to an exact signed source row.");
      if (!ref.selection_ids.some((selectionId) => { const value = selections.get(selectionId); return value?.kind === row.selection.kind && value?.name === row.selection.name; })) throw new Error("Governing selection mismatch.");
      return [ref.reference_id, ref.scenario_id, ref.member_id, ref.component, ref.sign, ref.rule_id, ref.governing_value, ref.is_concurrent, id, row.selection.name, row.object_station_mm, row.element_name, row.element_station_mm, row.step_type, row.step_number, row.p_kn, row.v2_kn, row.v3_kn, row.t_knm, row.m2_knm, row.m3_knm];
    })),
    checks: [],
    holds: [...scope.held_checks.map((text) => ["scope", "BLOCKED", "HELD_CHECK", text]), ...scope.assumptions.map((text) => ["scope", "PRESENT", "ASSUMPTION", text]), ...scope.exclusions.map((text) => ["scope", "NOT_APPLICABLE", "EXCLUSION", text]), ...scenario.held_checks.map((value) => ["scenario", value.state, value.reason_code, value.message]), ...snapshot.limitations.map((text) => ["demand", "PRESENT", "LIMITATION", text])],
    attestations: list(dossier.attestations, "attestations").map((row) => [row.attestation_id, row.revision, row.dossier_sha256, row.identity.identity_id, row.identity.person_name, row.role, row.decision, row.comments.join("\n"), row.attested_at_utc, ...evidence(row.supersedes).slice(0, 2)]),
    comments: [[`review:${dossier.dossier_sha256}`, dossier.dossier_sha256, request.revision, request.dossier_id, "PENDING", "", "", ""]],
    revisions: [[dossier.dossier_sha256, request.revision, request.created_at_utc, ...evidence(request.supersedes_dossier_sha256).slice(0, 2), transport.dossier_content_sha256]],
    json: [],
  };
  if (calculation.schema_version === "beam-audit-evaluation/v1" && calculation.status === "ACCEPTED") {
    for (const row of calculation.rows) {
      const action = row.input.action;
      const station = stations.get(action.row_id);
      if (!station || action.baseline_sha256 !== snapshot.baseline_sha256 || action.catalogue_sha256 !== catalogue.catalogue_sha256 || !["p_kn", "v2_kn", "v3_kn", "t_knm", "m2_knm", "m3_knm"].every((field) => action[field] === station[field])) throw new Error("Calculation signed source row mismatch.");
      await verifyText(row.canonical_result_json, row.canonical_result_sha256, cryptoImpl);
      tables.checks.push(...row.checks.map((check) => [check.action_row_id, check.scenario_id, check.check, ...evidence(check.outcome), ...evidence(check.utilization).slice(0, 2), check.clause_references.join(" | "), row.canonical_result_sha256]));
    }
    tables.holds.push(...calculation.limitations.map((text) => ["calculation", "PRESENT", "LIMITATION", text]));
  } else if (calculation.status === "BLOCKED" && calculation.inputs === null && calculation.issues?.length && request.software_status === "HOLD") {
    tables.holds.push(...calculation.issues.map((issue) => ["calculation", "BLOCKED", issue.code, issue.message]));
  } else throw new Error("Missing calculation evidence must be explicitly blocked.");
  const chunks = [];
  for (let index = 0; index < transport.dossier_json.length; index += REVIEW_LIMITS.chunk) chunks.push(transport.dossier_json.slice(index, index + REVIEW_LIMITS.chunk));
  tables.json = chunks.map((text, index) => [`chunk:${index}`, transport.dossier_content_sha256, index, chunks.length, bytes.length, text]);
  tables.summary.push(["Review history SHA-256", "PRESENT", await sha256Hex(new TextEncoder().encode(JSON.stringify(tables.revisions)), { cryptoImpl }), "Append-only workbook revision identities"]);
  for (const [key, definition] of Object.entries(ETABS_REVIEW_TABLES)) tables[key] = nonempty(tables[key], definition.headers.length);
  return { baselineSha256: transport.dossier_content_sha256, hashBasisJson: transport.dossier_json, tables, projectedRows: validateReviewRows(tables), dossierSha256: dossier.dossier_sha256, revision: request.revision, supersedes: request.supersedes_dossier_sha256 };
}
