---
owner: Main Agent
status: active
last_updated: 2026-09-06
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

# StructAutomate learning record

For an engineer who can read basic code and is new to C#/.NET. The assistant prepares and verifies the examples; the learner predicts, runs, changes and explains them.

**Historical source clarification:** the supplied original XLL architecture has been read and compared. Its P0–P6 meanings are preserved in the [current plan](../current-plan.md). The original shell-only Windows P0 lessons remain below; the current product-code series starts here. No learner exercise is marked completed.

## Start here: current product code

| Lesson | Outcome | Practice |
| --- | --- | --- |
| [1 — Model data in memory](product-code/01-model-data.md) | Read C# records, follow exact source IDs, filter frames and find neighbours using the real session class | Invented model; no installed applications needed |
| [2 — Follow Connect ETABS](product-code/02-connect-workflow.md) | Explain the ribbon, background client, worker and workbook completion; diagnose late results | Deterministic workflow simulation; no installed applications needed |

[Open the visual practice companion](product-code/practice.html) in a browser. It works offline. Its JavaScript simulation illustrates the lessons; the separate console lab runs C# and reuses the actual context contracts and session index code.

**Product baseline:** the running-model connection packet is merged in PR 975 (main `a36e7f4a`). Connect captures source geometry and builds ID indexes. Existing-force handoff is the next implementation packet; broad result coverage, full design orchestration and controlled reanalysis remain later work. These lessons do not expand that implementation scope. See the [current product workflow](../etabs-design-workflow.md).

Budget about 45–60 minutes per lesson, with a natural break before the exercises. Read only the core path first; answers, debugging tables and source maps are references to return to. The original P0 foundation lesson below remains useful optional background.

### Teaching packet and acceptance — WP10-05B-FORCES-PLAN

The user redirected the planning discussion into preparing these first two lessons. Deliver the two guides, a small executable console lab and an offline visual companion. Explain every new C# construct used in the core path, connect it to actual source owners, supply predictions and answers, and distinguish stored geometry from engineering interpretation. Make process, thread, task, cancellation, workbook identity and request identity visible in Lesson 2.

Acceptance: locked restore and Release compilation of the lab; all documented stock scenarios and the lab's self-check pass; documented outputs match the executable examples; visual filtering and workflow scenarios work in a browser, including narrow layout and keyboard access; scoped documentation checks pass. Review only lesson accuracy, executable examples and the product boundaries they teach. No production behavior, live model, workbook, installed package or force-acquisition implementation changes belong to this packet.

Assistant verification is recorded in the task session log. **No learner exercise is marked complete.** Record the learner's own date, command/change, observed result and explanation when they do an exercise. The earlier planning/discussion timer is not a measurement of active lesson-authoring time.

## Original P0 lesson sequence (historical, separate)

| Lesson | What we learn | Status |
| --- | --- | --- |
| 01 | Workbook, add-in, C#, XLL, runtime and pure function; observe Excel version/bitness | Lesson issued; user observation pending |
| 02 | Preservation checks, project folder, Git and build prerequisites | Planned |
| 03 | A small C# class library, explicit target framework and the two demo functions | Planned |
| 04 | Excel-DNA packaging, x64 output and the first build | Planned |
| 05 | Native Ribbon callbacks and a simple WinForms diagnostic dialog | Planned |
| 06 | Pure-function/diagnostic tests, installed lifecycle checks and the P0 receipt | Planned |

These are teaching units within P0, not new product phases. Instructions for later lessons will be checked against the actual environment before they are given. A blocked installed check does not become accepted because an explanation or unit test exists.

For each completed exercise record the date, what the user did, the actual output, what it proves and any unresolved issue. Do not prefill predicted results as observed results. A useful lesson is concept → prediction → small user action → observation → explanation.

Use the [corrected phase comparison](../phase-review.md) for the actual original phases and proposed improvements, the [current plan](../current-plan.md) for scope, and the [research map](../research/README.md) when a specific decision needs evidence.
