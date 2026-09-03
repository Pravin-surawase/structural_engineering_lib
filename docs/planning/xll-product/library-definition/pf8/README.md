---
owner: Main Agent
last_updated: 2026-09-03
doc_type: spec
phase_id: PF8
---

# PF8 — Excel, ETABS and coupled automation

PF8 is complete. [baseline.json](baseline.json) defines the Windows application
boundary around the reusable library: ETABS acquisition, immutable action
snapshots, Excel functions and commands, coupled candidate reanalysis and
installed-host evidence.

## D16 through D18 decisions

An ETABS action row is suitable only when source model/analysis/result identity,
case/combination/step, object and element station, units, right-handed axes,
physical-face mapping and all six signed components are retained. The operation
declares whether it accepts static concurrent rows, staged steps, response
results or an envelope. A component envelope never becomes a concurrent vector
silently.

Attached ETABS acquisition is getter-only. It proves the exact process, model,
analysis epoch and result selection before reading and proves the observed state
unchanged afterward. Model mutation occurs only in an identified disposable
copy through a single-use transaction with dry run, readback, reanalysis,
new snapshot and comparison evidence. Uncertain interrupted transactions are
recorded and the copy is quarantined without automatic replay.

Excel worksheet functions are deterministic calculations over explicit values,
ranges or immutable serialized inputs. They never call ETABS, access the Excel
object model, write a cell, save/export a file, start a process or record
approval. Project/table validation, workbook calculation, member design,
optimization, ETABS import/application, report export and performance measurement
are explicit commands with progress, cancellation, controlled writes and receipts.

Reinforcement/detail/cost-only candidates may reuse a frozen action snapshot.
Changes to section, stiffness, releases, offsets, mass/self-weight, loads,
supports, meshing or analysis settings require an owned-copy ETABS reanalysis
and a new immutable snapshot. Unknown coupling prevents evaluation until the
project basis is resolved.

## Exit review

- Five ETABS acquisition stages validate calls, arrays, axes, state and evidence.
- The vendor-neutral snapshot retains every source and engineering dependency.
- Nine worksheet-function families and seven application commands are separated.
- The candidate state machine classifies fixed-action and coupled changes.
- Ten E5 scenarios define installed Excel/ETABS acceptance without overstating it.

PF9 now fixes the runtime, package, dependency, deployment and performance
environments in which these contracts will be delivered.
