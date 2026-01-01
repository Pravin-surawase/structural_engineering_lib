# Copilot Task Execution System

**Purpose:** Cost-optimized workflow using GitHub Copilot for implementation and Claude for strategic planning

---

## System Files

| File | Purpose | When to Use |
|------|---------|-------------|
| **COPILOT_WORKFLOW.md** | Master guide for working with Copilot | Read first, reference always |
| **PROGRESS_TRACKER.md** | Track completion of tasks | Update as you work |
| **TASK_X.Y_Name_Spec.md** | Detailed implementation specs | One per task, feed to Copilot |
| **README.md** | This file (system overview) | Orientation |

---

## Quick Start

### 0. Start Session (Every time, 30 sec)

```bash
./.venv/bin/python scripts/start_session.py
```

### 1. Read Workflow Guide (One-time, 10 min)
```bash
Open: COPILOT_WORKFLOW.md
Read: Sections 1-3 (System Overview, How to Use Specs, Best Practices)
```

### 2. Start First Task (3 hours)
```bash
Open: TASK_1.1_BeamDesignSchedule_Spec.md
Follow: Step-by-step instructions
Use: Copilot prompts provided in spec
Update: PROGRESS_TRACKER.md as you complete steps
```

### 3. Mark Progress (Throughout)
```bash
Open: PROGRESS_TRACKER.md
Check: ✅ Completed steps
Note: Session log (time, blockers)
```

### 4. Complete Task
```bash
Run: Acceptance criteria tests from spec
Commit: git add . && git commit -m "feat: complete Task 1.1"
Update: PROGRESS_TRACKER.md (mark task complete)
```

---

## File Structure

```
docs/_internal/copilot-tasks/
├── README.md                           (This file)
├── COPILOT_WORKFLOW.md                 (Master workflow guide)
├── PROGRESS_TRACKER.md                 (Task completion checklist)
├── TASK_1.1_BeamDesignSchedule_Spec.md (First task - ready to start)
├── TASK_1.2_QuickDesign_Spec.md        (To be created)
├── TASK_1.3_Compliance_Spec.md         (To be created)
└── ...                                 (More specs as needed)
```

---

## Workflow Diagram

```
┌──────────────────┐
│  You (Pravin)    │
│  - Opens spec    │
│  - Runs Copilot  │
│  - Tests output  │
│  - Commits work  │
└────────┬─────────┘
         │
         ├─── reads ───► Task Spec (TASK_1.1_*.md)
         │               - Step-by-step instructions
         │               - Copilot prompts
         │               - Acceptance criteria
         │
         ├─── uses ────► GitHub Copilot
         │               - Generates code from prompts
         │               - Implements formulas
         │               - Creates documentation
         │
         ├─── updates ─► Progress Tracker
         │               - Check off completed steps
         │               - Log session notes
         │
         └─── escalates (if needed) ─► Claude
                         - Unclear specs
                         - Architectural decisions
                         - Complex research
```

---

## Cost Comparison

### Without This System (All Claude)
```
Task 1.1 (3 hours):
- Claude writes all code: ~50,000 tokens @ $15/1M tokens = $0.75
- 10 tasks: $7.50
- Review cycles: +$5.00
Total: ~$12.50
```

### With This System (Copilot + Claude)
```
Task 1.1 (3 hours):
- Claude creates spec: ~5,000 tokens @ $15/1M tokens = $0.08
- Copilot implements: $10/month (unlimited)
- 10 tasks: $0.80 (specs) + $10/month (Copilot)
Total: ~$10.80/month (unlimited tasks)

Savings: ~90% cost reduction for implementation
```

**Why this works:**
- Specs are reusable (write once, use many times)
- Copilot is flat-rate unlimited
- Claude only used for high-value strategic work

---

## When to Use What

### Use Copilot for:
✅ Writing VBA code from specs
✅ Creating Excel formulas
✅ Generating documentation
✅ Formatting, boilerplate
✅ Debugging syntax errors
✅ Refactoring existing code

