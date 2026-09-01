---
owner: Main Agent
status: active
last_updated: 2026-08-31
doc_type: reference
complexity: advanced
tags: [etabs, w3, research, api, planning, efficiency]
---

# Whole-W3 research and completion audit

## Decision

Put saved-model evidence and physical suitability ahead of further COM
diagnostics. W3's useful data/audit/review foundation exists; actual-building
calibration, complete candidate checks, screening, reanalysis and final
integration do not. Finishing a getter is not the same as finishing W3.

The [master plan](etabs-data-analysis-optimization-foundation-plan.md#whole-w3-execution-reset-2026-08-31)
owns execution order. This report supplies the evidence and alternatives. It
does not authorize application actions, change public capabilities, remove
acceptance gates, or reopen a frozen attempt.

## Audit boundary and method

- Fresh fetch and GitHub inspection verified PR #933 merged at
  `ce9c799030754cbb105a308f45da9f66434392a8`, tree
  `8562f8fb0b9ce2b3320787ffec21d4ac62543206`. All 36 predecessor worktrees
  were inspected; no open task-owned candidate PR was found. Unrelated
  dependency PRs and dirty predecessor lanes remain untouched.
- Read the complete W3 roadmap, task/handoff owners, software owners for
  beam audit/solver/comparison/dossier, and accepted W3D-H/J/repair receipts.
  The four planned screening/reanalysis service definitions remain absent.
- Studied installed CHM topics and retained assembly/wrapper signature
  evidence; read current official CSI release notes, API guidance and export
  documentation, and Microsoft JSON documentation. No application attachment,
  model extraction, benchmark, solver, design, installation or UI action.
- Inspected the authorized saved model's sibling text backup as text, with
  file identities recorded externally. Only section/record inventory was
  performed: no claim of a validated engineering parser or complete mapping.
- External evidence lives under `ETABS-W3-WHOLE-PLAN-AUDIT-20260831`.
  Proprietary text, model paths and installed help remain outside Git. The
  [safe receipt](../verification/etabs-w3-whole-plan-audit-evidence.json)
  binds the outputs. This is a static/saved-evidence audit, not fresh live state.

## Repeated problems that change the outcome

| Finding | Evidence and cause | Correction and exit |
|---|---|---|
| Tests stopped short of the real command twice | #932 tested the table stand-in but omitted model guards; #933 tested the compiled client but the separate outer launcher failed first. The newest JSON timestamp cause is confirmed; the older COM binder internals are not. | One executable path for disk contract parsing, real collectors, guards, client, raw logging and postflight. Test that exact CLI process offline and exercise real host collection with attachment disabled before freezing any live observation. |
| Transport diagnosis became the default next milestone | #931-#933 produced no catalogue/schema; the accepted saved-mapping assessment still has zero calibration-ready mappings. | First identify which physical input is missing and the cheapest trustworthy source. A transport task must name the acceptance row it can close. |
| A saved input source was not incorporated in the active route | A 271,593-byte `.$et` backup exists beside the authorized EDB. It contains connectivity, assignments, frame/shell loads, analysis options and design settings. | Reconcile this saved source first. Filename/time coincidence is insufficient: require semantic joins to accepted identities before using values. |
| Signature presence was too close to semantic acceptance | Installed `cAreaObj.GetLoadUniformToFrame` is marked NOT APPLICABLE; `cLineElm.GetLoadDistributed` exposes parameter types without adequate physical interpretation. | Retain raw values and source semantics separately. Do not assume a callable signature yields complete slab-to-beam transferred loading. |
| Completed and pending work share imperative wording | The master plan still said no solver exists, described the repaired Pareto defect as current, and instructed a two-span benchmark that has already passed. TASKS left W3H integration pending. | Replace active status, mark original specifications/estimates as historical, and maintain one current sequence. Keep immutable receipts unchanged. |
| Other hard dependencies were hidden behind W3H | W3E's canonical serviceability path still holds; W3I lacks complete criteria and implementation; W3K/L are unimplemented. | Make serviceability, constructability, applicability, objectives and whole-model safeguards explicit deliverables. Preparing these specifications does not authorize candidate screening. |
| Numerical agreement can be mistaken for model suitability | Current solver has zero-settlement vertical supports; inspected building joints move, slab/support basis is incomplete, and all 153 result members have some excluded-action component. | Decide declared comparability before solving. Nonzero excluded actions alone are not an engineering failure threshold. No support/tolerance fitting or blanket rejection of every building member. |
| Small diagnostic packets repeated fixed overhead | Five recent W3H packets each created a candidate and hosted run. | Batch coherent preparation and evidence into an outcome-sized packet; retain required checks, one quick gate after content freeze, and one cumulative broad gate at integration. |

The failure ledger must keep three causes distinct: historical Python CSI 1
is unconfirmed; managed guard binding is unconfirmed internally; the latest
PowerShell ISO-string/DateTime mismatch is confirmed. None establishes a
licensing fault. Changing language, reinstalling ETABS or rerunning analysis
is not an evidence-backed repair for these observations.

## Measured cost, with limits

| Retained W3H packet | Recorded session minutes | Outcome |
|---|---:|---|
| Saved-building mapping | 19.207 | Physical input gaps enumerated |
| Installed mapping signatures | 25.208 | 40 signatures checked; semantics remain incomplete |
| Table metadata | 32.238 | First display getter returned CSI 1 |
| Table transport | 39.205 | Managed guard binding stopped before table call |
| Typed guard | 30.694 | Outer timestamp check stopped before attachment |
| **Subset total** | **146.552** | **Five candidates / five hosted runs** |

The last three total 102.137 minutes. These are retained session-clock
observations, not all W3 time, CPU time, token cost, or a measured attribution
of waste. Useful offline proof was produced. The latest quick gate's external
203.098 seconds included 166.593 seconds of preparation and 29.688 seconds
of internal check wall time; those measures have different boundaries and
must not be added as independent work. Avoid repeating unchanged preparation;
do not remove safeguards to meet an invented speed target.

## Official research and practical consequences

1. CSI directs API users to the installed CHM documentation. Installed
   signatures/help plus observed version-bound behavior should therefore
   control the adapter, with older web examples used only for concepts.
   [CSI OAPI FAQ](https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2000456/OAPI%2BFAQ).
2. The current 23.3 release adds SQLite table export and .NET 10 COM client
   support. These are documented capabilities, not proof of successful access
   on this host. The listed table-API fix concerns editing/versioning, not our
   failed display getter. There is no matched root-cause fix in these release
   notes for the observed CSI 1.
   [ETABS 23.3.1/23.3.0 release notes, tickets 12022, 12108 and 12183](https://www.csiamerica.com/software/ETABS/23/ReleaseNotesETABSv2331plus2330.pdf).
3. CSI describes `.$et` as a text backup written with a model save, and E2K
   export as equivalent text. It is not a substitute for the binary model or
   proof of analysis results. The existing sibling file therefore deserves
   inspection before requesting a new export; do not import it or resave the
   model during this investigation.
   [CSI Saving Models](https://docs.csiamerica.com/help-files/etabs/Menus/File/Saving_Models.htm).
4. Table visibility/filter settings matter: the UI distinguishes all possible
   tables from tables used by the model and supports selected table exports.
   A successful export still needs exact selections, units, schemas, row
   accounting and revision proof.
   [CSI Choose Tables](https://docs.csiamerica.com/help-files/etabs/Keyboard_Commands_and_Special_Features/Choose_Tables_form.htm).
5. PowerShell normally interprets date-shaped JSON strings as date objects;
   `-DateKind String` preserves them. Apply one typed parsing policy to every
   contract reader, not just one comparison. Preserve empty/singleton/null
   arrays as well as exact numeric and timestamp types.
   [Microsoft ConvertFrom-Json](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertfrom-json?view=powershell-7.6).
6. ETABS v22 changed API libraries to .NET Standard 2.0 and disabled its Remote
   API feature. Local Windows evidence plus saved, approved artifacts remains
   the campaign architecture; a speculative remote-Mac attachment is not an
   escape route. The installed version still governs any future capability.
   [ETABS v22 release notes, ticket 10489](https://www.csiamerica.com/software/ETABS/22/ReleaseNotesETABSv2200.pdf).

Installed help additionally distinguishes catalogue/schema APIs from row
retrieval. `GetAvailableTables` and `GetAllFieldsInTable` identify available
tables and their versioned fields. `GetTableForDisplayArray` returns flattened
row-major strings; returned field order, units and row count must be retained.
CSV-file output avoids a large returned table array but still uses ETABS table
state and does not repair a failing preflight. No table call is authorized here.

## Acquisition routes, ranked by work and evidential value

| Priority | Route | What it can answer | Boundary / decision |
|---|---|---|---|
| 1 | Existing `.$et` plus accepted saved snapshots | Object definitions, explicit assignments/loads/settings; source-to-result identity candidates | No COM. Narrow parser/reconciliation needed. Story templates, labels, units and omitted defaults must be resolved explicitly. Input backup does not prove generated mesh, transferred loads or result freshness. |
| 2 | Already accepted typed object getters | Specific residual assignment or identity questions covered by proved interfaces | Reuse reviewed decoding; new live observations need their own guards. Avoid broad interface rescans. |
| 3 | Supported UI export to SQLite, or documented CSV/XML if suitable | Versioned model tables and any available required output tables | Assess only the missing tables. SQLite is a new supported export, not a promise of desired fields. UI changes/exports need a separate exact packet and preservation proof; no Excel dependency is required for SQLite parsing. |
| 4 | Equivalent managed/Python table client | Reusable unattended table access | Closed for this model/host: the installed wrapper's correct zero-argument call still returned CSI 1 with complete preservation. Reopen only for a materially new vendor-supported cause and a named required field that cannot use priorities 1-3. |
| Escalation | Sanitized CSI reproduction or a formally scoped solver extension | Unresolved vendor semantics, or a proved missing physical capability | Draft only; no vendor send/upload, subscription, installation or solver expansion is authorized by this audit. |

The old P5 exported-snapshot path hashes E2K and parses geometry/force CSV; it
does **not** implement a general E2K/`.$et` model-definition parser. Reuse its
identity and row-ledger patterns, not its reduced fixed `mu/vu` projection as
a replacement for W3's signed same-row contracts. A new narrow importer must
feed current W3 contracts or explicitly remain unaccepted research evidence.

The zero-argument closure also adds a recurrence rule for every future ETABS
probe: persist the raw COM result before strict decoding can raise, and prove the
complete guard projection through the exact entrypoint before a live call. A
guard-projection failure consumes no table-call budget and must be corrected
offline. Do not use another live call merely to recover raw logging that was
ordered incorrectly.

## Smallest useful building investigation

Inspect at most three deterministically selected one-to-five-span candidates,
chosen from saved definitions before looking for numerical agreement. Use the
already inspected pinned member as a known limitation, not the only candidate.
Record why each candidate was included and the exact population considered.

For each candidate, prepare one matrix covering: object-to-analysis-element
and station-side mapping; axes/signs/offsets/releases; material/EI/shear basis;
support translations/rotations and surrounding connectivity; diaphragm/slab
participation; explicit frame loads, self-weight, shell transfer and the five
ordered contributing cases/factors; and requested comparison components.
Classify every required item PRESENT, missing, or outside the solver's scope.

Then make one decision: comparable as-is for an explicit scope; potentially
comparable after a named missing input/justified bounded extension; or outside
the present surrogate. Do not keep fetching unrelated tables. A no-go is useful
evidence but does not complete W3H. An action-only study with complete independent
loads/boundaries can have a narrower claim; using ETABS forces to invent its
loads is circular and cannot validate independent prediction.

If all bounded candidates are unsupported, retain ETABS-sourced beam auditing
and saved review as the usable deliverable, and present the cost/benefit of an
ETABS-first candidate programme versus a separately scoped surrogate extension.
Neither option silently replaces the accepted W3H/I/K/L dependencies.

## Completion requirements still missing

W3E needs a strict serviceability route when service checks are mandatory, plus
explicit service scenarios, applicability and detailing/constructability basis.
Existing required-steel calculations do not prove installed rebar adequacy.
Any ETABS-design comparison also needs matched code/preferences/overwrites.

W3H needs independent physical mapping and predeclared model-specific criteria;
numerical residual tolerances are not engineering acceptance criteria. Draft
criteria from evidence and identify only genuine project decisions for review;
do not ask the owner to guess unavailable model facts.

W3I still needs family bounds, objectives/cost scope, mandatory scenarios,
uncertainty cases, all required feasibility checks and calibrated applicability
over the candidate range. Agreement at a single baseline is not proof across
changed stiffness/self-weight/support-sensitive candidates. W3K must freeze
freshness, change allowlist, restoration, affected-member/global safeguards and
the independent final repeat. W3L must define a finite budget, stopping rules,
and explicit unresolved/failure outcomes. W3J can project accepted real evidence
without waiting for those extensions, but its fictional L4 proof is not a
completed real-building dossier or professional signature.

## Recurrence controls

- One active status table and one next sequence; old receipts are history.
- Finish useful offline preparation in a batch. Freeze the exact command and
  serializers, not a helper beside an untested launcher. Any source change
  invalidates the affected proof before live use.
- Each frozen live attempt still stops after any guard/native failure. A new
  packet needs a materially new, proved hypothesis; new names do not create
  retry permission. Do not skip display guards to reach a table faster.
- Reuse hash-bound results for unchanged questions. Recheck state that can
  change before a live call, but do not rehash thousands of historical files
  or rerun installed benchmarks to answer a documentation question.
- Use the CHM topic index rather than recursively scanning the entire mirror;
  the broad scan was slow in this audit and was stopped. Exact indexed reads
  supplied the needed topics.
- Track acceptance rows closed, missing required inputs, live attempts,
  candidate/hosted counts and elapsed phase time. Do not call a pass-count
  increase or another receipt a completed engineering milestone.
