---
owner: Main Agent
status: active
last_updated: 2026-08-10
doc_type: reference
complexity: advanced
tags: [catalogue, tools, ai-readiness]
---

# Beam Tool Manifest

The generated [beam tool manifest](beam-tool-manifest.json) describes the one
approved `is456.beam.design` capability. It is a deterministic projection of the
versioned workflow catalogue; it does not maintain a second parameter, unit, or
limitation list.

Regenerate and byte-check the artifact in one command:

```bash
./scripts/python_runtime.sh scripts/generate_beam_tool_manifest.py --write --check
```

The descriptor is readiness evidence only. It does not activate a model, chat
interface, autonomous execution, plugin system, filesystem access, or external
integration. Execution remains default-disabled, user acknowledgement is
required, and any output remains software evidence requiring qualified
engineering review.

The JSON Schema property names, units, defaults, bounds, choices, schema IDs,
limitations, and adapter ID are all generated from the catalogue. The committed
artifact is checked for exact drift by pre-commit and repository validation.
