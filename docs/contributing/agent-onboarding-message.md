# First Message for New Agents

> **Copy-paste this exact message to any new agent starting work on this project.**

---

## 📋 The Message

```
Hi! You're working on the structural_engineering_lib project - an IS 456 RC beam design library with Python + VBA parity.

🚀 FIRST: Run this command immediately:
```bash
.venv/bin/python scripts/start_session.py
```

This shows: version, branch, active tasks, blockers, and doc freshness.

📖 THEN: Read these 3 documents in order (takes ~10 minutes):

1. **docs/agent-bootstrap.md** - Quick start guide (this is your roadmap)
2. **docs/ai-context-pack.md** - Project summary, architecture, golden rules
3. **docs/TASKS.md** - Current work (Active, Up Next, Backlog)

⚠️ CRITICAL: Before ANY commit, read:
- **.github/copilot-instructions.md** - Mandatory rules (git workflow, coding standards, pitfalls)

🎯 Key principles:
- ALWAYS use `./scripts/safe_push.sh "message"` for commits (never manual git)
- Production code → ALWAYS use PR (never direct commit)
- Docs/tests/scripts → Check size first: `./scripts/should_use_pr.sh --explain`
- Run tests locally before pushing: `pytest tests/test_<file>.py -v`
- If info is likely outdated (models, versions, CLI flags), verify online first

📍 You are here: [Describe current task or "Ready to receive instructions"]

What would you like me to work on?
```

---

## 🎓 Why This Works

**1. Immediate Action** - `start_session.py` gives instant context
**2. Progressive Loading** - 3 docs in logical order (~10 min total)
**3. Critical Safety** - copilot-instructions.md prevents common mistakes
**4. Key Tools** - Highlights the 2 most important scripts
**5. Engagement** - Ends with a question to start the conversation

---

## 📝 Usage Examples

### Example 1: Brand New Agent (First Time)
**User:** "Hi, can you help me with this project?"
**Agent Response:** [Copy-paste the message above]

### Example 2: Returning Agent (New Session)
**User:** "Let's continue where we left off"
**Agent Response:**
```
Welcome back! Let me check current state:
[Runs start_session.py]
[Reviews TASKS.md for Active work]
[Reads planning/next-session-brief.md]

Current status:
- Version: 0.14.0
- Branch: main
- Active tasks: [list from TASKS.md]
- Last session: [summary from next-session-brief.md]

Ready to continue. What would you like to work on?
```

### Example 3: Specialized Task (e.g., Testing Focus)
**User:** "I need help writing tests for the new feature"
**Agent Response:**
```
[Runs start_session.py]

I see we're working on [feature]. For testing, I'll need:
1. docs/testing-strategy.md - Test patterns and requirements
2. docs/verification-pack.md - Benchmark test cases
3. Python/tests/ - Existing test structure

Let me review these and then propose test coverage for [feature].
```

---

## 🔄 Maintenance

**When to update this:**
- Project structure changes (new critical docs)
- Workflow changes (new mandatory tools)
- Common onboarding issues discovered

**Who updates this:**
- PM or DOCS agent after onboarding improvements
- After any major documentation restructuring

**Version:** v1.0 (2026-01-06)
