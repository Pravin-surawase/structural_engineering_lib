# Agent Guides

**Purpose:** Stable reference documentation for each agent's protocols, tools, and best practices.

---

## Agent 8 - Git Operations Automation

**Mission:** Single source of truth for all git operations, preventing conflicts and ensuring consistency.

### Core Documentation
- [agent-8-quick-start.md](agent-8-quick-start.md) - 60-second onboarding
- [agent-8-git-ops.md](agent-8-git-ops.md) - Core protocol (1,320 lines)
- [agent-8-automation.md](agent-8-automation.md) - Script index & usage
- [agent-8-mistakes-prevention-guide.md](agent-8-mistakes-prevention-guide.md) - Historical mistakes DB (1,096 lines)
- [agent-8-implementation-guide.md](agent-8-implementation-guide.md) - Setup & implementation
- [agent-8-multi-agent-coordination.md](agent-8-multi-agent-coordination.md) - Multi-agent workflows
- [agent-8-operations-log-spec.md](agent-8-operations-log-spec.md) - Log format specification

### Tools & Scripts
All Agent 8 scripts are in [../../scripts/](../../scripts/) - see [agent-8-automation.md](agent-8-automation.md) for complete index.

### Research & Analysis
Agent 8 research documents remain in [../research/](../research/) for centralized research organization.

---

## Agent 9 - Governance & Documentation Structure

**Mission:** Maintain sustainable information architecture, govern folder structure, ensure migration safety.

### Core Documentation
- [agent-9-quick-start.md](agent-9-quick-start.md) - 60-second onboarding
- [agent-9-governance-hub.md](agent-9-governance-hub.md) - Access point to all governance docs
- Full governance docs: [../../agents/agent-9/governance/](../../../agents/GOVERNANCE.md)

### Key Rules
- Root directory: <10 files
- Kebab-case naming for all docs
- Scripts stay in `scripts/` (Rule 3.2)
- Time buckets for dated docs: `sessions/YYYY-MM/`
- Git mv for file moves (preserve history)

### Validation Tools
- `validate_folder_structure.py` - Check rule compliance
- `check_links.py` - Find broken links
- `check_docs_index_links.py` - Verify index accuracy
- `check_root_file_count.sh` - Ensure <10 root files

---

## Adding New Agent Guides

When creating documentation for a new agent:

1. **Create guide files** in this folder: `agent-N-*.md`
2. **Add entry** to this README.md
3. **Add section** to parent `docs/agents/README.md`
4. **Keep it stable** - guides are long-lived reference docs

---

**Last Updated:** 2026-01-10
