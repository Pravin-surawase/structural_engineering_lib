---
owner: governance
status: active
last_updated: 2026-08-27
doc_type: reference
task: LIB-PRO-013-A0-CONSOLIDATED-RENEWAL-AUDIT
---

# LIB-PRO-013 A0 consolidated renewal audit

## 1. Verdict and claim boundary

**A0 audit result: COMPLETE FOR C2 TRUTH FREEZE; RUNTIME REMEDIATION, RELEASE,
QUALIFIED REVIEW, AND PROFESSIONAL APPROVAL REMAIN HELD.**

All 42 LIB-PRO-013 Section 7 domains have an owner, method, evidence artifact,
and disposition. No new current-source P0 was reproduced. The accepted S0
repairs remain effective in the exact current source and a newly built
source-free wheel. The already-public `0.24.0a1` wheel and sdist are older,
different artifacts which predate S0; their known safety exposure is not
silently converted into a current-source defect or a release-ready claim.

This is a read-only product/repository audit. It changes no runtime, test,
formula, normalized table, dependency, public signature, generated owner,
release metadata, protected source, or professional claim. It authorizes no
automatic B0, F0, R0, Packets C-I, `/api/v2`, release, publication, deletion,
or engineering use.

## 2. Exact baseline and evidence objects

### 2.1 Git and accepted S0 identity

| Object | Exact identity | Decision |
|---|---|---|
| Freshly fetched audit source | commit `49c2fe4553e923a7433ca0a5fa28ea364956ae30`; tree `704190f7322b8c29bc4a85036d7ade54d355f306` | Exact `origin/main` at A0 entry |
| Reviewed S0 post-merge repair | candidate `1485da58297379a65882be7e4be8a23d6d86117d`; tree `704190f7322b8c29bc4a85036d7ade54d355f306` | Tree-identical to accepted merge |
| S0 post-merge repair integration | PR #878; merge `49c2fe4553e923a7433ca0a5fa28ea364956ae30`; hosted run `33088194292` | Required changed-path checks passed |
| Earlier S0 integration | merge `4cebcccb3a07b8046e31b23332236321ebee1d25` | Ancestor of the audit source |
| Original planning baseline | `d3242731e94dacd74e804a1f4a25c4c0da11790f` | Ancestor of the audit source |
| A0 branch | `codex/lib-pro-013-a0-consolidated-renewal-audit` | One session/branch/candidate/PR lane |

At entry, the A0 branch equalled freshly fetched `origin/main`, with no lock,
conflict, operation, stash, or overlapping evidence writer. Nine open
Dependabot PRs touched dependency manifests only and did not overlap A0-owned
or shared evidence paths.

### 2.2 Artifact separation

| Evidence object | Exact identity | What it proves | What it does not prove |
|---|---|---|---|
| Public tag | `v0.24.0a1`; commit `71b7065216d4266d63ad6b31bd39bba81fa16efc`; tree `221de5561bf6419396a2c20697c574124d721694` | Published source identity | Later S0 repairs |
| Public wheel | SHA-256 `b5e0df7b561e8c715f37c602200eaae2c369ec5dc992eec87110a77c1026201a`; 774,739 bytes | Exact PyPI/GitHub release artifact | Current source, S0 closure, professional use |
| Public sdist | SHA-256 `8c1d6b762a779686be5d17ed0dd9719f7155a5863a764e943a0e1ba9aeb0a53b`; 652,423 bytes | Exact PyPI/GitHub release artifact | Current source, S0 closure, professional use |
| Current-head wheel | SHA-256 `ab2ed108eaefc8763fd04cd7bdac9b60f1875930cf54ef7a1806b73f4432fcfd`; 253 members; source `49c2fe...`; tree `704190f...` | Current installed-user behavior and S0 artifact binding | A published release or qualified review |
| Current-head sdist | SHA-256 `8e8824d63cd0f47a49527c700d3c7f4d913f2515d3650010a685f2b4150103ae`; 288 members | Source-distribution content and source-free installation on macOS/Python 3.11 | Other platforms, every optional extra, publication |
| Embedded Excel workbench | SHA-256 `4cc492bfcbba456342c6358a8dcfe2749cafd723e9ee4fdaefa585f29e35ce63`; current library content identity `68ed0889316d65362d7861b298a47252574bb71a83a7f7013354c02036353a01` | Current wheel resource and source-free workbook definition | Installed Windows Excel/Office.js behavior |
| React/OpenAPI projection | 89 OpenAPI operations; OpenAPI owner SHA-256 `a45321c1d48da835863f24b9f9c69730f046fae526666822d2d34f5e980463bf` | Exact generated schema inventory | Exact-current browser journey or generated-client usability |
| Windows/external/professional evidence | `NOT_TESTED / HELD` at exact A0 identity | Honest absence | Nothing may infer it from macOS, source, CI, or generated parity |

The public release is a prerelease and its GitHub release reports
`isImmutable=false`. PyPI reports `provenance: null` for both public files, and
GitHub reports zero attestations for the public wheel digest. This is a supply-
chain/readiness gap, not evidence that the recorded SHA-256 identities are
wrong.

### 2.3 Maintained authority receipt

The entry receipt is
[`lib-pro-013-a0-entry-evidence.json`](lib-pro-013-a0-entry-evidence.json). It
binds the authority hashes and the live owners used below. At entry the control
plane held 116 operations with 102/102 scripts registered; the agent registry
held 16 roles; the skill registry held 14 maintained skills; the generated API
manifest held 199 service symbols; the classification census held 222 root
exports; the compatibility ledger reconciled 620 projections and 1,514 caller
records with zero ambiguous projections; and the capability authority held 13
supported and 8 held families.

## 3. Four-pass completion

| Pass | Scope | Evidence checkpoint | Result |
|---|---|---|---|
| A0.1 | G1, U1, U2, R2, R3 | Audit-of-audits, source-free 29-case UAT, 14 CLI entries, 222-export census, 620-projection ledger, validation census | Complete; recurrence and census gaps frozen |
| A0.2 | U3, U4, E1-E3, P1-P4 | Exact-wheel S0 replay, 460 class-bounded family/kernel/publication/REST cases, capability/evidence matrix, transport/Excel artifact probes | Complete; no new current-source P0; Windows/browser/professional holds preserved |
| A0.3 | R1, R4, R5, A1-A4, C1 | Wheel/sdist/extras, dependencies/platforms, active docs, Git/worktrees/CI/release, registries/retention, official peers | Complete; professionalism and retention decisions frozen |
| A0.4 | C2 and Section 7 gate | Deduplicated finding register, dependency-ordered portfolio, 42-row crosswalk | Complete; no unresolved current-source P0 |

The authoritative A0 estimate remains 15-24 engineer-days. Shared inventory,
accepted evidence reuse, and class sampling reduce repeated execution; they do
not reduce the audited universe.

## 4. Audit-of-audits and recurrence matrix

