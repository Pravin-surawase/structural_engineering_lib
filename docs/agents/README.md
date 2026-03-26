# Agent Documentation Hub

> **For AI Agents:** Use the semantic registry below to find the right docs quickly.
> **Start here** → Find your agent → Read Quick Start → Use Hub for details.

---

## 🎯 Agent Registry (Semantic Index)

| Agent | Role | Domain | Quick Start | Hub | Complexity |
|-------|------|--------|-------------|-----|------------|
| **8** | Git Operations | Commits, PRs, conflict prevention | [Automation](guides/agent-8-automation.md) | [Full Hub](guides/agent-8-git-ops.md) | 🟡 Intermediate |
| **9** | Governance | Docs structure, migrations, quality | [60s Start](guides/agent-9-quick-start.md) | [Full Hub](guides/agent-9-governance-hub.md) | 🟡 Intermediate |

### 📋 When to Use Each Agent

| Task | Agent | Key Docs |
|------|-------|----------|

| Commit code changes | **8** | [ai_commit.sh](../../scripts/ai_commit.sh), [safe_push.sh](../../scripts/safe_push.sh) |
| Fix merge conflicts | **8** | [mistake-prevention](guides/agent-8-mistakes-prevention-guide.md) |
| Reorganize docs | **9** | [governance spec](../guidelines/folder-structure-governance.md) |
| Clean up stale files | **9** | [check_redirect_stubs.py](../../scripts/_archive/check_redirect_stubs.py) |

---

## 📂 Structure

### guides/
Agent-specific guides, protocols, and reference documentation:
- **Agent 8 (Git Operations):** Git workflow automation, mistake prevention, coordination
- **Agent 9 (Governance):** Documentation governance, migration plans, quality standards

### sessions/
Time-bucketed session logs and summaries by month:
- `2026-01/` - January 2026 sessions
- Future months as they occur

---

## Quick Links

### Agent 8 - Git Operations Automation
**Mission:** Prevent merge conflicts, automate git workflows, ensure safe commits

- [Automation Index](guides/agent-8-automation.md) - Quick start + all scripts & tools
- [Git Operations Protocol](guides/agent-8-git-ops.md) - Core mission & workflow
- [Mistake Prevention](guides/agent-8-mistakes-prevention-guide.md) - Historical mistakes database
- [Multi-Agent Coordination](guides/agent-8-multi-agent-coordination.md) - Work with background agents
- [Operations Log Spec](guides/agent-8-operations-log-spec.md) - Log format specification

### Agent 9 - Governance & Documentation Structure
**Mission:** Maintain sustainable information architecture, govern folder structure, ensure migration safety

- [Quick Start](guides/agent-9-quick-start.md) - Get started in 60 seconds
- [Governance Hub](guides/agent-9-governance-hub.md) - Access all governance docs
- [Governance Spec](../guidelines/folder-structure-governance.md) - Folder structure rules

---

## Related Documentation

- [Scripts Directory](../../scripts/) - All automation scripts (shared across agents)
- [Research](../research/) - Agent research and analysis

---

**Last Updated:** 2026-01-10
