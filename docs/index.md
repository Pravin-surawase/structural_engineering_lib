# StructLib Documentation

Use the `structural-lib-is456` Python package and the React/FastAPI workbench for
case-qualified IS 456 reinforced-concrete workflows. The current public release
is `0.24.0` and requires Python 3.11 or newer.

## Install and verify

```bash
python3 -m pip install "structural-lib-is456===0.24.0"
python3 -m structural_lib install-preflight
```

The preflight confirms the interpreter, installed version, package origin, and
optional extras before you run a calculation.

## Choose your path

| Goal | Start here |
|---|---|
| See the visual workflow | [Product tour](getting-started/product-tour.md) |
| Run a first Python calculation | [Python quick start](getting-started/python-quickstart.md) |
| Follow a beginner copy/paste path | [Beginner's guide](getting-started/beginners-guide.md) |
| Use the command line | [CLI cookbook](cookbook/cli-reference.md) |
| Copy an element-family recipe | [13 family facades](cookbook/python/family-facades.md) |
| Look up a public function | [Python API reference](reference/api.md) |
| Integrate the platform | [Developer platform guide](developers/platform-guide.md) |
| Confirm supported cases and evidence | [IS 456 evidence crosswalk](verification/is456-library-first-evidence.md) |
| Check release status | [Current release](getting-started/release-status.md) |

## Use results responsibly

`PASS`, `FAIL`, and `HOLD` are calculation/review outcomes for the supplied
case. This software is a design aid, not complete IS 456 coverage or
professional approval. Review inputs, assumptions, limitations, and outputs
independently with a qualified structural engineer before engineering or
construction use.

## Build and contribute

- [Architecture overview](architecture/project-overview.md)
- [Development guide](contributing/development-guide.md)
- [Testing strategy](contributing/testing-strategy.md)
- [Agent bootstrap](getting-started/agent-bootstrap.md)
- [Git workflow](git-automation/git-workflow-single-source.md)
