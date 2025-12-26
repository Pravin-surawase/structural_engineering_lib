# Agent Prompt Cheat Sheet

Use these snippets to quickly engage the right agent with the right context.

---

## Using with GitHub Copilot Coding Agent

The role docs in this folder can guide **GitHub Copilot Coding Agent** when you create well-scoped GitHub Issues.

**How it works:**
1. Create a GitHub Issue using the `bug_report` or `feature_request` template
2. Fill in the **Acceptance criteria** and **Files likely affected** sections
3. Assign the issue to Copilot (or mention `@copilot` in a comment)
4. Copilot creates a branch, implements the fix, and opens a PR

**Tips for good results:**
- Be specific about expected inputs/outputs
- Reference IS 456 clauses when relevant
- Mention if Python/VBA parity is required
- Keep scope small (one function or one bug per issue)

**Example issue title:** `Fix shear interpolation for pt < 0.25% in M04_Tables`

**Known limitations:**
- Coding agent may not run formatters (black, ruff) — you may need to fix formatting manually or approve auto-fix
- First PR from coding agent requires workflow approval (GitHub security feature)
- Agent works best with small, well-scoped tasks (one function or one bug)
- Complex multi-file refactors may need human guidance

---

## PM
- Role: scope, governance, orchestration, release ledger.
- Prompt:  
  ```
  Act as PM. Use docs/PROJECT_OVERVIEW.md. Scope and plan v0.5 Excel workbook integration; list agent handoffs and risks.
  ```

## CLIENT
- Role: practicing engineer proxy; requirements, workflow sanity, terminology.
- Prompt:  
  ```
  Act as CLIENT. Review planned BEAM_INPUT columns for usability and missing fields; suggest acceptance criteria.
  ```

## UI
- Role: Excel UX; sheet layout, validation, error surfacing.
- Prompt:  
  ```
  Act as UI. Design BEAM_INPUT and BEAM_DESIGN sheet layout, colors, validation, and buttons for v0.5.
  ```

## RESEARCHER
- Role: clause/algorithm expert; platform constraints.
- Prompt:  
  ```
  Act as RESEARCHER. Cite IS 456/13920 for effective flange width and neutral axis checks; give boundary conditions.
  ```

## DEV
- Role: implementation/refactor; layer-aware, units, Mac VBA safety.
- Prompt:  
  ```
  Act as DEV. Implement/update <function> in M06_Flexure with clause refs, units, and Mac-safe CDbl guards.
  ```

## TESTER
- Role: test matrices, benchmarks, edge cases, regression capture.
- Prompt:  
  ```
  Act as TESTER. Propose regression cases for Design_Doubly_Reinforced covering Mu<=Mu_lim, Mu>Mu_lim, and Mac overflow edge.
  ```

## DEVOPS
- Role: repo/layout, import/export, build/CI, release packaging.
- Prompt:  
  ```
  Act as DEVOPS. Draft the release checklist for v0.4: tests, xlam build/import order, tagging, ledger updates.
  ```

## DOCS
- Role: API/README/CHANGELOG/RELEASES/TASKS alignment; release notes.
- Prompt:  
  ```
  Act as DOCS. Update API_REFERENCE and CHANGELOG for the new flanged beam API changes; note units/examples.
  ```

## INTEGRATION
- Role: ETABS/CSV mapping, BEAM_INPUT schema, validation.
- Prompt:  
  ```
  Act as INTEGRATION. Define ETABS CSV -> BEAM_INPUT mapping, required headers, units, and validation rules.
  ```

## SUPPORT
- Role: troubleshooting/known pitfalls/runbook.
- Prompt:  
  ```
  Act as SUPPORT. Add a TROUBLESHOOTING entry for Excel add-in load failures on macOS with probes and fixes.
  ```
