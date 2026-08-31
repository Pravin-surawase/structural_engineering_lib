import assert from "node:assert/strict";
import { createHash, webcrypto } from "node:crypto";
import test from "node:test";
import fs from "node:fs";
import { ETABS_REVIEW_TABLES, projectCalculationReview } from "../review-core.mjs";

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
  writeCalculationReview,
  verifyCalculationReview,
  readCalculationReviewComments,
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

function baselineProjection({ chunks = ["literal-json"] } = {}) {
  const hashBasisJson = chunks.join("");
  const baselineSha256 = createHash("sha256").update(hashBasisJson).digest("hex");
  const tables = Object.fromEntries(
    Object.entries(ETABS_BASELINE_TABLES).map(([key, spec]) => [
      key,
      [spec.headers.map((_, index) => (index === 0 ? `${key}:1` : null))],
    ]),
  );
  tables.summary[0][0] = baselineSha256;
  tables.frames[0][6] = 6437.202640387113;
  tables.frames[0][20] = "";
  tables.json = chunks.map((chunk, index) => [
    `${baselineSha256}:${String(index + 1).padStart(6, "0")}`,
    baselineSha256,
    index + 1,
    chunks.length,
    Buffer.byteLength(hashBasisJson),
    chunk,
  ]);
  return {
    baselineSha256,
    hashBasisJson,
    projectedRows: 6 + chunks.length,
    tables,
  };
}

function stringCell(value) {
  return { type: "String", basicValue: value };
}

function emptyCell() {
  return { type: "Empty" };
}

function cloneCells(rows) {
  return rows.map((row) => row.map((cell) => ({ ...cell })));
}

function primitiveCell(cell) {
  if (cell?.type === "Empty") return null;
  return cell?.basicValue ?? cell;
}

function excelExpected(rows) {
  return rows.map((row) => row.map((value) => {
    if (value === "") return null;
    if (typeof value === "number" && Number.isFinite(value)) {
      return Number(value.toPrecision(15));
    }
    return value;
  }));
}

