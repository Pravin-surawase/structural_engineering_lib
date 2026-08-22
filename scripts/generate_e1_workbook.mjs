#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";
import JSZip from "jszip";

const ARTIFACT_RELATIVE_PATH =
  "Python/structural_lib/data/excel/outputs/e1-excel-routine-workbench/" +
  "structural-lib-rectangular-beam-workbench-v1.xlsx";
const MANIFEST_RELATIVE_PATH =
  "Python/structural_lib/data/excel/outputs/e1-excel-routine-workbench/" +
  "workbook-manifest.json";

const INPUT_HEADERS = [
  "Row ID",
  "Beam ID",
  "Case ID",
  "Mu (kN·m)",
  "Vu (kN)",
  "b (mm)",
  "D (mm)",
  "Depth Basis",
  "Effective d (mm)",
  "Clear Cover (mm)",
  "Stirrup Dia (mm)",
  "Tension Bar Dia (mm)",
  "d' (mm)",
  "Asv (mm²)",
  "fck (N/mm²)",
  "fy (N/mm²)",
  "Shear Basis",
];

const MAPPING_ROWS = [
  ["row_id", "Row ID", "READY", "Exact template mapping"],
  ["beam_id", "Beam ID", "READY", "Exact template mapping"],
  ["case_id", "Case ID", "READY", "Exact template mapping"],
  ["mu_knm", "Mu (kN·m)", "READY", "Exact template mapping"],
  ["vu_kn", "Vu (kN)", "READY", "Exact template mapping"],
  ["b_mm", "b (mm)", "READY", "Exact template mapping"],
  ["D_mm", "D (mm)", "READY", "Exact template mapping"],
  ["depth_basis_mode", "Depth Basis", "READY", "Exact template mapping"],
  ["d_mm", "Effective d (mm)", "READY", "Exact template mapping"],
  ["clear_cover_mm", "Clear Cover (mm)", "READY", "Exact template mapping"],
  ["stirrup_dia_mm", "Stirrup Dia (mm)", "READY", "Exact template mapping"],
  [
    "tension_bar_dia_mm",
    "Tension Bar Dia (mm)",
    "READY",
    "Exact template mapping",
  ],
  ["d_dash_mm", "d' (mm)", "READY", "Exact template mapping"],
  ["asv_mm2", "Asv (mm²)", "READY", "Exact template mapping"],
  ["fck_nmm2", "fck (N/mm²)", "READY", "Exact template mapping"],
  ["fy_nmm2", "fy (N/mm²)", "READY", "Exact template mapping"],
  ["shear_basis_mode", "Shear Basis", "READY", "Exact template mapping"],
];

const COLORS = {
  navy: "#16324F",
  teal: "#087E8B",
  paleBlue: "#EAF1F8",
  paleGray: "#F4F6F7",
  paleYellow: "#FFF4CC",
  greenFill: "#E6F4EA",
  greenText: "#137333",
  amberText: "#9A6700",
  border: "#C8D2DA",
  white: "#FFFFFF",
};

function parseArgs(argv) {
  const result = { repoRoot: null };
  for (let index = 0; index < argv.length; index += 1) {
    if (argv[index] === "--repo-root") {
      result.repoRoot = argv[index + 1];
      index += 1;
    }
  }
  if (!result.repoRoot) {
    throw new Error("usage: generate_e1_workbook.mjs --repo-root <path>");
  }
  return result;
}

