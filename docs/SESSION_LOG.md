# Session Log

> Append-only decision log for AI agent sessions.
> Earlier sessions (1-100): [SESSION_LOG_through_session_100.md](_archive/SESSION_LOG_through_session_100.md)

---

## 2026-08-24 — Session: LIB-PRO-010-RC bounded v0.24.0a1 candidate

**Agent:** Codex (`ops`, sole writer; no subagents)

**Branch:** `codex/lib-pro-010-rc-artifact`, from exact hosted LIB-PRO-009 merge
`b3309260686a05b4cbb9c9358c89d6218a700357`, tree
`90894f2f39b4356b4aa30b6c3661ac9c718b3073`.

**Git handoff receipt:**
`docs/verification/lib-pro-010-rc-git-handoff-receipt.json`

**Focus:** Prepare one bounded `v0.24.0a1` Alpha candidate from the integrated
post-`v0.23.1a2` subset, freeze its supported scope and exclusions, build exact
wheel/sdist artifacts, and run source-free installed-package UAT. Preserve the
separate qualified-engineer, owner release, tag, upload, GitHub Release,
professional-approval, later-scope, and cleanup gates.

### Summary

- Verified live GitHub `main` and `origin/main` at `b3309260`, then created one
  fresh clean source-bound worktree. All retained dirty, detached, divergent,
  historical, and unrelated lanes remain untouched.
- Selected `0.24.0a1` from the maintained Alpha-only release policy and the
  repository's next-version examples. Public `v0.23.1a2` remains immutable and
  is not rebuilt from current `main`.
- The first pre-bump preflight passed 7,033 Python tests, 492 FastAPI tests, and
  the React production build, but correctly returned `NOT_READY` because the
  footing release-inclusion receipt predated six reviewed footing-path changes.
- Traced every changed footing path to merged canonical-transport, public-domain
  validation, or bounded end-anchorage packets; refreshed exact owned-file
  hashes and limitations; and passed the inclusion gate plus 128 focused
  release/footing tests.

### Issues encountered

- An initial GitHub commit query used the wrong account spelling and returned
  HTTP 404 before the configured remote owner was inspected.
- The first pre-bump release preflight found six stale footing inclusion hashes
  and returned `NOT_READY` despite otherwise green Python, FastAPI, and React
  results.
- The first preliminary commit hook rejected the inherited LIB-PRO-009 handoff
  receipt after its 15-minute authorization and retention observations became
  stale.

### Root causes and resolutions

- Confirmed root cause: the GitHub query guessed `pravinsurawase` instead of
  reading the configured `Pravin-surawase` remote identity. Resolution: resolve
  `nameWithOwner` through `gh repo view` before querying; live GitHub and local
  remote `main` both equal `b3309260`. ⚠️ TERMINAL ISSUE: guessed GitHub owner
  returned 404 -> resolved the configured remote identity first.
- Confirmed root cause: the footing receipt still bound hashes from the A-G
  release slice even though PRs #822, #833, and #855 had deliberately changed
  six owned paths. Resolution: review those exact merged diffs and evidence,
  name the refresh chain, preserve the narrowed anchorage holds, and bind the
  current hashes. Proof: `footing-inclusion-check` and 128 release/footing tests
  pass. ⚠️ TERMINAL ISSUE: preflight stopped on stale inclusion evidence ->
  refreshed only the reviewed receipt and its truthful gate message.
- Confirmed root cause: handoff observations are intentionally valid for at
  most 900 seconds, so a later task cannot reuse the predecessor's authorization
  or retention evidence. Resolution: create a fresh LIB-PRO-010-RC source
  evidence and fail-closed task receipt, then embed it through the maintained
  session handoff. Proof: the session-document hook accepts the current receipt.
  ⚠️ TERMINAL ISSUE: the first commit hook stopped on stale predecessor
  evidence -> generated the current task-owned receipt instead of rewriting the
  historical one.

### Validation through current checkpoint

- Pre-bump candidate preflight: 7,033 Python passed, 3 skipped, 6 deselected;
  492 FastAPI passed, 6 deselected; React Node 24 install/build passed. Verdict:
  `NOT_READY` only for the six stale inclusion hashes.
- Focused release and footing verification: 128 tests pass; the refreshed
  inclusion gate passes and JSON/diff checks are clean.

### Preserved holds

- No tag, TestPyPI/PyPI upload, GitHub Release, stable/engineering-use wording,
  qualified-engineer receipt, INDIA-4 acceptance, or professional approval.
- No IS 13920 wall/foundation, IS 875, IS 1893, dynamic, response-spectrum, FEM,
  ETABS write-back, or complete building-design scope.
- No branch, worktree, archive, source-copy, alias, private source, or unrelated
  file deletion or mutation.

---

## 2026-08-24 — Session: LIB-PRO-009 bounded release-trust closeout

**Agent:** Codex (`backend`, sole writer; no subagents)

**Branch:** `codex/lib-pro-009-rc-trust`, from exact hosted INDIA-3 M0 merge
`b85d514ed93e22a154badde990ef1c3fb02ae0d9`, tree
`8a45afa44a5fb3d227aab666d17aadf29fe1c26e`.

**Git handoff receipt:**
`docs/verification/lib-pro-009-git-handoff-receipt.json`

**Focus:** Close strict rebar input, evidence-status, and living-state defects.
Require positive-integer `bar_count` values, separate benchmark replay from
engineering disposition, and reconcile task/roadmap/handoff state. Preserve all
formulas, supported scope, historical receipts, release authority, qualified
review, professional approval, and cleanup holds.

### Summary

- Created one clean source-bound worktree from live GitHub `main` after verifying
  that the only open PRs were unrelated dependency updates. No existing branch,
  worktree, source, archive, alias, or unrelated file was modified or removed.
- Made `validate_rebar_config` accept only an actual positive Python/JSON
  integer for `bar_count`. Booleans, strings, fractional values, zero, negatives,
  and missing values now return the same structured validation failure and no
  geometry. `apply_rebar_config` consumes the validated value instead of
  reparsing raw input.
- Preserved the immutable INDIA-3 M0 evidence and added one current status
  clarification with independent benchmark-replay, calculation, engineering,
  and review axes. The represented cases are beam `NOT_EVALUATED`, bounded
  column `PASS`, and joint `FAIL` while all three replays are `PASS` and qualified
  review remains required.
- Added the clarification to every supported IS 13920 family in the generated
  capability manifest and added a recurrence test for the four-axis contract.
- Reconciled the current task board, Indian-code completion plan, and next-
  session prose to the merged M0 state. Added one ordered bounded-release plan:
  internal closeout, exact candidate/artifact freeze, installed UAT, qualified
  review of the unchanged candidate, separate owner release decision, then
  later scope expansion.

### Issues encountered

- The first `LIB-PRO-009` session start was blocked because the already-merged
  `INDIA-3-IS13920-M0` task retained an unmatched start checkpoint in the shared
  Git-common usage ledger.
- Public rebar validation coerced `bar_count` through `int(...)` before checking
  it, so booleans were accepted, fractional values were silently truncated, and
  invalid text could raise instead of returning the advertised validation
  result. The apply path independently repeated the coercion.
- The immutable M0 evidence used one nested benchmark `result: PASS` field even
  for the unsafe joint vector whose actual engineering check was `FAIL`.
- Living control documents still instructed the next task to merge the M0
  candidate after PR #869 had already merged it.
- The first focused Black check rejected one newly added test layout.
- The first consolidated full gate passed 30 of 31 checks and rejected the new
  bounded-release plan's unsupported `doc_type: plan` front-matter value.
- The first normal commit-hook run passed every other hook but mypy rejected the
  strict helper's `Any` return even after its runtime integer guard.

### Root causes and resolutions

- Confirmed root cause: M0 recorded its clean local session end but no successor
  usage closeout after the hosted merge, leaving the shared timer unmatched.
  Resolution: verify PR #869, exact candidate `0a20774e`, merge `b85d514e`,
  required hosted checks, reachability, and exact tree equality; then append the
  supported late successor closeout without rewriting M0 evidence. Proof: the
  shared ledger accepted the closeout and the canonical `LIB-PRO-009` session
  start then passed. ⚠️ TERMINAL ISSUE: session start was blocked by a stale
  predecessor checkpoint -> used exact hosted and Git tree evidence to close it.
- Confirmed root cause: type conversion occurred before semantic validation and
  the application path did not reuse the validated canonical value. Resolution:
  add one strict positive-integer normalizer, return zero only as the internal
  invalid sentinel, issue a structured error, and consume `report.details` in
  the apply path. Proof: 11 rebar tests cover valid use plus booleans, strings,
  fractional values, missing/zero/negative values, structured failure, and no
  geometry.
- Confirmed root cause: the historical `benchmark.result` represented replay-
  harness success rather than case engineering truth, but its generic name did
  not express that boundary. Resolution: preserve the historical receipt and
  add a machine-readable four-axis clarification consumed by the capability
  manifest. Proof: 12 manifest/status tests require replay `PASS`, beam
  `NOT_EVALUATED`, bounded column `PASS`, joint `FAIL`, and qualified review.
- Confirmed root cause: candidate-frozen task/handoff prose had no later living-
  status reconciliation after the hosted merge. Resolution: record the exact
  M0 merge/tree in current control documents while leaving historical session
  and handoff receipts unchanged. Proof: the updated documents contain no
  instruction to merge M0 and link the ordered successor plan.
- Confirmed root cause: the new multi-line assertion was not in Black's
  canonical layout. Resolution: format the affected test only and recheck all
  four changed Python files. Proof: Black reports all four unchanged and Ruff
  reports no findings. ⚠️ TERMINAL ISSUE: focused Black check failed one file ->
  formatted that file and reran only the failed formatting evidence.
- Confirmed root cause: repository front-matter uses the closed `doc_type`
  vocabulary and `plan` is not an allowed value; maintained planning documents
  use `spec`. Resolution: change only the new document's type to `spec` and
  preserve its task status and content. Proof: strict documentation validation
  and the content-addressed corrective full gate pass. ⚠️ TERMINAL ISSUE: the
  first full gate rejected one front-matter value -> used the maintained closed
  vocabulary and reran the failed domain through the cached consolidated gate.
- Confirmed root cause: `_pick` intentionally returns `Any`, and mypy does not
  promote that value to the helper's declared `int` return solely from the
  runtime `isinstance` branch. Resolution: return `int(value)` only after the
  bool/type/range guard, preserving the strict behavior while making the type
  contract explicit. Proof: focused mypy and the normal commit hooks pass all
  247 checked source files. ⚠️ TERMINAL ISSUE: the first commit hook stopped on
  one `no-any-return` error -> made the validated return explicitly typed and
  reran the failed type evidence before the normal hooks.

### Validation through content freeze

- Focused Python: 23 tests pass across rebar validation, status semantics,
  generated capability truth, and existing Indian-code manifest behavior.
- Ruff passes the four changed Python files. Black passes after one formatting-
  only repair. The maintained Indian-code manifest currentness check passes.
- Both changed JSON documents parse successfully. No formula, code-source
  provenance, supported-family status, route, version, or public artifact was
  changed.
- The first full gate passed 30/31 and exposed only the new plan front-matter
  value. The corrective run reuses unchanged domains and passes all 31 checks.

### Preserved holds

- Qualified structural-engineering review, INDIA-4 acceptance, stable release,
  engineering-use wording, professional approval, versioning, tagging, package
  publication, and GitHub Release creation remain separate and unperformed.
- IS 13920 walls/foundations, IS 875, IS 1893, dynamic/response-spectrum/FEM
  analysis, ETABS write-back, and broader building design remain held.
- No historical evidence or handoff receipt was rewritten. No protected source,
  branch, worktree, archive, source-copy, alias, or unrelated file was deleted.

---

## 2026-08-24 — Session: INDIA-3-IS13920-M0 cumulative bounded acceptance

**Agent:** Codex (`structural-math`, sole writer; no subagents)

**Branch:** `codex/india-3-is13920-m0`, from exact hosted
INDIA-3-COLUMN-R1 merge `306e2a46328ce2b519d1352131b64ef310271b5e`,
tree `cbe0f8d934d99a090597958749e224b6e37b21b4`.

**Git handoff receipt:**
`docs/verification/india-3-is13920-m0-git-handoff-receipt.json`

**Focus:** Run the single G0-frozen cumulative source, benchmark, unsafe-case,
cross-surface, capability, package, and qualified-review-boundary acceptance for
the repaired IS 13920 beam, rectangular-column, and directional joint subset.
Preserve every wall, foundation, IS 875/1893, source/distribution, support,
version, release, professional-use, and qualified INDIA-4 review hold.

### Summary

- Verified live `origin/main`, merged PR #868, and the exact column predecessor
  commit/tree before creating one fresh source-bound task lane. All unrelated
  lanes remain retained; none was reset, cleaned, rebased, deleted, or reused.
- Bound the cumulative result to the visually reviewed IS 13920:2016 First
  Revision plus Amendments 1 (2017) and 2 (2020), with 2021 reaffirmation kept
  separate and the draft successor unused. The private archive is not mounted
  in this worktree, so M0 relies on the integrated G0/source-metadata receipts
  and claims only the current tracked no-private-material boundary.
- Accepted beam requirements-with-geometry, rectangular-column provided
  special confinement, and one-principal-plane/one-shaking-direction SCWB as
  bounded software contracts. The benchmark outputs are respectively 72 mm;
  222.28915662650604 mm2 plus 277.10843373493975 mm2; and required 280 kNm,
  ratio 0.8928571428571429, `FAIL` at 250/200 kNm.
- Reconciled the generated joint capability to its fixed 1.4 factor,
  directional/opposing-capacity rule, factored axial-load basis, non-roof and
  non-flat-slab applicability, supported interior/left-exterior/right-exterior
  topologies, one-case-not-whole-joint limit, and core-only publication truth.
  No route, service, root export, formula, or support-status promotion was
  added.
- The first cumulative broad Python run exposed six IS 13920 metadata/test
  integration failures and one unrelated stale visualization expectation. One
  bounded repair registered four accepted joint identifiers, corrected the
  179-record count and exact source tests, and made the old multi-leg 3D test
  assert the already-maintained fail-closed runtime behavior.
- The repaired broad Python gate passes 7,024 cases, FastAPI passes 498, and a
  source-free 0.23.1a2 wheel replays all three benchmarks. The 29-case/14-entry
  package UAT passes with `qualified_review_required=true` and
  `professional_approval=false`.
- M0 accepts the qualified-review boundary; it does not claim an identified
  qualified-engineer approval. Cumulative qualified structural-engineering
  review remains INDIA-4. No successor packet ID was frozen or started.

### Issues encountered

- The maintained Indian-code generator was first invoked without `--write`, so
  it printed the new manifest to stdout and the deterministic-current test
  correctly failed.
- One guessed verification subcommand (`affected`) and three guessed helper
  paths for private-source, import, and frontmatter checks were not registered
  current commands.
- The first source-free wheel probe used core result field/method names against
  the package wrapper and raised two attribute errors before the actual
  dataclass contract was inspected. A later command changed into the temporary
  source-free directory before running a repository-relative `rg`, so that
  diagnostic path was unavailable.
- `test_import_pipeline.py` was run without its required separately started
  FastAPI server and produced only connection-refused failures; that live-server
  diagnostic is not part of the M0 changed-path route.
- The first cumulative broad Python run failed seven tests: six clause-registry
  and exact-reference assertions plus one large-beam visualization expectation.
- The first full repository gate passed 30 of 31 checks and rejected the stale
  public API manifest signature for `check_column_ductility_is13920`.

### Root causes and resolutions

- Confirmed root cause: `generate_indian_code_manifest.py` defaults to stdout.
  Resolution: rerun the maintained command with `--write`, then verify with
  `--check`. Proof: the deterministic manifest tests and currentness check pass.
  ⚠️ TERMINAL ISSUE: generator output was not written -> used the documented
  `--write` mode.
- Confirmed root cause: the guessed automation names are not owners in the
  current control registry. Resolution: use `verification.py plan`,
  `validate_imports.py`, `check_circular_imports.py`, the two private-boundary
  pytest cases, link validation, context validation, and the consolidated
  repository gates. Proof: maintained import, boundary, link, context, and
  routing controls pass. ⚠️ TERMINAL ISSUE: guessed commands were absent ->
  discovered and used their maintained owners.
- Confirmed root cause: the beam package wrapper returns the legacy
  `DuctileBeamResult` fields `confinement_spacing` and `compliance_status`, not
  the core field name or a `to_dict()` method. Resolution: inspect the installed
  dataclass and replay against its real contract from a subshell that preserves
  repository cwd. Proof: all three source-free installed-wheel benchmarks pass.
  ⚠️ TERMINAL ISSUE: wrapper-field probes raised `AttributeError` and a
  temporary-directory `cd` hid repository paths -> used the actual dataclass
  fields inside a bounded subshell.
- Confirmed root cause: `test_import_pipeline.py` is a live-server end-to-end
  diagnostic, not a static import verifier. Resolution: exclude it from this
  offline changed-path route and use the maintained static import/circular
  checks plus complete FastAPI pytest. Proof: 2,290 internal imports resolve,
  zero cycles exist, and all 498 FastAPI tests pass. ⚠️ TERMINAL ISSUE:
  live import pipeline had no server -> used the offline controls required by
  this packet.
- Confirmed root cause: BEAM-R1 and COLUMN-R1 replaced obsolete generic clause
  identifiers without updating the aggregate count or legacy coverage list;
  JOINT-R1 corrected runtime provenance but intentionally left its cumulative
  capability/identifier reconciliation to M0. Resolution: register only four
  project-authored joint identifiers, set the exact 179 count, update tests to
  the accepted exact references, and regenerate the capability manifest.
  Proof: the 29-case failure reproducer passes, the manifest has 22 known
  references and zero registration-only references, and broad Python is green.
- Confirmed root cause: LIB-PRO-008 made one-loop 3D geometry truthfully reject
  disconnected internal legs, but a 2026-01 large-beam test still expected the
  former false representation. Resolution: preserve runtime and assert the
  fail-closed result for the automatically selected four-leg case. Proof: the
  focused reproducer and all 7,024 broad Python tests pass.
- Confirmed root cause: COLUMN-R1 changed the existing service signature to
  require applicability, topology, actual geometry, and provided confinement,
  but its broad generated API-manifest projection remained on the old optional-
  core signature because that full check was deferred to M0. Resolution:
  regenerate only the canonical API manifest; no signature or runtime changed
  in M0. Proof: the exact diff updates one signature plus its generation date,
  and focused API-manifest/stability tests pass.

### Validation through content freeze

- Focused cumulative evidence passes 284 Python cases, 6 routed FastAPI cases,
  2 private-boundary cases, 221-file architecture validation, 696-file import
  validation, 202-file cycle validation, deterministic manifest generation,
  and repository link/context/efficiency controls.
- Initial broad Python: 7 failed, 7,008 passed, 3 skipped, 6 deselected. The one
  bounded repair's 29 targeted cases pass. The required corrective broad rerun
  passes 7,024, with 3 skipped and 6 deselected. Complete FastAPI passes 498.
- The exact source-free wheel SHA-256 is
  `03c646a258304fcc431df142a26ee77d3aced8466603a06737a1648b60470b9a`.
  Installed origin, all three IS 13920 benchmarks, 29 negative-UAT cases, and
  14 advertised entry points pass; package version remains 0.23.1a2.
- The first full repository gate passed 30/31 and exposed only the stale
  COLUMN-R1 API-manifest projection. After the bounded regeneration, the
  corrective full gate passes 31/31 with 15 exact content-addressed reused
  results for unchanged domains.
- The sole final quick gate passes 10/10 with three exact content-addressed
  reused results for unchanged domains. The immutable candidate still requires
  normal commit hooks, clean-commit `session end`, hosted checks, unchanged-head
  merge, and candidate/merge tree equality. Later hosted facts remain external
  and are not pre-claimed here.

### Preserved holds

- Beam provided reinforcement remains not evaluated. Column applicability is
  caller-confirmed, non-rectangular columns remain unsupported, and provided
  longitudinal steel remains not evaluated. One joint result is not a whole-
  joint assessment; both directions in all applicable planes remain caller-
  owned.
- IS 13920 wall and foundation provisions remain held. The next sequence item
  is a separate source/benchmark wall decision, but M0 does not freeze or start
  an exact packet ID. IS 875 and IS 1893 remain later sequential work.
- Passing software/source/package gates does not constitute qualified
  structural-engineering review, engineering-use approval, professional-use
  approval, a version change, package publication, tag, or release.
- No protected/private source byte, prose, image, hash, path, or database
  content changed or entered the tracked candidate. Branch, worktree, archive,
  source-copy, alias, and unrelated-file deletion remain unauthorized.

---

## 2026-08-24 — Session: INDIA-3-COLUMN-R1 bounded column contract repair

**Agent:** Codex (`structural-math`, sole writer; no subagents)

**Branch:** `codex/india-3-column-r1`, from exact hosted INDIA-3-BEAM-R1
merge `cfe29f890e62c40546f3a91c8810e1daf7c0d722`, tree
`a0a095e00f3555fe5bdd8ccf5704ba4b71b69289`.

**Git handoff receipt:**
`docs/verification/india-3-column-r1-git-handoff-receipt.json`

**Focus:** Repair only the G0-bounded IS 13920 rectangular-column geometry,
applicability, actual-core, amended confinement, provided-detail, result
meaning, and affected existing transport/metadata contract. Preserve every
adjacent formula, source, distribution, support, version, release, and
professional-use hold.

### Summary

- Verified live `origin/main` and merged PR #867 at exact predecessor
  `cfe29f89`, tree `a0a095e0`, before creating one fresh source-bound task
  worktree. Every unrelated dirty, detached, divergent, or unknown lane remains
  retained.
- Reproduced the outcome-changing G0 defects: the second rectangular
  confinement-area expression returned 181.0372 mm2 instead of the governing
  277.1084 mm2; NaN geometry returned valid/compliant; obsolete or wrong clause
  identities were attached; and the service invented gross/core geometry from
  a hidden 40 mm cover assumption before returning a success-like result.
- The repaired contract requires caller-confirmed applicability with a non-empty
  basis, rectangular topology, actual `Ag`, `Ak`, and hoop `h`, and provided
  spacing, confinement length, and hoop area. No cover, gross area, core
  dimension, or provided reinforcement is inferred.
- Both accepted rectangular confinement-area expressions are evaluated and the
  maximum governs. The amended spacing/length boundaries, exact geometry
  clauses, finite intake, actual/provided checks, structured findings, and
  source/amendment provenance agree across core, package/service, the existing
  FastAPI route, OpenAPI, clause maps, and generated capability truth.
- The separately retained 0.8% and 4.0% values are sourced to IS 456:2000 Cl
  26.5.3.1(a) and explicitly marked `NOT_EVALUATED` because this contract has
  no provided longitudinal steel. No new endpoint or product workflow was
  added.
- No beam, joint, wall, foundation, IS 875, or IS 1893 formula; React/Excel
  surface; package version; release; source/distribution decision; support
  promotion; or professional-use approval changed. `INDIA-3-IS13920-M0` is
  next and was not started.

### Issues encountered

- The first worktree-creation tool call selected the not-yet-created target as
  its process directory, so the tool could not start and no Git command ran.
- The first historical reproducer tried to reach the wrapped geometry helper
  through decorator globals and raised `KeyError` after printing the numeric
  defect evidence.
- The first structured-error patch expected rendered comparison symbols while
  the file stored escaped Unicode literals, so its context did not match.
- The first test-file replacement patch combined delete and add operations for
  the same path, which the patch tool rejects.
- The consolidated focused run found one manifest regression that still
  required obsolete IS 13920 reference `7.4.8` to remain registration-only
  after this packet corrected that identity.
- The first targeted mypy command ran from the repository root even though the
  configured explicit package base is `Python/`, causing one source file to be
  discovered under two module names.

### Root causes and resolutions

- Confirmed root cause: a process working directory must exist before command
  execution. Resolution: create the isolated worktree from the existing beam
  checkout. Proof: the new lane starts at exact `cfe29f89`, reports
  `source_bound=true`, and began `READY_LOCAL`. ⚠️ TERMINAL ISSUE: target cwd did
  not yet exist -> created the worktree from an existing checkout.
- Confirmed root cause: the clause decorator returns a wrapper whose globals
  are the traceability module, not the wrapped column module. Resolution: import
  the geometry helper directly for the clause replay. Proof: the exact obsolete
  geometry and orchestrator reference lists were recorded. ⚠️ TERMINAL ISSUE:
  decorator globals produced `KeyError` -> reran with the direct import.
- Confirmed root cause: source text uses literal escaped Unicode sequences in
  the error records. Resolution: match the actual stored representation and
  apply only the bounded column error changes. Proof: E001-E007 now carry the
  exact IS 13920 or IS 456 identity and provided-detail fields. ⚠️ TERMINAL
  ISSUE: rendered-symbol patch context failed -> matched the literal file text.
- Confirmed root cause: one patch transaction cannot delete and re-add the same
  file. Resolution: perform the deletion and bounded replacement as two patch
  operations, then format the result. Proof: the focused column contract file
  collects 30 passing cases. ⚠️ TERMINAL ISSUE: combined delete/add was rejected
  -> used two non-overlapping patch operations.
- Confirmed root cause: `test_is456_and_is13920_registration_cannot_cross_match`
  encoded the obsolete column reference as its namespace sentinel. Resolution:
  retain the namespace invariant but bind the sentinel to the remaining
  registration-only joint reference `7.2.1`. Proof: the exact failed node then
  passes; the other 228 Python nodes were already green and were not rerun.
- Confirmed root cause: configured mypy uses `explicit_package_bases=true` with
  `Python/` as the package base. Resolution: run from `Python/` and pass the
  bounded core, service, and FastAPI model paths. Proof: all three source files
  report no issues. ⚠️ TERMINAL ISSUE: root-level mypy found a duplicate module
  -> reran from the configured package base.
- Confirmed root cause: original core commit `6b412719` implemented only the
  first area expression and a success-like all-in-one result; service commit
  `61e6020f` added the hidden 40 mm core default; later rename and decorator
  commits preserved or mislabeled that behavior. Resolution: require the
  applicability, actual geometry, topology, and provided check inputs; compute
  both accepted expressions; and align the existing transports and exact
  metadata owners. Proof: both independent benchmarks, unsafe provided-detail
  cases, missing-input route case, and provenance assertions pass.

### Validation through content freeze

- Aggregate impact-mapped Python evidence passes 229 cases: 228 passed in the
  consolidated run and the single stale manifest expectation passed on its
  exact failed-only repair rerun. The FastAPI transport/response selection
  passes 15 cases.
- Targeted Black and Ruff pass. Configured mypy reports no issues in the column
  core, service, and request/response model. Architecture boundaries report
  zero violations across 221 files, and all 2,290 internal imports across 696
  Python files resolve.
- The OpenAPI baseline matches 89 endpoints and 444 schemas. API classification
  and its 620-projection compatibility ledger are current. The Indian-code
  manifest registers the exact amended column clauses and IS 456 companion
  reference without capability-status, release, or authorization promotion.
- Changed-path routing selects Python, FastAPI, control-plane, and docs. The
  broad repository gate remains deferred to cumulative
  `INDIA-3-IS13920-M0` because the bounded checks have no material failure or
  unknown impact.
- The immutable candidate still requires the sole post-freeze quick gate,
  normal commit hooks, clean-commit `session end`, all required hosted checks,
  unchanged-head merge, and candidate/merge tree equality. Those later facts
  remain external and are not pre-claimed here.

### Preserved holds

- Applicability is caller-confirmed rather than inferred from an unproven axial
  threshold. Non-rectangular columns and provided longitudinal-reinforcement
  compliance remain outside the supported result.
- `INDIA-3-IS13920-M0` remains a separate sequential cumulative packet.
  Wall/foundation detailing and IS 875/1893 remain held.
- No protected/private source byte, text, image, hash, path, or database
  content changed or entered the tracked candidate. Source/distribution,
  support, version, release, package publication, and professional-use
  approval remain separate claims.
- Branch, worktree, archive, source-copy, alias, and unrelated-file deletion
  remain unauthorized.

---

## 2026-08-24 — Session: INDIA-3-BEAM-R1 bounded beam contract repair

**Agent:** Codex (`structural-math`, sole writer; no subagents)

**Branch:** `codex/india-3-beam-r1`, from exact hosted INDIA-3-JOINT-R1
merge `b59e6ea02e52056d1024bb4dc90204f149f112eb`, tree
`acc167e2caaa311a8f4fe2861e6a5aa4afd7d75c`.

**Git handoff receipt:**
`docs/verification/india-3-beam-r1-git-handoff-receipt.json`

**Focus:** Repair only the G0-bounded IS 13920 beam amendment, strict
geometry, finite-intake, requirement-versus-compliance, and affected
core/service/HTTP/clause-metadata contract. Preserve every adjacent formula,
source, distribution, support, version, release, and professional-use hold.

### Summary

- Verified live `origin/main` and merged PR #866 at exact predecessor
  `b59e6ea0`, tree `acc167e2`, before creating one fresh source-bound task
  worktree. Every unrelated dirty, detached, divergent, or unknown lane remains
  retained.
- Reproduced all four outcome-changing G0 defects: the benchmark returned 96
  mm instead of 72 mm, exact `b/D = 0.3` passed, NaN concrete strength produced
  a NaN requirement with no error, and a requirement calculator reported
  `Compliant` despite accepting no provided reinforcement.
- Applied the accepted Amendment 1 spacing expression
  `min(d/4, 6*db_min, 100 mm)`, enforced `b/D > 0.3`, and fail-closed finite
  intake for all six calculation inputs. The 200 mm minimum width remains
  inclusive.
- Made result meaning machine-readable as
  `REQUIREMENTS_WITH_GEOMETRY_CHECK` and
  `NOT_EVALUATED_NO_PROVIDED_REINFORCEMENT`. Source/amendment identity and exact
  clause references travel through the existing core, service/package, and
  FastAPI route without adding a new endpoint or changing the service
  signature.
- Corrected swapped/generalized decorators, structured error clauses, clause
  maps, OpenAPI truth, and generated Indian-code registration metadata. The
  declared capability status is unchanged and its limitation now states that
  provided reinforcement compliance is not evaluated.
- No column, joint, wall, foundation, IS 875, or IS 1893 formula; React/Excel
  surface; package version; release; source/distribution decision; support
  promotion; or professional-use approval changed. `INDIA-3-COLUMN-R1` is next
  and was not started.

### Issues encountered

- The retired `./run.sh context show task-brief` alias returned `unknown context
  area` during orientation.
- The existing beam path reproduced the amended-spacing, strict-boundary,
  non-finite-input, compliance-label, and clause-identity defects frozen by G0.
- Running the maintained error-document generator exposed that the committed
  reference predates many unrelated error families and would have widened this
  packet from two affected beam rows to a repository-wide 29-to-64-code
  refresh.
- The first consolidated focused command used the wrong containing class name
  for one FastAPI endpoint test, and targeted Ruff requested canonical import
  ordering in the new direct test.
- The first hosted documentation job stopped at the API-classification
  freshness check before MkDocs ran.
- A direct attempt to run `scripts/check_session_docs.py` failed because that
  path is not a maintained top-level script.
- The first handoff-receipt validation call guessed an unsupported `--receipt`
  option instead of the required positional receipt path.
- Receipt validation then failed closed because the task authorization and
  retention observations had aged beyond the bounded freshness window during
  implementation and hosted repair preparation.
- The first repair commit attempt was stopped by the session-document hook
  because the handoff line carried the receipt file checksum instead of its
  canonical local-state receipt hash.

### Root causes and resolutions

- Confirmed root cause: `task-brief` is not a registered context-manifest area;
  the governed `session begin` command itself provides the maintained compact
  agent brief. Resolution: use that session brief plus targeted source/G0
  reads. Proof: session start completed with source-bound runtime and
  `READY_LOCAL`. ⚠️ TERMINAL ISSUE: `context show task-brief` is not a valid
  area -> the canonical `session begin` brief supplied the bounded orientation.
- Confirmed root cause: original commit `7f12fd90` introduced the eight-bar
  spacing rule and success-like `Compliant` label without provided
  reinforcement. Namespace-migration commit `32f49571` added the equality
  tolerance and positivity guards that do not reject NaN. Later decorator and
  reference-map commits `54b7e2d8`, `55a5096d`, and `410fb881` attached
  generalized or swapped clause identities without an amended independent
  benchmark. Resolution: implement the accepted G0 source map directly and
  align every existing transport and affected metadata owner. Proof: the
  benchmark is 72 mm, the 0.3 boundary fails, all non-finite inputs return
  `E_INPUT_017`, and no success-like reinforcement claim is emitted.
- Confirmed root cause: `generate_error_docs.py` reflects all 64 live error
  definitions while the tracked reference intentionally remains an older
  29-code snapshot. Resolution: preserve that separate repository-wide drift
  and update only the two task-owned beam rows through the required surgical
  file patch. Proof: the final diff contains only the corrected
  `E_DUCTILE_001` and `E_DUCTILE_002` rows.
- Confirmed root cause: the endpoint regression belongs to
  `TestDepthValidationUX01`, not the guessed class selector; Ruff's isort rule
  also owns the import grouping. Resolution: use the discovered exact node and
  apply the formatter-owned import fix. Proof: the interrupted FastAPI set
  passes all 24 cases and targeted Black/Ruff are green; the already-passing
  231 Python cases were not rerun.
- Confirmed root cause: the candidate added explicit result-semantics and
  provenance fields to `DuctileBeamResult`, but the maintained API registries
  were not regenerated before the first immutable candidate. The date-bound
  classification registry therefore still carried 2026-08-23, and the compact
  compatibility ledger still carried the preceding result signature. An
  unpacked semantic comparison found exactly one compatibility change: the
  `DuctileBeamResult` root-stub projection signature and its derived identity
  key. Resolution: regenerate both maintained registries as an explicit repair
  candidate. Proof: `generate_api_classification.py --check` and the exact
  hosted documentation command set are the affected rerun; counts, callers,
  classifications, authorization, package version, support, and release truth
  remain unchanged.
- Confirmed root cause: session-document validation is owned by the governed
  session-end workflow rather than a maintained top-level
  `scripts/check_session_docs.py`. Resolution: use the required clean-commit
  `./run.sh session end --agent structural-math` validation after the repair
  candidate is committed. ⚠️ TERMINAL ISSUE: the guessed direct session-doc
  script path did not exist -> use the governed session-end workflow.
- Confirmed root cause: `git_handoff_receipt.py validate` defines its receipt
  as a positional argument. Resolution: rerun it with the exact tracked path as
  the positional value. ⚠️ TERMINAL ISSUE: unsupported `--receipt` option ->
  use the documented positional validation argument.
- Confirmed root cause: the receipt deliberately treats caller-supplied
  authorization and retention evidence older than its freshness limit as
  unknown. Resolution: re-observe the unchanged owner delegation, task/head
  binding, integration non-claim, and retain-all decision, then regenerate the
  receipt. Proof: positional receipt validation passes with the refreshed
  bounded evidence; no authority or deletion scope was added.
- Confirmed root cause: the handoff contract binds `sha256:` to
  `local_state_receipt_hash`, while the preparatory command had used a generic
  file checksum. Resolution: copy the receipt's exact canonical local-state
  hash into the handoff line and rerun the normal commit hooks. The failed
  `check-session-docs` hook is the repair evidence; no commit was created.

### Validation through content freeze

- Consolidated impact-mapped Python checks pass 231 cases across direct beam,
  unit, property, service facade, deprecation, error-schema, API-stability,
  generated-manifest, and private-source-boundary coverage.
- The corrected FastAPI selection passes 24 cases, including the accepted 72
  mm benchmark, explicit result meaning/provenance, strict 0.3 failure, and
  existing effective-depth validation.
- Targeted Black and Ruff pass. Focused mypy reports no issues in the beam core
  and response model. Architecture boundaries report zero violations across
  221 files, and all 2,288 internal imports across 696 Python files resolve.
- The OpenAPI baseline matches 89 endpoints and 444 schemas. The Indian-code
  manifest is current with no capability-status promotion; affected IS 13920
  beam references are registered under their corrected identities.
- Changed-path routing selects Python, FastAPI, control-plane, and docs. The
  broad repository gate remains deferred to cumulative `INDIA-3-IS13920-M0`
  because the bounded checks have no material failure or unknown impact.
- The immutable candidate still requires the sole post-freeze quick gate,
  normal commit hooks, clean-commit `session end`, all required hosted checks,
  unchanged-head merge, and candidate/merge tree equality. Those later facts
  remain external and are not pre-claimed here.

### Preserved holds

- This contract checks beam geometry and calculates requirements; it does not
  accept provided longitudinal steel or link spacing and does not establish
  reinforcement compliance or cumulative IS 13920 engineering acceptance.
- `INDIA-3-COLUMN-R1` and `INDIA-3-IS13920-M0` remain separate sequential
  packets. Wall/foundation detailing and IS 875/1893 remain held.
- No protected/private source byte, text, image, hash, path, or database
  content changed or entered the tracked candidate. Source/distribution,
  support, version, release, package publication, and professional-use
  approval remain separate claims.
- Branch, worktree, archive, source-copy, alias, and unrelated-file deletion
  remain unauthorized.

---

## 2026-08-24 — Session: INDIA-3-JOINT-R1 bounded SCWB contract repair

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/india-3-joint-r1`, from exact hosted
INDIA-3-SOURCE-META-R1 merge
`20b60a047e5c6d88b800f7094dd64fcf4bebad28`, tree
`ff65c71e1b875acdf5c53ee1b9723b4637639717`.

**Git handoff receipt:**
`docs/verification/india-3-joint-r1-git-handoff-receipt.json`

**Focus:** Repair only the G0-bounded IS 13920 beam-column-joint SCWB
contract. Keep the factor fixed at 1.4, encode direction and factored-axial-load
capacity provenance, enforce applicability, represent supported interior and
exterior topologies, and preserve every adjacent formula, source,
distribution, support, version, release, and professional-use hold.

### Summary

- Verified live `origin/main` and merged PR #864 at exact predecessor
  `20b60a04`, tree `ff65c71e`, before creating one source-bound task branch.
  Every unrelated dirty, detached, divergent, or unknown lane remains retained.
- Reproduced the G0 false pass: 250 kNm column capacity against 200 kNm beam
  capacity passed because the implementation used 1.1 and required only 220
  kNm. The corrected fixed 1.4 requirement needs 280 kNm and fails that case;
  equality at 280 kNm passes.
- Removed the caller-controlled factor from the IS 13920 function. A result is
  always labeled with fixed factor 1.4 plus its IS 13920 source/amendment basis,
  so a custom scalar cannot be presented as a standard check.
- Made every result one explicitly bounded principal-plane and shaking-direction
  case. Beam capacities act with the declared shaking direction; column
  capacities must oppose it and retain the exact top/bottom factored axial
  loads plus the required capacity basis. A directional pass is explicitly not
  a whole-joint assessment.
- Enforced known applicability. Roof joints and flat-slab systems receive no
  PASS/FAIL result. Interior topology requires both beam sides; left and right
  exterior topologies require exactly their one present side.
- Kept the repair code-namespace-only. No package-root facade, service,
  FastAPI, React, Excel, generated capability promotion, package version,
  release, source/distribution, support, or professional-use state changed.
  `INDIA-3-BEAM-R1` is next and was not started.

### Issues encountered

- The delegated worktree was clean and at the exact predecessor but detached,
  so it was not `READY_LOCAL` for implementation.
- The existing joint check produced the source-audited false pass and could not
  represent direction, factored-axial-load capacity basis, applicability, or an
  exterior one-beam topology.
- The first focused Ruff sequence stopped before its chained tests because the
  new string enums used the older `str, Enum` inheritance form.
- Focused mypy then rejected branch-inferred fixed-length tuple types in the
  topology helper even though the runtime tests were green.

### Root causes and resolutions

- Confirmed root cause: the delegated lane intentionally began detached at the
  exact requested hosted commit. Resolution: after live fetch, PR, worktree,
  branch, and tree inspection, bind this worktree to
  `codex/india-3-joint-r1` at unchanged `origin/main`. Proof:
  `git_state.py --strict` reports `READY_LOCAL` and runtime diagnosis reports
  `source_bound=true` at exact `20b60a04`.
- Confirmed root cause: commit `c974f362` introduced the entire joint module,
  the 1.1 constant, custom-factor escape hatch, four-scalar input, and tests in
  one change without an independent source-bound benchmark or applicability
  model. The tests therefore repeated the implementation assumption instead of
  falsifying it. Resolution: implement the accepted G0 source map directly as
  a fixed 1.4, keyword-only directional-case contract with explicit capacity
  basis, applicability, and topology. Proof: the independent 250/200 benchmark
  now fails at required 280, the exact boundary passes, and all 29 focused
  cases pass.
- Confirmed root cause: Python 3.11 Ruff rule UP042 requires `StrEnum` rather
  than combined `str, Enum` bases. Resolution: use `StrEnum` for the four
  contract enums. Proof: targeted Ruff and Black checks pass.
- Confirmed root cause: mypy inferred the first interior assignment as a
  two-element tuple and rejected later one-element exterior assignments.
  Resolution: annotate the local collection as `tuple[float, ...]`. Proof:
  focused mypy reports success with no issues.

### Validation through content freeze

- Targeted Black and Ruff pass on the joint owner, shared SCWB error, and direct
  test module. Focused mypy passes on the joint owner.
- Architecture boundaries report zero violations; all 1,513 scanned
  structural-library imports resolve. Documentation frontmatter, links, budget,
  and context validation pass, as do both private-source boundary regressions.
- `Python/tests/codes/is13920/test_joint.py` passes all 29 cases, including the
  independent false-pass benchmark, fixed boundary, rejected override, all
  X/Y positive/negative direction combinations, opposing column direction,
  axial-load basis, roof/flat-slab applicability, and interior/left-exterior/
  right-exterior topology.
- Caller inventory finds only the core definition and its direct test helper;
  no service or transport migration is required. Changed-path routing selects
  Python, FastAPI, and documentation; the broad repository gate remains
  deferred to the cumulative INDIA-3 milestone unless a material failure
  requires it.
- The immutable candidate still requires the sole post-freeze quick gate,
  normal commit hooks, clean-commit `session end`, all required hosted checks,
  unchanged-head merge, and candidate/merge tree equality. Those later facts
  remain external and are not pre-claimed here.

### Preserved holds

- One directional case is not a whole-joint or cumulative IS 13920 engineering
  acceptance claim. Both shaking directions in every applicable principal
  plane remain caller-owned inputs to later cumulative acceptance.
- `INDIA-3-BEAM-R1`, `INDIA-3-COLUMN-R1`, and `INDIA-3-IS13920-M0` remain
  separate sequential packets. Wall/foundation detailing and IS 875/1893
  remain held.
- No protected/private source byte, text, image, hash, path, or database content
  changed or entered the tracked candidate. Source/distribution, support,
  version, release, package publication, and professional-use approval remain
  separate claims.
- Branch, worktree, archive, source-copy, alias, and unrelated-file deletion
  remain unauthorized.

---

## 2026-08-24 — Session: INDIA-3-SOURCE-META-R1 private catalogue repair

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/india-3-source-meta-r1`, from exact hosted INDIA-3-G0 merge
`c0e34235b485799d26fcb55df45f74ed9104e003`, tree
`62b22ce2a6930fc77954b8e0cd93c4d6b987bbf1`.

**Git handoff receipt:**
`docs/verification/india-3-source-meta-r1-git-handoff-receipt.json`

**Focus:** Repair only ignored private IS 13920 catalogue document-kind,
page-content, and actual visual-renderability metadata. Preserve every source
byte and alias; do not change formulas, runtime/API behavior, tests to bless a
formula, support status, version/release state, or professional-use approval.

### Summary

- Verified PR #863 merged as exact hosted `c0e34235`, then created one fresh
  source-bound Codex lane at that commit. All unrelated lanes remain untouched.
- Corrected the base acquisition identity from base-only `STANDARD` to
  `STANDARD_WITH_APPENDED_AMENDMENTS`, classified the consolidated source as a
  candidate with appended amendments, and classified all four byte-distinct
  amendment sources as standalone copies. Exact source IDs, logical IDs,
  source bytes, cached text, hashes, paths, and aliases were not changed.
- Added a private schema-v2 content-range map, a repeatable metadata-application
  command, and separate page/document renderability states. The private tool,
  seed, database, and source material remain under the existing Git-ignore
  boundary and are not part of the tracked candidate.
- Rendered all 84 retained IS 13920 pages one by one: all 84 produced page
  images, 42 also emitted parser warnings, and zero failed. The warning-bearing
  pages remain truthfully distinct from clean renders; neither state is an
  engineering/source acceptance claim.
- Private verification passes at 25 documents, 27 aliases, 732 cached pages,
  142 text-layer visual-review pages, 84 render-checked IS 13920 pages, and zero
  render failures. The six IS 13920 identities, eight aliases, four standalone
  amendment copies, and two exact duplicate aliases all remain retained.
- Added aggregate tracked evidence only. It contains no protected bytes, prose,
  extracted text, page image, private hash value, or private absolute path.
  `INDIA-3-JOINT-R1` is next in the owner-authorized sequence and was not
  started here.

### Issues encountered

- The delegated worktree was clean and exact-main but detached, so governed
  session start could not produce `READY_LOCAL` until the task branch existed.
- Existing metadata could not distinguish acquisition intent from actual page
  composition, and the existing visual flag described text extraction rather
  than whether a renderer produced a page.
- Poppler produced parser warnings for 42 pages across three retained source
  identities even though all 84 pages rendered successfully.
- A diagnostic page-by-page shell probe yielded after 30 seconds while its
  process continued, so only the first document summary was returned in that
  call.
- One diagnostic SQL aggregation joined aliases and pages directly, doubling
  displayed page counts for the two identities with two aliases.
- Preparation-mode session synchronization detected pre-existing global API
  count drift and rewrote one out-of-scope onboarding line.
- The repository safety deleter rejected two generic scratch filenames because
  basename search found unrelated maintained references elsewhere.

### Root causes and resolutions

- Confirmed root cause: the delegated lane intentionally began detached at the
  exact requested commit. Resolution: after live remote, worktree, and PR
  inspection, create `codex/india-3-source-meta-r1` at unchanged `origin/main`.
  Proof: `git_state.py --strict` reports `READY_LOCAL` and runtime diagnosis
  reports `source_bound=true` at exact `c0e34235`.
- Confirmed root cause: seed document kinds represented filenames/acquisition
  intent, while the deduplication path preserved aliases without a mechanism to
  update canonical metadata already stored in SQLite. Resolution: add explicit
  page-range content identity plus a hash-bound metadata application command;
  update only six IS 13920 document rows. Proof: schema v2 reports the corrected
  kinds and complete page maps while document, alias, page, source-ID, logical-
  ID, and byte-verification counts remain unchanged.
- Confirmed root cause: `visual_review_required` is calculated only from
  extracted-text length and never invokes a PDF renderer. Resolution: keep that
  flag intact, add independent page/document renderability states, and run
  `pdftoppm` page by page with output and warning classification. Proof: 84/84
  pages render; 42 record parser warnings; zero record render failure.
- The exact internal cause of the warning-bearing PDF operators was not needed
  for this bounded metadata packet and remains `unconfirmed`; suppressing the
  warnings would make the catalogue less truthful. Resolution: retain the
  warnings as metadata and expose both warning-bearing and clean-rendering
  retained copies without silently preferring either. Proof: all four standalone
  amendment copies and both 33-page base/consolidated identities remain
  hash-verified and available.
- Confirmed root cause: the long shell diagnostic used a 30-second yield while
  rendering many pages serially. Resolution: use the maintained private command
  as a resumable terminal process and poll its session to completion. Proof: the
  governed command exited zero with all 84 pages classified. ⚠️ TERMINAL ISSUE:
  the first serial page probe outlived its 30-second yield -> the maintained
  render-audit command completed through the returned terminal session.
- Confirmed root cause: the first aggregate query formed a many-to-many result
  by joining page and alias rows before counting. Resolution: use correlated
  per-document counts for evidence. Proof: the corrected results report six and
  three pages for each amendment copy and eight IS 13920 aliases in total.
- Confirmed root cause: `session sync --fix` refreshes repository-wide metrics,
  including owners outside this documentation-only packet. Resolution: restore
  the unrelated onboarding line exactly and retain only task-owned paths. Proof:
  the final changed-path set excludes that file. ⚠️ TERMINAL ISSUE: preparation
  sync touched an unrelated metric owner -> reversed only its exact generated
  line with no change to the user's surrounding content.
- Confirmed root cause: the safe deleter conservatively searches basenames, so
  generic render scratch names collided with unrelated words in maintained
  files even though the files lived under the task's ignored temporary root.
  Resolution: validate the exact absolute task temp directory, delete only its
  remaining regular files with `unlink`, and remove only now-empty directories.
  Proof: the exact temp root no longer exists while private archive verification
  still passes. ⚠️ TERMINAL ISSUE: `safe_file_delete.py` held generic scratch
  names on false reference matches -> used exact-root `unlink` only for ignored,
  regenerable render intermediates; no archive/source/alias was targeted.

### Validation through content freeze

- Private syntax/seed validation, schema migration, metadata application,
  page-by-page render audit, SQLite/source/cache/FTS verification, Git-ignore
  checks, and the focused private-boundary regression pass.
- Tracked scope is limited to this session/task/handoff and aggregate evidence.
  Private archive files and render intermediates remain ignored; runtime,
  formula, generated capability, API, test, package, and release paths are
  unchanged.
- The frozen focused documentation/boundary checks, sole quick gate, normal
  staged hooks, immutable local candidate, clean-commit session end, and hosted
  checks follow. A broad runtime gate is not selected by this metadata-only
  packet.

## 2026-08-24 — Session: INDIA-3-G0 IS 13920 source-to-result decision

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/india-3-g0-acceptance`, from exact post-LIB-PRO-008 hosted
commit `3bcc34223d8eaf236c62a5f54dfe4b7960876457`, tree
`337c74aa7028ce95939043ccb2acf2e106ce82d0`.

**Git handoff receipt:**
`docs/verification/india-3-g0-audit-decision-git-handoff-receipt.json`

**Focus:** Complete the bounded existing-surface audit for IS 13920 beam,
column, and strong-column/weak-beam joint claims. Resolve the exact
edition/amendment chain, map every current calculation and outcome-changing
default, freeze independent benchmarks and unsafe cases, reconcile public
truth, and classify each family without changing formulas or support status.

### Summary

- Created one fresh source-bound lane at exact hosted `3bcc3422`; the older
  INDIA-3 candidates and unrelated dirty detached worktree remain untouched.
- Reverified the ignored private archive at 25 documents, 27 aliases, 732
  cached pages, and 142 visual-review pages. Complete governing base and
  amendment pages were visually reviewed; extracted text was navigation only.
- Resolved the page-bound chain as IS 13920:2016 First Revision plus Amendment
  1 (September 2017) and Amendment 2 (November 2020). Reaffirmation in 2021 is
  separate from edition/amendment identity. Both byte-distinct copies of each
  amendment are normalized-text equal page by page and remain preserved.
- Official BIS material available in June 2026 still identifies IS 13920:2016
  as published while the split successor remains under development. The draft
  successor was not used as an Indian Standard.
- Independently reproduced outcome-changing source/code or source/contract
  mismatches for beam, column, and joint. All three families are
  `REPAIR_PACKET_REQUIRED`; none is `ACCEPT_CURRENT_BOUNDED`.
- Froze separate source-metadata, beam, column, and joint repair packets plus
  one cumulative IS 13920 acceptance gate. No formula, runtime surface,
  generated support status, package version, or release state changed.

### Issues encountered

- Primary `main` was clean but one commit behind exact hosted `origin/main`.
- The private catalogue's file-level labels were insufficient: one identity
  labelled as a base includes appended amendment sheets, and one consolidated
  copy did not render every appended amendment page reliably.
- The first FastAPI model search included two guessed paths that do not exist.
- The system exposed `pdftoppm` but not `pdftotext`; the PDF runtime also did
  not contain PyMuPDF under the `fitz` import name.
- The first front-matter check rejected `status: complete` because the
  maintained schema uses `archived` for a terminal plan.
- The first hosted documentation job rejected the compatibility ledger after
  the G0 decision added two maintained public-facade references.
- Existing beam tests encode the pre-amendment eight-bar spacing rule; column
  tests encode obsolete clause numbers and only one confinement-area
  expression; joint tests encode a 1.1 factor.
- Beam accepts the exact ratio boundary and non-finite material input, column
  omits a governing confinement expression and reports compliance using hidden
  geometry defaults, and joint returns a false pass under its default factor.

### Root causes and resolutions

- Confirmed root cause: the primary anchor had not been fast-forwarded after
  PR #862, although `origin/main` was current and clean. Resolution: create the
  task branch/worktree directly from exact `origin/main` without mutating the
  primary checkout. Evidence: `git_state.py --strict` reports `READY_LOCAL`,
  equal to `origin/main`, and runtime diagnosis reports `source_bound=true`.
- Confirmed root cause: document-kind metadata described acquisition intent,
  not reliable page-level engineering identity, and one PDF has an incomplete
  visual layer for appended amendment pages. Resolution: bind decisions to the
  visually reviewed base pages plus standalone Amendment 1 and Amendment 2
  copies; retain every source and freeze a separate private metadata repair.
  Evidence: both amendment-copy pairs are normalized-text equal page by page,
  and complete governing pages were visually reviewed. No private source was
  changed or tracked.
- Confirmed root cause: the Pydantic models live under
  `fastapi_app/models/`, not the two guessed module paths. Resolution: use the
  discovered `compliance.py` and `column.py` owners. Evidence: exact beam and
  column request/response contracts were mapped. ⚠️ TERMINAL ISSUE: guessed
  FastAPI paths made one read-only `rg` command exit 2 -> reran against files
  discovered under `fastapi_app/models/`.
- Confirmed root cause: this host's Poppler installation contains the renderer
  but not the text CLI, and the bundled PDF environment supplies `pdfplumber`
  rather than `fitz`. Resolution: keep Poppler for visual PNG review and use
  bundled `pdfplumber` only to compare amendment-copy text without emitting
  source expression. Evidence: both amendment pairs compare equal page by
  page. ⚠️ TERMINAL ISSUE: `pdftotext` and then `fitz` were unavailable -> used
  the installed `pdfplumber` fallback.
- Confirmed root cause: the audit outcome and the document-state vocabulary are
  separate contracts; `complete` is an outcome phrase but not an allowed
  front-matter status. Resolution: retain the explicit G0-complete decision in
  the body and set the terminal plan metadata to `archived`. Evidence: the
  repeated 359-document front-matter check reports zero invalid files.
- Confirmed root cause: the compatibility generator treats tracked
  documentation references to public facades as caller records. The G0 machine
  decision added `check_beam_ductility` and
  `check_column_ductility_is13920`, while local docs-only commit hooks did not
  select the generator that hosted documentation validation runs
  unconditionally. Resolution: regenerate only the maintained compatibility
  ledger and rerun only the failed documentation path; do not rerun unrelated
  runtime domains. Evidence: caller records move exactly from 1,502 to 1,504,
  both additions are `OUT_OF_SCOPE_PRESERVED` references from the G0 decision,
  zero callers are ambiguous, and generator `--check` passes.
- Confirmed root cause: current tests reproduce implementation constants and
  were never bound to the complete amendment chain. Resolution: treat them as
  software-regression baseline only and originate G0 benchmarks from the
  reviewed source. Evidence: the beam benchmark requires 72 mm but current code
  returns 96 mm; the joint benchmark requires 280 kNm but current code requires
  220 kNm and returns a false pass.
- Confirmed root cause: the beam module applies the pre-Amendment-1 link rule,
  treats a strict source boundary as inclusive, validates inputs only with
  comparison operators, and labels calculated requirements as compliance.
  Resolution: classify beam as `REPAIR_PACKET_REQUIRED` and freeze the exact
  source, finite-input, result-semantics, metadata, and transport repair scope.
  Proof: the live benchmark, exact boundary, `NaN`, and missing-provided-steel
  cases reproduce every outcome difference.
- Confirmed root cause: the column module was written against a different
  clause organization, maps unrelated longitudinal percentages to the SCWB
  clause, implements only the first rectangular confinement-area expression,
  invents a 40 mm cover/core, and has no provided-reinforcement or axial
  applicability state. Resolution: classify column as
  `REPAIR_PACKET_REQUIRED` and freeze a separate repair contract. Proof: the
  second-expression case requires 277.108 mm2 while current code returns
  181.037 mm2; the core accepts `NaN`, and the service reports compliant
  without actual confining steel.
- Confirmed root cause: the joint module uses a non-source 1.1 default and a
  four-scalar contract that cannot encode the required shaking direction,
  axial-load column-capacity basis, or applicability. Resolution: classify
  joint as `REPAIR_PACKET_REQUIRED` and freeze a direction/provenance/domain
  repair packet. Proof: column capacity 250 kNm versus beam capacity 200 kNm
  is a source failure at factor 1.4 but a current-code pass at factor 1.1.

### Validation through content freeze

- Private archive verification passes with zero private material tracked or
  packaged; all source copies remain retained.
- Independent runtime reproducers bind exact beam, column, and joint expected
  versus current results on source-bound `3bcc3422`.
- The G0 machine decision contains source identity, normalized source maps,
  benchmarks, boundary/inadequate/invalid/out-of-domain cases, cross-surface
  reconciliation, and the frozen follow-on sequence without protected prose,
  page images, extracted text, private hashes, or private paths.
- The existing focused IS 13920 regression baseline passes 63 tests. This is
  software continuity evidence only, not source acceptance. Front-matter,
  maintained-link, and context validation pass with zero invalid or broken
  records.
- The final frozen quick gate, normal staged hooks, immutable candidate audit,
  and hosted checks follow. The first hosted documentation job exposed the
  two-record compatibility-ledger freshness repair above; its exact failed path
  is impact-mapped for one repair-candidate rerun. The broad runtime gate
  remains deferred because G0 changes no runtime behavior.

## 2026-08-24 — Session: LIB-PRO-008 pre-INDIA-3 safety closure

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/lib-pro-008-pre-india3-safety`, from exact clean hosted-main
commit `e2fac7419551988def59101ac63a5f8e491bc7a2`.

**Git handoff receipt:**
`docs/verification/lib-pro-008-pre-india3-safety-git-handoff-receipt.json`

**Focus:** Repair only the confirmed software safety and verification defects
that block a trustworthy INDIA-3-G0 start. No IS 13920 formula, support claim,
version/release, professional-use decision, or destructive lane action is in
scope.

### Summary

- Reproduced the newer review's WebSocket load-case-only false calculation and
  compatibility drift on exact `e2fac741`, plus the older torsion `NaN`
  false-safe path. Preserved the unrelated dirty detached worktree.
- Made WebSocket check geometry/material/cover fields required, replaced loose
  case dictionaries with a fail-closed typed model, and rejected unknown or
  non-finite fields. Added the exact reproducer to the public-route safety gate.
- Bound all public torsion helpers and the composed design to finite-real intake
  before arithmetic, including every scalar that previously allowed `NaN` to
  propagate into a safe result.
- Replaced repository-wide compatibility walking with Git's tracked source
  allowlist plus a safe source-archive fallback, regenerated only the stale
  compatibility ledger, and made documentation CI run its freshness check.
- Completed the stirrup-path geometry boundary and rejected multi-leg output
  that the single closed-loop return type cannot represent.
- Focused Python, FastAPI, compatibility, and repaired geometry evidence pass.
  The readiness audit remains truthfully `PARTIAL` at 23/24 with zero failures:
  its longstanding broad input-ownership diagnostic still reports 359
  `UNPROVEN` parameters outside this bounded packet.

### Issues encountered

- The canonical session start was initially blocked by an unmatched
  `INDIA-3-G0` usage timer even though its candidate had already merged through
  PR #861.
- The first readiness audit after fixing the two displayed stirrup parameters
  moved its abbreviated warning to the remaining section-geometry inputs; after
  the complete local boundary repair, the warning moved to unrelated existing
  functions instead of clearing.
- The compatibility generator produced different outcomes in the normal
  checkout and a source archive because it walked ignored generated HTML in
  `site/`; the checked-in ledger was also two tracked documentation callers
  behind.
- The maintained `session summary --write` command replaced the task-authored
  summary with the four already-merged predecessor commit subjects because the
  current packet had no commit yet.
- The first normal hook run reformatted one FastAPI assertion and rejected the
  replacement handoff table because its required exact `Next` row was absent.
- Initial hosted documentation validation exposed a second compatibility
  environment dependency: three DXF stub projections changed kind/signature
  when the optional `ezdxf` package was absent.

### Root causes and resolutions

- Confirmed root cause: the merged INDIA-3-G0 run had no usage closeout record,
  so session enforcement correctly prevented a second active timer. Resolution:
  reconcile the exact candidate `b39fcda5`, PR #861, merge `e2fac741`, hosted
  run, phase allocation, and counters before starting LIB-PRO-008. Evidence:
  the G0 closeout records 50.063 minutes and the LIB-PRO-008 session begins
  normally. ⚠️ TERMINAL ISSUE: session start was blocked by the unmatched G0
  timer -> recorded its already-merged closeout before opening this task.
- Confirmed root cause: `compute_stirrup_path` had no complete intake boundary;
  the readiness report displays only the tail of a much larger diagnostic, so
  fixing the displayed names cannot make that repository-wide diagnostic pass.
  Resolution: validate the entire function boundary because it is in scope,
  reject geometrically impossible/multi-leg output, and retain the broader
  diagnostic as a truthful warning rather than chasing unrelated functions.
  Evidence: all 69 geometry tests pass; the audit reports zero failed checks and
  its remaining sample no longer names `compute_stirrup_path`.
- Confirmed root cause: the compatibility scan used `os.walk` over the live
  filesystem, so ignored build output became false caller evidence, while docs
  CI did not own the freshness command. Resolution: use `git ls-files` as the
  maintained checkout allowlist, retain a filtered archive fallback, refresh
  the 1,502-caller ledger, and run `--check` in documentation validation.
  Evidence: the compatibility module and generator check pass with zero blocked
  ambiguous callers; focused CI-contract tests pass.
- Confirmed root cause: comparison-only validation lets IEEE `NaN` bypass
  `<=` checks, and the WebSocket model encoded structural defaults plus an
  untyped case list. Resolution: normalize every torsion scalar through the
  shared finite validator and require typed WebSocket engineering input before
  calling the service. Evidence: all exact `NaN` and missing-input reproducers
  raise/return input errors; no safe calculation payload is produced.
- Confirmed root cause: the summary writer derives its body from committed Git
  history, so before candidate creation it selected the predecessor merge set
  instead of current uncommitted work. Resolution: retain its correctly
  generated handoff block but restore the task-owned summary and do not rerun
  the writer before candidate freeze. Evidence: the newest session entry again
  describes only LIB-PRO-008. ⚠️ TERMINAL ISSUE: pre-commit session summary
  inserted predecessor commits -> restored the task-owned summary while
  retaining the generated receipt handoff block.
- Confirmed root cause: Ruff's formatter and the FastAPI Black hook use
  different preferred layouts for the pre-existing assertion, while the
  session-document contract requires literal `Current` and `Next` table keys.
  Resolution: retain Black's staged format and restore the exact `Next` row.
  Evidence: the focused session-document checker and repeated normal hooks
  pass. ⚠️ TERMINAL ISSUE: first normal hooks stopped on one formatter write
  and the missing exact row -> accepted the hook format and restored the
  required handoff key.
- Confirmed root cause: root-stub ledger identity used live Python object kind
  and signature for `ezdxf`, `units`, and `TextEntityAlignment`; those aliases
  are exact delegates but are intentionally `None` without the optional DXF
  extra. Resolution: preserve the exact runtime object-identity assertion while
  encoding those three records as stable optional-dependency proxies whose
  ledger identity does not depend on the installed extra. Evidence: the focused
  compatibility/CI selection passes 69 tests, and `--check` passes in both the
  normal project environment and a clean documentation-only environment with
  no `ezdxf`. ⚠️ TERMINAL ISSUE: initial hosted documentation validation found
  the stale ledger -> reproduced it in a clean local docs profile and removed
  the optional-dependency identity drift at its generator owner.

### Validation through content freeze

- Focused Python selection passes 187 tests; the audit-driven affected geometry
  rerun passes 69 tests. Focused WebSocket passes 12 tests.
- API classification and compatibility check is current; the packed ledger has
  1,502 caller records and zero blocked ambiguous callers.
- The repaired compatibility/CI selection passes 69 tests, and the exact
  documentation-only dependency profile now passes ledger freshness without
  installing the optional DXF extra.
- Readiness audit passes 23/24 checks with zero failures and one expected broad
  input-ownership warning. The warning is not release or engineering approval.
- Frozen quick/full gates, normal staged hooks, immutable candidate review,
  final read-only session validation, and applicable hosted checks follow.

## 2026-08-24 — Session: INDIA-3-G0 IS 13920 truth-audit readiness

**Agent:** Codex (`library-expert`, sole writer; no subagents)

**Branch:** `codex/india-3-g0-truth-audit`, from exact M0 hosted-main commit
`3e9796872fbf79bf4d0a7c09c018e4978664f079`, tree
`f673e604a3647973345d2cd07ef48f2cabc4b93f`.

**Git handoff receipt:**
`docs/verification/india-3-g0-truth-audit-git-handoff-receipt.json`

**Focus:** Reconcile the completed M0 boundary, preserved source-library work,
private archive readiness, and the exact existing IS 13920 beam/column/joint
surface into one implementation-ready G0 audit packet. No structural formula,
public signature, transport response, capability promotion, IS 875/1893 work,
release, or professional-use approval is authorized.

### Summary

- Confirmed M0 merged through PR #860 at hosted `3e979687`, from reviewed
  candidate `eb92db48`, with exact candidate/merged tree `f673e604` and all
  required hosted checks green.
- Created a fresh source-bound INDIA-3-G0 lane from exact hosted M0. Preserved
  the older `9c976b1f` source-library candidate and the unrelated dirty detached
  worktree without reset, stash, clean, rebase, deletion, or cherry-pick.
- Reverified the ignored private archive: 25 documents, 27 aliases, 732 cached
  pages, three project-authored navigation records, and 142 visual-review
  pages. All six IS 13920 identities and all three implementation claims remain
  unreviewed; accepted normalized engineering values remain zero.
- Inventoried the exact current beam, column, and joint core/service/HTTP/test
  surfaces and the generated three-supported/two-held claim. Identified the
  source/amendment, clause-map, registration metadata, default/domain,
  independent-benchmark, and cross-transport questions that G0 must decide.
- Froze one audit order and explicit acceptance criteria. The readiness verdict
  is `READY_FOR_BOUNDED_G0_AUDIT`, not ready for formula implementation,
  support promotion, broader companion codes, or release.

### Issues encountered

- The remembered private-library readme path `README.md` did not exist.
- The first two normalized-reference queries guessed a `standard_code` column
  that is not present on either the normalized-reference or document table.
- The preserved `9c976b1f` candidate differs widely from current M0 because it
  was created before the intervening product packets; a direct candidate-to-M0
  diff is therefore not a safe transplant list.
- The first normal commit-hook attempt stopped because the new handoff brief
  used `Required reading` instead of the checker's exact required
  `Required Reading` heading. The narrow repair check then exposed that the
  manually replaced brief also omitted its generated Date/receipt handoff
  block.

### Root causes and resolutions

- Confirmed root cause: the private boundary intentionally names its guide
  `README_PRIVATE.md`. Resolution: locate the private files first and read the
  existing guide; the archive verifier and database were intact. Evidence: the
  private verifier reports `VERIFIED` for all 25 documents and 732 pages.
  ⚠️ TERMINAL ISSUE: remembered `README.md` did not exist -> located and used
  `README_PRIVATE.md`.
- Confirmed root cause: the normalized-reference schema stores the joined
  standard identity as `documents.standard_id`, not `standard_code`.
  Resolution: inspect the SQLite schema and join on `documents.id` while
  selecting `documents.standard_id`, without reading or emitting protected
  normalized text. Evidence: the corrected query returns exactly three
  `UNREVIEWED_IMPLEMENTATION_CLAIM` navigation records for beam, column, and
  joint. ⚠️ TERMINAL ISSUE: guessed `standard_code` did not exist -> inspected
  the schema and used `documents.standard_id`.
- Confirmed root cause: PR #849 already merged the durable source boundary at
  `40aa5864`, while the retained candidate also carries stale shared handoff
  files and lacks the later product history. Resolution: retain it as evidence,
  create the fresh task lane from exact M0, and author only the reconciled G0
  readiness packet. Evidence: fresh lane is `READY_LOCAL`, equal to
  `origin/main`, clean before edits, and `source_bound=true`.
- Confirmed root cause: the session-document checker treats its maintained
  section titles and generated handoff block as an exact contract; replacing
  the brief manually removed that block. Resolution: correct the heading,
  retain the six existing links and all G0 content, then use the maintained
  handoff command to generate the Date and receipt identity. Evidence: the
  narrow session-document check and the repeated normal commit hooks pass.
  ⚠️ TERMINAL ISSUE: first commit stopped on the exact handoff contract ->
  corrected `Required Reading`, generated the maintained Date/receipt block,
  and committed through normal hooks.

### Validation through content freeze

- Private archive verification passes for 25 documents, 27 aliases, 732 cached
  pages, three normalized navigation records, and 142 visual-review pages.
- The private-boundary tests plus existing beam unit/property, column, and joint
  baselines pass 63 tests. This is a software-baseline result only; it does not
  accept the current formulas or claims as source-correct.
- Documentation passes all five maintained checks with only existing soft
  metadata/budget warnings; 998 maintained links resolve with zero broken;
  context validation passes its 10 areas and six authorities.
- The frozen quick gate passes 10/10 with zero reused results. The broad gate is
  deferred because this packet changes no behavior, public contract, generated
  truth, or runtime surface. Normal staged hooks, immutable commit, final
  read-only session validation, and hosted checks follow.

## 2026-08-24 — Session: LIB-PRO-007-M0 cumulative acceptance

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/lib-pro-007-m0-cumulative-acceptance`, from exact merged P7
hosted-main commit `823b39896a53fde7e4c5e0805faa8ec02e075ee5`, tree
`e5b1e9eecf590f996028058edee2b03d09095e6a`.

**Git handoff receipt:**
`docs/verification/lib-pro-007-m0-cumulative-acceptance-git-handoff-receipt.json`

**Focus:** Run the single cumulative P1-P7 software acceptance across broad
Python, FastAPI, React, architecture/import/parity, exact installed-wheel, and
production website surfaces; repair only confirmed integration defects. Excel
remains conditional on an Excel-surface change. Release, professional or
engineering-use approval, live ETABS/EDB/model control/save/write-back,
INDIA-3 formulas/source promotion, and branch/worktree deletion remain held.

### Summary

- Preserved every unrelated lane and created a fresh source-bound M0 worktree
  from the exact P7 hosted commit/tree. The held INDIA-3 candidate remains
  `9c976b1f` and the separately dirty detached lane remains untouched.
- Repaired one impossible historical bar-selection test fixture and reconciled
  the retained unit/registration metadata for two P3 anchorage functions. No
  calculation formula or public signature changed.
- Migrated the maintained React catalogue caller from catalogue 1.2.0 to 1.3.0
  after the live production journey proved the old request forced a visible
  manual-form fallback. The beam capability remains 1.2.0 and the FastAPI
  response contract is unchanged.
- Passed the repaired broad suites, architecture/import/circular validation,
  cross-layer parity, one exact-wheel installation, CLI/product vectors, and a
  production home/quick-beam/gravity browser journey with zero console, page,
  or request failures.
- Changed no Excel workbook or Office.js file, so installed Windows Excel is
  `NOT_REQUIRED_UNCHANGED_SURFACE`. Removed no export, signature, file, branch,
  worktree, archive, fixture, or vendor/reference item and activated no
  retirement candidate.

### Issues encountered

- The first cumulative Python run failed three tests: an auto-selected 25 mm
  bar fixture returned 32 mm, the clause-quality inventory found two missing
  unit contracts, and the committed Indian-code manifest was one registration
  behind.
- The first production quick-beam journey visibly reported `Unsupported
  catalogue version '1.3.0'` and forced the reviewed manual-form fallback even
  though calculation and HTTP routes remained available.
- The browser-verification skill's preferred `agent-browser` executable was not
  installed, and the Node runtime's ESM loader could not import the temporary
  Playwright entry point directly.
- Sending Ctrl-C to the production preview through `node_runtime.py` stopped
  the listener but the wrapper surfaced `KeyboardInterrupt` with exit code 1.
- The first full repository gate passed 29 of 31 checks but rejected the stale
  compatibility ledger and the P7 migration guide's uncontrolled `doc_type`.

### Root causes and resolutions

- Confirmed root cause: six 25 mm bars required for 2,500 mm2 cannot satisfy
  the maintained clear-spacing rule in a 230 mm beam with one layer, so the
  production selector correctly advances to 32 mm. The P3 anchorage packet also
  introduced two clause-decorated functions without registering their exact
  retained `bar_dia` millimetre signatures or regenerating the clause manifest.
  Resolution: use a 350 mm fixture that actually exercises the 25 mm branch,
  add only the two function-level legacy-unit records, and regenerate the
  maintained manifest. Evidence: the three exact reproducers pass and the
  repaired broad Python suite passes 6,934 tests.
- Confirmed root cause: the earlier gravity-composition work advanced the
  catalogue document to 1.3.0 while the React request, parser type, and fixtures
  remained pinned to 1.2.0. The contained beam capability deliberately remains
  1.2.0. Resolution: advance only the maintained React catalogue transport to
  1.3.0. Two focused files pass four tests, the production rebuild passes, and
  the repeated live route displays catalogue 1.3.0 without fallback.
- Confirmed root cause: the installed browser skill did not provide its CLI in
  this environment, while Node's ESM loader treated Playwright's CommonJS
  bridge incompatibly. Resolution: install `playwright-core` in a temporary
  directory, load it through `createRequire`, and launch the installed system
  Chrome headlessly through the persistent Node browser runtime. The complete
  production journey passes. ⚠️ TERMINAL ISSUE: `agent-browser` was absent and
  direct Playwright ESM import failed -> used the temporary CommonJS runtime
  with system Chrome.
- Confirmed root cause: `node_runtime.py` waits in `subprocess.run`, so the
  interactive Ctrl-C reaches the Python wrapper as `KeyboardInterrupt` after
  terminating Vite. Resolution: verify both ports with `lsof`; neither 4173 nor
  8000 retained a listener. No production process remained. ⚠️ TERMINAL ISSUE:
  preview Ctrl-C returned exit 1 -> verified graceful listener shutdown
  directly.
- Confirmed root cause: the compatibility ledger records maintained caller
  paths and content, so migrating the React catalog request changed its
  deterministic input; P7 also used `doc_type: migration`, outside the
  repository's closed front-matter vocabulary. Resolution: regenerate the API
  classification/ledger through its maintained generator and classify the
  migration document as a guide. The ledger reconciles 620/620 projections,
  records 1,500 callers with zero ambiguity, and both failed checks pass
  narrowly. The full repaired-candidate gate is the required retry evidence.

### Validation through content freeze

- Source binding: hosted P7 base `823b3989`, tree `e5b1e9ee`,
  `source_bound=true`; all sibling worktrees remain preserved.
- Broad Python: first attempt 3 failures, three exact repair reproducers pass,
  repaired attempt 6,934 passed / 3 skipped / 6 deselected. FastAPI passes
  491. React initially passes 52 files / 283 tests plus lint/build; the affected
  catalogue selection passes 2 files / 4 tests plus a production rebuild.
- Architecture checks 222 files with zero violations; imports check 695 files
  with zero broken imports; circular validation checks 202 files with no cycle;
  three canonical parity vectors pass and the actionable cross-layer score is
  100%.
- Exact wheel SHA-256 is
  `0a42d90e432b5b9d86d12b3fec4373ac1b95a253646e0a18fdcf135f143347ca`.
  Its isolated installation passes 5,920 tests / 51 skips / 2 deselections,
  job/critical/report CLI flow, Python/CLI/FastAPI `d_mm=443` identity with
  truthful `FAIL`, and all 29 negative-UAT cases. Professional approval remains
  false and qualified review remains required.
- The production website loads home and catalogue 1.3.0, changes calculation
  identity after editing beam width from 300 to 350 mm, and returns current
  `PASS` with 5/5 checks. The maintained gravity request has 26 zero-residual
  boundaries, immutable model/load/ledger/result hashes, and truthful
  `HOLD 6 / PASS 5` with
  `BEAM_SUPPLIED_REINFORCEMENT_NOT_SUPPLIED`. Console errors, page errors, and
  failed requests are all zero.
- The frozen quick gate passed 10/10 with zero reused results. The first full
  gate passed 29/31; its two generated/governance owners now pass narrowly and
  the repaired full-gate retry remains. Normal staged hooks, immutable
  candidate, push, and required hosted checks follow. The machine evidence
  states cumulative software compatibility only; it does not authorize
  release, professional use, live ETABS/write-back, or INDIA-3 engineering
  claims.

## 2026-08-24 — Session: LIB-PRO-007-P7 compatibility convergence

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/lib-pro-007-p7-compatibility-convergence`, from exact merged
P6 hosted-main commit `6cb4722103bfc018dc3889fcc1a5a437e3579897`, tree
`d2b3efa3243d06e2bfff8ff1990db19eac282eb5`.

**Git handoff receipt:**
`docs/verification/lib-pro-007-p7-compatibility-convergence-git-handoff-receipt.json`

**Focus:** Converge maintained compatibility callers after P1-P6, prove every
retained facade/module projection delegates to an exact canonical owner or a
documented formula-free namespace adapter, and hold legacy P5 ETABS shapes
truthfully. Public deletion, signature breaks, cumulative M0, live ETABS/EDB,
installed Excel, INDIA-3 engineering, release, and professional approval remain
excluded.

### Summary

- Extended the maintained API-classification generator with a deterministic
  compatibility ledger. It remeasures 222 package-root, 199 service-facade, and
  199 legacy-facade exports and reconciles all 620 facade projections exactly.
- Proved function/class/value projections by exact object and signature. Module
  compatibility namespaces carry per-symbol owner maps because Python can bind
  an explicitly imported submodule over a package attribute; no module wrapper
  contains a structural formula.
- Accounted for 45 root compatibility modules, 520 exact symbol projections,
  the 87-name `api_hub` identity subset, existing import-warning metadata, and
  every detected maintained/intentional/preserved caller. Zero maintained
  callers remain ambiguous.
- Migrated maintained implementation code, active scripts, examples, and
  current user/developer documentation to owning modules or the deliberate
  package-root facade. Compatibility tests and policy/migration examples remain
  preserved so old imports continue to be verified.
- Marked `normalize_etabs_forces`, `load_etabs_csv`,
  `create_job_from_etabs`, and `create_jobs_from_etabs_csv` as
  `HELD_COMPATIBILITY` with no removal version. They cannot be described as P5
  accepted snapshots. `ETABSAdapter` remains the canonical parser delegate used
  through lossless intake.
- Found no caller-free second calculation path or unsafe contract requiring a
  retirement candidate. No export, signature, file, branch, worktree, archive,
  fixture, or vendor/reference item was removed or rewritten.

### Issues encountered

- The app-created worktree started detached, although it was clean and already
  at the exact hosted P6 base.
- The frozen plan, task board, and next-session brief still described P6 as
  active after PR #858 had merged.
- The first caller-ledger implementation exceeded 60 seconds and had to be
  interrupted.
- The live export counts had grown from the G0 baseline of 205/182/182 and 447
  compatibility entries to 222/199/199 and 498 compatibility entries.
- Four root-stub docstrings named pre-restructure replacement modules.
- The first focused ledger test found that module projection identity and a
  `typing.Literal` alias were misrepresented by generic `__module__` /
  `__qualname__` introspection. It also exposed ten import paths with real
  `DeprecationWarning` behavior that the first ledger draft called
  non-deprecated.
- The first P5 held-metadata assertion assumed every limitation sentence used
  the word `snapshot`, while the JobSpec record correctly names its incompatible
  `ProjectBeamDesignInputV1` shape instead.
- A focused test-name inventory used an unmatched zsh glob for an optional
  ETABS integration-test path.
- The first frozen changed-source static batch reported one dynamic-`setattr`
  Ruff finding, two format-only files, scanner-local mypy inference conflicts,
  and the existing missing `xlwings` stub at the optional Excel import.
- The first normal commit-hook attempt created no commit: the complete generated
  ledger exceeded the 500 KiB small-file limit, Black normalized one P5
  metadata assignment, and full-project mypy rejected the targeted
  environment's `xlwings` import ignore. The first repair static check then
  exposed an inferred module-versus-fallback-stub assignment type.
- The second commit-hook attempt created no commit because Black restored one
  metadata assignment that the manual Ruff formatting pass had changed back to
  Ruff's alternate valid layout. Every other hook passed.

### Root causes and resolutions

- A Codex app worktree may be detached by construction. Resolution: verify exact
  hosted commit/tree, all worktrees, candidate ordering, and source binding,
  then attach the new task branch at the same commit without reset, stash,
  clean, rebase, discard, or deletion.
- P6 froze its candidate documents before hosted merge facts existed, and the
  immutable candidate was correctly not amended after merge. Resolution: P7
  reconciles the reviewed P6 head `9647fedd`, PR #858 merge `6cb47221`, and
  exact candidate/merged tree `d2b3efa3` in its own candidate documents.
- Recursive `Path.rglob` plus repeated per-symbol regular-expression scans made
  caller discovery multiply work across the repository. Resolution: prune
  ignored directories with `os.walk`, parse Python once with AST, and scan other
  text once with indexed expressions. Ledger generation now completes in about
  2.5 seconds. ⚠️ TERMINAL ISSUE: initial caller scan exceeded 60 seconds ->
  interrupted it and replaced recursive repeated scanning with pruned,
  single-pass discovery.
- P1-P6 deliberately added public objects across the same three facades.
  Resolution: treat G0 counts as a baseline, group projections by exact owner,
  and record 620/620 reconciliation rather than interpreting 498 compatibility
  entries as engines.
- The detailing, serviceability, shear, and torsion root stubs retained older
  module paths in prose although their imports already delegated to the beam
  owners. Resolution: update the docstrings and fail closed when documented and
  imported owners disagree.
- Importing `structural_lib.<module>` can replace a root package attribute with
  the compatibility module object, and typing aliases do not have a unique
  resolvable owner through generic introspection. Resolution: classify module
  paths as formula-free namespace adapters and derive exact symbol owners from
  import statements; record warning category, message, replacement, and
  stacklevel from the ten warning stubs. The focused test now passes 18 tests.
- Held P5 metadata is deliberately specific to each incompatible legacy shape.
  Resolution: assert the shared status/removal boundary and accept either the
  snapshot-identity or ProjectBeamDesignInputV1 limitation language. The
  affected focused test passes.
- zsh rejects unmatched globs before `rg` can inspect the remaining paths.
  Resolution: enumerate the maintained ETABS test files with `rg --files` and
  pass the exact results. ⚠️ TERMINAL ISSUE: unmatched
  `Python/tests/integration/test_etabs_import*` glob -> used an `rg --files`
  inventory and exact paths.
- Dynamic assignment hid a constant compatibility attribute from Ruff/mypy;
  reused local names made mypy join AST and text-scan types; and optional
  `xlwings` intentionally has no importable stub on this Mac. Resolution: use
  typed direct compatibility assignments, distinct scanner-local names, an
  explicit optional-import ignore, and Ruff formatting. All 28 changed Python
  files pass Ruff/format and all 17 changed runtime/scanner sources pass mypy.
- The full record ledger repeated long signatures, paths, migration metadata,
  and test evidence across 1,408 owner/projection/module records, producing a
  2.9 MiB pretty-printed file. Resolution: retain the complete in-memory
  contract while checking in a lossless global value dictionary, recursively
  interned/front-coded string table, and indexed record rows. The generator and
  test suite expand it before comparison; the exact 620 projections and 1,501
  callers remain present while the deterministic file is 498,253 bytes. The
  optional Excel bridge now imports `xlwings` dynamically into an `Any`-typed
  binding so both installed and fallback environments type-check without an
  environment-dependent suppression. Black's hook edit was retained. The
  repaired 19-test compatibility selection, generator check, Ruff/format, and
  full 247-source mypy run pass.
- `etabs_import.py` is on the repository's Black hook surface; using Ruff to
  format it after the first hook correction caused a deterministic formatter
  oscillation even though Ruff lint stayed green. Resolution: retain Black's
  hook output, verify it with Black and Ruff lint only, and exclude it from any
  further Ruff formatting pass. The final hook retry is the acceptance
  evidence. ⚠️ TERMINAL ISSUE: alternating Black and Ruff format layouts kept
  rejecting the commit -> retained the configured Black output and used Ruff
  only as a linter.

### Validation through content freeze

- Exact source binding remains hosted `6cb47221` / tree `d2b3efa3`; the
  preserved INDIA-3 candidate `9c976b1f` and every unrelated clean, dirty,
  detached, behind, or diverged lane remain unchanged.
- The generated ledger reconciles 620/620 facade projections, records 222
  canonical owners, 45 root modules, 520 root-symbol projections, 87 `api_hub`
  exports, and zero blocked maintained callers or retirement candidates.
- The P5 snapshot remains
  `a82d927d347108f56aa3fcdd559c1aa45ba8d87673cb3feec61a03d5eadbf4f8`;
  the P6 maintained gravity vector remains hash `95487e89`, governing `HOLD`,
  with issue `BEAM_SUPPLIED_REINFORCEMENT_NOT_SUPPLIED`.
- The frozen focused selection passes 224 package/facade, P5, websocket, and
  representative P1-P6 tests. All 28 changed Python files pass Ruff/format and
  all 17 changed runtime/scanner sources pass mypy. Architecture checks 221
  files with zero violations, imports check 695 files with zero broken imports,
  and circular validation checks 202 files with no cycle. Classification and
  ledger reconcile 620/620, all 100 public functions pass schema/manifest
  validation, and OpenAPI/API-doc contracts remain green. The single
  pre-repair consolidated quick gate passed 10/10 with zero reused results. The
  repaired-candidate quick gate also passes 10/10 with zero reused results;
  normal hook retry and hosted-candidate evidence follow before integration.
  Broad suites remain reserved for M0. React/Office.js were not changed, so
  installed Windows Excel is `NOT_REQUIRED_UNCHANGED_SURFACE`.

## 2026-08-24 — Session: LIB-PRO-007-P6 cross-surface parity

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/lib-pro-007-p6-cross-surface-parity`, from exact merged P5
hosted-main commit `6d533b6f3754e4fe41522e042f17192d550a1d1b`, tree
`d3bbaeb239726733412af7072a651a718d893d18`.

**Git handoff receipt:**
`docs/verification/lib-pro-007-p6-cross-surface-parity-git-handoff-receipt.json`

**Focus:** Prove one canonical calculation identity, governing status, issues,
and source freshness through maintained Python, REST, React, and Excel product
surfaces. P7, broad cumulative M0 suites, live ETABS, EDB parsing, analysis
control, model modification/save/write-back, installed Excel rerun, INDIA-3
engineering, release, and professional approval remain excluded.

### Summary

- Preserved the original effective-depth basis through strict project-batch
  design instead of converting it to an explicit numeric depth before the
  canonical calculation.
- Proved both accepted P5 synthetic snapshot members carry the same normalized
  input hash, canonical result identity, governing status, and issues through
  Python, REST, and Routine Workbench V1.
- Factored the React request transport into a pure formula-free mapper and made
  retained batch results fail closed unless the canonical result envelope and
  evidence agree on contract, input, calculation, library, and status identity.
- Included complete imported source metadata in React member revisions. A
  snapshot-only source change now stales retained results and blocks export.
  Excel applies the equivalent block through its selected-table hash while the
  evidence-only snapshot column remains outside calculation mapping.
- Added a gravity-client contract check that preserves the maintained example's
  workflow-result hash, calculation-book binding, governing `HOLD`, and issues
  from Python through REST and React. Excel remains a canonical beam review
  surface; no second gravity calculator or transport-side formula was added.
- Kept the open Windows ETABS trial model untouched. The public P6 vector is the
  deterministic synthetic P5 export; optional real-model evidence remains a
  private, read-only exported-file supplement under the P5 acquisition matrix.

### Issues encountered

- The first P6 session start found an unmatched P5 usage checkpoint even though
  the P5 read-only session end had passed.
- The pre-repair parity reproducer found different Python and Excel normalized
  input/result identities for P5 member `101`.
- The first gravity REST parity test returned HTTP 422 while direct Python
  execution passed.
- A broad shell path probe used an unmatched `Excel*` zsh glob.
- The first React focused command could not find Vitest in this linked worktree.
- The first frozen React production build rejected an under-typed test fetch
  mock, and the first changed-file Ruff check required canonical import order.
- The first test-inclusive targeted mypy command selected existing test-module
  annotations outside P6's source-check contract.
- Two manual P5 usage phase-closeout attempts drifted while elapsed time
  advanced before the dynamic closeout succeeded.

### Root causes and resolutions

- P5 had passed its repository session closeout, but the separate shared usage
  ledger lacked an exact merge closeout. Resolution: bind the retained P5
  candidate `783cc15e`, PR #857, hosted merge `6d533b6f`, and exact merged tree,
  then record a dynamically measured phase total. P6 session begin passed.
- The project batch resolved a complete cover/stirrup/bar basis to `d=442 mm`
  and then called `design_beam_is456` as though that depth had been supplied
  explicitly. That selected the historical `d'=50 mm` default instead of the
  basis-derived `D-d=58 mm`; Excel preserved the basis. Resolution: pass the
  original `EffectiveDepthBasisV1` to the canonical service and use the same
  resolved compression depth in evidence. Both P5 members now have identical
  Python/Excel input and result identities, and REST delegates the same result.
- Serializing the internal gravity request model included computed
  `accepted_model_hash` and `load_model_hash` fields that the public request
  contract rejects. Resolution: send
  `get_gravity_workflow_example_document_v1()`, the maintained public REST
  example document. The affected parity test passes.
- zsh rejects an unmatched glob before the command can inspect paths.
  Resolution: rerun the read-only inventory with explicit maintained paths.
  ⚠️ TERMINAL ISSUE: unmatched `Excel*` glob -> used exact repository paths.
- Linked worktrees do not share `react_app/node_modules`. Resolution: install
  the exact lockfile with the maintained pinned Node launcher, then run focused
  tests through `./run.sh frontend test`; 25 React tests pass.
  ⚠️ TERMINAL ISSUE: Vitest missing in linked worktree -> initialized exact
  worktree-local dependencies with the supported launcher.
- Vitest inferred the zero-argument mock implementation rather than the fetch
  call signature used by the assertion; the Python import additions were not in
  Ruff order. Resolution: type the fetch mock as `(RequestInfo | URL,
  RequestInit?) -> Promise<Response>` and order the two service imports. The
  affected two React and 15 Excel tests pass, Ruff passes, and the production
  TypeScript/Vite build passes.
- The chosen mypy command included entire established test modules, exposing 11
  existing optional-typing findings rather than source defects. Resolution:
  run configured mypy on the changed calculation source, matching the normal
  source-hook boundary; `batch.py` passes. No unrelated test annotations were
  changed. ⚠️ TERMINAL ISSUE: test-inclusive mypy exceeded the maintained
  source boundary -> used the changed-source configured check.
- Manually copied elapsed totals were stale by command completion. Resolution:
  read the live checkpoint and close the predecessor with a command-derived
  current phase total; no verification or task claim was changed.

### Validation through content freeze

- Exact source binding is hosted `6d533b6f` / tree `d3bbaeb2`; preserved
  INDIA-3 candidate `9c976b1f` and every unrelated dirty, detached, behind, or
  diverged lane remain unchanged.
- The P5 snapshot remains
  `a82d927d347108f56aa3fcdd559c1aa45ba8d87673cb3feec61a03d5eadbf4f8`.
  Member `101` resolves input hash `b7f22f6e`, calculation identity
  `2c15be7a`, `PASS`, and no issues; member `102` resolves input hash
  `e7a4d93d`, calculation identity `0d9677e6`, `PASS`, and no issues.
- The maintained gravity example resolves workflow-result and calculation-book
  hash `95487e89`, governing `HOLD`, and sole issue
  `BEAM_SUPPLIED_REINFORCEMENT_NOT_SUPPLIED`.
- The frozen affected selection passes 147 Python/FastAPI/Excel tests and 35
  React tests. React lint and production build pass; changed-source Ruff/mypy
  pass. Architecture checks 222 files with zero violations, imports check 694
  files with zero broken imports, and circular-import validation checks 202
  files with no cycle. The one consolidated quick gate passes 10/10 with two
  unchanged reused checks. Normal staged hooks and hosted checks follow on the
  immutable candidate; broad cumulative suites remain reserved for M0.

## 2026-08-23 — Session: LIB-PRO-007-P5 ETABS exported snapshot

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/lib-pro-007-p5-etabs-snapshot`, from exact merged P4
hosted-main commit `426d401bb2afde417ff989bd7349c99b8f7cb438`, tree
`a5b0127295eff69d70572c63a488ca29e0fa5839`.

**Git handoff receipt:**
`docs/verification/lib-pro-007-p5-etabs-snapshot-git-handoff-receipt.json`

**Focus:** Converge existing ETABS exported-file paths into one deterministic,
hash-bound snapshot that emits existing canonical beam requests. Direct EDB
parsing, live ETABS automation, analysis control, model modification/save or
write-back, P6/P7, INDIA-3 engineering, release, and professional approval
remain excluded.

### Summary

- Added `build_etabs_canonical_snapshot_v1`, which delegates separate ETABS
  geometry and force CSVs to the maintained lossless import service and emits
  existing `ProjectBeamDesignInputV1` objects only after the complete snapshot
  is accepted.
- Bound project/export identity, Windows-recorded EDB name/hash, ETABS version,
  byte-verified E2K and selected table exports, exact units, local-axis mapping,
  one case/combination or source-envelope identity, normalization-ledger hash,
  stable ETABS `UniqueName` member IDs, and a versioned snapshot SHA-256.
- Added exhaustive P5 row dispositions. Every physical calculation-source row
  is `ACCEPTED`, `APPROVED_EXCLUSION`, or `BLOCKED`; exclusions require an exact
  row, reason, and approval reference. Any blocked row, unused approval, or
  ambiguity exposes no snapshot or canonical request.
- Added a synthetic trial-compatible E2K/CSV/XML fixture. Its seven source rows
  resolve to six accepted rows, one approved non-beam exclusion, zero blocked
  rows, two stable members, and two canonical beam requests.
- Added a trial-compatible acquisition matrix. Read-only API table export is
  preferred when available, while manual ETABS table export remains a fully
  valid fallback. EDB opening stays inside ETABS on Windows; the Mac consumes
  exported artifacts only.
- Kept `ETABSAdapter` as the canonical parser delegate. The older
  `normalize_etabs_forces`, `load_etabs_csv`, and `create_job_from_etabs`
  helpers remain held compatibility paths because they do not establish the
  P5 snapshot contract.

### Issues encountered

- The Codex worktree began clean but detached at the exact requested P4 merge.
- The first metadata-block path returned before accounting readable CSV rows.
- Initial targeted mypy found function-scope variable reuse widening an
  exclusion lookup and force-member mapping to incompatible optional types.
- One combined documentation patch did not match the current wrapped wording
  in the CSV specification.

### Root causes and resolutions

- Codex-created linked worktrees can begin detached even when bound to hosted
  `main`. Resolution: verify remote commit `426d401b`, tree `a5b01272`, clean
  status, all sibling lanes, and predecessor order first; then create the
  isolated `codex/lib-pro-007-p5-etabs-snapshot` branch. The held INDIA-3 lane
  and unrelated dirty detached lane remain untouched.
- Artifact and contract validation initially shared one early-return condition,
  so a unit mismatch produced zero row dispositions despite readable source
  CSVs. Resolution: return early only when E2K/geometry/force artifacts are
  unavailable; otherwise run the maintained lossless parser, preserve all row
  dispositions, and block globally. The unsupported-unit vector now reports
  all seven source rows without exposing requests.
- Reusing `approval`, `key`, and `canonical_member_id` names across branches
  caused mypy to retain narrower earlier types. Resolution: assign distinct
  approval-row, source-row, and force-mapping names. Targeted configured mypy
  passes the implementation and tests.
- The large patch used a line break that differed from the live specification.
  Resolution: inspect the exact lines and apply bounded document patches; no
  partial change was made by the failed patch.
  ⚠️ TERMINAL ISSUE: combined `apply_patch` context verification failed ->
  inspected the exact wrapped text and applied smaller bounded patches.

### Validation through content freeze

- Source binding is exact hosted `426d401b` / tree `a5b01272`; the retained
  INDIA-3 candidate `9c976b1f` and every unrelated branch/worktree are
  unchanged.
- The deterministic fixture snapshot is
  `a82d927d347108f56aa3fcdd559c1aa45ba8d87673cb3feec61a03d5eadbf4f8`;
  its normalization ledger is
  `a50c13df5d7f1efa5ab4ce2793ee5822727b59a3194e191ef65015f190c8412e`.
- The frozen focused snapshot/import/adapter/project-beam/packaging/capability
  batch collects 212 tests and passes 209, with three existing environment
  skips. It includes JSON round-trip/hash replay, exhaustive row conservation,
  exact exclusion approval, result-selection and unit failures, archive-order
  determinism, ambiguity blocking, and direct EDB rejection. Targeted Ruff and
  mypy pass.
- Architecture boundaries report 221 files and zero violations. The one
  consolidated quick gate passes 10/10 with two unchanged cached checks.
  Normal staged hooks and hosted checks follow on the immutable candidate;
  broad cumulative suites remain reserved for M0.

## 2026-08-23 — Session: LIB-PRO-007-P4 explicit practical actions

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/lib-pro-007-p4-practical-actions`, from exact merged P3
hosted-main commit `0ea3e2d43343d70f007b0771896b41566e3b5064`.

**Git handoff receipt:**
`docs/verification/lib-pro-007-p4-practical-actions-git-handoff-receipt.json`

**Focus:** Add only caller-assigned wall/beam line, beam point, and supported
slab-area gravity actions with stable identity and exact reconciliation. P5,
automatic load generation, lateral actions, live ETABS, write-back, release,
professional approval, and new INDIA-3 engineering remain excluded.

### Summary

- Added a frozen `GravityPracticalActionV1` input with unique action/source
  identity, source category and reference, DL/LL case, exact units, explicit
  destination, magnitude, point station where applicable, and caller assignment
  basis.
- Limited the contract to DL wall lines, full-span beam lines, positioned beam
  points, and area actions on the sole supported panel. Unsupported source
  categories, wrong units, missing/out-of-span stations, unknown destinations,
  and conflicting inclusion/exclusion evidence fail before calculation.
- Added source and destination ledger entries plus one exact balance for every
  practical action. The storey, beam, column, footing, and combination balances
  include these sources without silent loss or double counting.
- Reused the maintained simply supported load-analysis authority for combined
  UDL and point-load moment/shear. Point reactions use the exact supplied
  station and may be unequal; no stiffness or frame solver was added.
- Exposed practical-action reconciliation through the workflow result,
  calculation book, package-root types, existing REST route, and React review
  surface. The component-action count remains 22 and no new endpoint or second
  structural formula was added.

### Issues encountered

- The first context command guessed an unregistered `gravity` context area.
- The pre-repair reproducer confirmed `LoadModelV1` rejected every
  `practical_actions` field as extra input.
- The first focused batch had two contract-test failures after the additive
  field and exclusion rule changed.
- Initial changed-source mypy rejected a dynamically expanded practical
  metadata dictionary even though Pydantic runtime validation passed.
- A direct `npm test` in the fresh worktree could not find Vitest because that
  worktree had no local `node_modules` dependency runtime.
- The first independent evidence-replay command passed a prebuilt load model to
  a test helper that accepts practical actions instead.
- The first final mypy command ran from the repository root and resolved the
  package through both `Python.structural_lib` and `structural_lib` identities.

### Root causes and resolutions

- `gravity` is not a registered context-manifest area. Resolution: use the
  bounded plan plus targeted `rg` over the core ledger/workflow, REST, and React
  callers. ⚠️ TERMINAL ISSUE: `context show gravity` was rejected -> used exact
  symbol and caller discovery.
- The frozen B1 load model had no typed practical-action field, the ledger had
  no point stage, and all beam reactions assumed uniform 50/50 transfer.
  Resolution: add the bounded action contract, explicit point ledger stage,
  exact source/destination balances, and closed-form positioned reactions.
- The builder intentionally permits no hidden engineering defaults, so making
  `practical_actions` optional violated its established contract; the updated
  exclusion diagnostic also dropped a relied-on phrase. Resolution: require an
  explicit builder tuple and retain the prior diagnostic wording while adding
  the supplied-category rule. The affected 39 Python/FastAPI tests pass.
- The untyped metadata dictionary collapsed StrEnum and string values into an
  unusably broad constructor expansion for static checking. Resolution: factor
  one typed `_practical_ledger_entry` helper; configured mypy passes all six
  changed source modules.
- Linked worktrees do not automatically share the primary React dependency
  directory. Resolution: use the maintained pinned Node runtime to run
  `npm --prefix react_app ci`, then route the focused test through
  `./run.sh frontend test`; all three review-page tests pass.
  ⚠️ TERMINAL ISSUE: direct `npm test` could not find Vitest -> initialized the
  worktree-local pinned dependencies.
- The evidence helper constructs its own `LoadModelV1` from a practical-action
  tuple. Resolution: call the helper with the accepted action tuple and compare
  its independent workflow result with the machine-readable hand vector. The
  replay passes all exact counts, balances, footing actions, and B1 response.
  ⚠️ TERMINAL ISSUE: the first replay used an unsupported `loads` keyword ->
  used the helper's declared `practical_actions` contract.
- Configured mypy uses `Python/` as the explicit package base. Resolution: run
  the same six changed modules from that directory; mypy reports no issues.
  ⚠️ TERMINAL ISSUE: root-level mypy found two module identities -> ran the
  configured check from `Python/`.

### Validation through content freeze

- Exact source binding is `0ea3e2d4`; the preserved INDIA-3 candidate
  `9c976b1f` and every unrelated dirty, detached, behind, or diverged lane remain
  unchanged.
- The frozen focused building-model/ledger/workflow/builder/FastAPI selection
  passes 39 tests. The frozen focused React review-page selection passes 3
  tests; React lint and the production build pass.
- The four-action hand vector produces 13 source entries, 50 accepted ledger
  entries, 30 balances, four exact action balances, and zero maximum residual.
  Its service B1 action is `27.25 kN/m` plus `12 kN` at `2000 mm`, giving
  `134.91857798165137 kNm` and `89.75 kN`.
- Changed-source Ruff and configured mypy pass. Architecture boundaries report
  221 files and zero violations; import validation reports 691 files and zero
  broken imports; circular-import validation reports none across 201 files.
  API classification/manifest checks pass, and OpenAPI remains exactly 89
  operations and 444 schemas. The consolidated quick gate passes 10/10. Normal
  staged hooks pass, including mypy across 246 source files, 18 contract tests,
  API/docs/registry checks, and the routed quick validation.
- Broad Python/FastAPI/React suites and the full repository gate remain reserved
  for cumulative M0 under the frozen milestone cadence.

## 2026-08-23 — Session: LIB-PRO-007-P3 footing anchorage truth

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/lib-pro-007-p3-footing-anchorage`, from exact merged P2
hosted-main commit `e4d86d13e671516ca65d27028defb791e7d277c0`.

**Git handoff receipt:**
`docs/verification/lib-pro-007-p3-footing-anchorage-git-handoff-receipt.json`

**Focus:** Extend the bounded concentric isolated-footing detailing contract
with source-bound supported bend/U-hook anchorage and decisive physical-fit
evidence. P4, live ETABS, write-back, release, professional approval, and new
INDIA-3 engineering remain excluded.

### Summary

- Added an exact shared tension-bar anchorage primitive. Development-length
  compliance uses the unrounded Cl. 26.2.1 result; normalized bend anchorage is
  `4φ` per 45 degrees up to `16φ`, and a standard U-hook is `16φ`.
- Corrected the legacy shared 180-degree deformed-bar hook allowance from
  `8φ` to `16φ`; its compatibility wrapper now decides adequacy from exact
  values before rounding its display fields.
- Extended isolated-footing detailing with straight, 90-degree bend, and
  standard U-hook arrangements. Bent/hooked requests require an approved
  project geometry reference, internal radius, and extension.
- Added structured per-direction evidence for straight length to tangent,
  exact required/available length, bend/hook value, shortfall, radius, arc,
  extension, vertical envelope, U-hook return envelope, bounded member-envelope
  constructability, and total bar length.
- Preserved fail-closed status truth: an omitted arrangement needed to close
  anchorage or a missing/unsupported basis is `HOLD`; complete inadequate
  anchorage or physical fit is `FAIL`; only complete supported evidence can
  `PASS`.
- Projected the same calculation authority through the package root, isolated-
  footing service, Gravity V1 request adapter, typed REST request/response, API
  registries, OpenAPI baseline, product specification, and machine-readable P3
  evidence. No endpoint or second calculation path was added.

### Issues encountered

- The first footing search guessed a nonexistent
  `Python/structural_lib/codes/is456/foundation` path.
- An unquoted dotted clause number was rejected by the private SQLite FTS5
  query parser before source lookup.
- Source review confirmed that the shared 180-degree hook helper credited only
  `8φ` to deformed bars, changing anchorage outcomes from the bound IS 456
  source value.
- The first focused collection found invalid line-breaking around a union type
  annotation in two new request fields.
- Initial changed-source mypy found three Literal/optional narrowing errors,
  and Ruff found one import-order error in the re-export hub.
- Existing tests asserted the old `8φ` hook allowance and the B2 contract
  identity, so five vectors failed after the source-bound outcome changed.
- Essential diff review found that `constructability_is_adequate` overstated
  the bounded envelope proof and that a global failure flag could disagree with
  the exact failed diameter candidate retained in the response.
- Final checker routing found that three guessed script names for API and
  private-source verification did not exist in this worktree.
- The first staged-hook invocation used the obsolete `--commit-hook` spelling,
  which the current check runner rejected.
- The staged session-doc hook rejected the handoff receipt after the session
  log changed, adding stale authorization and retention holds.

### Root causes and resolutions

- The footing module is named `codes/is456/footing`, not `foundation`.
  Resolution: discover exact paths with `rg --files` before the bounded search.
  ⚠️ TERMINAL ISSUE: guessed footing directory did not exist -> used the
  discovered maintained path.
- FTS5 treats periods as query syntax unless the token is quoted. Resolution:
  rerun the private navigation search with `"26.2.2"`; the bound consolidated
  IS 456 source resolved to PDF page 44 without copying protected text into the
  repository. ⚠️ TERMINAL ISSUE: unquoted dotted FTS term failed -> quoted
  the exact clause token.
- Confirmed root cause: `calculate_standard_hook` varied its anchorage value by
  bar type and assigned only `8φ` to a deformed 180-degree hook. Resolution:
  factor exact unrounded development length and normalized Cl. 26.2.2.1
  anchorage into `evaluate_tension_bar_anchorage_v1`; the 16 mm reproducer now
  credits `256 mm`, not `128 mm`.
- Python does not permit the binary union operator to begin the following line
  outside a parenthesized annotation. Resolution: parenthesize both annotations;
  focused collection and the complete selected batch pass.
- The type checker could not narrow a broad Literal through set membership or
  carry optional narrowing across a separate condition. Resolution: branch on
  exact values and keep positive-geometry validation inside the narrowed block;
  configured mypy passes all six changed source modules. Ruff import ordering
  was corrected directly.
- The five failing assertions were source-truth regressions rather than new
  defects. Resolution: update only the outcome-changing vectors and add exact
  straight, bend, U-hook, geometry failure, unsupported hold, package, gravity,
  and REST evidence.
- The constructability field did not name its deliberate member-envelope limit,
  and failure flags were accumulated across all diameter pairs instead of
  travelling with each candidate. Resolution: rename the field to
  `bounded_constructability_is_adequate`, keep bar-to-bar collision modelling
  excluded, and store anchorage/geometry flags with each failed candidate. The
  retained evidence and governing reason now describe the same candidate; 53
  affected footing/package/REST tests, evidence replay, and the repaired quick
  gate pass.
- The maintained API checks are the generators' `--check` modes, while the
  private verifier is intentionally gitignored under the primary checkout.
  Resolution: route through `generate_api_manifest.py --check`,
  `generate_api_classification.py --check`, and the absolute private
  `library.py ... verify` command; all pass. ⚠️ TERMINAL ISSUE: guessed
  checker filenames were absent -> used the maintained registered commands.
- The current staged-hook selector is `./run.sh check --pre-commit`.
  Resolution: use that maintained selector once on the frozen staged paths.
  ⚠️ TERMINAL ISSUE: `--commit-hook` was rejected -> used
  `--pre-commit`.
- The receipt correctly binds mutable handoff evidence and must be regenerated
  after the final session-log edit. Resolution: freeze the log, recreate the
  receipt and handoff block, then rerun only `check-session-docs`; this removes
  the stale-evidence holds without repeating unrelated passed hooks.

### Validation through content freeze

- Exact source binding is `e4d86d13`; the preserved INDIA-3 candidate
  `9c976b1f` and every unrelated dirty, detached, behind, or diverged lane remain
  unchanged.
- The consolidated affected selection passes 158 Python/FastAPI tests covering
  shared detailing, isolated-footing calculation/publication, package-root
  entrypoints, gravity request/adapters, typed REST transport, and all P3
  `PASS`/`FAIL`/`HOLD` vectors.
- Changed-source Ruff and configured mypy pass. API documentation, manifest,
  classification, React/FastAPI contract, and the updated OpenAPI snapshot are
  current; the endpoint count remains 89 and schemas grow additively to 440.
- The private-source navigation result is recorded only as hash-bound source
  identity and page pointer. No protected source prose or page image is tracked.
- Broad Python/FastAPI/React suites and the full repository gate remain reserved
  for cumulative M0 under the frozen milestone cadence.

## 2026-08-23 — Session: LIB-PRO-007-P2 supplied beam reinforcement truth

**Agent:** Codex (`orchestrator`, sole writer; no subagents)

**Branch:** `codex/lib-pro-007-p2-supplied-beam-reinforcement`, from exact
merged P1 hosted-main commit `9119cadc1322a718a00dd4e00f5650a21f100af4`.

**Git handoff receipt:**
`docs/verification/lib-pro-007-p2-supplied-beam-reinforcement-git-handoff-receipt.json`

**Focus:** Separate calculated beam-steel demand, preliminary bar selection,
and source-referenced supplied reinforcement; make clear spacing, layer
geometry, effective depth, and support anchorage decisive in Building Gravity
V1. P3 work, live ETABS, write-back, release, professional approval, and new
INDIA-3 engineering remain excluded.

### Summary

- Added an immutable public supplied-reinforcement evaluator for the bounded
  rectangular, non-bundled, one-diameter-per-group case. It reports required
  `Ast`/`Asc`, a distinctly preliminary recommendation, exact supplied layers,
  area/spacing/depth/group-clearance/anchorage checks, provenance, clauses,
  limitations, and `PASS`/`FAIL`/`HOLD`.
- Added an additive versioned Gravity V1 reinforcement basis. Old requests
  still calculate beam demand but now remain `HOLD`; selection-only requests
  also return a recommendation; only complete source-referenced bars can reach
  bounded `PASS`.
- Resolved square-column widths at both accepted beam-end nodes for the
  conservative simple-support anchorage check. Ambiguous or non-square support
  orientation remains `HOLD`.
- Corrected the shared beam-spacing authority to derive clear distance from
  centre-to-centre spacing and removed decision-changing whole-millimetre
  rounding. All maintained optimizer/detailing callers now use that result.
- Updated the maintained open-hall example, Python/CLI/REST workflow evidence,
  public facades, API documentation, request schema, and packet evidence. Its
  exact `2129.575184323628 mm2` demand now returns a 7-20 mm preliminary
  recommendation and `HOLD`, not completed beam detailing.

### Issues encountered

- A first read-only search used an unmatched
  `Python/structural_lib/gravity*` glob, so zsh stopped before searching.
- A first inspection assumed serialized flexure key `ast_required`; the exact
  transport key is `Ast_required`, causing a read-only `KeyError`.
- A focused pytest command guessed
  `Python/tests/unit/test_rebar_optimizer.py`; the maintained test is under
  `Python/tests/integration/`, so pytest stopped before running the selection.
- Correcting centre versus clear spacing invalidated three optimizer vectors
  and one selection vector that had depended on the old false-feasible rule.
  Removing rounding then exposed a 36.75 mm centre / 24.75 mm clear vector that
  also had been promoted to 37/25 mm.
- The first gravity `PASS` fixture widened square supports to 1600 mm but kept
  the original 1800 mm2 column steel, so the independent column adapter rejected
  the unrealistic 0.07% steel ratio before the workflow completed.
- Initial targeted mypy found optional-spacing narrowing, one reused local
  variable name, and invariant `dict` typing on the support-section helper.
- Read-only inspection tried the nonexistent `session status` subcommand while
  locating the closeout interface.
- One combined task/plan documentation patch used stale exact prose and was
  rejected without writing.
- The first dependency install invoked ambient `npm` directly and selected
  Node 26 instead of the repository's pinned Node 24, producing an engine
  warning before the exact packages were installed.
- The strict documentation batch rejected the touched foundation plan's
  inherited `doc_type: plan`; the maintained checker accepts only its current
  typed metadata vocabulary.
- The subsequent API documentation check found that the new public function
  was described but its seven public input/result type names were not all bound
  with exact `api.*` symbols.
- The first exact evidence replay used a manually copied preliminary bar area
  with one incorrect final floating-point digit, so the strict identity
  assertion failed after all affected tests had passed.

### Root causes and resolutions

- zsh's default unmatched-glob behavior rejected the search before `rg` ran.
  Resolution: discover exact files with `rg --files` and search explicit paths.
  ⚠️ TERMINAL ISSUE: unmatched gravity glob stopped a read-only search -> used
  exact discovered paths.
- The design object exposes canonical `Ast_required`/`Asc_required` attributes,
  while deprecated lowercase compatibility properties and serialized naming
  made guessing unsafe. Resolution: inspect the exact object/schema and use the
  canonical attributes; focused workflow tests emit no deprecation warning.
  ⚠️ TERMINAL ISSUE: guessed flexure key raised `KeyError` -> re-read exact keys.
- The optimizer test's location was guessed instead of discovered. Resolution:
  locate it with `rg --files` and rerun the exact maintained file.
  ⚠️ TERMINAL ISSUE: guessed unit-test path did not exist -> used the integration
  test path.
- Confirmed root cause: `check_min_spacing` documented centre spacing but
  compared it directly with the Clause 26.3.2 clear-distance minimum, and
  `calculate_bar_spacing` rounded before that decision. Resolution: subtract
  bar diameter, retain exact spacing, return explicit centre/clear evidence,
  and rebind only mathematically valid benchmark vectors. The exact 40.6 mm
  centre / 24.6 mm clear case now fails against the 25 mm minimum.
- The widened-support fixture changed column gross area without preserving a
  valid column steel ratio. Resolution: derive the test column steel at 1% of
  its accepted square section while retaining the existing 1800 mm2 minimum;
  the column route then completes and the intended beam `PASS`/`FAIL` vectors
  are isolated.
- The type errors came from an unnecessary optional annotation, a function-
  scope name collision, and mutable-dictionary invariance. Resolution: narrow
  before assignment, use separate issue names, and accept a covariant
  `Mapping`; configured mypy passes all four changed source modules.
- `session` exposes `begin`, `handoff`, `usage`, and `end`, but no `status`.
  Resolution: use `usage --active` for timer state and the documented closeout
  commands. ⚠️ TERMINAL ISSUE: nonexistent session subcommand -> used supported
  session interfaces.
- `apply_patch` requires exact current context. Resolution: re-read the bounded
  task/plan blocks and apply two smaller patches; no partial write occurred.
- The ambient shell runtime is not the repository runtime selector. Resolution:
  rerun the lockfile-exact install through `scripts/node_runtime.py`; Node
  24.19.0/npm 11.17.0 then installed the same 395 packages and all React tests
  and the build passed. ⚠️ TERMINAL ISSUE: direct `npm ci` selected Node 26 ->
  reran through the maintained pinned-runtime wrapper.
- Confirmed root cause: the plan retained an older free-form documentation
  type after the front-matter checker moved to an enumerated schema. Resolution:
  classify the frozen product contract as `spec`; the failed-only strict docs
  batch passes without changing plan content.
- The API checker binds exports by exact facade symbol rather than inferred
  prose. Resolution: list all seven new public `api.*` types beside the
  evaluator contract; the failed-only API documentation check passes.
- The evidence value had been copied from a separately rounded display rather
  than the live Python `repr`. Resolution: bind the JSON to the exact live
  `2199.114857512855 mm2` value and repeat only the evidence replay.

### Validation through content freeze

- Source binding diagnosed the current linked worktree against exact base
  `9119cadc`; every dirty, detached, diverged, foreign, P1, and INDIA-3 lane was
  preserved without reset, stash, clean, deletion, or rewrite.
- Direct service truth table: missing supplied bars `HOLD` with recommendation;
  exact 4-16 plus 2-12 supplied bars `PASS`; insufficient area, clear spacing,
  or depth identity `FAIL`; missing support or required compression-depth basis
  `HOLD`.
- Gravity truth table: old request basis `HOLD`, selection-only request `HOLD`
  with recommendation, complete reviewed supply `PASS`, and inadequate supply
  `FAIL`; a canonical shallow-beam design failure remains `FAIL`.
- Changed source Ruff/Black and configured mypy pass. Generated public API
  manifest/classification are current; the new surface is preview on stable
  facades and compatibility-only on the legacy facade. OpenAPI retains 89
  operations and grows additively from 437 to 439 schemas.
- The frozen consolidated selection passes 95 Python/FastAPI tests, 3 React
  review-page tests, and the production React build. Architecture checks 221
  files with zero violations; 691-file import validation finds zero broken
  imports; 201-file circular analysis finds no cycle. Strict docs and all API
  documentation/React-contract checks pass.
- The first quick gate passed `10/10`. Publishing exact preliminary steel area
  and strengthening the direct-service input contract changed the frozen
  candidate, so only the affected 31 Python vectors and evidence replay were
  repeated, followed by one repaired-candidate quick gate; both pass (`10/10`).
  Normal staged hooks pass, including 246-file mypy, Ruff/Black, Bandit,
  generated registries, API/docs/session contracts, and the reused exact quick
  evidence. Immutable audit, hosted checks, and merge remain. Broad repository
  suites remain reserved for cumulative M0 by packet policy.

## 2026-08-23 — Session: LIB-PRO-007-P1 optimization truth

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/lib-pro-007-p1-optimization-truth`, from exact merged G0
hosted-main commit `a6d47a85b78e3dc8317f65bb33b2247b69aa9bf9`.

**Git handoff receipt:**
`docs/verification/lib-pro-007-p1-optimization-truth-git-handoff-receipt.json`

**Focus:** Make every accepted beam cost-optimization input decisive and every
published engineering field traceable to the canonical result.

No release, professional-use approval, P2 work, live ETABS, write-back, or new
INDIA-3 engineering claim is included.

### Summary

- Replaced the fixed internal search with an explicit transport-neutral section
  grid, material basis, utilization threshold, stirrup area, and alternative
  count while retaining legacy library-call defaults outside the held product
  request.
- Forwarded the stable facade's effective-depth deduction and every REST
  project input instead of dropping cover, grade, bounds, steps, and objective.
- Made maintained singly reinforced flexure, maximum shear, and required Vus at
  the returned practical stirrup spacing decisive candidate checks.
- Replaced zero Ast/Asc/steel quantity and assumed utilization with calculated
  values, real material/depth identity, exact total/per-metre costs, code
  edition, and flexure/shear clause references.
- Restricted the cost endpoint to the cost objective and added a stable
  infeasible-candidate error; no engineering result is returned for impossible
  shear or insufficient supplied Asv.
- Preserved the explicit cost boundary that longitudinal reinforcement is
  included while stirrup mass is excluded until its perimeter/anchorage
  geometry becomes an accepted input.

### Issues encountered

- P1 session start was initially blocked by an unmatched G0 usage-start event
  even though the G0 candidate had completed session validation and merged.
- Before repair, `vu_kn=0`, `80`, and `1000` returned the same core optimum;
  stable `cover_mm=25` and `50` returned the same effective depth; and REST
  material/grid/objective variants returned the same 230 x 450 mm section with
  zero steel fields and assumed utilization.
- The maintained shear function can return the 75 mm minimum practical spacing
  with `is_safe=true` when the supplied Asv at 75 mm is still slightly below
  the required Vus; maximum-shear stress alone was therefore insufficient as
  the optimizer's supplied-reinforcement acceptance invariant.
- A combined `apply_patch` delete/add operation for the same optimizer path was
  rejected before writing the replacement file.
- The first frozen React command found no worktree-local `node_modules`; because
  that compound shell had changed into `react_app`, the remaining root-relative
  checks in the same command were not executed.
- The first post-repair pytest selector used a guessed optimization test-name
  pattern and selected zero cases, so pytest exited 5 before the following
  React command could run.
- The first immutable-candidate commit was stopped by mypy because an internal
  failure formatter annotated its iterable errors as plain `object`, and by
  the API-documentation hook because the two new public optimizer types lacked
  explicit `api.*` reference entries.
- A read-only `rg` command embedded a Markdown backtick inside double-quoted
  zsh text, causing an unmatched-quote error before the search ran.
- PR #853's first hosted FastAPI job passed 478 cases but failed two smart-
  analysis cases: an infeasible optional cost search converted an already
  calculated canonical beam `FAIL` result into HTTP 422.
- The installed GitHub CLI accepted PR creation but does not support the newer
  `--json` flag on `pr create` or `--head` on `pr view`; both inspection attempts
  exited before their requested query step.

### Root causes and resolutions

- Confirmed root cause: session validation and usage accounting are separate;
  the unmatched G0 usage event required its explicit seven-phase closeout
  checkpoint. Resolution: record the exact G0 candidate, PR #852, merge, tree,
  phase timing, retry, and hosted counters; P1 session begin then passed.
- Confirmed root cause: the optimizer owned fixed widths/grades, did not call
  shear design, the insights adapter dropped cover, and the REST mapper ignored
  request fields while fabricating response values. Resolution: define one
  explicit candidate contract, forward it through the stable facade, and map
  only calculated result fields. Direct sensitivity/rejection vectors now prove
  each outcome-changing family.
- Confirmed root cause: `design_shear` enforces the practical spacing list after
  its section-level `tau_v <= tau_c,max` decision, so the lower 75 mm clamp can
  exceed the calculated required spacing for the supplied Asv. Resolution:
  retain the maintained shear result and add the optimizer's required-to-
  provided stirrup-capacity invariant at the reported spacing. The 300 x 500
  mm, 350 kN vector rejects 100.53 mm2 Asv and accepts 157 mm2 at 100 mm.
- The patch utility does not accept delete and add operations targeting the same
  path in one patch. Resolution: perform the two file operations separately and
  immediately validate the imported optimizer. ⚠️ TERMINAL ISSUE: combined
  delete/add patch was rejected -> separate patch operations completed the
  intended replacement without touching another path.
- Confirmed root cause: linked worktrees intentionally require their own
  lockfile-pinned Node dependencies, and shell `cd` persists within one compound
  command. Resolution: install the exact lockfile with the maintained Node 24
  launcher, rerun only the unexecuted React/root checks from the workspace root,
  and retain the existing one-high npm advisory as the already governed baseline
  rather than mutating dependencies. The targeted React file then passed 51/51.
  ⚠️ TERMINAL ISSUE: missing linked-worktree `node_modules` plus persistent
  compound-shell cwd -> canonical `npm --prefix react_app ci` and root-bound
  `./run.sh frontend test ...` completed the unexecuted checks.
- Confirmed root cause: the optimization endpoint cases are grouped under the
  exact `TestOptimizationEndpoints` class and do not share the guessed function
  substring. Resolution: invoke that exact class, then run the React command
  separately. Six endpoint cases and 51 React files/278 tests pass.
  ⚠️ TERMINAL ISSUE: guessed pytest `-k` selected no tests -> exact class
  selection completed the intended affected repair pass.
- Confirmed root cause: the formatter accepts the maintained result error list,
  but its annotation did not express iteration; the reference described the
  optimizer signature without naming both public types as `api.*` symbols.
  Resolution: type the formatter input as `Iterable[object]` and add exact
  constraint/error reference entries while correcting the obsolete fixed-grade
  optimizer description. The failed-only mypy and API-doc hooks are the repair
  evidence before the normal commit path is retried.
- Confirmed root cause: shell double quotes allowed the Markdown backtick to
  begin command substitution. Resolution: rerun the exact search with a
  single-quoted expression; it completed without mutation.
  ⚠️ TERMINAL ISSUE: unmatched shell quote blocked one read-only search ->
  single-quoted `rg` expression completed it.
- Confirmed root cause: `SmartDesigner.analyze` invoked cost optimization as if
  it were mandatory and allowed the new exact `OptimizationInfeasibleError` to
  escape, even though cost advice is optional and the canonical beam result is
  the disposition authority. Resolution: catch only that exact optimizer
  outcome, retain the canonical `FAIL`, return no cost analysis, and publish an
  explicit warning through the REST response. Four focused core/REST pass and
  fail vectors are the local repair evidence; unrelated input/type exceptions
  remain unsuppressed.
- Confirmed root cause: this host has an older `gh` flag surface. Resolution:
  create PR #853 without `--json`, then query it by number with the supported
  `pr view 853 --json ...` form. No duplicate PR or Git mutation resulted.
  ⚠️ TERMINAL ISSUE: unsupported GitHub CLI query flags -> supported
  create-then-query sequence confirmed PR #853 at exact head `1e2f4eb5`.

### Validation through content freeze

- Source binding began clean at exact hosted `main` `a6d47a85`, with
  `source_bound=true`, no Git operation/conflict, and all unrelated and INDIA-3
  lanes preserved.
- Machine-readable P1 evidence binds all pre-repair reproducers, the exact
  Python/REST accepted vector, infeasible shear, objective rejection, supplied-
  Asv sensitivity, clause provenance, and held cost boundary.
- The frozen focused batch passes 42 Python/FastAPI optimizer tests and 51 React
  API-contract tests. Evidence assertions, API manifest/classification,
  89-endpoint/437-schema OpenAPI, 220-file architecture, 200-file circular-
  import, 689-file/4,858-import resolution, and `git diff --check` all pass.
- After the request cost contract was tightened, the bounded repair pass passes
  the exact six-case FastAPI optimization class and 51 React files/278 tests;
  regenerated API manifest/classification and OpenAPI evidence remain current
  at 89 endpoints/437 schemas.
- The required post-repair consolidated quick gate passes 10/10 (eight safe
  cached results plus fresh Git-state and unfinished-operation checks). Normal
  staged hooks and read-only session closeout remain before immutable commit.
- The first immutable candidate `1e2f4eb5` passed local hooks and clean session
  closeout. On PR #853, Python, React, and documentation passed; FastAPI exposed
  the optional-cost integration defect above (2 failed, 478 passed), so merge
  remained blocked and the candidate was not rewritten.
- The explicit hosted repair passes four focused cases: normal smart cost
  analysis remains available, infeasible core cost advice preserves a canonical
  `FAIL`, and both REST visibility variants return HTTP 200 with no cost result
  plus the exact warning. Repair quick gate, hooks, closeout, push, and hosted
  rerun remain before merge.

## 2026-08-23 — Session: LIB-PRO-007-G0 product contract freeze

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/lib-pro-007-g0-contract-freeze`, from fetched hosted `main`
commit `2d6df18efa9228afbf593f36fa95d2ce574977ac`.

**Git handoff receipt:**
`docs/verification/lib-pro-007-g0-product-contract-git-handoff-receipt.json`

**Focus:** Freeze the bounded product-contract and implementation sequence
before optimization repair and INDIA-3-G0.

No formula, runtime result, supported engineering case, live ETABS operation,
release, or professional-approval claim is included.

### Summary

- Verified a clean, source-bound linked worktree at exact fetched hosted
  `main`; no open task-owned PR exists, and the preserved INDIA-3 plus dirty or
  uncertain sibling lanes remain untouched.
- Froze live capability, router, endpoint-test, React-hook, workflow-catalogue,
  and API-classification counts with their claim boundaries.
- Assigned nine product contracts one canonical calculation authority,
  transport set, current disposition, blocking gap, and owning successor
  packet.
- Marked beam cost optimization `HOLD_OUTCOME_CHANGING` because the current
  service ignores shear and fixed candidate dimensions/materials while its REST
  mapper publishes assumed or zero engineering fields.
- Sequenced P1 optimization truth, P2 supplied beam reinforcement, P3 footing
  hooks/bends, P4 explicit actions, P5 exported ETABS snapshot, P6 cross-surface
  parity, P7 compatibility convergence, and one cumulative acceptance gate.
- Corrected the stale active-task and handoff orientation after merged
  LIB-PRO-006/PR #851 without rewriting its immutable candidate evidence.

### Issues encountered

- The task board and next-session brief still described LIB-PRO-006 as a local
  candidate awaiting integration even though fetched hosted `main` contains its
  PR #851 merge at `2d6df18e`.
- Two bounded introspection commands initially assumed every route had HTTP
  `methods` and that catalogue/capability document helpers returned Pydantic
  models.
- The first staged-hook run rejected the handoff because its prose named the
  receipt path but did not contain the generated receipt identity/hash block.
  An initial attempt to repair it with `session sync --fix` instead performed
  the command's maintained metric synchronization and exposed one stale public
  API count in the bootstrap guide.

### Root causes and resolutions

- Confirmed root cause: the immutable LIB-PRO-006 candidate correctly froze
  before hosted integration, but its later merge fact was not written back into
  that candidate. Resolution: verify hosted `main` by fetch, archive the
  completed row, activate LIB-PRO-007-G0, and retain hosted facts in the new
  task-owned documents.
- Confirmed root cause: FastAPI includes an `APIWebSocketRoute` without an HTTP
  `methods` attribute, while both document helpers intentionally return plain
  dictionaries. Resolution: use `getattr(route, "methods", ())` and
  `json.dumps(...)`; the exact route and catalogue inventories then render.
  ⚠️ TERMINAL ISSUE: bounded introspection used incompatible object assumptions
  -> object-safe access and dictionary serialization produced the required
  live evidence.
- Confirmed root cause: the handoff block is generated from the selected Git
  receipt by preparation-mode `session end --fix`; `session sync --fix` owns
  repository metric synchronization instead. Resolution: retain its truthful
  91-to-97 public-API count repair in the bootstrap guide, then run
  preparation-mode session end with the exact receipt. The generated handoff
  identity passes the session checks. ⚠️ TERMINAL ISSUE: `session sync --fix`
  was the wrong receipt-projection command -> `session end --fix
  --git-receipt ...` produced the maintained handoff block.

### Validation through content freeze

- Git/source binding: linked lane from exact fetched hosted `main` `2d6df18e`,
  `READY_LOCAL`, `source_bound=true`, no operation/conflict, and no open
  task-owned PR before edits.
- Evidence JSON parses and its focused contract asserts nine product rows,
  optimization `HOLD_OUTCOME_CHANGING`, and P1 as the next packet.
- Maintained links report zero broken links; metadata, task WIP/format, context,
  and `git diff --check` pass.
- The generated API classification is current; API documentation, stability,
  signatures, and the 31 React/FastAPI call sites pass against 88 OpenAPI paths.
- The consolidated quick gate passes 10/10 with zero reused results before the
  staged-hook run.
- The first staged-hook run passed every applicable check except the exact
  session-handoff projection. Preparation-mode session end repaired that one
  root cause; the failed session-doc check and final staged candidate remain
  the bounded rerun before immutable commit.

## 2026-08-23 — Session: LIB-PRO-006 gravity usability foundation

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/lib-pro-006-gravity-foundation`, from exact `main` commit
`69c09cc741e11ba50521cb2cadaf2ba560ba4c51`.

**Git handoff receipt:**
`docs/verification/lib-pro-006-gravity-usability-foundation-git-handoff-receipt.json`

**Focus:** Close gravity usability foundation gaps before INDIA-3-G0.

No new structural formula, supported engineering case, release, or
professional-approval claim is included.

### Summary

- Confirmed that the audited gravity product paths were unchanged between exact
  audited commit `3f61bd93` and the task base, then reproduced the practical
  10 m x 4 m open-hall values, 26 balanced boundaries, and correct overall
  footing-detailing `HOLD` to displayed precision.
- Added an installed-package runnable example and an explicit rectangular
  builder whose engineering values, support idealizations, load inclusion
  rules, combinations, source identities, exclusions, and component bases are
  all caller supplied.
- Added package-root, CLI, REST-definition, and review-UI onboarding; promoted
  the deterministic governing component reason into every non-pass aggregate;
  and exposed the same reason in the calculation book and UI.
- Projected all 10 canonical component capability families plus the composed
  gravity workflow into the application catalogue. The separately approved
  beam automation capability remains the only tool-eligible surface; the
  gravity workflow explicitly remains ineligible without separate approval.
- Updated generated API, OpenAPI, and beam-tool manifests plus focused Python,
  FastAPI, React, documentation, and contract evidence. Provided beam-bar
  checking, footing hooks/bends, new action families, analysis adapters,
  INDIA-3 engineering, release, and qualified approval remain held.

### Issues encountered

- The first session start was blocked by an unmatched MAINT-0134 checkpoint
  even though its exact candidate had already merged through PR #850.
- The audit's approximate schema-size and "catalogue is beam-only" statements
  needed current-snapshot qualification before they could become foundation
  requirements.
- The first maintained-example serializer included nested Pydantic computed
  hash fields, so its own strict request model rejected the emitted JSON.
- Independent review found that the first builder revision hard-coded load
  combinations and support idealizations while documentation claimed it had no
  hidden engineering defaults.
- The first focused catalogue test still instantiated the expanded dataclass
  without the two additive catalogue fields.
- The isolated worktree had no local React dependencies. Direct Vitest fallback
  attempts first could not resolve Vite and then created a small ignored cache
  before failing package resolution.
- One new governing-reason assertion expected a synthesized beam issue code,
  while the canonical beam result already supplied a more specific issue.
- The final task-format check counted the completed MAINT-0134 row left in the
  Active table and rejected three rows against the WIP=2 contract.
- The pre-publication worktree comparison found the preserved INDIA-3 source-
  library candidate `9c976b1f` on older base `f24c3904`, with overlap in three
  shared session/task handoff documents.
- The first normal staged-hook pass found two builder typing errors, missing
  `api.`-qualified documentation for the new exports, and a stale generated API
  classification registry.

### Root causes and resolutions

- Confirmed root cause: the prior immutable candidate could not record its
  later hosted merge in the same commit and its usage closeout checkpoint was
  absent. Resolution: bind the old candidate, merged tree, PR #850, and current
  base before recording the missing closeout; the new exact session then began
  normally. The task board now records MAINT-0134 as integrated.
- Confirmed snapshot facts: the current compact schema is 23,738 characters
  with 28 definitions, while the pretty form is 39,195 characters. The
  automation adapter catalogue was beam-only, but the separate canonical
  registry already had 10 component families. Resolution: preserve beam tool
  eligibility and add component/composed-workflow discoverability as separate
  catalogue claims.
- Confirmed root cause: `model_dump()` included nested computed fields that are
  output-only under the strict models. Resolution: the JSON-document helper
  explicitly excludes those two computed hashes; CLI output round-trips through
  `GravityWorkflowRequestV1` and runs without repository fixtures.
- Confirmed root cause: combination factors and member support assumptions are
  engineering inputs even when fixed by the bounded V1 contract. Resolution:
  make support idealizations, inclusion rules, and complete combinations
  required builder inputs; validate supported V1 idealizations and keep only
  topology IDs, source accounting, and hashes generated.
- Confirmed root cause: the legacy duplicate-ID test used the old positional
  contract. Resolution: preserve both canonical additive catalogue projections
  in that deliberately invalid fixture; the failed-only test passes.
- Confirmed root cause: linked worktrees intentionally do not inherit
  `react_app/node_modules`. Resolution: use the repository's pinned Node runtime
  with an ignored temporary symlink to the primary checkout's existing
  dependencies; targeted Vitest, ESLint, and production build pass. Remove the
  exact temporary link before candidate freeze. ⚠️ TERMINAL ISSUE: direct
  Vitest could not resolve worktree dependencies → pinned shared dependencies
  plus the canonical frontend commands proved the worktree source.
- Confirmed root cause: beam design already emits
  `BEAM_DESIGN_CHECK_FAILED`, so the fallback correctly preserves that more
  specific reason. Resolution: assert the canonical code and rerun only the
  failed test; component and aggregate reasons remain non-empty.
- Confirmed root cause: task-table WIP counts rows, not status labels.
  Resolution: move the already merged MAINT-0134 row to task history and retain
  only LIB-PRO-006 plus paused INDIA-3-G0 in Active; rerun only task formatting.
- Confirmed ordering fact: the source-library packet predates MAINT-0134 and
  this gravity foundation; its unique paths are `.gitignore`, the private-source
  boundary test, and its evidence, while `SESSION_LOG`, `TASKS`, and the next
  brief overlap. Resolution: retain the worktree/branch unchanged, integrate
  LIB-PRO-006 first as the owner-requested prerequisite, then rebind the source-
  library packet onto exact new `main` and reconcile only the shared documents
  before INDIA-3 engineering resumes.
- Confirmed root causes: the heterogeneous generated entity tuple needed an
  explicit union annotation; `LoadModelV1` requires exactly two combinations,
  while the builder field used a variadic tuple; the API documentation checker
  recognizes `api.<symbol>` references; and new root exports require a generated
  classification refresh. Resolution: bind both tuple types exactly, qualify
  every new API symbol in the reference, regenerate the canonical registry, and
  rerun only the failed mypy/API-documentation/classification hooks. All three
  failed checks now pass.

### Validation through content freeze

- Git/source binding: source-bound linked lane from exact base `69c09cc7`, no
  operation/conflict, with `source_bound=true` before edits.
- Audit reproduction: every displayed slab, beam, column, and footing value
  matches; example result is `HOLD`, top issue is
  `FOOTING_GOVERNING_HOLD`, and all 26 boundaries reconcile at `0.0 kN`.
- Focused Python/FastAPI evidence covers 37 unique gravity/catalogue/REST tests;
  the explicit-assumption repair subset passes 8/8 and the focused governing
  reason suite passes 12/12 through failed-only repair.
- React evidence: Building Gravity review page 3/3, ESLint, TypeScript, and
  Vite production build pass on pinned Node 24.
- Generated API manifest, OpenAPI baseline, and beam-tool manifest were
  regenerated from the reviewed contracts; `git diff --check` passes.
- API compatibility and OpenAPI checks pass at 89 endpoints/437 schemas;
  architecture has zero violations and all 2,253 internal imports resolve.
- The consolidated quick gate passes 10/10 with zero reused results. Normal
  staged-hook failed checks pass after their exact repairs, and the consolidated
  normal staged-hook rerun is green. Immutable commit, final session closeout,
  and hosted checks remain the candidate integration sequence.

## 2026-08-23 — Session: MAINT-0134 agent instruction consolidation

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-0134-agent-instructions`.

**Focus:** Consolidate the inherited Claude, Copilot, VS Code, and Codex
instruction surfaces into one owned, executable contract before INDIA-3-G0
continues. No INDIA-3 source interpretation, formula, support, release, or
professional-approval work is included.

### Summary

- Consolidated root, Claude, Copilot, VS Code agent, prompt, skill, and generated
  agent-context guidance under one explicit ownership model.
- Added exact scoped-rule projection and semantic contract enforcement plus the
  multiline closed-task regression.
- Froze the plan, task boundary, handoff, authorization receipt, and evidence;
  the focused, quick, cumulative, formatting, and normal-hook gates pass.

### Issues encountered

- The canonical `session begin` brief emitted two macOS `awk: newline in
  string` errors and falsely reported no active task.
- The first generated Claude projection of the Python scoped rule omitted one
  meaningful blank line, so the new exact-body validator rejected the pair
  despite 99% textual similarity.
- The first guessed control-plane projection command used
  `python_runtime.sh -m control_plane.cli`; the launcher intentionally binds
  repository and package roots but not `scripts/` as an importable module root,
  so that invocation could not resolve `control_plane`.
- The first session-log insertion used a repeated historical receipt line as
  its patch anchor and placed the new entry inside the older E1 entry instead
  of at the top of the newest-first log.
- The first cumulative gate rejected the two new maintained documents because
  their frontmatter used the human-facing values `candidate` and `architecture`
  instead of the repository schema enums.
- The targeted Black check found noncanonical wrapping in the two changed
  validators and their governance regression file before the commit hook.
- The first final read-only `session end` rejected the clean candidate because
  the newest log recorded outcomes only under `Validation through content
  freeze`, not under a parser-recognized completion section.

### Root causes and resolutions

- Confirmed root cause: `agent_brief.sh` passed newline-separated closed task
  IDs through `awk -v`, embedding those newlines in the macOS awk source
  string. Resolution: normalize the IDs to a comma-delimited value before the
  awk boundary and add injected-path/closed-ID regression coverage. A
  two-line closed-ID input now excludes the closed row, includes the live row,
  and emits no awk error.
- Confirmed root cause: approximate similarity had previously treated
  near-matching scoped rules as sufficient and provided no exact projection
  contract. Resolution: retain frontmatter differences but require identical
  normalized bodies; restore the missing blank line. All four pairs now report
  exact matches.
- Confirmed root cause: the control-plane CLI package lives below `scripts/`,
  while the worktree-bound launcher exposes the repository and `Python/` roots.
  Resolution: use the maintained `./run.sh control export-legacy --write`
  operation. The export completed and `./run.sh control validate` reports the
  projection current. ⚠️ TERMINAL ISSUE: guessed module invocation could not
  resolve `control_plane` → used the canonical `run.sh control` operation.
- Confirmed root cause: the historical E1 receipt label was not a unique patch
  anchor. Resolution: remove only the new MAINT-0134 block, reinsert it after
  the unique session-log header, and regenerate the handoff view. MAINT-0134 is
  now the newest complete entry and the E1 history is unchanged.
- Confirmed root cause: task state and document topic were copied into strict
  frontmatter fields whose accepted values are narrower. Resolution: retain
  candidate state in the document body/task board and use schema-valid
  `status: active` plus `doc_type: reference`. The failed-only documentation
  check is the repair evidence; no instruction behavior changed.
- Confirmed root cause: the new Python patches were composed manually and had
  not yet passed the repository formatter. Resolution: run Black only on the
  three reported files, then repeat their formatting check and affected
  instruction tests/validators. No behavior or scope changed.
- Confirmed root cause: the session parser recognizes completed bullets only
  below `### Summary` or `**Completed:**`; the validation heading is not an
  outcome section. Resolution: add one concise summary of the already-proven
  work and keep the detailed evidence below. The failed final closeout is the
  exact repair reproducer.

### Validation through content freeze

- Source-bound isolated lane: base
  `40aa5864194a7296caea13def1ccf82f44aca917`,
  `codex/maint-0134-agent-instructions`, `source_bound=true`.
- Entry sizes: `AGENTS.md` 22,705 bytes; `CLAUDE.md` 38 lines/1,449
  bytes; Copilot global 3,583 bytes; Copilot orchestrator 17,943 bytes.
- Maintained instruction and generated-agent context surfaces contain zero
  direct checkout-specific Python/pytest commands.
- Four of four scoped-rule projections are exact; semantic contract and
  composition audits report zero issues.
- Control validation passes with 115 active operations and 101/101 registered
  top-level scripts; its compatibility projection is exact.
- Five focused instruction-governance tests and the multiline task-brief
  regression pass. The final frozen focused batch, context/efficiency checks,
  quick gate, cumulative gate, normal hooks, and hosted checks remain the
  immutable-candidate closeout sequence.

**Git handoff receipt:** `docs/verification/maint-0134-agent-instruction-consolidation-git-handoff-receipt.json`

## 2026-08-23 — Session: INDIA-3-G0 private multi-code source library

**Agent:** Codex (`library-expert`, sole writer)

**Branch:** `codex/india-3-g0-source-library`, from exact remote `main`
commit `f24c3904b4af7d768f71342f11ac70f21e7b1dfa`.

**Git handoff receipt:**
`docs/verification/india-3-g0-private-source-library-git-handoff-receipt.json`

**Focus:** Inspect additional IS-code PDFs in Downloads, preserve useful code
sources in the existing Git-ignored private-source boundary, and create a
searchable, hash-bound database that avoids repeated discovery/screenshots
without reproducing protected source content in tracked or packaged outputs.

### Summary

- Created a private SQLite source library in the retained primary checkout,
  referenced the two existing IS 456 PDFs, and copied 23 distinct IS 875,
  IS 1893, IS 13920, and IS 2950 PDFs without moving or deleting Downloads.
- Bound 25 distinct PDF identities to 27 original aliases and 732 cached pages;
  exact duplicate downloads deduplicate by SHA-256.
- Added separate identity, edition/amendment, review, applicability, and
  distribution states; page FTS; visual/OCR-required flags; and normalized
  reference contracts with no protected-excerpt field.
- Added three `UNREVIEWED_IMPLEMENTATION_CLAIM` navigation records for the
  current IS 13920 beam, column, and strong-column/weak-beam symbols. No
  source-derived engineering value or accepted page pointer was recorded.
- Reconciled the merged MAINT-0133B predecessor and activated INDIA-3-G0 as an
  audit/decision packet only. No formula, support, release, or professional-use
  claim changed.

### Issues encountered

- `session brief` emitted a macOS `awk` newline error while formatting the
  multi-line closed-task ID list.
- A SQLite CLI `-readonly` query returned `unable to open database file` once
  immediately after parallel verification, although the database file and
  integrity state were present.
- The first page-cache classifier treated any non-empty extracted text as a
  successful page. The consolidated IS 13920 PDF has scanned pages whose only
  extractable content is a short watermark layer.
- The available PDF runtime has no OCR engine. Several scanned/low-text pages
  cannot truthfully become searchable source content in this packet.
- The first Git handoff-receipt invocation passed a Markdown file to the
  structured `--evidence` option, so receipt creation stopped without output.
- The first normal hook run rejected the Latest Handoff receipt hash even
  though the receipt itself validated.

### Root causes and resolutions

- Confirmed inherited root cause: `scripts/agent_brief.sh` passes multi-line
  closed task IDs through one `awk -v` value, which macOS awk rejects.
  Resolution: use `session start`'s independent Python task parser, which
  returned `READY_LOCAL`; retain the formatter repair for automation scope.
  ⚠️ TERMINAL ISSUE: the shell brief could not format closed tasks → the
  maintained Python session parser completed startup and task state was read
  directly from `docs/TASKS.md`.
- SQLite CLI root cause remains **unconfirmed**; file presence, permissions,
  page rows, and `PRAGMA integrity_check` were healthy immediately afterward.
  Resolution: reopen the same database normally with `PRAGMA query_only=ON`;
  the failed query and all later read-only SQL completed without recreation or
  data loss. ⚠️ TERMINAL ISSUE: one `sqlite3 -readonly` open failed → a normal
  connection with query-only enforcement worked and integrity stayed `ok`.
- Confirmed root cause: a watermark text layer made scanned pages non-empty but
  did not contain their engineering content. Resolution: classify empty pages
  as `NO_EXTRACTABLE_TEXT`, normalized text below 250 characters as
  `LOW_TEXT_VISUAL_OR_OCR_REQUIRED`, reclassify all 732 cached pages, and save
  no incomplete clause pointer as accepted normalization.
- Confirmed limitation: neither `tesseract` nor another OCR executable is
  provisioned. Resolution: preserve the exact PDF/page identities and mark 142
  pages for future visual/OCR review; do not infer missing content or block the
  590 genuinely searchable pages.
- Confirmed root cause: `git_handoff_receipt.py --evidence` parses a JSON
  mapping, while the reviewed evidence artifact was Markdown. Resolution: keep
  the Markdown as an owned path, add a minimal structured authorization and
  retention evidence record, and regenerate the receipt from that JSON.
  ⚠️ TERMINAL ISSUE: Markdown evidence failed JSON parsing → structured source
  evidence plus the owned Markdown path produced the fail-closed receipt.
- Confirmed root cause: the handoff contract requires the receipt's embedded
  `local_state_receipt_hash`, while the briefing contained the SHA-256 of the
  JSON file bytes. Resolution: replace that one field with the embedded
  `sha256:c81907...84484cf` identity and rerun only `check-session-docs`.

### Validation through content freeze

- Git/source binding: clean linked worktree from exact `origin/main` at
  `f24c3904`; `git_state.py` returned `READY_LOCAL` and runtime diagnosis
  returned `source_bound=true` before edits.
- Private verifier: `documents=25`, `aliases=27`, `pages=732`,
  `normalized_references=3`, `visual_review_pages=142`; SQLite integrity,
  every stored/reference PDF hash, page ownership, and Git-ignore guard pass.
- Private seed idempotence: a second 27-entry run created aliases only; document
  and page counts stayed unchanged.
- Focused repository boundary: `2 passed` in
  `Python/tests/test_private_source_boundary.py`; `git ls-files private_sources`
  is empty and representative database/PDF paths are ignored.
- Documentation: front matter reports zero invalid files; 478 maintained
  Markdown files, 992 local links, and six local images have zero broken links.
- Consolidated quick gate passed `10/10` with zero reused results. Every
  ordinary staged hook also passes after the one targeted session-document
  receipt-hash repair. The fail-closed Git handoff receipt validates as `HOLD`
  only for the expected dirty/remote/PR/review facts. Final read-only session
  closeout, commit, push, and hosted evidence remain.

## 2026-08-23 — Session: MAINT-0133B exact cleanup execution

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-0133b-packet-a`, from exact fetched `origin/main`
commit `417a16590892d176ea288bbda93ad4d48b4603c4`.

**Git handoff receipt:**
`docs/verification/maint-0133b-git-handoff-receipt.json`

**Focus:** Execute only the two owner-authorized planning moves frozen by
MAINT-0133, preserve every held candidate, and clear the maintenance boundary
before actual product work.

### Summary

- Reverified both frozen source blobs and absent destinations on current
  `origin/main`, then repeated each exact transactional preview.
- Executed 2/2 moves through `safe_file_move.py`: five maintained references
  were updated, 71 historical references were preserved, zero references were
  unresolved, and neither operation rolled back.
- Preserved the four unresolved candidates, all deletion cases, all branches,
  and all worktrees. No cleanup discovery or adjacent repair was added.

### Issues encountered

- `session brief` printed an awk newline error after the shared efficiency
  ledger began returning both `MAINT-0132` and `MAINT-0133` as closed IDs.
- Two initial context calls used unregistered area names (`planning` and
  `governance`) and stopped their chained read-only commands.
- The transactional reference updater rewrote the plan's historical source-path
  literals to the destinations, making the source/destination columns
  misleadingly identical.
- `session summary --write` refreshed the receipt-backed handoff but replaced
  this task's summary with eight unrelated repository commits.

### Root causes and resolutions

- Confirmed root cause: `scripts/agent_brief.sh` passes the multi-line
  `--closed-task-ids` output through a single `awk -v` assignment, which macOS
  awk rejects when the value contains newlines. Resolution in this bounded
  packet: rely on `session start`'s independent Python task parser, which
  completed and reported `READY_LOCAL`; preserve the shell formatter repair for
  separate automation maintenance rather than mixing it into file cleanup.
- Confirmed root cause: context areas are registry keys, not free-form folder or
  role names. Resolution: `./run.sh context list` exposed the valid keys and
  `context show docs` plus `context show automation` completed successfully.
  ⚠️ TERMINAL ISSUE: unregistered context names stopped chained reads → listing
  the registry first and using `docs`/`automation` worked.
- Confirmed root cause: the mover classifies maintained literal occurrences as
  updateable references without understanding historical table semantics.
  Resolution: retain the link rewrites, relabel the table as original source
  versus current destination, and restore the two original source literals;
  execution evidence independently binds old and new blob identities.
- Confirmed root cause: the summary writer selects the first prior-day session
  date, gathers every later commit, and overwrites the first current-day
  `### Summary`; it is not task-start-bound. Resolution: retain its correct
  receipt-backed handoff block, restore this task-owned summary, and do not run
  the mutating summary command again in this packet.

### Verification

- Both exact previews and live moves pass with zero unresolved references and
  zero broken links; destination Git blobs equal their original source blobs.
- Focused migration tests, maintained links, context, quick/full gates, normal
  hooks, clean session closeout, and hosted evidence remain pending until the
  candidate is frozen.

## 2026-08-23 — Session: MAINT-0133 cleanup inventory and authorization

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-0133-cleanup-inventory`, from exact fetched
`origin/main` commit `60e95bbe52575d3335e7195db944b2c82630ed2e`.

**Git handoff receipt:**
`docs/verification/maint-0133-git-handoff-receipt.json`

**Focus:** Freeze an exact read-only repository file-cleanup inventory and
future transactional batch without moving or deleting content.

### Summary

- Bound the discovery contract to tracked hygiene artifacts, exact Git blobs,
  explicit inactive metadata outside archive roots, active control coverage,
  and exact safe-file previews; age-only and unreferenced-name guesses are
  excluded.
- Classified six explicit inactive-location files: two are
  `MOVE_READY_NOT_AUTHORIZED`, four are `HOLD_UNRESOLVED`, and none has enough
  evidence for deletion.
- Froze exact source blobs, destinations, reference counts, retained surfaces,
  and the two-operation future `MAINT-0133B-PACKET-A` batch.
- Preserved 507 archived documents, 119 archived scripts, 1,760 vendor
  references, four distinct empty Python test-package markers, and all 48
  observed worktrees. No live move, delete, branch, or worktree action ran.

### Issues encountered

- The first worktree-creation call used the not-yet-created worktree as its
  process directory, so the process could not start.
- The exact-byte duplicate probe assumed `shasum` existed and repeated the
  command-not-found error for each tracked file.
- A zsh loop variable named `path` overwrote zsh's tied command-search path, so
  subsequent `sed` calls in that shell were not found.
- The deprecated agent-guide `README.md` preview matched 1,107 basename
  occurrences and blocked on 279 unresolved maintained references.
- Three other inactive documents remain blocked by two, two, and three
  unresolved references respectively.

### Root causes and resolutions

- Confirmed root cause: a command cannot start in a directory that will only be
  created by that same command. Resolution: create the worktree from the
  existing repository, then run `session begin` inside the new lane; exact Git
  state reports `READY_LOCAL` and the runtime reports `source_bound=true`.
- Confirmed root cause: `shasum` is unavailable in this environment.
  Resolution: use tracked Git blob identities, which directly prove exact byte
  equality without an external hash executable; the only duplicate group is
  four empty `__init__.py` package markers and is kept.
- Confirmed root cause: `path` is a special zsh array tied to `PATH`.
  Resolution: use task-specific variable names such as `candidate_file`; the
  corrected header/reference inspection completed without state changes.
- Confirmed root cause: the transactional scanner conservatively treats the
  generic `README.md` basename as ambiguous across maintained surfaces.
  Resolution: record the 279-reference hold and require a separately reviewed
  path-qualified mapping or scanner repair; no force or manual move was used.
- Confirmed root cause: active governance/planning content still owns the other
  unresolved names. Resolution: keep those four sources in place and reserve
  their exact repairs for separate packets. The two completed INDIA-2 plans
  independently pass single and complete-batch previews with zero unresolved
  references.

### Verification

- Repository hygiene, maintained links/images, the 115-operation/101-script
  control registry, JSON syntax, source-blob identity, and the complete
  two-operation batch dry run pass. The batch preview performs zero writes.
- Focused migration tests, context, quick/full gates, normal hooks, clean
  session closeout, and hosted evidence remain pending until candidate freeze.

## 2026-08-23 — Session: MAINT-0132 automatic efficiency observability

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-0132-efficiency-observability`, from exact fetched
`origin/main` commit `d4e5b122e903e3c0e1229d2255bcaf3e03ed9d94`.

**Git handoff receipt:**
`docs/verification/maint-0132-git-handoff-receipt.json`

**Focus:** Measure the whole task rather than a manually reconstructed subset,
and prevent already-integrated work from consuming the next session's intake.

### Summary

- Added one `session begin` entry point that starts task-bound timing before the
  compact brief and environment check; its composed compatibility helper stops
  after preflight instead of printing a second copy of session context.
- Moved new telemetry to the Git-common ignored ledger while retaining a
  read-only projection of older worktree-local entries.
- Made closeout derive elapsed time from its unmatched start and reject
  unallocated/over-counted phase totals, invented short candidate IDs, inferred
  model profiles, incomplete hosted integration, and unequal reviewed/merged
  trees.
- Added automatic quick/full/session-end step durations and an exact external
  closeout projection so a frozen pre-push task row does not remain active after
  proven integration.

### Issues encountered

- The MAINT-0131 app duration was 20m15s, while its manually entered phase sum
  was 18m31s; 1m44s (8.6%) was absent from the ledger.
- The compact start still reported merged MAINT-0130 and MAINT-0131 as active.
- The prior ledger was rooted under each worktree, defaulted omitted identity to
  `gpt-5.6-sol/high`, and accepted seven-character hexadecimal text as an exact
  candidate without resolving a Git object.
- The prior transcript contained 47 discovery markers before its first edit and
  another seven edits after implementation was described as complete.
- The first `session begin` composition still followed the compact brief with
  the legacy helper's duplicate task, handoff, guidance, and Docker context.
- Two diagnostic commands were started from the wrong directory: the first
  memory lookup ran from the repository, and the first historical PR lookup ran
  from the memory folder.
- The first control-projection attempt used nonexistent `control project`, then
  replacing the public start operation exposed `agent_start.sh` as unregistered.
- The first consolidated focused batch found one Black delta and two stale
  assertions: the old 114-operation count and one policy phrase spelling.
- The first immutable-candidate commit attempt was stopped because the final
  preflight-only assertion had not been included in the earlier Black target.

### Root causes and resolutions

- Confirmed root cause: closeout compared one manually supplied elapsed value
  only with the manually supplied phase sum. Resolution: bind closeout to the
  shared unmatched task-start timestamp and report the exact residual before
  refusing a mismatched write.
- Confirmed root cause: runtime telemetry used worktree-relative `logs/` paths.
  Resolution: write through `git rev-parse --git-common-dir` and project retained
  legacy worktree ledgers read-only for historical summaries.
- Confirmed root cause: the immutable candidate cannot contain its future PR and
  squash-merge identity, while the compact brief trusted only the frozen task
  row. Resolution: require exact external PR/merge/tree closeout evidence and
  use that successor observation only as a compact active-task overlay.
- Confirmed root cause: model defaults and syntax-only short SHA validation
  fabricated precision. Resolution: default model/reasoning to `unknown`,
  require exact 40-character lowercase commits, resolve their trees, and prove
  the final candidate tree equals the reachable merged tree.
- Confirmed root cause: session orientation and routine gates had no automatic
  step receipts. Resolution: make `session begin`, quick/full checks, and
  `session end` append task-bound durations without changing command outcomes.
- Confirmed root cause: `agent_start.sh --quick` combines environment preflight
  with its own full onboarding output. Resolution: add a composable
  `--preflight-only` mode and use it only after the canonical compact brief; the
  compatibility start path remains unchanged.
- Confirmed root cause: command working directories were not kept with their
  evidence source. Resolution: rerun memory reads from the memory root and Git/
  GitHub queries from the repository; neither failure changed repository state.
- Confirmed root cause: the control CLI exposes `export-legacy`, not `project`,
  and `session begin` composes rather than retires `agent_start.sh`. Resolution:
  use the documented exporter and register the helper as an internal maintained
  compatibility operation; control validation passes at 115 operations and
  101/101 scripts.
- Confirmed root cause: focused contracts still froze the pre-MAINT-0132 count
  and an imprecise phrase. Resolution: update only those assertions and format
  the affected test file; the failed/affected evidence then passes.
- Confirmed root cause: the last focused edit occurred after the earlier
  formatting check. Resolution: accept only Black's quote normalization, rerun
  that focused module and the consolidated quick gate once, then retry normal
  hooks without bypassing them.

### Verification

- Session automation, verification control, token efficiency, control plane,
  Git guidance, and governance automation focused modules pass. Shell syntax,
  Black, the live preflight-only path, instruction drift, task format, script
  references, token policy, context, next-brief length, and the
  115-operation/101-script registry pass.
- The quick gate, commit hooks, full gate, clean session verdict, and hosted
  evidence remain pending until immutable candidate freeze.

## 2026-08-23 — Session: MAINT-0131 measurable efficiency controls

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-0131-efficiency-controls`, from exact fetched
`origin/main` commit `58ecc149bd4525ae92c4affb369851919fe1c402`.

**Git handoff receipt:**
`docs/verification/maint-0131-git-handoff-receipt.json`

**Focus:** Turn the reproduced MAINT-0130 efficiency defects into narrow,
executable controls without changing product or safe-file behavior.

### Summary

- Made dirty content an expected preparation-only state for `session end --fix`
  while preserving fail-closed handling for unknown Git state, operations,
  missing receipts, and every other failed preparation check.
- Replaced the blanket `scripts/_lib/**` all-domain rule with explicit
  maintained-caller mappings for shared utilities, AST helpers, Indian-code
  manifests, and safe-file primitives; control-only agent helpers retain the
  generic control owner, and unknown impact still selects all domains.
- Added a direct executable-mode regression for the two public safe-file
  compatibility entrypoints.
- Made closeout timing evidence executable in the ignored local usage ledger:
  all seven non-overlapping phases, exact candidate heads, and rejection,
  repair, retry, full-gate, and hosted-run counters are required and validated.

### Instruction decision record

- Evidence session: Codex task `01a02ce0-3608-7a32-afae-e69019d14822`
  and its merged MAINT-0130 record below.
- Repeated behavior: broad domain scheduling, preparation exit contradiction,
  late repair candidates, and omitted closeout timing metrics.
- Confirmed root cause: deterministic source/contract mismatches, not a model
  preference or a correlation inferred from one score.
- Exact instructions changed: the mandatory efficiency summary, canonical
  efficiency policy, end-of-session workflow, Git workflow, and the
  agent-evolution deterministic-repair boundary.
- Expected measurable effect: safe-file helper changes select only maintained
  control/docs/repository owners; otherwise passing dirty preparation exits `2`;
  incomplete timing closeout fails before writing; candidate and hosted reruns
  are visible in one local report.
- Approval: the user explicitly authorized the bounded implementation with
  “okay do it” on 2026-08-23.
- Evolution/rollback identity: no automatic evolution proposal or ID was
  fabricated; this is normal regression-backed control work. Rollback remains
  the exact MAINT-0131 candidate commit through an ordinary reviewed revert.

### Issues encountered

- The protected primary `main` was clean but one commit behind merged
  `origin/main`; editing there would have omitted MAINT-0130.
- The verification manifest assigned every product domain to every helper in
  `scripts/_lib`, even though those helpers have different maintained callers.
- `session end --fix` reused the final clean-tree verdict for a phase that is
  required to run before the candidate is committed.
- The canonical policy required closeout timing/candidate/retry fields, but the
  usage command accepted and stored an incomplete closeout checkpoint.
- The prior safe-file rewrite lost two executable bits without an invariant
  that protected those public compatibility entrypoints.

### Root causes and resolutions

- Confirmed root cause: the primary checkout had not been fast-forwarded after
  PR #844. Resolution: create one clean source-bound worktree directly from
  exact `origin/main` and preserve every existing lane.
- Confirmed root cause: `classify_paths` unions every matching rule, so a later
  specific rule could not override the blanket `scripts/_lib/**` all-domain
  owner. Resolution: remove that blanket and explicitly map outcome-changing
  helper families while retaining generic control-plane coverage and unknown
  fail-closed behavior.
- Confirmed root cause: `cmd_end` marked dirty evidence failed before applying
  its preparation-only return contract. Resolution: allow only `DIRTY` in
  preparation mode; `UNKNOWN`, operation/conflict, receipt, and other failures
  remain status `1`, while plain final validation still requires `CLEAN`.
- Confirmed root cause: timing labels lived only in prose and the ledger schema
  had no completeness or sum checks. Resolution: validate canonical labels,
  non-negative finite minutes, exact total, candidate heads, and every required
  counter before appending a closeout checkpoint.
- Confirmed root cause: executable compatibility was accidental file metadata.
  Resolution: add one focused regression for the two public entrypoints rather
  than create a second executable registry.

### Verification

- The complete affected selection passes: 235 tests across session automation,
  verification routing/evidence, migration entrypoints, Git guidance,
  token-efficiency semantics, and control-plane contracts.
- Verification-manifest validation passes with seven domains, 28 rules, and
  unknown impact selecting all domains. Instruction drift, task format, active
  script references, token-efficiency controls, and canonical context pass.
- Live preparation on the 15-path dirty candidate validates the exact HOLD
  receipt and exits `2`; it updates only the maintained handoff block and never
  prints the final safe-closeout verdict.
- The immutable candidate still requires one quick gate, one cumulative full
  gate, ordinary commit hooks, and all applicable hosted checks.

## 2026-08-23 — Session: MAINT-0130 transactional safe-file foundation

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-0130-safe-file-foundation`, from exact fetched
`origin/main` commit `242ba386925d29766b1467810044e276ebbceb64`.

**Git handoff receipt:**
`docs/verification/maint-0130-git-handoff-receipt.json`

**Focus:** Replace split file-operation safety with one fail-closed transactional system.

### Summary

- Added a shared safe-file library for repository/path validation, maintained
  versus preserved reference classification, exact snapshots, structured link
  validation, hashes, and collision-safe delete backups.
- Made move, delete, Python/React migration, and batch execution transactional.
  Missing validators, unresolved maintained references, path hazards, bypass
  flags, preview/live disagreement, validation regressions, or corrupt rollback
  evidence now fail without reporting success.
- Expanded maintained Markdown/link/image coverage, made ambiguous repair
  require an explicit mapping, and preserved immutable historical references.
- Retired the live age-only archive command, changed evolution to report-only,
  refreshed the control projection, and updated the operator guidance. Bulk
  cleanup remains held until this foundation is merged and a separately
  classified plan is approved.

### Issues encountered

- The pasted audit described the pre-MAINT-012D surface while `origin/main` had
  already advanced through scanner/script consolidation.
- `./run.sh context show scripts` failed because `scripts` is not a maintained
  context-area name.
- The first archive-script dry run blocked two maintained references rather
  than moving with an incomplete update set.
- A control-projection refresh failed during the intentional interval where the
  old top-level archive script was no longer registered but had not yet moved.
- A batch using a caller-selected rollback directory failed because child
  safe-move discovery treated the batch's own manifest as maintained content
  and rewrote it during execution.
- The first affected-test run exposed five stale contract expectations after
  the intentional operation-count, permission, preview, and batch changes.
- Focused Ruff and Black checks initially found one unused test import and seven
  changed Python files requiring canonical formatting.
- Closeout preparation completed every preparation check but exited `1` instead
  of the documented preparation-only status `2` because the candidate was dirty.
- The first candidate commit summary showed that the two rewritten safe-file
  entrypoints had unintentionally lost their executable file modes.
- Hosted Repository Validation passed the migration but failed its generated
  rollback entrypoint because that script required a project `.venv` absent
  from the provisioned GitHub Actions Python environment.

### Root causes and resolutions

- Confirmed root cause: the audit snapshot predated the merged MAINT-012D
  control plane. Resolution: fetch and bind this work to exact current
  `origin/main`, then recheck every finding against live source before editing.
- Confirmed root cause: context routing is manifest-area based, not an arbitrary
  folder lookup. Resolution: use the registered automation/verification areas
  and targeted `rg`. ⚠️ TERMINAL ISSUE: unknown context area `scripts` -> used
  the maintained context manifest and targeted source inspection.
- Confirmed root cause: the existing guides/evolution caller still contained
  active references to the legacy archive command. Resolution: update those
  maintained callers first; the repeated safe-move preview then classified 36
  historical references as preserved and zero as unresolved.
- Confirmed root cause: top-level script coverage correctly rejects a half-
  completed registry/file transaction. Resolution: finish the safe move before
  regenerating the compatibility projection; control validation passes at 114
  active operations and 101/101 active scripts.
- Confirmed root cause: batch-owned rollback evidence was inside the repository
  scanner's normal maintained surface. Resolution: pass the exact batch run
  root to child operations as a scanner exclusion while independently hashing
  and verifying that evidence. The exact rollback/corruption regression and
  the complete affected suite pass.
- Confirmed root cause: tests encoded the superseded counts, default live
  permissions, incomplete preview path lists, and an old fixture literal.
  Resolution: update only the outcome contracts and add direct transactional
  regressions; exact failed-node reruns passed before the complete affected
  suite was run once.
- Confirmed root cause: new source had not yet received the repository formatter
  and one imported helper was unused. Resolution: remove the import, format the
  seven reported files, and rerun only Ruff and Black; both pass.
- Confirmed root cause: `session end --fix` marks any uncommitted candidate as a
  failed closeout before applying its documented preparation-mode exit rule,
  even though preparation is required before candidate freeze. Resolution: keep
  this as a recorded session-control follow-up and rely on the required clean,
  read-only post-commit `session end` verdict; do not expand MAINT-0130 into an
  adjacent session-lifecycle repair. ⚠️ TERMINAL ISSUE: preparation returned `1`
  after all generated handoff checks passed -> retained the reviewed writes and
  reserved final authority for the clean read-only closeout.
- Confirmed root cause: replacing the script contents through the patch workflow
  recreated `safe_file_move.py` and `safe_file_delete.py` as mode `100644` even
  though both tracked entrypoints were previously `100755`. Resolution: restore
  only those executable bits, directly invoke both entrypoints, rerun the
  affected transaction tests and consolidated gate, and create an explicit
  repair candidate before publication.
- Confirmed root cause: `rollback.sh` delegated to `python_runtime.sh`, which is
  intentionally worktree-bound and rejects environments without a discoverable
  project interpreter even when the batch is already running under a valid
  provisioned Python. Resolution: record the exact running `sys.executable` in
  the generated rollback command, keep the same manifest-verified restore
  primitive, and regression-test execution through that exact interpreter.

### Verification

- The complete affected migration/control/governance selection passes: 93
  tests across transactional success, rejection, rollback, corruption, link,
  registry, permission, and inactive-archive behavior.
- Ruff and Black pass for all 13 changed Python source/test files.
- Maintained-link validation passes for 478 Markdown files, 1,013 local links,
  six local images, and zero broken targets.
- Control validation passes with 114 active operations and 101/101 scripts;
  context validation passes with zero generated folder indexes.
- The immutable candidate additionally requires one fresh quick gate, one
  cumulative full gate, ordinary commit hooks, and all applicable hosted PR
  checks. Hosted and merge facts remain outside this candidate commit.

## 2026-08-23 — Session: MAINT-012D scanner and script consolidation

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-012d-scanner-consolidation`, from exact merged
`origin/main` commit `84f3cbe6ce576a6c3a22882ddec2e1c08415c4e0`.

**Git handoff receipt:**
`docs/verification/maint-012d-git-handoff-receipt.json`

**Focus:** Consolidate duplicate scanners and retire obsolete compatibility scripts.

### Summary

- Mapped active callers, runtime behavior, outcome ownership, aliases, and
  historical references before selecting KEEP, CONSOLIDATE, or RETIRE.
- Kept the distinct readiness, error, input, function-quality, public-route,
  and agent-evolution scanners. Consolidated duplicate OpenAPI, health, link,
  task/WIP, import-test, Git, and context surfaces under canonical owners.
- Archived sixteen obsolete files without redirect stubs and reduced the
  canonical surface from 130 operations (124 active) and 115 top-level scripts
  to 115 active operations and 102/102 active top-level scripts.
- Added evidence-preserving safe-move behavior so old logs, audits, research,
  receipts, and explicit retirement sentinels keep the path truth recorded at
  their original snapshot.

### Issues encountered

- Session intake and the task board still described MAINT-012C or MAINT-012B
  after both were merged, so startup guidance selected a completed packet.
- `./run.sh context show operations` failed because `operations` is not a
  context area; the maintained areas are exposed by `./run.sh context list`.
- A baseline probe invoked the shell script `check_wip_limits.sh` through the
  Python runtime and produced a `SyntaxError`; no file was changed.
- `governance_health_score.py --json` failed in the linked worktree because it
  invoked `.venv/bin/python` relative to the worktree. `repo_health_check.sh`
  failed because it assumed `.git/` was a directory rather than a linked-
  worktree Git file.
- Safe-move dry runs initially proposed rewriting historical sessions, audits,
  research, and verification receipts to archived paths.
- Deep agent context reran the entire project-health scan just to display a
  score, and the nominally read-only score/JSON modes always wrote a trend file.
- One broad JSON patch attached the merge-guard aliases to adjacent operations;
  an immediate parsed-registry inspection caught the wrong owners.
- Two optional shell inspections failed because zsh rejected an unmatched glob
  and did not split a quoted pair variable like bash; neither command wrote.
- Focused control/context tests initially retained exact-operation permission
  and executable generator-bridge assumptions after those surfaces became
  aliases and archived files.
- The first generated handoff again truncated a wrapped session `Focus` value,
  despite the same parser limitation having been recorded in MAINT-012C.
- The first broad Python run reached 6,838 passes but failed one readiness-truth
  test because the retained performance authority became WARN under suite-order
  cwd state.
- The first normal commit attempt was stopped by the session-doc hook because
  the newest entry omitted its explicit Git handoff receipt line; no commit was
  created.
- The first direct retry guessed a nonexistent `check_session_docs.py` filename
  from the hook label instead of reading its configured entry.

### Root causes and resolutions

- Confirmed root cause: task/handoff closeout state was not reconciled after the
  prior merges. Resolution: activate MAINT-012D and record MAINT-012B/C as done
  with exact merge commits; validate the task board at candidate freeze.
- Confirmed root cause: the context CLI is area-manifest based rather than an
  operation namespace. Resolution: list valid areas, then inspect `automation`
  and `verification`. ⚠️ TERMINAL ISSUE: unknown context area `operations` ->
  used `./run.sh context list` and the two maintained areas.
- Confirmed root cause: the probe inferred an interpreter from the `.sh` path.
  Resolution: inspect shell scripts with `bash`/read-only source commands and
  use `python_runtime.sh` only for Python. ⚠️ TERMINAL ISSUE: shell source sent
  to Python -> reran the intended read-only inspection with the correct runtime.
- Confirmed root cause: both retired health scripts encoded primary-checkout
  layout assumptions and duplicated maintained owners. Resolution: archive them,
  route health to worktree-bound `project_health.py`, and repair the active agent
  context caller to read the latest recorded receipt. Project health now writes
  only for explicit `--write` or `--fix`; normal score/JSON scans remain read-only.
- Confirmed root cause: automatic path replacement did not distinguish live
  callers from immutable evidence or absence assertions. Resolution: teach
  `safe_file_move.py` the preservation boundary, regression-test live versus
  preserved references, and require all sixteen dry runs to show no historical
  rewrite before moving.
- Confirmed root cause: the patch context matched repeated JSON permission
  blocks rather than named operations. Resolution: patch using operation-name
  anchors and immediately parse/inspect alias ownership before projection.
- Confirmed root cause: the inspection snippets used bash word-splitting/glob
  assumptions under zsh. Resolution: use exact paths and direct per-target tool
  calls. ⚠️ TERMINAL ISSUE: unmatched glob and quoted-pair splitting failed ->
  replaced with exact `rg` paths and per-file safe-move invocations.
- Confirmed root cause: the regressions were written for the temporary 12A/12B
  compatibility stage rather than the 12D end state. Resolution: canonical
  permission tests use canonical operation names, legacy intent is proved by
  alias discovery, and context tests now require active bridge absence plus a
  passing live context manifest. Exact failed-test reruns passed.
- Confirmed root cause: handoff extraction reads only the physical `Focus` line,
  not Markdown continuations. Resolution: keep the value on one line and rerun
  the receipt-bound handoff writer. The regenerated block contains the complete
  focus. This parser hardening remains a future control improvement because it
  does not change MAINT-012D's scanner/script outcome.
- Confirmed root cause: `audit_readiness_report.py` used process-relative `Path`
  existence/reads even though its command runner was repository-bound. A prior
  test cwd could therefore hide real evidence. Resolution: resolve every audit
  evidence path from the script-derived repository root, pass concise relative
  paths to the runner, and regression-test the performance authority from an
  unrelated cwd. The failed test and the affected readiness suite pass; the
  broad candidate is rerun because this changes readiness outcome.
- Confirmed root cause: generating the receipt and next-session handoff does not
  automatically add the receipt field to a manually authored session entry.
  Resolution: bind the existing validated receipt explicitly in this entry,
  rerun only the failed session-doc check, and let normal hooks revalidate the
  staged candidate. The failed attempt left `HEAD` unchanged.
- Confirmed root cause: the human hook name differs from its actual command,
  `scripts/session.py check`. Resolution: inspect `.pre-commit-config.yaml` and
  run `./run.sh session check`, which passed. ⚠️ TERMINAL ISSUE: guessed session
  checker path did not exist -> used the configured session command.

### Verification

- Focused control, migration, Git, context, verification, CI, session, and
  evolution regressions passed after exact reruns of the changed assumptions.
- Direct control/context/verification manifests, script references, Git
  workflow, CLI reference/smoke, links, task format, and full-spec OpenAPI
  checks pass. Script references report zero runtime breaks and zero misleading
  outputs.
- The immutable candidate additionally requires one broad Python run, one fresh
  quick gate, one cumulative full gate, ordinary commit hooks, and every
  applicable hosted check. Those execution/PR facts remain in receipts, GitHub,
  and the external handoff rather than causing a post-push documentation commit.

## 2026-08-23 — Session: MAINT-012C evidence scheduling and exact PASS reuse

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-012c-evidence-scheduling`, from exact merged
`origin/main` commit `646660e323b65118a805b554c6cf4dbef46ef479`.

**Git handoff receipt:**
`docs/verification/maint-012c-git-handoff-receipt.json`

**Focus:** Modernize validation scheduling and reuse only exact PASS evidence.

### Summary

- Added a strict seven-domain verification manifest and one read-only CLI for
  validation planning, fingerprints, receipt probing, and PASS recording.
- Migrated local changed checks/tests and hosted applicability to the same
  whole-candidate plan. Unknown paths or Git-query failures select every domain.
- Added shared-Git local PASS reuse, exact-key hosted evidence reuse after
  runtime/dependency resolution, a fresh-run override, and one consolidated
  quick pre-commit hook. Git-state checks always execute.
- Product behavior, dependencies, scanners, physical compatibility scripts,
  release authority, settings, and professional approval remain unchanged.

### Issues encountered

- The startup command batch executed in the primary checkout after creating the
  new linked worktree, so its first session/source/Git proof described `main`
  instead of the 12C lane.
- The inherited local changed-check path used only `HEAD~1..HEAD` and returned
  no work for unmapped paths or Git-query failures; hosted CI separately owned a
  second YAML path map.
- The first partial-tree quick diagnostic failed CLI discovery because the new
  top-level verification script existed before its control-registry transaction
  and generated compatibility projection were complete.
- The first focused workflow-test batch retained one assertion for the removed
  YAML path-filter variable, so that test failed after the canonical planner
  replaced the duplicate filter.
- Inspection found that the parallel check runner could reach its aggregate
  timeout without adding a result for each unfinished future; the final total
  could therefore omit required checks.
- The initial manifest draft routed every known `scripts/**` change to all seven
  product domains, which was safe but would preserve unnecessary broad reruns.
- The old unconditional repository job mixed docs, architecture, registries,
  CLI policy, YAML, and migration checks, so making it conditional without
  reallocating ownership would either skip evidence or keep broad scheduling.
- The active link-governance and CI learning guides still taught the retired
  per-link hook, `dorny/paths-filter`, 28-check/17-workflow topology, bare
  `.venv` commands, and a retired commit helper.
- The first consolidated focused selection found one governance test still
  looking for CLI smoke in the repository job after that check moved to its
  natural control-plane owner.
- Preparation produced an incomplete auto-handoff focus because the session
  entry's `Focus` value wrapped onto continuation lines.
- The cumulative full gate initially passed 30/31; the Git-workflow checker
  still required the retired standalone merge hook and literal YAML
  `scripts/**`/`docs/**` filters.
- The repaired checker passed as a script but its focused semantic-test import
  initially failed to resolve the sibling verification module.

### Root causes and resolutions

- Confirmed root cause: one terminal call has a static working directory;
  creating a worktree does not retarget later commands in that call. Resolution:
  rerun session brief/start, context routing, source diagnosis, and Git-state
  authority with the 12C worktree as the explicit working directory; it reported
  `source_bound=true` and `READY_LOCAL`, while primary `main` remained clean.
  ⚠️ TERMINAL ISSUE: post-creation startup commands stayed in primary `main` ->
  reran the complete startup proof with the explicit 12C worktree.
- Confirmed root cause: local and hosted classification evolved independently
  from prefix/path filters with no coverage invariant or fail-closed unknown
  state. Resolution: both now load the strict manifest, compare the whole
  candidate, and expand unknown/query-failed impact to all seven domains; PR
  Gate rejects missing flags and partial fallback.
- Confirmed root cause: top-level script coverage intentionally fails during an
  incomplete registry transaction. Resolution: add the active read-only
  `verification impact` operation, refresh the deterministic legacy projection,
  and add the CLI smoke contract. Control validation then reported 124 active
  operations and 115/115 scripts.
- Confirmed root cause: the workflow test refactor removed the local
  `control_paths` collection but left one membership assertion behind.
  Resolution: replace it with assertions against the canonical planner command
  and exact control-test command; the failed node and then the complete focused
  workflow/control selection passed.
- Confirmed root cause: `as_completed(...)` returned only observed futures, and
  the timeout handler cancelled the rest without materializing failed results.
  Resolution: every missing future now becomes an explicit timed-out failure;
  a regression proves an omitted result cannot produce a green total.
- Confirmed root cause: a blanket script rule confused verification-engine
  changes with known domain-specific check scripts. Resolution: one rule set now
  drives both scheduling and fingerprint inputs; verification-engine changes
  select all domains, known API/docs/control scripts select their affected
  domains, and only unknown paths use the all-domain fallback.
- Confirmed root cause: repository validation had accumulated checks belonging
  to four other authorities because it was previously always-run. Resolution:
  documentation now owns versions/tasks/links, Python/FastAPI own architecture,
  control owns registries/CLI policy, and repository owns YAML, hygiene, and
  exact maintenance-script contracts. Workflow regressions prove no command was
  lost and every command file belongs to its fingerprint domain.
- Confirmed root cause: the two active teaching guides were not migrated when
  MAINT-008 consolidated workflows and the current packet consolidated hooks.
  Resolution: update both to the 10/31-check topology, manifest planner,
  repository runtime commands, exact quick hook, four retained workflow lanes,
  and explicit release authority.
- Confirmed root cause: the runtime-launcher regression encoded the old job
  location rather than the check's ownership contract. Resolution: retarget it
  to the control-plane job while retaining the required install-before-smoke
  assertion; the failed node and consolidated focused selection then passed.
- Confirmed root cause: the handoff formatter reads the physical `Focus` line,
  not Markdown continuation lines. Resolution: make the bounded focus a single
  complete line and regenerate the preparation handoff block.
- Confirmed root cause: the Git-workflow checker duplicated the pre-12C hook
  and hosted path-routing topology instead of consuming their new authorities.
  Resolution: require the consolidated quick hook's explicit completion flag,
  require the workflow planner outputs, and verify script/docs ownership through
  the canonical manifest. The failed check and then the cumulative gate passed.
- Confirmed root cause: direct script execution adds `scripts/` to `sys.path`,
  while importing it as `scripts.check_codex_git_workflow` from pytest does not.
  Resolution: bind the checker's own script directory before importing the
  sibling verification control; direct and package-import regressions passed.

### Validation through content freeze

- Focused verification/control/workflow/Git/session/migration regression
  selection: PASS after the recorded ownership-test repair.
- Black and Ruff on every changed Python file: PASS. YAML compose validation:
  PASS. `git diff --check`: PASS.
- Verification manifest: PASS, 7 domains and 24 rules; control plane: PASS,
  124 active operations and 115/115 scripts; context manifest: PASS, 10 areas
  and zero generated folder indexes; CLI smoke: 16/16; token efficiency: PASS.
- Pre-commit handoff receipt: valid fail-closed `HOLD`, local-state hash
  `sha256:f4662fdc2b557aeb1c0011ce4f7aac795b09a4cb7cd704923e9dd4b0054da485`.
- Pending final quick, cumulative full, hook, exact-head, and hosted evidence.

## 2026-08-23 — Session: MAINT-012B index architecture and retirement

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-012b-index-architecture`, from exact `origin/main`
commit `efd219178c4293ab106f43e37b903c5c268283aa`.

**Git handoff receipt:**
`docs/verification/maint-012b-git-handoff-receipt.json`

**Focus:** Replace high-churn generic indexes with a small validated context
manifest and read-only live summaries without changing product, structural,
release, or hosted-check behavior.

### Summary

- Retired 140 generated artifacts: all generic folder `index.json` files, 69
  generic folder `index.md` files, and the 8,254-line global docs projection.
  Retained only two authored MkDocs route pages and one specialized Git-policy
  manifest under an explicit allowlist.
- Added `scripts/context-manifest.json`, `scripts/repo_context.py`, and
  `./run.sh context` for strict routing validation plus bounded, deterministic
  live-worktree summaries. Validation rejects unknown fields, duplicate JSON
  keys, path escapes, missing authorities, inactive operations, and tracked or
  untracked generic-index reintroduction.
- Converted the three legacy generator entry points to read-only deprecation
  bridges, migrated session/evolution/nightly/governance consumers, preserved
  command discovery through the canonical control plane, and removed all
  active instructions requiring an index refresh.
- Measured the retired baseline at 141 generated/index-named artifacts,
  1,391,320 bytes, and 43,141 lines. The old all-index check covered only 32 of
  70 folder JSON indexes, while direct targeted `rg --files` was effectively
  instantaneous and the live context summary stays bounded without committed
  timestamps or hashes.

### PRs Merged

- None. MAINT-012B remains a local frozen-candidate workflow until its quick,
  full, hook, hosted, and exact-head acceptance evidence completes.

### Issues encountered

- The first inventory assumed a repository-root `index.md`, but no such file
  existed, so the read-only command failed before the exact topology was known.
- The initial validator reported every intended deleted index as still present.
- Retiring the generated Markdown indexes exposed three current README links
  that still pointed directly to those generated files.
- The first focused contract run had four failures: three tests still expected
  deprecated generator operations to own permissions/discovery, and one
  session test still expected changed-document index scheduling.
- Review of the first validator revision showed that an untracked regenerated
  generic index would not be rejected until it was staged.
- The affected documentation/governance batch used `check_governance.py --all`,
  but that validator exposes the complete profile as `--full`.
- The current documentation hub still paired its old index generators with a
  removed governance `--index-links` option.
- The first full 31-check gate passed 30 checks but the Git-workflow checker
  still opened the deleted `docs/agents/guides/index.json` projection.

### Root causes and resolutions

- Confirmed root cause: root-index presence was inferred from the old indexing
  convention instead of discovered from Git. Resolution: inventory exact paths
  with `rg --files` and `git ls-files`; the measured baseline is 70 generic
  JSON indexes, 70 generic Markdown indexes, and one global docs projection.
  ⚠️ TERMINAL ISSUE: assumed a root `index.md` existed -> used `rg --files` to
  inventory exact maintained index paths.
- Confirmed root cause: `git ls-files --cached` includes paths deleted in the
  working tree. Resolution: subtract `git ls-files --deleted`, fail closed if
  that query cannot complete, and retain the filesystem fallback only when Git
  inventory is unavailable. Live manifest validation then passed with zero
  generated folder indexes.
- Confirmed root cause: three authored README tables used generated index pages
  as navigation targets. Resolution: remove only those obsolete rows; the full
  link scan passes 379 Markdown files, 935 internal links, and zero failures.
- Confirmed root cause: permission resolution intentionally considers active
  operations only, but compatibility queries and tests still treated the three
  deprecated generators as active owners. Resolution: move their legacy names
  into the active read-only `repository context` aliases, keep the old entries
  visibly deprecated, and remove changed-folder scheduling expectations. The
  exact four failed nodes then passed without weakening permission failure.
- Confirmed root cause: the first topology scan combined tracked and fallback
  behavior but omitted Git's untracked set. Resolution: include
  `--others --exclude-standard` and add a temporary-repository regression that
  proves an untracked `index.md` fails immediately.
- Confirmed root cause: the broad-profile flag was inferred from the adjacent
  documentation checker instead of read from the governance CLI. Resolution:
  inspect `--help` and run the maintained `check_governance.py --full` profile.
  ⚠️ TERMINAL ISSUE: `check_governance.py --all` is unsupported -> used its
  documented `--full` profile; the earlier command made no repository writes.
- Confirmed root cause: the documentation-maintenance snippet predated both the
  unified docs checker and MAINT-012B routing. Resolution: replace it with
  `context validate`, optional live summary, `check_docs.py --all`, and the
  maintained link checker. Every displayed command now exists and is read-only.
- Confirmed root cause: the specialized live-Git guidance manifest delegated
  one surface set to the generic folder-index format, so its checker had a
  hidden runtime dependency that the earlier reference scan did not classify.
  Resolution: define a bounded `live_surface_sets` root/glob contract, discover
  those Markdown files from the current worktree, preserve explicit deprecated
  boundaries, and fail closed if the retired indexed form returns. The failed
  Git-workflow check and its semantic regression file are the repair evidence.

### Validation through content freeze

- Source binding is `source_bound=true`; the isolated lane is based on exact
  merged `origin/main` commit `efd219178c4293ab106f43e37b903c5c268283aa`.
- Black and Ruff pass every changed Python contract. The context validator
  passes under `python -S`, and control validation reports 123 active
  operations with 114/114 top-level scripts represented.
- CLI smoke passes 15/15, including live context validation and bounded summary.
  The consolidated focused selection passes 271 tests across repository
  context, control plane, governance, session, release, and CI-workflow
  contracts. The link scanner validates all 935 internal links.
- MAINT-012C evidence reuse/change-domain scheduling, MAINT-012D physical
  compatibility-script retirement and scanner consolidation, dependency work,
  product code, formula/API/UI/Excel/ETABS behavior, release publication, and
  professional approval remain excluded.

## 2026-08-23 — Session: MAINT-012A canonical control-registry foundation

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/maint-012a-control-registry`, from exact `origin/main`
commit `fc904511cc7b9683b2b464cdef71a45d2e9ee277`.

**Git handoff receipt:**
`docs/verification/maint-012a-git-handoff-receipt.json`

**Focus:** Implement MAINT-012A canonical operation registry and compatibility projection.

The versioned registry replaces duplicated and implicit metadata while
preserving existing commands during migration.

### Summary

- Added the Draft 2020-12 control-plane schema, fail-closed loader, and
  `./run.sh control` validation/search/list/statistics/projection interface.
- Migrated discovery, tool search, prompt routing, permission enforcement and
  audit, governance permission validation, script coverage, and session context
  guidance to `scripts/control-plane.json`.
- Represented 128 total/125 active operations and 113/113 top-level scripts;
  all active operations now have explicit default permissions and structured
  command steps. `automation-map.json` is an exact generated projection.
- Froze MAINT-012B-D as separate successor packets for index architecture,
  evidence reuse/validation scheduling, and scanner/script consolidation.

### PRs Merged

- None. MAINT-012A remains an unpushed local candidate until the post-freeze
  local gates, exact-head review, required hosted checks, and merge complete.

### Key Deliverables

- `scripts/control-plane.json` and `scripts/control-plane.schema.json`
- `scripts/control_plane/` validated loader and CLI
- `Python/tests/test_control_plane.py` parity, schema, alias, permission,
  structured-command, missing-target, duplicate-key, and determinism contracts
- `docs/planning/maint-012-control-plane-modernization.md`
- `docs/verification/maint-012a-git-handoff-receipt.json`

### Issues encountered

- The legacy map contained 78 active operations without default permissions,
  plus three deprecated Git-compatibility operations omitted from the initial
  active-only inventory. The first import therefore stopped fail-closed rather
  than silently assigning them.
- One legacy alias used mixed case (`release CI parity`), so canonical alias
  normalization correctly rejected the first generated candidate.
- Placing the loader and CLI as new top-level `.py` files would have changed the
  frozen script inventory from 113 to 115 and forced self-registration churn.
- The inherited next-session brief still described the uncommitted MAINT-011
  candidate even though MAINT-011 was already merged.
- Active bootstrap, automation-catalog, and cross-agent instruction surfaces
  still named the legacy automation map without a canonical/projection boundary.
- The first generated handoff block selected MAINT-011 instead of MAINT-012A.
- The first staged session-doc hook rejected the new brief's lowercase
  `Required reading` heading.
- The first hosted repository, Python, and control-plane jobs could not import
  `jsonschema`; their aggregate PR Gate therefore failed.

### Root causes and resolutions

- Permission metadata had been added incrementally to only 47 of 125 active
  operations; absence was tolerated by discovery even though permission lookup
  failed closed. Every canonical operation now declares one of the four known
  levels, with explicit mode elevations for mixed read/write commands.
- Aliases previously lived in both per-task fields and a hard-coded tool map,
  with no normalization/ownership invariant. All aliases now live normalized in
  the canonical registry; duplicate owners and operation collisions fail.
- The script counter intentionally covers only active top-level tools. The new
  implementation was placed in `scripts/control_plane/`, leaving 113/113
  coverage exact while providing a namespaced control module.
- The stale brief had no live-state guard after the predecessor merge. It now
  records the exact MAINT-012A base, boundary, current parity, and next action.
- Active entry documents now point to the control registry and compact validator;
  historical audits, deprecated guides, and immutable receipts remain unchanged.
- Session handoff discovery recognizes dated headings only when they retain the
  `Session` marker. Restoring `Session: MAINT-012A` made the generated block bind
  to the current entry and exact MAINT-012A receipt.
- The session checker intentionally treats `Required Reading` as an exact
  structural contract. Restoring that capitalization made the focused staged
  hook decisive without weakening the checker.
- `jsonschema` is an existing optional `validation` extra, while the affected
  hosted lanes intentionally install `Python[dev]`. The local full environment
  masked that difference. The loader now evaluates the exact schema keywords it
  uses with the Python standard library, preserving strict validation without a
  dependency or workflow change.
- Proof: `./run.sh control validate` reports PASS at 125 active operations and
  113/113 scripts; the two focused control/governance files pass 61 tests; the
  legacy projection check, tool stats, find alias smoke, and permission audit
  pass. Final consolidated gates remain acceptance evidence outside the frozen
  candidate content.

### Notes

- MAINT-012A does not retire indexes, cache test evidence, reschedule scanners,
  delete/move legacy scripts, change CI topology, or alter product/release
  behavior. Those boundaries remain separately reviewable.


## 2026-08-22 — Session: MAINT-011 developer gate hygiene

**Agent:** Codex (`governance` + `ops`, sole writer)

**Branch:** `codex/maint-011-developer-gate-hygiene`, from exact merged PR #837
commit `3f61bd93d92b7092a55e25b8ca99eda4b3335ff1`.

**Git handoff receipt:**
`docs/verification/maint-011-git-handoff-receipt.json`

**Focus:** Complete the 13 confirmed MAINT-011 findings plus any additional
reproduced root cause in one branch/PR. Finish all implementation, tests,
documentation, task/handoff records, and the receipt before one consolidated
focused/hook/quick/full validation sequence. Formula work, Excel features,
ETABS, INDIA-3 implementation, release publication, and destructive cleanup
remain excluded.

### Summary

- Gave all three text normalizers one explicit preservation boundary for
  archived, vendored, and frozen artifacts while retaining active-file hygiene;
  excluded only the two deliberate TypeScript JSONC configs from strict JSON.
- Dispositioned all eight Bandit findings without a broad exclusion: candidate
  searches now log expected domain rejections and propagate unexpected faults,
  HTTP examples have finite timeouts, and vacuous security tests now assert
  exact HTTP/WebSocket behavior.
- Preserved staged mypy, documented typed loop-variable ownership, reconciled
  active instructions to the live 31-check registry, repaired alias discovery,
  and documented the global/leaf/deepest-parent index sequence.
- Added a worktree-local React readiness probe and exact pinned-Node `npm ci`
  remediation; added shell-safe zsh examples for globs, literal backticks, and
  package extras.
- Made audit summaries retain the first hard failure plus final context, added
  explicit executable-versus-parked performance authority, clarified Excel
  skip semantics, and separated historical transition receipts from successor
  final-merge observations.
- Made the next-session brief's receipt path, embedded local-state hash, and
  status machine-checked against the selected receipt object. Added M11-14 for
  the live bare-`pre-commit` PATH failure and converted maintained commands to
  the repository-bound Python launcher.

### Issues encountered

- The documented all-file hook path could rewrite 1,738 preserved files and
  then fail on two JSONC configs, three core Bandit findings, and five FastAPI
  findings even though the cumulative gate was green.
- Three research/service candidate loops silently swallowed every exception;
  three FastAPI security tests allowed any exception to count as success; two
  live HTTP examples had no finite timeout.
- Active developer instructions carried a stale 30-check count, automation
  aliases were stored but ignored by the unified tool registry, and a fresh
  worktree's `node_modules` directory was not a reliable readiness contract.
- Compact readiness details retained only trailing warning lines, and the
  session checker did not compare the brief's receipt identity with the
  selected receipt object.
- Live preparation confirmed that the repository runtime can import
  `pre_commit` while the bare executable is absent from this shell's PATH.
- One MAINT-011 inspection used an unquoted speculative test-file glob; zsh
  rejected it before `rg` ran.
- The first handoff-receipt command also left `**` path contracts unquoted;
  zsh expanded them into hundreds of arguments before the generator ran.
- The first final all-file replay still normalized 38 tracked paths and the
  session hook could not resolve the newly generated receipt from the log.
- The task board still called merged LIB-PRO-005 a local candidate because its
  immutable predecessor correctly did not receive a post-push status commit.

### Root causes and resolutions

- M11-01/02 root cause: generic normalizers and strict JSON selection had no
  representation of repository-owned preserved bytes or deliberate JSONC.
  Resolution: share exact preservation roots across every mutating text hook
  and exclude only `tsconfig.app.json`/`tsconfig.node.json` from `check-json`.
  Proof contract: configuration regressions require preserved roots to match,
  active docs to remain included, and ordinary project JSON to remain strict.
- M11-03 root cause: broad exception swallowing conflated expected candidate
  rejection with implementation faults, while example/security code lacked
  decisive network and authentication assertions. Resolution: catch/log only
  expected value/type/arithmetic errors, let unexpected failures propagate,
  set 30-second HTTP timeouts, and assert public no-token ping plus invalid-token
  close code 4001. Both Bandit hooks retain full source-tree scope.
- M11-04 root cause: mypy retains the first loop variable's inferred type in a
  function. Resolution: keep staged mypy and document distinct ownership names
  plus narrowing for differently typed iterables.
- M11-05 root cause: count-bearing instructions were manually duplicated after
  the 31st registry check was added. Resolution: update all three active
  surfaces and bind their statement to `check_all.CATEGORIES` in a regression.
- M11-06 root cause: the automation map had weak aliases and `tool_registry.py`
  discarded task aliases entirely. Resolution: add maintained/legacy/intention
  aliases, index them in both discovery paths, document default dry-run modes,
  and freeze global catalog then leaf-to-parent index ordering.
- M11-07 root cause: ignored dependencies are worktree-local and directory
  existence does not prove Vite/Vitest/TypeScript/ESLint readiness. Resolution:
  probe exact local tools before React commands and print one root-stable pinned
  Node `npm ci` command; never copy dependency trees between worktrees.
- M11-08 root cause: zsh expands unmatched globs, backticks, and square-bracket
  extras before the intended program receives them. Resolution: add quoted
  literal examples and prefer exact paths discovered with `rg --files`.
  ⚠️ TERMINAL ISSUE: an unquoted `test_sync_numbers*` inspection aborted in zsh
  and unquoted receipt `**` contracts expanded before argument parsing -> reran
  with exact maintained paths/literal quoted contracts and added the governing
  examples; neither failed command mutated repository state.
- M11-09 root cause: `_diagnostic_summary()` selected only the final three
  lines. Resolution: select the first error/failure/invalid/exception line and
  append the last two distinct context lines, with a mixed error/warning test.
- M11-10 root cause: a time-bound transition receipt and a final merge
  observation have different identities and lifetimes. Resolution: validate
  the receipt during final pre-push session closeout, retain it unchanged after
  expiry, and keep hosted/merge facts in the successor external observation.
- M11-11 root cause: selective path classification was being read as missing
  Excel validation. Resolution: document that non-applicable Excel must skip,
  required PR Gate verifies the classification/skip pair, and cross-product
  local Excel acceptance remains separate.
- M11-12 root cause: parked reporting automation was conflated with missing
  executable thresholds. Resolution: readiness names
  `fastapi_app/tests/test_load.py` as latency/degradation authority and the
  workflow document as the parked standalone reporter disposition.
- M11-13 root cause: artifact SHA-256 and embedded local-state SHA-256 are both
  valid-looking but semantically different, and only the generated output knew
  which one was required. Resolution: compare brief path/hash/status with the
  receipt object during preservation, session check, and session end.
- M11-14 root cause: `pre-commit` is installed in the approved repository
  environment, not guaranteed on the interactive shell PATH. Resolution:
  convert maintained install/run examples to
  `./scripts/python_runtime.sh -m pre_commit`.
- M11-15 root cause: the session-log convention permits the receipt path on the
  line after its bold label, while `_parse_git_receipt_path()` accepted only an
  inline value. Resolution: parse either maintained representation and freeze a
  wrapped-Markdown regression, so the session hook resolves the selected
  receipt before comparing its brief identity.
- Final-hook root cause: the first preservation boundary still omitted the
  generated `.vite/` cache and React migration fixtures, while 34 active
  text/config/index assets on `main` genuinely lacked canonical terminal
  newlines. Resolution: restore the four generated/frozen files byte-for-byte,
  add their exact roots to every normalizer exclusion, and retain the hook's
  one-time newline normalization only for the 34 active assets. The affected
  indexes and byte-clean hook evidence are regenerated once after this repair.
- Task-state root cause: closeout freeze forbids updating a reviewed candidate
  only to add hosted/merge facts. Resolution: re-observe PR #837 from the new
  authorized MAINT lane and reconcile LIB-PRO-005 as merged at `3f61bd93`.

### Validation boundary

- All intended source, test, instruction, task, handoff, issue, and receipt
  content is frozen before validation. The final write is the affected-index
  refresh in dependency order.
- One consolidated sequence owns formatting/lint/type checks, focused Python
  and FastAPI regressions, strict JSON/Bandit, command discovery, staged/all-file
  hook parity in a disposable clean worktree, quick 10/10, full 31/31, audit,
  immutable candidate review, required hosted checks, and merge.
- Excel/product/release/ETABS suites are not rerun because no changed path owns
  those implementations; Excel skip semantics are proven by the CI contract.
- Exact pass/fail, PR, hosted, and merge facts remain external read-only
  closeout evidence after this candidate freezes.

### Handoff

Commit only the MAINT-011 paths after the consolidated local acceptance passes,
push one branch, open one PR, and merge only the unchanged reviewed head when
every required hosted check succeeds. Retain the branch and worktree; deletion
remains separately authorized. Select core Indian-code/earthquake/ETABS work in
a new bounded task rather than extending this maintenance candidate.

## 2026-08-22 — Session: LIB-PRO-005 confirmed release-safety closure

**Agent:** Codex (`backend` + `api-developer` + `frontend` + `ops`, sole writer)

**Branch:** `codex/lib-pro-005-release-safety-closure`, from exact merged PR
#836 commit `f1a9937cfdba4c72c22e6219ffaf02f94809f1a5`.

**Git handoff receipt:**
`docs/verification/lib-pro-005-git-handoff-receipt-2.json`

**Focus:** Independently reproduce the post-`LIB-PRO-004` audit claims, repair
only confirmed outcome-changing defects, batch all writes before cumulative
verification, and complete the normal Git/PR/check lifecycle. Tag, publication,
professional approval, ETABS, new structural capability, and destructive lane
cleanup remain excluded.

### Summary

- Made all nine WebSocket beam-design values explicit and fail-closed; an empty
  payload now returns a sanitized error and cannot produce a default beam.
- Removed concrete-rate invention from both BOQ surfaces, required complete
  coverage for used grades, and corrected mixed-grade story cost arithmetic to
  use exact per-beam rates.
- Added finite-real/type ownership at equivalent shear, pure development
  length/bond stress, and beam-outline boundaries, with direct regressions.
- Declared the experimental PMM NumPy extra, restored four workflow-catalogue
  root exports, and preserved canonical fail-closed streaming statuses in
  React while keeping blocked records non-exportable.
- Confirmed that performance CI is intentionally parked and Excel CI is
  intentionally path-aware, so neither required workflow rewiring. Updated the
  two exact active counts identified by the maintained number synchronizer.
- Rebound the input auditor to the guarded development-length delegate. It now
  reports 132 `PROVEN`, 96 `DELEGATED`, 361 `UNPROVEN`, and 130
  `NOT_APPLICABLE` parameters; its expected exit 1 keeps readiness `PARTIAL`.
- Preserved the encountered hook/CI/legacy-tool issues, root causes, evidence,
  safety constraints, and measurable exit criteria in the separate
  `MAINT-011` follow-up; no adjacent tooling repair was mixed into this packet.

### Issues encountered

- The active task board and next-session handoff still described
  `LIB-PRO-004` as a local candidate, although PR #836 and all required checks
  were merged at `f1a9937c`.
- Root-cause tracing found that the service BOQ did not only invent missing
  rates; it also priced each story with an average of project grade rates.
- The repaired development-length adapter remained a static-auditor false
  negative because its guarded pure calculation was absent from the explicit
  delegate set.
- The first empty-WebSocket regression expected Pydantic's detailed "required"
  wording, but the maintained error sanitizer intentionally returned a generic
  invalid-input message.
- The linked worktree had no ignored React dependencies. A shared Vitest binary
  could not resolve Vite from this worktree, and the first direct npm test had
  no local Vitest command.
- Three inspection commands used unmatched zsh globs or unescaped backticks,
  and one guessed `sync_numbers.py --check` flag did not exist.
- The first final index batch named three folders that have no maintained
  folder-level index topology; the live generator correctly refused them, and
  the subsequent all-index check found two stale parent indexes.
- The first readiness run reported the documentation contract as failed while
  its compact detail ended with the permitted 405-file soft-budget warning;
  the direct checker exposed one invalid front-matter value in the new plan.
- The first full repository gate passed 29/31 checks but rejected a stale API
  classification registry and three rows in the WIP-limited Active task table.
- The first exact-wheel PMM-extra install command let zsh interpret `[pmm]` as
  an array subscript instead of part of the wheel requirement.
- A direct task-format rerun guessed `check_tasks.py` even though the search
  result identified the maintained script as `check_tasks_format.py`.
- The first repaired-index command guessed an active
  `generate_folder_index.py`; that legacy helper is archived and the maintained
  generator has a different name.
- The all-file hook mode normalized 1,738 out-of-scope vendored/reference files,
  rejected two existing JSON-with-comments configs as strict JSON, repeated
  known repository Bandit findings, and found one in-scope BOQ mypy error.
- A combined focused-proof shell changed into `Python/` for mypy and then tried
  later workspace-root launcher paths from that persisted directory.
- The first `MAINT-011` front matter used intuitive status `planned`, which is
  not in the enforced lowercase status vocabulary.
- The original time-bound transition receipt aged past its evidence window
  during cumulative tests and correctly failed with three stale-evidence holds.
- The manually refreshed next-session brief used the successor receipt file hash
  where the handoff contract requires its embedded local-state receipt hash.

### Root causes and resolutions

- Confirmed root cause: durable task state predated the merged `LIB-PRO-004`
  candidate. Resolution: verify PR #836 live, bind this lane to its exact merge,
  mark the predecessor done, and write a bounded `LIB-PRO-005` plan/evidence
  handoff. Evidence: PR #836 is merged with required PR Gate success and local
  `origin/main` equality at `f1a9937c` before mutation.
- Confirmed root cause: BOQ rate selection used `.get(..., 6000)` and story
  totals multiplied all concrete by a project-wide mean rate. Resolution: add
  one shared rate-table resolver, reject uncovered used grades, use direct
  indexing after proof, and accumulate exact concrete cost per story. Evidence:
  missing custom/default grade regressions and exact mixed-grade arithmetic pass.
- Confirmed root cause: the audit recognizes only named guarded calculation
  delegates and could not infer the validated pure detailing implementation
  behind the service adapter. Resolution: add exactly
  `calculate_development_length` to that evidence set and freeze a synthetic
  delegation regression. Evidence: all five adapter parameters are delegated
  and unresolved ownership falls from 370 to 361 without hiding other rows.
- Confirmed root cause: production sanitization deliberately avoids returning
  raw validation detail. Resolution: assert the safe public message and the
  absence of design data, not internal Pydantic prose. The failed-only node
  passes with all nine fields logged internally as missing.
- Confirmed root cause: Git worktrees do not share ignored `node_modules`, and
  ESM resolves config dependencies relative to the worktree. Resolution: run
  one exact-lockfile `npm ci`, then the focused hook test locally; the final
  frontend gate uses the repository's pinned Node 24 runtime. Evidence: 17/17
  hook tests pass.
  ⚠️ TERMINAL ISSUE: Vitest/Vite were unavailable from the fresh worktree ->
  installed its exact lockfile once and reran the failed React check.
- Confirmed root cause: zsh rejects unmatched globs, shell backticks execute
  command substitution, and the synchronizer's read-only mode is its default
  invocation. Resolution: use exact discovered paths, quote literal search
  text safely, and run `sync_numbers.py` without the invented flag.
  ⚠️ TERMINAL ISSUE: two unmatched globs, one backtick substitution, and an
  unsupported `--check` flag aborted read-only inspections -> reran each with
  exact paths/literal quoting/the documented default command.
- Confirmed root cause: a recursive dry-run can display prospective indexes in
  unmaintained subfolders, while live mode requires explicit topology approval;
  changed child indexes also invalidate maintained parent hashes. Resolution:
  do not create new `beam/`, `tests/integration/`, or `tests/unit/` indexes;
  retain the refreshed parent test index and regenerate only the reported
  `codes/` and `docs/` parents in dependency order.
  ⚠️ TERMINAL ISSUE: the live index generator refused three unmaintained
  folders -> preserved topology and used the authoritative all-index stale
  check to identify the two maintained parent refreshes.
- Confirmed root cause: `doc_type: plan` is not in the enforced documentation
  vocabulary, and the readiness summary retained only the tail of combined
  front-matter/budget output. Resolution: classify the execution plan as the
  allowed `spec` type and rerun the exact documentation/readiness checks. The
  405 active files remain below the owner-selected hard cap of 500.
- Confirmed root cause: adding four supported root exports changes the generated
  API registry, while two merged predecessor tasks had not been moved out of
  the Active section. Resolution: regenerate the classification registry and
  move `LIB-PRO-003-D`/`LIB-PRO-004` to Recently Done, leaving one active task.
  Evidence: the generator's `--check` mode and direct task-format check pass.
- Confirmed root cause: unquoted square brackets are zsh glob/subscript syntax.
  Resolution: quote the exact wheel-plus-extra requirement and rerun only the
  failed clean-environment install. PMM imports with NumPy 2.4.6 and the wheel
  metadata declares the `pmm` extra.
  ⚠️ TERMINAL ISSUE: the first wheel `[pmm]` install lost its extra selector ->
  quoted the complete wheel requirement and reran only that failed install.
- Confirmed root cause: the direct task-check filename was inferred instead of
  copied from the preceding search result. Resolution: run the discovered
  `scripts/check_tasks_format.py` path exactly.
  ⚠️ TERMINAL ISSUE: guessed task-check filename did not exist -> used the exact
  filename returned by `rg`.
- Confirmed root cause: the index command was inferred from an old naming
  pattern instead of discovered first. Resolution: locate and use the maintained
  `scripts/generate_enhanced_index.py` entry point.
  ⚠️ TERMINAL ISSUE: guessed active index-generator path did not exist -> used
  the repository's discovered enhanced-index generator.
- Confirmed root cause: `pre-commit --all-files` applies normalizers and legacy
  scans to the entire historical/vendor tree, whereas the normal commit path is
  staged-file scoped. The BOQ resolver also reused `fck` first as an integer
  mapping key and then as an object-typed iterable value, preventing mypy from
  narrowing the second loop. Resolution: reverse only the hook-created
  out-of-scope patch, retain every task-owned change, rename/narrow the required
  grade variable, and use the normal staged-file hook path. Evidence: the
  worktree returns to exactly 60 intended paths before the source repair; focused
  BOQ/mypy and staged-hook results are the decisive follow-up.
  ⚠️ TERMINAL ISSUE: all-file hooks rewrote 1,738 unrelated files and failed on
  existing JSONC/Bandit baseline findings -> reversed only that generated patch
  and switched to the repository's actual staged commit-hook path.
- Confirmed root cause: directory changes persist for every later line in one
  shell command. Resolution: keep every command rooted and run mypy through an
  explicit subshell so subsequent launchers remain workspace-relative.
  ⚠️ TERMINAL ISSUE: post-mypy commands resolved `./scripts` from `Python/` ->
  reran them from the workspace root and avoided a persistent `cd`.
- Confirmed root cause: task-board states and documentation front-matter states
  use different controlled vocabularies. Resolution: classify the not-yet-active
  follow-up document as `draft`; direct documentation validation is the proof.
- Confirmed root cause: authorization/retention observations in a transition
  receipt deliberately expire; the receipt is not final merge evidence.
  Resolution: retain the historical receipt unchanged, use the user's current
  continuation to create a second exact-branch transition observation, and
  reserve hosted/check/tree facts for the separate post-merge observation.
  Evidence: successor receipt validation returns `LIB-PRO-005 | HOLD` with only
  the expected dirty/pre-PR holds.
- Confirmed root cause: the receipt artifact hash and embedded state hash are
  both SHA-256 values but represent different identities, and the brief was
  manually refreshed instead of generated from the receipt object. Resolution:
  use the embedded `local_state_receipt_hash` printed by `session end`, correct
  the brief in a separate documentation repair commit, and preserve an
  `MAINT-011` consistency-check follow-up.

### Validation through repaired content freeze

- Focused Python/FastAPI/manual-comparison selection is 306/306; focused React
  hook is 17/17; Excel add-in is 21/21.
- The complete product gate passes its Python phase, 482 FastAPI tests, and 277
  React tests. The public-route gate passes 20 Python and 4 FastAPI targets.
- The exact built wheel passes minimal/root import, actionable missing-PMM-extra
  failure, and installed `[pmm]` import in clean environments.
- Diagnostic evidence is deterministic at 719 parameters across 101 owners:
  132 proven, 96 delegated, 361 unproven, and 130 not applicable.
- `sync_numbers.py` reports 6,760 Python tests, 89 endpoints/26 routers, 91
  public plus 18 private API helpers, and updates only its two stale targets.
- Readiness is truthfully `PARTIAL` with 22/23 passing checks and the input
  diagnostic as the sole expected warning. The quick repository gate is 10/10;
  direct API-classification and task-format checks pass after their repairs.
- The full repository rerun, hooks, immutable-candidate review, and hosted
  checks remain the final read-only closeout sequence after index refresh.
- After the hook-directed BOQ narrowing repair, mypy passes all 244 library
  source files and the exact BOQ/insights selection passes 36/36. The new
  `MAINT-011` record passes strict metadata, task-format, and brief-length checks.

### Handoff

Refresh the affected indexes once, freeze the repaired tree, run the focused
BOQ/mypy proof and normal staged hooks, create the immutable commit, push one
PR, and merge only if the exact reviewed head is unchanged and every required
hosted check succeeds. Retain the branch/worktree; deletion remains a separate
owner decision. Execute `MAINT-011` only later in a separate clean lane.

## 2026-08-22 — Session: LIB-PRO-004 lower-level safety and diagnostic truth

**Agent:** Codex (`reviewer` + `backend` + `governance`, sole writer)

**Branch:** `codex/lib-pro-004-safety-auditors`, from exact hosted Packet D
merge `640c7839f043adb0e7db02d924a9e1a3a06e1131`.

**Git handoff receipt:**
`docs/verification/lib-pro-004-git-handoff-receipt.json`

**Focus:** Review the proposed diagnostic/lower-level safety plan, verify Git
and all retained lanes first, repair the bounded six-helper defect family,
replace misleading diagnostics, and run one cumulative verification sequence.
No wider route remediation, new formula, release, ETABS, `INDIA-3`, branch
cleanup, or professional approval was in scope.

### Summary

- Fast-forwarded the clean primary checkout to the exact merged PR #835 tree,
  preserved every retained lane, and created one isolated task branch.
- Added a shared finite-real/range boundary to the six table/material helpers,
  legacy exports, and relevant `IS456Code` methods. Public Table 19 lookup is
  strict; a separate private path owns valid internally derived row bounding.
- Replaced the legacy input percentage/grade with parameter-owned `PROVEN`,
  `DELEGATED`, `UNPROVEN`, and `NOT_APPLICABLE` evidence from 101 maintained
  owners. All 370 unresolved parameters are reported and exit nonzero.
- Calibrated function quality to 88/88 without renaming public signatures or
  hiding ambiguous units; all three exact comparisons have review contracts.
- G0 returned `REVISE`: additional torsion, development-length, and geometry
  routes accept booleans/NaN, so this packet remains truthfully `PARTIAL` and a
  successor route-safety packet is required.

### Issues encountered

- Versioned task/handoff files still described Packet D as a local candidate
  even though PR #835 was merged, and the primary checkout was ten commits
  behind before the preflight.
- The proposed G0 conflated the `@clause` quality inventory with declared
  public route ownership and assumed a scanner rewrite would leave few or no
  genuine defects.
- The first input-auditor pass used the wrong inventory and weak attribution,
  first reporting 161/135 and then 370 unresolved parameters as discovery was
  corrected.
- Exact-diff review found that the repaired scanner still treated ordinary
  `Path`, `Callable`, and `Any` annotations as delegated validation owners.
- The first focused direct-call batch had 12 failures from obsolete clamping,
  unsupported Fe600 coverage, and legacy error-message assertions; the wider
  property batch then generated M50 for Table 19/20 in four cases.
- The first broad Python run had six composite failures after strict public
  Table 19 validation exposed mixed public and derived-value contracts.
- The first FastAPI run had two evidence-contract failures after a compatibility
  bridge incorrectly bounded the decisive shear input.
- The first immutable-commit attempt was blocked by the normal mypy hook because
  the new validation helper did not return a narrowed numeric type and the
  resolved compliance percentage remained statically optional.
- The isolated worktree had no Node dependencies. React used its lockfile;
  Excel has no lockfile because it has no package dependencies.
- A focused command named a nonexistent slab test path before `rg` located the
  maintained integration file.
- A combined mypy/test command changed into `Python/` and then attempted a
  workspace-root-relative test launcher from the persisted subdirectory.
- One `apply_patch` transaction could not delete and add the same scanner path
  in one call during early implementation.
- The first committed candidate revealed that the scanner replacement had
  changed `audit_input_validation.py` from executable to non-executable.

### Root causes and resolutions

- Root cause: the primary and frozen handoff predated hosted Packet D closure.
  Resolution: verify PR #835 checks/tree, fast-forward only the clean primary,
  and start from exact `640c7839`. Evidence: strict source binding and Git state
  were `READY_LOCAL` before mutation; the unrelated dirty detached lane remains
  untouched.
- Root cause: `@clause` selects calculation-quality functions but is not the
  public API authority. Resolution: bind input discovery to
  `api-classification.json`, supplement the six helpers and `IS456Code`, and
  keep the clause inventory in the function-quality checker. Evidence: 101
  owners/719 parameters are deterministic; synthetic/current-source tests pass.
- Root cause: a generic non-numeric-type fallback confused type hints with
  validated domain models. Resolution: permit `DELEGATED` only for recognized
  domain-model suffixes and make ordinary objects/raw collections `UNPROVEN`.
  Evidence: the new ordinary-object regression passes and the final decisive
  inventory reports 132 proven, 86 delegated, 370 unproven, and 131 not
  applicable parameters.
- Root cause: legacy tests encoded invalid substitution and message details
  rather than the frozen domains. Resolution: preserve compatible message
  fragments, use valid Fe550 for fallback coverage, constrain Table properties
  to M15-M40, and require invalid public percentages to raise. Evidence: all
  failed nodes and the complete Python suite pass.
- Root cause: `get_tc_value` owned both caller-supplied validation and internal
  derived row bounding. Resolution: keep the public helper strict and add a
  private finite/non-negative derived lookup used only by footing/slab; beam
  torsion receives a bounded lookup while decisive shear keeps the exact value.
  Evidence: 76 affected composite/boundary tests, 6,728 Python, and 479 FastAPI
  tests pass; failed HTTP evidence again has no invented exact utilization.
- Root cause: runtime checks do not automatically narrow an `object` or
  `float | None` for mypy across helper/control-flow boundaries. Resolution:
  make the scalar validators return the validated float and add an explicit
  fail-closed postcondition after percentage resolution. Evidence: the normal
  mypy hook and affected boundary/compliance tests pass before recommit.
- Root cause: linked worktrees do not share ignored Node dependencies, while the
  dependency-free Excel package intentionally has no lockfile. Resolution:
  install React with Node 24 `npm ci` and run Excel's direct Node 24 `npm test`.
  Evidence: 276 React and 21 Excel tests pass.
  ⚠️ TERMINAL ISSUE: `excel_addin` has no lockfile, so `npm ci` returned
  `EUSAGE` -> used its maintained dependency-free `npm test` command.
- Root cause: the guessed slab test path did not exist. Resolution: use `rg` to
  locate `Python/tests/integration/test_slab_boundary_closure.py`; the affected
  set then passed.
  ⚠️ TERMINAL ISSUE: nonexistent slab test path -> located and ran the
  maintained integration file.
- Root cause: shell working-directory changes persist for later lines in the
  same command. Resolution: rerun the 69 affected tests from the explicit
  workspace root; all pass.
  ⚠️ TERMINAL ISSUE: root-relative launcher failed after `cd Python` ->
  reran from the explicit workspace root.
- Root cause: the patch tool rejects a same-path delete/add transaction.
  Resolution: restored the scanner through two immediate patch operations; no
  content was lost.
  ⚠️ TERMINAL ISSUE: same-path delete/add patch rejected -> used two
  bounded `apply_patch` operations.
- Root cause: recreating the script through the patch tool used the default
  regular-file mode and did not preserve its executable bit. Resolution:
  restore mode `100755` in an explicit post-candidate repair commit. Evidence:
  the final Git diff reports no unintended mode change and the direct script
  help path executes.

### Validation through content freeze

- Boundary/diagnostic tests: 90 pass; public-route gate: 20 Python + 4 FastAPI
  targets; function quality: 88/88.
- Architecture/imports: 218 files with zero violations; 244 source files and
  1,459 imports with zero broken imports.
- Complete suites: 6,728 Python pass (3 skipped, 6 deselected), 479 FastAPI,
  276 React, and 21 Excel add-in tests pass.
- Quick repository gate: 10/10 pass. The rebuilt input diagnostic exits 1 with
  370 `UNPROVEN` parameters, preserving readiness `PARTIAL` and release hold.

### Handoff

Create the immutable local candidate after the one focused index refresh, run
the final read-only repository/session gates, then push one branch and create
one PR. Hosted checks may merge the unchanged reviewed head when eligible.
Retain the branch/worktree and do not begin the wider route successor without a
new bounded plan.

## 2026-08-22 — Session: LIB-PRO-003-D decisive gates and cumulative safety closure

**Agent:** Codex (`ops` + `governance`, sole writer)

**Branch:** `codex/public-route-decisive-gates`, from exact hosted Packet C
merge `027554457c58303f435dc4a9940dc683def22895`.

**Git handoff receipt:**
`docs/verification/lib-pro-003-d-git-handoff-receipt.json`

**Focus:** Make Excel-only CI, public-route safety evidence, readiness exits,
release/API wording, and documentation contracts decisive; then run one
cumulative A-D product and repository acceptance sequence. No engineering
formula, ETABS/desktop Excel, package publication, or professional approval was
in scope.

### Summary

- Added an Excel add-in path classifier, Node 24 test job, and required PR-gate
  result so an `excel_addin/**`-only change cannot bypass all 21 add-in tests.
- Added a required public-route safety runner covering the reproduced Python
  and FastAPI boundaries. The readiness report now returns 0 only for `PASS`,
  1 for `FAIL`, and 2 for `PARTIAL`.
- Made the legacy validation scanner non-green for high-risk findings or less
  than 90% heuristic coverage; made front-matter and the active-file budget a
  required readiness check. The owner changed the Markdown hard cap to 500.
- Synchronized current `v0.23.1a2` publication truth, `CITATION.cff`, and the
  distinct 89-operation/88-path API metrics without rewriting historical
  release or E1 snapshots.
- Reconciled four stale cumulative contracts exposed by A-C and regenerated
  the public API manifest plus script discovery/index records.

### Issues encountered

- The first cumulative Python run had four failures: semantic introspection
  ignored typed result unions; one flexure test intentionally used Fe10; the
  shear property strategy generated M50 outside the maintained Table 19 route;
  and release preflight still classified public `v0.23.1a2` as unpublished.
- The first failed-only release repair validated the historical authorization
  against the current dirty/post-release source tree, then exposed a stale
  `CITATION.cff` publication message and date.
- The second cumulative run found one older authorized-release fixture after
  the release-ledger matcher had become too narrow.
- The isolated worktree had no React `node_modules`; `./run.sh test --react`
  stopped at `vitest: command not found`. Direct `npm ci` used the shell's Node
  26 and emitted an engine warning before the maintained launcher selected
  Node 24.19.0 for the actual test.
- The first full repository gate passed 29/31 and correctly reported the API
  manifest plus script index/automation map as stale.
- A zsh result-capture probe used the reserved variable name `status` before
  this packet's implementation began.

### Root causes and resolutions

- Root cause: the semantic test descended only when the entire return type was
  a dataclass, while Packet C intentionally introduced a union of success and
  typed capacity-failure dataclasses. Resolution: traverse every dataclass
  member of the return union. Evidence: the semantic contract test and all
  6,653 selected Python tests pass.
- Root cause: two inherited tests generated domains that Packet B now rejects
  before calculation. Resolution: assert the low-grade flexure domain error and
  constrain only the composed shear-design strategy to M15-M40; direct helper
  strategies remain broad. Evidence: both failed nodes and the full property
  suite pass.
- Root cause: source-surface release truth read a checklist phrase and
  candidate-era `CITATION.cff`, despite the existing machine authorization and
  public release ledger. Resolution: recognize the exact authorization record,
  accept both published and historical authorized ledgers, and record the
  actual release date/message. Evidence: current and temporary-fixture release
  tests plus the full Python suite pass.
- Root cause: linked worktrees do not share ignored npm dependencies.
  Resolution: install the exact lockfile once and execute through the repository
  Node 24 launcher. Evidence: 51 React files / 276 tests pass.
  ⚠️ TERMINAL ISSUE: missing worktree-local `vitest` -> `npm ci`, then
  `./run.sh frontend runtime` proved Node 24.19.0 before the green React run.
- Root cause: Packet C's new typed slab union and Packet D's new safety script
  had not yet been regenerated into their canonical inventories. Resolution:
  regenerate the API manifest and scripts folder index after mapping the new
  script. Evidence: the final repository gate passes 31/31.
- Root cause: zsh reserves `status` as a shell parameter. Resolution: use the
  task-specific `doc_exit` and `budget_exit` names; the documentation probe then
  reported its exact exits.
  ⚠️ TERMINAL ISSUE: zsh rejected assignment to `status` -> reran with
  task-specific result variables.

### Validation through content freeze

- Public-route gate: 73 Python and 5 FastAPI adversarial cases pass; all 21
  Excel add-in tests pass.
- Cumulative product tests: 6,653 Python pass (3 skipped, 6 deselected), all
  479 FastAPI tests pass, and all 276 React tests pass across 51 files.
- Documentation: zero invalid front-matter values, 401/500 active Markdown
  files, and zero broken links. Quick gate passes 10/10.
- Full repository gate passes 31/31 after deterministic manifest/index refresh.
- Readiness is truthfully `PARTIAL` with exit 2: 21/23 pass, zero fail, and two
  warnings (62 function-quality diagnostic failures and F-rated heuristic input
  validation). Therefore package release and professional/stable claims remain
  `HOLD`; a green software regression set is not professional approval.

### Remaining holds

- Hosted PR checks, immutable candidate review, and exact candidate/merged tree
  equality remain before Packet D merge closure.
- The two advisory diagnostics require separate bounded truth triage before any
  future release decision. INDIA-3-G0 may resume only after Packet D merge and
  does not change the release/professional hold.

---

## 2026-08-22 — Session: LIB-PRO-003-C public failure contracts

**Agent:** Codex (`backend` + `api-developer`, sole writer)

**Branch:** `codex/public-route-failure-contracts`, from hosted `main` at
`e19b757ccb9922061369a236501f037ec20503ab` after exact-tree merge of
`LIB-PRO-003-B` PR #833.

**Git handoff receipt:**
`docs/verification/lib-pro-003-c-git-handoff-receipt.json`

**Focus:** Replace slab over-capacity exceptions, malformed legacy CSV zero
coercion, and invalid BOQ pricing arithmetic with truthful public failure
contracts, without changing supported engineering formulas.

### Summary

- Added one shared slab capacity-failure carrier with demand, capacity,
  utilization, clause/source provenance, a stable issue, qualified-review
  requirement, and the common `VALID/COMPLETED/FAIL` envelope.
- Returned that carrier through one-way, two-way, complete-workflow, service,
  FastAPI, and OpenAPI serialization paths while retaining exceptions for
  invalid or unsupported intake.
- Made `GenericCSVAdapter.load_forces` reject malformed and non-finite numeric
  cells with field and source-row context; blank optional cells retain the
  documented zero default.
- Rejected bool, non-real, non-finite, and non-positive BOQ rates and
  non-positive concrete grades at the Python and request-model boundaries.
- Regenerated the canonical OpenAPI baseline after the response-model change.
  Packet D, cumulative broad acceptance, release authority, INDIA-3, ETABS,
  and professional approval remain held.

### Issues encountered

- The first 122-test focused run left five adapter-test failures: four new
  parameter cases inherited assertions from the prior valid-fixture test, and
  one historical test still expected malformed text to become zero.
- A broad-context patch initially matched repeated force-row loops in the
  2,100-line adapter module and changed two unrelated adapter classes.
- Targeted mypy found that an untyped shared two-way argument dictionary widened
  required floats and source references to `object`; Ruff found two import
  blocks; Black identified three formatting-only files.
- The read-only documentation audit found an inherited 401-file count against
  its 400-file hard cap and three invalid front-matter values already present
  at the exact source base; a new Markdown packet record would raise the count
  to 402.
- The first normal commit-hook run blocked on three repository-wide mypy
  errors: Gravity Workflow read optional slab shear/serviceability results and
  release UAT read optional detailing without narrowing the new failure union.
- Hosted FastAPI validation on PR #834 left 471 tests green but failed two
  unsafe-beam routes with HTTP 422 because strict evidence hashing received an
  infinite derived utilization; `PR Gate` correctly failed with it.
- ⚠️ TERMINAL ISSUE: the first slab lookup guessed a nonexistent
  `one_way_flexure.py`; `rg --files` identified the maintained `one_way.py`.
- ⚠️ TERMINAL ISSUE: a direct complete-workflow replay omitted six required
  reviewed serviceability inputs; the already-covered one-way public endpoint
  replay was used for the exact capacity evidence instead.
- ⚠️ TERMINAL ISSUE: unquoted `index.*` probes triggered zsh `no matches
  found`; a literal `find` expression then identified the maintained parent
  indexes without changing files.
- ⚠️ TERMINAL ISSUE: the first explicit staging parser called `trim()` on
  porcelain output, removed the first line's leading status marker, and formed
  the nonexistent path `ython/...`; Git rejected the command and staged no
  files.

### Root causes and resolutions

- Symptom: supported slab overload raised `SlabContractError` and prevented a
  disposition. Root cause: the flexure functions treated a completed capacity
  miss as invalid intake. Resolution: introduce a shared typed failure carrier
  and propagate it before detailing/serviceability access. Evidence: both slab
  systems serialize demand, capacity, provenance, issue, and
  `VALID/COMPLETED/FAIL`; supported valid workflows remain green.
- Symptom: malformed CSV forces became zero or disappeared. Root cause: each
  force conversion caught `ValueError`, kept its initialized zero, and the
  outer row handler also swallowed `ValueError`. Resolution: one finite parser
  now raises with field/row context and only a missing mapped key is wrapped as
  malformed-row intake. Evidence: malformed/non-finite cells reject while
  valid, blank, SAFE, STAAD, and end-to-end adapter tests pass.
- Symptom: negative BOQ rates produced negative totals. Root cause: neither
  Pydantic request models nor the reusable Python aggregator constrained rates
  or concrete-grade keys. Resolution: finite positive request fields plus a
  direct public aggregator guard. Evidence: API cases return 422 and direct
  calls raise `ValueError`; all valid costing tests remain unchanged.
- Symptom: unrelated adapter loops appeared in the patch. Root cause: repeated
  method and loop text made a broad context patch non-unique. Resolution:
  inspect the diff immediately and reverse only the unintended SAFE/STAAD
  edits. Evidence: the final adapter diff contains only `GenericCSVAdapter`.
- Symptom: the first focused suite had five test failures. Root cause: the new
  parametrized test split the preceding fixture assertions, and one expected
  contract was intentionally obsolete. Resolution: restore valid-fixture
  assertions to their original test and change malformed-text expectations to
  explicit rejection. Evidence: all affected nodes and the complete 122-test
  selection pass.
- Symptom: static checks failed after runtime tests were green. Root cause:
  dictionary unpacking erased precise types and patched imports/lines were not
  normalized. Resolution: pass the six two-way shared values explicitly and
  apply deterministic Ruff/Black ordering. Evidence: targeted mypy, Ruff,
  Black, and `git diff --check` pass.
- Symptom: the standalone Markdown evidence worsened a pre-existing hard doc
  budget failure. Root cause: the exact base already contained 401 counted
  Markdown files and three older invalid `doc_type` values. Resolution: retain
  the full narrative in this required session record and store standalone
  machine evidence as JSON. Evidence: Packet C adds zero counted Markdown
  files; the inherited 401-file/front-matter debt remains visible for Packet D
  gate truth instead of being misreported as green.
- Symptom: explicit staging failed on one malformed path. Root cause: trimming
  the whole porcelain output altered only the first record before its fixed
  three-character status prefix was removed. Resolution: preserve the raw
  first-line whitespace and split before slicing each status prefix. Evidence:
  the failed command left the index and worktree unchanged; the corrected
  parser stages the complete 43-path candidate.
- Symptom: normal hooks rejected otherwise-green Packet C source. Root cause:
  two downstream public consumers encoded the old assumption that every valid
  slab intake reaches detailing, shear, and serviceability, which is no longer
  true for a completed flexural capacity failure. Resolution: Gravity Workflow
  treats absent downstream checks as component `FAIL`, and release UAT asserts
  its known-safe fixture reached detailing before checking review status.
  Evidence: 13 affected Gravity/UAT tests pass, the overloaded workflow result
  is `VALID/COMPLETED/FAIL`, and targeted mypy passes all three affected source
  modules.
- Symptom: valid but grossly unsafe beam designs could not return their
  expected HTTP 200 engineering `FAIL`. Root cause: a zero/invalid calculated
  capacity intentionally produced mathematical infinity, but beam evidence
  schema 3.0 inserted that value into strict JSON identity. Resolution: schema
  3.1 records `UNBOUNDED_FAILURE`, leaves `exact_utilization` and margin null,
  and forces `SUPPORTED/FAIL` even if a contradictory caller supplies
  `is_ok=True`. Evidence: the two hosted reproductions plus the evidence
  fail-closed regression pass; 14 affected tests and 20 API-contract tests are
  green with no OpenAPI breaking drift.

### Verification through content freeze

- 122 implementation-focused tests pass across slab, CSV, BOQ, and FastAPI.
- 214 independent neighboring slab, adapter, and costing tests pass; 20
  independent API surface/manifest tests pass.
- 13 affected downstream Gravity Workflow and release-UAT tests pass after the
  full-source typing repair.
- The first hosted run passed Python, documentation, and repository validation
  but failed FastAPI 2/473 and therefore failed `PR Gate`; the exact two failed
  nodes, evidence regressions, and 20 API-contract tests pass after repair.
- The schema snapshot authority reports five models and two enums unchanged;
  the canonical OpenAPI baseline contains the reviewed response-model update.
- Targeted mypy reports no issues in seven changed source modules; focused
  Ruff, Black, and `git diff --check` pass. The consolidated quick gate passes
  10/10; commit hooks, immutable commit, hosted checks, and exact-tree merge
  remain in the candidate sequence.

### Remaining holds

- `LIB-PRO-003-D` and cumulative broad acceptance remain open.
- No package publication, version bump, stable/professional-use claim,
  qualified-engineer approval, INDIA-3 work, ETABS, or desktop Excel work is
  authorized by this packet.

---

## 2026-08-22 — Session: LIB-PRO-003-B domains and footing provenance

**Agent:** Codex (`backend`, sole writer)

**Branch:** `codex/public-route-domain-provenance`, from hosted `main` at
`e7698a63b86d2db6db2f3970871122af1ce562f6` after exact-tree merge of
`LIB-PRO-003-A` PR #832.

**Git handoff receipt:**
`docs/verification/lib-pro-003-b-git-handoff-receipt.json`

**Focus:** Close reproduced beam material/shear-table domains, column
longitudinal-steel limits and stale result access, and isolated-footing
provenance origins without changing engineering formulas.

### Summary

- Replaced permissive beam material extrapolation, Table 19 percentage
  clamping, and supplied-shear-steel substitution with explicit public
  boundary rejection and stable structured errors.
- Enforced the maintained 0.8-4.0% column longitudinal-steel domain across
  axial, uniaxial, biaxial, and long-column safety routes.
- Repaired unified column orchestration to consume the typed uniaxial
  `is_safe` field instead of the removed `ok` key.
- Added runtime validation for service-load, allowable-soil-pressure, and
  effective-supporting-area provenance origins before calculation or replay
  hashing.
- Preserved all valid benchmark arithmetic and public result shapes; Packets
  C-D, release authority, INDIA-3, ETABS, and professional approval remain
  held.

### Issues encountered

- The first 656-test focused run had seven failures: one expected error-code
  mismatch, three high-shear paths still referenced a removed warning list,
  two property tests generated newly invalid column steel ratios, and the
  fck=50 service replay reached evidence serialization with infinite
  utilization instead of rejecting at the boundary.
- The first focused style check found one Black formatting change and two Ruff
  import-order changes.
- ⚠️ TERMINAL ISSUE: a guessed prior handoff filename omitted the repository's
  `-source-evidence` suffix; the tracked exact filename was then used.
- ⚠️ TERMINAL ISSUE: quiet pytest collection output contained no node lines for
  `rg` to count; verbose collection produced the exact 656 and 294 counts.

### Root causes and resolutions

- Symptom: direct M10/Fe700 and impossible shear percentages could still be
  accepted. Root cause: material validation checked only positivity and Table
  19 helpers clamped unsupported inputs. Resolution: add supported material
  errors, make out-of-range Table 19 concrete decisive, and reject percentages
  outside 0.15-3.0%. Evidence: the direct adversarial replay rejects service
  inputs and returns structured unsafe lower-level results.
- Symptom: supplied zero/negative shear steel was replaced by flexural steel.
  Root cause: the optional value entered the supplied branch only when greater
  than zero. Resolution: reject every supplied non-positive value before the
  fallback decision. Evidence: direct compliance and public single/multi-case
  regressions pass.
- Symptom: column steel outside 0.8-4.0% could return safe. Root cause: core
  routes appended warnings but did not change disposition. Resolution: one
  shared Clause 26.5.3.1 validator now rejects the invalid domain before
  capacity/safety calculation. Evidence: axial/uniaxial focused tests plus 294
  independent biaxial, long-column, P-M, golden-vector, and API tests pass.
- Symptom: a valid unified uniaxial branch raised `KeyError: 'ok'`. Root cause:
  orchestration retained the old dictionary key after the result became a
  typed dataclass with `is_safe`. Resolution: use the typed field for both
  axes. Evidence: the exact low-axial replay returns `uniaxial_x` normally.
- Symptom: unknown footing origins could return `PASS` and enter replay hashes.
  Root cause: `Literal` annotations had no runtime enforcement. Resolution:
  validate all three origin fields before calculation. Evidence: every unknown
  origin raises `ValidationError`; composed footing publication remains green.
- Symptom: fck=50 reached JSON evidence with an infinite failed utilization.
  Root cause: the service allowed the core shear failure to continue into a
  strict finite JSON identity. Resolution: reject outside-Table-19 concrete at
  the service boundary before calculation/evidence construction. Evidence: the
  failed node and the original public replay now pass with explicit rejection.

### Verification through content freeze

- 656 selected focused tests are green by consolidated-run plus affected-node
  replay; 294 independent benchmark/public-contract tests pass.
- The original adversarial examples now fail closed, while the stale-key valid
  branch returns normally.
- Focused Black and Ruff checks pass, targeted mypy reports no issues in the
  13 changed source modules, and `git diff --check` passes. The consolidated
  quick gate passes 10/10; normal commit hooks, immutable commit, hosted checks,
  and exact-tree merge remain in the candidate sequence.

### Remaining holds

- `LIB-PRO-003-C` and D remain open.
- No package publication, version bump, stable/professional-use claim,
  qualified-engineer approval, INDIA-3 work, ETABS, or desktop Excel work is
  authorized by this packet.

---

## 2026-08-22 — Session: LIB-PRO-003-A public numeric boundaries

**Agent:** Codex (`backend`, sole writer)

**Branch:** `codex/public-route-numeric-boundaries`, from hosted `main` at
`e40c0b564acae82f6696e204e8b382342fbf4321`.

**Git handoff receipt:**
`docs/verification/lib-pro-003-a-git-handoff-receipt.json`

**Focus:** Close reproduced non-finite public calculation outcomes, empty
compliance success, and the rounded uniaxial-column safety decision without
changing engineering formulas or supported domains.

### Summary

- Introduced one shared finite-real structured validation boundary and applied
  it before arithmetic in lower-level beam flexure, beam shear, compliance,
  direct uniaxial-column, and unified column routes.
- Changed an empty compliance report from vacuous success to explicit input
  rejection.
- Changed uniaxial-column safety to compare exact utilization while retaining
  the rounded public display field.
- Added direct regressions for all affected numeric arguments, the exact
  `-infinity` column and `1.0000` display-boundary reproductions, empty public
  compliance, numeric-text NaN, booleans, and compatibility exports.
- Froze the remaining public-route safety work as `LIB-PRO-003` Packets B-D;
  INDIA-3 and the next package remain held behind that sequence.
- Verification: 260 unique implementation-focused tests and 138 independent
  verification/API tests pass; focused Ruff and `git diff --check` pass; the
  consolidated quick gate passes 10/10.

### Issues encountered

- The first focused run had six failures because the new canonical validation
  helper was not exposed through the backward-compatible
  `structural_lib.validation` module.
- A focused Ruff check found one extra blank line in the compliance-validation
  test import block.
- ⚠️ TERMINAL ISSUE: unquoted forbidden-path globs expanded during the first
  handoff-receipt command and were rejected as extra arguments; quoting the
  literal patterns produced the receipt successfully and no failed-command
  write occurred.
- The first normal commit-hook pass stopped after Black reformatted the changed
  uniaxial module and two focused test files.

### Root causes and resolutions

- Symptom: `AttributeError` occurred only through the compatibility facade.
  Root cause: that facade uses an explicit import list, so adding the helper to
  canonical `core.validation.__all__` did not update the old module. Resolution:
  add both finite-real helpers to the explicit facade import list. Evidence:
  the complete 86-test validation file passes.
- Symptom: focused Ruff reported `I001`. Root cause: the patched import block
  contained one surplus blank line. Resolution: remove that line. Evidence:
  focused Ruff and `git diff --check` pass.
- Symptom: the first receipt command rejected many expanded file arguments.
  Root cause: zsh expanded unquoted `**` patterns before the script received
  them. Resolution: quote each forbidden pattern. Evidence: receipt creation
  and session handoff both completed successfully.
- Symptom: the candidate commit was not created on the first hook pass. Root
  cause: three changed Python files were Ruff-clean but not Black-normalized.
  Resolution: retain Black's mechanical output, refresh only its affected
  maintained indexes, and restage the candidate. Evidence: Black identified
  and reformatted exactly those three files; all other normal hooks passed on
  that pass, including repository-wide mypy over 243 source files.

### Remaining holds

- `LIB-PRO-003-B` through D remain open.
- No package publication, version bump, stable/professional-use claim,
  qualified-engineer approval, INDIA-3 work, ETABS, or desktop Excel work is
  authorized by this packet.

---

## 2026-08-22 — Session: E1 G3 integration and roadmap closeout

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/e1-g3-closeout`, from integrated E1 `main` at
`b720119ea6a22a2b1963be0a0b9b300fca333d4a`.

**Git handoff receipt:**
`docs/verification/e1-g3-closeout-git-handoff-receipt.json`

**Focus:** Close accepted E1, reconcile release/task truth, and select the next bounded library decision packet without ETABS or new engineering implementation.

### Summary

- Consolidated the complete E1 stack into PR #830, proved the accepted
  candidate and merged trees identical, passed cumulative local and hosted
  validation, and merged the exact product tree as `b720119e`.
- Preserved the superseded E1 branches, worktrees, artifacts, and evidence while
  closing draft PRs #826-#829 with pointers to the cumulative integration.
- Recorded the installed-desktop-Excel `G3_PASS`, deterministic export hashes,
  freshness/reopen results, and `DAY_CLOSE_CLEAN` receipt in the canonical E1
  evidence and handoff.
- Reconciled live release truth: `v0.23.1a2` was already published on
  2026-08-17 from tag target `09861d3d`; later Gravity and E1 merges require a
  new version and must never be republished as the same Alpha.
- Selected `INDIA-3-G0`, a read-only IS 13920 beam/column/joint truth,
  benchmark, and contract audit, as the correct next bounded library packet.

### Issues encountered

- GitHub did not start PR Validation when cumulative PR #830 was retargeted to
  `main` and marked ready, so the exact cumulative head initially had no hosted
  rollup.
- The task board and pre-release documents still described `v0.23.1a2` as an
  unpublished local candidate although GitHub and PyPI already exposed it.
- The retained Alpha release lane predates the current Git-state authority and
  therefore could not run `scripts/git_state.py` for orientation.
- The session handoff command reported success but did not replace the existing
  block while its heading used lowercase `handoff`.
- ⚠️ TERMINAL ISSUE: a guessed `scripts/check_tasks.py` command did not
  exist → the maintained `scripts/check_tasks_format.py` entry from the script
  registry was used and passed.

### Root causes and resolutions

- Confirmed hosted-trigger cause: the PR workflow listens to opened,
  synchronize, and reopened events, not ready-for-review or base-edited events.
  Resolution: close and reopen unchanged PR #830 once; run `32560422307` passed
  every applicable job on the exact reviewed head before merge.
- Confirmed release-record cause: the 2026-08-17 publication completed without
  the planning/task documents being reconciled afterward. Resolution: verify
  the live tag and exact PyPI artifacts, correct the append-only release receipt,
  task board, checklist, and changelog, and explicitly prohibit same-version
  republication.
- Confirmed stale-lane cause: the historical release branch is an evidence lane
  from before `git_state.py` existed and is far behind current `main`.
  Resolution: use bounded read-only Git fallback for that lane, preserve it,
  and take no reset, rebase, deletion, or release action.
- Confirmed command-selection cause: task validation is exposed as
  `check_tasks_format.py` and through the unified gate, not `check_tasks.py`.
  Resolution: use the maintained script registry and record the terminal issue
  so it is not repeated.
- Confirmed handoff-update cause: the session updater's replacement expression
  requires the exact `Latest Handoff` heading even though the marker block was
  otherwise valid; its success path did not detect zero substitutions.
  Resolution: restore the canonical heading, rerun the maintained updater, and
  verify that the receipt hash appears in the generated block.

### Validation through content freeze

- E1 cumulative local acceptance: 6,508 Python tests passed, 3 skipped,
  6 deselected; full repository gate passed 31/31.
- Hosted PR Validation run `32560422307`: every applicable job passed; React was
  correctly skipped by the path classifier.
- Integration proof: PR #830 merged as `b720119e`; merged tree
  `bcc7fcf1b22212950ae530ca87c8bab907b6391f` equals the accepted candidate
  tree exactly.
- Closeout documentation strict validation and 1,350-link check pass. The final
  quick gate, normal commit hooks, immutable commit, hosted documentation PR,
  and read-only session audit remain in the consolidated closeout sequence.

## 2026-08-22 — Session: E1 desktop-Excel workbook-open repair

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/e1-workbook-open-repair`, stacked on immutable export
candidate `98c60bc1f7c3899c28f662e82399cb25d80bbf26`.

**Git handoff receipt:**
`docs/verification/e1-workbook-open-repair-git-handoff-receipt.json`

**Focus:** Diagnose Excel's content-recovery prompt on an evidence-only copy,
repair the confirmed workbook-package defect from maintained source, and return
one deterministic candidate for the frozen G3 journey without starting ETABS.

### Summary

- Accepted recovery only on a uniquely named diagnostic copy and preserved the
  original, repaired evidence copy, Excel repair log, hashes, package delta,
  visible outcome, and clean Windows shutdown receipt.
- Added a maintained spreadsheet-artifact generator for all six sheets and five
  named tables; the generated workbook contains no macros or structural
  formulas.
- Replaced the case-colliding effective-depth table header with
  `Effective d (mm)`, retained the old service alias, refreshed the manifest,
  and added source/wheel package regressions.
- Normalized volatile relationship identifiers and ZIP timestamps so two clean
  generator runs produce byte-identical workbooks.

### Issues encountered

- Excel displayed “We found a problem with some content” before the exact
  product workbook opened, blocking mapping, calculation, freshness, reopen,
  and supported export. The prompt alone did not identify the rejected part.
- The workbook was tracked only as binary package data; no maintained generator
  for reproducing a corrected artifact was present.
- The first two artifact-tool exports had equivalent worksheet content but
  different bytes, so manifest identity could not be reproduced reliably.
- Windows `Ctrl+Shift+S` did not open Save As for the recovered evidence copy;
  `F12` opened the dialog and permitted preservation under the frozen diagnosis
  contract.
- ⚠️ TERMINAL ISSUE: an orientation `shasum excel_addin/*.xlsx` command failed
  because zsh rejected the unmatched glob → the exact package-data workbook
  path was used instead; this was a shell-selection issue, not workbook damage.

### Root causes and resolutions

- Confirmed file root cause: `tbl_Beam_Workbench_V1` declared `D (mm)` and
  `d (mm)`, which collide under Excel's case-insensitive table-column naming.
  Excel's repair log named `/xl/tables/table1.xml`, and the recovered evidence
  changed only the latter logical header to `d (mm)2`. Resolution: generate the
  supported artifact with `Effective d (mm)` and reject case-insensitive
  duplicate table names in source and installed-wheel probes.
- Confirmed process root cause: the original gate verified ZIP/XML structure,
  tables, formulas/macros, hashes, and rendered appearance, but did not require
  an immutable desktop-Excel open. Resolution: make the no-recovery real-Excel
  open a required D3 gate before the remaining frozen journey.
- Confirmed reproducibility gap: the binary artifact had no maintained creation
  path. Resolution: add `scripts/generate_e1_workbook.mjs` using the approved
  spreadsheet artifact workflow and preserve the exact six-sheet contract.
- Confirmed byte-instability cause: artifact-tool emitted random relationship
  identifiers and current ZIP timestamps. Resolution: normalize relationship
  IDs consistently across targets/references and set fixed ZIP member dates;
  two clean executions then matched byte for byte.
- Confirmed shortcut issue: the diagnostic Excel session did not respond to
  `Ctrl+Shift+S`; using Excel's `F12` Save As path preserved the recovered copy
  without changing the production artifact. The host was returned with Excel
  and ETABS closed, services stopped, ports free, and retained worktrees clean.
- Confirmed terminal issue: the unmatched zsh glob had no target files in the
  add-in directory. Resolution: select the exact installed package-data path;
  its original SHA-256 matched the frozen receipt.

### Validation through content freeze

- Generator determinism: PASS — two clean runs produced the same 15,101-byte
  workbook, SHA-256 `4cc492bfcbba456342c6358a8dcfe2749cafd723e9ee4fdaefa585f29e35ce63`.
- Final six-sheet render/inspection is readable and formula/error-free; focused
  workbook/service/REST evidence passes 22/22 cases.
- Affected Black/Ruff pass after formatting only the failed verifier slice.
  The source-free wheel SHA-256 is `0943e277…ba43`; its isolated install reports
  library content `eafb869a…8ebf`, the exact repaired workbook identity, one
  canonical `PASS` row, and deterministic complete review-bundle bytes.
- Documentation/index validation, quick gate, hooks, immutable commit, and
  read-only session audit remain pending in the consolidated closeout sequence.

## 2026-08-22 — Session: E1 complete review-bundle export

**Agent:** Codex (`reviewer`, sole writer)

**Branch:** `codex/e1-review-bundle-export`, stacked on exact Windows-validated
predecessor `514155b266af6dff3e30bf39ee28671c17345454`.

**Git handoff receipt:** `docs/verification/e1-review-bundle-export-git-handoff-receipt.json`

**Focus:** Close the G3 export-surface gap with one complete, deterministic,
fail-closed Python/REST/Office.js successor; preserve workbook bytes,
calculations, manifest, ETABS/VBA, release, merge, cleanup, and professional
approval boundaries.

### Summary

- Added a versioned complete review-bundle request/result contract and
  deterministic JSON serialization.
- Added a same-origin REST attachment whose file, logical bundle, and canonical
  result identities are explicit.
- Added an installed-pane Export control that is eligible only after a current
  run or explicit freshness check and verifies response bytes before download.
- Extended focused Python, REST, Office.js, source-free wheel, plan, evidence,
  and Windows acceptance surfaces.

### Issues encountered

- The frozen G3 journey required pane-accessible deterministic review-bundle
  export, but the installed pane and REST router exposed no export operation.
- The existing deterministic Markdown renderer was a compact status summary;
  it omitted the complete mapping, structured results, passports, raw ledger
  detail, and issues required for qualified review.
- The first OpenAPI assertion found the new route documented no response
  content even though its runtime JSON attachment passed.
- The first affected-file Ruff run stopped before mypy because two new service
  contract imports were not in canonical order.

### Root causes and resolutions

- Confirmed root cause: local renderer determinism had been accepted as proof
  of a complete installed Excel export journey even though no source-to-pane
  route existed. Resolution: add one typed export request, service regeneration
  boundary, raw JSON attachment route, pane action, and exact identity checks.
- Confirmed root cause: the old renderer was designed as a human-readable
  summary and its tests asserted repeatability plus hash presence, not complete
  artifact content. Resolution: make `ExcelReviewBundleV1` contain the full
  canonical run result, preserve the renderer as a summary-only compatibility
  surface, and add nested-content plus deterministic-byte tests.
- Confirmed root cause: setting generic `Response` as the decorator response
  class suppressed FastAPI's schema content even with a response model.
  Resolution: keep `ExcelReviewBundleV1` as the documented response model and
  return a raw `Response` instance only at runtime. Proof: the failed OpenAPI
  assertion and refreshed 89-endpoint/434-schema baseline check pass.
- Confirmed root cause: the new retained/export contract imports were added in
  semantic rather than Ruff alphabetical order. Resolution: reorder only those
  imports; affected Black/Ruff and the previously skipped configured mypy pass.

### Validation through content freeze

- Focused Python/REST/Open XML: 22 cases pass using one impact-mapped repair
  rerun; Office.js: 21/21; four JavaScript modules and the manifest parse.
- Black, Ruff, configured mypy, 217-file architecture, 685-file/4,732-import
  validation, and the 89-endpoint/434-schema OpenAPI baseline pass.
- A source-free wheel proves unchanged workbook SHA-256 `497dd44d…ac85`, new
  library content identity `87ae4fbe…d57a5`, and complete deterministic 8,987-
  byte review evidence with both structured result and passport.
- Documentation, maintained indexes, quick gate, hooks, immutable commit/audit,
  hosted checks, and Windows G3 remain in the closeout sequence.

## 2026-08-22 — Session: E1 blank-workbook guard repair

**Agent:** Codex (`backend`, sole writer)

**Branch:** `codex/e1-blank-workbook-guard`, stacked on
`codex/e1-w0-maintenance-plan` at
`654e40b1370d098fca4d001146a030b9937536a8`.

**Git handoff receipt:** `docs/verification/e1-blank-workbook-guard-repair-git-handoff-receipt.json`

**Focus:** Diagnose the exact Windows blank-workbook pane failure, repair only
the Office.js startup boundary, freeze local evidence, and leave G3 and all
ETABS/VBA work held.

### Summary

- Recovered the long Windows W0 task, completed the restricted SMB/trusted-
  catalog setup, and loaded the exact E1 add-in from `SHARED FOLDER`.
- Moved the new source diagnosis into a fresh, read-only Windows task and bound
  it to E1 head `ef5ee05c` and tree `30d8eb79`.
- Added a guarded, testable Office.js workbook-surface boundary that leaves
  blank/wrong workbooks read-only and keeps controls disabled.
- Preserved strict complete-workbook initialization and genuine Office/API
  failure reporting; no calculation, workbook, manifest, Python, ETABS/VBA, or
  G3 behavior changed.

### PRs Merged

- None.

### Key Deliverables

- `excel_addin/taskpane-office.mjs`
- `excel_addin/tests/taskpane-office.test.mjs`
- `docs/verification/e1-blank-workbook-guard-evidence.md`
- Updated W0/E1 evidence, task state, and next-session handoff.

### Issues encountered

- The exact trusted add-in loaded in a new blank workbook but stopped with
  `WORKBOOK CONTRACT ERROR — The requested resource doesn't exist` before its
  definition API request. This blocks W0 and therefore G3.
- The first remote task initially described the failure at the broad document-
  settings initialization stage because W0 did not capture `error.code`,
  `debugInfo`, or a JavaScript stack. Treating that visible message as the root
  cause would have repaired the wrong boundary.
- The first immutable repair head reached Windows with a new local module
  import but no matching `serve.mjs` route. `/taskpane-office.mjs` returned 404,
  leaving the pane at `INITIALIZING` and preventing the definition request.
- Closing the blank workbook produced a save prompt even though the missing
  module meant the repaired JavaScript never executed. Save-prompt presence is
  therefore not a reliable proxy for document-settings writes.

### Root causes and resolutions

- Confirmed root cause: startup saved/read the workbook ID, then
  `registerInputChange()` called `worksheets.getItem("Beam_Workbench")` in a
  blank workbook containing only `Sheet1`. The following `context.sync()`
  raised Office `ItemNotFound`; this documented error message and the source
  order match the observed pre-API failure. Resolution: inspect both the sheet
  and table with `getItemOrNullObject()` before any settings write/event
  registration, return the controlled `E1 WORKBOOK NOT OPEN` state when absent,
  and retain strict failures after the complete surface exists. Proof: 15/15
  Office.js tests, four JavaScript parse checks, manifest XML validation, and
  217-file architecture validation pass.
- Confirmed root cause of the initial broad attribution: the UI catch grouped
  settings, event registration, and API startup under one generic `WORKBOOK
  CONTRACT ERROR`, while the W0 receipt lacked runtime error metadata.
  Resolution: the read-only Windows source trace followed execution order and
  compared the blank workbook contents with Microsoft Office.js semantics;
  production now reports workbook check, local API, and strict workbook
  initialization failures separately and preserves Office code/debug location.
- Confirmed root cause of the Windows repair-load failure: `serve.mjs` uses an
  explicit static-file map, and the initial repair added a module import without
  adding its route. Resolution: serve `/taskpane-office.mjs` from the trusted
  origin and add a focused test that compares local `taskpane.mjs` imports with
  the server map. The original W2 receipt proves the 404 and clean shutdown;
  the consolidated local Office suite provides the repaired route evidence.
- Confirmed root cause of the misleading save-prompt criterion: inserting an
  Office add-in can itself dirty an unsaved workbook independently of document
  settings. Resolution: discard the W0 workbook and rely on exact code/test
  evidence plus the controlled visible state; record, but do not interpret, any
  close prompt.

### Notes

- The repair base and original E1 candidate remain clean and immutable.
- Windows revalidation must use the exact repair commit and reuse passing setup
  evidence; no broad rebuild or G3 work is authorized by this local result.


## 2026-08-21 — Session: E1 Windows W0 evidence and maintenance

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/e1-w0-maintenance-plan`, stacked on the immutable E1 head
`ef5ee05c785904e1a01c2d09cc65649edc8745ab`.

**Git handoff receipt:** `docs/verification/e1-w0-maintenance-git-handoff-receipt.json`

**Focus:** Record the completed Windows setup and legacy VBA/API handoff,
reconcile current library progress, run a non-destructive maintenance pass,
and freeze the next controlled work sequence.

### Summary

- Recorded W0 as `SETUP_BLOCKED`, with all entitlement, candidate, wheel,
  artifact, HTTPS, and loopback checks passing and one restricted SMB catalog
  share remaining before the blank-workbook add-in check.
- Preserved the 2019-2021 ETABS/VBA, exporter, structural-design, and legacy
  workbook bundles as historical reference evidence with hashes and explicit
  no-live-model/no-macro-execution boundaries.
- Verified live GitHub progress: PRs #822, #823, and #825 are merged; draft PR
  #826 is clean at the exact E1 head and all required hosted checks pass.
- Ran health, audit, parity, efficiency, feedback, source-binding, and local
  branch-disposition checks. Corrected four confirmed endpoint/router count
  drifts and preserved all uncertain lanes.

### PRs Merged
| PR | Summary |
|----|---------|
| None | This session did not merge or close a pull request. |

### Key Deliverables

- `docs/verification/e1-windows-w0-setup-evidence.md`
- Updated E1 evidence, task board, next-session brief, and four onboarding/API
  counts.
- Non-destructive cleanup result: 25 local non-default branches classify
  `HOLD_UNKNOWN_OWNER` without refreshed per-branch ownership, PR, remote-ref,
  and retention evidence; no branch, worktree, file, or stash was removed.

### Issues encountered

- The Mac controller lost readable access to the remote Windows Codex task,
  even though the task continued and completed on Windows.
- Documentation health found four stale endpoint/router counts after the recent
  API additions.
- Cleanup classification found 25 local branches without enough refreshed
  authority for safe retirement; one separate detached worktree is also dirty
  and remains preserved.
- The all-folder index audit found six stale aggregate indexes. Three were
  inherited from E1 (`Python/structural_lib`, `Python/tests`, and `fastapi_app`)
  and three reflected this session's documentation changes.
- The first normal commit hook rejected the rewritten next-session brief because
  its `Required Reading` heading used lowercase `reading`; the failed-only
  session check then exposed missing exact `Current` and `Next` table labels.
- The first clean exact-head session audit could not discover the valid handoff
  receipt because its path was wrapped onto the following line.

### Root causes and resolutions

- Remote disconnect root cause is `unconfirmed`. Completed Windows commands,
  clean Git, stopped services, and the final receipt localize the symptom to the
  Codex remote-control/task-visibility path rather than the build or candidate.
  The passing work is retained and will not be rerun; only the remaining catalog
  and blank-workbook checks will resume after the user action.
- E1 and preceding API work raised the maintained surface to 88 endpoints and
  26 routers, but four descriptive counts remained at 81/24. The four exact
  values were updated; direct `sync_numbers.py` and documentation checks provide
  the correction evidence.
- Branch age or apparent merge history is not retirement authority. Without
  current owner, PR, remote-ref, and retention receipts, the classifier correctly
  fails closed. All 25 branches and every existing worktree remain untouched;
  any destructive cleanup requires a separately reviewed proposal and explicit
  user authorization.
- E1 refreshed its directly changed nested indexes but did not refresh three
  maintained parent aggregate indexes whose hashes include those descendants.
  This session also changed three indexed documentation folders. Resolution:
  refresh exactly the six reported stale folders plus `docs/verification` for
  its newly added evidence; the final all-folder read-only check must report
  32/32 current.
- The session checker intentionally treats the exact `Required Reading` heading
  and `Current`/`Next` table labels as a machine-readable handoff contract.
  Resolution: restore those canonical tokens without losing the clearer W0/G3
  content, refresh only the affected docs/planning and docs indexes, and rerun
  the failed check before the normal commit hooks; all other first-pass hooks
  had passed.
- The session-end receipt parser requires the label and tracked path on the same
  line. Resolution: bind the existing valid receipt on that line and create a
  minimal repair commit after refreshing only the root docs index; no product,
  Windows, G3, or ETABS evidence was repeated.

### Notes

- Health initially reported 94/100 only because of the four stale numbers;
  code, agents, infrastructure, and feedback were 100/100.
- Audit was 21/22 with one non-blocking function-quality diagnostic warning;
  parity showed 88/88 endpoint tests and 13/13 React hook connections.
- ETABS snapshot/live work, Excel G3, repository publication, release, and
  professional approval were not run.


## 2026-08-18 — Session: E1 Excel Routine Workbench V1 implementation

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/e1-excel-routine-workbench`.

**Git handoff receipt:** `docs/verification/e1-excel-routine-workbench-git-handoff-receipt.json`
**Focus:** Implement the frozen E1 selected-table rectangular-beam workflow,
including strict intake and row reconciliation, canonical Python/CLI/REST
results, calculation passports and freshness, one macro-free workbook, a
bounded Office.js task pane, installed-wheel artifact identity, documentation,
and evidence. ETABS file/live work, write-back, optimization, nightly work,
release, and professional approval remain excluded.

### Summary

- Implemented the strict selected-table Python/CLI/REST workflow, canonical row
  ledger, calculation passports, four-hash freshness, and explicit capability
  truth without adding a second structural calculation path.
- Packaged and verified one macro-free six-sheet workbook plus a bounded
  Office.js task pane; focused tests, source-free wheel proof, documentation,
  quick gates, and normal commit hooks pass.
- Retained `TO_VERIFY_WINDOWS` for the separate installed Windows Excel G3 cell
  and held ETABS, write-back, optimization, release, and approval work.

### Issues encountered

- The previous session's time-bounded Git handoff evidence had expired before
  implementation resumed.
- The first header mapper case-folded structural notation `D` and `d`, so seven
  of ten new service vectors were blocked as duplicate mappings.
- Two first-pass REST cases asked pytest for an `unwrap` fixture although the
  maintained helper is an ordinary function.
- The artifact patch helper created its temporary builder under the primary
  checkout instead of the visualization workspace, and the E1 safe-move script
  could not move a file whose source was outside the current worktree.
- The first workbook's placeholder row populated both categorical dropdown
  cells, so it was not a blank row and would have become `BLOCKED` instead of
  explicitly `EXCLUDED`. Its first render also expanded the input sheet to 204
  rows and cramped the information-sheet workflow text.
- The first workbook location was a repository output outside Python package
  data, so a built wheel could not prove or expose the exact artifact.
- Retaining the complete result bundle in Office document settings would scale
  poorly for a large selected table even though full evidence already persists
  in workbook tables.
- The first frozen architecture/import commands used guessed script names, and
  root-level mypy saw the same module through both `Python.structural_lib` and
  `structural_lib` package identities. The corrected mypy run then exposed
  literal, inherited-schema, and untyped-constructor weaknesses.
- The root `Excel/` ignore rule also matched the lower-case installed package
  data directory on the default macOS filesystem, hiding the workbook and its
  manifest from an ordinary Git add.
- The first strict documentation closeout rejected descriptive E1 front-matter
  values even though all E1 links and the repository quick gate passed.
- The first normal commit hook run rejected the new session order and the new
  wheel verifier's missing automation-map registration.
- The first immutable read-only session audit could not find completion items
  or the Git handoff receipt in the newest E1 entry.

### Root causes and resolutions

- Confirmed root cause: the start receipt intentionally expires and cannot be
  reused as current authorization. Resolution: bind fresh user continuation to
  exact branch head `64f3518a`, regenerate the handoff receipt, and validate it
  before writes. Evidence: the receipt validator returned valid `HOLD` with the
  E1 task authority and unchanged base.
- Confirmed root cause: case folding erased the semantically significant
  uppercase/lowercase depth distinction. Resolution: preserve exact `D_mm` and
  `d_mm` aliases before folded aliases. Evidence: all 13 consolidated Python
  E1/workbook cases pass, including PASS/FAIL/HOLD/blocked and mapping vectors.
- Confirmed root cause: the new REST file copied a fixture-style call pattern
  for a helper exported from `fastapi_app.tests.conftest`. Resolution: import
  and call the helper directly. Evidence: all three consolidated REST cases
  pass.
- Confirmed root cause: `apply_patch` is rooted at the desktop session workspace,
  not the per-command shell workdir, and `safe_file_move.py` intentionally
  rejects cross-worktree sources. Resolution: run the generated builder only
  from the exact temporary primary path, verify the output, safely delete the
  one untracked builder, validate and unlink only its known dependency symlink,
  and recheck the primary checkout. It is clean. ⚠️ TERMINAL ISSUE: patch
  workdir assumption placed one temporary file in the primary checkout -> used
  exact-path cleanup and prefixed all later E1 patches with the linked-worktree
  path.
- Confirmed root cause: preset dropdown values are data, and formatting/data
  validation across 200 unused rows expanded the workbook used range.
  Resolution: leave the placeholder's 17 cells null, retain validation only on
  the compact three-row table, widen/wrap the workflow panel, and visually
  inspect all six final renders. Open XML checks prove the exact sheets/tables,
  no formulas, no formula errors, and no VBA/macros.
- Confirmed root cause: root `outputs/` is not inside the setuptools package
  tree. Resolution: move, do not copy, the single workbook and manifest into
  maintained package data and make the definition service verify installed
  bytes, size, and SHA-256. The repaired source-free wheel contains the exact
  workbook and reports canonical PASS for one installed-package row.
- Confirmed root cause: complete row ledgers and result JSON grow with table
  size, while freshness needs only bundle, source-table, mapping, and engine
  identities. Resolution: persist those four hashes plus the stale flag and
  workbook ID in Office settings; keep full ledgers, results, and passports in
  their named worksheets. The focused Python, REST, and seven Office.js tests
  pass.
- Confirmed root cause: the maintained commands are
  `check_architecture_boundaries.py` and `validate_imports.py`, and configured
  mypy requires the `Python/` package workdir. Resolution: correct the frozen
  evidence commands, then fix the real type roots with literal-final constants,
  a standalone run-request schema, and a direct typed result constructor.
  Evidence: 217 architecture files have zero violations, 685 Python files have
  zero broken imports, and mypy reports no issues in both new modules.
  ⚠️ TERMINAL ISSUE: guessed architecture/import script paths and root-level
  mypy failed -> discovered the registered commands and ran mypy from `Python/`.
- Confirmed root cause: Git's case-insensitive path matching on the current
  filesystem applied the broad `Excel/` output ignore to the new lower-case
  package-data path. Resolution: force-stage only the exact verified workbook
  and manifest; once tracked, later changes remain visible normally. Evidence:
  `git ls-files --stage` lists both exact package-data paths and their SHA-256
  values remain bound by the workbook manifest and artifact verifier.
- Confirmed root cause: the three new E1 documents used human-readable workflow
  states where the maintained checker accepts only its controlled `status` and
  `doc_type` vocabularies. Resolution: retain the exact software-candidate/G3
  hold in document content while using `status: active` and the supported
  `spec`/`log` document types. The failed-only strict documentation rerun and
  impact-mapped quick gate are the repair evidence.
- Confirmed root cause: the implementation session was appended after older
  entries even though the maintained checker requires newest-first ordering,
  and adding a maintained script requires both its generated index and the
  hand-maintained automation map. Resolution: move only the new E1 session to
  the top and register the verifier as a read-only Testing task with exact-wheel
  usage. The two failed hook checks and impact-mapped quick gate are the repair
  evidence; no calculation suite is repeated.
- Confirmed root cause: the audit parser recognizes completed work only below
  `### Summary` or `**Completed:**` and discovers a receipt only from the exact
  bold label in the same newest session block. Resolution: add those two
  machine-readable boundaries without changing any implementation or evidence
  claim. The failed-only session check and exact-head read-only audit are the
  repair proof.

### Validation through content freeze

- Focused Python workbook/service/CLI/Open XML: 13 passed; focused REST: 3
  passed; Office.js: 7 passed plus syntax and XML parsing; advertised-command
  UAT: passed.
- Architecture: 217 files, zero violations. Imports: 685 files and 4,729
  imports, zero broken. OpenAPI: 88 endpoints and 432 schemas match baseline.
  Black and Ruff pass on every changed Python path; configured mypy passes both
  new source modules.
- Repaired source-free wheel SHA-256:
  `c4c5d09872d080ac5b1bee9e72c5af87e52df65c893358a15cc478cc4b5753b9`;
  installed library content identity:
  `6b2d8f43c4fecd8eaa0c3ec692db13db4118ac04fe141458307e114421ab1764`;
  workbook SHA-256:
  `497dd44d8dbe30ca8a6f3154b17d1d3598c517d96ffe0923e3ca44778450ac85`.
- Documentation/index, quick gate, normal hooks, immutable session audit, push,
  and hosted validation remain the closeout sequence. The supported real
  Windows Excel journey remains `TO_VERIFY_WINDOWS`, so Gate G3 is held.

## 2026-08-17 — Session: v0.23.1a2 Release Candidate Preparation

**Agent:** Codex (`ops`, sole writer)

**Branch:** `codex/release-0231a2` from synchronized
`main = 970a78c1931a3aa0439f487e6892a888bb113962`

**Local evidence:** `docs/verification/alpha-0231a2-local-prepublication-rehearsal.md`

**Git handoff receipt:** `docs/verification/release-0231a2-preparation-git-handoff-receipt.json`

**Focus:** Prepare and locally verify the exact v0.23.1a2 Alpha candidate with
one source-bound wheel, while keeping TestPyPI, PyPI, tag, GitHub Release,
whole-building, professional-approval, and retained-lane actions explicitly
unauthorized.

### Summary

- A fresh linked worktree was created from live GitHub `main`; it reported
  `READY_LOCAL`, `source_bound=true`, and no open PR overlap. All retained
  detached, dirty, and historical lanes were preserved unchanged.
- The canonical release preparation changed source/package/documentation
  version surfaces from `0.23.1a1` to `0.23.1a2`, retained the published
  `v0.23.1a1` evidence, and added bounded candidate release notes.
- The preparation gate passed 6,414 Python tests with 3 skipped and 6
  deselected, then passed the repository-pinned Node 24 React production build.
- Repaired build anchor `a115b16efbb85db0459c79836f55b6c43a586470`
  produced one wheel and matching sdist. The wheel is 665,658 bytes with
  SHA-256 `34892d867845d044249236f32b700ab5e10ec558225407a47717fe3c3c2614bb`.
- The clean installed-wheel verifier passed 5,553 tests with 51 skipped and 2
  deselected plus installed `job`, `critical`, and HTML `report` workflows.
- The narrow exact candidate check passed the 29-case matrix, all 12 advertised
  commands, public examples, content/version boundaries, and clean installed
  package-origin assertion against the same wheel hash.
- Candidate wording is historical and explicit: at freeze it is not tagged or
  published. The current public Alpha remains `0.23.1a1`; publication and
  professional approval remain separate holds.

### Issues encountered

- The release-preflight skill instructed maintainers to record a checked
  publication authorization in the checklist before immutable review.
- The general installed-wheel verifier passed its broad package suite and
  legacy CLI workflows but did not execute the newer 29-case advertised-command
  release matrix.
- Version synchronization printed optional-pattern warnings for source files
  that deliberately do not contain those optional tag/metadata forms.
- The first direct index-generator command guessed the retired
  `scripts/generate_folder_indexes.py` path and stopped before any write.
- Exact-head Weekly Verification run `32006071604` passed the clean-wheel,
  Python, FastAPI, benchmark, Docker, and dependency stages, then stopped in
  documentation drift because `fastapi_app/index.json` was stale; React was
  skipped after that failure.
- The first repair closeout invocation passed two folder arguments to the
  single-folder index command; argument parsing stopped before either write.
- The first authorized exact-wheel publication preflight passed clean-wheel
  UAT, 6,413 Python tests, FastAPI, React, docs, and version checks, but one
  release test failed because it read the live authorization record after the
  owner correctly changed that record from `HOLD` to `AUTHORIZED`.
- A read-only generated-artifact inspection loop used the zsh variable name
  `path`, after which standard commands in that loop were reported as missing;
  the failed inspection made no writes.

### Root causes and resolutions

- Confirmed root cause: the skill retained the earlier checklist-marker
  authorization sequence after publication authority moved to the exact JSON
  authorization plus immutable review-receipt flow. Resolution: candidate
  preparation now requires unpublished/on-hold wording and forbids pre-checking
  tag/publication approval; post-review authorization is routed only through
  validator-permitted exact evidence. Proof: focused release-document checks,
  14 release environment/version regressions, and normal commit hooks pass
  while the v0.23.1a2 publication checkbox remains open.
- Confirmed root cause: `release verify` and `release candidate-check` have
  distinct maintained responsibilities; only the latter invokes packaged
  `structural_lib.release_uat`. Resolution: run the broad verifier once, then
  the narrow candidate check once without replaying manual CLI cases. Proof:
  both commands exit zero against wheel SHA-256 `34892d86...14bb`; the packaged
  matrix contains 29 cases and the advertised inventory contains 12 commands.
- Confirmed root cause: the version synchronizer reports absent optional regex
  forms even when all required candidate surfaces agree. Resolution: inspect
  the intended surfaces once and rely on `--check-docs`, release-doc checks,
  exact candidate validation, and commit hooks; no non-outcome tooling change
  was added. Proof: every maintained check exits zero and the warnings identify
  only non-applicable optional forms.
- Confirmed root cause: the direct script name was guessed instead of using the
  maintained `run.sh generate indexes <folder>` entry point documented by the
  live launcher. Resolution: discover the current command with `rg --files`
  and use only targeted dry-run/final refresh calls. Proof: the guessed command
  made no write; final affected-folder index checks pass. ⚠️ TERMINAL ISSUE:
  nonexistent direct generator path -> maintained targeted `run.sh` command.
- Confirmed root cause: release preparation changed `fastapi_app/__init__.py`,
  `fastapi_app/config.py`, and `fastapi_app/openapi_baseline.json`, but the
  affected-folder index refresh omitted `fastapi_app`. Resolution: regenerate
  only `fastapi_app/index.json`; do not rebuild or repeat wheel UAT because the
  Python package tree and exact wheel are unchanged. Proof: the exact failing
  command, `scripts/generate_enhanced_index.py --all --check`, reports all
  32 maintained indexes current before the single repair commit is pushed.
- Confirmed root cause: the maintained targeted generator accepts one optional
  positional folder, not a folder list. Resolution: invoke it once for `docs`
  and once for `docs/verification`; both targeted refreshes pass. ⚠️ TERMINAL
  ISSUE: combined two-folder index refresh -> separate maintained invocations.
- Confirmed root cause: `test_release_publication_authorization_holds_by_default`
  tested the mutable repository authorization record instead of an isolated
  default-HOLD fixture, making a genuine authorization state fail the release
  suite by construction. Resolution: create a temporary HOLD record inside the
  test and pass it explicitly to the validator. Evidence: the focused
  regression passes for the isolated HOLD state while the live three-target
  authorization checks remain reserved for the refreshed reviewed candidate.
- Confirmed root cause: zsh reserves `path` as an array tied to `PATH`, so the
  loop assignment replaced command lookup for that shell process. Resolution:
  rerun the inspection with the task-specific variable `release_artifact` and
  absolute command paths, then move only the inspected ignored, non-symlink
  build directories recoverably before the clean rebuild. Evidence: the
  corrected inspection identified exactly `Python/dist` and
  `Python/structural_lib_is456.egg-info`; the clean build, candidate check, and
  installed-wheel verifier all passed. ⚠️ TERMINAL ISSUE: zsh special variable
  `path` shadowed `PATH` -> task-specific variable plus absolute commands.

### Validation through local candidate freeze

- Live base/GitHub: `main = 970a78c1`; no open PRs; release worktree
  `READY_LOCAL`; `source_bound=true`.
- Focused release environment/version regressions: 14 passed.
- Canonical release preparation: 6,414 passed, 3 skipped, 6 deselected; React
  production build passed.
- Normal build-anchor commit hooks: all passed.
- Rebuilt exact installed wheel: SHA-256 `34892d86...14bb`; 5,553 passed, 51
  skipped, 2 deselected; installed CLI workflows passed.
- Exact candidate: 29/29 UAT cases and 12/12 advertised commands passed.
- Final affected indexes, quick 10/10, immutable final commit, hosted checks,
  and exact-head review complete in the next closeout stage. The exact-wheel
  publication preflight is intentionally reserved for the reviewed and
  authorized target identity.

### Timing through local candidate freeze

- Orientation, release controls, and lane creation: approximately 2 minutes.
- Canonical preparation, release-document correction, and focused checks:
  approximately 6 minutes.
- Exact build, installed verification, candidate UAT, and evidence recording:
  approximately 5 minutes.
- Hosted CI/review wait and final closeout are not included here.

## 2026-08-17 — Session: LIB-PRO-002-J Release Signal Convergence

**Agent:** Codex (`ops`, sole writer)

**Branch:** `codex/lib-pro-002-j-release-signal` from Packet I merge
`origin/main = 0ba2f397aec267bc74a31281f9158189fde2749d`

**Git handoff receipt:** `docs/verification/lib-pro-002-j-closeout-determinism-git-handoff-receipt.json`

**Focus:** Bind scheduled/tag full suites to the interpreter selected by
`actions/setup-python`, replace the preflight's shared release-ready label with
mode-accurate preparation/candidate/publication verdicts, and require exact-head
hosted receipts before publication readiness. Do not build a wheel, bump a
version, tag, publish, authorize targets, or activate Packet H; exact artifact
steps 3 and 4 are reserved for the next session at the owner's request.

### Summary

- Weekly Verification and publish validation now pass the exact setup-python
  executable through the supported `STRUCTURAL_LIB_PYTHON` contract when their
  full Python suites execute launcher-dependent tests. The strict launcher was
  not weakened and no bare-system fallback was introduced.
- Preflight now reports `READY_TO_PREPARE_CANDIDATE` without a wheel,
  `CANDIDATE_TECHNICALLY_READY` plus `PUBLICATION_HOLD` after exact-wheel/UAT
  success without complete publication evidence, `NOT_READY` on technical
  failure, and `READY_TO_PUBLISH` only for an exact authorized target.
- Candidate-wheel preflight now runs the packaged source-free release UAT and
  public examples in the disposable clean-install environment rather than
  treating metadata/import/CLI help alone as technical candidate evidence.
- The exact-candidate review receipt now binds passing required PR checks and
  Weekly Verification to the reviewed head. Wrong/missing hosted status, head,
  or run URL blocks publication readiness.
- The next-session brief records the owner's requested boundary: step 3 builds
  one temporary technical-acceptance wheel from unchanged synchronized `main`;
  step 4 clean-installs and verifies that same hash. Neither step authorizes a
  new version or publication.
- Maintained index dates now follow content identity instead of checkout mtime,
  and no-op generation skips disk writes. Session preparation no longer hides
  index generation or presents a pre-mutation Git snapshot as a final verdict;
  logs/tasks/receipts freeze first, affected indexes refresh once, and the last
  session check is read-only.

### Issues encountered

- Hosted Weekly Verification run `31988837003` had failed six otherwise valid
  governance/session tests because their recursive repository launchers could
  not resolve a project Python, while the publish full-suite step contained the
  same latent environment gap.
- A zero-error pre-bump run with no wheel, exact review, hosted receipt, or
  target authorization printed `READY TO RELEASE`, conflating permission to
  prepare a candidate with permission to publish.
- The exact-review receipt template and validator did not record hosted checks,
  so the future publication verdict could not machine-prove the plan's required
  exact-head PR and Weekly Verification evidence.
- The first post-implementation formatting check found one deterministic Black
  wrapping change in `scripts/release.py`; tests already passed, but the Python
  candidate was not yet format-frozen.
- The first focused index refresh again rewrote historical `last_updated` values
  for unchanged files in the fresh linked worktree, producing unrelated
  generated diff churn before the candidate freeze.
- The first React-suite command stopped before collection because the fresh
  Packet J worktree had no `react_app/node_modules`, so `vitest` was not found.
  No test executed and the attempt was not accepted as React evidence.
- Final semantic review found that the CLI still permitted two contradictory
  combinations: a future pre-bump positional version together with an exact
  current-source wheel, or a publication target without any wheel evidence.
- The first normal commit-hook run rejected the rewritten handoff because its
  `Required Reading` heading capitalization no longer matched the session
  checker's exact required contract. No commit was created.
- Manual Weekly Verification run `31998565603` passed dependency, clean-wheel,
  Docker, Python-coverage, and FastAPI work, then failed documentation drift;
  React was skipped and the summary correctly failed. Required PR checks had
  passed, so the Packet J head was not merged.
- The previous index-determinism repair excluded `last_updated` from freshness
  hashes but left every displayed file date sourced from filesystem mtime. A
  fresh linked worktree therefore still rewrote many byte-level projections
  even while `--check` correctly reported their content hashes current.
- `session end --fix` silently invoked the index generator from the dirty-path
  snapshot captured before its own handoff/task writes. It could therefore miss
  newly changed folders, mutate indexes before all source docs froze, and print
  a safe-closeout message from the earlier Git snapshot.
- The first durable freeze wording placed the final read-only `session end`
  before the candidate commit, but that command correctly treats intended
  uncommitted changes as a failed closeout. Following the wording would make a
  successful final verdict impossible.
- Active handoff guidance still required every new candidate to record its PR
  number inside `SESSION_LOG.md`, although the number normally does not exist
  until after the first push. That requirement itself forced a status-only
  post-PR rewrite and another index/CI cycle.
- Independent read-only review rejected the first closeout repair because a
  clean pre-mutation `session end --fix` could write the handoff and still exit
  `0`. The text said preparation-only, but machine callers could still accept
  the process status as final success.
- No Git, worktree, or Python interpreter-binding issue occurred in Packet J.

### Root causes and resolutions

- Confirmed root cause: `actions/setup-python` changes the workflow `python`
  path but does not create a repository `.venv` or set `VIRTUAL_ENV`; the full
  suites recursively invoke `run.sh`/`python_runtime.sh`, whose fail-closed
  contract accepts `STRUCTURAL_LIB_PYTHON` instead of guessing a system
  interpreter. Resolution: prefix the Weekly and publish full pytest commands
  with `STRUCTURAL_LIB_PYTHON="$(command -v python)"` and enforce both exact
  workflow steps in repository tests. Evidence: the focused workflow contract
  passes and the launcher remains unchanged.
- Confirmed root cause: `cmd_preflight` selected its final text only from the
  aggregate technical error count; wheel, review, hosted, target, and owner
  authorization states did not participate. Resolution: centralize a pure
  mode-specific verdict contract, add optional exact target evaluation, and
  print every remaining publication hold. Evidence: parameterized tests cover
  technical failure, missing wheel, technically ready/no target, authorization
  HOLD, and fully authorized publication with their exact exit codes.
- Confirmed root cause: clean-wheel preflight ran metadata inspection, import,
  and CLI help but not the packaged negative UAT/public examples. Resolution:
  run `structural_lib.release_uat --require-installed-wheel` inside the same
  disposable source-free environment before technical readiness. Evidence: a
  focused source contract test requires that exact invocation; live artifact
  execution is intentionally deferred to next-session step 4.
- Confirmed root cause: authorization validated an independent review receipt
  but the receipt schema contained no hosted evidence. Resolution: require
  `required_pr_checks` and `weekly_verification` PASS records, GitHub Actions
  URLs, and head SHAs equal to the reviewed candidate. Evidence: the valid
  authorization fixture passes and a mismatched Weekly head is rejected.
- Confirmed root cause: the new verdict helper and summary branch exceeded
  Black's canonical wrapping shape. Resolution: run Black on the one reported
  source file only. Evidence: the repeated 103-test selection, Black, Ruff, and
  `git diff --check` all pass.
- Confirmed root cause: the earlier hash repair treated `last_updated` as
  observation-only but every analyzer still recomputed that field from
  filesystem mtime, and writers always rewrote both projections. Resolution:
  date new/changed entries at generation, preserve prior entry dates by raw-file
  content hash and the folder date by deterministic projection hash, and skip
  byte-identical writes. Evidence: regressions change both checkout mtime and
  generation date yet retain byte-identical JSON/Markdown, while a content
  change at the same mtime advances both dates and changes the hash.
- Confirmed root cause: `session end --fix` mixed preparation, index mutation,
  and final validation while relying on one pre-mutation Git snapshot.
  Resolution: remove its index-generator call, label it preparation-only, make
  the final safe verdict available only without `--fix`, and encode the exact
  log/task/receipt -> one index refresh -> read-only validation order in agent
  and contributor instructions. Evidence: the session regression observes the
  canonical dirty paths, proves no generator subprocess is invoked, and proves
  preparation mode cannot print `Safe to end session`.
- Confirmed root cause: the freeze policy named the final repository write but
  did not explicitly place the immutable local commit before the clean-tree
  validation. Resolution: encode one unambiguous sequence everywhere:
  freeze sources/receipt, refresh affected indexes, commit locally, run plain
  `session end` read-only, then push unchanged. Evidence: the final command is
  now evaluated only against a clean committed candidate, while every later
  hosted/merge fact remains external.
- Confirmed root cause: the older continuity rule treated a future GitHub PR
  identifier as required versioned session content instead of external status.
  Resolution: include a PR number only when it is already known before freeze;
  never rewrite a candidate solely for a new PR number, hosted result, or merge
  hash. Evidence: all active onboarding/closeout guidance and the retained
  deprecated example now state the same no-rewrite boundary.
- Confirmed root cause: `cmd_end` changed its human message for `--fix` but left
  the shared `0 if all_passed else 1` return branch unchanged. Resolution: an
  otherwise passing preparation exits distinct status `2`; only plain read-only
  validation can exit `0`. Evidence: the new clean-state regression simulates a
  successful handoff write, requires exit `2`, and forbids the final safe text;
  the dirty preparation path continues to exit `1`.
- Confirmed root cause: linked worktrees share Git objects but not ignored
  dependency directories, and `./run.sh test --react` intentionally executes
  the pinned test command without installing packages. Resolution: select the
  repository's healthy pinned Node 24 runtime, run `npm ci` from the lockfile in
  the Packet J worktree, then execute the unchanged React command. Evidence:
  48 files and 267 tests pass.
  ⚠️ TERMINAL ISSUE: `vitest` was unavailable in the fresh worktree -> installed
  lockfile dependencies with pinned Node 24, then reran the actual React suite.
- Confirmed root cause: parser arguments represented independent options while
  verdict modes are mutually exclusive; no cross-option contract rejected the
  contradictory combinations. Resolution: add an explicit mode validator so
  future-version checks remain pre-bump-only and publication-target evaluation
  requires an exact wheel. Evidence: four mode-combination regressions pass and
  both contradictory modes return `NOT_READY` through the normal error path.
- Confirmed root cause: the handoff rewrite changed a machine-consumed heading
  from `Required Reading` to sentence case even though the session validator
  performs an exact heading match. Resolution: restore the canonical heading
  without changing the handoff content. Evidence: the repeated session-doc and
  normal commit-hook checks pass.
- Confirmed root cause: the scheduled/manual FastAPI benchmark saved its
  transient report into tracked `docs/reference` before the workflow ran the
  maintained index check. That outcome-changing write made
  `docs/reference/index.json` and parent `docs/index.json` stale on the hosted
  runner; it was unrelated to interpreter binding. Resolution: save and upload
  the report from `$RUNNER_TEMP`, leaving the indexed checkout immutable, and
  add a workflow regression forbidding the tracked path. Evidence: the focused
  workflow/release selection and local canonical gates pass; an exact-head
  Weekly rerun is required before merge.

### Validation through content freeze

- Startup: Packet I PR #819 passed required checks and merged unchanged at
  `0ba2f397`; primary `main` was clean/equal before a fresh Packet J linked lane
  was created from that exact commit.
- Source binding: Packet J reported `source_bound=true`, `READY_LOCAL`, clean
  tree, no operation marker, and equality with fetched `origin/main`.
- Focused Packet J release selection: 103 workflow-contract, release-script,
  and release-environment tests passed before the closeout repair. The added
  closeout/index regressions pass and are included in the final consolidated
  focused replay.
- Hosted-repair replay: the exact quick FastAPI benchmark saved a non-empty
  report under a fresh temporary directory, after which all 32 maintained
  indexes remained current; quick 10/10 and canonical 31/31 gates passed.
- Consolidated repository boundary: quick gate 10/10; Python 6,406 passed, 3
  skipped, and 6 deselected; FastAPI 452 passed; React 267 passed across 48
  files; the full canonical gate passes after content freeze; normal commit
  hooks pass on the immutable candidate.
- Exact wheel build and clean-install verification were not run because the
  owner explicitly assigned release-preflight steps 3 and 4 to the next
  session. Publication remains `HOLD`.

### Timing through content freeze

- Packet I hosted acceptance, exact-head merge, and primary synchronization:
  approximately 3 minutes.
- Packet J safe-lane orientation, root-cause trace, implementation, and focused
  proof: approximately 15 minutes.
- The cyclic closeout/index defect was accepted as an outcome-changing repair;
  final focused, quick/canonical, exact-head hosted, and merge closeout follow
  this new content freeze. No hosted/merge status-only repository write follows.

## 2026-08-17 — Session: LIB-PRO-002-I Advertised CLI Convergence

**Agent:** Codex (`backend`, sole writer)

**Branch:** `codex/lib-pro-002-i-cli` from freshly fetched
`origin/main = b3a9c367de012982a8b9adefda0db60e2d762d7b`

**Git handoff receipt:** `docs/verification/lib-pro-002-i-git-handoff-receipt.json`

**Focus:** Replace the advertised beam-design CLI's lossy/defaulting intake
with a fail-closed lossless/strict project boundary while retaining the
versioned `beams` output and its `bbs`, `detail`, and `dxf` consumers. Add the
advertised-entrypoint inventory and CLI cases to source-free release UAT. Do
not start Packet J, change formulas, bump a version, or publish.

### Summary

- Added one strict CLI design service. Generic CSV passes through the lossless
  import ledger; JSON rejects duplicate keys, non-finite constants, unsupported
  envelopes, unknown fields, alias conflicts, and empty projects.
- The entire project, including duplicate member identities and explicit
  effective-depth basis, validates before the first calculation call. Blocked
  input returns non-zero, writes no result, emits no partial PASS, and keeps
  stdout free of diagnostics.
- Retained output schema version `1` and its top-level `beams` envelope. Valid
  output remains accepted by BBS, detailing, and DXF consumers; the maintained
  sample and CLI guidance now provide complete explicit inputs rather than
  precomputed steel/status fields.
- Expanded packaged release UAT from 19 to 29 cases and bound all 12 live CLI
  commands to a packaged inventory classified as calculation entry, result
  consumer, inspection, or compatibility.
- Exposed a validation-only project-batch command so the CLI can prove whole-
  batch acceptance without performing the strict calculation and legacy
  compatibility calculation twice.

### Issues encountered

- The existing advertised `design` command silently skipped malformed CSV rows,
  supplied effective depth/cover values through legacy defaults, contaminated
  stdout with warnings, exited zero, and published a partial PASS artifact.
- The first worktree-creation command could not start because its execution
  working directory was the not-yet-created target path. No command ran and no
  repository state changed.
- The first formatting check found the expanded UAT and CLI test modules did
  not match Black/import ordering, so candidate formatting was not yet frozen.
- The first focused index refresh rewrote `last_updated` for many unchanged
  files because the fresh linked worktree gave all checked-out files today's
  filesystem mtime, creating unrelated candidate churn.
- The first session-end check could not discover the existing valid receipt
  because its Markdown path was wrapped onto the line after the required label.
- The first normal commit-hook run stopped on strict typing for derived-depth
  nullable values and Bandit's existing row-skip findings because the packet
  had unnecessarily changed the legacy adapter file.
- A follow-up direct hook diagnostic guessed a bare `pre-commit` executable,
  which is not exposed on this shell's PATH even though it is installed in the
  project-bound Python environment.

### Root causes and resolutions

- Confirmed root cause: `cmd_design` directly called
  `excel_integration.load_beam_data_from_csv`, whose compatibility parser
  catches row exceptions and continues, and whose model constructor fills
  structural defaults. Resolution: route CSV through `parse_single_csv_lossless`,
  use a strict versioned JSON reader, account every accepted field, validate the
  whole project through `validate_project_beam_batch_v1`, then call the retained
  beam pipeline only after all records pass. Evidence: malformed-only, mixed,
  empty, missing-depth, non-finite, unknown, duplicate, and ambiguous cases all
  return non-zero with zero calculation calls and no output artifact.
- Confirmed root cause: process creation resolves `workdir` before executing the
  shell, so a command cannot create its own nonexistent working directory.
  Resolution: create the linked worktree from the verified primary checkout,
  then run session/source-binding checks inside it. Evidence: the lane reported
  `source_bound=true`, `READY_LOCAL`, exact base equality, and a clean start.
  ⚠️ TERMINAL ISSUE: new worktree path used as `workdir` before creation ->
  created from the existing primary checkout, then changed command context.
- Confirmed root cause: hand-written additions required deterministic formatter
  wrapping and import sorting. Resolution: format only the two reported files
  and apply Ruff's import-order fix. Evidence: Black, Ruff, and
  `git diff --check` pass on all Packet I Python paths.
- Confirmed root cause: index dates are still derived from filesystem mtime,
  which is not stable provenance in a newly materialized linked worktree.
  Resolution: restore only the task-generated indexes to their reviewed base,
  set unchanged tracked source mtimes to their last commit time, and regenerate
  the affected folders once; retain task entries and genuine content-hash
  repairs while removing date-only churn. Evidence: final index checks pass and
  the reviewed index diff contains no unchanged-file date rewrites.
- Confirmed root cause: `_parse_git_receipt_path` requires the receipt label and
  path on one line. Resolution: place the existing repository-relative path on
  the label line without changing the receipt. Evidence: the repeated session-
  end validator resolves and validates the task ID, branch, and receipt hash.
- Confirmed root cause: runtime issue checks established complete numeric input,
  but Mypy could not narrow values stored in a `dict[str, float | None]`; CLI
  aliases were also added to the legacy adapter even though only the ledger
  needs them. Resolution: explicitly narrow the operands, annotate UAT helper
  arguments/parser choices, restore the adapter unchanged, and extend aliases
  only in the lossless import boundary. Evidence: focused tests, Mypy, Bandit,
  and the repeated normal hooks pass. No Bandit suppression was added.
- Confirmed root cause: the shell PATH does not include the primary checkout's
  virtual-environment scripts. Resolution: invoke the installed hook runner
  through `./scripts/python_runtime.sh -m pre_commit`. Evidence: targeted Mypy
  and Bandit diagnostics complete through the bound interpreter.
  ⚠️ TERMINAL ISSUE: bare `pre-commit` was unavailable -> used the maintained
  worktree-bound Python launcher with `-m pre_commit`.

### Validation through content freeze

- Startup: fetched `origin/main`; primary was clean/equal at `b3a9c367`; fresh
  linked lane was `source_bound=true`, `READY_LOCAL`, with no operation marker.
- Narrow contract diagnostic: 26 selected CLI tests and the release-UAT test
  passed before documentation closeout.
- Consolidated Packet I selection: 150 passed across CLI, Excel integration
  edges, lossless imports, strict batch, and expanded release UAT.
- Expanded source UAT: 29/29 cases pass; the live 12-command parser inventory
  exactly matches the packaged classified inventory.
- Black, Ruff, and `git diff --check` pass for every changed Python/test path.
- Exact-wheel build/install verification is intentionally reserved for the
  next release-preparation task at the owner's request; it is not publication
  authority.

### Timing through content freeze

- Git/source orientation and safe lane creation: approximately 5 minutes.
- Contract tracing, implementation, and focused repair: approximately 20
  minutes.
- Documentation, receipt, indexes, gates, hosted CI, and merge closeout are
  completed after this content freeze.

## 2026-08-17 — Session: LIB-PRO-002 Post-Fix Usability Re-Audit

**Agent:** Codex (`library-expert`, documentation/evidence owner)

**Branch:** `codex/lib-pro-002-usability-refresh` from A-G merge
`fe4ab025419b834c6d0f840e9492c0604ae74201` (PR #815)

**Git handoff receipt:** `docs/verification/lib-pro-002-post-fix-recheck-git-handoff-receipt.json`

**Focus:** Re-run the synthetic one-storey user workflow and manual comparison,
verify whether A-G fixed the original usability hazards, audit professional API
and publication surfaces, and update the active plan without changing runtime
behavior or authorizing publication/professional use.

### Summary

- Confirmed that the A-G fixes are material: canonical and compatibility beam
  services block malformed/empty inputs; named imports account rows/fields;
  column materials are explicit; beam/slab/column/footing results retain
  qualified-review truth; the current candidate wheel passes its declared
  19-case negative UAT.
- Recomputed a linked one-storey slab-to-beam-to-column-to-footing gravity
  example. The library matches the independent load, action, flexure, shear,
  column, footing pressure/moment/punching, and development-length arithmetic.
  The footing correctly remains `FAIL` for inadequate dowel anchorage and
  retains HOLD reasons for assumed load/soil/supporting-area bases.
- Reproduced one unresolved advertised-path defect: the `design` CLI skipped a
  malformed row, printed its warning to stdout, exited `0`, and emitted a
  one-of-one PASS summary. Its old intake also supplies cover/effective-depth
  assumptions outside the lossless/strict boundary.
- Confirmed that the published PyPI `0.23.1a1` is the pre-A-G artifact: its page
  has the wrong `0.23.0` pin and its displayed batch example raises
  `AttributeError` against the exact installed wheel. No claim was made that
  current source repairs the immutable old artifact.
- Updated the active plan, task board, planning handoff, and planning README.
  New Packet I owns CLI intake convergence, a versioned machine-readable output
  contract, retained `design -> bbs/detail/dxf` compatibility or explicit
  deprecation, advertised-entry-point inventory, and exact-wheel CLI negatives.
  Packet H whole-building planning remains inactive.
- A follow-up publication-readiness replay added Packet J rather than widening
  Packet I: scheduled/tag full suites must bind the setup-python interpreter,
  and pre-bump, technical-candidate, and authorized-publication modes must emit
  different verdicts. No version bump or release action was authorized.

### Verification

- Current source binding: `source_bound=true`; exact audit base
  `fe4ab025419b834c6d0f840e9492c0604ae74201`.
- Manual/library comparison matched the Section 2.4 values for slab, beam,
  column, and footing, including `Ast_slab=207.012 mm2`,
  `Ast_beam=465.092 mm2`, `Pu_column=68.789063 kN`,
  `q_footing=89.027778 kPa`, `Mu_footing=1.533643 kNm`, punching utilization
  `0.023010`, and required dowel `Ld=644.732 mm`.
- Built the current wheel into a temporary directory, installed it into a clean
  temporary environment, and ran `structural_lib.release_uat
  --require-installed-wheel`: `PASS`, 19/19 declared cases, installed origin.
- Focused current-source selection: 79/79 passed across batch, imports, column
  project contract, result contract, release UAT, and Excel-integration edges.
- Exact published-wheel replay: installed PyPI `0.23.1a1` into an isolated
  environment; the displayed `GenericCSVAdapter` example failed with
  `AttributeError: 'BeamGeometry' object has no attribute 'b_mm'`.
- API audit: root `__all__` 187 symbols; service facade 168 symbols (91
  functions, 77 classes); 28 service functions expose at least one audited
  unit-ambiguous name requiring canonical/compatibility disposition before a
  stable promise.
- Independent structural reviewer: ACCEPT; independently reproduced every
  Section 2.4 value and ran 101 focused tests, with no clause/claim
  contradiction. Independent release reviewer initially rejected two plan
  gaps; both the CLI output/downstream contract and post-plan-merge base wording
  were corrected, and the focused follow-up returned ACCEPT before closeout.
- Provisional `./run.sh release preflight 0.23.1a2`: 6,387 Python tests passed,
  446 FastAPI tests passed, and the React build passed; it also reported no
  candidate wheel and still printed `READY TO RELEASE`, so it is accepted only
  as green pre-bump local health—not publication readiness.
- Hosted Weekly Verification run `31988837003` at exact A-G merge
  `fe4ab025...`: Docker, locked dependency, and clean-wheel jobs passed; the
  full suite failed six governance/session tests because recursive repository
  launchers could not find a project interpreter, and the summary failed.
- Publication authorization checks for provisional `0.23.1a2` correctly
  returned non-zero for TestPyPI, PyPI, and GitHub Release because decision,
  version, tag, targets, owner, time, and exact review receipt remain unset.

### Issues encountered

- The advertised CLI retained the original row-loss/defaulting class after A-G
  merged, even though the declared 19-case wheel UAT passed.
- The first isolated PyPI replay inherited the repository `PYTHONPATH`, so it
  imported current source rather than the installed wheel and then failed on a
  missing dependency. That attempt was not accepted as package evidence.
- The first synthetic footing call used human-readable basis text where the
  strict contract requires exact controlled tokens. It blocked correctly before
  calculation.
- Independent release review found that a direct switch from the old CLI
  `beams` artifact to the strict service `members` envelope could silently break
  advertised `bbs`, `detail`, and `dxf` consumers, and that the handoff's exact
  `fe4ab025…` future base would become stale after this plan merges.
- The scheduled full workflow and publish full-suite step do not export the
  selected setup-python interpreter, although their tests can recursively call
  `run.sh`/`python_runtime.sh`; the scheduled run failed six such tests.
- Pre-bump preflight uses the same success label as publication readiness even
  when it has no exact wheel and does not evaluate immutable review, hosted
  receipts, or exact target authorization.
- ⚠️ TERMINAL ISSUE: a targeted workflow search included an unmatched
  `.github/workflows/*.yaml` zsh glob and stopped that compound command; running
  `rg` directly on `.github/workflows` produced the intended evidence.
- The first I-J handoff draft duplicated detailed-plan history and commands,
  reached 200 lines, and failed the repository's 150-line brief gate.
- Normal commit hooks accepted the plan but warned that the descriptive status
  `In Progress — Packets I-J Planned` was outside the canonical metadata enum.
- ⚠️ TERMINAL ISSUE: the first repair check guessed the nonexistent
  `scripts/check_doc_metadata.py`; `./run.sh find "doc metadata"` resolved the
  maintained command to `scripts/check_docs.py --metadata --strict`.

### Root causes and resolutions

- Confirmed CLI root cause: A-G's route inventory covered service,
  imports, HTTP/SSE/React, and selected package examples, but not every
  advertised calculation entry point. The historical CLI therefore continued
  calling `services.excel_integration.load_beam_data_from_csv`, which catches
  parse errors, prints a warning, and continues with surviving rows. Resolution
  in this documentation packet: add RC-7, CLI-01/CLI-02/REL-UAT-02, and Packet I
  with whole-file blocking, row/field conservation, non-zero exit, stderr-only
  diagnostics, versioned output compatibility, downstream workflow tests, and
  an advertised-entry-point inventory. Evidence: mixed-row live replay and
  direct source trace.
- Confirmed UAT root cause: the packaged matrix proves its handler set is
  complete relative to its data file, not complete relative to public docs/CLI
  surfaces. Resolution: Packet I binds matrix coverage to the advertised
  entry-point inventory and adds exact-wheel CLI cases. Evidence: 19/19 UAT PASS
  alongside the reproduced CLI failure.
- Confirmed installed-package evidence root cause: worktree-bound launchers set
  source routing that is unsuitable for an isolation proof. Resolution: remove
  `PYTHONPATH`/`PYTHONHOME`, install dependencies and the exact wheel in a fresh
  temporary environment, verify `structural_lib.__file__`, then accept the
  replay. Evidence: installed origin under temporary `site-packages` for both
  current candidate and published-wheel runs.
- The footing token failures were correct fail-closed validation, not product
  defects. Resolution: use the maintained exact values
  `includes_footing_self_weight_and_overburden` and
  `largest_frustum_1v_2h`; the corrected call then matched manual arithmetic.
- The independent review defects were plan incompleteness, not style issues.
  Resolution: freeze the CLI output/downstream contract and treat `fe4ab025…`
  as the required A-G ancestor while binding Packet I to exact fetched
  `origin/main` after this reviewed plan merges.
- Confirmed hosted-interpreter root cause: setup-python selects an executable
  but creates neither the repository `.venv` nor `VIRTUAL_ENV`; the launcher is
  intentionally fail-closed, and nightly/publish full suites omitted the
  supported `STRUCTURAL_LIB_PYTHON` binding already used by PR control-plane
  checks. Resolution in the plan: Packet J exports the exact
  `command -v python` path for recursive full suites, preserves strict launcher
  selection, adds workflow-contract tests, and requires a fresh manual Weekly
  Verification pass on the immutable J head.
- Confirmed preflight-verdict root cause: local pre-bump, exact-wheel technical,
  and authorized publication states share one `errors == 0` success label;
  missing wheel is only a warning and authorization is a separate command.
  Resolution in the plan: Packet J introduces mode-specific verdicts and
  reserves `READY_TO_PUBLISH` for exact wheel/UAT, review, hosted receipts, and
  target authorization. Evidence: the green provisional preflight coexisted
  with the reproduced CLI failure, failed hosted full run, and three rejected
  authorization checks.
- Confirmed brief-length root cause: the handoff repeated A-G history and full
  command blocks already owned by the detailed plan. Resolution: retain exact
  branches, I/J ownership, evidence, and stop rules while linking execution
  details to the plan; the brief is 141 lines and the brief-length gate passes.
- Confirmed metadata root cause: a descriptive suffix was placed in the strict
  `Status` field instead of plan prose. Resolution: restore canonical
  `In Progress`; validate through the discovered consolidated metadata command.

### Limitations and handoff

- This session changed documentation and work state only; it did not implement
  Packet I or alter structural calculations.
- The one-storey replay is a synthetic component/load-path regression, not a
  building analysis, source acceptance, geotechnical verification, qualified
  review, code-compliant deliverable, or professional approval.
- Next routine action: merge this plan, implement and merge Packet I from exact
  fetched post-plan `origin/main`, then implement Packet J from exact post-I
  `origin/main`. Run broad/exact-wheel/full hosted evidence at J, stop before a
  version bump, and keep publication and Packet H held.

## 2026-08-17 — Session: LIB-PRO-002 B-G Cumulative Safety Integration

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/lib-pro-002-b-lossless-import` from Packet A merge
`3986935ecb473c1f9d56dec44aeb4218d9192f84` (PR #814)

**Git handoff receipt:** `docs/verification/lib-pro-002-a-g-git-handoff-receipt.json`

**Focus:** Complete Packets B-G as one cumulative candidate: lossless imports,
transport/client convergence, cross-element result truth, evidence identity,
API/documentation truth, exact-wheel negative UAT, and publication policy.
Packet H, publication, professional approval, issue/PR closure, branch deletion,
and unrelated worktree cleanup remain out of scope.

### Summary

- Replaced first-match/row-dropping import behavior with explicit or uniquely
  detected adapters, a versioned every-field/every-row normalization ledger,
  stable blocking issues, exact source/accepted/blocked accounting, and strict
  single- and dual-CSV boundaries.
- Converged HTTP, SSE, compatibility, and React batch paths on the canonical
  strict beam service. Deprecated routes delegate; clients send explicit
  materials, actions, and depth basis without filling absent structural data.
- Added one fail-closed result contract separating intake, calculation,
  engineering, review, and overall state; required qualified review remains
  independent of serviceability escalation, and the footing dowel regression
  remains an engineering FAIL.
- Bound calculation, package content, controlled source/amendment, imported
  artifacts, normalization ledger, assumption origin, provenance, and replay
  identities without treating approval flags as verified source data.
- Added a machine-checked Alpha API classification, removed callable leakage,
  corrected version/claim/example documentation, and provided an installed-
  package interpreter/origin/extras preflight.
- Added the packaged source-free 19-case negative matrix and public-example
  runner, exact-wheel workflow receipts, and an explicit per-version/tag/target
  owner-authorization check before TestPyPI, PyPI, or GitHub Release actions.

### Issues encountered

- The owner had requested Git/worktree safety at the start of Packet A, yet a
  later policy side packet advanced `main` and overlapped Packet A's mutable
  session/index closeout surfaces, making the otherwise clean candidate
  diverge and forcing forward integration.
- The public single-CSV FastAPI route still bypassed the new lossless boundary,
  while the first lossless model counted one physical combined CSV as separate
  geometry and force rows.
- The streaming route initially imported the compatibility facade rather than
  the canonical service, preserving duplicate orchestration under a different
  import name.
- The first source-identity consolidation left footing code and the service
  evidence path with separate constants; an intermediate footing helper edit
  also misplaced a return and produced a `TypeError` in focused tests.
- The bundled sample route still substituted missing dimensions/actions and
  zero coordinates. React preserved the dataset hash separately but dropped
  each beam's sample/assumption provenance before batch calculation.
- Public API discovery exposed imported callables not covered by a complete
  stability class, while maintained READMEs and release checks disagreed about
  Alpha version and executable examples.
- The first architecture run found two FastAPI imports of a core model after
  strict import migration. This would violate the required Core to IS 456 to
  Services to UI dependency direction.
- The local React command initially assumed `$HOME/.nvm/nvm.sh`, which is not
  installed on this machine. An earlier `npm run type-check` attempt also found
  that the project declares no such script.
- PDF text extraction was unavailable during source-identity inspection, and
  an attempted release helper name (`source-surface-check`) did not exist.
- The first cumulative run exposed four stale dependent contracts: evidence
  schema `2.0` assertions after the intentional `3.0` upgrade, a React legacy
  response field used but omitted from its type, a compatibility-facade test
  monkeypatching internals removed for API classification, and a column test
  still requiring the deleted 25/415 defaults.
- The first exact-wheel candidate check stopped because the footing release-
  inclusion receipt still carried pre-INDIA-2 exact-arithmetic hashes and did
  not cover Packet E's reviewed footing assumption/provenance changes.
- The guessed direct index generator `scripts/generate_folder_indexes.py` does
  not exist in this repository, so that command stopped before any index write.
- The first full 31-check gate found three Packet F/governance omissions: the
  old API-doc sync check still required the deleted symbol-by-symbol stability
  duplicate, the new API-classification generator was absent from the script
  map/index, and placing its packaged UAT implementation at package root
  exceeded the root non-stub module limit.
- The second full gate passed 30/31 and found that the injected row-loss UAT
  adapter had suppressed Mypy's untyped-definition warning but still lacked
  the explicit return type required by the repository annotation checker.
- The first session-end check reported the handoff receipt missing even though
  the new receipt file existed and independently validated.
- A final verification attempt used the nonexistent `run.sh check-indexes`
  command, so the chained session-end step did not execute.
- The first maintained all-index check found three stale parent indexes after
  all directly edited child-folder indexes had been refreshed.
- The first staged diff check found trailing spaces in a new evidence file;
  the earlier unstaged diff check did not inspect untracked content.
- Normal commit hooks found four package-wide Mypy errors and rejected the
  noncanonical heading/row labels in the cumulative handoff brief.
- Independent exact-head review rejected `c66160c7` because publication
  authorization accepted arbitrary non-empty review-receipt text without
  resolving evidence or binding reviewed head/tree/version/target identity.
- A post-commit exact-wheel command was rejected before execution because its
  temporary cleanup trap used a raw recursive delete operation.
- A repair verification attempt guessed the nonexistent
  `scripts/check_annotations.py` path after the focused release suite passed.

### Root causes and resolutions

- Confirmed Git root cause: startup cleanliness was checked correctly, but lane
  safety was treated as a start-time property. Linked worktrees isolate files,
  not refs, and no active-candidate dependency/path-overlap gate ran before the
  later side packet merged. Resolution: Packet A added the durable whole-
  candidate overlap gate to `AGENTS.md` and the canonical Git workflow; this
  session then used one isolated cumulative writer from exact `origin/main`,
  made no primary-tree mutation, and preserved every unrelated lane. Evidence:
  `git_state.py --json --worktrees` reports the candidate at base equality,
  primary `main` clean, no operation marker, and the unrelated dirty detached
  `e54a` lane unchanged.
- Confirmed import root cause: parsing, adapter selection, row conversion, and
  compatibility return shapes were coupled, so downstream code could not prove
  conservation. Resolution: one ledger owns adapter candidates, artifacts,
  fields, physical rows, matches, exclusions, issues, and totals; combined CSV
  is an explicit single artifact role and every blocker returns no batch.
  Evidence: malformed, non-finite, ambiguous, duplicate, dropped, and unmatched
  regressions pass, including valid explicit zero.
- Confirmed orchestration root cause: transports independently normalized
  values because there was no canonical iterator/result boundary. Resolution:
  service validation prepares the complete batch contract and executes lazily;
  POST/SSE/React consume it, while legacy entry points delegate or deprecate.
  Evidence: service/HTTP/SSE request equivalence and calculation-call spies
  pass; blocked inputs make zero core calls.
- Confirmed identity root cause: source/amendment constants lived in an
  application service and were recopied into IS 456 code. Resolution: the
  layer-neutral identities now live in `core/source_identity.py`; evidence and
  footing import that one record, and the misplaced return was restored to its
  owning helper. Evidence: focused evidence/replay and footing tests pass, and
  the architecture checker reports zero violations.
- Confirmed sample root cause: the endpoint was historically a demo convenience
  path and therefore used `dict.get(..., plausible_value)` rather than treating
  bundled data as a controlled fixture. Resolution: all required strings and
  finite numbers are parsed without fallback, duplicate/unmatched identities
  fail closed, exact dataset/record identity and sample assumptions accompany
  every beam, and React preserves them. Evidence: the 153-beam BOQ/evidence
  regression plus the React provenance mapping test pass.
- Confirmed API/release root cause: public exposure, documentation, installed
  examples, artifact identity, and publication authority were independent
  lists. Resolution: generated classification and version checks fail on drift;
  exact-wheel UAT packages the negative matrix and advertised examples; the
  publish workflow checks a separate exact authorization record before any
  target. Evidence: classification, install-preflight, release-script, UAT,
  workflow-YAML, and current HOLD-policy tests pass.
- Confirmed architecture root cause: FastAPI constructed the historical core
  `DesignDefaults` compatibility model directly after migration. Resolution:
  explicit values enter a service factory and the UI layer imports services
  only. Evidence: 206 files pass the four-layer check and 661 files/4,498
  imports validate with zero broken imports.
- ⚠️ TERMINAL ISSUE: `$HOME/.nvm/nvm.sh` was absent -> used the repository-
  reported pinned Node 24 binary directory from `./run.sh frontend runtime`.
  The focused React test then passed. The missing `type-check` script is not a
  product failure; canonical React lint/tests/build are used instead.
- ⚠️ TERMINAL ISSUE: `pdftotext` was absent -> used maintained controlled-
  source manifests and hashes, without changing source claims. The nonexistent
  release helper name was replaced by the maintained `candidate-check` and
  direct version-surface helper tests discovered from `release.py`.
- Confirmed dependent-contract root cause: evidence/API/input contracts changed
  at their canonical owners, but four broad regressions still encoded the old
  surface. Resolution: update only those expectations/types to schema `3.0`,
  retain the explicit legacy `beam_id` fallback in its response type, patch the
  canonical common-version module rather than facade internals, and assert
  missing column materials block. Evidence: the four failed paths pass, and
  pinned React lint, all 267 tests, TypeScript production build, and Vite build
  pass.
- Confirmed receipt root cause: the D1 inclusion record was hash-frozen before
  the accepted exact stress-block correction in `d8202fef`, and Packet E then
  intentionally changed eight owned footing files. Resolution: inspect the
  exact diffs, record both reviewed refresh bases, update only the controlled
  owned-file hashes, and rerun the maintained inclusion check. Evidence: the
  inclusion gate and 40 Python/FastAPI footing regressions pass; no scope marker
  or original D1 source-head identity was weakened.
- ⚠️ TERMINAL ISSUE: the guessed `scripts/generate_folder_indexes.py` path was
  absent -> `./run.sh find "folder index"` identified the maintained
  `./run.sh generate indexes <owned-folder>` interface; only affected existing
  index folders are refreshed after every task-owned evidence write.
- Confirmed Packet F check-drift root cause: the generated classification
  registry replaced the old hand-maintained stability list, but
  `check_api.py --sync` still validated the removed duplicate rather than the
  new single source. Resolution: the checker now requires the stability page
  to bind `api-classification.json`, proves every documented compatibility
  symbol is classified, and excludes the literal `api.md` filename from symbol
  extraction. The three exported result dataclasses are explicitly identified
  as Alpha-preview calculation evidence in `api.md`. Evidence: all three API
  validation lanes pass.
- Confirmed control-plane root cause: the new generator was added to CI before
  the maintained automation registry/index, and the executable UAT lived at
  package root instead of behind a root facade. Resolution: register the
  generator with read/write permission modes, move the implementation with the
  maintained safe-file tool to `services/release_uat.py`, and retain the public
  `python -m structural_lib.release_uat` facade as a nine-line stub. Evidence:
  automation coverage is 110/110, the UAT test passes through the facade, and
  governance reports every root module stub-only with zero errors.
- Confirmed annotation root cause: the UAT test double used a local Mypy ignore
  instead of matching `InputAdapter.load_forces() -> list[BeamForces]`.
  Resolution: add the exact override type and remove the ignore. Evidence: all
  27 functions in the service UAT module are fully annotated and its 19-case
  regression passes.
- ⚠️ TERMINAL ISSUE: the first direct annotation-check command passed the file
  as a positional argument, but the maintained CLI requires `--file` -> reran
  with `--file Python/structural_lib/services/release_uat.py`; 27/27 functions
  report fully annotated.
- Confirmed session-end root cause: receipt discovery intentionally reads an
  explicit `**Git handoff receipt:**` path from the newest session entry and
  does not guess among many verification files. Resolution: bind this entry to
  the exact cumulative receipt path. Evidence: direct receipt validation
  already passes; session-end is rerun after the final index refresh.
- ⚠️ TERMINAL ISSUE: `run.sh` exposes maintained index validation as
  `./run.sh generate indexes --all --check`, not `check-indexes` -> discovered
  the exact interface with `./run.sh find "folder index validation"` and the
  built-in help, then used the maintained check before rerunning session-end.
- Confirmed index root cause: parent folder content hashes include changed
  descendants, so refreshing only folders containing directly edited files
  left `Python/structural_lib`, `fastapi_app`, and `react_app/src` stale.
  Resolution: regenerate those three maintained parents, then run the all-index
  check. Evidence: all 32 maintained index pairs must report current before the
  immutable commit.
- Confirmed staged-diff root cause: `git diff --check` covers tracked changes
  but not a new untracked file until it is staged. Resolution: remove the
  trailing spaces and require `git diff --cached --check` after intentional
  staging. Evidence: the staged candidate check passes before commit.
- Confirmed Mypy root causes: the strict import factory relied on two unused
  Pydantic compatibility defaults and typed the integer FastAPI stirrup value
  as `float`; the heterogeneous install-preflight report also widened its
  nested extras map to `object`. Resolution: pass the inert compatibility
  fields explicitly, match the boundary's integer type, and keep a separately
  typed `dict[str, bool]` for extras. Evidence: the package-wide Mypy commit
  hook must pass on all 234 source files.
- Confirmed handoff root cause: the general Markdown/index/brief-length checks
  accept heading case and descriptive table labels, while `scripts/session.py
  check` requires the canonical `## Required Reading`, `| **Current** |`, and
  `| **Next** |` literals. Resolution: restore those exact contract labels and
  retain the normal commit hook as the decisive contract. Evidence: the
  session-doc commit hook must pass before the candidate exists.
- Confirmed publication-gate root cause: the first authorization schema treated
  `exact_candidate_review_receipt` as a presence-only string and therefore
  could not distinguish immutable reviewed evidence from fabricated text.
  Resolution: require a repository-relative JSON receipt and exact SHA-256;
  validate ACCEPT, independent reviewer/time, reviewed head/tree/Python tree,
  version/tag/targets, review-before-authorization chronology, Git ancestry,
  clean checkout, unchanged package content, and an allowlisted evidence-only
  descendant delta. Evidence: valid reviewed candidate plus authorization must
  pass, while fabricated text, receipt tampering, identity drift, package
  drift, target drift, pre-review authorization, and extra changed paths must
  fail closed before publication.
- ⚠️ TERMINAL ISSUE: the first post-commit wheel command included a raw
  recursive temp-directory cleanup trap and was rejected before execution ->
  reran without any delete operation and retained the isolated UAT directory;
  exact-wheel UAT then passed 19/19 without repository mutation.
- ⚠️ TERMINAL ISSUE: `scripts/check_annotations.py` does not exist ->
  `./run.sh find "type annotation check"` resolved the maintained
  `scripts/check_type_annotations.py` command, which is used for the repair
  candidate instead.

### Validation before cumulative freeze

- Focused import/service/API/React, result/review, evidence/replay, API
  classification, install-preflight, release-policy, sample, and packaged-UAT
  regressions pass.
- Focused Mypy passes ten new/changed contract modules; Ruff and Black are
  clean on the complete Python/FastAPI/script surface.
- Architecture: 206 files, zero violations. Import validation: 661 files,
  4,498 imports, zero broken imports. OpenAPI baseline: 82 endpoints and 357
  schemas, current with no unrecorded drift. Publish workflow YAML parses with
  five jobs.
- Source-free candidate wheel
  `structural_lib_is456-0.23.1a1-py3-none-any.whl` passes clean-install version
  evidence, installed-package preflight, both advertised examples, and all 19
  declared negative UAT cases. Rehearsal SHA-256 is
  `cf16b49963374e31eee80a31b73f94d0997969fdf5515e805f270eafb16f4830`;
  matrix SHA-256 is
  `21da496a9dc9d90b3ce3537d100293db2a23d14461ed2f602b185fd13288f8ea`.
  The receipt says qualified review required and professional approval false.
- Publication authorization deliberately returns HOLD for `v0.23.1a1`/PyPI;
  the owner, exact future version/tag/targets, and candidate-review receipt are
  absent as required.
- Final cumulative suites pass on the repaired tree: Python 6,382 passed, 3
  skipped, 6 deselected; FastAPI 452 passed; React lint, 267 tests, TypeScript,
  and production build pass. The Git handoff source evidence and pre-index
  receipt validate with the expected HOLD for dirty/local-only/unchecked
  remote-review state.
- Immutable head `c66160c7bc25eba22011d051643fe93c1b406bac`
  passed normal hooks, the exact committed wheel (SHA-256
  `edefc7235944892a059345383f55547e71d49d1c3eb64cb0777d397433e811bc`)
  passed 19/19 UAT, all 6,382 Python/452 FastAPI/267 React tests passed, and all
  eight hosted PR #815 checks passed. Independent review correctly returned
  REJECT for the publication-receipt bypass above; none of those green gates
  overrides that outcome-changing finding.
- The first full canonical run passed 28/31 and exposed the three omissions
  above; their narrow API, automation, governance, and facade regressions now
  pass. The second run passed 30/31 and exposed the annotation omission above;
  its direct regression now passes. Refreshed affected indexes are the final
  repository writes. The final full 31-check retry, quick, session-end,
  immutable commit/review, and hosted results follow without changing this
  candidate evidence.

## 2026-08-17 — Session: LIB-PRO-002-A Strict Service Intake

**Agent:** Codex (`backend` and `tester`, sole writer)

**Branch:** `codex/lib-pro-002-a-strict-input` from freshly fetched
`origin/main = 55104e11257937b0a42fb06f931a70b8484cef39`

**Git handoff receipt:** `docs/verification/lib-pro-002-a-forward-integration-git-handoff-receipt.json`

**Focus:** Replace the beam batch service's silent structural defaulting and
implicit effective-depth derivation with the versioned strict project contract
frozen by G0. Do not edit imports, FastAPI/React transports, other element
families, release automation, API classification, or whole-building behavior.

### Summary

- Added strict versioned project beam input and result types with explicit-unit
  fields, stable issue codes and paths, orthogonal intake/calculation/
  engineering/review states, and a summary in which zero evaluated members can
  never PASS.
- Required every calculation-bearing value and exactly one explicit `d_mm` or
  complete cover/stirrup/tension-bar depth basis; malformed, empty, non-finite,
  out-of-range, unknown, conflicting, or duplicate inputs now block.
- Made the legacy batch functions a compatibility adapter that maps only known
  aliases, applies no structural defaults or alias precedence, and delegates to
  the canonical validator and calculation path.
- Preserved the accepted synthetic beam arithmetic and the completed unsafe-
  shear FAIL while proving every blocked member avoids `design_beam_is456`.
- Forward-integrated the subsequently merged workflow-policy packet without
  rewriting the original Packet A commit or touching unrelated worktrees.

### Issues encountered

- The live G0 task board and handoff still described G0 as a local candidate
  even though PR #812 had been independently accepted, merged, and synchronized
  to `main`; following that state literally would repeat the completed packet.
- The original batch path combined alias selection, numeric coercion, fallback
  structural values, fabricated member identity, and `D - cover - 8` depth
  derivation before invoking the calculation core.
- The first duplicate-identity implementation counted only otherwise-valid
  inputs, so a valid row could still calculate when its duplicate twin was
  independently blocked for another field error.
- Final pre-candidate review found that whole-batch duplicate validation also
  caused both strict and legacy iterators to calculate every accepted member
  before returning the first result, weakening streaming/cancellation behavior.
- The first focused Mypy run rejected the concrete `list[dict[str, Any]]`
  compatibility payload against an invariant `list[Mapping[...] | Input]`
  internal annotation.
- The first handoff-receipt command left zsh glob patterns unquoted, so the
  shell expanded the forbidden FastAPI/React/workflow paths and the receipt
  parser rejected the resulting arguments before writing a receipt.
- The first normal commit-hook run stopped because canonical Black reformatted
  one conditional-comprehension expression that Ruff format had left unchanged.
- Although Packet A started from a clean, current, isolated worktree, merging
  the later workflow-policy side packet advanced `main` and changed the same
  session/index surfaces before Packet A was published. Packet A therefore
  became `HOLD_DIVERGED` despite remaining clean.
- The first post-resolution quick gate passed all content checks but failed its
  two Git checks because the authorized merge operation necessarily remained
  open until the merge commit existed.

### Root causes and resolutions

- Confirmed root cause: immutable G0 closeout correctly froze versioned records
  before hosted review/merge facts existed, so the successor packet had to
  reconcile those external facts rather than mutate the prior candidate.
  Resolution: bind Packet A to fetched merge `55104e11`, mark G0 merged, and
  make Packet A the sole active task. Evidence: startup reports the new lane at
  exact base equality, `READY_LOCAL`, clean, and `source_bound=true`.
- Confirmed root cause: `_pick_first()` and `_to_float()` treated parsing,
  aliases, and assumptions as one operation and supplied 300/500/100/50/25/500/
  40 plus a generated ID whenever source values were absent or malformed.
  Resolution: one strict validator now accepts only canonical JSON numbers and
  a separately named compatibility adapter maps aliases without filling any
  structural value. Evidence: the table-driven service matrix and calculation
  spies pass; blocked/duplicate members make zero core calls.
- Confirmed root cause: duplicate counting used only validations that still
  held a constructed value, excluding invalid rows even when their non-blank
  `member_id` remained known. Resolution: count all validated member-ID hints,
  block every occurrence, and preserve each row's other issues. Evidence: the
  valid-plus-invalid duplicate-twin regression passes with two blocked members
  and zero calculation calls.
- Confirmed root cause: the first iterator delegated to a helper that eagerly
  constructed the complete typed batch result, coupling required whole-batch
  validation to calculation execution. Resolution: prepare all validations
  first but yield each blocked/calculated member lazily. Evidence: strict and
  legacy iterator regressions observe zero core calls before iteration and
  exactly one call after requesting the first of two members.
- Confirmed root cause: Python mutable lists are invariant even when their item
  types are compatible. Resolution: accept `Sequence` at the internal
  read-only batch boundary. Evidence: focused Mypy reports success for both new
  service modules.
- Confirmed root cause: zsh expands `**` before the called program can preserve
  it as a policy pattern. Resolution: quote every glob-valued receipt argument
  and rerun creation/validation. Evidence: the literal forbidden paths appear
  in the validated receipt. ⚠️ TERMINAL ISSUE: unquoted receipt globs expanded
  into repository paths -> quoted the patterns and reran the maintained tool.
- Confirmed root cause: Ruff format and the repository's pinned Black do not
  produce identical wrapping for the conditional-comprehension expression.
  Resolution: use the repository's normal Black hook result, run Black against
  all owned Python files, then rerun focused checks before restaging. Evidence:
  the retry must pass the unmodified normal hooks. ⚠️ TERMINAL ISSUE: commit
  hook reformatted one file -> accepted canonical Black output and reran gates.
- Confirmed root cause: worktree cleanliness and isolation were checked, but no
  active-candidate dependency/path-overlap gate was run before the later policy
  PR merged. Worktrees isolate files and indexes; they share refs, so advancing
  `main` made Packet A diverge, and the two packets overlapped
  `docs/SESSION_LOG.md` plus generated indexes. Resolution: preserve
  `22066d0d`, merge current `origin/main` into the existing Packet A branch,
  resolve only the predicted governance/index conflicts, and add a durable
  pre-publication active-candidate overlap gate to `AGENTS.md` and the canonical
  Git workflow. Evidence: the pre-merge comparison identifies only five shared
  governance/index paths, the merge reports conflicts only in those five paths,
  and no runtime source conflict occurs. ⚠️ TERMINAL ISSUE: a later side packet
  made the clean Packet A candidate diverge -> forward-integrated without
  rebase/reset/force and recorded the missing sequencing guard.
- Confirmed root cause: `git_state.py` correctly classifies any live merge as
  `HOLD_OPERATION`, while a merge cannot leave that state until its resolving
  commit is created. Resolution: for an authorized, fully resolved merge, run
  focused/content checks first, create the merge commit through normal hooks,
  then run the sole quick gate on the clean merge head before audit or push.
  Evidence: the premature quick run passes 8/10 content/governance checks and
  fails only `Git state` and `Unfinished operation` with the same explicit
  `operation: merge` hold. ⚠️ TERMINAL ISSUE: quick cannot pass inside an open
  merge -> move the single quick gate to the clean merge head.

### Validation through content freeze

- Startup: freshly fetched base equality at `55104e11257937b0a42fb06f931a70b8484cef39`,
  fresh linked worktree, `READY_LOCAL`, no operation marker, clean tree, and
  `source_bound=true`; the unrelated dirty detached `e54a` worktree remains
  untouched.
- Focused strict/compatibility service contract: 43 passed, including the
  complete negative matrix, calculation spies, accounted mixed/empty batches,
  explicit-versus-derived depth equivalence, lazy iterator execution, unchanged
  pilot numbers, and retained unsafe-shear FAIL.
- Ruff passes the three owned Python files; focused Mypy passes both service
  modules; `git diff --check` is clean.
- Architecture boundary check passes with 201 files and zero violations;
  import validation passes with 650 files, 4,416 imports, and zero broken
  imports.
- Forward integration started from clean heads `22066d0d` and `87205d64` with
  `source_bound=true`; all five conflicts were confined to the predicted shared
  session/generated-index paths.
- Receipt, affected indexes, quick `10/10`, session-end validation, immutable
  candidate commit, exact-head independent review, and hosted closeout remain
  after the final content freeze.

### Timing through content freeze

- Plan/Git/worktree safety and source binding: approximately 2 minutes.
- Test-first implementation, root-cause repair, and focused validation:
  approximately 14 minutes.
- Receipt/index/quick, immutable review, hosted wait, merge closeout, and total
  wall time remain to be recorded externally.

## 2026-08-17 — Session: Implementation-First Verification Policy

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/implementation-first-verification-policy` from freshly
fetched `origin/main = 55104e11257937b0a42fb06f931a70b8484cef39`

**Git handoff receipt:** `docs/verification/implementation-first-verification-policy-git-handoff-receipt.json`

**Focus:** Make the owner's implementation-first, batched-verification cadence
durable for future repository chats. Preserve the clean Packet A candidate and
all unrelated worktrees; do not change structural calculations, APIs, React,
adapters, release behavior, or the active LIB-PRO-002 handoff.

### Summary

- Made one bounded packet, rather than each edit, the routine verification
  boundary.
- Limited during-implementation checks to narrow evidence needed to guide or
  debug a live question.
- Consolidated focused checks, the single quick gate, commit hooks, hosted
  checks, and the cumulative full gate into an explicit non-duplicative
  cadence shared by top-level instructions, canonical efficiency policy, and
  the quality-gate skill.
- Kept required safety, independent-review, hosted-CI, and release gates intact.

### Issues encountered

- Existing guidance said to use targeted checks while editing and to avoid
  duplicated gates, but did not explicitly say that routine verification
  starts only after the whole bounded packet is implemented and frozen. That
  ambiguity could make future chats rerun unchanged checks after small edits.
- The first session-end check did not discover the committed handoff receipt
  because its path was wrapped onto the line after the bold label.

### Root causes and resolutions

- Confirmed root cause: the intended cadence was split across `AGENTS.md`, the
  canonical token-efficiency guide, and the quality-gate skill, while the phrase
  “while editing” lacked a necessity condition. Resolution: align all three
  surfaces on implementation first, necessary diagnostics only, one
  consolidated post-freeze focused selection, one quick gate, required hosted
  checks, and one cumulative full gate. Evidence: the efficiency policy check,
  documentation checks, affected indexes, quick gate, session-end contract,
  and normal commit hooks complete after content freeze.
- Confirmed root cause: the session-end parser requires the receipt path on the
  same line as the bold `Git handoff receipt` label. Resolution: place the
  committed path on that label line and retain this exact format for future
  entries. Evidence: the repaired session-end check discovers and validates
  the receipt. ⚠️ TERMINAL ISSUE: session end reported a missing receipt ->
  matched the maintained same-line parser contract.

### Validation through content freeze

- Startup evidence: fresh fetch equality at
  `55104e11257937b0a42fb06f931a70b8484cef39`, a clean isolated policy lane,
  and current-worktree Python source binding.
- Packet A remains a separate clean `READY_LOCAL` worktree at
  `22066d0d83f84995b898a58b43993f621ec2d8d0`; the unrelated dirty detached
  worktree remains untouched.
- No task-board or next-session-brief update is required because this policy
  change does not alter the active LIB-PRO-002 packet sequence or handoff.

## 2026-08-17 — Session: Pre-Release Input-Safety Contract Freeze

**Agent:** Codex (`orchestrator` and `doc-master`, sole writer; two bounded
read-only reviewers)

**Branch:** `codex/pre-release-input-safety-plan` from freshly fetched
`origin/main = 904a2f8cf0ea5d4595f57c46dac06e2e837bba45`

**Git handoff receipt:** `docs/verification/lib-pro-002-g0-git-handoff-receipt.json`

**Focus:** Independently check the one-storey usability report, reconcile its
confirmed outcome-changing defects with the completed professional remediation
history and current release surface, and freeze a dependency-ordered plan
before implementation. Do not change calculation, API, React, adapter, or
release behavior and do not publish a package.

### Summary

- Bounded the reported numerical match to the exact synthetic cases and
  retained the correct footing dowel-development failure.
- Traced the unsafe PASS path to silent project defaults and then found the
  wider shared cause: normalization and structural derivation are duplicated
  across service batch, imports, streaming, React, and column entry paths.
- Reconciled two independent read-only audits into six root causes, a single
  outcome-changing issue register, strict target contracts, a negative
  acceptance matrix, and eight dependency-ordered packets.
- Held every next publication until the Alpha safety gate and separate owner
  authorization; stable, engineering-use, professional-approval, and
  whole-building claims have additional explicit gates.

### Key Deliverables

- `docs/planning/pre-release-input-safety-and-professional-readiness-plan.md`
- active `LIB-PRO-002-G0` task and exact Packet A boundary
- current next-session handoff and planning index entry

### Issues encountered

- `./run.sh session start` was first run from the clean primary `main` checkout
  during orientation and wrote a new session skeleton there, contrary to the
  intended fresh-lane-only mutation boundary.
- The earlier `LIB-PRO-001` plan is correctly marked software-complete, while
  the new user pilot proves a different end-user data-ingress defect. Treating
  the pilot as unfinished old work would corrupt the historical evidence
  ledger and hide the new root cause.
- Existing green audit/quick/health evidence and the exact arithmetic pilot do
  not exercise silent field replacement, ambiguous import selection, row loss,
  executable README examples, or exact-wheel negative paths.
- A guessed standalone `scripts/check_frontmatter.py` path did not exist because
  frontmatter validation is part of the maintained unified documentation
  checker.
- Independent candidate review found that the Alpha gate called for an
  unspecified “independent review” and classified exact replay provenance as
  stable-only even though the same gate required immutable release evidence.
- The first session-end check did not discover the valid receipt because its
  parser requires the receipt path on the same line as the bold label.
- The first staged diff check exposed trailing Markdown hard-break spaces in
  the new plan; earlier unstaged `git diff --check` did not inspect that
  untracked file.

### Root causes and resolutions

- Confirmed root cause: `session start` is intentionally a writing command,
  but it was invoked before the fresh worktree had been created. Resolution:
  inspect the exact primary diff, remove only the generated skeleton, verify
  primary returned clean, then create and bind the fresh lane before invoking
  it again. Recurrence guard: run `session brief` during read-only orientation
  and defer `session start` until the intended lane reports `READY_LOCAL`.
  ⚠️ TERMINAL ISSUE: session start wrote a skeleton on primary `main` -> exact
  generated block removed after diff inspection; the command succeeded in the
  source-bound task worktree.
- Confirmed root cause: the pilot covers live workflows added or exercised
  after the historical remediation packet and reveals no single canonical
  project-input boundary. Resolution: retain `LIB-PRO-001` unchanged and create
  `LIB-PRO-002` with new IDs, explicit compatibility policy, and route-level
  ownership.
- Confirmed root cause: present gates emphasize valid/happy paths and component
  calculations, so they can remain green while callers substitute or discard
  data before calculation. Resolution: freeze a cross-surface negative matrix,
  row/field conservation rules, executable exact-wheel examples, and
  publication holds before code changes. Evidence: the plan maps each live
  confirmed path to one packet and makes Packet G the cumulative release gate.
- Confirmed root cause: the old standalone frontmatter checker is archived and
  the maintained command is `scripts/check_docs.py --frontmatter --json`.
  Resolution: locate the current implementation with `rg --files`, use the
  unified checker, and retain `./run.sh find` plus `rg --files` as the discovery
  sequence. Evidence: the maintained documentation check passes with zero
  invalid frontmatter. ⚠️ TERMINAL ISSUE: guessed a retired standalone
  frontmatter path -> discovered and used the unified checker.
- Confirmed root cause: the issue register, Alpha gate, and stable gate used
  individually reasonable wording but had not been cross-checked as one claim
  matrix. Resolution: name the Alpha review as independent exact-head
  software/release-evidence review, state that it is not qualified engineering
  review, and promote replay/source identity `PROV-01` to the Alpha gate.
  Evidence: both bounded reviewers accepted the remaining plan and identified
  only these minimal corrections for exact-candidate reconciliation.
- Confirmed root cause: the session log followed several older two-line receipt
  examples, but `_parse_git_receipt_path()` recognizes only a same-line path.
  Resolution: place the validated receipt path on the label line and rerun
  session end. Evidence: the repaired checker must report the receipt and its
  expected pre-commit HOLD. ⚠️ TERMINAL ISSUE: session end reported a missing
  receipt -> matched the maintained same-line parser contract.
- Confirmed root cause: authoring used two-space Markdown line breaks, and Git's
  unstaged diff does not include untracked files. Resolution: remove trailing
  whitespace mechanically and require intended-path staging before the final
  `git diff --cached --check`. Evidence: the cached diff check must be clean
  before commit. ⚠️ TERMINAL ISSUE: staged diff check rejected trailing spaces
  -> normalized the new plan and refreshed only affected indexes.

### Validation through content freeze

- Startup evidence: fetched base equality at
  `904a2f8cf0ea5d4595f57c46dac06e2e837bba45`, fresh linked lane, no operation
  marker, and `source_bound=true` before intended edits.
- Live inspection confirmed service defaults and `D-cover-8`, import-model
  defaults and `D-cover-25`, React 25/500/40 defaults, first-match adapter
  selection, invalid-row/force fallback behavior, and the maintained unsafe
  slab review phrase/test.
- Both bounded reviewers returned `ACCEPT` after the Alpha review type was made
  explicit and `PROV-01` was promoted into the Alpha gate.
- The pre-commit Git handoff receipt validates as an expected `HOLD` with local
  dirty, remote/PR, and exact-head review evidence still pending; it grants no
  authority and records the user-selected planning-only boundary.
- Planning metadata, links, affected indexes, quick gate, session-end contract,
  exact-head independent review, and normal commit hooks complete during
  candidate closeout.

### Timing through content freeze

- Orientation, prior-state reconciliation, and two bounded audits began on
  2026-08-17; final wall time including validation and closeout is reported in
  the external handoff.


## 2026-08-16 — Session: Index Local-Artifact Determinism Repair

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/index-local-artifact-determinism` from PR #810 merge
`755ed9d95c0a8f7e8c4a2165ddb748262df54482`

**Git handoff receipt:**
`docs/verification/post-india2-index-local-artifact-git-handoff-receipt.json`

**Focus:** Repair the one material post-merge defect found by primary-checkout
validation: checkout-local hidden artifacts changed recursive subfolder counts
and therefore the otherwise deterministic `docs/index.json` watermark.

### Summary

- Preserved both user-local editor swap files and every retained Git lane.
- Made recursive subfolder counts follow the scanner's existing top-level rule
  by excluding hidden files and hidden directory contents.
- Added a regression proving visible subfolder files remain hash-significant
  while `.swp` files and hidden editor directories do not affect counts or the
  freshness hash.
- Used one explicit repair candidate under the immutable closeout rule; no
  status-only update was appended to PR #810.

### Issues encountered

- After PR #810 merged with exact reviewed-tree equality, primary `main`
  reported only `docs/index.json` stale while a fresh detached worktree at the
  same tree reported 32/32 current.
- The first live-primary proof after excluding hidden paths restored the
  `planning` and `verification` counts but correctly differed from the old
  stored hash because the tracked hidden placeholder
  `docs/audit/reports/.gitkeep` also stopped contributing to `audit` count.

### Root causes and resolutions

- Confirmed root cause: direct-folder scanning excluded dot-prefixed files and
  directories, but recursive subfolder counting used unrestricted `rglob` and
  excluded only named cache/build directories. The primary checkout's ignored
  planning and verification `.swp` files increased those counts by one each.
  Resolution: reject any recursive file whose path relative to the subfolder
  contains a dot-prefixed component. Proof: the regression adds both a `.swp`
  and `.editor/state.json`; visible count and folder hash remain unchanged.
- Confirmed root cause: the first proof compared the new hidden-path semantics
  with the pre-repair stored hash, which still counted a tracked `.gitkeep`.
  Resolution: treat all hidden paths consistently as non-index content and
  perform one affected-index migration in the repair candidate. Proof: final
  evidence compares the migrated stored hash with a read-only scan of the real
  primary checkout containing both preserved swap files.

### Validation

- The three focused index-hash tests pass: visible subfolder changes remain
  significant; filesystem `mtime` and hidden local artifacts do not.
- Exact validation and immutable closeout requirements are recorded in
  `docs/verification/post-india2-index-local-artifact-evidence.json`.

### Timing

- Post-merge primary verification exposed the defect at approximately
  `2026-08-16T18:01:00Z`; root cause was confirmed within four minutes.

---

## 2026-08-16 — Session: Post-INDIA-2 Index Determinism Repair

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/index-mtime-determinism` from maintenance merge
`7541a7c768aee408e38bf8e7b4a1997469b0b9b1`

**Git handoff receipt:**
`docs/verification/post-india2-index-determinism-git-handoff-receipt.json`

**Focus:** Remove filesystem-time churn from maintained index freshness,
replace all-folder regeneration guidance with affected-folder refresh, and add
one read-only weekly drift audit without changing product, engineering,
dependency, release, or retained Git-lane state.

### Summary

- Made the index freshness watermark depend on repository content and structure
  while retaining `last_updated` only as observational display metadata.
- Added a regression that changes only a source file's filesystem timestamp and
  requires an unchanged folder freshness hash.
- Kept the existing docs/scripts structural guards because they validate real
  registry and link contracts; no all-folder freshness check existed in PR CI
  or pre-commit.
- Added one non-writing all-folder freshness audit to the existing Monday
  workflow and changed operator guidance to refresh only folders reported
  stale.
- Performed the one-time deterministic-hash migration for all 32 maintained
  indexes and bound the candidate to independent fresh-worktree validation.

### Issues encountered

- After PR #809 merged with a tree exactly equal to its reviewed candidate,
  the maintenance worktree reported 32/32 indexes current while primary
  `main` reported all 32 stale for the same Git tree.
- The existing closeout wording allowed agents to update versioned session,
  PR, hosted-check, or merge status after index generation or PR creation,
  creating a documentation-to-index-to-CI mutation loop.
- The first patch application could not match the decorative folder-scanner
  separator; no file changed in that failed attempt.
- The first focused Black check required one mechanical line-wrap change in
  the timestamp regression.

### Root causes and resolutions

- Confirmed root cause: file analyzers derive nested `last_updated` values from
  filesystem `mtime`, but the generator excluded only the top-level
  `last_updated` field from `content_hash`. A fresh linked worktree therefore
  produced a different freshness hash for byte-identical files. Resolution:
  recursively omit observational timestamps from the hash projection while
  retaining per-file content hashes and every deterministic structural field.
  Proof: the regression moves one unchanged Python file from 2020 to 2021,
  observes a changed display date, and observes an identical freshness hash.
- Confirmed root cause: the generator's stale-result message prescribed
  `--all`, encouraging repository-wide regeneration even when only one folder
  changed. Resolution: report all stale folders and explicitly require only
  those folders to be refreshed; agent guidance now separates the global
  read-only audit from focused writes.
- Confirmed root cause: the workflow required an immutable candidate but did
  not state the final mutation cutoff explicitly across all agent/session entry
  points. Resolution: freeze logs, task/handoff state, local evidence, and the
  pre-commit receipt first; refresh affected indexes once as the last repository
  write; keep later PR/CI/merge facts in GitHub and the external handoff. Proof:
  the canonical Git workflow, cross-agent instructions, session skill, and
  session-end prompt now carry the same ordered rule.
- Confirmed root cause: the failed patch used an inexact Unicode separator as
  context. Resolution: anchor the patch to function definitions and assertions.
  Proof: the intended implementation diff applies cleanly and the
  focused regression passes.
- Confirmed root cause: the handwritten multi-line assertion did not match the
  repository formatter's compact layout. Resolution: run Black on the one test
  file. Proof: Black, Ruff, and all 164 focused governance tests pass.

### Validation

- The focused content-hash tests pass, including timestamp independence and
  subfolder-projection sensitivity.
- Final evidence, exact counts, same-commit fresh-worktree proof, repository
  gates, and immutable handoff binding are recorded in
  `docs/verification/post-india2-index-determinism-evidence.json`.

### Timing

- Root-cause investigation began during maintenance closeout at approximately
  `2026-08-16T17:44:00Z`; bounded repair work began at approximately
  `2026-08-16T17:47:00Z`.

---

## 2026-08-16 — Session: Post-INDIA-2 Maintenance

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/post-india2-maintenance` from cleanup-execution merge
`3b08a9c1a0471dea86ac36e7a0ca1e03b045b82e`

**Git handoff receipt:** `docs/verification/post-india2-maintenance-git-handoff-receipt.json`

**Focus:** Complete only `MAINT-010-POST-INDIA2`: generated-truth refresh,
history compaction, completed-plan archival, feedback verification, and
review-only monthly evolution without product, engineering, dependency,
release, or additional Git-cleanup behavior.

### Summary

- Refreshed five stale generated count occurrences across four maintained
  guidance files; a repeated session-sync scan reports zero updates.
- Inspected the exact 32-folder index target set, ran one full live generation,
  and retained only deterministic generated-index changes.
- Compacted 107 parsed session entries to ten live plus 97 month-partitioned
  archives. Full-body multiset hashing proved no missing or duplicate entry;
  the final maintenance entry is compacted under the same ten-entry limit.
- Kept exactly 20 recent completed task rows, moved 49 older rows intact into
  `docs/_archive/tasks-history.md`, and preserved current release, no-active-
  task, INDIA-2 closeout, pile-cap HOLD, and raft HOLD truth.
- Used individual safe-move dry runs and live moves to archive the deprecated
  agent-evolver plan and completed post-v0.20 maintenance plan. The Git-
  hardening plan was already archived during Phase A, and `_active` now reports
  no active multi-session plans.
- Confirmed feedback is already clean, made no tester-instruction change, and
  ran the overdue monthly evolution in preview/review-only mode with no report
  or automated mutation.

### Issues encountered

- The planning snapshot expected 105 session entries, two pending feedback
  items, and three active plans. Live state had 107 entries, zero feedback
  items, and only two active plans because Phase A already archived the Git-
  hardening plan.
- ⚠️ TERMINAL ISSUE: the first two safe-move dry runs failed with
  `env: bash: No such file or directory`; no file moved.
- ⚠️ TERMINAL ISSUE: the first independent task-row hash report used a literal
  backslash-n separator, so its displayed digest differed from the mover's
  newline-delimited digest even though row counts and uniqueness passed.
- Repeating compaction after adding this maintenance entry preserved all 108
  session bodies but rebuilt `logs/session_index.json` as only 11 total / one
  archived entry, omitting the prior 97 archive rows from the index.
- The first new compaction regression stopped in its temporary fixture because
  the status printer could not express an archive path outside `REPO_ROOT`.
- The first final 32-folder index check found four stale indexes after the
  planned live generation pass.
- The first focused Black check required a mechanical layout change in the new
  archive-reader call.
- The first commit attempt was blocked before commit because the 91-entry
  August archive was 521,084 bytes, above the 500 KB added-file gate.

### Root causes and resolutions

- Confirmed root cause: the cleanup audit and execution added two new session
  records after the planning snapshot; Phase A advanced one explicitly
  authorized plan archival; the feedback ledger had already been resolved on
  merged `main`. Resolution: reconcile to live state, retain the latest ten and
  archive the actual remaining 97, skip already-complete feedback/plan actions,
  and preserve all feedback holds. Proof: session body hash/counts, feedback
  summary, and `_active` inventory are recorded below.
- Confirmed root cause: in zsh, the loop variable `path` is tied to the special
  `PATH` array; assigning the destination filenames to it temporarily removed
  `bash` from executable lookup. Resolution: stop, avoid the reserved variable,
  and invoke the worktree-bound Python launcher normally. Proof: both repeated
  dry runs and both live safe moves completed with zero broken links.
- Confirmed root cause: the read-only verifier encoded `\\n` rather than an
  actual newline when independently rebuilding the task-row digest. Resolution:
  use `chr(10)` as the delimiter. Proof: the corrected independent SHA-256
  `fda1896831fba820dc54d540e3b50b333f16203418b2c67ef6b65c376728b67e`
  exactly matches the mover's pre-write digest; all 68 original rows were
  present once before adding MAINT-010 and rotating the twentieth row.
- Confirmed root cause: `cmd_compact` rebuilt the session index from live
  entries plus only the entries archived in the current invocation; it never
  re-read existing monthly archives. Resolution: add one archive reader and use
  its complete parsed result in both the compaction and no-op index paths.
  Proof: the recurrence test passes and the repaired live index reports 108
  total, ten live, and 98 archived entries, matching the files on disk.
- Confirmed root cause: the new test monkeypatched the log/archive paths but
  left `REPO_ROOT` pointed at the real checkout. Resolution: bind all four
  repository paths to the temporary fixture. Proof: the exact test then passes
  without touching workspace archives.
- Confirmed root cause: the first live index generation preceded the newly
  required compactor repair/test, final handoff evidence, and next-session
  brief; those legitimate later writes changed the four indexed folders.
  Resolution: run one maintained corrective all-folder generation after content
  freeze. Proof: the repeated check reports all 32 indexes current.
- Confirmed root cause: the manually wrapped function call did not match the
  repository's Black layout. Resolution: format only `scripts/session.py` and
  regenerate its maintained index. Proof: Black and Ruff pass on the changed
  script and regression file, and all 32 indexes remain current.
- Confirmed root cause: strict one-file-per-month grouping did not account for
  the repository's per-file size ceiling, and the session index assumed every
  archived entry lived in the unnumbered monthly file. Resolution: shard a
  month into bounded parts below 480,000 bytes, preserve/parse all existing
  bodies before rewriting, and attach the actual archive path to each indexed
  entry. Proof: the commit hook stopped without a commit; August now occupies
  two files of 475,805 and 45,322 bytes, the pre/post body multiset hash is
  equal with zero duplicates, and the 108-row index names both parts.

### Validation

- Session compaction proof initially reports 107 total entries, ten live, 97
  archived, no duplicate bodies, and exact pre/post full-body multiset hash
  `90e50dc5a5a10f36e5b4deef4f4def26f1bef72c53de19a9efc52a2102567659`.
- Final proof after adding this entry reports 108 total entries, ten live, 98
  archived, zero duplicate bodies, and an unchanged pre/post multiset hash;
  the stable digest is stored outside the hashed session bodies in the
  maintenance evidence record, and the rebuilt index carries the same
  108/10/98 counts with actual part paths.
- Task compaction reports 20 unique live rows and 49 intact older rows in the
  new archive section after adding MAINT-010; closeout and both foundation HOLD
  IDs remain live. The task-format checker passes.
- All 163 focused tests in `test_agent_governance_automation.py`,
  `test_session_automation.py`, and `test_branch_disposition.py` pass,
  including the targeted index-generator write-scope regressions.
- Generated-number sync reports zero pending updates, and the corrective final
  index check reports 32/32 current.
- Health is 100/100 with zero issues; audit passes 19/19; parity remains 13
  supported / 8 held and 81/81 endpoints directly tested. Monthly evolution
  review completes in preview mode and feedback summary reports no pending
  items. Links validate all 1,319 internal references with zero broken links;
  strict metadata passes; the quick gate passes 10/10 and the full gate passes
  30/30 in 10.9 reported seconds. After the compactor repair and Black pass,
  all 163 focused tests, 32/32 indexes, links, quick 10/10, and full 30/30
  repeat green; the final full gate reports 11.3 seconds. Immutable-head,
  hosted, and merge-tree gates remain before integration.

### Timing

- Clean/source-bound maintenance orientation began at approximately
  `2026-08-16T17:24:00Z`.
- Count/index refresh, both compactions, safe archival, feedback reconciliation,
  review-only evolution, root-cause repair, and local validation completed in
  approximately 12 minutes.
- Final validation, hosted CI wait, merge closeout, and cumulative workflow time
  are recorded after the immutable candidate is integrated.

---

## 2026-08-16 — Session: Post-INDIA-2 Cleanup Execution

**Agent:** Codex (`ops`, sole writer)

**Branch:** `codex/post-india2-cleanup-execution` from audited merge
`cbe10638fcba3f8919f8776462af34247b0604d0`, tree
`83804f8c3af4edcc7454c8f916e4f0fb3ca36231`

**Git handoff receipt:** `docs/verification/post-india2-cleanup-execution-git-handoff-receipt.json`

**Focus:** Execute only frozen candidate set
`POST-INDIA2-2499DF4ADE0DF704`, preserve every audit hold/exclusion, and publish
an action-level receipt with exact identities and postconditions.

### Summary

- Revalidated all 193 frozen actions against the audited merge, current local
  and GitHub refs, open pull requests, worktree states, protected branches, and
  held lanes before mutation.
- Removed exactly 58 clean inactive worktrees, 64 detached local branches, and
  71 remote branches; every action was immediately checked and recorded.
- Recovered 8,388,911,104 bytes from worktree surfaces, exactly matching the
  audited estimate; no force option, prune, reset, stash, history rewrite, PR
  closure, issue closure, or non-candidate deletion was used.
- Preserved 17 held/excluded union branches, including dirty detached `e54a`,
  Excel, `gh-pages`, all seven open Dependabot heads, and every detached,
  mismatched, owner-unknown, or integration-unknown lane.
- Final state has 11 worktrees, 8 local branches, and 16 remote branches. The
  receipt proves every candidate worktree/local/remote surface absent and every
  required protection postcondition true.

### Issues encountered

- After all 58 worktrees were removed, the first local-branch classification
  stopped before deletion because 28 squash-integrated branches were reported
  as `HOLD_UNIQUE_OR_UNPUBLISHED_WORK` with
  `UNIQUE_COMMITS_OR_PATCHES`. No local or remote branch had yet been deleted.
- ⚠️ TERMINAL ISSUE: a read-only `jq` projection assumed the worktree list was
  nested under a second `worktrees` key; the projection failed after the
  independent exact-tree assertion had already passed.
- ⚠️ TERMINAL ISSUE: the first semantic-workflow command guessed the obsolete
  direct path `scripts/check_git_workflow_semantics.py`; metadata passed, but
  the chained command stopped before the quick gate.
- The first session-end check accepted the session content but reported that
  the action receipt was not declared as a task-to-Git handoff contract.

### Root causes and resolutions

- Confirmed root cause: the inspection-only classifier intentionally treats
  commit/patch ancestry as a hold, while a multi-commit PR that was squash
  merged can retain unique commits/patches even when its complete head tree is
  byte-for-byte equal to the reachable merge tree. Resolution: stop closed,
  preserve the 58 completed removals in the receipt, then resume only after
  rechecking exact local/remote heads, selected PR identity, equal branch and
  merge trees, and merge-commit reachability for every named exception. Proof:
  the receipt binds 56 conservative classifier exceptions to those exact facts,
  all 193 actions are `REMOVED`, and all candidate refs are absent.
- Confirmed root cause: `git_state.py --json --worktrees` emits `worktrees` as a
  top-level array. Resolution: query its actual shape and repeat the read-only
  counts. Proof: the corrected projection reports 11 worktrees and no inventory
  query failures; no mutation occurred in either command.
- Confirmed root cause: semantic Git-workflow validation is maintained as
  `scripts/check_codex_git_workflow.py`. Resolution: discover it with
  `./run.sh find` and invoke that maintained path. Proof: the semantic check and
  the repeated quick gate pass.
- Confirmed root cause: the action-level cleanup receipt proves deletion and
  preservation outcomes but intentionally does not implement the repository's
  task-to-Git handoff schema. Resolution: generate the separate fail-closed
  handoff receipt from `git_state.py` plus fresh owner-authority evidence and
  declare its path on one line in this entry. Proof: the maintained receipt
  validator returns `CLEAN-001-POST-INDIA2-PHASE-B | HOLD`, and the repeated
  session-end check must discover it.

### Validation

- Receipt invariant checks pass: candidate-set hash is unchanged; 193/193
  actions are removed; failed actions are zero; expected and observed recovery
  are equal; all candidate absence flags and protection postconditions are true.
- `Python/tests/test_branch_disposition.py` and
  `Python/tests/test_git_state.py` pass all 89 focused tests.
- `scripts/check_links.py` validates 1,317 internal links with zero broken
  links; strict metadata, the maintained semantic Git-workflow check, and the
  targeted `docs/verification` index hash check pass.
- `./run.sh check --quick` passes 10/10 and `./run.sh check` passes 30/30 in
  11.7 reported seconds. Immutable-candidate audit, hosted checks, and
  post-merge tree comparison remain before Phase B integration.

### Timing

- Execution preflight began at `2026-08-16T16:42:32Z`.
- The fail-closed first pass removed worktrees through
  `2026-08-16T16:56:34Z`; root-cause confirmation and the independent resume
  boundary took about 4 minutes.
- Local and remote deletion completed at `2026-08-16T17:17:09Z`; focused
  postcondition validation completed by `2026-08-16T17:18:43Z`.

---

## 2026-08-16 — Session: Post-INDIA-2 Cleanup Audit

**Agent:** Codex (`ops`, sole writer)

**Branch:** `codex/post-india2-cleanup-audit` from freshly fetched
`origin/main = d8202fef2566cd4955b2ba041914ff318d15d043`

**Focus:** Build one inspection-only union inventory of every pre-existing
worktree, local branch, GitHub branch, and associated pull-request integration
receipt. Freeze exact cleanup candidates and holds without removing any Git or
filesystem surface in Phase A.

### Summary

- Verified the fresh default anchor, clean primary, `source_bound=true`,
  `READY_LOCAL`, exact base equality, and no operation marker before writing.
- Inventoried 67 pre-existing worktrees, 70 pre-existing local branches, and 86
  GitHub branches; the audit lane raises the live local totals to 68 worktrees
  and 71 branches while the packet is active.
- Bound PR heads, submitted-review heads, merge commits, branch/merge trees,
  live owners, remote/API identities, open dependencies, worktree state, and
  disk estimates for every union member.
- Froze candidate set `POST-INDIA2-2499DF4ADE0DF704`: 71 evidence-complete
  branches and 193 separately bound worktree/local/remote actions, with about
  7.8 GiB recoverable only from the 58 worktree surfaces.
- Retained `main`, dirty detached `e54a`, `gh-pages`, the current audit lane,
  and Dependabot-managed refs; held Excel, all detached lanes, every mismatch,
  and every owner/integration-unknown branch.
- Performed no worktree removal, branch/ref deletion, prune, PR/issue closure,
  stash operation, history rewrite, release, or cleanup mutation in Phase A.

### Issues encountered

- ⚠️ TERMINAL ISSUE: immediately after `git worktree add`, the first runtime
  diagnosis and session command still ran from the primary checkout.
- The inherited planning snapshot said there were no open PRs, while the live
  GitHub query found seven open Dependabot PRs.
- The first full evidence-generator pass failed when it treated the nullable
  `mergeCommit` field on an open PR as an object; no partial artifact was
  produced.
- The first strict documentation metadata check rejected the new proposal's
  noncanonical `doc_type: verification` value.
- The first commit attempt was blocked by the 500 KB added-file limit because
  the evidence JSON repeated classifier inputs/outputs already present in the
  union rows; no commit was created.
- The first full repository gate passed 29/30 and failed only the hard
  documentation budget: the required proposal raised the non-archived count
  from the existing limit of 400 to 401.
- ⚠️ TERMINAL ISSUE: the first exact-commit invariant command used escaped
  quotes inside an f-string expression and stopped with `SyntaxError`; the
  committed candidate and repository were unchanged.

### Root causes and resolutions

- Confirmed root cause: creating a worktree does not change the caller's
  process working directory. Resolution: rerun diagnosis and every evidence or
  validation command with the audit path as the explicit working directory.
  Proof: runtime diagnosis resolves `structural_lib` under the audit lane and
  reports `source_bound=true`; `git_state.py` reports `READY_LOCAL` there.
- Confirmed root cause: GitHub state changed after the planning snapshot.
  Resolution: use fresh branch API, `ls-remote`, and all-state PR observations;
  all seven open heads are Dependabot-managed and remain excluded. Proof: the
  JSON packet reports seven open PRs and zero non-Dependabot open PRs.
- Confirmed root cause: GitHub represents an unmerged PR with
  `mergeCommit: null`, not an empty merge object. Resolution: normalize the
  nullable field before reading its OID and rerun the complete union build.
  Proof: the regenerated JSON parses and every candidate has an
  exact equal branch/merge tree reachable from current `origin/main`.
- Confirmed root cause: the content category was incorrectly reused as a
  metadata type. Resolution: keep the artifact in `docs/verification/` but use
  canonical `doc_type: reference`. Proof: the repeated strict metadata check
  passes.
- Confirmed root cause: the indented evidence serialized the same remote, PR,
  worktree, and classifier fields up to three times. Resolution: deduplicate
  projections, retain all decision-bearing classifier identities/facts, and
  use compact JSON. Proof: the artifact is 329,393 bytes, its candidate-set
  hash remains `POST-INDIA2-2499DF4ADE0DF704`, and all invariant checks pass.
- Confirmed root cause: `origin/main` was already at the 400-document ceiling,
  while this packet requires a new non-archived Markdown proposal. Resolution:
  advance one already-authorized maintenance action: dry-run then safely move
  the explicitly superseded Git-hardening plan to `docs/_archive/planning/`,
  update its maintained links, and reconcile `_active/README.md` to two plans.
  Proof: the safe mover preserves zero broken links; the corrective full gate
  must accept the restored 400-document count.
- Confirmed root cause: Python forbids backslashes inside f-string expression
  segments. Resolution: compute `head` and `tree` before formatting the line.
  Proof: the repeated committed-data audit passes at head `4240cc12`, tree
  `321fb684`, candidate set `POST-INDIA2-2499DF4ADE0DF704`, and 193 actions.

### Validation

- JSON syntax and invariant assertions pass for counts, protected exclusions,
  owner evidence, remote/API SHA equality, exact squash-tree equality, current-
  main reachability, and complete worktree action identities.
- `Python/tests/test_branch_disposition.py` and
  `Python/tests/test_git_state.py` pass all focused tests.
- `scripts/check_links.py` passes 1,319 internal links with zero broken links;
  strict metadata and semantic Git-workflow checks pass.
- Targeted `docs/verification` dry-run, live generation, and hash check pass;
  the maintained index advances from 141 to 143 files.
- Initial and final `./run.sh check --quick` runs pass 10/10.
- Immutable-candidate inspection, the full repository gate, exact-head hosted
  checks, and post-merge tree comparison remain before Phase A integration.

### Timing

- Orientation and live-state reconciliation started at approximately
  `2026-08-16T16:22:00Z`.
- Inventory/evidence implementation and first corrective passes took about 14
  minutes through the initial focused validation boundary.
- Hosted CI wait, Phase A closeout, and total elapsed workflow time are recorded
  in the cleanup execution receipt after the audit packet merges.

---

## 2026-08-16 — Session: INDIA-2 Final Closeout

**Agent:** Codex (`reviewer`, sole writer)

**Branch:** `codex/india-2-closeout` from freshly fetched
`origin/main = d28852156752ea6e44b0c9fbb67988088851bf3e`, tree
`38958c8a484d5f63a1092b2e852af64bef7afc2a`

**Git handoff receipt:** `docs/verification/india-2-closeout-git-handoff-receipt.json`

**Focus:** Administratively close INDIA-2 around six accepted bounded families
and explicit pile-cap/raft holds. Freeze one cumulative evidence index, pass
the broad Python suite and full repository gate, and publish without adding
calculation, service, API, React, capability, release, cleanup, or professional-
approval behavior.

### Summary

- Verified the exact fresh base, `source_bound=true`, `READY_LOCAL`, no Git
  operation marker, and a clean one-writer linked worktree before editing.
- Reconciled the task board, parent/dedicated plans, and next-session brief to
  the final INDIA-2 accepted/held boundary.
- Added one durable evidence index linking source, benchmark, publication,
  focused acceptance, PR/merge, tree, and Git receipt evidence for all six
  accepted families.
- The first broad Python run exposed 11 stale downstream contracts from the
  exact stress-block correction. Replayed the values independently and repaired
  only the affected tests/golden data; production calculation code is unchanged.
- The first full repository gate exposed the public API manifest still at 160
  symbols after the already-integrated strap Python workflow raised the actual
  public surface to 165. Regenerated only the maintained manifest.
- Bound pile-cap PR #804 and raft PR #805 as explicit G0 holds with no
  implementation and retained their exact reactivation contracts.
- Preserved generated truth at 13 supported / 8 held and 81/81 directly tested
  endpoints; no executable or capability-promotion file changed.

### Issues encountered

- The status projections intentionally still named `INDIA-2-CLOSEOUT` as next
  after raft G0 merged, so umbrella INDIA-2 could not yet be reported complete.
- The first broad Python run failed 11 tests: five beam golden cases, two
  footing golden cases, three isolated-footing/detailing cases, and one obsolete
  branch-coverage case still expected the pre-PR-#803 rounded inverse/clamp.
- The first full repository gate passed 29/30 and failed only API-manifest
  determinism because all five strap public exports were absent from the
  generated reference artifact.
- The first candidate Black check required a mechanical layout change in the
  rewritten stress-block domain-guard test.
- ⚠️ TERMINAL ISSUE: the first read-only commit/tree inspection loop assumed
  POSIX word splitting for quoted rows; zsh kept each row as one value and Git
  received an empty revision.
- ⚠️ TERMINAL ISSUE: one read-only status search used an unmatched shell glob;
  zsh stopped that command before `rg` ran.
- ⚠️ TERMINAL ISSUE: the first index-help lookup used the obsolete filename
  `scripts/generate_folder_indexes.py`; the interpreter reported that the file
  does not exist and made no changes.
- ⚠️ TERMINAL ISSUE: the first read-only diagnostic serializer did not provide
  an enum fallback to `json.dumps`; it stopped on `DesignSectionType` before
  printing the requested values and made no changes.
- ⚠️ TERMINAL ISSUE: the first `./run.sh session end --agent reviewer` could
  not discover the valid closeout receipt because its path was wrapped onto the
  line after the `Git handoff receipt` label.

### Root causes and resolutions

- Confirmed root cause: family/G0 packets correctly deferred umbrella status,
  cumulative gates, and the final evidence index to this dedicated closeout
  packet. Resolution: link all immutable family receipts in one closeout
  record, mark only the bounded INDIA-2 wave complete, and keep both held
  foundations and all post-INDIA-2 authority boundaries explicit. Evidence:
  final document, link, manifest/parity, broad Python, full repository, quick,
  exact-head, and hosted checks pass.
- Confirmed root cause: PR #803 deliberately replaced the approximate rounded
  inverse with shared exact Clause 38.1/Annex G equilibrium, but its focused
  selection did not include older broad beam golden vectors or isolated-footing
  expectations that consume the same helper. One coverage test also described
  the removed clamp instead of the exact solver's fail-closed domain guard.
  Resolution: independently replay the exact quadratic at high precision,
  update only the affected Ast/xu/pt/downstream shear expectations, and rewrite
  the obsolete coverage test to require `ValueError` outside the rectangular
  stress-block domain. Evidence: all 88 affected focused tests pass; the broad
  rerun is the cumulative acceptance proof.
- Confirmed root cause: strap publication PR #796 added four public types and
  one workflow but did not regenerate `docs/reference/api-manifest.json`; the
  later D and focused-acceptance packets validated Indian-code/OpenAPI truth,
  not this broad public-symbol artifact. Resolution: run the maintained API
  manifest generator and accept only its five-symbol 160-to-165 diff. Evidence:
  direct manifest check and focused API-manifest tests pass; the corrective full
  gate rerun is the repository-wide acceptance proof.
- Confirmed root cause: the manually wrapped `pytest.raises` call did not match
  Black's canonical layout. Resolution: run repository-bound Black on that one
  test file. Evidence: Black check, Ruff, and the exact domain-guard test pass.
- Confirmed root cause: zsh does not perform the assumed implicit word
  splitting on scalar expansions. Resolution: encode each row as
  `name:revision` and split it with zsh parameter expansion. Evidence: all nine
  requested commit/tree pairs resolved exactly; no files changed during the
  failed or corrected read-only commands.
- Confirmed root cause: zsh rejects unmatched globs before invoking a command.
  Resolution: use exact maintained paths or discover candidates with
  `rg --files` before filtering. Evidence: the subsequent targeted status and
  frontmatter searches completed; the worktree diff remained limited to the
  closeout documentation set.
- Confirmed root cause: the maintained index generator is named
  `scripts/generate_enhanced_index.py`; the attempted plural filename was an
  unverified recollection. Resolution: run `./run.sh find "generate folder
  indexes"` before invoking the maintained command. Evidence: repository
  discovery returned the exact generator and its help completed successfully.
- Confirmed root cause: dataclass serialization included an enum that standard
  `json.dumps` cannot encode. Resolution: add `default=str` to the read-only
  diagnostic serializer. Evidence: the corrected command printed all beam,
  footing, service, and detailing values without repository mutation.
- Confirmed root cause: the session checker intentionally parses a receipt path
  only when it appears on the same line as its label. Resolution: use the
  established one-line declaration. Evidence: direct receipt validation and
  the repeated session-end check both accept the same committed receipt.

### Validation

- First `./run.sh test`: 6,301 passed, 11 failed, 3 skipped, 6 deselected in
  55.21 seconds; this is diagnostic evidence, not acceptance.
- Focused repair selection: 88 passed after independently replaying the exact
  stress-block and downstream values.
- Corrective broad `./run.sh test` rerun: 6,312 passed, 3 skipped, 6 deselected,
  and 46 warnings in 50.59 seconds (51.98 seconds wall time).
- First `./run.sh check`: 29/30 passed; only API manifest failed because the
  five integrated strap exports were absent.
- Corrective `./run.sh check` rerun: 30/30 passed in 11.0 seconds (3.16
  seconds wall time); API, docs, architecture, governance, FastAPI, Git, stale-
  reference, and code-quality groups are all green.
- Focused frontmatter, links, manifest, parity, folder-index, and quick-gate
  results are recorded after the human-owned closeout content is frozen.
- Required hosted checks must pass on the unchanged reviewed head before merge.

### Timing

- Orientation and exact Git/runtime verification: approximately 3 minutes.
- Evidence-chain sampling and final truth reconciliation: approximately 9
  minutes before cumulative validation.
- Initial plus corrective broad validation and focused repair: approximately 4
  minutes. First full gate plus API-manifest repair: approximately 2 minutes.
  Corrective full validation: 11.0 reported seconds. Candidate audit, hosted CI
  wait, closeout, and total elapsed time are reported in the final handoff.

## 2026-08-16 — Session: INDIA-2 Foundation Raft G0

**Agent:** Codex (`structural-engineer`, sole writer)

**Branch:** `codex/india-2-foundation-raft-g0` from freshly fetched
`origin/main = def0b493e33fa566fd3f23bf166287fcda6169d6`, tree
`7da91c66143e83933a88bb9a4d5396bede89cf6d`

**Git handoff receipt:**
`docs/verification/india-2-foundation-raft-g0-git-handoff-receipt.json`

**Focus:** Decide whether exactly one regular rectangular rigid raft can be
source-bound and independently benchmarked. Publish `HOLD` with exact
reactivation conditions if either prerequisite is absent. Do not create
calculation, service, API, React, release, cleanup, or retirement work.

### Summary

- Verified the exact fresh base, `source_bound=true`, `READY_LOCAL`, no Git
  operation marker, and a clean one-writer linked worktree before editing.
- Reconfirmed the controlled IS 456 source hashes and found no retained IS
  2950 or other raft companion source.
- Verified official BIS discovery: IS 2950 (Part 1):1981 is active, reaffirmed
  2023 with one amendment, and its preview covers conventional rigid and
  simplified flexible methods for mainly vertical/evenly distributed loads.
- Verified that IISc/NPTEL describes a relevant conventional rigid-mat model,
  but neither that chapter nor the located question set supplies a complete,
  independently replayable structural raft benchmark.
- Returned `HOLD`, retained the regular rigid-raft candidate, and created no
  numeric design result or raft calculation/publication file.
- Made the hold machine-visible in the generated manifest with a direct
  regression and reconciled the task board/plans/brief to name cumulative
  `INDIA-2-CLOSEOUT` next.

### Issues encountered

- The required controlled IS 2950 source/amendment binding and structural raft
  benchmark were absent, so the conventional rigid candidate could not be
  activated or verified through strength/detailing.
- The public material initially appeared promising because it included both a
  conventional analysis procedure and a raft-design question, but it did not
  include the complete worked structural result set required by G0.

### Root causes and resolutions

- Confirmed root cause: the repository-controlled source registry contains
  only IS 456:2000 through Amendment 5 and Amendment 6. The BIS catalogue and
  preview prove IS 2950 discovery/scope but are not a committed authenticated
  source/amendment identity. Resolution: publish `HOLD`, preserve
  `HELD / NOT_IMPLEMENTED`, and require the exact standard/amendment hashes
  before reactivation. Evidence: the decision record binds current official
  discovery separately from the controlled-source inventory.
- Confirmed root cause: the NPTEL chapter defines a rigid planar-pressure/
  whole-mat method, while the question set asks for a raft design without an
  accepted solution; neither closes the requested pressure, equilibrium,
  orthogonal actions, flexure, shear, reinforcement, or anchorage values.
  Resolution: retain the candidate but treat conceptual procedure and unsolved
  prompts as non-benchmarks. Evidence: the G0 record lists the missing
  intermediates and a five-part reactivation contract.

### Validation

- `./scripts/python_runtime.sh -m pytest Python/tests/test_indian_code_manifest.py -q`:
  `10 passed`.
- `./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check`:
  current; raft is `HELD / NOT_IMPLEMENTED`, has no workflow, and cites the G0
  hold evidence.
- `./scripts/python_runtime.sh scripts/check_docs.py --frontmatter --json`:
  345 scanned, 285 with frontmatter, 60 permitted legacy records, zero invalid.
- `./scripts/python_runtime.sh scripts/check_links.py`: 1,277 internal links,
  zero broken.
- `./run.sh efficiency check`: pass.
- Black and Ruff on the two owned Python files: pass.
- `./run.sh parity`: 13 supported / 8 held, 81/81 endpoints directly tested,
  and 13/13 React hooks connected.
- `./run.sh check --quick`: `10/10` pass.

### Timing

- Orientation/source/Git inspection and public evidence verification:
  approximately 3 minutes.
- Decision record, truth reconciliation, and focused validation before
  candidate closeout: approximately 2 minutes.
- Hosted CI wait, closeout, and total elapsed: record after merge.

## 2026-08-16 — Session: INDIA-2 Foundation Pile-Cap G0

**Agent:** Codex (`structural-engineer`, sole writer)

**Branch:** `codex/india-2-foundation-pile-cap-g0` from freshly fetched
`origin/main = 1139e9ea06751c72b66098a575c1f5e327c56ef5`, tree
`0abefcd0255157bd1444549f2066eb937f45e5a0`

**Git handoff receipt:**
`docs/verification/india-2-foundation-pile-cap-g0-git-handoff-receipt.json`

**Focus:** Decide whether exactly one centred axial two-pile structural cap can
be source-bound and independently benchmarked. Publish `HOLD` with exact
reactivation conditions if either prerequisite is absent. Do not create
calculation, service, API, React, release, cleanup, or retirement work.

### Summary

- Verified the exact fresh base, `source_bound=true`, `READY_LOCAL`, no Git
  operation marker, and a clean one-writer linked worktree before editing.
- Reconfirmed the controlled IS 456 source hashes and found no retained IS
  2911 or other pile-cap companion source.
- Searched existing code, tests, evidence, official BIS discovery surfaces,
  and primary NPTEL material. No pile-cap implementation or accepted,
  independently replayable structural two-pile-cap benchmark exists.
- Returned `HOLD`: neither a footing critical-section analogy nor generalized
  strut-and-tie model has enough authority to activate. No numeric design
  result and no pile-cap calculation/publication file was created.
- Made the hold machine-visible in the generated manifest with a direct
  regression and reconciled the task board, both INDIA-2 plans, and the compact
  brief to name decision-only raft G0 next.

### Issues encountered

- The required controlled IS 2911 companion source and structural two-pile-cap
  benchmark were absent, so the candidate could not select or verify a
  structural action model.
- The linked worktree has no `private_sources/` directory because the retained
  controlled sources are ignored and live only under the primary checkout.
- ⚠️ TERMINAL ISSUE: the first source-inventory command used the worktree-local
  `private_sources` path and failed; a later `shasum` glob also included
  directories and reported them as invalid hash targets.
- ⚠️ TERMINAL ISSUE: one multi-section documentation patch used a stale line-
  wrapping context and applied nothing.
- The first Black check found the added manifest regression needed mechanical
  formatting.
- The all-folder index generator also refreshed modification dates in unrelated
  folders because linked-worktree file mtimes are current even when content is
  unchanged.

### Root causes and resolutions

- Confirmed root cause: the repository-controlled source registry contains
  only IS 456:2000 through Amendment 5 and Amendment 6; official IS 2911
  catalogue/preview pages are discovery evidence, not controlled
  implementation inputs. The benchmark search found pile-group/geotechnical
  material and a course syllabus, not a complete structural cap example.
  Resolution: publish `HOLD`, preserve `HELD / NOT_IMPLEMENTED`, and require an
  authenticated controlled companion source plus a replayable benchmark before
  reactivation. Evidence: the G0 decision record inventories the sources,
  compares both candidate models, and states five exact reactivation gates.
- Confirmed root cause: ignored controlled-source material is intentionally not
  populated in linked worktrees. Resolution: inspect the primary checkout's
  retained private-source registry by absolute path without mutation and hash
  the two exact PDF paths. Evidence: SHA-256 values reproduce as
  `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`
  and `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`.
- Confirmed root cause: the inventory/hash commands assumed worktree-local
  ignored files and then used a directory-bearing wildcard. Resolution: use
  the verified absolute primary registry and exact file targets. Evidence: the
  corrected inventory and both hashes completed successfully.
- Confirmed root cause: the failed patch copied a nearby sentence without its
  exact preceding line wrap. Resolution: inspect the target ranges and apply
  smaller exact-context hunks. Evidence: the plans now record pile-cap HOLD and
  identify raft G0 as next; `git diff --check` passes.
- Confirmed root cause: the new assertion exceeded the formatter's line width.
  Resolution: run repository-bound Black once on the owned test. Evidence:
  Black check and Ruff pass, and all nine manifest tests pass.
- Confirmed root cause: the index generator derives per-file update dates from
  filesystem mtimes, which are not stable content provenance in a newly
  materialized linked worktree. Resolution: use exact reverse patches through
  `apply_patch` to remove only generator-created unrelated diffs, retain the
  five owned folder indexes and two previously stale content hashes exposed by
  generation, then check each owned index directly. Evidence: the final diff
  contains no unrelated agent, React, FastAPI, example, core, insight, report,
  or visualization index, while all five owned index checks pass.

### Validation

- `./scripts/python_runtime.sh -m pytest Python/tests/test_indian_code_manifest.py -q`:
  `9 passed`.
- `./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check`:
  current; pile-cap is `HELD / NOT_IMPLEMENTED`, has no workflow, and cites the
  G0 hold evidence.
- `./scripts/python_runtime.sh scripts/check_docs.py --frontmatter --json`:
  344 scanned, 284 with frontmatter, 60 permitted legacy records, zero invalid.
- `./scripts/python_runtime.sh scripts/check_links.py`: 1,271 internal links,
  zero broken.
- `./run.sh efficiency check`: pass.
- Black and Ruff on the two owned Python files: pass.
- `./run.sh parity`: 13 supported / 8 held, 81/81 endpoints directly tested,
  and 13/13 React hooks connected.
- Direct checks for `Python/tests`, `docs`, `docs/planning`,
  `docs/verification`, and `scripts` indexes: pass.
- `./run.sh check --quick`: `10/10` pass.

### Timing

- Orientation/source and Git inspection: approximately 4 minutes.
- Decision research and evidence drafting: approximately 3 minutes.
- Repair and focused validation before candidate closeout: approximately 4
  minutes.
- Hosted CI wait, closeout, and total elapsed: record after merge.

## 2026-08-16 — Session: INDIA-2 Clause 38.2 Truth Hygiene

**Agent:** Codex (`structural-engineer`, sole writer)

**Branch:** `codex/india-2-truth-hygiene-38-2` from freshly fetched
`origin/main = df3635e8811a4d7e69f8786349ce3507f8a28001`, tree
`4de5ae83cdc115fe1984e2b97b616676e094e578`

**Git handoff receipt:**
`docs/verification/india-2-truth-hygiene-38-2-git-handoff-receipt.json`

**Focus:** Audit every live Clause 38.2 beam-flexure identity, independently
benchmark the rounded inverse against exact equilibrium, and repair arithmetic
only if a supported outcome changes. Do not start pile-cap, raft, cleanup,
release, React, dependency, or broad final-gate work.

### Summary

- Controlled-source inspection proved that live beam flexure must bind Clause
  38.1 and Annex G-1.1/G-1.2/G-2.2; the source contains no Clause 38.2, 38.3,
  or 38.4 identity.
- Replayed the legacy rounded inverse and exact equilibrium independently. A
  supported maximum-steel discriminator changed from a false safe result to
  `E_FLEXURE_003`, so metadata-only repair was rejected.
- Promoted one exact rectangular stress-block solver to the common IS 456
  layer, delegated the slab wrapper to it without changing the slab error
  contract, and routed beam required-steel design through it.
- Reconciled decorators, serialized result provenance, registry metadata,
  traceability examples, parity/regression data, active formulas/maps, and the
  generated Indian-code manifest without changing public signatures or units.
- Named decision-only `INDIA-2-FOUNDATION-PILE-CAP-G0` as the sole next packet
  after merge; no foundation implementation was started.

### Issues encountered

- Live metadata and result provenance named nonexistent Clause 38.2/38.3/38.4
  identities and misapplied flanged Annex G-2.2 to rectangular steel design.
- The rounded `4.6` inverse returned steel just below the maximum for a valid
  supported beam while exact equilibrium returned steel just above it, changing
  the main-process safety outcome.
- The first focused test command guessed a nonexistent
  `Python/tests/codes/is456/beam` directory and stopped before collection.
- After executable truth changed, the deterministic committed Indian-code
  manifest was stale until its single planned generator pass.
- The first formatting gate found the new common helper and acceptance module
  did not match the repository Black layout, so the quick gate did not start.
- The first public-contract selection guessed two nonexistent Python API test
  files; the corrected maintained selection then exposed one stale hardcoded
  downstream shear value after the exact flexural steel percentage changed.
- Hosted FastAPI validation passed 441 tests but failed two additional
  benchmark-derived literals: the 153-beam BOQ total and isolated-footing
  screening steel percentage still reflected rounded beam flexure.

### Root causes and resolutions

- Confirmed root cause: historical registry and decorator entries treated
  derived beam design cases as Clause 38 subclauses without checking the
  controlled source hierarchy. Resolution: remove unsupported 38.2/38.3/38.4
  registry entries, register G-1.2, and bind each live consumer to Clause 38.1
  and the applicable Annex G case. Evidence: semantic tests and the generated
  manifest show G-1.2 registered to doubly reinforced design and zero
  registration-only references.
- Confirmed root cause: beam required-steel design used rounded algebraic
  coefficients (`0.5` and `4.6`) instead of solving the canonical `0.36/0.42`
  stress-block equilibrium already used exactly in later foundation/slab work.
  Resolution: one common exact solver now serves beam and slab paths. Evidence:
  the independent `100 kN m` back-substitution closes equilibrium, and the
  `572.05 kN m` discriminator now returns `6600.050311675635 mm2`, exceeds the
  `6600 mm2` maximum, and fails with `E_FLEXURE_003`.
- Confirmed root cause: the focused command assumed a test-folder topology
  instead of discovering maintained paths. Resolution: use `rg --files` to
  select the actual integration/property/regression/unit/slab files, then rerun
  the complete focused selection. Evidence: 190 focused tests pass.
  ⚠️ TERMINAL ISSUE: guessed nonexistent beam test directory -> discovered and
  ran maintained focused files with `rg --files`.
- Confirmed root cause: clause/decorator truth is an input to the deterministic
  Indian-code manifest. Resolution: run the maintained generator exactly once
  after code and tests froze. Evidence: the deterministic-current manifest test
  passes with 173 known references, 98 registered, and zero registration-only.
- Confirmed root cause: hand-applied multiline expressions differed from
  Black's deterministic line wrapping. Resolution: format only the two reported
  files, rerun all 190 focused tests, then run the quick gate. Evidence: Black
  and Ruff pass and the quick gate passes 10/10.
- Confirmed root cause: the public beam test correctly derives shear steel per
  spacing from returned `tau_v` and `tau_c`, but also pinned the old rounded-
  flexure-derived scalar; exact Ast changes the tension percentage and Table 19
  interpolation. Resolution: preserve the formula assertion and update only the
  exact derived scalar. Evidence: the actual maintained beam/capability/public-
  documentation selection passes 17 tests. ⚠️ TERMINAL ISSUE: guessed two
  nonexistent Python public API tests -> discovered the maintained FastAPI
  public-contract paths with `rg --files` and reran them.
- Confirmed root cause: the bundled BOQ test derives selected-bar weight from
  all 153 exact beam results, while the footing screening value uses the shared
  rectangular stress-block inverse; both assertions pinned outputs from the
  replaced rounded solver. Resolution: update only the observed derived
  scalars, retaining dataset hash, calculation identity, PASS, provided-steel,
  and shear-basis assertions. Evidence: the two failed tests and the complete
  FastAPI suite are rerun before the replacement PR head is accepted.

### Validation through content freeze

- Startup: `source_bound=true`, `READY_LOCAL`, no operation marker, exact base
  equality with freshly fetched `origin/main`, and a clean fresh lane.
- Focused flexure, slab compatibility, traceability, manifest, parity,
  regression, service, property, and unit selection: 190 passed.
- Focused FastAPI beam, capability, and public-documentation contracts: 17
  passed.
- Hosted failure reproduction: both exact failing tests reproduced locally,
  then passed after the derived-value repair; the complete FastAPI suite passed
  all 449 tests with 52 warnings.
- Exact equilibrium and false-safe outcome have direct semantic regressions;
  public signatures and unit conventions remain stable.
- Links, maintained indexes, quick `10/10`, normal hooks, hosted checks,
  immutable-head review, merge-tree equality, and final elapsed time complete
  during candidate/publication closeout.

### Timing through content freeze

- Orientation and source audit: `14:51:40Z` to `14:56:30Z` — 4 minutes 50
  seconds.
- Implementation, benchmark repair, and focused validation: `14:56:30Z` to
  `15:02:20Z` — 5 minutes 50 seconds.
- Evidence, plan, task, and handoff freeze: `15:02:20Z` to `15:05:00Z` — 2
  minutes 40 seconds.
- Generator/gates, hosted CI wait, merge closeout, and total wall time are
  reported by the final closeout observation.

## 2026-08-17 — Session: A1 Canonical Truth and Transport Contract

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/a1-canonical-transport-contract` from clean base
`09861d3d5ef758abbe0f7c40b8b49b2f90510765`; isolated linked-worktree runtime
diagnosis reported `source_bound=true`.

**Focus:** Complete M2 packet A1 only: canonical result/error/unit/identity/depth,
serialization, API-surface classification, and transport adapters for the
reference beam journey and applicable maintained consumers. Do not begin A2,
gravity, live ETABS, Excel write-back, optimization, solver, or release work.

### Summary

- Added a shared fail-closed v2 structural-result envelope, stable issues and
  replay identity, a strict JSON normalizer, and a shared explicit/derived beam
  effective-depth contract.
- Migrated the root/service/compatibility Python APIs, CLI, workflow, FastAPI,
  OpenAPI, React catalogue/workflow/trust surfaces, and checked-in development
  clients without creating a second calculation authority.
- Separated HTTP transport acceptance from engineering PASS/FAIL/HOLD and
  normalized maintained JSON 4xx/5xx declarations and framework exceptions to
  `structural-problem/v1`.
- Added source-versus-wheel version authority, claim/artifact classification,
  readiness truth collection, and a reproducible source-free wheel plus
  exact-head FastAPI import-binding verifier.
- Kept the compatibility WebSocket on explicit HOLD when its old payload lacks
  the canonical result envelope. No gravity or A2 implementation was started.

### Issues encountered

- Source imports could be labelled by unrelated stale installed distribution
  metadata.
- Effective-depth arithmetic and required-field defaults were duplicated in
  workflow/transport consumers, including a hidden `D - 43` calculation.
- The parity script compared the same implementation twice and used shallow
  serialization while describing FastAPI parity.
- Readiness omitted semantic parity/quality/input-validation outcomes and could
  report false green.
- HTTP error declarations and framework 404 responses did not share one
  versioned problem contract.
- React accepted allowed status words without proving that the axes, aggregate,
  evidence, and replay identity agreed.
- The workflow catalogue, UI, drafts, generated clients, and tool manifest
  retained older schema versions or incomplete depth/status fields.
- Evidence normalization assumed deflection and crack-width parameter mappings
  always appeared together.
- Several large or multi-file edit attempts failed before changing their target,
  and one accidental signature edit was caught by syntax compilation.

### Root causes and resolutions

- Confirmed root cause: version lookup treated installed metadata as universal
  authority. Resolution: source checkout uses the adjacent package project and
  an installed wheel uses its distribution metadata. Proof selected: unit
  identities plus source-free artifact import receipt.
- Confirmed root cause: adapters owned calculation-bearing depth/default logic.
  Resolution: one resolver requires explicit `d_mm` or a complete cover/stirrup/
  bar basis; required workflow inputs are never filled from display defaults.
  Proof selected: exact `d=443 mm` PASS/FAIL boundary across Python, CLI,
  workflow, REST, React contract, and wheel probes.
- Confirmed root cause: parity did not cross distinct facades and the generic
  serializer did not reject non-finite JSON. Resolution: compare root, service,
  and compatibility facades through one recursive strict JSON round trip; HTTP
  parity remains owned by an actual FastAPI route test.
- Confirmed root cause: readiness collected file-presence proxies instead of
  semantic contract outcomes. Resolution: required API parity can fail the
  report, while advisory quality/input debt produces PARTIAL rather than PASS.
- Confirmed root cause: local route handlers and Starlette's framework 404 path
  used different error shapes. Resolution: one problem builder, global OpenAPI
  models, and shared request/HTTP/domain/generic handlers.
- Confirmed root cause: React treated each status field independently and trust
  presentation fell back to old booleans. Resolution: recompute overall status,
  validate review/depth/identity structure, require current matching evidence,
  and HOLD missing/contradictory WebSocket payloads.
- Confirmed root cause: maintained consumer schemas and generated templates
  were not bound to the new authority. Resolution: version/migrate catalogue,
  workflow, draft, OpenAPI, clients, tool manifest, and claim-surface matrix in
  the same packet; optional explicit depth has no hidden tool default.
- Confirmed root cause: evidence normalization coupled two independently
  optional serviceability mappings. Resolution: retain each supplied mapping
  independently and require at least one only when serviceability is enabled.
- ⚠️ TERMINAL ISSUE: one delete/add mega-patch and one malformed multi-file
  patch did not apply -> inspected exact ranges and used bounded hunks.
- ⚠️ TERMINAL ISSUE: an accidental broad signature edit failed targeted
  `py_compile` -> restored the exact public signature before any test batch.

### Validation through content freeze

- Startup/source: clean isolated base, no operation marker, exact equality with
  `origin/main`, and `source_bound=true`.
- Implementation diagnostics only: changed Python files compile; exact direct,
  workflow, and live FastAPI boundary vector agrees at `d=443 mm`, engineering
  `FAIL`, utilization approximately `1.0194422195`; live invalid request and
  framework 404 use the canonical problem envelope; all 82 HTTP operations
  declared the selected problem responses at inspection time.
- Post-freeze focused tests, deterministic projections, source-free wheel/app
  binding, quick gate, hooks, immutable audit, and hosted checks remain the
  frozen next steps; no broad suite was run during implementation.

### Efficiency receipt through content freeze

- Unchanged-suite reruns: 0.
- Quick/full Python/full repository/React/FastAPI suite runs: 0.
- Maintained index refreshes: 0; the one final refresh remains pending.

## 2026-08-16 — Session: Documentation Frontmatter Contract Repair

**Agent:** Codex (`doc-master`, sole writer)

**Branch:** `codex/doc-frontmatter-contract` from freshly fetched
`origin/main = c8fcd2f0f9b933eb8e8787dc901ee440e05ae984`, tree
`41d878c0681e5e51d159615d14290d5c3964c822`

**Focus:** Make machine-readable frontmatter validation fail whenever invalid
records exist, add direct valid/invalid regressions, and repair exactly the
eight frozen lifecycle/type records. Do not bulk-add frontmatter to 60
permitted legacy documents or start Clause 38.2, pile-cap, raft, cleanup,
release, React, dependency, or broad-gate work.

### Summary

- Reproduced the defect on the clean source-bound lane: JSON mode reported
  `342` checked, `282` with frontmatter, `60` without frontmatter, and `8`
  invalid, but exited `0`; text mode exited `1` on the same records.
- Made JSON mode return the same invalid-count result as text mode without
  changing the report object, and added direct valid/invalid payload-and-exit
  regressions.
- Changed only the eight frozen metadata values: the closed library-first plan
  is `archived`; live combined/flat/deep/wall evidence is `active`; strap A/B/C
  evidence uses `doc_type: reference`. Narrative engineering outcomes remain
  unchanged.
- Reconciled the task board, execution plan, and compact handoff so
  `INDIA-2-TRUTH-HYGIENE-38-2` is the sole next packet after merge.

### Issues encountered

- JSON validation visibly printed eight invalid records but returned success,
  allowing a machine consumer to accept an invalid documentation state.
- Eight documents used completion/acceptance/evidence words as schema lifecycle
  or type values, conflating narrative engineering outcome with maintained
  document metadata.
- The first normal commit-hook run stopped because the compact brief used
  `## Required reading` instead of the exact required heading
  `## Required Reading`, blocking candidate publication.

### Root causes and resolutions

- Confirmed root cause: `check_frontmatter()` returned `0` unconditionally
  immediately after printing its JSON report, before applying the invalid-count
  rule used by text mode. Resolution: return `1` when
  `report["invalid_frontmatter"]` is nonzero in that branch. Evidence: the
  direct invalid fixture preserves the full report and returns `1`; the direct
  valid fixture preserves its report and returns `0`; both tests pass.
- Confirmed root cause: record authors used `completed`, `complete`, `accepted`,
  and `verification` to describe the body outcome/purpose even though the
  maintained schema defines document lifecycle as active, draft, deprecated,
  or archived and type as guide, reference, tutorial, index, spec, or log.
  Resolution:
  map the closed plan to `archived`, live evidence to `active`, and strap
  evidence to `reference`, without changing any engineering statement.
  Evidence: live JSON and text modes both exit `0`, report zero invalid, and
  retain exactly 60 permitted no-frontmatter records.
- Confirmed root cause: the handoff rewrite normalized heading capitalization
  without first checking the exact string contract enforced by
  `check_session_docs.py`; generic link, brief-length, and quick checks did not
  exercise that constraint. Resolution: restore the exact required heading and
  retain normal hooks as the publication guard. Evidence: the repaired hook
  run must pass before the candidate commit is accepted. ⚠️ TERMINAL ISSUE:
  normal commit hooks rejected the compact brief heading -> restored the exact
  maintained heading and reran the candidate gates.

### Validation through content freeze

- Startup: `source_bound=true`, `READY_LOCAL`, no operation marker, exact base
  equality with fetched `origin/main`, and a clean fresh lane.
- Focused regressions: `2 passed`; Ruff and Black pass for the checker and new
  test module.
- Live replay: JSON reports `invalid_frontmatter: 0` with `files_invalid: []`;
  JSON and text both exit `0`; total/with/without/skipped counts remain
  `342/282/60/462`.
- Maintained indexes, links, quick `10/10`, normal hooks, hosted checks, and
  merge-tree equality complete during candidate/publication closeout.

### Timing through content freeze

- Orientation and source binding: `14:23:14Z` to `14:24:24Z` — 1 minute 10
  seconds.
- Reproduction, implementation, and focused validation: `14:24:24Z` to
  `14:26:36Z` — 2 minutes 12 seconds.
- Task/plan/handoff reconciliation: `14:26:36Z` to `14:28:30Z` — 1 minute 54
  seconds.
- Generator/gates, hosted CI wait, merge closeout, and total wall time are
  reported by the final closeout observation.

## 2026-08-17 — Session: A1 Canonical Transport Closeout Continuation

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/a1-canonical-transport-contract`.

**Focus:** Continue the immediately preceding full A1 session record through
the repository closeout sequence. All scope, non-goals, issues, root causes,
and frozen validation selections in that A1 record remain authoritative.

### Issues encountered

- The first append used a repeated historical closeout sentence as context and
  placed the full A1 record before the final older session entry, so it was not
  the physically newest entry consumed by session validation.
- The first index-tool discovery guessed a nonexistent
  `scripts/generate_folder_indexes.py` path and stopped without writing.
- The first focused-test tool call lost its result because the output wrapper
  referenced an undefined JavaScript variable; process inspection confirmed no
  pytest process remained before the batch was relaunched once.
- The focused React command exited before collection because this isolated
  worktree had no ignored `react_app/node_modules` installation, while the
  pinned dependency tree existed only in the primary checkout.
- The first post-freeze TypeScript build found one imprecise draft-parser cast
  and two older auto-design test fixtures without the required v2 result
  envelope; lint itself passed.
- The changed-file quality batch then rejected two missing optional-dependency
  metadata names, one unused validation assignment, three import-order
  findings, three formatting findings, and a guessed obsolete frontmatter
  checker path. This was the second material rejection, so A1 returned to a
  bounded replan before further validation.
- The first candidate commit was blocked before creation: mypy found two depth
  narrowing errors and one evidence tuple type error; the API-doc hook required
  explicit `api.EffectiveDepth*` tokens; and the scripts hook found the new
  artifact verifier absent from `automation-map.json`.
- After those repairs, the maintained contract suite found that public
  `design_beam_is456` had made `d_mm` omittable, contrary to its frozen
  signature. A further bounded replan was required before another candidate.
- A grouped command changed directory to `Python` for mypy, so two following
  root-relative pytest commands did not start.
- All other A1 material issues are recorded in the full
  `A1 Canonical Truth and Transport Contract` entry above.

### Root causes and resolutions

- Confirmed root cause: the session log contains repeated closeout phrases, so
  a patch with only generic trailing context matched an earlier occurrence.
  Resolution: add this bounded continuation after the uniquely identified
  final documentation-frontmatter timing block. Proof: this continuation is
  now the last session entry and contains both mandatory sections.
- Confirmed root cause: the maintained index entrypoint is
  `./run.sh generate indexes`, backed by `scripts/generate_enhanced_index.py`;
  the guessed plural filename was never a maintained path. Resolution: discover
  the entrypoint with targeted `rg` and use the documented targeted-folder
  command for the final batch. ⚠️ TERMINAL ISSUE: guessed a nonexistent index
  script -> discovered and used the maintained `run.sh` entrypoint.
- Confirmed root cause: the command runner was correct, but the surrounding
  result-rendering snippet referenced `rest` without defining it. Resolution:
  inspect live processes first, confirm no test remained active, then launch
  the one evidence-producing batch with a minimal output wrapper.
- Confirmed root cause: linked Git worktrees do not share ignored dependency
  directories. Resolution: run the pinned lockfile install in this worktree;
  `react_app/.gitignore` keeps `node_modules` outside Git. Proof selected: the
  failed command is rerun only after the dependency repair, followed by the
  frozen TypeScript/lint checks. ⚠️ TERMINAL ISSUE: Vitest was absent in the
  isolated lane -> install the exact lockfile dependencies locally and rerun
  the failed React evidence only.
- Confirmed root cause: `Object.fromEntries` loses the exact required-key shape,
  and the two fixtures predated the canonical result carrier. Resolution: build
  the already-validated draft object with explicit required keys and give both
  fixtures a typed canonical PASS envelope. Proof: 7 impacted tests, lint, and
  the production build pass.
- Confirmed root cause: the library-version migration removed
  `importlib.metadata` names that `show_versions()` still needs for optional
  dependency reporting; the depth resolver assignment survived after its value
  stopped being consumed; and changed import/test files had not received their
  normal formatter pass. Resolution: restore only the dependency lookup names,
  retain the resolver call as validation without assignment, and apply the
  maintained formatters to the reported files. The maintained frontmatter
  entrypoint is `scripts/check_docs.py --frontmatter`, not the guessed deleted
  path. Proof: 108 impact-mapped tests, all 3 parity vectors, Ruff, Black,
  frontmatter with zero invalid records, and all 1,363 links pass.
- Confirmed root cause: optional `d_mm` was not explicitly narrowed in the
  deflection helper, branch-specific tuple inference was too narrow, the API
  checker recognizes `api.Symbol` tokens rather than prose mentions, and every
  maintained script requires one automation-map task. Resolution: add the
  explicit `None` guard and tuple annotation, document both public types with
  recognized names, and register the verifier. Proof: mypy passes 236 source
  files, API documentation passes, and automation coverage is 111/111.
- Confirmed root cause: adding `=None` changed the frozen public signature even
  though the intended contract change concerned accepted depth methods, not
  keyword presence. Resolution: retain required `d_mm: float | None`; explicit
  callers use a number, while derived-basis callers use `d_mm=None` plus the
  complete basis. Proof: 42 affected tests, 18 frozen contract tests, all 3
  parity vectors, generated signature registries, and the final source-free
  wheel proof pass.
- ⚠️ TERMINAL ISSUE: `cd Python` changed the directory for later commands in
  the same shell block -> reran the two unstarted pytest commands from the
  workspace root with `./scripts/python_runtime.sh`; both passed.
- No additional calculation, API, transport, or engineering root cause was
  discovered after the full A1 record.

### Validation through the revised content freeze

- The frozen focused Python/FastAPI selection passed. The focused React
  selection passed with 10 files and 87 tests. The impact-mapped TypeScript
  repair passed 7 tests, lint, and the production build.
- The second-rejection replan passed its 108 impact-mapped tests, all 3 parity
  vectors, changed-file Ruff/Black checks, frontmatter, and link validation.
- API manifest, classification, beam tool manifest, and OpenAPI projections are
  current; OpenAPI matches 82 endpoints and 362 schemas.
- One external wheel passed source-free Python/CLI and exact-head FastAPI import
  binding. All used effective depth 443 mm and engineering `FAIL`; installed
  identity was version `0.23.1a2` with matching distribution metadata. The
  final rebuilt wheel SHA-256 is
  `2c943b2bbb61c8a2572ee7118b08b5650628ea25b83c2f87a71ed31afc359793`.
- The first quick gate passed 10/10. The first hook attempt rejected the
  candidate and created no commit. A revised-candidate quick gate, normal hooks,
  immutable audit, and hosted checks remain after this final content freeze and
  are not written back into the candidate.
- No A2, gravity, live ETABS, Excel write-back, optimizer, solver, or release
  work was started.

## 2026-08-17 — Session: A1 Hosted FastAPI Repair

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/a1-canonical-transport-contract`.

**Focus:** Repair only the single FastAPI validation failure on PR #822 at
exact head `98927f1de4a1e8f60d1d9d66bf2e8a036c2a0dd2`.

### Issues encountered

- Hosted FastAPI Validation reported 449 passing tests and one failure in
  `test_depth_boundary_matches_the_canonical_failure_vector`; the aggregate PR
  Gate failed only because that required job failed.

### Root causes and resolutions

- Confirmed root cause: when A1 restored the frozen required `d_mm` keyword,
  the production FastAPI adapter and the canonical Python test were updated to
  pass `d_mm=None` with the complete derivation basis, but the direct comparison
  call in this FastAPI test was missed. Resolution: add the same explicit
  `d_mm=None` to that test fixture. Proof selected: run only the failed test,
  then normal commit hooks and the automatically triggered hosted validation;
  do not rerun unchanged local suites.

### Boundary

- No calculation, HTTP adapter, schema, React, A2, gravity, ETABS, Excel,
  optimization, release, or professional-approval behavior is changed.

## 2026-08-17 — Session: A2 Lossless Intake and Calculation Root Causes

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/a2-lossless-intake-calculation`.

**Focus:** Implement only Packet A2 bundles F3, F4, and the calculation/advice
part of F5 on the merged A1 base. Gravity, live ETABS, Excel, write-back,
optimization, solver, release, and professional approval remain excluded.

### Issues encountered

- The first exact-extrema diagnostic used `zip(..., strict=True)` for adjacent
  boundary lists whose one-item length difference is intentional, so the point
  load reproducer stopped before calculation.
- After retaining both sides of a point-load jump, the generic critical-point
  interpolator divided by zero between two samples at the same physical
  location.
- The frozen focused batch rejected five contract assertions: two tests still
  required exactly the requested plot count, the schema freeze omitted the
  intended additive ETABS provenance, one test used a nonexistent field
  attribute, and semantic reflection could not see optional nested dataclasses.
  Its first repair then exposed the same checker's inability to validate the
  deliberately serialized canonical result-envelope mapping, so the candidate
  returned to a bounded replan.
- The architecture check rejected a direct UI-to-core import in the repaired
  building route. The first service-facade repair then selected the facade's
  visualization `Point3D` name rather than the canonical nested point model,
  and two building-route cases returned 422.
- This isolated worktree did not contain ignored React dependencies. A direct
  `npm ci` used the shell's Node 26 and warned that the project requires Node
  24, although the lockfile installation completed.
- The cumulative Python run rejected 11 legacy assertions. Eight were one
  public effective-depth error-message drift, while three audit-readiness tests
  passed immediately in the isolated failed-only selection. The reconnect
  removed the original process handle after pytest had written its exact
  failed-node cache.
- The first full repository gate passed 28 of 31 checks and rejected only the
  intentionally changed ETABS API manifest, its additive `BeamForces` schema
  snapshot, and the 404-file active-document count against the 400-file limit.
- The first normal commit-hook attempt applied deterministic formatting/newline
  fixes, then rejected the candidate because mypy treated the seven new
  provenance fields as required constructor arguments and Bandit scanned three
  pre-existing silent invalid-member skips plus the `PASS` enum string.
- Hosted PR Validation passed repository, documentation, React, and Python but
  failed three FastAPI plausibility-validator tests whose direct
  `SmartAnalysisRequest` construction omitted A2's now-required explicit
  effective depth and span.

### Root causes and resolutions

- Confirmed root cause: `zip(boundaries, boundaries[1:])` is intentionally
  non-equal. Resolution: declare `strict=False`. Evidence: exact off-grid point,
  partial UDL, mirrored-location, and load-scaling vectors pass.
- Confirmed root cause: discontinuity plotting represents left/right shear at
  identical coordinates, but continuous zero-crossing interpolation assumed a
  positive interval. Resolution: skip interpolation when adjacent coordinates
  are equal while retaining both values. Evidence: applied moment and point-load
  discontinuity tests pass without losing extrema.
- Confirmed root cause: the contract tests encoded the old display-array and
  `BeamForces` shapes, used `.canonical_unit` instead of `.unit`, and traversed
  only direct dataclass annotations. Resolution: assert the exact critical-point
  behavior, freeze the additive provenance fields, traverse optional dataclasses,
  and validate serialized `result_envelope.*` paths against
  `StructuralResultEnvelopeV2`. Evidence: all eight semantic-contract checks and
  the failed schema/load assertions pass after the bounded replan.
- Confirmed root cause: UI code bypassed the service layer, while the facade has
  two historical `Point3D` meanings. Resolution: import only `BeamGeometry` and
  `FrameType` from the service facade and pass validated point/section mappings
  into the canonical Pydantic model. Evidence: six building-route tests pass;
  architecture reports 209 files and zero violations; 668-file import validation
  reports zero broken imports. ⚠️ TERMINAL ISSUE: direct core import failed the
  architecture gate -> used the maintained service boundary and typed mappings.
- Confirmed root cause: linked worktrees do not share ignored `node_modules`,
  and the interactive shell runtime is not the repository-pinned Node version.
  Resolution: install the exact lockfile once, then run every React command
  through `./run.sh frontend`, which selected Node 24.19.0/npm 11.17.0. Evidence:
  focused Vitest, production build, and lint pass. ⚠️ TERMINAL ISSUE: isolated
  React dependencies were absent and direct npm used Node 26 -> installed once
  and used the pinned frontend wrapper for evidence.
- Confirmed root cause: `resolve_effective_depth_v1` combined non-finite,
  non-positive, and geometric depth failures into newer generic messages after
  A1, while the public beam contract still distinguishes those outcomes.
  Resolution: retain the central validator and restore field-specific finite
  messages plus the established overall-depth relationship message. Evidence:
  all eight failed depth cases, the 46 canonical transport/batch cases, and
  changed-file Ruff pass.
- Root cause unconfirmed for the three audit-readiness failures: they passed in
  the first isolated failed-only selection with no code or fixture change, so
  no product behavior was changed for them. Their exact failed nodes were
  recovered from pytest's cache and the remaining gate will determine whether
  any reproducible repository-level issue remains. ⚠️ TERMINAL ISSUE: app
  reconnect removed the completed pytest process/output handle -> recovered the
  exact failed-node set from `Python/.pytest_cache/v/cache/lastfailed` and ran
  only that set with verbose output.
- Confirmed root cause: ETABS provenance fields changed the public dataclass and
  serialized model intentionally, but the generated manifest and snapshot still
  described the pre-A2 shapes. Resolution: regenerate each canonical artifact
  once with its maintained generator; no calculation code changed.
- Confirmed root cause: four documents already marked `archived` or `deprecated`
  remained in the active documentation tree, so adding the A2 evidence record
  exposed the hard limit. Resolution: preview and move exactly those four files
  through `safe_file_move.py`, preserving content and updating ordinary links;
  the active count is now 400 and link validation remains at zero broken links.
  A tempting INDIA plan was explicitly excluded because its preview would have
  rewritten immutable historical receipts.
- Confirmed root cause: positional `Field(None, ...)` defaults were valid at
  runtime but were not inferred as optional by the configured Pydantic mypy
  plugin for the extended `BeamForces` signature. Resolution: express those
  seven defaults as `default=None`; the exact configured mypy command passes all
  236 source files and 55 affected model/adapter tests pass.
- Confirmed root cause: touching the historical multi-format adapter brought
  three broad `except Exception: continue` paths into Bandit's changed-file
  scope, while `DesignStatus.PASS` is an engineering status false positive.
  Resolution: narrow those catches to validation errors, log every skipped
  member identity/reason, and annotate only the enum literal as non-credential
  `B105`. Changed-file Bandit reports no issues. The hook's Black and EOF edits
  were retained exactly.
- Confirmed root cause: the three older tests exercised only the depth/width
  validator and were outside the focused smart-route selection, so their setup
  still relied on the removed hidden `D - 50` and `12D` assumptions. Resolution:
  add realistic explicit `effective_depth` and `span_length` values without
  changing the assertions or production model. The exact three failed tests are
  the repair evidence; the unchanged hosted jobs are not rerun locally.

### Validation through content freeze

- Source binding: base `a0458e1935e9f14bcba47a838d5fe61b46174b05`,
  `source_bound=true`.
- Focused Python/FastAPI selection completed; every initially failed assertion
  passed through impact-mapped repair without rerunning unchanged suites.
- React contract `1/1`, production build, lint, changed-file Ruff, architecture,
  import validation, and OpenAPI all pass. OpenAPI remains 82 endpoints and now
  contains 368 schemas.
- Broad Python, full repository, quick, hooks, immutable audit, push, and hosted
  checks remain the cumulative M2/G1 closeout sequence after the final index
  refresh.

## 2026-08-17 — Session: B1 Gravity Model and Load Ledger

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/b1-gravity-model-load-ledger`.

**Focus:** Freeze the exact one-storey physical model, dead/live source basis,
self-weight ownership, deterministic slab-to-footing transfer ledger, and
balance evidence. Component design, Gravity Workflow V1 orchestration, REST,
CLI, React, Excel, live ETABS, solver, lateral loads, optimization, release,
and professional approval remain excluded.

### Issues encountered

- The initial ledger labelled a combined dead reaction/action as slab
  superimposed dead or column self-weight even though it contained several
  separately owned dead sources. The numbers balanced, but the provenance label
  would have misrepresented the engineering basis.
- The first physical-model validator permitted an extra unused section and did
  not reject a second accepted source record pointing to the same canonical
  entity, so exact model/source closure was incomplete.
- The first narrow test run had two test-fixture errors: one exception-message
  regex was narrower than the actual contract and one serialized nested model
  was treated as a model object instead of a dictionary.
- A root-level targeted mypy invocation combined the `Python.` and installed
  `structural_lib.` module identities, then the package-context invocation
  exposed the known Pydantic computed-property decorator diagnostic for the
  four new computed fields.
- Adding the B1 specification and evidence raised active documentation from the
  enforced limit of 400 to 402.
- The first frozen focused batch rejected the new specification's front matter
  because it used `doc_type: specification` instead of the repository's exact
  `doc_type: spec` vocabulary. Its parallel style/type lane also started in the
  `Python/` directory with a root-relative `./scripts/` path and did not run.
- The corrected changed-file Ruff lane then rejected one import-order rule and
  two constant-attribute `getattr` calls in the new model/test files.
- The first normal commit-hook attempt passed every substantive hook but its EOF
  fixer changed the freshly generated `docs/docs-index.json`, so no commit was
  created.
- The second hook attempt proved the EOF repair but Black reformatted the new
  docs-index regression test, so it also correctly created no commit.

### Root causes and resolutions

- Confirmed root cause: the entry category type had only source categories, so
  the implementation reused a source label after aggregation. Resolution: add
  the derived `COMBINED_DEAD` category and use it only after separately traced
  dead sources combine. Evidence: the hand vector preserves nine distinct
  sources, 41 accepted ledger entries, and exact zero-residual balances.
- Confirmed root cause: set equality proved that every canonical ID appeared
  but did not prove one-to-one source mapping, and the topology count did not
  freeze the three-section boundary. Resolution: require one material, one
  section of each exact kind, complete participation, one accepted source row
  per canonical entity, and one common base elevation. Evidence: the focused
  orphan and duplicate-source vectors reject before calculation.
- Confirmed root cause: `model_dump(mode="python")` serializes nested Pydantic
  models as dictionaries, and the test expected a different but equivalent
  error phrase. Resolution: mutate the serialized dictionaries and assert the
  stable contract phrase. No production behavior changed; the repaired test
  file passes all 10 cases.
- Confirmed root cause: running configured mypy against a repository-root path
  conflicted with its `explicit_package_bases` package context, while Pydantic
  computed fields require the same narrow `prop-decorator` suppression already
  used by repository Pydantic models. Resolution: run from `Python/`, add only
  the four exact ignores, and correct real type errors exposed in the first
  pass. Evidence: configured mypy reports no issues in both new source modules.
  ⚠️ TERMINAL ISSUE: root-level targeted mypy found one file under two module
  names -> ran the exact modules from the configured Python package directory.
- Confirmed root cause: the active-doc count was already exactly at its hard
  limit before the two required B1 records. Resolution: use the safe-file-ops
  preview and maintained move script to archive exactly two already-deprecated,
  unreferenced retired Git-wrapper documents. They remain recoverable under
  `docs/_archive/2026-08`; active count is 400 and all 1,361 links pass.
- Confirmed root cause: the human term "specification" differs from the
  generator/checker's controlled `spec` metadata token, and the parallel lane's
  workdir did not match its first command path. Resolution: change only the
  front-matter token, start changed-file Ruff from the repository root, and run
  configured mypy separately from `Python/`. The impact-mapped repair repeats
  documentation and the previously unexecuted style/type evidence only.
  ⚠️ TERMINAL ISSUE: a Python-workdir lane used `./scripts/python_runtime.sh` ->
  split root Ruff and package-context mypy commands with explicit workdirs.
- Confirmed root cause: the initial formatting pass normalized layout but did
  not run Ruff's import and bugbear rules. Resolution: group the Pydantic import
  deterministically and replace both constant `getattr` calls with typed direct
  attributes; the generic canonical sorter now declares its small `id`
  protocol and the test helper declares the exact ledger type. The repair
  repeats only changed-file Ruff, configured mypy, and the 10 directly affected
  gravity vectors.
- Confirmed root cause: `generate_docs_index.py --write` serialized JSON without
  a final newline, while the mandatory EOF hook adds one. This deterministic
  mismatch had also caused hook churn in an earlier packet. Resolution: make
  the maintained generator write UTF-8 JSON with one final newline and add a
  temporary-file regression proving valid JSON and the EOF contract. The hook's
  newline-only edit is retained; gravity evidence is unchanged.
- Confirmed root cause: the narrow generator repair check ran pytest and Ruff
  but omitted Black after creating the regression file. Resolution: retain the
  hook's formatting, refresh the test index, and add Black to the failed-only
  repair evidence before the next normal hook run. All other hooks passed and
  are not independently repeated.

### Validation through content freeze

- Source binding: base `32daa0138b969be0b77b59dd33d938ad170f3a9e`,
  `source_bound=true`.
- Hand arithmetic and adverse-contract file: `10 passed`; configured mypy for
  both new modules: no issues.
- Exact expected actions are 198 kN DL and 72 kN LL at foundation level, with
  49.5 kN DL, 18 kN LL, 67.5 kN service, and 101.25 kN factored action at each
  footing destination. All 26 reconciliation records have zero residual.
- The consolidated focused selection passed `52/52`; architecture checked 210
  files with zero violations, 238-file library import validation found zero
  broken imports, and 191-file circular analysis found no cycle. Documentation
  passes all five checks at 400 active files and zero broken links. The first
  quick gate passed `10/10`.
- The first normal hooks passed every substantive check, including 238-file
  mypy and Bandit; only the repaired generator/EOF mismatch prevented the
  commit. The repaired-candidate quick gate also passed `10/10`; final hooks,
  immutable audit, push, and hosted validation remain. Broad Python and the full
  repository gate remain reserved for cumulative M2+M3 closeout.

## 2026-08-17 — Session: B2 Building Gravity Workflow V1

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/b2-gravity-workflow-v1`.

**Focus:** Bind the frozen B1 model/load identities to exact member actions,
component applicability, canonical slab/beam/column/footing APIs, a calculation
book, CLI, versioned REST routes, and a review UI. Excel, live ETABS, write-back,
optimization, multi-storey/general analysis, release, and professional approval
remain excluded.

### Issues encountered

- Eagerly exporting the new gravity service from `services/__init__.py` caused
  a circular import through the established beam service pipeline.
- The first FastAPI response converted the already validated bundle to a
  dictionary containing its computed workflow hash. Response-model validation
  then treated that computed field as unknown input and rejected the request.
- The isolated B2 worktree did not contain ignored React `node_modules`.
  Attempts to invoke Vitest from the primary checkout could not resolve the B2
  worktree's dependencies.
- A zsh inspection loop used `path` as its variable name. In zsh, `path` is tied
  to `PATH`, so normal commands became unavailable inside that shell.
- The maintained safe-move tool rewrote normal links while archiving two guides
  but missed three links that included Markdown anchors, then correctly failed
  its link gate after completing each affected move.
- A guessed standalone documentation front-matter script name was not present;
  the repository now exposes that check through its unified documentation tool.
- The first frozen architecture check found that the new FastAPI router imported
  `GravityWorkflowRequestV1` directly from the core layer.
- The strict documentation batch exposed one unchanged A2 evidence document
  that had neither the current YAML metadata contract nor the complete legacy
  Type/Audience/Status header.
- The cumulative Python run passed 6,488 cases but rejected the new CLI because
  its maintained advertised-entry-point inventory had not been updated. The
  same run reproduced three audit-readiness tests that returned an empty
  evidence set only under the `run.sh test` working directory.
- Adding B2 evidence would otherwise return the active documentation tree to
  its enforced file limit, while the user requested that up to ten obsolete
  files be removed if safely possible.

### Root causes and resolutions

- Confirmed root cause: `services.__init__` initialization reached
  `gravity_workflow`, which imports `beam_api`, before the existing service
  facade had finished initializing. Resolution: remove the eager facade export
  and keep the exact public module import
  `structural_lib.services.gravity_workflow`. Focused imports and workflow tests
  load without a cycle.
- Confirmed root cause: FastAPI revalidated a serialized response as new model
  input, while `workflow_result_hash` is an output-only Pydantic computed field
  under an `extra="forbid"` contract. Resolution: pass the validated model object
  to the response wrapper and let FastAPI serialize it once. The three focused
  REST definition/run/rejection tests pass.
- Confirmed root cause: linked worktrees share Git objects but not ignored npm
  dependencies, and a shared binary still resolves packages relative to the
  calling worktree. Resolution: perform one lockfile-pinned, offline-preferred
  `npm ci` in the B2 worktree, then run the focused React test through the
  repository runtime. Both UI cases pass. ⚠️ TERMINAL ISSUE: shared Vitest could
  not resolve worktree dependencies -> installed the exact lockfile once.
- Confirmed root cause: zsh exposes `path` as a special array synchronized with
  the executable search path. Resolution: rename the loop variable to
  `doc_file`; inspection commands then ran normally. ⚠️ TERMINAL ISSUE: using
  `path` hid `basename`, `rg`, `wc`, and `tr` -> reran with `doc_file`.
- Confirmed root cause: the safe-move reference matcher handled file links but
  did not rewrite the same paths when an anchor suffix was present. Resolution:
  repair only the three exact anchored references with `apply_patch` and rerun
  link validation before each next move. Link validation remains at zero broken
  links. The tool itself is not changed in this feature packet.
- Confirmed root cause: front-matter validation was consolidated into
  `scripts/check_docs.py` while the old single-purpose implementation is
  archived. Resolution: use `scripts/check_docs.py --frontmatter`; the unified
  check reports zero invalid front matter. ⚠️ TERMINAL ISSUE: the guessed
  `scripts/check_docs_frontmatter.py` path did not exist -> used the maintained
  unified documentation checker.
- Confirmed root cause: the router reused the type's defining module instead of
  the service boundary required for UI/transport consumers. Resolution: export
  the request contract from the exact `services.gravity_workflow` module and
  import it there in the router, without adding the eager package-level export
  that caused the earlier cycle. The affected architecture, import, REST, Ruff,
  Black, and type checks form the repair evidence.
- Confirmed root cause: the A2 evidence body predated its integration into the
  strict active-document metadata set. Resolution: add the canonical lowercase
  front matter without changing its evidence claims. The B2 documents already
  had valid front matter; the failed-only documentation batch is repeated after
  the affected index refresh.
- Confirmed root cause: the CLI parser and implementation contained
  `gravity-v1`, while `advertised_entry_points_v1.json` still described the
  preceding parser surface. Resolution: add the command as a calculation entry
  bound to its exact CLI acceptance test and advance the frozen UAT inventory
  count from 12 to 13 with an explicit entry assertion; the failed release-UAT
  node is the repair evidence.
- Confirmed root cause: `collect_contract_truth_evidence` tested repo-relative
  `scripts/...` paths against the process working directory. `run.sh test`
  correctly runs pytest from `Python/`, so all three checks were silently
  skipped and the report falsely appeared empty/PASS; an isolated root-level
  test had previously masked that defect. Resolution: bind existence checks,
  script execution paths, and subprocess cwd to the audit script's repository
  root while retaining stable relative evidence labels. The exact three failed
  nodes are the repair evidence.
- Confirmed root cause: ten documents marked deprecated or superseded still
  occupied active guide/contributing locations. Resolution: archive exactly
  those ten through `safe_file_move.py`; content remains recoverable under
  `docs/_archive/2026-08`, ordinary references point to the preserved copies,
  and widely referenced active guides plus immutable historical receipts were
  excluded from cleanup. Active Markdown documents fall from 400 to 390 before
  the required B2 evidence record is added.

### Validation through content freeze

- Source binding: base `cb49234f93283e35a87789bf631596f35c8cfcb1`,
  `source_bound=true`.
- Exact hand output: 22 actions; beam service/ULS line actions 20.25/30.375
  kN/m; moments 91.125/136.6875 kNm; shears 60.75/91.125 kN; footing ULS
  handoff 101.25 kN; all 26 ledger boundaries have zero residual.
- The first focused implementation checks passed six Python workflow cases,
  three REST cases, and two React review cases. Subsequent adverse vectors add
  exact footing and CLI coverage to the frozen consolidated selection.
- Ten safe archive moves complete with 390 active Markdown files before the B2
  evidence record and zero broken links across 1,336 internal references.
- The consolidated focused, OpenAPI, index, quick, cumulative broad, hook,
  immutable-audit, push, and hosted-check results remain the closeout sequence
  for the frozen candidate.

## 2026-08-17 — Session: E1 Excel Routine Workbench next-session freeze

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/e1-excel-routine-workbench`.

**Focus:** Stop before M4 implementation and leave a durable, source-bound E1
plan and next-session handoff on the exact merged B2 base. ETABS file/live work,
write-back, optimization, release, and professional approval remain excluded.

### Issues encountered

- The first worktree-creation tool composition embedded shell `${name:?}`
  expressions in a JavaScript template literal, so JavaScript parsed them as
  incomplete interpolation before any shell command ran.
- A dependency search passed an unmatched `Python/requirements*.txt` glob to
  zsh, which rejected the command before the intended read-only search.
- The inherited task board and next-session briefing still described the older
  Alpha release/whole-building decision state even though A1, A2, B1, and B2
  are merged and E1 is now the requested next packet.
- The first two session handoff checks rejected the new briefing because its
  `Required Reading` heading used sentence-case capitalization and its state
  table used `Complete` where the parser requires the exact `Current` row.

### Root causes and resolutions

- Confirmed root cause: two interpreters were competing for the same `${...}`
  syntax in the tool wrapper. Resolution: pass the command as a normal
  JavaScript string so `${target_path:?}` reaches zsh unchanged; the isolated
  worktree was then created at exact base `c127e4b2`. No partial Git mutation
  occurred. ⚠️ TERMINAL ISSUE: JavaScript consumed shell parameter syntax ->
  reran with a non-template command string.
- Confirmed root cause: zsh uses `nomatch` for unmatched globs. Resolution:
  enumerate maintained dependency manifests with `rg --files`, then search only
  existing exact paths. ⚠️ TERMINAL ISSUE: unmatched dependency glob aborted a
  read-only search -> used exact discovered files.
- Confirmed root cause: the durable task/handoff records predated the integrated
  master-plan execution. Resolution: add the exact E1 execution plan, replace
  the next-session handoff, and minimally reconcile task state with PRs
  #822-#825. No E1 production or test code was changed.
- Confirmed root cause: the session parser matches the required handoff heading
  and `Current`/`Next` state rows literally. Resolution: use those exact
  contract labels; the failed handoff checks are the repair evidence.

### Validation through content freeze

- Source-bound isolated lane created from merged B2 commit
  `c127e4b2325fceb9adebf3d29d59e549f7ae4aa6`; session start reported
  `READY_LOCAL` and `Python source binding: current worktree`.
- The E1 plan freezes the selected-table journey, workbook/table identities,
  strict field and row-accounting rules, canonical status/passport/stale
  behavior, implementation map, exact validation categories, Windows Excel
  matrix cell, and G3 stop conditions.
- Implementation remains intentionally unstarted. Only planning, task, session,
  and handoff records changed; calculation, FastAPI, React, Excel, ETABS, and
  broad repository suites are therefore unchanged and not rerun.

**Git handoff receipt:** `docs/verification/e1-excel-routine-workbench-git-handoff-receipt.json`
