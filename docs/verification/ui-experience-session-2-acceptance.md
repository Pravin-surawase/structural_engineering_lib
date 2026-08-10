---
owner: Main Agent
status: active
last_updated: 2026-08-10
doc_type: reference
complexity: advanced
tags: [verification, react, fastapi, workflow, uix]
---

# UIX-001 Session 2 Acceptance

This is the software acceptance record for UIX-001 P9-P15. It does not certify
the formulas, approve a structural design, or authorize professional use.

## Accepted product story

| Journey | Maintained evidence |
|---|---|
| Quick beam | Safe result becomes current and exportable; unsafe 200 x 300 mm, 2,000 kNm, 500 kN case shows FAIL and disables export; an edit makes evidence stale until recalculation |
| Imported project | Bundled sample imports 153 beams across six stories, settles 153 PASS / 0 FAIL, and reaches canonical results |
| Project evidence | Results show 100%, 1,831.3 kg steel, 48.7 m³ concrete, and calculation identity `daf4db29b14ad439c34c9a941e086d878c0dcdfbfd0829a30c49e811986361ac` |
| Resume | A fresh direct results URL waits for IndexedDB hydration and restores the project instead of redirecting to false recovery |
| Export | Quick and project report requests return HTTP 200 only from current accepted evidence |
| Curated workflow | Reviewed safe run completes; unsafe run stops at review with `UNSAFE_RESULT`; a saved local draft reloads its saved inputs |
| Legacy routes | `/start`, `/design`, `/import`, `/editor`, `/dashboard`, and `/batch` resolve to their canonical workbench destinations; an empty legacy results link exposes an explicit recovery reason |
| 3D fallback | Simulated WebGL context loss exposes `3D context interrupted` while current evidence and project actions remain available in the DOM |

The workflow runner remains default-disabled and is available only through the
explicit development/test flags. The generated provider-neutral manifest does
not activate AI chat, autonomous execution, or an external integration.

## Root-cause fixes found during acceptance

| Observed outcome | Root cause | Fix and proof |
|---|---|---|
| Initial quick result remained Calculating after server HTTP 200 | React Strict Mode cancelled the first effect-owned request, while a one-shot ref prevented the replacement setup | Retain the latest design runner; Strict Mode regression proves first cancellation and second-result ownership |
| Catalogue mode showed duplicate engineering inputs | The schema renderer was added alongside, rather than instead of, the manual input surface | Catalogue/manual render boundary now permits one input owner; component and live locator checks find one shear and one concrete control |
| Direct canonical results reload entered recovery | Route guards redirected while persistence was still `idle`, before the bridge entered `loading` | Guards treat idle/loading as hydration; focused route test and fresh live reload preserve results |
| Full gate rejected P9 public API/doc state | Generated API manifest was stale and frontmatter used a semantic phrase outside the validator vocabulary | Regenerated the canonical manifest and used `active` frontmatter while retaining development-preview limits in the body |

## Verification matrix

- 91 focused Python/FastAPI catalogue, workflow, evidence, and API tests.
- 87 focused React route, catalogue, automation, lifecycle, workspace, and
  viewport tests; 76 focused geometry/streaming tests.
- 29 React request call sites match the maintained FastAPI/OpenAPI contracts.
- `./run.sh frontend check`: lint, 239 tests in 42 files, production build.
- `./run.sh check --quick`: 10/10.
- `./run.sh check`: 30/30 at the stable integrated P15 milestone.
- Maintained Chromium at 390 x 844, 1024 x 768, and 1440 x 900 has no document
  horizontal overflow and retains the critical workbench actions.
- The 153-member viewport at 390 px remained usable in 122.6 ms, with 14.2 ms
  average / 28.7 ms maximum sampled frame time, 155 draw calls, 165 geometries,
  and four textures.

Pull-request checks remain the merge authority after local acceptance.

## Holds and tooling limits

- Firefox support, exact Safari responsive automation, GitHub Pages, public
  workflow-runner activation, release/tag/package publication, and professional-
  use claims remain outside this acceptance.
- Safari desktop smoke remains Session 1 evidence; Chromium is the maintained
  exact-width authority.
- The in-app browser did not emit a download event for programmatic Blob-anchor
  downloads, but the export requests returned HTTP 200 and no browser error.
- Device emulation screenshots tiled in the observer, so exact DOM widths and
  overflow metrics—not those image artifacts—are the responsive authority.
