import assert from "node:assert/strict";
import test from "node:test";

import {
  ETABS_BASELINE_TABLES,
  ETABS_PILOT_HEADERS,
  SETTINGS_KEYS,
} from "../taskpane-core.mjs";
import {
  ensureWorkbookId,
  inspectWorkbookSurface,
  officeErrorDetail,
  registerWorksheetChange,
  writeEtabsBaselineResults,
  writeEtabsPilotResults,
} from "../taskpane-office.mjs";

function surfaceExcel(
  { missingSheet = false, missingTable = false, syncError = null } = {},
) {
  const calls = [];
  const table = {
    isNullObject: missingTable,
    load(property) {
      calls.push(["table.load", property]);
    },
  };
  const sheet = {
    isNullObject: missingSheet,
    load(property) {
      calls.push(["sheet.load", property]);
    },
    tables: {
      getItemOrNullObject(name) {
        calls.push(["table.get", name]);
        return table;
      },
    },
  };
  const context = {
    workbook: {
      worksheets: {
        getItemOrNullObject(name) {
          calls.push(["sheet.get", name]);
          return sheet;
        },
      },
    },
    async sync() {
      calls.push(["sync"]);
      if (syncError) throw syncError;
    },
  };
  return {
    calls,
    api: {
      async run(callback) {
        return callback(context);
      },
    },
  };
}

function officeSettings({ initialId = null, saveError = null } = {}) {
  const values = new Map();
  const calls = [];
  if (initialId) values.set(SETTINGS_KEYS.workbookId, initialId);
  const settings = {
    get(key) {
      calls.push(["get", key]);
      return values.get(key) ?? null;
    },
    set(key, value) {
      calls.push(["set", key, value]);
      values.set(key, value);
    },
    saveAsync(callback) {
      calls.push(["save"]);
      callback(
        saveError
          ? { status: "failed", error: saveError }
          : { status: "succeeded" },
      );
    },
  };
  return {
    calls,
    api: {
      AsyncResultStatus: { Failed: "failed" },
      context: { document: { settings } },
    },
  };
}

test("missing worksheet is an expected unavailable blank-workbook state", async () => {
  const excel = surfaceExcel({ missingSheet: true });
  const result = await inspectWorkbookSurface(excel.api, {
    worksheetName: "Beam_Workbench",
    tableName: "tbl_Beam_Workbench_V1",
  });
  assert.deepEqual(result, {
    available: false,
    missing: "worksheet",
    detail:
      "Open the packaged E1 workbook containing Beam_Workbench / tbl_Beam_Workbench_V1.",
  });
  assert.equal(excel.calls.some(([name]) => name === "table.get"), false);
});

test("missing table is an expected unavailable workbook state", async () => {
  const excel = surfaceExcel({ missingTable: true });
  const result = await inspectWorkbookSurface(excel.api, {
    worksheetName: "Beam_Workbench",
    tableName: "tbl_Beam_Workbench_V1",
  });
  assert.equal(result.available, false);
  assert.equal(result.missing, "table");
  assert.match(result.detail, /tbl_Beam_Workbench_V1 is missing/);
});

test("complete E1 surface is accepted without mutating the workbook", async () => {
  const excel = surfaceExcel();
  const result = await inspectWorkbookSurface(excel.api, {
    worksheetName: "Beam_Workbench",
    tableName: "tbl_Beam_Workbench_V1",
  });
  assert.deepEqual(result, { available: true, missing: null, detail: "" });
  assert.deepEqual(
    excel.calls.filter(([name]) => name === "sync"),
    [["sync"], ["sync"]],
  );
});

test("missing workbook ID is created and saved after surface acceptance", async () => {
  const office = officeSettings();
  const workbookId = await ensureWorkbookId(
    office.api,
    SETTINGS_KEYS.workbookId,
    () => "fixed id",
  );
  assert.equal(workbookId, "EXCEL-fixed-id");
  assert.deepEqual(office.calls, [
    ["get", SETTINGS_KEYS.workbookId],
    ["set", SETTINGS_KEYS.workbookId, "EXCEL-fixed-id"],
    ["save"],
  ]);
});

test("existing workbook ID is reused without a settings write", async () => {
  const office = officeSettings({ initialId: "EXCEL-existing" });
  assert.equal(
    await ensureWorkbookId(office.api, SETTINGS_KEYS.workbookId),
    "EXCEL-existing",
  );
  assert.deepEqual(office.calls, [["get", SETTINGS_KEYS.workbookId]]);
});

test("settings save failure preserves Office code and debug location", async () => {
  const office = officeSettings({
    saveError: {
      message: "Settings are read-only",
      code: "PermissionDenied",
      debugInfo: { errorLocation: "Office.Settings.saveAsync" },
    },
  });
  await assert.rejects(
    ensureWorkbookId(
      office.api,
      SETTINGS_KEYS.workbookId,
      () => "fixed",
    ),
    (error) => {
      assert.equal(error.code, "PermissionDenied");
      assert.equal(error.debugInfo.errorLocation, "Office.Settings.saveAsync");
      assert.match(officeErrorDetail(error), /PermissionDenied/);
      return true;
    },
  );
});

