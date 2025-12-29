# Handoff Quick Start

Goal: enable the next agent to resume in under 2 minutes.

---

## Resume (next agent)
1. Run: `.venv/bin/python scripts/start_session.py`
2. Read:
   - `docs/planning/next-session-brief.md` (what changed + blockers)
   - `docs/contributing/session-issues.md` (recent pitfalls + fixes)
   - `docs/TASKS.md` (active + up next)
3. If releasing: `./scripts/ci_local.sh` then `python scripts/verify_release.py --version X.Y.Z --source pypi`

## Handoff (ending)
1. Run: `.venv/bin/python scripts/end_session.py --fix`
2. Update `docs/planning/next-session-brief.md` with summary + blockers.
3. Update `docs/TASKS.md` (move items to Done/Active).
4. Ensure clean tree: `git status -sb`

## Common Traps (fast fixes)
- CI watch times out: re-run `gh pr checks <num> --watch`.
- PR behind base: `gh pr update-branch <num>` then re-check CI.
- PyPI verification: always use a clean venv.
