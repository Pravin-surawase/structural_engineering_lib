# Documentation Template

**Type:** Guide
**Audience:** Developers
**Status:** Approved
**Importance:** Medium
**Version:** 1.0.0
**Created:** 2026-01-10
**Last Updated:** 2026-01-13

---

## Doc Front-Matter Guide

Copy this header to new documentation files and fill in the metadata.

**Fields:**
- `owner`: Who maintains this doc (Main Agent, Agent 9, User)
- `status`: active | draft | deprecated | archived
- `last_updated`: YYYY-MM-DD format
- `doc_type`: guide | reference | tutorial | index | spec | log
- `complexity`: beginner | intermediate | advanced
- `tags`: Optional array of keywords

## Template Header

```markdown
# Document Title

**Type:** [Guide|Research|Reference|Architecture|Decision|Implementation]
**Audience:** [All Agents|Developers|Users|Maintainers]
**Status:** [Draft|In Progress|Review|Approved|Complete|Deprecated]
**Importance:** [Critical|High|Medium|Low]
**Version:** 1.0.0
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Related Tasks:** TASK-XXX
```

## Front-Matter Notes

**owner:**
- Main Agent: General documentation
- Agent 9: Governance and sustainability docs
- Agent 8: Velocity and automation docs
- User: User-maintained docs

status:
  - active: Current and maintained
  - draft: Work in progress
  - deprecated: Superseded, still accessible
  - archived: Moved to _archive/

doc_type:
  - guide: How-to instructions
  - reference: API/technical reference
  - tutorial: Step-by-step learning
  - index: Navigation/overview page
  - spec: Technical specification
  - log: Session logs, changelogs

complexity:
  - beginner: New users, basic concepts
  - intermediate: Familiar users, standard tasks
  - advanced: Expert users, complex scenarios

tags:
  - Optional array of keywords for search/filtering
  - Example: ['streamlit', 'ui', 'testing']
-->

## Introduction

Brief description of what this document covers.

## Content

Main content here.

## See Also

- Related doc links