### Use Claude for:
✅ Creating task specs (architecture)
✅ Making design decisions
✅ Research and exploration
✅ Reviewing complex logic
✅ Planning multi-task workflows
✅ Quality gates (final review)

### Example Decision Tree:
```
Question: "How should I implement beam export?"

Is the approach already defined in a spec?
├─ YES → Use Copilot to implement from spec
└─ NO  → Ask Claude to create spec first

Question: "This VBA code has syntax error"
├─ Simple syntax → Use Copilot to fix
└─ Logic error → Ask Claude to review
```

---

## Tips for Success

### 1. Work in Sessions
```
Session = 60-90 minutes of focused work
- Set timer
- Complete 2-4 spec steps per session
- Update progress tracker
- Commit work
- Take break
```

### 2. Test Frequently
```
After each spec step:
1. Test the feature (does it work?)
2. Check quality (is it clean code?)
3. Verify UX (is it user-friendly?)

Don't wait until end to test - fix issues immediately
```

### 3. Keep Copilot Context Fresh
```
Every 5-10 prompts:
- Start new Copilot Chat session
- Provide context again
- Paste relevant code/specs

Why: Copilot context window is limited, fresh start = better results
```

### 4. Use Git Commits as Checkpoints
```
After each major step:
git add .
git commit -m "feat(task-1.1): complete step 3 - calculated columns"

Benefits:
- Easy to revert if something breaks
- Track progress
- Clear history
```

---

## Troubleshooting

### Problem: Copilot generates wrong code

**Solution:**
1. Check if spec is clear (is prompt specific enough?)
2. Provide more context in prompt
3. Show Copilot example of expected output
4. If still wrong, escalate to Claude

---

### Problem: Spec is unclear/incomplete

**Solution:**
1. Note blocker in PROGRESS_TRACKER.md
2. Ask Claude: "Task 1.1 Step 5 unclear - need clarification on [issue]"
3. Claude updates spec
4. Resume with Copilot

---

### Problem: Lost track of progress

**Solution:**
1. Open PROGRESS_TRACKER.md
2. Find current task
3. Check last completed step
4. Resume from next unchecked step

---

### Problem: Excel/VBA questions

**Solution:**
1. Check existing docs:
   - VBA API Reference (docs/reference/vba-api-reference.md)
   - FAQ (docs/troubleshooting/excel-faq.md)
   - VBA Guide (docs/contributing/vba-guide.md)
2. Ask Copilot to explain
3. If still unclear, escalate to Claude

---

## Success Metrics

**After completing Task 1.1, you should have:**
- [ ] Professional Excel template (BeamDesignSchedule.xlsm)
- [ ] Working formulas (no #NAME or #VALUE errors)
- [ ] Functional export macro (DXF generation works)
- [ ] Clear documentation (Instructions sheet)
- [ ] Test-validated (all acceptance criteria pass)
- [ ] Time spent: ~3 hours (vs 1 hour if all manual, 5+ hours if all Claude)

**Learning curve:**
- Task 1.1: ~3 hours (learning Copilot workflow)
- Task 1.2: ~2 hours (more familiar with system)
- Task 1.3: ~1.5 hours (efficient with workflow)

**ROI:** After 3 tasks, workflow becomes faster than manual coding

---

## Next Steps

**Ready to start?**

1. ✅ Read COPILOT_WORKFLOW.md (10 min)
2. ✅ Open TASK_1.1_BeamDesignSchedule_Spec.md
3. ✅ Open Excel, prepare environment
4. ✅ Follow spec step-by-step with Copilot
5. ✅ Update PROGRESS_TRACKER.md as you go
6. ✅ Test and commit when complete

**Time estimate:** 3 hours for first task

**Output:** Professional beam design template worth sharing/selling

---

**Good luck! 🚀**

*If you get stuck, check COPILOT_WORKFLOW.md or escalate to Claude.*