test("unexpected workbook sync failure remains a blocking Office error", async () => {
  const syncError = Object.assign(new Error("The request was rejected"), {
    code: "AccessDenied",
    debugInfo: { errorLocation: "WorksheetCollection.getItemOrNullObject" },
  });
  const excel = surfaceExcel({ syncError });
  await assert.rejects(
    inspectWorkbookSurface(excel.api, {
      worksheetName: "Beam_Workbench",
      tableName: "tbl_Beam_Workbench_V1",
    }),
    (error) => error === syncError,
  );
});

test("change handler registration remains strict after surface acceptance", async () => {
  const calls = [];
  const handler = () => {};
  const excelApi = {
    async run(callback) {
      return callback({
        workbook: {
          worksheets: {
            getItem(name) {
              calls.push(["getItem", name]);
              return {
                onChanged: {
                  add(value) {
                    calls.push(["add", value]);
                  },
                },
              };
            },
          },
        },
        async sync() {
          calls.push(["sync"]);
        },
      });
    },
  };
  await registerWorksheetChange(excelApi, {
    worksheetName: "Beam_Workbench",
    handler,
  });
  assert.deepEqual(calls, [
    ["getItem", "Beam_Workbench"],
    ["add", handler],
    ["sync"],
  ]);
});

function pilotRow(label = "B1") {
  return ETABS_PILOT_HEADERS.map((_, index) => (index === 0 ? label : null));
}

function pilotExcel({ existingSheet = false, existingTable = true, wrongHeaders = false } = {}) {
  const calls = [];
  const body = {};
  const header = {
    values: [wrongHeaders ? ["Wrong"] : [...ETABS_PILOT_HEADERS]],
    rowIndex: 0,
    columnIndex: 0,
    columnCount: ETABS_PILOT_HEADERS.length,
    load(properties) { calls.push(["header.load", properties]); },
  };
  const table = {
    isNullObject: !existingTable,
    name: null,
    load(property) { calls.push(["table.load", property]); },
    getHeaderRowRange() { return header; },
    getDataBodyRange() { return body; },
    resize(range) { calls.push(["table.resize", range]); },
  };
  const createdRange = {};
  const sheet = {
    isNullObject: !existingSheet,
    load(property) { calls.push(["sheet.load", property]); },
    getRangeByIndexes(...args) {
      calls.push(["range", ...args]);
      return existingSheet ? { args } : createdRange;
    },
    activate() { calls.push(["activate"]); },
    tables: {
      getItemOrNullObject(name) { calls.push(["table.get", name]); return table; },
      add(range, hasHeaders) { calls.push(["table.add", range, hasHeaders]); return table; },
    },
  };
  const context = {
    workbook: {
      worksheets: {
        getItemOrNullObject(name) { calls.push(["sheet.get", name]); return sheet; },
        add(name) { calls.push(["sheet.add", name]); sheet.isNullObject = false; return sheet; },
      },
    },
    async sync() { calls.push(["sync"]); },
  };
  return {
    calls,
    body,
    createdRange,
    table,
    api: { async run(callback) { return callback(context); } },
  };
}

test("ETABS pilot creates only its controlled sheet and named table", async () => {
  const excel = pilotExcel();
  const row = pilotRow();
  const result = await writeEtabsPilotResults(excel.api, [row]);
  assert.deepEqual(result, { disposition: "CREATED", sheetName: "ETABS_Pilot" });
  assert.deepEqual(excel.createdRange.values, [ETABS_PILOT_HEADERS, row]);
  assert.equal(excel.table.name, "tbl_ETABS_Pilot_V1");
  assert.equal(excel.calls.some(([name]) => name === "sheet.add"), true);
});

test("ETABS pilot updates only an exact existing V1 table", async () => {
  const excel = pilotExcel({ existingSheet: true });
  const row = pilotRow("B2");
  const result = await writeEtabsPilotResults(excel.api, [row]);
  assert.deepEqual(result, { disposition: "UPDATED", sheetName: "ETABS_Pilot" });
  assert.deepEqual(excel.body.values, [row]);
  assert.equal(excel.calls.some(([name]) => name === "table.resize"), true);
});

test("ETABS pilot never overwrites a colliding user worksheet", async () => {
  const missing = pilotExcel({ existingSheet: true, existingTable: false });
  await assert.rejects(
    writeEtabsPilotResults(missing.api, [pilotRow()]),
    /already exists without tbl_ETABS_Pilot_V1/,
  );
  const changed = pilotExcel({ existingSheet: true, wrongHeaders: true });
  await assert.rejects(
    writeEtabsPilotResults(changed.api, [pilotRow()]),
    /headers do not match V1/,
  );
});

