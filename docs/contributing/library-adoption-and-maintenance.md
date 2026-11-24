# StructLib library adoption and maintenance guide

**Type:** Guide
**Audience:** Developers
**Status:** Active
**Importance:** High
**Created:** 2026-11-18
**Last Updated:** 2026-11-24
**Abstract:** Patterns from actively maintained Python libraries and a reusable check for StructLib changes affecting users, AI assistants and maintainers.

---

Use this guide when a change affects how people install, learn, call, upgrade,
or maintain StructLib. Choose the checks relevant to the change and put the
result in the existing PR description. The
[development guide](development-guide.md) and
[Git workflow](../git-automation/git-workflow-single-source.md) own the
repository procedures.

## References checked on 18 November 2026

FastAPI is the closest combined reference for people and AI assistants.
Requests gives a compact first-run model, Pydantic makes error recovery
explicit, and scikit-learn provides a contributor model. PyNite is a
smaller structural-engineering peer with a focused first example.
Versions below were checked on PyPI. Upload dates use India Standard Time.
GitHub stars are rounded snapshots of project visibility. The practices
below come from the public documentation. All five repositories showed
activity in November before this check.

| Reference | Published version and visibility | Practice to apply in StructLib |
| --- | --- | --- |
| FastAPI | [0.164.0, 18 November](https://pypi.org/project/fastapi/0.164.0/), [about 105k stars](https://github.com/fastapi/fastapi) | A minimal first program beside generated OpenAPI documentation and AI guidance selected for the installed version. Keep StructLib's human example and machine-readable contract bound to the same release. [First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/) · [Develop with AI](https://fastapi.tiangolo.com/ai-development/) |
| Requests | [2.34.2, 15 May](https://pypi.org/project/requests/2.34.2/), [about 55k stars](https://github.com/psf/requests) | Show the first usable response immediately, then teach success, failure and recovery. Make compatibility and versioning expectations easy to find. [Quickstart](https://requests.readthedocs.io/en/stable/user/quickstart/) · [Release policy](https://requests.readthedocs.io/en/latest/community/release-process/) |
| Pydantic | [2.14.3, 5 November](https://pypi.org/project/pydantic/2.14.3/), [about 30k stars](https://github.com/pydantic/pydantic) | Give the person an understandable error and give software a structured code, path and context it can act on. Keep the documented fields consistent with the actual validation result. [Error handling](https://pydantic.dev/docs/validation/latest/errors/errors/) |
| scikit-learn | [1.9.1, 11 September](https://pypi.org/project/scikit-learn/1.9.1/), [about 68k stars](https://github.com/scikit-learn/scikit-learn) | Ask for one reproducible case, environment information and an expected result. Give a first-time contributor a clear path to fix and verify a small change. [Getting started](https://scikit-learn.org/stable/getting_started.html) · [Contributing](https://scikit-learn.org/stable/developers/contributing.html) |
| PyNite | [3.2.1, 29 October](https://pypi.org/project/PyNiteFEA/3.2.1/), [about 790 stars](https://github.com/JWock82/Pynite) | Lead with one recognizable structural task and explicit units. Keep more examples available from that starting point. [Quickstart](https://pynite.readthedocs.io/en/stable/quickstart.html) |

## Make the first use work from one page

Start with a user task, such as checking a beam or sizing a supported footing
from supplied inputs. Confirm the public version on the
[current release page](../getting-started/release-status.md), then run the
beam example in the [Python quick start](../getting-started/python-quickstart.md)
or the footing example in the
[element workflow guide](../getting-started/element-workflow-guide.md).
Signpost optional drawing, report and application paths when they become
relevant. The [family cookbook](../cookbook/python/family-facades.md) covers
further element cases.

For each new or changed example, give the reader the tested version or source
revision, required extras, complete input and expected outcome. Mark
checkout-only examples where a published install cannot run them. Verify a
changed first-use example in a clean environment outside the source checkout.
Check the imported package version and origin before interpreting the result.

## Give AI the same contract as a person

Use the [API chooser](../reference/api-levels.md) to find the documented
entry point for the task. Give the assistant the installed version, the
matching recipe, the [generated family contracts](../reference/family-facade-contracts.md)
and the supplied data. The contract should tell both audiences the required
fields, units, limits, statuses and next actions. A successful call can
return an engineering `FAIL` or `HOLD`. Invalid intake has its own
structured diagnostics.

The [beam tool manifest](../reference/beam-tool-manifest.md) describes one
approved beam design capability and its execution conditions. The broader
Python recipe catalogue has its own scope. Any new AI-facing reference should
link to existing contracts for the installed version, including their use
limits. Generate machine-readable descriptions from those contracts when
adding a supported integration.

For a recurring or AI-assisted workflow, give the caller the actual geometry,
units, sign convention, actions and source revision. Ask the data owner to
resolve missing inputs. Define how each status is represented in the user's
report or review queue. Check that the report refers to the same input
revision and result.

## Keep upgrades and maintenance easy to follow

- **Upgrade instructions.** Follow the
  [API evolution standard](../guidelines/api-evolution-standard.md) and
  [current compatibility policy](../reference/api-stability.md). For changes
  that affect existing code or files, record the affected entry point, the
  old and new behavior, and the smallest conversion example. The strict CSV
  span migration is an example of telling users which input to add and what
  happens when it is missing. The 0.31.1 slab correction identifies which
  earlier results need to be rerun and which reports to refresh.
  [CSV migration](../getting-started/release-status.md#upgrade-existing-generic-csv-files) ·
  [Slab rerun guidance](../getting-started/release-status.md#rerun-affected-continuous-slab-checks)
- **First contribution.** A human contributor should be able to find the
  owning module, reproduce a small issue and run one focused check from
  [CONTRIBUTING](../../CONTRIBUTING.md). Link the
  [agent bootstrap](../getting-started/agent-bootstrap.md) from that path for
  contributors using an assistant. For code written with AI, the author
  verifies the behavior and explains the change before handing it off.
- **Reproducible support.** Ask the reporter for a minimal input or fixture,
  exact package version and `install-preflight` output, the command or
  entry point, and observed and expected behavior. Include the issue code,
  field path, or status when one is returned.
- **Release handoff.** Run the existing version, generated-reference and
  focused checks when their inputs are ready. Resolve known version and
  documentation drift before exact artifact qualification. After the
  public-readback check, make the public install instructions and release
  status agree with the published version. Use the
  [release checklist](../planning/pre-release-checklist.md) for release work.

## Select evidence for the next change

| If the work changes… | Proof to capture in its PR |
| --- | --- |
| First-use instructions or an example | The exact installed version and package origin, the command a new user can copy, and the expected result they actually see. Record where an unfamiliar reader needed another page or help. |
| A public workflow or input contract | A passing recipe and the relevant rejection, failure or hold control. Link the generated contract or test that establishes each result. Explain migration where existing callers are affected. |
| AI or recurring automation | The exact-version recipe or schema the caller used and the observed result for valid input and one missing or unsupported input. Check the issue or status that reaches the user's review queue. |
| Contribution or release procedure | A new contributor can follow the documented setup and verify one change. For release-process work, compare equivalent runs and record verification time, handoff time and retries separately. |

Use the rows that match the changed behavior. Link existing evidence when it
already answers the question. For a PR handoff, state the **user task**, the
**public entry point or guide**, the **expected behavior**, any **upgrade
impact**, and the **check that verified it**.

## Where to apply this first

1. **Keep the public first run aligned with the current release.** After a
   release or a change to the first-use path, repeat the public install,
   preflight and first example from the maintained entry pages. Record the
   installed version and example outcome in the PR.
2. **Pilot one documentation path for AI and automation.** Use the supported
   beam recipe and generated contract for one pinned release. Record whether
   an assistant can find the correct entry point and report the missing-input
   or hold case without inventing an engineering value.
3. **Simplify the first contribution.** Try a small documentation or Python
   fix from a clean checkout using only the contributor guide. Keep the
   focused setup and check that worked visible at the top.
4. **Measure release work separately.** Use the
   [0.31.0 release timing baseline](../planning/structlib-0311-patch-plan.md#release-timing-baseline-and-targets)
   when choosing changes to the release workflow. Record verification,
   approval wait, dispatch and publication execution separately.
