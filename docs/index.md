# Structural Engineering Library Documentation

Design and verification guidance for the IS 456 Python library, FastAPI
service, React application, and repository workflows.

## Start here

- [Python quick start](getting-started/python-quickstart.md)
- [Agent bootstrap](getting-started/agent-bootstrap.md)
- [Public Python API](reference/api.md)
- [IS 456 formulas](reference/is456-formulas.md)

## Build and contribute

- [Architecture overview](architecture/project-overview.md)
- [Development guide](contributing/development-guide.md)
- [Testing strategy](contributing/testing-strategy.md)
- [Git workflow](git-automation/git-workflow-single-source.md)

## Find current repository context

The authored [documentation directory](README.md) owns human navigation.
Repository agents should use the canonical operation registry and live context
summaries instead of generated folder inventories:

```bash
./run.sh control find "task description"
./run.sh context list
./run.sh context show docs
./run.sh context summary docs/reference
```

These commands read current worktree files and do not require an index refresh.