function baselineExcel({
  specifications = ETABS_BASELINE_TABLES,
  existing = false,
  missingTableKey = null,
  wrongHeaderKey = null,
  failJsonWrite = false,
} = {}) {
  const calls = [];
  const sheets = new Map();
  let pendingSyncError = null;
  let jsonFailureConsumed = false;
  const keyBySheet = new Map(
    Object.entries(specifications).map(([key, spec]) => [spec.sheetName, key]),
  );

  function ensureCellGrid(sheet, rowCount, columnCount) {
    while (sheet.cells.length < rowCount) sheet.cells.push([]);
    for (let row = 0; row < rowCount; row += 1) {
      while (sheet.cells[row].length < columnCount) sheet.cells[row].push(emptyCell());
    }
  }

  function readCells(sheet, rowIndex, columnIndex, rowCount, columnCount) {
    ensureCellGrid(sheet, rowIndex + rowCount, columnIndex + columnCount);
    return Array.from({ length: rowCount }, (_, rowOffset) =>
      Array.from({ length: columnCount }, (_, columnOffset) => ({
        ...sheet.cells[rowIndex + rowOffset][columnIndex + columnOffset],
      })),
    );
  }

  function writeCells(sheet, rowIndex, columnIndex, values) {
    ensureCellGrid(sheet, rowIndex + values.length, columnIndex + (values[0]?.length ?? 0));
    values.forEach((row, rowOffset) => {
      row.forEach((cell, columnOffset) => {
        if (cell.type === "String" && cell.basicValue === "") {
          sheet.cells[rowIndex + rowOffset][columnIndex + columnOffset] = emptyCell();
        } else if (cell.type === "Double") {
          sheet.cells[rowIndex + rowOffset][columnIndex + columnOffset] = {
            ...cell,
            basicValue: Number(cell.basicValue.toPrecision(15)),
          };
        } else {
          sheet.cells[rowIndex + rowOffset][columnIndex + columnOffset] = { ...cell };
        }
      });
    });
  }

  function makeSheet(name, exists) {
    const key = keyBySheet.get(name);
    const spec = specifications[key];
    const originalRows = [
      spec.headers.map((_, index) => (index === 0 ? `original:${key}:1` : null)),
      spec.headers.map((_, index) => (index === 0 ? `original:${key}:2` : null)),
    ];
    const initialHeader = wrongHeaderKey === key ? ["Wrong"] : [...spec.headers];
    const initialMatrix = [initialHeader, ...originalRows].map((row) =>
      row.map((value) => (value === null ? emptyCell() : stringCell(value))),
    );
    const sheet = {
      exists,
      tableExists: exists && missingTableKey !== key,
      tableName: exists && missingTableKey !== key ? spec.tableName : null,
      tableRowCount: exists && missingTableKey !== key ? initialMatrix.length : 0,
      cells: exists ? cloneCells(initialMatrix) : [],
      ranges: [],
    };

    function makeRange(rowIndex, columnIndex, rowCount, columnCount) {
      const range = {
        args: [rowIndex, columnIndex, rowCount, columnCount],
        rowIndex,
        columnIndex,
        rowCount,
        columnCount,
        load(properties) { calls.push(["range.load", key, properties]); },
      };
      Object.defineProperty(range, "valuesAsJson", {
        get() {
          return readCells(sheet, rowIndex, columnIndex, rowCount, columnCount);
        },
        set(values) {
          calls.push(["valuesAsJson", key, values.length]);
          writeCells(sheet, rowIndex, columnIndex, values);
          if (key === "json" && failJsonWrite && !jsonFailureConsumed) {
            jsonFailureConsumed = true;
            pendingSyncError = new Error("Injected ETABS_W2_JSON write failure");
          }
        },
      });
      Object.defineProperty(range, "values", {
        get() {
          return readCells(sheet, rowIndex, columnIndex, rowCount, columnCount)
            .map((row) => row.map(primitiveCell));
        },
        set(values) {
          calls.push(["unsafe.values", key]);
          const converted = values.map((row) => row.map((value) => {
            if (typeof value === "string" && /^[+=-]/.test(value)) {
              return stringCell("#FORMULA_INTERPRETED");
            }
            return value === null ? emptyCell() : stringCell(value);
          }));
          writeCells(sheet, rowIndex, columnIndex, converted);
        },
      });
      sheet.ranges.push(range);
      return range;
    }

    const table = {
      get isNullObject() { return !sheet.tableExists; },
      get name() { return sheet.tableName; },
      set name(value) { sheet.tableName = value; },
      load(property) { calls.push(["table.load", key, property]); },
      getHeaderRowRange() {
        return makeRange(0, 0, 1, spec.headers.length);
      },
      getRange() {
        return makeRange(0, 0, sheet.tableRowCount, spec.headers.length);
      },
      resize(range) {
        calls.push(["resize", key, range.args]);
        sheet.tableRowCount = range.rowCount;
        ensureCellGrid(sheet, range.rowCount, range.columnCount);
      },
    };
    Object.assign(sheet, {
      load(property) { calls.push(["sheet.load", key, property]); },
      getRangeByIndexes(...args) {
        calls.push(["range", key, ...args]);
        return makeRange(...args);
      },
      activate() { calls.push(["activate", key]); },
      delete() {
        calls.push(["sheet.delete", key]);
        sheet.exists = false;
        sheet.tableExists = false;
        sheet.tableName = null;
        sheet.tableRowCount = 0;
        sheet.cells = [];
      },
      tables: {
        getItemOrNullObject(tableName) {
          calls.push(["table.get", key, tableName]);
          return table;
        },
        add(range, hasHeaders) {
          calls.push(["table.add", key, range, hasHeaders]);
          sheet.tableExists = true;
          sheet.tableRowCount = range.rowCount;
          return table;
        },
      },
      table,
    });
    Object.defineProperty(sheet, "isNullObject", {
      get() { return !sheet.exists; },
    });
    return sheet;
  }

  for (const spec of Object.values(specifications)) {
    sheets.set(spec.sheetName, makeSheet(spec.sheetName, existing));
  }
  const context = {
    workbook: {
      worksheets: {
        getItem(name) { return sheets.get(name); },
        getItemOrNullObject(name) {
          calls.push(["sheet.get", keyBySheet.get(name)]);
          return sheets.get(name);
        },
        add(name) {
          const sheet = sheets.get(name);
          sheet.exists = true;
          calls.push(["sheet.add", keyBySheet.get(name)]);
          return sheet;
        },
      },
      tables: {
        getItemOrNullObject(name) {
          return [...sheets.values()].find((sheet) => sheet.tableName === name)?.table ?? { isNullObject: true, load() {} };
        },
      },
    },
    async sync() {
      calls.push(["sync"]);
      if (pendingSyncError) {
        const error = pendingSyncError;
        pendingSyncError = null;
        throw error;
      }
    },
  };
  return {
    calls,
    sheets,
    failNextJsonWrite() { failJsonWrite = true; jsonFailureConsumed = false; },
    snapshot() {
      return Object.fromEntries([...sheets.entries()].map(([name, sheet]) => [name, {
        exists: sheet.exists,
        tableExists: sheet.tableExists,
        tableName: sheet.tableName,
        tableRowCount: sheet.tableRowCount,
        cells: cloneCells(sheet.cells),
      }]));
    },
    api: { async run(callback) { return callback(context); } },
  };
}

