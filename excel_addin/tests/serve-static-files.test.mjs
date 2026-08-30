import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const taskpaneSource = fs.readFileSync(
  new URL("../taskpane.mjs", import.meta.url),
  "utf8",
);
const serverSource = fs.readFileSync(
  new URL("../serve.mjs", import.meta.url),
  "utf8",
);
const taskpaneHtml = fs.readFileSync(
  new URL("../taskpane.html", import.meta.url),
  "utf8",
);

test("HTTPS server exposes every local task-pane module dependency", () => {
  const modulePaths = Array.from(
    taskpaneSource.matchAll(/from\s+"\.\/([^"]+)"/g),
    ([, modulePath]) => modulePath,
  );
  assert.deepEqual(modulePaths.sort(), [
    "review-pane.mjs",
    "taskpane-core.mjs",
    "taskpane-office.mjs",
  ]);
  for (const modulePath of modulePaths) {
    assert.equal(
      serverSource.includes(`["/${modulePath}",`),
      true,
      `${modulePath} must be served over the trusted HTTPS origin`,
    );
  }
});

test("W3 review loads before any optional API connection and serves every transitive module", () => {
  assert.ok(taskpaneSource.indexOf("initializeCalculationReviewPane(Office, Excel)") < taskpaneSource.indexOf('ui.status = document.getElementById'));
  for (const name of ["review-core.mjs", "review-pane.mjs"]) assert.ok(serverSource.includes(`["/${name}",`));
  for (const id of ["w3-review-file", "w3-review-preview", "w3-review-publish", "w3-review-verify", "w3-review-comments"]) assert.ok(taskpaneHtml.includes(`id="${id}"`));
});

test("installed pane exposes and wires fail-closed review-bundle export", () => {
  assert.match(taskpaneHtml, /id="export"[^>]*aria-describedby="export-detail"[^>]*disabled/);
  assert.match(taskpaneHtml, /id="export-detail"[^>]*aria-live="polite"/);
  assert.match(taskpaneSource, /\/excel-workbench\/v1\/review-bundle/);
  assert.match(taskpaneSource, /ui\.export\.addEventListener\("click", exportReviewBundle\)/);
  assert.match(taskpaneSource, /state\.freshnessVerified = false/);
});

test("installed pane exposes the explicit read-only ETABS pilot controls", () => {
  assert.match(taskpaneHtml, /id="etabs-connect"[^>]*disabled/);
  assert.match(taskpaneHtml, /id="etabs-run"[^>]*disabled/);
  assert.match(taskpaneSource, /\/etabs-bridge\/v1\/status/);
  assert.match(taskpaneSource, /\/etabs-bridge\/v1\/beam-pilot/);
  assert.match(taskpaneSource, /writeEtabsPilotResults\(Excel, rows\)/);
});

test("installed pane exposes the preflight-bound W2 baseline controls", () => {
  assert.match(taskpaneHtml, /id="etabs-w2-preflight"[^>]*disabled/);
  assert.match(taskpaneHtml, /id="etabs-w2-confirm"[^>]*disabled/);
  assert.match(taskpaneHtml, /id="etabs-w2-run"[^>]*disabled/);
  assert.match(taskpaneSource, /\/etabs-bridge\/v1\/beam-baseline\/preflight/);
  assert.match(taskpaneSource, /\/etabs-bridge\/v1\/beam-baseline/);
  assert.match(taskpaneSource, /verifyEtabsBaselineTransport\(transport\)/);
  assert.match(taskpaneSource, /writeEtabsBaselineResults\(Excel, projection\)/);
});