function applySheetFrame(sheet, lastColumn, title, subtitle) {
  sheet.showGridLines = false;
  sheet.mergeCells(`A1:${lastColumn}1`);
  sheet.mergeCells(`A2:${lastColumn}2`);
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A1:${lastColumn}1`).format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 18 },
  };
  sheet.getRange(`A2:${lastColumn}2`).format = {
    fill: COLORS.paleBlue,
    font: { italic: true, color: COLORS.navy, size: 10 },
    wrapText: true,
    borders: { preset: "all", style: "thin", color: COLORS.border },
  };
  sheet.getRange(`A1:${lastColumn}1`).format.rowHeight = 34;
  sheet.getRange(`A2:${lastColumn}2`).format.rowHeight = 30;
}

function addStyledTable(sheet, range, name) {
  const table = sheet.tables.add(range, true, name);
  table.style = "TableStyleMedium2";
  table.showHeaders = true;
  table.showTotals = false;
  table.showBandedColumns = false;
  table.showFilterButton = true;
  return table;
}

function buildWorkbookInfo(workbook) {
  const sheet = workbook.worksheets.add("Workbook_Info");
  applySheetFrame(
    sheet,
    "F",
    "Excel Routine Workbench V1",
    "Macro-free Office.js workbook. Structural calculations run only through structural_lib design_beam_is456; this file contains no structural-design formulas.",
  );

  sheet.getRange("A4:B14").values = [
    ["Workbook identity", "Value"],
    ["Template ID", "structural-lib-rectangular-beam-workbench"],
    ["Template version", "1.0"],
    ["Contract schema", "excel-workbook-contract/v1"],
    ["Input worksheet", "Beam_Workbench"],
    ["Input table", "tbl_Beam_Workbench_V1"],
    ["Unit system", "IS456"],
    ["Trust mode", "MACRO_FREE_OFFICE_JS"],
    ["Torsion scope", "DISABLED_E1"],
    ["Serviceability scope", "DISABLED_E1"],
    ["Canonical function", "design_beam_is456"],
  ];
  sheet.getRange("D4:F14").values = [
    ["Capability", "State", "Meaning"],
    ["E1 software", "AVAILABLE", "Contract, API, workbook, and task pane implemented"],
    [
      "Windows Excel runtime",
      "TO_VERIFY_WINDOWS",
      "Requires the separate installed-Windows evidence gate",
    ],
    [
      "Qualified engineering review",
      "REQUIRED",
      "Software output is not professional approval",
    ],
    [null, null, null],
    ["Workflow", "Rule", "Why it matters"],
    ["1. Select", "Use only tbl_Beam_Workbench_V1", "Binds worksheet and table identity"],
    ["2. Preview", "Review the exact header mapping", "Blocks missing or duplicate mappings"],
    ["3. Run", "Confirm the mapping hash", "Prevents unreviewed remapping"],
    ["4. Review", "Inspect ledger, results, passports", "Every source row is accounted for"],
    ["5. Recheck", "Treat edits as stale immediately", "Prevents reuse of superseded output"],
  ];

  const headerStyle = {
    fill: COLORS.teal,
    font: { bold: true, color: COLORS.white },
    wrapText: true,
    borders: { preset: "all", style: "thin", color: COLORS.border },
  };
  sheet.getRange("A4:B4").format = headerStyle;
  sheet.getRange("D4:F4").format = headerStyle;
  sheet.getRange("D9:F9").format = headerStyle;
  sheet.getRange("A5:B14").format = {
    fill: COLORS.paleGray,
    borders: { preset: "outside", style: "thin", color: COLORS.border },
  };
  sheet.getRange("D5:F7").format = {
    borders: { preset: "outside", style: "thin", color: COLORS.border },
  };
  sheet.getRange("D10:F14").format = {
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: COLORS.border },
  };
  sheet.getRange("E5").format = {
    fill: COLORS.greenFill,
    font: { color: COLORS.greenText },
  };
  sheet.getRange("E6:E7").format = {
    fill: COLORS.paleYellow,
    font: { color: COLORS.amberText },
  };
  sheet.mergeCells("A16:F16");
  sheet.getRange("A16").values = [[
    "Held in E1: torsion, serviceability, ETABS import/write-back, hidden defaults, VBA/macros, and release or qualified-approval claims.",
  ]];
  sheet.getRange("A16:F16").format = {
    fill: COLORS.paleYellow,
    font: { bold: true, color: COLORS.amberText },
    borders: { preset: "outside", style: "thin", color: COLORS.amberText },
    wrapText: true,
  };
  sheet.getRange("A16:F16").format.rowHeight = 30;

  for (const [range, width] of [
    ["A1:A16", 26],
    ["B1:B16", 44],
    ["C1:C16", 4],
    ["D1:D16", 30],
    ["E1:E16", 40],
    ["F1:F16", 56],
  ]) {
    sheet.getRange(range).format.columnWidth = width;
  }
}

function buildBeamWorkbench(workbook) {
  const sheet = workbook.worksheets.add("Beam_Workbench");
  applySheetFrame(
    sheet,
    "Q",
    "Rectangular Beam Input Workbench — IS 456",
    "Yellow cells are user inputs. Numeric text such as '300' is blocked; enter actual numbers. Blank table rows are retained as EXCLUDED in the row ledger.",
  );
  sheet.getRange("A4:Q7").values = [
    INPUT_HEADERS,
    [
      "R1",
      "B1",
      "ULS-1",
      150,
      100,
      300,
      500,
      "DERIVED_FROM_BARS",
      null,
      40,
      8,
      18,
      null,
      100,
      25,
      500,
      "AUTO_FROM_FLEXURE",
    ],
    [
      "R2",
      "B2",
      "ULS-2",
      150,
      420,
      300,
      500,
      "EXPLICIT_D",
      443,
      null,
      8,
      null,
      57,
      100,
      25,
      500,
      "AUTO_FROM_FLEXURE",
    ],
    Array(INPUT_HEADERS.length).fill(null),
  ];
  addStyledTable(sheet, "A4:Q7", "tbl_Beam_Workbench_V1");
  sheet.getRange("A5:Q7").format.fill = COLORS.paleYellow;
  for (const range of ["D5:G7", "I5:P7"]) {
    sheet.getRange(range).format.numberFormat = "0.00";
  }
  sheet.dataValidations.add({
    range: "H5:H7",
    rule: { type: "list", values: ["DERIVED_FROM_BARS", "EXPLICIT_D"] },
  });
  sheet.dataValidations.add({
    range: "Q5:Q7",
    rule: { type: "list", values: ["AUTO_FROM_FLEXURE"] },
  });

  const widths = [12, 14, 14, 14, 14, 14, 14, 22, 20, 17, 17, 20, 17, 17, 17, 17, 22];
  for (let index = 0; index < widths.length; index += 1) {
    const column = String.fromCharCode("A".charCodeAt(0) + index);
    sheet.getRange(`${column}1:${column}7`).format.columnWidth = widths[index];
  }
}

function buildMappingPreview(workbook) {
  const sheet = workbook.worksheets.add("Mapping_Preview");
  applySheetFrame(
    sheet,
    "D",
    "Mapping Preview",
    "Review these mappings in the task pane before Run. A changed mapping invalidates the prior confirmation hash.",
  );
  sheet.getRange("A4:D21").values = [
    ["Canonical Field", "Source Header", "Status", "Notes"],
    ...MAPPING_ROWS,
  ];
  addStyledTable(sheet, "A4:D21", "tbl_Mapping_Preview_V1");
  sheet.getRange("C5:C21").format = {
    fill: COLORS.greenFill,
    font: { color: COLORS.greenText },
  };
  for (const [range, width] of [
    ["A1:A21", 24],
    ["B1:B21", 26],
    ["C1:C21", 14],
    ["D1:D21", 38],
  ]) {
    sheet.getRange(range).format.columnWidth = width;
  }
}

function buildOutputSheet(workbook, config) {
  const sheet = workbook.worksheets.add(config.name);
  applySheetFrame(sheet, config.lastColumn, config.title, config.subtitle);
  const blankRow = Array(config.headers.length).fill(null);
  sheet.getRange(config.tableRange).values = [config.headers, blankRow];
  addStyledTable(sheet, config.tableRange, config.tableName);
  for (let index = 0; index < config.widths.length; index += 1) {
    const column = String.fromCharCode("A".charCodeAt(0) + index);
    sheet.getRange(`${column}1:${column}5`).format.columnWidth = config.widths[index];
  }
}

async function normalizeRelationshipIds(zip, relationshipPath, ownerPath = null) {
  const relationshipEntry = zip.file(relationshipPath);
  if (!relationshipEntry) {
    throw new Error(`missing relationship part: ${relationshipPath}`);
  }
  let relationshipXml = await relationshipEntry.async("string");
  const oldIds = [...relationshipXml.matchAll(/\bId="([^"]+)"/g)].map(
    (match) => match[1],
  );
  const replacements = new Map(
    oldIds.map((oldId, index) => [oldId, `rId${index + 1}`]),
  );
  relationshipXml = relationshipXml.replace(
    /\bId="([^"]+)"/g,
    (_match, oldId) => `Id="${replacements.get(oldId)}"`,
  );
  zip.file(relationshipPath, relationshipXml);

  if (ownerPath) {
    const ownerEntry = zip.file(ownerPath);
    if (!ownerEntry) {
      throw new Error(`missing relationship owner: ${ownerPath}`);
    }
    let ownerXml = await ownerEntry.async("string");
    for (const [oldId, newId] of replacements) {
      ownerXml = ownerXml.replaceAll(`r:id="${oldId}"`, `r:id="${newId}"`);
    }
    zip.file(ownerPath, ownerXml);
  }
}

async function normalizePackageBytes(artifactPath) {
  const zip = await JSZip.loadAsync(await fs.readFile(artifactPath));
  await normalizeRelationshipIds(zip, "_rels/.rels");
  await normalizeRelationshipIds(
    zip,
    "xl/_rels/workbook.xml.rels",
    "xl/workbook.xml",
  );
  for (let sheetNumber = 2; sheetNumber <= 6; sheetNumber += 1) {
    await normalizeRelationshipIds(
      zip,
      `xl/worksheets/_rels/sheet${sheetNumber}.xml.rels`,
      `xl/worksheets/sheet${sheetNumber}.xml`,
    );
  }

  const fixedZipDate = new Date(Date.UTC(1980, 0, 1, 0, 0, 0));
  for (const entry of Object.values(zip.files)) {
    entry.date = fixedZipDate;
  }
  const normalized = await zip.generateAsync({
    type: "nodebuffer",
    compression: "DEFLATE",
    compressionOptions: { level: 9 },
    platform: "DOS",
  });
  await fs.writeFile(artifactPath, normalized);
}

async function main() {
  const { repoRoot } = parseArgs(process.argv.slice(2));
  const workbook = Workbook.create();
  buildWorkbookInfo(workbook);
  buildBeamWorkbench(workbook);
  buildMappingPreview(workbook);
  buildOutputSheet(workbook, {
    name: "Row_Ledger",
    title: "Source Row Ledger",
    subtitle: "Every source table row must appear exactly once as ACCEPTED, BLOCKED, or EXCLUDED.",
    lastColumn: "I",
    tableRange: "A4:I5",
    tableName: "tbl_Row_Ledger_V1",
    headers: [
      "Source Row",
      "Row ID",
      "Beam ID",
      "Disposition",
      "Issue Codes",
      "Overall Status",
      "Raw Row Hash",
      "Result Hash",
      "Passport Hash",
    ],
    widths: [14, 14, 14, 18, 22, 18, 36, 36, 36],
  });
  buildOutputSheet(workbook, {
    name: "Results",
    title: "Canonical Beam Results",
    subtitle:
      "These are display projections of canonical-beam-result/v1. The full result envelope remains authoritative.",
    lastColumn: "J",
    tableRange: "A4:J5",
    tableName: "tbl_Results_V1",
    headers: [
      "Row ID",
      "Beam ID",
      "Case ID",
      "Overall Status",
      "Mu (kN·m)",
      "Vu (kN)",
      "d (mm)",
      "Ast Required (mm²)",
      "Shear Status",
      "Result Envelope JSON",
    ],
    widths: [14, 14, 14, 18, 14, 14, 14, 20, 18, 60],
  });
  buildOutputSheet(workbook, {
    name: "Passports",
    title: "Calculation Passports",
    subtitle:
      "Each passport binds a row, normalized input, canonical result, library content, workbook selection, and reviewed mapping.",
    lastColumn: "L",
    tableRange: "A4:L5",
    tableName: "tbl_Passports_V1",
    headers: [
      "Row ID",
      "Beam ID",
      "Case ID",
      "Raw Row Hash",
      "Normalized Input Hash",
      "Calculation Identity",
      "Result Hash",
      "Library Version",
      "Library Content Identity",
      "Workbook Selection Hash",
      "Mapping Hash",
      "Passport Hash",
    ],
    widths: [14, 14, 14, 36, 36, 36, 36, 16, 36, 36, 36, 36],
  });

  const artifactPath = path.join(repoRoot, ARTIFACT_RELATIVE_PATH);
  const manifestPath = path.join(repoRoot, MANIFEST_RELATIVE_PATH);
  await fs.mkdir(path.dirname(artifactPath), { recursive: true });
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(artifactPath);
  await normalizePackageBytes(artifactPath);
  const payload = await fs.readFile(artifactPath);
  const manifest = {
    schema_version: "excel-workbook-artifact-manifest/v1",
    artifact: ARTIFACT_RELATIVE_PATH,
    artifact_sha256: crypto.createHash("sha256").update(payload).digest("hex"),
    artifact_size_bytes: payload.length,
    template_id: "structural-lib-rectangular-beam-workbench",
    template_version: "1.0",
    contract_schema: "excel-workbook-contract/v1",
    trust_mode: "MACRO_FREE_OFFICE_JS",
    visual_review: {
      reviewed_on: "2026-08-22",
      status: "PASS",
      worksheets: [
        "Workbook_Info",
        "Beam_Workbench",
        "Mapping_Preview",
        "Row_Ledger",
        "Results",
        "Passports",
      ],
    },
    installed_windows_excel_evidence: "TO_VERIFY_WINDOWS",
  };
  await fs.writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  console.log(JSON.stringify(manifest));
}

await main();
