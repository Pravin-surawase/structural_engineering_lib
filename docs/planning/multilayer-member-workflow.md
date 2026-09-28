# LIB-MEMBER-WORKFLOW-002 — multilayer beam acceptance

Owner: Main Agent. Authorized by the owner on 28 September 2026. Baseline:
PR #1016, `0793a34f2bbefd6253a3b608c1c4226fdf56fc84`; Mac is the sole writer
on `codex/lib-member-workflow-002`. The separate unpublished solver candidate
remains held and must be rebound before future integration.

## Frozen scope and case

Extend the existing public physical-beam workflow with one ordinary rectangular
beam: 300 × 500 mm, M25, Fe415 deformed bars, 25 mm nominal cover, 20 mm
aggregate, mild exposure, simply supported at 0/5000 mm. Bearing faces remain
−200/200 and 4800/5200 mm; all longitudinal bars run from −175 to 5175 mm.
Two 25 mm bottom bars lie at each of y=450 and 375 mm; two 16 mm top bars lie
at y=50 mm and two 12 mm top bars at y=125 mm. Each pair lies at x=50/250 mm.
The area-weighted bottom depth is 412.5 mm. Existing two-leg 8 mm links at
150 mm and explicit hooked fabrication paths are retained.

Separate total uniform loads, including self weight: ULS 36 N/mm, SLS
24 N/mm. Independent statics give ULS 112.5 kNm/90 kN and SLS 75 kNm.
No axial load, biaxial bending, torsion demand, seismic frame, lap, curtailment,
support congestion, special exposure/fire requirement or package release is
selected. Physical support fit beyond this admitted case remains separate.

## Root cause and implementation boundary

The current physical capacity owner assumes yielded tension bars and uses one
compression centroid. The frozen layers cross different steel stress ranges,
so those assumptions do not represent their actual forces or lever arms.
Replace this calculation in Python and .NET with signed per-bar strains from
a plane section, equilibrium of concrete plus every bar's net force, and the
sum of their moments. Deduct displaced concrete at the actual compression-bar
strain. Face labels continue to own reinforcement-group limits, not stress sign.

Use the source-normalized Fig 23 curve, including its 0.975fy point, with
Es=200000 N/mm² and design steel strength fy/1.15. Fe250 uses a definite yield
point; the declared deformed-bar profile uses Fig 23A. Keep the existing
rectangular/eligible-flange design concrete blocks (38.1/Fig 22/Annex G).
Check 38.1(f) at the most strained tension bar. Return the actual equilibrated
capacity even for a ductility failure, with FAIL; do not clamp the neutral axis
and present unequilibrated forces. Retain existing request constructors,
operation IDs, explicit units and new method provenance.

The controlled IS 456 source was visually checked at printed pages 69–70
(PDF pages 70–71), Fig 21–23 and 38.1. Its SHA256 is
`964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`.
Amendment 6 remains bound by the existing workflow. Only normalized equations,
values and references enter the repository.

## Acceptance and verification

1. Retain each physical bar's depth, area, signed strain, steel/concrete stress
   and net force in capacity results in both languages; force residual <1e-6 N.
2. Independently implement the normalized material and force/moment equations
   and solve with SciPy Brent, without calling production material/section
   helpers. Freeze reference vectors for the case, mirrored bending,
   mixed stress ranges, a nominal top bar in tension, and over-reinforcement.
   Compare neutral axis within 1e-7 mm, capacity within 1e-7 kNm and bar stresses
   within 1e-6 N/mm². Also quantify the design-block approximation against
   direct numerical integration of Fig 21; do not call the models identical.
3. Run the existing complete workflow plus the multilayer case through geometry,
   depth, flexure, shear, torsion, serviceability, every bar end, continuity,
   arrangement, actual paths, member acceptance, BBS, quantities and report.
   The new case has 27 required leaves and 43 physical bars. Omitted leaves,
   overload and insufficient embedment must remain unevaluated/failed and draft.
4. Independently derive cracked elastic SLS inputs at the actual layers. Keep
   span/depth screening explicit; no calculated long-term displacement claim.
   Preserve a report table of per-bar ULS evidence and all source identities.
5. After content freezes, batch affected formatting, WP01/WP02 and workflow
   tests, .NET physical-caller tests, semantic contract checks and changed-area
   repository checks. Build and replay an installed wheel outside the checkout;
   record observed process timing without a speedup claim. No broad local suite
   is needed: the affected physical owners and consumers are the concrete risk;
   required hosted checks cover the integrated Python/.NET/backend callers.
6. Review the essential diff, publish one milestone PR, repair any confirmed
   failure at its owner, pass required checks on the unchanged reviewed head,
   merge, verify clean synchronized Mac main, and close the task timer.

General service-stress/crack-input APIs, calculated short/long-term deflection,
new element families, general axial/biaxial section analysis, UI work, installed
Excel/ETABS qualification and publication remain separate milestones.

