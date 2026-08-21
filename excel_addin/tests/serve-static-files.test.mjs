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

test("HTTPS server exposes every local task-pane module dependency", () => {
  const modulePaths = Array.from(
    taskpaneSource.matchAll(/from\s+"\.\/([^"]+)"/g),
    ([, modulePath]) => modulePath,
  );
  assert.deepEqual(modulePaths.sort(), [
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
