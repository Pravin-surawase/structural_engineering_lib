---
owner: Main Agent
status: active
last_updated: 2026-08-17
doc_type: guide
complexity: intermediate
tags: []
---

# End-of-Session Workflow

**Type:** Guide
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Version:** 1.3.0
**Created:** 2026-01-08
**Last Updated:** 2026-08-17

---

> **Standard procedure for ALL agents when ending a session.**

**Purpose:** Ensure clean handoff, prevent knowledge loss, maintain documentation quality.

---

## ⚡ Quick Checklist (5 Minutes)

```bash
# 1. Finish code, docs, SESSION_LOG, task/handoff state, and receipt
# 2. If preparation automation is explicitly needed, run it before the freeze
./run.sh session end --agent <role> --fix
# 3. Review every resulting write
# 4. Validate live repository context read-only
./run.sh context validate
# 5. Commit the immutable local candidate
# 6. Run final validation read-only on the clean commit
./run.sh session end --agent <role>
# 7. Push and use hosted GitHub facts externally
```

**That's it for routine sessions.** The steps below are detailed explanations.

---

## 📋 Full Workflow (Step-by-Step)

### Step 1: Prepare Closeout Documents When Needed ⚡

```bash
./run.sh session end --agent <role> --fix
```

This is preparation mode, not a final closeout verdict. It may update handoff
or task files, but it never generates indexes. Review its writes before the
candidate freeze.

**What it checks:**
- ✅ Uncommitted changes (reminds you to commit)
- ✅ Session log entry for today and required issue/root-cause sections
- ✅ Handoff freshness (next-session-brief.md date)
- ✅ Test count drift (ensures test_stats.json is current)
- ✅ Version consistency (package version matches docs)
- ✅ Active task status (checks TASKS.md Active section)

**Options:**
- `--fix` - Prepare supported handoff/task files before the candidate freeze
- no `--fix` - Read-only final validation

Preparation returns exit status `2` when its checks otherwise pass. That
non-zero status is intentional: callers must not treat a potentially mutating
preparation run as the final closeout success.

**Expected output:**
```
============================================================
🏁 END OF SESSION CHECKS
============================================================
[✓] Git working tree clean
[✓] Session log entry exists for 2026-01-06
[✓] Next session brief is fresh (updated today)
[✓] No active tasks need attention
[i] Remember to update TASKS.md if work completed

Preparation mode completed; this is not a final closeout verdict.
============================================================
```

### Step 2: Review and Fix Issues 🔧

**If checks fail, fix them:**

**❌ Uncommitted changes detected:**
```bash
# Codex reviews and includes task-owned session records in the scoped commit.
```

**❌ Session log entry missing:**
- Add it to `docs/SESSION_LOG.md` before the candidate freeze:
  ```markdown
  ## 2026-01-06 — Session (Brief Title)

  **Focus:** What you worked on

  ### Summary
  - Key accomplishments
  - Issues encountered
  - Decisions made
  ```

**Candidate accuracy rules:**
- Record the PR number and frozen candidate head before publication.
- Keep hosted-check and merge facts in GitHub and the external handoff after
  push; do not rewrite `SESSION_LOG.md` only to add them.
- A material post-push defect is a separate repair candidate, not a status-log
  commit.

**❌ Next session brief outdated:**
- Update `docs/planning/next-session-brief.md`:
  ```markdown
  ## Latest Handoff (auto)

  <!-- HANDOFF:START -->
  - Date: 2026-01-06
  - Focus: [What you worked on]
  - Completed: [Key accomplishments]
  - Next: [What's pending or blocked]
  <!-- HANDOFF:END -->
  ```

**❌ Active tasks need attention:**
- Update `docs/TASKS.md`:
  - Move completed tasks to "Recently Done"
  - Update task status in "Active" section
  - Add new tasks to "Backlog" if discovered

### Step 3: Update TASKS.md (If Work Completed) ✅

**When you complete a task:**

```markdown
## Recently Done

| ID | Task | Completed | Agent |
|----|------|-----------|-------|
| **TASK-XXX** | [Task description] | 2026-01-06 | [AGENT] |
```

**Move from Active or Up Next → Recently Done**

**Example:**
```markdown
| **TASK-171** | Phase 1: Create Automation Script Catalog | 2026-01-06 | DOCS |
```

### Step 4: Document Issues Encountered (If Any) 📝

**If you encountered issues/traps during session:**

Add to `docs/contributing/session-issues.md`:

```markdown
## 2026-01-06 (Your Session Title)

### Issues Seen
- **[Issue name]:** Brief description of what went wrong

### Cause
- Why it happened (root cause analysis)

### Fixes Applied
- What you did to solve it
- Commands used or changes made

### Prevention
- How future agents can avoid this issue
- What to check before starting similar work
```

**Examples of what to document:**
- Tools that didn't work as expected
- Workflow confusion or mistakes
- Dependencies missing or outdated
- Documentation gaps discovered
- Unexpected behavior in scripts

### Step 5: Create Session Research (Optional - For Major Work) 🔬

**When to do this:**
- Session >4 hours
- Multiple complex issues solved
- Significant workflow improvements
- New patterns/learnings discovered