| Earlier authority | Original scope and useful proof | What it did not prove | Later counterexample | Confirmed recurrence mechanism | A0 prevention decision |
|---|---|---|---|---|---|
| 2026-04 professional-library audit | Broad repository score and remediation inventory | Exact installed artifact and every callable advertised route | Later direct external use found safe-looking invalid results | Aggregate score allowed decisive route gaps to be diluted | Gate promoted journeys and decisive P0/P1 independently of aggregate score |
| Professional remediation plan | Repaired batch/report/status and many package/repository outcomes within scope | Every direct/compatibility/nested public callable | LIB-PRO-011 direct-route failures | Route ownership was not derived from all advertising and callers | One advertised-journey-to-owner matrix; failing class expands to every maintained member |
| Pre-release input-safety audit | Exact-wheel project/CLI negative matrix and nine root causes | Direct expert, nested, compatibility, transport-export, and all family routes | LIB-PRO-011 and S0 found additional route classes | Negative inventory followed selected strict project/CLI routes | Generate route/field census from maintained public owners plus active advertised journeys |
| Historical folder audit | Identified folder/document drift and cleanup candidates | Current context-manifest/generated-owner model | Later MAINT-012B retired generated folder indexes | A historical index list was treated as current authority | `context validate` and live callers own current context; old indexes remain historical only |
| Automation/scripts audit | Reconciled the then-current 104/106 operation/script estate | Later additions and current execution callers | Current estate is 116 operations and 102/102 scripts | Snapshot counts age even when the audit was correct | Re-query control registry and automation projection; never copy old counts |
| MAINT-012A/B/C/D control/context/verification work | Established single owners, fail-closed routing, context and evidence schemas | Installed-user correctness | Green controls coexisted with external route defects | Registry conformance was used as product outcome evidence | Treat control/generation as evidence ownership, not engineering or user acceptance |
| LIB-PRO-010 release candidate/publication | Exact RC artifact and bounded public identity | Future source, later repairs, all active docs, qualified review | Public `0.24.0a1` predates S0 while active docs still contradict release truth | Release closeout did not reconcile every active advertised surface | R0 owns generated release truth and exact artifact-to-source reconciliation |
| LIB-PRO-011 external API audit | Reproduced route-bound P0/P1 failures with external-user journeys | Remediation implementation | S0 repaired the mapped P0 classes; wider census remains incomplete | Advertising, classification, and negative tests were separate inventories | U1/U2/U3 share one journey inventory and stable finding identities |
| S0 implementation and post-merge audit | Repaired the mapped current-source P0 routes and exact-wheel/REST boundaries | Whole-library readiness, public replacement artifact, Windows/professional evidence | A0 current wheel passes while public wheel remains older | Source safety, release status, and professional approval are different claims | Preserve separate evidence objects and separate authority gates |

No earlier audit is reclassified as failed merely because later work had a
larger scope. The recurrence decision is about missing ownership linkage, not
about retroactively changing accepted evidence.

## 5. Advertised journey and public contract inventory

### 5.1 Inventory outcome

| Journey class | Maintained source | Exact A0 outcome | Disposition |
|---|---|---|---|
| Select/install artifact | PyPI/GitHub, `Python/pyproject.toml`, release evidence | Public and current artifacts separately identified; current wheel and sdist install on macOS/Python 3.11 | R0 must publish only under separate release authority |
| Install preflight/version/origin | `install-preflight`, metadata/runtime identity | PASS from source-free current wheel and current sdist | Keep |
| Capability discovery | `capabilities`, capability JSON | PASS; CLI schema `2.0`; package report and 21-family repository authority are distinct inventories | Reconcile discoverability in F0/R0 |
| First valid/invalid Python result | root facade and exact-wheel UAT | 29/29 source-free UAT cases pass; S0 15 invalid classes reject; engineering `FAIL` remains typed | Keep repaired boundary; expand census in B0/F0 |
| CLI | `advertised_entry_points_v1.json`, `__main__.py` | All 14 registered commands reconcile and help loads | Keep; active docs still advertise one nonexistent `check` command |
| Batch/job/import/export | workflow catalogue, CLI, adapters, BBS/DXF/report | S0 beam/BBS chain and canonical transport exact-wheel probes pass; not every adapter/export/extra has exact-current source-free behavior proof | R0 closure, B0 where canonical contract changes |
| Family Python workflows | capability authority, services, family evidence | 13 bounded supported families; exact current selected family tests pass; only beam/slab/footing have current-wheel starter UAT | F0 construction/facade convergence; R0 recipes |
| REST | OpenAPI and 26 routers | 89 operations; all have maintained direct-test ownership; selected current routes pass; full route-field adversarial census incomplete | B0 canonical contract and R0 generated closure |
| WebSocket/streaming | FastAPI/WebSocket owners | Inventory exists; exact-current installed-user parity and timeout/error journey not replayed | B0/R0; no readiness claim |
| Generated client | OpenAPI/client generators | Generated drift is owned; no exact-current source-free compile/import/run across promoted journeys | R0 |
| React | React 19 client and hosted S0 checks | Hosted React tests/build passed for the accepted S0 tree; no exact-current browser, keyboard, large-batch, or API-bound artifact run in A0 | `NOT_TESTED / HELD`; R0 or separate installed UI evidence |
| Excel workbook | wheel resource and Excel artifact verifier | Source-free definition/resource PASS; explicit `TO_VERIFY_WINDOWS` | Windows owner/authority required |
| ETABS | snapshot/import owners and historical Windows lane | No exact-current installed ETABS acquisition/write-back evidence | `NOT_TESTED / HELD`; exact Windows ETABS authority required |
| Documentation examples | active README/getting-started/reference/cookbook | Some source-free examples pass; active cookbook and release/Streamlit paths fail or contradict current truth | R0 |

The package registry advertises 14 CLI entry points but active documentation
advertises many additional Python, REST, UI, notebook, adapter, and export
journeys. Therefore the CLI registry is not a complete promoted-journey owner.
No third API manifest is proposed: R0 must connect active advertising to the
existing API classification, workflow catalogue, OpenAPI, capability, and
artifact-UAT owners.

### 5.2 Public contract census

- Root classification: 222 exports -- 68 stable, 73 preview, 71
  compatibility, and 57 internal classifications can overlap by axis.
- Services manifest: 199 symbols; compatibility manifest: 199 symbols.
- Claim dispositions: 57 canonical, 54 advanced, 55 compatibility, 100 hold,
  and 33 internal records.
- Exactly one task is marked canonical: `design_beam_is456`. Its reference
  journey has eight maintained surface records across Python, CLI, REST,
  workflow, and React/manual catalogues.
- Validation census: 110 maintained functions and 763 parameters -- 141
  `PROVEN`, 167 `DELEGATED`, 326 `UNPROVEN`, and 129 `NOT_APPLICABLE`.
- Frozen S0 safety replay passes for 21 Python and 5 FastAPI target classes.
  That pass does not turn the remaining `UNPROVEN` census into proof.

## 6. Engineering scope and evidence-class matrix

### 6.1 Family reconciliation

