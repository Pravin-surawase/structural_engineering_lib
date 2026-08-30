import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

test("Long review JSON cannot set the pane grid's minimum width", () => {
  const css = fs.readFileSync(new URL("../taskpane.css", import.meta.url), "utf8");
  const main = css.match(/main\s*\{([^}]+)\}/)[1];
  assert.match(main, /grid-template-columns:\s*minmax\(0,\s*1fr\)/);
  assert.match(css, /\.detail,\s*\.status\s*\{[^}]*overflow-wrap:\s*anywhere/);
  assert.match(css, /input\[type="file"\]\s*\{[^}]*max-width:\s*100%/);
  assert.doesNotMatch(css, /text-overflow:\s*ellipsis|overflow(?:-x)?:\s*hidden/);
});
