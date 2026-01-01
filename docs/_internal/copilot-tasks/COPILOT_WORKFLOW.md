# GitHub Copilot Workflow Guide

**Purpose:** Instructions for using GitHub Copilot to execute task specifications efficiently

**Cost Optimization:** Use Copilot (cheap) for implementation, Claude (expensive) for planning/review only

---

## System Overview

```
┌─────────────────────┐
│ Claude (Strategic)  │ → Creates detailed task specs
│ - Planning          │ → Reviews complex decisions
│ - Architecture      │ → Quality gates
│ - Research          │
└──────────┬──────────┘
           │
           ├─ Task Specs (.md files)
           │
           ▼
┌─────────────────────┐
│ GitHub Copilot      │ → Implements from specs
│ - Code generation   │ → Writes VBA macros
│ - Formulas          │ → Creates Excel tables
│ - Boilerplate       │ → Formats documentation
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ You (Execution)     │ → Runs Copilot prompts
│ - Review            │ → Tests output
│ - Integration       │ → Commits to git
│ - Decision-making   │
└─────────────────────┘
```

---

## How to Use Task Specs

### Step 0: Start Session (Every time, 30 sec)

Before starting any task work, run the repo session bootstrap:

```bash
./.venv/bin/python scripts/start_session.py
```

This ensures you're aligned on current branch/state, active tasks, and doc freshness.

### Step 1: Open Task Spec

Example: `TASK_1.1_BeamDesignSchedule_Spec.md`

**Structure:**
- **Objective** - What we're building
- **Step-by-Step Implementation** - Numbered steps
- **Copilot Prompts** - Ready-to-use prompts
- **Acceptance Criteria** - How to verify
- **Testing Checklist** - Validation steps

---

### Step 2: Work Through Steps Sequentially

**For each step:**

1. **Read the step description** (understand what to build)
2. **Find "Copilot Prompt" section**
3. **Copy prompt to Copilot Chat**
4. **Review Copilot's output**
5. **Apply to Excel/code**
6. **Mark step as complete** (checkbox in spec)

**Example:**

```markdown
## Step 3: Design Sheet - Calculated Columns (J-Q)

**Copilot Prompt:**
In Excel sheet "Design", add calculated column headers in J1:Q1:
Mu_lim (kN·m), Ast (mm²), Bar Count, Bar Callout...

**Your workflow:**
1. Copy prompt above
2. Open Copilot Chat in VS Code or Excel
3. Paste prompt
4. Copilot generates formula suggestions
5. Apply formulas to Excel
6. Verify first formula calculates correctly
7. Copy down to row 51
```

---

### Step 3: Use "Manual" Sections