**Template:** `docs/research/session-YYYY-MM-DD-brief-title.md`

**Include:**
1. **Executive Summary** - What was done, key achievements
2. **Timeline** - Chronological work breakdown
3. **Issues & Solutions** - Problems faced and how solved
4. **Lessons Learned** - What future agents should know
5. **Recommendations** - Process improvements, tool enhancements
6. **Metrics** - Quantitative improvements (if measurable)

**See example:** `docs/research/session-2026-01-06-documentation-enhancement.md`

### Step 6: Run Quick Quality Checks 🎯

**Before ending session, verify:**

```bash
# Test basic functionality (if code changed)
./scripts/python_runtime.sh -m pytest <focused-test-paths> -q

# Check for obvious formatting issues (if Python changed)
./scripts/python_runtime.sh -m black <changed-python-paths> --check

# Verify docs links aren't broken (if docs changed)
./scripts/python_runtime.sh scripts/check_links.py docs/
```

Follow the repository's packet and cumulative verification cadence in
`AGENTS.md`; required hosted checks are never bypassed.

### Step 7: Confirm Handoff Readiness ✨

Before this final read-only step, finish all session/task/handoff/evidence
writes and the pre-commit Git handoff receipt. Validate live repository context
and commit the immutable local candidate. Nothing in the repository may be
rewritten after that freeze.

**Final checklist:**

- [ ] TASKS.md reflects current state
- [ ] Session log has today's entry
- [ ] Next session brief updated (if major work)
- [ ] Issues documented (if encountered)
- [ ] Pre-commit handoff receipt created
- [ ] Live repository context validates without writes
- [ ] Intended paths committed locally
- [ ] Plain `./run.sh session end --agent <role>` passes read-only
- [ ] Candidate pushed without rewriting history
- [ ] No active work left in limbo

**Verify:**
```bash
git status -sb          # Should show "## main...origin/main"
git log --oneline -3    # Verify your commits are there
```

### Live context validation

Generic folder indexes are retired. After structural changes, validate the
small routing manifest and request a bounded live summary only when it helps
review:

```bash
./run.sh context validate
./run.sh context summary <area-or-folder>
```

Neither command writes repository files. The no-flag `sync_numbers.py`
command is also a read-only report; only `--fix` writes.

---

## 🎓 Best Practices

### Do These Things

✅ **Commit work before ending session**
- Don't leave uncommitted changes
- Use descriptive commit messages
- Reference task IDs where applicable

✅ **Update TASKS.md immediately when completing work**
- Don't batch updates for later
- Move completed tasks to Recently Done right away
- Add new tasks discovered during work

✅ **Document issues as they happen**
- Don't wait until end of session
- Fresh memory = better documentation
- Include exact error messages and solutions

✅ **Be honest in handoff notes**
- Document what's incomplete or blocked
- Explain why certain approaches didn't work
- Surface dependencies or blockers

✅ **Keep handoff brief concise**
- 2-minute read maximum
- Focus on actionable information
- Link to details rather than duplicating

### Don't Do These Things

❌ **Don't skip session.py end checks**
- Takes <30 seconds
- Catches issues before handoff
- Prevents broken handoffs

❌ **Don't leave work "almost done"**
- Either finish it or document clearly what's left
- Incomplete work wastes next agent's time
- Better to have clear stopping point

❌ **Don't commit with generic messages**
- ❌ "updates", "fixes", "changes"
- ✅ "feat: Add cost optimization API"
- ✅ "fix: Resolve whitespace conflict in safe_push"

❌ **Don't update docs without testing links**
- Broken links frustrate future agents
- Run check_links.py on changed docs
- Fix broken links before committing

❌ **Don't assume next agent will remember context**
- Document everything explicitly
- Link to relevant docs/issues
- Explain non-obvious decisions

---

## 🔄 Quick Reference by Session Type

### ✅ Session Docs Rule (Avoid the Commit Loop)
Update `docs/SESSION_LOG.md` and `docs/planning/next-session-brief.md` in the
same candidate when their state changes. Record a PR number only if it is
already known before the freeze. Never rewrite the candidate merely to add a
new PR number, hosted status, or merge hash.

The final read-only `session end` validates the fresh transition receipt before
push. After hosted CI or merge, retain that historical receipt unchanged even
when its time-bound observations later expire. Record the final PR/check/head/
tree facts in the successor external closeout observation; do not rerun or
rewrite the reviewed candidate merely to make its historical receipt current.

### Routine Bug Fix (1-2 hours)
1. Finish the log/task/handoff/receipt writes.
2. Validate live repository context.
3. Commit the candidate and run plain `session.py end` read-only.
4. Push the unchanged candidate.

### Feature Implementation (2-4 hours)
1. Update TASKS, next-session brief, session issues, and receipt.
2. Use `session.py end --fix` only if preparation automation is needed.
3. Review all writes and validate live repository context.
4. Commit, run plain `session.py end` read-only, then push unchanged.

### Major Enhancement (4+ hours)
1. Complete every task, brief, research, issue, session-log, and receipt write.
2. Use `session.py end --fix` only before the freeze if needed.
3. Review all writes and validate live repository context.
4. Commit, run plain `session.py end` read-only, then push unchanged.

