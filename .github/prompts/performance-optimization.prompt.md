---
description: "Performance optimization workflow — profile, identify, optimize, benchmark"
---

# Performance Optimization Workflow

## 1. Identify the Bottleneck

```bash
# Run performance benchmarks
.venv/bin/pytest Python/tests/performance/ -v

# Profile a specific function
.venv/bin/python -c "
import cProfile
from structural_lib.services.api import {{function_name}}
cProfile.run('{{function_name}}({{args}})', sort='cumulative')
"

# Check API response time
.venv/bin/python scripts/benchmark_api.py
```

## 2. Measure Current Baseline

Before optimizing, record current performance:

```bash
# Python function timing
.venv/bin/python -c "
import time
from structural_lib.services.api import {{function_name}}

start = time.perf_counter()
for _ in range(100):
    {{function_name}}({{args}})
elapsed = (time.perf_counter() - start) / 100
print(f'Average: {elapsed*1000:.2f}ms per call')
"

# FastAPI endpoint timing
# Start server first: .venv/bin/uvicorn fastapi_app.main:app --host '::' --port 8000
curl -w '%{time_total}s\n' -s -o /dev/null -X POST http://localhost:8000/api/v1/design/beam \
  -H 'Content-Type: application/json' \
  -d '{{request_body}}'

# React bundle size
cd react_app && npm run build 2>&1 | tail -20
```

## 3. Common Optimization Targets

| Area | Common Issue | Fix |
|------|-------------|-----|
| Python | Repeated calculations in loop | Cache results or vectorize |
| Python | Large dict/list copies | Use views or generators |
| FastAPI | Slow response serialization | Simplify Pydantic models |
| FastAPI | Sequential API calls | Use `asyncio.gather()` |
| React | Unnecessary re-renders | `React.memo()`, `useMemo()`, `useCallback()` |
| React | Large bundle size | Code-split with `React.lazy()` |
| R3F | Too many draw calls | Instanced meshes, geometry merging |

## 4. Optimization Rules

- **Measure first** — never optimize without profiling
- **One change at a time** — measure impact of each change
- **Don't break correctness** — run full test suite after optimizing
- **IS 456 math is sacred** — never approximate structural calculations for speed
- **Document trade-offs** — comment why an optimization was chosen

## 5. Verify Optimization

```bash
# Run tests (correctness not broken)
.venv/bin/pytest Python/tests/ -v

# Re-run benchmark (improvement confirmed)
.venv/bin/pytest Python/tests/performance/ -v

# React build (if frontend changed)
cd react_app && npm run build
```

## 6. Commit

```bash
./scripts/ai_commit.sh "perf: optimize {{what}} — {{improvement}}"
```
