---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: log
---

# Dependency and Security Baseline

This record makes MAINT-003 reproducible. It separates confirmed vulnerabilities
from transferred-environment residue and records every temporary exception.

## Baseline (2026-08-07)

| Surface | Before | Maintained state | Verification |
|---------|--------|------------------|--------------|
| Python transferred `.venv` | 98 findings across 21 packages | Not a source of truth; it contained undeclared/stale packages including retired `python-jose` and `ecdsa` | Rebuilt from `requirements.txt` in a clean Python 3.11.15 environment |
| Python clean environment | Four findings in `cryptography` 46.0.7 | `cryptography` 50.0.0; zero known vulnerabilities across 147 installed dependencies | `pip-audit --path <clean-site-packages>` |
| Python declarations | FastAPI tests relied on undeclared `pytest-asyncio` | Plugin declared in both root requirements and the package `dev` extra | 5,146 core tests collected; 5,138 passed and 8 skipped; 326 FastAPI tests passed |
| Python lock | Contained an editable Git URL and stale `python-jose`/`ecdsa` residue | Regenerated from a clean environment with `pip freeze --exclude-editable` | `pip check` passes and package/module versions both report 0.21.6 |
| React/npm | 13 findings: 11 high, 1 moderate, 1 low | One underlying high advisory remains, represented as two dependency nodes | 139 tests, lint, build, and a reviewed production audit on Node 24 |

## Temporary npm Exception

- **Advisory:** `GHSA-qwww-vcr4-c8h2` — React Router RSC action CSRF bypass.
- **Observed packages:** `react-router` and direct dependency `react-router-dom`.
- **Why it is not currently exploitable here:** the application uses `BrowserRouter`,
  `Routes`, and browser-only Vite rendering. It does not enable React Server
  Components or React Router RSC action handling, which is the affected mode.
- **Why no automated downgrade was applied:** npm proposes `react-router-dom`
  7.11.0, but that would move backward across other previously fixed advisories.
  A patched 8.3.0 package was not available in the npm registry when checked.
- **CI policy:** only this exact advisory and these two package nodes are allowed.
  Any additional npm package or advisory fails the security workflow.
- **Removal condition:** remove the exception immediately when a compatible patched
  React Router release exists, or before introducing any RSC/server-action mode.

## Reproduction

Use a disposable Python 3.11 environment; do not regenerate the lock from the
long-lived workspace `.venv`.

```bash
python3.11 -m venv <temporary-venv>
<temporary-venv>/bin/python -m pip install -r requirements.txt
<temporary-venv>/bin/python -m pip install --no-deps --no-build-isolation -e Python/
<temporary-venv>/bin/python -m pip check
<temporary-venv>/bin/python -m pip freeze --exclude-editable
pip-audit --path <temporary-venv>/lib/python3.11/site-packages
```

For the frontend, use Node 24 from `.nvmrc`, then run:

```bash
cd react_app
npm ci
npm test
npm run lint
npm run build
npm audit --omit=dev
```

## Automation

- `.github/workflows/security.yml` audits the exact Python lock and the production
  npm graph. New findings fail the job.
- `.github/dependabot.yml` monitors root Python requirements, the distributable
  Python package, npm dependencies, and GitHub Actions every week.
