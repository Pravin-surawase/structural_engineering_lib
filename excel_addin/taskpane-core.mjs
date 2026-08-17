const TEMPLATE = Object.freeze({
  template_id: "structural-lib-rectangular-beam-workbench",
  template_version: "1.0",
  worksheet_name: "Beam_Workbench",
  table_name: "tbl_Beam_Workbench_V1",
});

export const SETTINGS_KEYS = Object.freeze({
  workbookId: "excel_workbench_v1.workbook_instance_id",
  previousEvidence: "excel_workbench_v1.previous_evidence",
  stale: "excel_workbench_v1.stale",
});

export function normalizeCalculationMode(value) {
  const key = String(value ?? "").replaceAll("_", "").toLowerCase();
  if (key === "automatic") return "AUTOMATIC";
  if (key === "manual") return "MANUAL";
  if (
    key === "automaticexcepttables" ||
    key === "automaticexceptdatatables"
  ) {
    return "AUTOMATIC_EXCEPT_TABLES";
  }
  throw new Error(`Unsupported Excel calculation mode: ${value}`);
}

export function buildPreviewRequest({
  workbookInstanceId,
  headers,
  rows,
  firstDataRowNumber,
  locale,
  calculationMode,
}) {
  if (!Array.isArray(headers) || headers.length === 0) {
    throw new Error("The selected Excel table has no headers.");
  }
  if (!Array.isArray(rows)) {
    throw new Error("The selected Excel table rows are unavailable.");
  }
  return {
    schema_version: "excel-workbook-preview-request/v1",
    selection: {
      workbook_instance_id: workbookInstanceId,
      template_id: TEMPLATE.template_id,
      template_version: TEMPLATE.template_version,
      worksheet_name: TEMPLATE.worksheet_name,
      table_name: TEMPLATE.table_name,
      first_data_row_number: firstDataRowNumber,
      locale: locale || "en-IN",
      decimal_separator: ".",
      calculation_mode: normalizeCalculationMode(calculationMode),
      unit_system: "IS456",
      trust_mode: "MACRO_FREE_OFFICE_JS",
    },
    headers: [...headers],
    rows: rows.map((row) => [...row]),
  };
}

export function buildRunRequest(previewRequest, confirmedMappingHash) {
  if (!/^[0-9a-f]{64}$/.test(String(confirmedMappingHash ?? ""))) {
    throw new Error("A reviewed 64-character mapping hash is required.");
  }
  return {
    ...previewRequest,
    schema_version: "excel-workbook-run-request/v1",
    confirmed_mapping_hash: confirmedMappingHash,
  };
}

export function sameSourceSnapshot(left, right) {
  if (!left || !right) return false;
  return JSON.stringify(left) === JSON.stringify(right);
}

export function unwrapApiResponse(body) {
  if (!body || body.success !== true || body.data == null) {
    const message = body?.error?.message || "The local API rejected the request.";
    throw new Error(message);
  }
  return body.data;
}

export async function postWorkbenchApi(
  baseUrl,
  path,
  payload,
  { token = "", fetchImpl = globalThis.fetch } = {},
) {
  const root = String(baseUrl || "").replace(/\/$/, "");
  if (!root) throw new Error("The local API base URL is required.");
  const headers = { "Content-Type": "application/json", Accept: "application/json" };
  if (token.trim()) headers.Authorization = `Bearer ${token.trim()}`;
  const response = await fetchImpl(`${root}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error(`The local API returned non-JSON HTTP ${response.status}.`);
  }
  if (!response.ok) {
    throw new Error(body?.error?.message || `The local API returned HTTP ${response.status}.`);
  }
  return unwrapApiResponse(body);
}

export async function getWorkbenchApi(
  baseUrl,
  path,
  { token = "", fetchImpl = globalThis.fetch } = {},
) {
  const root = String(baseUrl || "").replace(/\/$/, "");
  if (!root) throw new Error("The local API base URL is required.");
  const headers = { Accept: "application/json" };
  if (token.trim()) headers.Authorization = `Bearer ${token.trim()}`;
  const response = await fetchImpl(`${root}${path}`, { method: "GET", headers });
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error(`The local API returned non-JSON HTTP ${response.status}.`);
  }
  if (!response.ok) {
    throw new Error(body?.error?.message || `The local API returned HTTP ${response.status}.`);
  }
  return unwrapApiResponse(body);
}

export function projectMappingRows(preview) {
  const rows = preview.mapped_fields.map((field) => [
    field.canonical_field,
    field.source_header,
    "READY",
    `Column ${field.source_column_index + 1}`,
  ]);
  for (const issue of preview.issues) {
    rows.push([issue.path, "-", "BLOCKED", `${issue.code}: ${issue.message}`]);
  }
  return rows;
}

export function projectLedgerRows(result) {
  return result.row_ledger.map((row) => [
    row.source_row_number,
    row.row_id,
    row.beam_id,
    row.disposition,
    row.issues.map((issue) => issue.code).join(", "),
    row.result_envelope?.overall_status ?? row.disposition,
    row.raw_row_hash,
    row.passport?.result_hash ?? null,
    row.passport?.passport_hash ?? null,
  ]);
}

export function projectResultRows(result) {
  return result.row_ledger
    .filter((row) => row.result != null)
    .map((row) => [
      row.row_id,
      row.beam_id,
      row.result.case_id,
      row.result.result_envelope?.overall_status ?? null,
      row.result.Mu_knm,
      row.result.Vu_kn,
      row.result.effective_depth_resolution?.d_mm ?? null,
      row.result.flexure?.Ast_required ?? null,
      row.result.shear?.is_safe === true
        ? "PASS"
        : row.result.shear?.is_safe === false
          ? "FAIL"
          : null,
      JSON.stringify(row.result),
    ]);
}

export function projectPassportRows(result) {
  return result.row_ledger
    .filter((row) => row.passport != null)
    .map((row) => [
      row.passport.row_id,
      row.passport.beam_id,
      row.passport.case_id,
      row.passport.raw_row_hash,
      row.passport.normalized_input_hash,
      row.passport.calculation_identity,
      row.passport.result_hash,
      row.passport.library_version,
      row.passport.library_content_identity,
      row.passport.workbook_selection_hash,
      row.passport.mapping_hash,
      row.passport.passport_hash,
    ]);
}

export function retainEvidence(result) {
  return {
    schema_version: "excel-retained-evidence/v1",
    bundle_hash: result.bundle_hash,
    source_table_hash: result.source_table_hash,
    mapping_hash: result.mapping.mapping_hash,
    library_content_identity: result.library_content_identity,
  };
}

export function reconciliationSummary(result) {
  const counts = result.counts;
  if (
    counts.source_rows !==
    counts.accepted_rows + counts.blocked_rows + counts.excluded_rows
  ) {
    throw new Error("The API returned a non-reconciling row count.");
  }
  return `${counts.source_rows} source = ${counts.accepted_rows} accepted + ${counts.blocked_rows} blocked + ${counts.excluded_rows} excluded`;
}