function baselineProjection() {
  const tables = Object.fromEntries(
    Object.entries(ETABS_BASELINE_TABLES).map(([key, spec]) => [
      key,
      [spec.headers.map((_, index) => (index === 0 ? `${key}:1` : null))],
    ]),
  );
  return { baselineSha256: "a".repeat(64), projectedRows: 7, tables };
}

function baselineExcel({ existing = false, missingTableKey = null, wrongHeaderKey = null } = {}) {
  const calls = [];
  const sheets = new Map();
  const keyBySheet = new Map(
    Object.entries(ETABS_BASELINE_TABLES).map(([key, spec]) => [spec.sheetName, key]),
  );

  function makeSheet(name, exists) {
    const key = keyBySheet.get(name);
    const spec = ETABS_BASELINE_TABLES[key];
    const body = {};
    const header = {
      values: [wrongHeaderKey === key ? ["Wrong"] : [...spec.headers]],
      rowIndex: 0,
      columnIndex: 0,
      columnCount: spec.headers.length,
      load(properties) { calls.push(["header.load", key, properties]); },
    };
    const table = {
      isNullObject: missingTableKey === key,
      name: null,
      load(property) { calls.push(["table.load", key, property]); },
      getHeaderRowRange() { return header; },
      getDataBodyRange() { return body; },
      resize(range) { calls.push(["resize", key, range]); },
    };
    const sheet = {
      isNullObject: !exists,
      body,
      table,
      ranges: [],
      load(property) { calls.push(["sheet.load", key, property]); },
      getRangeByIndexes(...args) {
        const range = { args };
        sheet.ranges.push(range);
        calls.push(["range", key, ...args]);
        return range;
      },
      activate() { calls.push(["activate", key]); },
      tables: {
        getItemOrNullObject(tableName) {
          calls.push(["table.get", key, tableName]);
          return table;
        },
        add(range, hasHeaders) {
          calls.push(["table.add", key, range, hasHeaders]);
          return table;
        },
      },
    };
    return sheet;
  }

  for (const spec of Object.values(ETABS_BASELINE_TABLES)) {
    sheets.set(spec.sheetName, makeSheet(spec.sheetName, existing));
  }
  const context = {
    workbook: {
      worksheets: {
        getItemOrNullObject(name) {
          calls.push(["sheet.get", keyBySheet.get(name)]);
          return sheets.get(name);
        },
        add(name) {
          const sheet = sheets.get(name);
          sheet.isNullObject = false;
          calls.push(["sheet.add", keyBySheet.get(name)]);
          return sheet;
        },
      },
    },
    async sync() { calls.push(["sync"]); },
  };
  return {
    calls,
    sheets,
    api: { async run(callback) { return callback(context); } },
  };
}

test("W2 baseline creates only all seven controlled tables", async () => {
  const excel = baselineExcel();
  const projection = baselineProjection();

  const result = await writeEtabsBaselineResults(excel.api, projection);

  assert.equal(result.disposition, "CREATED");
  assert.equal(result.baselineSha256, projection.baselineSha256);
  assert.equal(result.sheets.length, 7);
  assert.equal(excel.calls.filter(([name]) => name === "sheet.add").length, 7);
  for (const [key, spec] of Object.entries(ETABS_BASELINE_TABLES)) {
    const sheet = excel.sheets.get(spec.sheetName);
    assert.equal(sheet.table.name, spec.tableName);
    assert.deepEqual(sheet.ranges[0].values, [spec.headers, ...projection.tables[key]]);
  }
});

test("W2 baseline keeps an empty controlled table header-only", async () => {
  const excel = baselineExcel();
  const projection = baselineProjection();
  projection.tables.connectivity = [];
  projection.projectedRows = 6;

  await writeEtabsBaselineResults(excel.api, projection);

  const spec = ETABS_BASELINE_TABLES.connectivity;
  const sheet = excel.sheets.get(spec.sheetName);
  assert.deepEqual(sheet.ranges[0].values, [spec.headers]);
  assert.equal(sheet.ranges[0].args[2], 1);
});

test("W2 baseline preflights every collision before changing cells", async () => {
  const missing = baselineExcel({ existing: true, missingTableKey: "stations" });
  await assert.rejects(
    writeEtabsBaselineResults(missing.api, baselineProjection()),
    /ETABS_W2_Stations already exists without tbl_ETABS_W2_Stations_V1/,
  );
  assert.equal(missing.calls.some(([name]) => name === "resize"), false);
  assert.equal(missing.calls.some(([name]) => name === "sheet.add"), false);

  const changed = baselineExcel({ existing: true, wrongHeaderKey: "frames" });
  await assert.rejects(
    writeEtabsBaselineResults(changed.api, baselineProjection()),
    /ETABS_W2_Frames headers do not match/,
  );
  assert.equal(changed.calls.some(([name]) => name === "resize"), false);
});
