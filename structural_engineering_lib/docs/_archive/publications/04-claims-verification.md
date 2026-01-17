# Claims Verification Ledger

**Purpose:** Track key public-facing claims, sources, evidence strength, and verification status.
**Status:** In progress
**Owner:** RESEARCHER
**Last updated:** 2025-12-31

---

## Evidence Levels

- **Primary:** Standards, peer-reviewed papers, official government reports.
- **Secondary:** Industry blogs, vendor marketing, curated articles.
- **Anecdotal:** Forums, user comments, individual reports.

---

## Claim Ledger (Draft)

| ID | Claim | Sources | Evidence | Status | Notes |
|----|-------|---------|----------|--------|-------|
| C-001 | 80-90% of spreadsheets contain errors | Maplesoft blog | Secondary | Pending | Seek primary study or meta-analysis. |
| C-002 | ETABS API fails 8/10 times on startup | ResearchGate thread | Anecdotal | Pending | Treat as anecdotal unless corroborated. |
| C-003 | Constructability scoring yields 7-10% savings | BCA + academic paper | Primary? | Pending | Need exact source for the 7-10% number. |
| C-004 | No product offers sensitivity analysis in Excel | Product survey | Secondary | Pending | Rephrase as "no evidence found in this review." |
| C-005 | No IS 456 beam design library (Python or VBA) | GitHub survey | Secondary | Pending | Verify with explicit repo searches + date stamp. |
| C-006 | ML requires thousands of samples for beam design | Academic papers | Secondary | Pending | Replace with "many ML papers use large datasets." |
| C-007 | Engineers iterate 10-20 times per beam | Forum discussions | Anecdotal | Pending | Label as anecdotal or remove if unsupported. |
| C-008 | 100% accuracy on golden vectors (3-4 cases) | Test logs | Primary (internal) | Pending | Must state sample size; avoid universal claim. |
| C-009 | Excel users dislike black-box tools | SkyCiv blog | Secondary | Pending | Prefer survey data if available. |
| C-010 | Singapore mandates constructability scoring | BCA + academic paper | Primary | Pending | Validate exact mandate language. |

---

## Verification Queue (Top Priority)

1. C-003: Find primary source for 7-10% savings or remove claim.
2. C-001: Locate original study behind error rate (if any).
3. C-010: Confirm mandate language and scope (building vs element level).
4. C-004/C-005: Document scope of product survey + date stamped search notes.
5. C-008: Confirm test case count and wording for "golden vectors."

---

## Notes

- Keep existing findings unchanged until claims are verified or reworded.
- Any claim that stays anecdotal must be clearly labeled as such in blog drafts.
