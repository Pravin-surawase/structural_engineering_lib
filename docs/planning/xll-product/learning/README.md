---
owner: Main Agent
status: active
last_updated: 2026-09-07
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

# StructAutomate learning record

For an engineer who can read basic code and is new to C#/.NET. The assistant prepares and verifies the examples; the learner predicts, runs, changes and explains them.

**Historical source clarification:** the supplied original XLL architecture has been read and compared. Its P0–P6 meanings are preserved in the [current plan](../current-plan.md). The original shell-only Windows P0 lessons remain below; the current product-code series starts here. No learner exercise is marked completed.

## Start here: current product code

**Current owner direction — 7 September:** learn inside the main product
solution, using real ETABS/Excel and actual product code as each step needs
them. Begin with [Lesson 0 — real product in VS Code](product-code/00-real-product-vscode.md)
and the [product workspace](../../../../CSharp/StructAutomate.code-workspace).
Acquire the required model/result data into memory before discussing design
or persistence. The current production Connect command writes transport and
evidence files, so a memory-only adaptation must precede that live exercise.
The two earlier invented-data lessons below are optional background; they do
not substitute for the requested real-product learning sequence.

| Lesson | Outcome | Practice |
| --- | --- | --- |
| [0 — Real product in VS Code](product-code/00-real-product-vscode.md) | Verify tools, build the actual solution, check the installed XLL version and trace real connection source | Current product; no live ETABS acquisition in this first exercise |
| [1 — Model data in memory](product-code/01-model-data.md) | Read C# records, follow exact source IDs, filter frames and find neighbours using the real session class | Invented model; no installed applications needed |
| [2 — Follow Connect ETABS](product-code/02-connect-workflow.md) | Explain the ribbon, background client, worker and workbook completion; diagnose late results | Deterministic workflow simulation; no installed applications needed |

[Open the visual practice companion](product-code/practice.html) in a browser. It works offline. Its JavaScript simulation illustrates the lessons; the separate console lab runs C# and reuses the actual context contracts and session index code.

The visual companion opens in a dark theme for night reading. Use **Dark theme**
at the top to switch between dark and light; the browser remembers the choice
when local storage is available. This controls the companion page; Markdown
lesson previews use the reading application's own theme.

### Night-reading update — LESSON-DARK-THEME

Scope: default-dark companion, accessible dark/light toggle and saved browser
preference. Preserve the lesson content and model/workflow interactions.
Acceptance: inspect both palettes, reload persistence, keyboard toggle, readable
diagram/form controls and narrow layout; run affected documentation and final
candidate-integrity checks. No C# or installed-application change is needed.

**Product baseline:** the running-model connection packet is merged in PR 975 (main `a36e7f4a`). Connect captures source geometry and builds ID indexes. The owner now wants to learn and adapt this real path for memory-only acquisition before continuing existing-force handoff. Broad result coverage, full design orchestration and controlled reanalysis remain later work. Lesson 0 adds setup/source navigation, not that runtime adaptation. See the [current product workflow](../etabs-design-workflow.md).

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