function reviewTransport() {
  return JSON.parse(fs.readFileSync(new URL("./fixtures/calculation-review-reinforcement-v2.json", import.meta.url), "utf8"));
}

test("W3 publishes all sixteen literal tables and commits only after complete readback", async () => {
  const excel = baselineExcel({ specifications: ETABS_REVIEW_TABLES });
  const projection = await projectCalculationReview(reviewTransport(), { cryptoImpl: webcrypto });
  const result = await writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto });
  assert.equal(result.sheets.length, 16);
  assert.equal(result.verifiedHashBasisUtf8Bytes, reviewTransport().dossier_utf8_bytes);
  assert.equal(result.verifiedProjectedRows, projection.projectedRows);
  assert.equal(excel.calls.some(([name]) => name === "unsafe.values"), false);
  const checked = await verifyCalculationReview(excel.api, projection, { cryptoImpl: webcrypto });
  assert.equal(checked.publication, "COMMITTED");
  assert.equal(checked.professionalApproval, "NOT_PROVIDED");
});

test("W3 same-dossier refresh retains user comments and export binds the revision", async () => {
  const excel = baselineExcel({ specifications: ETABS_REVIEW_TABLES });
  const projection = await projectCalculationReview(reviewTransport(), { cryptoImpl: webcrypto });
  await writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto });
  const sheet = excel.sheets.get(ETABS_REVIEW_TABLES.comments.sheetName);
  sheet.cells[1][5] = stringCell("=This is a literal user comment, not approval");
  sheet.cells[1][4] = stringCell("HOLD");
  await writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto });
  const comments = await readCalculationReviewComments(excel.api);
  assert.equal(comments.rows[0][1], projection.dossierSha256);
  assert.equal(comments.rows[0][5], "=This is a literal user comment, not approval");
  assert.equal(projection.tables.comments[0][5], "");
  assert.equal((await verifyCalculationReview(excel.api, projection, { cryptoImpl: webcrypto })).publication, "COMMITTED");
});

test("W3 failure removes all newly created sheets and never leaves COMMITTED output", async () => {
  const excel = baselineExcel({ specifications: ETABS_REVIEW_TABLES, failJsonWrite: true });
  const projection = await projectCalculationReview(reviewTransport(), { cryptoImpl: webcrypto });
  await assert.rejects(writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto }), /Injected/);
  assert.ok([...excel.sheets.values()].every((sheet) => !sheet.exists));
});

