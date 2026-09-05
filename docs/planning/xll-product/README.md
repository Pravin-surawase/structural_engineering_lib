---
owner: Main Agent
status: active
last_updated: 2026-09-05
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, handoff]
---

# Excel-DNA XLL plan and research handoff

This is the shared entry point for the XLL product planning and beginner learning track. It preserves the supplied architecture, the corrected phase comparison and the completed competitor/engineering research in the library repository.

**This track does not replace the maintained library workbench or the [six-phase beam/ETABS programme](../beam-design-optimization-master-plan.md).** The original XLL document is a research decision, even though its preserved metadata says active/spec. Its phases do not themselves authorize implementation, installed application activity, engineering approval or release.

## Read in this order

**Completed library definition:** the
[PF0–PF11 structural library definition programme](library-definition/README.md)
reconciles the existing Python library, C# foundation, three-project evidence,
standalone Excel workflow and later ETABS automation into twelve implementation
packets. Its PF11 blueprint is the authority for new library work.

**Implemented through WP10-04:** the native Python/.NET beam libraries, the
standalone Windows Excel XLL, portable analysis-snapshot contract, exact ETABS
getter adapter, bounded STA acquisition broker and offline normalization are complete. The Excel candidate passed
preflight, install, repair, installed Excel acceptance, performance, uninstall,
and cleanup. [WP10 read-only ETABS acquisition](wp10-etabs-read-adapter.md) next
continues with WP10-05 completed-snapshot import and new installed Excel proof.
The [reviewed next plan](wp10-etabs-read-adapter.md#wp10-05-preparation-review-and-executable-plan--2026-09-05)
also names the missing production acquisition handoff and multi-member
prerequisites before final ETABS/Excel qualification.

**Owner-selected workflow:** [Standalone Excel beam requirements and contract proposal](requirements-first/README.md) records the 3 September requirements-first research across all three projects. It supplements this plan; its proposed delivery packets do not rename P0–P6 or change the Windows shell exercise.

1. [PF0–PF11 library definition](library-definition/README.md): the complete requirements, semantics, APIs, assurance, boundaries and implementation blueprint.
2. [Original XLL architecture](../excel-dna-xll-product-architecture-decision.md): what was actually proposed.
3. [Current plan](current-plan.md): the source hierarchy and present scope.
4. [WP09 completion record](wp09-standalone-excel.md): the shipped Excel surface and installed evidence.
5. [WP09 postmortem](wp09-postmortem.md) and [compact recurrence index](../../verification/rework-recurrence-index.json): deep evidence plus stable issue IDs, counts, time, and short controls.
6. [WP10 execution plan](wp10-etabs-read-adapter.md): completed normalization evidence, next Excel import and subsequent acquisition/scale qualification gates.
7. [Phase comparison and improvements](phase-review.md): original meanings, proposed refinements and the broad POC versus shell-packet distinction.
8. [Windows P0 task](windows-p0-task.txt): the controlling first exercise.
9. [Research map](research/README.md): studies, costs, requirements, acceptance examples and unfinished questions.
10. [Learning record](learning/README.md): the last observed result and the next exercise.

## Original phase meanings

| Phase | Purpose |
| --- | --- |
| P0 | Packaging/runtime spike |
| P1 | Focused C# kernel |
| P2 | Read-only ETABS |
| P3 | Bounded solver and optimizer |
| P4 | Workbook delivery |
| P5 | Controlled ETABS transaction on a model copy |
| P6 | Commercial hardening |

Earlier blueprint/v2 phase numbers are historical. Optional AI has no assigned original phase. The current Windows P0 packet is a narrower shell exercise: no CSI references/calls, structural calculations or solver. Passing it cannot establish completion of the architecture's programme-level acceptance matrix.

## Evidence and learning status

- WP09 installed XLL acceptance is complete and bound to the candidate and
  artifact hashes in its verification receipts.
- No user lesson observation is marked complete; the learning sequence remains
  separate from product implementation evidence.
- The user implements the product; the assistant explains and reviews actual results.
- Broad market research remains paused. R01–R13 are proposed requirements and B01–B23 remain parked under their recorded reopening conditions.
- Costs and vendor claims retain their original 3 September research dates and limitations; this intake performs no price refresh.
- Software tests, inspected source, installed behaviour, independent reference work and engineering approval remain distinct evidence.

## What was preserved

The [source manifest](source-manifest.json) binds each imported file to the original workspace bytes and its published copy. Published Markdown uses LF and portable links. The [intake archive](../../_archive/xll-product-intake-2026-09-03/README.md) preserves the exact supplied architecture and Windows packet bytes, including their original line endings. Those hashes do not establish the earlier unverified Mac commit.

Authored studies, the two source ledgers, R/B registers, depth/readiness summaries, historical phase proposals and Lesson 1 are included. Word renderings, downloaded publications/transcripts/screenshots, raw application/test logs, private catalogs and supporting code checkouts remain outside this bundle. [Local evidence references](local-evidence-index.md) make that distinction explicit. Already-published commit links in the studies remain available; local paths have not been turned into guessed public URLs.

## Continue on either computer

Use the [Mac/Windows handoff](handoff.md) and the repository's [canonical Git workflow](../../git-automation/git-workflow-single-source.md). Identify this material by repository URL, full commit ID and this relative path, not a machine-specific folder. Fetch the shared revision before continuing. A local commit, pushed branch and merged default branch are separate states.
