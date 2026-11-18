# Using StructLib for reinforced-concrete elements

**Type:** Guide
**Audience:** Users and Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-11-18
**Last Updated:** 2026-11-18
**Abstract:** Published Python workflows, engineering sources, and completion criteria for StructLib element cases.

---

## Start with a supported case

Use this guide to choose a public Python workflow, run a known example and
decide what evidence is needed to use or extend it. The examples below are
anchored to the published **StructLib 0.31.0** package. The
[capability register](../verification/indian-code-capability-coverage.json)
owns the exact supported and held cases. The
[generated contracts](../reference/family-facade-contracts.md) own signatures,
input units, result fields and diagnostics.

With Python 3.11 or newer and an activated virtual environment, install the
release used in this guide.

```bash
python -m pip install "structural-lib-is456==0.31.0"
python -m structural_lib install-preflight --json
```

Check that the reported version is 0.31.0 and the package origin belongs to
the intended environment. See the [PyPI release](https://pypi.org/project/structural-lib-is456/0.31.0/)
and [PyPA virtual-environment guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

1. Choose a recipe whose geometry, support, action and reinforcement basis
   match your case. Run its first Python block with the supplied inputs.
2. Compare the returned outcome to the
   [cookbook's expected result](../cookbook/python/family-facades.md). The
   two-way slab example intentionally returns `FAIL` and the straight-flight
   staircase example intentionally returns `HOLD`. Both demonstrate how to
   read a valid result and its reasons.
3. Replace the example inputs with project-owned values. Keep member and
   case IDs, geometry, units, sign conventions and source revisions. Supply
   the required service and factored actions separately where the contract
   asks for both. For strict Generic CSV input, supply an actual positive
   span for every beam. [CSV migration notes](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.31.0)
4. Read the engineering status, governing check, assumptions, limitations and
   review requirement. Record the input, package version and result together.
   Use only the exports provided by that workflow, and keep them tied to the
   checked member and revision.

| Result | What to do |
| --- | --- |
| Input rejected | Read structured field issues, correct the source input, and rerun. |
| `FAIL` | Inspect the governing check, revise the supplied design or reinforcement, and rerun. |
| `HOLD` | Resolve the recorded missing evidence or applicability limit before relying on the result. |
| `PASS` | The checks represented by the case passed. Send the result and its basis for qualified engineering review. |

For new scripts, start with the documented family facade. Use the
[API chooser](../reference/api-levels.md) if you need physical member checks,
analysis snapshot replay or construction quantities. A recurring job or
AI-assisted tool should preserve these result states and ask for missing data
from its owner. The project supplies approved geometry, actions, soil inputs
and review evidence.

## Choose an element

| Published journey | Start here | Case to match |
| --- | --- | --- |
| Beam | [Beam design](../cookbook/python/beam-design.md) | Ordinary rectangular section with supplied actions, through the supported flexure and shear checks |
| Beam torsion | [Torsion design](../cookbook/python/torsion-design.md) | Bounded beam torsion with the declared action and section basis |
| Column | [Column supplied-steel check](../cookbook/python/column-supplied-steel-check.md) | Supplied reinforcement and supported section, action and effective-length basis |
| One-way slab | [One-way slab](../cookbook/python/slab-one-way.md) | Solid strip with simply supported or documented coefficient-method support conditions |
| Continuous one-way slab | [Continuous one-way slab](../cookbook/python/slab-continuous-one-way.md) | Continuous solid strip that matches the coefficient method's span, restraint and action assumptions |
| Two-way slab | [Two-way slab](../cookbook/python/slab-two-way.md) | Beam- or wall-supported rectangular solid panel with the documented edge conditions and action basis |
| Braced wall | [Braced axial wall](../cookbook/python/wall-braced-axial.md) | Bounded braced wall in axial compression |
| Staircase | [Straight-flight stair](../cookbook/python/staircase-straight-flight.md) | Straight waist-slab flight on the documented longitudinal support basis |
| Deep beam | [Simply supported deep beam](../cookbook/python/deep-beam-simply-supported.md) | Single-span solid rectangle with supplied actions and bearing evidence |
| Flat slab | [Regular interior flat slab](../cookbook/python/flat-slab-regular-interior.md) | Regular interior panel under the admitted uniform-gravity case |
| Isolated footing | [Concentric isolated footing](../cookbook/python/isolated-footing-concentric.md) | Centrally loaded footing on the declared bearing and reinforcement basis |
| Combined footing | [Symmetric combined footing](../cookbook/python/combined-footing-symmetric.md) | Symmetric rectangular footing under equal concentric loads |
| Strap footing | [Property-line strap footing](../cookbook/python/strap-footing-property-line.md) | Two rectangular pads connected by a prismatic strap that spans clear of soil, with the supplied action and review basis |

The existing verifier replayed **all 13 recipes** and **29 acceptance cases**
against the public wheel in an isolated package directory. Its SHA-256 matched
the [0.31.0 release record](../verification/library-0310-release-artifacts.json).
Each recipe establishes its named case. Check the
[evidence crosswalk](../verification/is456-library-first-evidence.md) before
building around more general geometry, loading, serviceability or detailing.

## Run a footing case

Save the first Python block from the
[concentric isolated footing recipe](../cookbook/python/isolated-footing-concentric.md)
as `footing_example.py`. Run it with `python footing_example.py` in the
environment above. The fixture returns `PASS` and prints structured JSON.

For a project request, confirm the footing and column layout, bearing-pressure
basis, service and factored loads and their combinations, reinforcement and
cover, plus the supporting-area and soil evidence required by the chosen
contract. Copying a fixture's approval fields into a project request cannot
supply those project facts. Use a separate checked case for each revision.

Once your reviewed input is in `footing.json`, this calls the same public
function and writes the result as JSON to standard output.

```python
import json
from pathlib import Path

from structural_lib.design.is456 import isolated_footing

request = isolated_footing.load_json(Path("footing.json").read_bytes())
result = isolated_footing.design(request)
print(json.dumps(result.to_dict(), indent=2, allow_nan=False))
```

Use the combined or strap recipe when its actual topology fits. Eccentric
isolated footing, partial contact, raft and pile-cap workflows need their own
scope and evidence. Use project geotechnical inputs and an approved bearing
basis for the footing cases covered here.

## Engineering rules and references

- **Use the governing source.** For each calculation, record the design code,
  edition, applicable amendments, clause, table or figure, and the assumptions
  that make the method applicable. Use [IS 456:2000, Fourth Revision](https://www.services.bis.gov.in/tmp/SR456.pdf)
  with the applicable issued amendments. The official
  [Amendment 6 notification](https://egazette.gov.in/WriteReadData/2024/254982.pdf)
  and the [StructLib amendment crosswalk](../verification/is456-amendment-impact.md)
  distinguish issued source evidence from qualified implementation.
- **State the mechanics and inputs.** For the checks that apply, document load
  path and equilibrium, material and section assumptions, serviceability,
  restraint, constructibility and detailing. Record inputs with units, axes,
  signs, station, load combination and source revision. Separate project load
  generation and global analysis from member checks. For extensions, verify
  the applicable companion standard and edition at the
  [BIS standards portal](https://standards.bis.gov.in/), including the relevant
  parts of IS 875 for design loads, IS 1893 for earthquake criteria, or IS 13920
  for ductile detailing where the case requires them.
- **Identify the role of a worked reference.** SP 34 is a detailing handbook.
  SP 16:1980 is a historical comparison source based on IS 456:1978. BIS
  lists it under withdrawn or superseded publications. Reconcile the edition
  and assumptions before comparing a historical result to a current check.
  [BIS handbook list](https://www.bis.gov.in/wp-content/uploads/2018/11/Special-Publication-CED.pdf) ·
  [BIS withdrawal and supersession list](https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/63/190/)

Keep project-authored derivations and approved normalized data with
clause/table provenance. Keep controlled source prose and pages in the
authorized source record.

## Completion rules for a usable function

Use the existing [function and element completion definitions](../planning/is456-library-first-master-plan.md#6-completion-definitions)
for each named workflow.

1. **Define the case.** State what the caller can ask, the engineering scope,
   the inputs and units, and the result and review requirements. Record which
   adjacent cases are held.
2. **Make the calculation reproducible.** Keep the math in the owning library
   layer. Use independent worked values for the governing checks. Record the
   inputs, result, tolerance and reason for the tolerance. Include the
   governing boundary and invalid or unsupported inputs that change the result.
3. **Expose a predictable API.** Document the exact signature, schema,
   errors, status and units. Preserve existing callers according to the
   [API evolution policy](../guidelines/api-evolution-standard.md). Return
   machine-readable results tied to the input revision. Make every advertised
   artifact traceable to that checked result.
4. **Teach and verify the journey.** Provide a runnable exact-release example,
   a failure or hold example with its next action, and a reference for all
   public fields. Run the example from an installed package and record the
   artifact identity and case outcome. Use the qualified-review requirement
   carried by the results.

Apply those rules across the published journeys first. Use the existing
two-way slab and staircase examples as failure and hold controls, and add
separate positive cases when the corresponding evidence supports them.
For new foundation or other element cases, start with one defined topology
and action set, then bind the governing source and independent reference
before adding it to the supported register.

## Library patterns worth reusing

| Reference | What to apply in StructLib |
| --- | --- |
| [PyPA installation guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) | Make the first run reproducible with an isolated environment and the exact package version. |
| [Applying Diátaxis](https://www.diataxis.fr/application/) | Keep the first-run tutorial, task guides, exact API reference and engineering explanation easy to find independently. |
| [SciPy result reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.OptimizeResult.html) | Document computed values, status, diagnostic messages and their method-specific meaning alongside each other. |
| [rcdesign section classes](https://rcdesign.readthedocs.io/en/latest/is456.html) | Compare a matching IS 456 section on the same material and load basis. Keep numerical reference values independent of the production calculation. |
| [PyNite documentation](https://pynite.readthedocs.io/en/stable/) | Use a matching model as a comparison for actions and reactions. Apply the governing IS 456 checks to separately verified member inputs. |
