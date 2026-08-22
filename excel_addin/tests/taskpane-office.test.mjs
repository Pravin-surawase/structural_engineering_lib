import assert from "node:assert/strict";
import test from "node:test";

import { SETTINGS_KEYS } from "../taskpane-core.mjs";
import {
  ensureWorkbookId,
  inspectWorkbookSurface,
  officeErrorDetail,
  registerWorksheetChange,
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