| Capability | State | Current A0 evidence | Evidence/authority gap |
|---|---|---|---|
| IS 456 beam | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current-wheel valid/invalid, BBS/torsion, Python/CLI/FastAPI parity; accepted arithmetic/source evidence | Current qualified engineer review absent; public wheel predates S0 |
| IS 456 column | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current-wheel UAT plus maintained golden/regression and prior evidence | Arbitrary-layout P-M-M remains experimental; qualified review absent |
| IS 456 isolated footing | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current-wheel UAT and release-inclusion evidence | Exact-current independent professional review absent |
| IS 456 solid slab | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current-wheel UAT, built-in coefficient and family evidence | Held slab cases remain held; qualified review absent |
| IS 456 stair | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current selected kernel/publication/REST tests pass; accepted family chain | No exact-wheel starter recipe; qualified review absent |
| IS 456 wall | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current selected kernel/publication/REST tests pass; independent hand receipt reused after owner-byte check | No exact-wheel starter recipe; qualified review absent |
| IS 456 deep beam | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current selected kernel/publication/REST tests pass; independent hand receipt reused after owner-byte check | External bearing/nodal prerequisites and qualified review remain held |
| IS 456 flat slab | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current selected kernel/publication/REST tests pass; independent hand receipt reused after owner-byte check | React/release/qualified review and excluded panel cases held |
| IS 456 combined footing | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current selected kernel/publication/REST tests pass; frozen and non-frozen arithmetic receipts reused after owner-byte check | No exact-wheel starter recipe; qualified review absent |
| IS 456 strap footing | `SUPPORTED / IMPLEMENTED_BOUNDED` | Current selected kernel/publication/REST tests pass; frozen and non-frozen arithmetic receipts reused after owner-byte check | External slab/transfer verification and qualified review held |
| IS 456 raft foundation | `HELD / NOT_IMPLEMENTED` | Explicit capability hold | Separate approved scope, source, implementation, evidence, and review required |
| IS 456 pile cap | `HELD / NOT_IMPLEMENTED` | Explicit capability hold | Separate approved scope, source, implementation, evidence, and review required |
| IS 13920 beam detailing | `SUPPORTED / IMPLEMENTED_BOUNDED` | Exact-current selected tests pass after merged status-semantics repair | Qualified review absent |
| IS 13920 column detailing | `SUPPORTED / IMPLEMENTED_BOUNDED` | Exact-current selected tests pass after confinement-contract repair | Qualified review absent |
| IS 13920 beam-column joint SCWB | `SUPPORTED / IMPLEMENTED_BOUNDED` | Exact-current selected tests pass; represented `FAIL` remains distinct from replay success | Qualified review absent; excluded framing cases held |
| IS 13920 wall detailing | `HELD / NOT_IMPLEMENTED` | Explicit capability hold | Separately approved implementation and review required |
| IS 13920 foundation detailing | `HELD / NOT_IMPLEMENTED` | Explicit capability hold | Separately approved implementation and review required |
| IS 875 gravity-load generation | `HELD / NOT_IMPLEMENTED` | Explicit capability hold, despite non-code-specific gravity workflow software | Source/scope/implementation/review authority required |
| IS 875 wind-load generation | `HELD / NOT_IMPLEMENTED` | Explicit capability hold | Source/scope/implementation/review authority required |
| IS 1893 equivalent-static seismic | `HELD / NOT_IMPLEMENTED` | Explicit capability hold | Source/scope/implementation/review authority required |
| IS 1893 response-spectrum analysis | `HELD / NOT_IMPLEMENTED` | Explicit capability hold | Source/scope/implementation/review authority required |

All 13 supported families have `qualified_review_required=true`. Software
acceptance and a benchmark replay are not complete engineering approval.

### 6.2 Evidence classes

| Evidence class | Present at exact/current identity? | Correct use | Gap/disposition |
|---|---|---|---|
| Independent arithmetic | Reused for unchanged family owners; current beam/slab/footing UAT includes accepted arithmetic controls | Engineering benchmark evidence within the written family boundary | Not one current independent receipt for every promoted family/artifact combination; R0 evidence ledger |
| Controlled source example | Present in family/source receipts | Source-bound example only | Protected prose/images remain outside Git; no expansion in A0 |
| External-software comparison | Historical, not exact-current installed evidence | External comparison only when source/software/version/inputs are bound | Current Excel/ETABS comparison `NOT_TESTED / HELD` |
| Blind internal recomputation | Present in historical calculation-book/golden lanes | Falsification stronger than direct wrapper parity but still internal | Never call it independent review |
| Wrapper/transport parity | Current wheel Python/CLI/FastAPI and embedded Excel definition pass selected controls | Contract and quantity parity | Does not prove formulas independently; broaden only in B0/R0 |
| Generated regression | Current manifests/OpenAPI/tests and 460 selected tests pass | Drift and recurrence protection | Cannot satisfy independent arithmetic or professional review |
| UI projection | Hosted React tests/build at accepted tree | Client projection/build evidence | Exact-current browser/API/artifact identity `NOT_TESTED / HELD` |
| Qualified review | Required by every supported family | Separate practicing-engineer decision on exact scope/artifact/evidence | Exact-current receipt absent; authority required |
| `NOT_TESTED` | Explicit for current Windows, ETABS, browser/accessibility, several extras/platforms/performance | Truthful evidence state | Remains a hold, not a pass or a failure |

No valid golden engineering quantity changed during A0 replay. The selected 460
family/kernel/publication/REST cases passed, and the S0 current-wheel verifier
preserved beam steel `883.7158126109596 mm2`, torsion equivalent shear
`153.33333333333334 kN`, a nine-item valid BBS, typed engineering `FAIL`, and
fail-closed invalid intake.

## 7. Package, platform, repository, and professional-system truth

### 7.1 Packaging and dependencies

- `structural-lib-is456==0.24.0a1` requires Python `>=3.11`; Pydantic `>=2.0`
  is the sole required runtime dependency.
- The current wheel installs cleanly with Pydantic `2.13.4`, passes candidate
  identity/import/CLI help, and imports from its isolated `site-packages`.
- The current sdist contains 288 members, excludes tests/examples/research/
  ACI/EC2 content, installs cleanly, reports `0.24.0a1`, and loads CLI help.
- One current macOS/Python 3.11 source-free sample installed the `dxf`,
  `report`, and `validation` extras and imported ezdxf `1.4.4`, Jinja2 `3.1.6`,
  and jsonschema `4.26.0`.
- `render`, `pdf`, `cad`, `pmm`, and `docs` extras were not functionally
  exercised at the exact A0 artifact. Python 3.12/3.13, Linux, Windows,
  Docker/Colima, browser matrices, and offline/Colab installation were not
  reproduced in A0. They remain `NOT_TESTED`, not failed.
- React declares Node `24.x`, npm `>=11 <12`, React `19.2.8`, and a locked
  dependency graph. Hosted S0 checks used the maintained Node 24 lane; A0 did
  not rerun the full React suite.

### 7.2 Architecture, generated ownership, tests, and CI

- The four-layer `Core <- IS 456 <- Services <- UI` rule remains the
  architecture authority. Later family owner bytes were unchanged from their
  accepted receipts; only retired folder indexes changed in their code trees.
- `structural_lib.api` is a formula-free compatibility re-export to
  `structural_lib.services.api`; the compatibility ledger reports no ambiguous
  projection.
- Current inventory: 247 Python package modules, 100 FastAPI Python modules,
  187 React source files, 227 Python test files, 43 FastAPI test files, and 52
  React test/spec files.