test("W3 failed refresh restores every table and prior user comment exactly", async () => {
  const excel = baselineExcel({ specifications: ETABS_REVIEW_TABLES });
  const projection = await projectCalculationReview(reviewTransport(), { cryptoImpl: webcrypto });
  await writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto });
  excel.sheets.get(ETABS_REVIEW_TABLES.comments.sheetName).cells[1][5] = stringCell("-KEEP");
  const before = excel.snapshot();
  excel.failNextJsonWrite();
  await assert.rejects(writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto }), /Injected/);
  assert.deepEqual(excel.snapshot(), before);
});

test("W3 collision and wrong revision stop before mutation", async () => {
  const excel = baselineExcel({ specifications: ETABS_REVIEW_TABLES });
  const projection = await projectCalculationReview(reviewTransport(), { cryptoImpl: webcrypto });
  await writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto });
  const before = excel.snapshot();
  const other = structuredClone(projection);
  other.dossierSha256 = "f".repeat(64);
  await assert.rejects(writeCalculationReview(excel.api, other, { cryptoImpl: webcrypto }), /exact next revision/);
  assert.deepEqual(excel.snapshot(), before);
  excel.sheets.get(ETABS_REVIEW_TABLES.governing.sheetName).cells[0][0] = stringCell("USER HEADER");
  await assert.rejects(writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto }), /headers/);
});

test("W3 readback rejects changed signed governing actions", async () => {
  const excel = baselineExcel({ specifications: ETABS_REVIEW_TABLES });
  const projection = await projectCalculationReview(reviewTransport(), { cryptoImpl: webcrypto });
  await writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto });
  excel.sheets.get(ETABS_REVIEW_TABLES.governing.sheetName).cells[1][20] = { type: "Double", basicValue: 999 };
  await assert.rejects(verifyCalculationReview(excel.api, projection, { cryptoImpl: webcrypto }), /read-back/);
});

test("W3 refuses tampered revision history before a refresh", async () => {
  const excel = baselineExcel({ specifications: ETABS_REVIEW_TABLES });
  const projection = await projectCalculationReview(reviewTransport(), { cryptoImpl: webcrypto });
  await writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto });
  excel.sheets.get(ETABS_REVIEW_TABLES.revisions.sheetName).cells[1][5] = stringCell("f".repeat(64));
  const before = excel.snapshot();
  await assert.rejects(writeCalculationReview(excel.api, projection, { cryptoImpl: webcrypto }), /revision history/);
  assert.deepEqual(excel.snapshot(), before);
});

test("W2 baseline creates only all seven controlled tables", async () => {
  const excel = baselineExcel();
  const projection = baselineProjection();

  const result = await writeEtabsBaselineResults(
    excel.api,
    projection,
    { cryptoImpl: webcrypto },
  );

  assert.equal(result.disposition, "CREATED");
  assert.equal(result.baselineSha256, projection.baselineSha256);
  assert.equal(result.verifiedProjectedRows, projection.projectedRows);
  assert.equal(result.verifiedHashBasisUtf8Bytes, Buffer.byteLength(projection.hashBasisJson));
  assert.equal(result.sheets.length, 7);
  assert.equal(excel.calls.filter(([name]) => name === "sheet.add").length, 7);
  for (const [key, spec] of Object.entries(ETABS_BASELINE_TABLES)) {
    const sheet = excel.sheets.get(spec.sheetName);
    assert.equal(sheet.table.name, spec.tableName);
    assert.deepEqual(
      sheet.table.getRange().values,
      excelExpected([spec.headers, ...projection.tables[key]]),
    );
  }
  assert.equal(excel.calls.some(([name]) => name === "unsafe.values"), false);
  assert.equal(
    excel.sheets.get(ETABS_BASELINE_TABLES.frames.sheetName).table
      .getRange().values[1][20],
    null,
  );
  assert.equal(
    excel.sheets.get(ETABS_BASELINE_TABLES.frames.sheetName).table
      .getRange().values[1][6],
    6437.20264038711,
  );
});

