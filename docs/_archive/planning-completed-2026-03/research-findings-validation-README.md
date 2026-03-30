# Research: Findings Validation & Evidence Strengthening

> **Template version:** 1.0

**Last Updated:** 2025-12-31
**Status:** Draft
**Owner:** RESEARCHER
**Decision Date:** 2026-01-07

---

## Problem Statement

We need to validate and strengthen the evidence behind public-facing research claims (blog + roadmap) so statements are accurate, well-sourced, and defensible for engineers.

---

## Context

Triggered by a review of `docs/publications/findings/*` and blog outlines. Several claims are based on anecdotal or vendor sources, and some are phrased as universal facts. The user requested deeper research before changing the content.

---

## Users & Personas

| User | Context | Pain Point |
|------|---------|------------|
| Practicing structural engineer | Reads blog for practical trust signals | "Is this claim backed by a real source?" |
| Engineering manager | Evaluates tool adoption | "Are the claims defensible in a QA review?" |
| Maintainer | Publishes content | "I don't want to over-claim and lose credibility." |

---

## Constraints (Non-Negotiables)

- [ ] Deterministic claims (no unverifiable absolutes)
- [ ] Prefer primary sources (standards, papers, case studies)
- [ ] Label anecdotal evidence as anecdotal
- [ ] No new required dependencies
- [ ] Keep current findings unchanged until verification is complete
- [ ] Every public claim mapped to at least one citation or downgraded

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Claim ledger coverage | 100% of blog claims mapped to sources |
| Evidence quality | Top 10 claims backed by primary or peer-reviewed sources |
| Over-claim removal | 0 absolute claims without hard evidence |
| Documentation | Research log + citations updated with links |

---

## Options Explored

### Option A: Deep Verification (Primary-Source First)

**Description:** For each major claim, locate primary sources (standards, journals, official reports) and rewrite claims to match evidence levels.
**Pros:** Highest credibility; academic-grade citations.
**Cons:** Time-intensive; some sources may be paywalled.

### Option B: Targeted Verification (Top 10 Claims)

**Description:** Validate the most important/topline claims first; downgrade or label the rest.
**Pros:** Faster; improves trust for core narrative.
**Cons:** Some secondary claims remain anecdotal.

### Option C: Conservative Rewording Only

**Description:** Reword claims to be clearly conditional/anecdotal without new research.
**Pros:** Fast; avoids over-claiming.
**Cons:** Weakens authority; no new evidence.

---

## Scoring Rubric

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Trust Impact** | High | Does this raise engineer confidence? |
| **User Value** | High | Does it protect credibility? |
| **Effort** | Medium | How much research time? |
| **Dependency Risk** | Medium | Paywalls, non-reproducible sources |
| **Alignment** | Low | Fits current publication plan |

### Scored Options (Preliminary)

| Option | Trust | Value | Effort | Risk | Alignment | Total | Rank |
|--------|-------|-------|--------|------|-----------|-------|------|
| A | 5 | 5 | 2 | 3 | 4 | 19 | 1 |
| B | 4 | 4 | 4 | 4 | 5 | 21 | 2 |
| C | 2 | 3 | 5 | 5 | 5 | 20 | 3 |

*Lower effort/risk is better; invert scores when totaling for final decision.*

---

## Decision

**Chosen option:** TBD
**Rationale:** Pending initial source audit and timebox decision.

**What we will NOT do (and why):**
- No sweeping edits to existing findings until verification is done.

---

## Parking Lot

| Idea | Why Parked | Revisit When |
|------|------------|--------------|
| Paid database subscriptions | Cost + access | If blog becomes commercial effort |
| Full competitive teardown | Requires hands-on trials | Post-v1.0 |

---

## Next Steps

- [ ] Create claim ledger and evidence levels
- [ ] Build source verification queue
- [ ] Gather primary sources for top 10 claims
- [ ] Propose wording updates (separate doc)

---

## Changelog

| Date | Change |
|------|--------|
| 2025-12-31 | Initial draft |