- OpenAPI owns 89 operations across 26 router modules plus a WebSocket route;
  maintained parity reports 89/89 endpoint test ownership and 13/13 connected
  React hooks. These counts are ownership indicators, not installed-user or
  independent-engineering proof.
- Four active workflows remain: fast checks, weekly/manual nightly, docs
  deployment, and publication. Changed-path routing and required PR checks
  passed for S0. Weekly lanes own broader dependency, package, and optional
  cross-platform evidence; A0 did not substitute them for exact-current
  Windows or browser proof.
- `Python/tests/README.md`, `fastapi_app/tests/README.md`, and
  `CONTRIBUTING.md` contain stale direct interpreter/test/session commands and
  old structure assumptions. The live `run.sh`, worktree-bound Python runtime,
  and control registry remain authoritative.

### 7.3 Active documentation, support, release, and naming

- Distribution `structural-lib-is456`, import `structural_lib`, and repository
  `structural_engineering_lib` are distinct but documented in the root README.
  No rename is justified in A0; migration cost exceeds the current search
  benefit.
- Active README/Python README/getting-started/release pages still say
  `0.24.0a1` is prepared or unpublished and point to `0.23.1a2` as current,
  although `0.24.0a1` is public.
- `docs/cookbook/README.md` advertises nonexistent current-wheel journeys:
  `python -m structural_lib check`, `from structural_lib import design_beam`,
  and `from structural_lib import JobRunner`. Exact source-free replay returns
  an invalid CLI choice or `ImportError`.
- Active troubleshooting and 3D-contract pages retain retired Streamlit paths
  even though the task authority declares React the only active UI.
- `CONTRIBUTING.md` advertises `./run.sh session start`, while the maintained
  command is `session begin --task-id ... --agent ...`.
- Citation, contribution, conduct, issue templates, release policy, and MIT
  license exist. A root `SECURITY.md` does not. GitHub reports secret scanning
  and push protection enabled, but Dependabot security updates disabled.
- The publication workflow builds an SBOM and uses trusted-publisher OIDC, but
  the public PyPI files expose no PEP 740 provenance. No professional,
  stable-readiness, or supply-chain completeness claim follows from the
  artifact hashes alone.

### 7.4 Git, retention, and recovery

Eighteen worktrees were re-queried. No worktree, ref, stash, cache, archive,
branch, or ignored file was changed, cleaned, reset, rebased, retired, or
deleted. The primary `main` checkout remains clean at the older planning
baseline; the exact A0 linked worktree is the fetched-current implementation
lane. The previous S0 candidate worktree is clean and tree-equivalent to the
accepted merge.

The previously observed detached `e54a` lane remains at
`0fdb48edbb73114288feb8a246d6f30b80ac4d95` with one tracked modification,
`docs/SESSION_LOG.md`, plus ignored caches/session data. It remains untouched.
No `private_sources` directory exists in this worktree. The independent
Sourcebook and protected standards were not read or modified. Their absence
from this checkout is not backup evidence.

| Retained class | Observed state | Proposal | Authority required before mutation |
|---|---|---|---|
| Tracked `docs/_archive` (8.2 MB) | Historical, linked from active records | `KEEP`, clearly historical | Separate retention review before move/consolidation |
| Generated control/OpenAPI/API/capability owners | Current, caller-bound | `KEEP`; regenerate only from maintained source | Owner-specific generation authorization |
| Retired Streamlit references in active docs | Current user-facing drift, runtime already retired | `CONSOLIDATE/RETIRE` references during R0 | R0 documentation authority; no runtime restoration |
| Old multi-code/early product plans | Historical decisions, not current feature authority | `KEEP` as historical; label when active docs imply current scope | Planning owner before consolidation |
| Current A0 build/venv caches and ignored bytecode | Reproducible task by-products | `HOLD`, later safe cleanup only | Explicit cleanup scope if material |
| Detached and MAINT worktrees/refs | Preserved; one dirty detached lane | `HOLD/KEEP` | Exact owner approval plus recovery proof before deletion |
| Independent Sourcebook/protected standards | Outside this checkout and Git scope | `KEEP` protected/local/read-only | Owner plus legal/source and tested backup/restore authority |
| Ignored session/pipeline state | Active operational evidence | `KEEP` while sessions/retention require it | Session/retention owner |

## 8. Current official-source peer decisions

Access date for every source below: **2026-08-27**. Each source is used once;
popularity is not evidence.