## Delivery evidence

The implementation uses the existing public capacity/check operations and
extends the complete example with `--case multilayer`. No optional numerical
dependency is added to the installed library. Python's pure material functions
live in `codes/is456/section_materials.py`; the physical owner and C# counterpart
perform equilibrium and retain the per-bar outputs. The independent generator
under `Python/tests/data/benchmark_vectors/` imports only NumPy/SciPy and standard
Python, and freezes 27 vectors in the shared semantic conformance directory.
Both language suites consume those same independently generated values.

| Independently checked item | Result |
|---|---|
| Frozen multilayer axis / resistance | 191.4090471482 mm / 235.9565626329 kNm |
| Old centroid resistance for the same case | 236.7818129291 kNm; the old calculation overestimated this resistance by 0.8252502963 kNm |
| Outer / inner bottom steel stress | −360.8695652174 / −357.0082724906 N/mm²; the inner layer has not reached the plateau |
| Outer / inner top steel stress | 347.3119353282 / 242.8638232954 N/mm²; the inner layer is elastic |
| Direct Fig 21 numerical integration | 236.5631985787 kNm; the retained normalized design block gives 0.25644% less for this case |
| Reference matrix | 27 vectors: 19 admissible and 8 ductility failures; Fe250/415/500, M20/25/40, 20/25/32 mm bottom bars, mirrored and reverse bending, nominal top steel in tension, T/L branches, and prior single-layer case |
| Cracked SLS section | x=156.4663217403 mm; Icr=1468328057.5917 mm⁴; centroid steel stress=104.6225372876 N/mm² |
| Service crack width / limit | 0.1537710802 / 0.3 mm; no tension-stiffening reduction |
| Span/depth screening | 12.1212121212 / 20; Fig 4 factor 1.0 conservatively below the source curve at p=1.586663%, fs=104.6225 N/mm² |
| Shear resistance / ULS demand | 193.1068649628 / 90 kN |
| Longitudinal development | 25 mm bottom Ld=1007.3939732143 mm; equivalent available=1125 mm, actual extension=375 mm |
| Physical output | 43 bars, 129.9145808448 kg, 0.81 m³ concrete, 7.08 m² formwork |

Fig 4 was visually rechecked at printed page 38 (PDF page 39). Per-bar ULS
stresses are resistance-state values, not stresses under the applied SLS load.
The SLS stress supplied to Annex F is at the bottom group's centroid; its
derivation and individual layers are retained in the test arithmetic. The
original 001 case remains accepted with v3 resistance 94.6188554985 kNm;
its earlier v2 values remain historical evidence.

The new replay tests omit each of all 27 required leaves in turn and retain an
unevaluated member/draft package. Actual overload and 5 mm support embedment
remain engineering failures with draft HTML/CSV. Every bar response survives
JSON serialization. Final focused checks and installation measurements are
recorded below; GitHub owns the reviewed head, hosted verdict and merge commit.

### Frozen candidate validation

- Affected Python union: **189 passed**, one unrelated snapshot case deselected.
  This covers WP01/02/04/06/07/08, the independent per-bar references, both
  complete cases and maintained candidate-ranking consumers.
- .NET SDK 10.0.400: zero build warnings/errors; **142 passed**, one existing
  proprietary-snapshot case skipped. WP01/02/04/06/07/08, per-bar references and
  maintained baseline consumers ran. This is portable source evidence, not an
  installed Excel session; required hosted checks also run Windows callers.
- Changed-path Ruff/Black/.NET formatting passed with a clean scope guard;
  **12/12** essential repository checks, semantic contracts and token-efficiency
  policy passed. No broad local Python suite or full repository audit was run.
- A fresh Python 3.11.15 environment outside the checkout imported the built
  package from `site-packages`, with source-path environment overrides removed
  during installation and execution. Wheel SHA256:
  `fc49d422c78327490a31c91dcf4b3bca0d0af44b499d9339cb530fd1e2909159`.
  Both nominal cases yielded `issue_ready` with approval false; missing flexure,
  overload and insufficient embedment replays yielded draft artifacts.
- Seven fresh installed processes (imports, calculation, serialization and
  HTML/JSON/CSV writes) took **0.720148084, 0.720260500, 0.719535875,
  0.744679041, 0.727283583, 0.725243333, 0.721633750 seconds**;
  median **0.721633750 s** on this Mac with a warmed filesystem. Single-layer
  compatibility replay took 0.712549125 s. These are observations without a
  comparative speedup or whole-building throughput claim. Source preparation,
  engineering review, installation and hosted CI are excluded.

Caller effort remains explicit: select the frozen case and output directory,
provide/verify its source admission and SLS section basis, then invoke the
single example command. The report, calculation JSON and physical-bar CSV are
generated together; no manual bar-response or leaf-state editing is required.
The example is not an automatic design input builder for arbitrary beams.