### Research Session (No Code Changes)
1. Commit research documents
2. Update TASKS.md (mark research complete)
3. Add SESSION_LOG entry
4. Update next-session-brief.md with findings
5. Link research from relevant docs
6. Done!

---

## 📊 Automated vs Manual Steps

| Step | Automated by session.py end | Manual Required |
|------|----------------------------|-----------------|
| Check git status | ✅ Yes | ❌ No |
| Check session log entry | ✅ Yes | 🟡 Review/edit if needed |
| Check handoff freshness | ✅ Yes | 🟡 Update if major work |
| Check test counts | ✅ Yes (if ran tests) | ❌ No |
| Update TASKS.md | ❌ No | ✅ Yes (move to Done) |
| Document issues | ❌ No | ✅ Yes (if encountered) |
| Commit uncommitted work | ❌ No | ✅ Yes |
| Create research doc | ❌ No | 🟡 Optional (major work) |
| Validate live repository context | ✅ Yes | 🟡 Review if routing changed |

**Legend:**
- ✅ Fully automated
- 🟡 Partially automated (review/edit needed)
- ❌ Fully manual

---

## 🚨 Common Handoff Failures (Prevent These)

### Failure #1: "I don't know what was done last"
**Cause:** Session log not updated, no handoff brief
**Prevention:** Add the required session entry before the candidate freeze;
plain `session.py end` validates it.

### Failure #2: "The working tree is dirty"
**Cause:** Uncommitted changes left in workspace
**Prevention:** `git status` before ending, commit everything

### Failure #3: "I don't know which tasks are done"
**Cause:** TASKS.md not updated after completing work
**Prevention:** Move tasks to Done immediately, don't batch updates

### Failure #4: "I hit the same issue as last agent"
**Cause:** Issues not documented in session-issues.md
**Prevention:** Document issues immediately when encountered

### Failure #5: "Links are broken in the docs"
**Cause:** Didn't run check_links.py after doc changes
**Prevention:** `scripts/check_links.py docs/` before committing docs

### Failure #6: "I can't find the research/context"
**Cause:** Work not added to SESSION_LOG, research doc not linked
**Prevention:** Add SESSION_LOG entry with links to deliverables

---

## 💡 Pro Tips

**Tip 1: Separate preparation from the final verdict**
- Use `session.py end --fix` only before the candidate freeze.
- Use plain `session.py end` once after the freeze for the read-only verdict.

**Tip 2: Update docs as you work, not at the end**
- Update TASKS.md when you complete each task
- Add session-issues.md entries when you encounter issues
- Reduces end-of-session work

**Tip 3: Keep commits atomic and well-messaged**
- One logical change per commit
- Future agents (and you) will thank you
- Makes git history useful

**Tip 4: Link everything**
- Session log → Research docs
- TASKS.md → PR numbers
- Issues → Solutions in session-issues.md
- Makes knowledge discoverable

**Tip 5: Test your handoff**
- Imagine you're the next agent
- Can you resume in <2 minutes?
- Is anything unclear or missing?

---

## 📝 Templates

### Session Log Entry Template
```markdown
## YYYY-MM-DD — Session (Brief Title)

**Focus:** Main goal or area of work

### Summary
- Key accomplishments (bullets)
- Issues encountered and resolved
- Decisions made

### PRs Merged (if any)
| PR | Summary |
|----|---------|
| #XXX | Description |

### Key Deliverables
- File paths or features delivered
- Links to docs/research

### Next Actions
- What's pending or blocked
- Recommendations for next session
```

### Next Session Brief Update Template
```markdown
## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: YYYY-MM-DD
- Focus: [What you worked on]
- Completed: [Key accomplishments - bullets]
- Next: [What's pending, blocked, or recommended]
<!-- HANDOFF:END -->
```

### Session Issues Entry Template
```markdown
## YYYY-MM-DD (Session Title)

### Issues Seen
- **[Issue name]:** Brief description

### Cause
- Root cause analysis

### Fixes Applied
- Solution implemented
- Commands used

### Prevention
- How to avoid in future
- What to check before similar work
```

---

## 🎯 Success Criteria

**Your handoff is successful if the next agent can:**

✅ Resume work in <2 minutes
✅ Understand what was done last session
✅ Know what's pending or blocked
✅ Find relevant research/docs quickly
✅ Avoid issues you already solved
✅ Pick up any incomplete work easily

**If any of these fail, improve your handoff documentation.**

---

## 🔗 Related Documentation

- **session.py end usage:** Run with `--help` for full options
- **Automation catalog:** [docs/reference/automation-catalog.md](../reference/automation-catalog.md)
- **Session issues log:** [docs/contributing/session-issues.md](session-issues.md)
- **Session log:** [docs/SESSION_LOG.md](../SESSION_LOG.md)
- **Handoff quick start:** [docs/handoff.md](handoff.md)

---

**Version:** v1.0 (2026-01-06)
**Maintained by:** PM + DOCS agents
**Update when:** End-session process changes, new tools added