| Official/primary source and comparable journey | Local finding | Decision | Benefit | Cost, compatibility/dependency effect, owner, gate |
|---|---|---|---|---|
| [NumPy module structure](https://numpy.org/doc/stable/reference/module_structure.html): recommended, special-purpose, legacy namespaces | 222 root exports and one canonical task make discovery noisy | `ADAPT` | Small beginner facade with explicit expert/compatibility routes | B0; preserve shims; no blind deletion; installed-wheel import gate |
| [NumPy NEP 23](https://numpy.org/neps/nep-0023-backwards-compatibility.html): deprecation impact and downstream testing | Compatibility entries lack one uniformly executable warning/replacement/removal journey | `ADAPT` | Predictable migrations tied to callers | B0/R0; Alpha policy and owner approval still control removal |
| [Pydantic strict mode](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/): reject coercion at chosen boundaries | S0 proves strict REST helps, while 326 parameter decisions remain unproven | `ADAPT` | Fail-closed intake with structured types | B0/F0; strictness is field/transport-specific and may break callers; exact compatibility matrix required |
| [PyPA packaging flow](https://packaging.python.org/en/latest/flow/): source tree, sdist, wheel, installed environment are distinct | Public and current artifacts were previously easy to conflate | `ADOPT` | Exact artifact truth and sdist/wheel parity | R0; no new dependency; build/install/content gate |
| [Pint dimensional wrappers](https://pint.readthedocs.io/en/latest/advanced/wrapping.html): quantity-aware boundaries | Explicit suffix units are widespread and serialization is frozen | `REJECT` for current programme | Avoids dependency/API/serialization churn without demonstrated outcome benefit | A future adapter needs separate benefit, provenance, performance, compatibility, and dependency approval |
| [Hypothesis introduction](https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html): round-trip/equivalence/property testing | Property evidence exists unevenly and cannot replace benchmarks | `ADAPT` | Add finite, round-trip, equivalence, monotonicity properties where engineering meaning exists | R0/F0; dev-only dependency already present; focused properties plus independent benchmarks |
| [StructuralCodes library structure](https://fib-international.github.io/structuralcodes/api/library_structure.html): equations, materials, geometry, calculators | Local four-layer rule is sound but facade growth obscures it | `ADOPT` existing rule | Clear formula and orchestration ownership | R0 architecture/import gate; do not introduce ambient code-selection state |
| [StructuralCodes section results](https://fib-international.github.io/structuralcodes/usage/sections/index.html): analysis-specific results with theory/conventions | Family result/status/provenance contracts are not uniform | `ADAPT` | Reviewable assumptions, axes, provenance, and limitations | B0/F0; compatibility carriers and migration fixtures required |
| [concreteproperties API](https://concrete-properties.readthedocs.io/en/latest/api.html): concept-grouped modules and result types | Family discoverability is weaker than raw export breadth | `ADAPT` | Family-oriented routes without forcing every helper into root/REST | F0; no dependency; source-free family recipes and facade gate |
| [anaStruct examples](https://anastruct.readthedocs.io/en/latest/examples.html): short modelling journeys | Several local advertised journeys are long, stale, or non-executable | `ADAPT` discovery only | Short first-use examples | R0; do not inherit mutable modeling defaults or claim analysis equivalence |
| [OpenSeesPy documentation](https://openseespydoc.readthedocs.io/en/latest/): compact model command journey and broad command catalogue | A large command surface is not a safe template for code-design intake | `REJECT` as API-state template; `ADAPT` example clarity | Clear navigable examples without importing global mutable state | F0/R0; no dependency or API-copying |
| [W3C WCAG 2.2 error identification](https://www.w3.org/WAI/WCAG22/Understanding/error-identification): identify and describe the exact invalid field in text | Exact-current browser error and keyboard evidence is absent | `ADOPT` as UI acceptance criterion | Accessible field-specific recovery | R0/installed UI evidence; no compliance claim until browser journey passes |
| [PyPI digital attestations](https://docs.pypi.org/attestations/): bind release files to trusted publisher/provenance | Public wheel/sdist have `provenance: null` | `ADOPT` for a future authorized release | Verifiable publication identity in addition to hashes | Release owner/R0; PEP 740 verification on exact future artifacts; does not prove safety |
| [GitHub repository security quickstart](https://docs.github.com/en/code-security/getting-started/quickstart-for-securing-your-repository): supported versions and vulnerability reporting | No root `SECURITY.md`; security updates disabled | `ADAPT` | Explicit reporting and response ownership | R0/repository owner; realistic support versions and response policy, no unsupported promise |

## 9. Deduplicated finding register

Shared identity for findings unless overridden: source
`49c2fe4553e923a7433ca0a5fa28ea364956ae30`, tree
`704190f7322b8c29bc4a85036d7ade54d355f306`, current wheel
`ab2ed108...fcfd`, public wheel `b5e0df7b...6201a`, public tag
`71b70652...16efc`. Evidence states use `REPRODUCED`, `PROVEN`, `PARTIAL`,
`NOT_TESTED`, or `HELD`.

| Finding | Domain, priority, evidence | Journey, expected/observed, impact | Cause, owner, compatibility, disposition, dependency | Focused proof, cumulative gate, provenance, review boundary |
|---|---|---|---|---|
| `LIB-PRO-013-A0-ART-001` | Versions/release/artifact; **P0 public-artifact exposure, CLOSED in current source**; `PROVEN` | Install public `0.24.0a1` vs current wheel. Expected: artifact identity determines behavior. Observed: public files predate S0; current wheel rejects repaired invalid routes. Impact: public artifact must not be described as S0-safe/current-ready. | Confirmed cause: release preceded S0. Owner R0 + release owner. Compatibility: requires a new version, never overwrite `0.24.0a1`. Disposition: current runtime root cause closed; public-use hold. Dependency: owner-selected release candidate and authorization. | Public/current hashes; S0 exact-wheel verifier. Gate: future exact artifact UAT, provenance, hosted release and public identity. Provenance: S0 acceptance/PyPI/GitHub. Review: no release or engineering-use claim. |
| `LIB-PRO-013-A0-DOC-001` | Documentation/release/discovery; **P1**; `REPRODUCED` | README/release/cookbook/contributing/Streamlit paths. Expected: active docs execute and match current release/UI/commands. Observed: contradictory release truth, three failing cookbook journeys, wrong session command, retired UI paths. Impact: a new user follows invalid paths. | Confirmed cause: prose snapshots are not bound to live artifact/control/advertising owners. Owner R0. Compatibility: preserve valid aliases; correct active docs. Disposition: R0. Dependency: A0 journey matrix. | Exact source-free CLI/import reproducers and active-doc search. Gate: executable exact-wheel examples, link/docs/generated truth, no active retired UI path. Provenance: active docs at source identity. Review: docs only, no runtime repair in A0. |
| `LIB-PRO-013-A0-CENSUS-001` | Public contracts/recurrence; **P1**; `PROVEN` | Compare 14 CLI registry entries with active Python/REST/React/notebook/export advertising. Expected: every promoted journey has an owner/test. Observed: existing registries reconcile internally but no one owner spans advertising. Impact: routes can escape negative/artifact gates. | Confirmed cause: advertising, API classification, workflow, capability, OpenAPI, and UAT inventories are separate. Owner R0 with B0/F0 consumers. Compatibility: no third manifest; connect existing owners. Disposition: R0 foundation. Dependency: before B0/F0 completion. | Registry counts and active-doc census. Gate: advertised-journey-to-owner completeness. Provenance: maintained owners. Review: outcome-owning journeys only. |
| `LIB-PRO-013-A0-VAL-001` | Validation/signatures; **P1**; `PARTIAL` | 110 functions/763 parameters. Expected: decision/proof for every promoted field/route. Observed: 326 `UNPROVEN`; S0 21 Python + 5 FastAPI classes pass. Impact: unknown invalid-intake behavior outside frozen S0 classes. | Cause unconfirmed per route; systemic cause is incomplete declarative coverage. Owner B0 for common/canonical beam, F0 for family contracts, R0 for generated evidence. Compatibility: route-specific migration. Disposition: B0 -> F0 -> R0. | `audit_input_validation.py` census; S0 safety PASS. Gate: every promoted field decided; failing class expands to all members. Provenance: source AST/owners. Review: do not infer a defect from `UNPROVEN`; reproduce before repair. |
| `LIB-PRO-013-A0-API-001` | Facade/naming/compatibility; **P1**; `PROVEN` | Discover recommended Python route. Expected: small beginner facade plus explicit advanced/compat routes. Observed: 222 root exports, 199 service symbols, 620 projections, one canonical task. Impact: first-use choice and deprecation responsibility are unclear. | Confirmed cause: generations accumulated through re-exports. Owner B0 common contract then F0 family construction. Compatibility: retain formula-free shims with warning/replacement/time policy before removal. Disposition: B0/F0. Dependency: CENSUS/VAL. | Classification/compatibility ledgers. Gate: installed imports and caller ledger. Provenance: generated owners. Review: no broad deletion or `/api/v2` in A0. |
| `LIB-PRO-013-A0-RESULT-001` | Errors/results/composition; **P1**; `PARTIAL` | Invalid intake, `FAIL`, `HOLD`, internal error, downstream artifact. Expected: stable typed distinctions across promoted families/transports. Observed: repaired beam chain passes, but no uniform all-family result protocol/transport proof exists. Impact: consumers may parse family-specific shape/text or create inconsistent downstream handling. | Cause state: mixed historical contract generations, exact manifestations to be reproduced before change. Owner B0 then F0. Compatibility: versioned carriers/migration fixtures. Disposition: B0/F0. Dependency: API/VAL. | S0 valid/invalid/FAIL replay, family contract census. Gate: common protocol plus family registry and artifact-stop proofs. Provenance: current wheel/source. Review: no claim that every family is defective. |
| `LIB-PRO-013-A0-FAMILY-001` | Family construction/usability; **P1**; `PROVEN` | Select and construct each of 13 supported families from installed wheel. Expected: one executable recipe/builder with enums/evidence/assumptions. Observed: capability discovery works; exact-wheel starter UAT is concentrated on beam/slab/footing. Impact: users must discover owner modules or guess nested evidence. | Confirmed cause: family publication outpaced unified installed-user recipes. Owner F0; R0 documents. Compatibility: add builders/family routes without promoting every helper. Disposition: F0/R0. Dependency: API/VAL/RESULT. | Capability matrix, 460 selected current tests, source-free UAT inventory. Gate: one exact-wheel valid/invalid recipe per supported family. Provenance: accepted family receipts/current owner-byte comparison. Review: no feature-scope expansion. |
| `LIB-PRO-013-A0-TRANSPORT-001` | REST/WebSocket/generated clients; **P1**; `PARTIAL` | Compare canonical Python with 89 REST operations, WebSocket, generated clients. Expected: strict/status/provenance parity and exact client compile/run. Observed: selected beam transport passes; OpenAPI/direct-test ownership is complete; full exact-artifact client/WebSocket parity is not. Impact: generated or streaming consumers lack complete installed proof. | Cause state: transport generations and incomplete exact-artifact journey linkage. Owner B0, closure R0. Compatibility: preserve v1 while deciding replacements; no `/api/v2` in A0. Disposition: B0/R0. Dependency: API/RESULT. | OpenAPI 89, selected exact-wheel FastAPI, client drift owner. Gate: exact-head client compile/import/run plus route matrix. Provenance: current OpenAPI/source. Review: direct-test ownership is not full parity. |
| `LIB-PRO-013-A0-EVIDENCE-001` | Engineering evidence/professional boundary; **P1**; `PROVEN` | Review 13 supported families. Expected: explicit evidence classes and exact qualified review where claimed. Observed: accepted arithmetic/source/regression varies; all require qualified review; exact-current qualified receipt absent. Impact: software PASS can be overread as engineering approval. | Confirmed cause: implementation/acceptance evidence is not a professional approval. Owner R0 evidence ledger + qualified engineer authority. Compatibility: none to runtime. Disposition: R0/hold. Dependency: exact integrated artifact before qualified review. | Family/evidence matrices. Gate: reviewer identity/scope/artifact/limitations and separate approval axes. Provenance: capability authority and receipts. Review: professional use remains false. |
| `LIB-PRO-013-A0-WINDOWS-001` | Excel/ETABS/platform; **P1**; `NOT_TESTED / HELD` | Install exact current artifact in Windows Excel/ETABS. Expected: bound add-in/import/units/error/refresh/write-back evidence. Observed: source-free workbook definition passes on macOS; explicit `TO_VERIFY_WINDOWS`; no exact ETABS run. Impact: Windows behavior cannot be claimed. | Cause: required environment/authority unavailable in A0, not a reproduced software defect. Owner Windows Excel/ETABS operator. Compatibility: no source inference. Disposition: hold. Dependency: exact installed artifact, Office/ETABS versions, dataset, evidence capture. | Excel artifact verifier only. Gate: installed Windows journey and independent comparison. Provenance: exact workbook/current wheel. Review: Mac/CI cannot satisfy. |
| `LIB-PRO-013-A0-UI-001` | React/browser/accessibility; **P2**; `NOT_TESTED / HELD` | Exact browser import/input/design/3D/status/error/export/keyboard/large batch. Expected: API/artifact identity and field-specific errors. Observed: hosted S0 React tests/build pass; no exact-current browser journey. Impact: installed UI outcome and accessibility remain unknown. | Cause: A0 lacked a bound running installed stack/browser evidence lane. Owner R0 or separate UI evidence packet. Compatibility: preserve routes/components. Disposition: R0/hold. Dependency: exact API/client build/dataset. | Hosted S0 run + absence of browser receipt. Gate: browser/API/artifact matrix, WCAG field-error/keyboard checks. Provenance: accepted source tree. Review: no accessibility claim. |
| `LIB-PRO-013-A0-PACKAGE-001` | Packaging/dependencies/platforms; **P2**; `PARTIAL` | Install wheel/sdist/extras across claimed matrix. Expected: tested or explicit untested combinations. Observed: macOS/Python 3.11 core, sdist, dxf/report/validation pass; other extras/platforms not tested. Impact: optional/system-dependent paths may fail outside sampled lane. | Cause: matrix wider than release-UAT sample. Owner R0. Compatibility: avoid dependency changes without benefit/cost. Disposition: R0. Dependency: exact candidate and supported-platform decision. | Candidate check, sdist install, extras imports. Gate: purpose/license/security/platform/functional extra matrix. Provenance: pyproject/lock/workflows/current artifacts. Review: untested is not failed. |
| `LIB-PRO-013-A0-SUPPLY-001` | Supply chain/security/support; **P2**; `PROVEN` | Verify public provenance/security response. Expected: artifact provenance and realistic reporting/support policy. Observed: hashes/SBOM workflow exist; PyPI provenance null, GitHub release mutable, no root SECURITY.md, security updates disabled. Impact: consumers cannot verify publisher provenance or find a complete vulnerability-response contract. | Confirmed cause: publication/support controls stop at hashes, OIDC workflow, issue templates, and internal evidence. Owner R0 + repository/release owner. Compatibility: none to runtime. Disposition: R0/future release. Dependency: owner policy and new authorized release. | PyPI/GitHub live queries and repo policy inventory. Gate: PEP 740 verify, immutable/identity decision, SECURITY.md/support versions, response owner. Provenance: official services at access date. Review: attestations do not prove safety. |
| `LIB-PRO-013-A0-TESTDOC-001` | Test architecture/docs; **P2**; `REPRODUCED` | Follow test READMEs/contributor start. Expected: current worktree-bound commands/taxonomy. Observed: stale direct pytest/interpreter/destructive cache/session commands and old counts. Impact: contributors run wrong or unsafe workflows and evidence categories drift. | Confirmed cause: hand-maintained docs were not bound to control/session/test owners. Owner R0. Compatibility: docs only. Disposition: R0. Dependency: current test taxonomy. | Live file counts and active README replay. Gate: maintained callers, link/docs checks, no destructive shortcut. Provenance: source docs/control. Review: no tests added for coverage in A0. |
| `LIB-PRO-013-A0-RETENTION-001` | Retained/protected data and recovery; **P2**; `HELD` | Prove every retained lane and protected source is recoverable before cleanup. Expected: preservation manifest plus tested restore for material local-only data. Observed: worktrees preserved, e54 dirty known, no stash; Sourcebook/protected sources are outside checkout and no exact restore proof was obtained. Impact: cleanup could lose local evidence/source if inferred safe. | Cause: retention authority is intentionally separate and local-only sources are not Git-backed. Owner MAINT/Sourcebook owner. Compatibility: none. Disposition: HOLD/KEEP. Dependency: exact manifest, owner approval, tested encrypted off-device restore. | Live worktree authority and preservation observations. Gate: recovery proof before any mutation. Provenance: local Git authority only. Review: no deletion authorized. |
| `LIB-PRO-013-A0-PERF-001` | Performance/resource/accessibility; **P3**; `NOT_TESTED` | Import/single/batch/memory/render/API load/large report. Expected: reproducible outcome-linked thresholds only if claimed. Observed: no exact-current baseline run in A0. Impact: no performance claim; no demonstrated main-process defect. | Cause unconfirmed; no claim requiring a threshold was promoted. Owner R0 if needed. Compatibility: benchmark design must avoid brittle thresholds. Disposition: P3, outside C2 remediation until an outcome/claim requires it. | Explicit non-run. Gate: exact environment/dataset/threshold. Provenance: none. Review: do not add speculative work. |

Priority summary: one known public-artifact P0 whose runtime root cause is
already closed in current source; nine P1 findings; five P2 findings; one P3
observation. There is **no new or unresolved current-source P0**.

## 10. C2 dependency-ordered remediation portfolio

| Order | Route | Findings and outcome owner | Effort class | Acceptance boundary |
|---|---|---|---|---|
| 0 | Existing source safety closure | `A0-ART-001` current-source root cause | Closed; no A0 repair | Preserve S0 exact-wheel regressions; never overwrite public `0.24.0a1` |
| 1 | **B0 common contract/canonical beam/downstream convergence** | `VAL-001`, `API-001`, `RESULT-001`, `TRANSPORT-001` canonical/common portions | `L` | Every promoted field decided; canonical result/status/provenance; invalid state cannot create artifact; compatibility fixtures pass |
| 2 | **F0 family facade/construction convergence** | `VAL-001`, `API-001`, `RESULT-001`, `FAMILY-001` family portions | `XL` | One exact-wheel valid/invalid recipe and builder per supported family; no scope expansion; family status/evidence/provenance consistent |
| 3 | **R0 cumulative documentation/generated/package/independent-audit closure** | `DOC-001`, `CENSUS-001`, `TRANSPORT-001`, `EVIDENCE-001`, `UI-001`, `PACKAGE-001`, `SUPPLY-001`, `TESTDOC-001` | `XL` | Active docs executable; journey-owner completeness; client/browser/package matrices; evidence ledger; cumulative artifact audit; exact hosted/release gates only with separate authority |
| 4 | **Separate P0 safety repair** | None newly reproduced | `NONE` | If later replay exposes a new safe-looking invalid result, stop and authorize a bounded repair before continuing |
| 5 | **Explicit holds** | `WINDOWS-001`, `RETENTION-001`, qualified review/professional approval, future release/publication | External authority | Exact Windows operator evidence; tested restore/owner approval; qualified engineer receipt; owner-selected version and release authorization |
| 6 | Outside outcome portfolio | `PERF-001` and cosmetic/speculative concerns | P3 | Activate only when a claim or observed main-process outcome requires it |

Dependencies are `CENSUS -> B0 -> F0 -> R0 exact integrated artifact ->
qualified review/release decisions`. R0 may prepare evidence and documentation,
but it cannot select a release, publish a tag/package, or grant professional
approval. Windows and protected-data holds may run as independent evidence
lanes only when their exact authorities are available.

## 11. Section 7 coverage crosswalk (42/42)

`This report` below means this canonical evidence document plus the entry
receipt and named maintained owners; it is not a new generated authority.

| # | Section 7 domain | Owner | Method and evidence artifact | Disposition |
|---:|---|---|---|---|
| 1 | Product purpose and personas | R0/product owner | Claim boundary, journey inventory, active docs; this report §§1,5,7 | Alpha/software-only; careful engineer/integrator/reviewer paths, no professional-ready claim |
| 2 | Supported engineering scope | F0/R0 | 21-family capability reconciliation; §6.1 | 13 bounded supported, 8 held |
| 3 | Formula and numerical evidence | R0/qualified reviewer | Evidence-class and family receipts; §6.2 | Reuse unchanged accepted evidence; gaps held |
| 4 | Public Python facade | B0/F0 | 222-export classification and 620-projection ledger; §5.2 | Converge later; no A0 deletion |
| 5 | Signatures and naming | B0/F0 | Validation census, classification, exact wheel; §§5.2,9 | 326 unproven decisions routed |
| 6 | Input construction | F0 | Family journey matrix; §§5.1,6.1 | Exact-wheel recipe per family required |
| 7 | Validation | B0/F0/R0 | 763-field audit plus S0 replay; §§5.2,9 | Class expansion after reproduction |
| 8 | Errors and statuses | B0/F0 | S0 valid/invalid/FAIL and result finding; §§5,9 | Typed convergence required |
| 9 | Results and provenance | B0/F0 | Artifact/result/evidence matrices; §§2,6,9 | Common protocol plus family registry |
| 10 | Composition/downstream artifacts | B0/R0 | S0 BBS/DXF and exact transport artifacts; §§5,9 | Broader chain closure later |
| 11 | CLI and batch | R0 | 14 CLI reconciliation, source-free UAT; §5 | CLI owner passes; active docs repaired later |
| 12 | FastAPI/WebSocket/streaming | B0/R0 | 89-operation OpenAPI and selected exact-wheel REST; §§5,9 | REST/client parity partial; WebSocket held |
| 13 | Generated clients | R0 | OpenAPI/client generator ownership; §§5,9 | Exact compile/import/run required |
| 14 | React workbench | R0/UI evidence owner | Hosted S0 React vs missing browser receipt; §§5,9 | `NOT_TESTED / HELD` exact browser |
| 15 | Excel and ETABS | Windows evidence owner | Current workbook artifact probe; §§2,5,9 | `NOT_TESTED / HELD` installed Windows/ETABS |
| 16 | Reports/BBS/CAD/exports | B0/R0 | Current wheel transport/extras sampling; §§5,7 | Selected paths pass; full extras/artifact matrix R0 |
| 17 | Distribution/import/repository names | R0 | README/metadata/import census; §7.3 | Keep names; clarify discovery |
| 18 | Packaging and installation | R0/release owner | Wheel/sdist/core/extras install; §§2,7 | Mac/Python 3.11 partial pass; matrix remains |
| 19 | Versions and release truth | R0/release owner | Public/current artifact identities and docs; §§2,7,9 | Public artifact held; active docs repair |
| 20 | Dependencies | R0 | pyproject/lock/workflows and extras sample; §7.1 | Purpose/support matrix; no A0 dependency change |
| 21 | Runtime and platforms | R0/platform owners | Python/Node/workflow declarations and tested states; §7.1 | Untested platforms explicit |
| 22 | Architecture and ownership | R0 | Four-layer rule, owner-byte comparison, generated registries; §7.2 | Pass/recheck at candidate |
| 23 | Data models/serialization | B0/F0 | Result/transport census, finite S0 replay; §§5,9 | Versioned convergence later |
| 24 | Compatibility/deprecation | B0/R0 | 620 projections/1,514 callers/NumPy peer; §§5,8 | Formula-free shims; explicit policy before removal |
| 25 | Tests and fixtures | R0 | Live file inventory, selected 460, README audit; §§6,7,9 | Taxonomy/docs repair |
| 26 | Benchmark independence | R0/qualified reviewer | Nine-class evidence matrix; §6.2 | Never promote generated parity |
| 27 | Performance/resource use | R0 if claimed | Explicit A0 non-run; finding `PERF-001` | P3/`NOT_TESTED` |
| 28 | Numerical robustness | B0/F0/R0 | S0 invalid/finite checks, family tests, evidence taxonomy | Selected classes pass; census/property closure later |
| 29 | Security/privacy | Repository owner/R0 | GitHub security settings, support inventory, existing checks; §§7,9 | SECURITY/support response gap; no speculative runtime issue |
| 30 | Supply chain/licensing | Release owner/R0 | MIT/license, hashes, SBOM workflow, PyPI/GitHub provenance; §§2,7,8 | PEP 740 and immutable identity future gate |
| 31 | Documentation/examples | R0 | Exact source-free active-doc reproducers; §§5,7,9 | P1 repair portfolio |
| 32 | Accessibility/international use | UI/R0 | W3C peer and explicit browser non-run; §§8,9 | `NOT_TESTED / HELD` |
| 33 | Support/professional policy | Repository/qualified-review owners | Citation/contribution/issues/release/SECURITY inventory; §§7,9 | Separate policy/reviewer/approval gates |
| 34 | Git/worktrees | Governance | Live Git/worktree/stash/overlap authority; §§2,7 | Safe A0 lane; all retained data preserved |
| 35 | CI/hooks/release workflows | Governance/release owner | Four workflows, S0 hosted run, routing/control evidence; §7.2 | One A0 candidate/PR/hosted cycle; release held |
| 36 | Agents/instructions | Governance | Complete AGENTS reading, 16-role registry, instruction validators; §§2,7 | Current owner map; candidate recheck |
| 37 | Skills | Governance | 14-skill registry/caller authority | Keep current; use/outcome inventory retained for R0 governance, no speculative retirement |
| 38 | Automations/tools | Governance | 116 operations, 102/102 scripts, automation projection; §§2,7 | Current control owner; no phantom command authority |
| 39 | AI efficiency | Governance | One parent/session/branch; shared inventories; class sampling; candidate counters | Policy conformant; exact usage checkpoint at closeout |
| 40 | Old/archived/generated/local data | Retention owners | Size/state/worktree/protected-source inventory; §7.4 | KEEP/HOLD/CONSOLIDATE proposals; no mutation |
| 41 | Early-project decisions/dead paths | Planning/R0 | Streamlit, root stubs, multi-code plans, API generations; §§7.3-7.4 | React remains active; stubs formula-free; historical plans labelled |
| 42 | Peer comparison | C1/R0/B0/F0 | 14 current official/primary sources; §8 | ADOPT/ADAPT/REJECT decisions with local gates |

## 12. Issues, root causes, and proof

### Issues encountered

- The first GitHub release query requested unsupported field `isLatest`.
- `./run.sh context show governance` used a role name where the command expects
  a maintained context area.
- One shell search used an unmatched quote and another used an unmatched
  no-result glob; neither mutated data.
- A first source-free wheel environment used `--system-site-packages` and
  `--no-deps`, then failed because the selected base interpreter did not carry
  the wheel's required Pydantic dependency.
- `./run.sh pipeline status` was guessed, while the maintained command exposes
  `show` for a previously created pipeline; A0 did not create a pipeline.
- A root `pyproject.toml` was assumed in one inspection; this repository's
  package owner is `Python/pyproject.toml`.
- The first consolidated documentation check rejected this new report's
  `doc_type: verification`; the allowed equivalent is `reference`. The same
  check also reproduced the pre-existing `status: ready` metadata on the
  already-merged A0 execution plan, outside this evidence-only repair scope.
- The first official-source URL loop used shell scalar expansion and passed
  all newline-separated URLs as one malformed URL.
- The public/current artifact split, active documentation drift, unproven
  validation census, missing exact Windows/browser/professional evidence, and
  missing public provenance are material audit findings captured in §9.

### Root causes and resolutions

- Invocation issues were confirmed as interface/path assumptions, not product
  defects. Each read-only query was rerun with supported fields, maintained
  areas, safe quoting, and exact package paths. No partial mutation occurred.
- The report metadata cause was an unverified front-matter vocabulary choice.
  Resolution: use the maintained `reference` type and rerun the focused
  front-matter check. The execution plan's `status: ready` is preserved as a
  pre-existing R0 documentation-contract finding because A0 may not repair
  unrelated planning metadata.
- The official-source loop cause was zsh scalar semantics, not an unreachable
  source. Resolution: feed one extracted URL per line to a `while read` loop
  and require an accepted HTTP response for all 14 sources.
- The source-free import failure was caused by intentionally suppressing
  declared dependency installation, not by the wheel. The exact same wheel was
  installed with its declared `pydantic>=2.0` dependency and all 29 UAT cases,
  package-candidate checks, and CLI help passed.
- The public/current artifact distinction is caused by the public release
  preceding S0. The current-source root cause is already repaired and proved;
  the correct resolution is an explicit future release decision, never a
  rewrite of `0.24.0a1` and never an A0 runtime change.
- Active documentation drift is confirmed to result from prose snapshots not
  being connected to current release/control/advertised-journey owners. Exact
  source-free command/import failures prove the impact; R0 owns resolution.
- The remaining validation/result/family/transport gaps arise from separate
  generations and incomplete cross-owner census. Individual route defects are
  not inferred from an `UNPROVEN` state; B0/F0 must reproduce failing classes
  before implementation.
- Missing Windows/browser/qualified-review evidence is an unavailable evidence
  lane, not proof of a defect. Exact installed environment/operator/reviewer
  authority is required to resolve each hold.
- Missing public provenance and security-reporting policy are confirmed live
  release/repository-control gaps. R0 and the release/repository owner must
  address them on a future authorized artifact/policy cycle.

## 13. Completion and remaining authority

A0 completion means the initial renewal audit through C2 is frozen and every
domain/finding has a dependency-ordered disposition. It does **not** mean the
library is release-ready, stable, independently validated across all families,
professionally reviewed, or approved for engineering use.

Remaining holds require these exact authorities:

1. **B0/F0 implementation:** a new explicit owner authorization after this A0
   evidence is integrated; A0 itself grants none.
2. **R0 closure:** explicit activation after B0/F0 integration or a separately
   approved documentation/evidence-only packet with no claim inflation.
3. **Windows Excel/ETABS:** a named operator with exact Windows, Office/add-in,
   ETABS version, installed artifact, dataset, and captured result identities.
4. **Qualified review/professional approval:** a practicing structural engineer
   reviewing an exact integrated artifact, bounded family claims, independent
   evidence, limitations, and review receipt; approval remains a separate
   decision.
5. **Release/publication:** owner-selected new version, per-release
   authorization, exact candidate/artifact gates, hosted publication workflow,
   public identity/provenance verification, and no overwrite of `0.24.0a1`.
6. **Protected sources/retained lanes:** owner approval, exact target manifest,
   legal/source boundary, and tested recovery before any mutation.

The next programme state after a green A0 integration is **hold for an explicit
owner decision on B0**, not automatic implementation.