Some tasks require manual Excel actions (Copilot can't directly manipulate Excel UI).

**Pattern:**
```markdown
**Copilot Prompt:** [Describes what to create]
**Manual:** [Steps to do in Excel UI]
```

**Example:**
```markdown
**Copilot Prompt:**
Create conditional formatting rule for column Q (Status):
- Red fill if "Check"
- Green fill if "Safe"

**Manual:**
Apply in Excel via Home → Conditional Formatting → New Rule
```

**Workflow:**
1. Use Copilot to understand what formatting to apply
2. Follow manual steps in Excel
3. Copilot can generate VBA code if you want to automate formatting setup

---

## Copilot Best Practices

### 1. Break Down Complex Prompts

**❌ Don't do this:**
```
Create complete BeamDesignSchedule workbook with all formulas,
formatting, macros, and export functionality
```
Too vague, Copilot will miss details.

**✅ Do this:**
```
Step 1: Create Excel sheet "Design" with headers A1-I1:
BeamID, b (mm), D (mm), d (mm), fck, fy, Mu (kN·m), Vu (kN), Cover (mm)

Format row 1: Bold, dark blue fill (RGB 0,32,96), white text, center-aligned
```
Specific, actionable, one step at a time.

---

### 2. Provide Context in Each Prompt

**Format:**
```
[Context] + [Action] + [Expected Output]
```

**Example:**
```
Context: I'm creating a beam design workbook using StructEngLib add-in.

Action: Write an Excel formula in cell J2 to calculate limiting moment (Mu_lim)
using the UDF IS456_MuLim(b, d, fck, fy).

Expected Output: Formula that references cells B2 (b), D2 (d), E2 (fck), F2 (fy)
```

Copilot understands context and generates better code.

---

### 3. Use Iterative Refinement

**First attempt:**
```prompt
Create VBA macro to export beams to DXF
```

Copilot generates basic structure.

**Refinement 1:**
```prompt
Update ExportAllBeamsToDXF macro to:
1. Loop through rows 2-51 in "Design" sheet
2. Skip empty rows
3. Show progress message every 10 beams
```

**Refinement 2:**
```prompt
Add error handling to ExportAllBeamsToDXF:
- If M16_DXF.Draw_BeamDetailing fails, log to Debug.Print
- Continue to next beam instead of stopping
- Show final count of successful vs failed exports
```

Build complexity gradually.

---

### 4. Leverage Copilot for Documentation

**Use Case:** Generate README files, comments, user guides

**Prompt:**
```
Create a README.md for BeamDesignSchedule.xlsm template.

Include:
- Purpose (batch beam design)
- Prerequisites (Excel 2016+, StructEngLib add-in)
- Quick start (5 steps)
- Column descriptions (A-Q)
- Troubleshooting (common errors)

Format in markdown with headers, bullet lists, code blocks.
```

Copilot excels at documentation generation.

---

### 5. Ask Copilot to Explain Code

**Scenario:** VBA macro in spec is complex

**Prompt:**
```
Explain this VBA code line by line:

[Paste VBA code from spec]

Focus on:
- What each loop does
- How BeamDetailingResult is populated
- Error handling strategy
```

Copilot will break down the logic. Helps you understand before implementing.

---

## Handling VBA with Copilot

### Method 1: Copilot in VS Code (Recommended)

**Setup:**
1. Open project folder in VS Code
2. Create `.bas` file (e.g., `ExportMacros.bas`)
3. Write VBA code with Copilot suggestions
4. Copy final code to Excel VBA editor

**Advantage:** Better Copilot integration, syntax highlighting, version control

---

### Method 2: Copilot Chat for VBA Snippets

**Workflow:**
1. Open Copilot Chat (Ctrl+Shift+I in VS Code)
2. Paste VBA code from spec
3. Ask Copilot to modify/explain
4. Copy final code to Excel

**Example:**
```chat
User: Modify this VBA macro to add a progress bar:
[Paste ExportAllBeamsToDXF code]

Copilot: [Generates updated code with UserForm progress bar]

User: Simplify - use StatusBar instead of UserForm

Copilot: [Generates simpler version with Application.StatusBar]
```

---

### Method 3: Excel VBA Editor (Limited Copilot)

**Note:** Copilot doesn't work directly in Excel VBA editor.

**Workaround:**
1. Write code in VS Code with Copilot
2. Test syntax
3. Copy to Excel VBA editor
4. Test in Excel

---

## Quality Checks

After completing each step:

### 1. Functional Check
```
✅ Does it work as described in spec?
✅ No errors when running?
✅ Output matches expected result?
```

### 2. Code Quality Check
```
✅ Code is readable (comments, meaningful variable names)?
✅ No hardcoded values (use constants)?
✅ Error handling present (On Error GoTo)?
```

### 3. User Experience Check
```
✅ Intuitive for end user?
✅ Clear labels, tooltips, instructions?
✅ Professional appearance?
```

**If any ❌, refine with Copilot before proceeding.**

---

## Common Copilot Pitfalls (and Solutions)

### Pitfall 1: Copilot hallucinates function names

**Problem:**
```vb
' Copilot generates:
result = IS456_CalculateBeam(...)  ' ❌ Function doesn't exist
```

**Solution:**
```
Refer to VBA API Reference (docs/reference/vba-api-reference.md)
Verify function names before implementing
```

---

### Pitfall 2: Copilot uses outdated Excel syntax

**Problem:**
```vb
' Copilot generates:
Worksheets("Design").Activate  ' ❌ Old style
```

**Solution:**
```
Prompt: "Use modern Excel VBA best practices (avoid .Activate, use With blocks)"
```

---

### Pitfall 3: Copilot doesn't follow Excel conventions

**Problem:**
```vb
' Copilot generates hardcoded cell references:
x = Cells(2, 1).Value  ' ❌ Magic numbers
```

**Solution:**
```
Prompt: "Use named constants for column indices. Example:
Const COL_BEAM_ID = 1
Const COL_WIDTH = 2
x = Cells(2, COL_BEAM_ID).Value
```

---

## Time Tracking

**Suggested workflow:**

```
Start of session:
- Note start time
- Open task spec
- Mark current step

Every 30 minutes:
- Mark completed steps
- Note any blockers
- Commit progress to git

End of session:
- Update task spec (mark completed steps)
- Note total time spent
- Update STRATEGIC_ROADMAP.md status
```

**Example log:**
```
Session 1 (Jan 1, 2:00-3:30 PM):
- Completed steps 1-5 (90 min)
- Blocker: Formula error in step 3 (resolved via Copilot Chat)
- Next: Step 6 (Instructions sheet)
```

---

## When to Escalate to Claude

**Use Copilot for:**
- ✅ Implementing from clear specs
- ✅ Writing formulas, VBA code
- ✅ Formatting, documentation
- ✅ Debugging syntax errors

**Escalate to Claude for:**
- ❌ Spec is unclear/incomplete
- ❌ Architectural decision needed (e.g., "Should we use UserForm or Ribbon?")
- ❌ Complex logic design (e.g., "How should we handle T-beam vs rectangular?")
- ❌ Research needed (e.g., "How does ETABS export format work?")

**How to escalate:**
1. Note blocker in task spec
2. Ask Claude via chat: "Spec unclear at step X. Need clarification on [issue]"
3. Claude updates spec or provides guidance
4. Resume with Copilot

---

## Workflow Cheat Sheet

```
┌─────────────────────────────────────────────────────────┐
│ COPILOT EXECUTION WORKFLOW                              │
├─────────────────────────────────────────────────────────┤
│ 1. Read task spec (TASK_X.X_Name_Spec.md)              │
│ 2. Open Copilot Chat / VS Code                         │
│ 3. For each step:                                       │
│    a. Copy "Copilot Prompt"                             │
│    b. Paste to Copilot                                  │
│    c. Review output                                     │
│    d. Apply to Excel/code                               │
│    e. Test (functional + quality checks)                │
│    f. Mark step complete ✅                             │
│ 4. When all steps done:                                 │
│    a. Run full acceptance criteria tests                │
│    b. Commit to git                                     │
│    c. Update STRATEGIC_ROADMAP status                   │
│ 5. If blocker: Escalate to Claude                       │
└─────────────────────────────────────────────────────────┘
```

---

## Example: Full Task 1.1 Workflow

**Estimated time:** 3 hours

**Session 1 (60 min):**
```
1. Open TASK_1.1_BeamDesignSchedule_Spec.md
2. Execute steps 1-5 (structure + data):
   - Copilot creates workbook structure
   - Add headers, formulas, sample data
3. Test: Verify formulas calculate correctly
4. Commit: "feat: add BeamDesignSchedule template (steps 1-5)"
```

**Session 2 (60 min):**
```
1. Execute steps 6-8 (documentation + automation):
   - Copilot writes Instructions sheet content
   - Copilot generates VBA macro
2. Test: Export 1 beam to DXF manually
3. Commit: "feat: add export macro and instructions"
```

**Session 3 (60 min):**
```
1. Execute steps 9-11 (polish + testing):
   - Add button, page setup, protection
2. Run full test suite (Test 1-4 from spec)
3. Fix any issues
4. Commit: "feat: complete BeamDesignSchedule template"
5. Update roadmap: Task 1.1 ✅ Complete
```

---

**END OF WORKFLOW GUIDE**

*Use this guide every time you work with Copilot on task specs. Optimize for speed + quality.*