test("W2 baseline keeps an empty controlled table header-only", async () => {
  const excel = baselineExcel();
  const projection = baselineProjection();
  projection.tables.connectivity = [];
  projection.projectedRows = 6;

  await writeEtabsBaselineResults(excel.api, projection, { cryptoImpl: webcrypto });

  const spec = ETABS_BASELINE_TABLES.connectivity;
  const sheet = excel.sheets.get(spec.sheetName);
  assert.deepEqual(sheet.table.getRange().values, [spec.headers]);
  assert.equal(sheet.tableRowCount, 1);
});

test("W2 JSON chunks preserve leading plus, minus, and equals as exact text", async () => {
  const excel = baselineExcel();
  const projection = baselineProjection({ chunks: ["+alpha", "-beta", "=gamma"] });

  const result = await writeEtabsBaselineResults(
    excel.api,
    projection,
    { cryptoImpl: webcrypto },
  );

  const jsonSheet = excel.sheets.get(ETABS_BASELINE_TABLES.json.sheetName);
  const jsonCells = jsonSheet.table.getRange().valuesAsJson.slice(1);
  assert.deepEqual(jsonCells.map((row) => row[5]), [
    stringCell("+alpha"),
    stringCell("-beta"),
    stringCell("=gamma"),
  ]);
  assert.equal(jsonCells.map((row) => row[5].basicValue).join(""), projection.hashBasisJson);
  assert.equal(result.baselineSha256, projection.baselineSha256);
  assert.equal(excel.calls.some(([name]) => name === "unsafe.values"), false);
});

test("W2 transaction removes every new controlled output after a JSON failure", async () => {
  const excel = baselineExcel({ failJsonWrite: true });

  await assert.rejects(
    writeEtabsBaselineResults(
      excel.api,
      baselineProjection({ chunks: ["+fails"] }),
      { cryptoImpl: webcrypto },
    ),
    /Injected ETABS_W2_JSON write failure/,
  );

  for (const spec of Object.values(ETABS_BASELINE_TABLES)) {
    const sheet = excel.sheets.get(spec.sheetName);
    assert.equal(sheet.exists, false);
    assert.equal(sheet.tableExists, false);
  }
});

test("W2 transaction exactly restores pre-existing controlled tables after failure", async () => {
  const excel = baselineExcel({ existing: true, failJsonWrite: true });
  const before = excel.snapshot();

  await assert.rejects(
    writeEtabsBaselineResults(
      excel.api,
      baselineProjection({ chunks: ["=fails", "+again"] }),
      { cryptoImpl: webcrypto },
    ),
    /Injected ETABS_W2_JSON write failure/,
  );

  assert.deepEqual(excel.snapshot(), before);
});

test("W2 baseline preflights every collision before changing cells", async () => {
  const missing = baselineExcel({ existing: true, missingTableKey: "stations" });
  await assert.rejects(
    writeEtabsBaselineResults(
      missing.api,
      baselineProjection(),
      { cryptoImpl: webcrypto },
    ),
    /ETABS_W2_Stations already exists without tbl_ETABS_W2_Stations_V1/,
  );
  assert.equal(missing.calls.some(([name]) => name === "resize"), false);
  assert.equal(missing.calls.some(([name]) => name === "sheet.add"), false);

  const changed = baselineExcel({ existing: true, wrongHeaderKey: "frames" });
  await assert.rejects(
    writeEtabsBaselineResults(
      changed.api,
      baselineProjection(),
      { cryptoImpl: webcrypto },
    ),
    /ETABS_W2_Frames headers do not match/,
  );
  assert.equal(changed.calls.some(([name]) => name === "resize"), false);
});
