# Day 29: Performance & Scale

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-09
**Last Updated:** 2026-04-09
**Prerequisites:** Day 8 (architecture layers), Day 20 (data flow E2E), Day 25 (code quality tools)
**Library files:** `Python/structural_lib/services/batch.py`, `Python/structural_lib/services/beam_api.py`, `Python/structural_lib/codes/is456/shear.py` (Table 19 lookups), `fastapi_app/routers/streaming.py`
**Related docs:** `docs/architecture/project-overview.md`

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why performance matters when you move from 1 beam to 1000 beams
- How to profile Python code with cProfile and line_profiler
- How the library's batch module optimises multi-beam design
- Caching strategies for repeated IS 456 table lookups
- Memory trade-offs between dataclasses and dicts
- Async vs sync in the FastAPI layer
- How to set up benchmarks that catch regressions automatically

---

## 📖 Theory

### 1. The Scale Problem

Designing a single beam takes about **2 ms** on a modern laptop. A 30-storey building might have **800–1200 beams**. An ETABS CSV can easily contain 1000+ rows:

```
1 beam  →  ~2 ms   (instant — you won't notice)
100 beams → ~200 ms (still fast — under a blink)
1000 beams → ~2 s   (noticeable — user stares at spinner)
5000 beams → ~10 s  (painful — user thinks app crashed)
```

Add detailing, BBS generation, DXF export, and 3D geometry per beam and you're multiplying by 4–5×.

### 2. Where Time Goes — Profiling

Before optimising anything, you **must measure**. Guessing where code is slow is wrong more often than right.

#### cProfile — The Built-in Profiler

Python ships with `cProfile`. It instruments every function call and records cumulative time.

```python
import cProfile

cProfile.run("""
from structural_lib import design_beam_is456
result = design_beam_is456(
    b_mm=300, d_mm=450, fck=25, fy=500,
    Mu_knm=120, Vu_kn=80, clear_cover_mm=25
)
""", sort="cumulative")
```

The output shows you which functions consume the most time. Typical hotspots in this library:
- `tau_c_is456()` — Table 19 interpolation (called once per beam)
- `flexure_design()` — iterative neutral axis calculation
- `_compute_stirrup_spacing()` — shear reinforcement loop
- `check_compliance_report()` — runs 15+ clause checks sequentially

#### line_profiler — Line-by-Line

For deeper investigation, `line_profiler` shows time per line inside a single function:

```bash
pip install line_profiler
kernprof -l -v profile_flexure.py
```

Decorate the target function with `@profile` and run via `kernprof`. The output shows microseconds per line — you'll immediately see whether the bottleneck is a math operation, a validation check, or a function call to another module.

### 3. Batch Design — From Naive to Optimised

The library provides `Python/structural_lib/services/batch.py` for multi-beam processing. Let's trace the evolution from slow to fast.

#### Level 1: Naive For-Loop (Slow)

```python
from structural_lib import design_beam_is456

results = []
for beam in beam_list:  # 1000 beams
    result = design_beam_is456(
        b_mm=beam["b_mm"], d_mm=beam["d_mm"],
        fck=beam["fck"], fy=beam["fy"],
        Mu_knm=beam["Mu_knm"], Vu_kn=beam["Vu_kn"],
        clear_cover_mm=beam["clear_cover_mm"],
    )
    results.append(result)
# ~2000 ms for 1000 beams
```

Problems:
- Each call re-validates material properties (same M25/Fe500 for all beams)
- No parallelism — one CPU core sitting at 100%, seven cores idle
- Python's GIL doesn't matter for CPU-bound work IF you use processes (not threads)

#### Level 2: Reuse Material Properties (Better)

Many beams share the same M25/Fe500. Compute design values once:

```python
from structural_lib.codes.is456.materials import (
    design_compressive_strength, design_tensile_strength,
)

fcd = design_compressive_strength(fck=25)  # 0.446 × 25 = 11.15 N/mm²
fsd = design_tensile_strength(fy=500)       # 500 / 1.15 = 434.78 N/mm²
# Saves ~0.1 ms per beam × 1000 = 100 ms
```

The library's `_design_single_beam()` in `batch.py` does this internally via `_coerce_params()` and `_pick_first()`.

#### Level 3: Parallel with ProcessPoolExecutor (Best)

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def design_one(beam_params):
    """Design a single beam — must be top-level for pickling."""
    from structural_lib import design_beam_is456
    return design_beam_is456(**beam_params)

with ProcessPoolExecutor(max_workers=4) as pool:
    futures = {pool.submit(design_one, b): i for i, b in enumerate(beam_list)}
    results = [None] * len(beam_list)
    for future in as_completed(futures):
        idx = futures[future]
        results[idx] = future.result()
# ~600 ms for 1000 beams on 4 cores (3.3× speedup)
```

> **Why ProcessPoolExecutor and not ThreadPoolExecutor?** Python's GIL (Global Interpreter Lock) means threads can't run Python bytecode in parallel. For CPU-bound math (our IS 456 calculations), threads give zero speedup. Processes each get their own Python interpreter and GIL, so they truly run in parallel.

### 4. Caching — Don't Compute the Same Thing Twice

#### Table 19 Lookups

IS 456 Table 19 gives permissible shear stress $\tau_c$ for different concrete grades and reinforcement percentages. For 1000 beams with similar ratios, many lookups hit the same interpolation range. Cache them:

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def tau_c_cached(fck: int, pt_percent_rounded: float) -> float:
    """Cache Table 19 lookups by rounding pt to 2 decimal places."""
    from structural_lib.codes.is456.beam.shear import tau_c_is456
    return tau_c_is456(fck=fck, pt_percent=pt_percent_rounded)

# Round to 2 decimals before lookup — trades tiny precision for big speed
pt_rounded = round(pt_percent, 2)
tc = tau_c_cached(25, pt_rounded)
```

#### When NOT to Cache

- **Design results** — each beam has unique dimensions; caching wastes memory
- **Mutable inputs** — `lru_cache` requires hashable arguments (no dicts or lists)
- **Stale data** — if you cache across different `fck` values accidentally, you silently produce wrong results. Always include ALL inputs that affect the output as cache keys

### 5. Memory — Dataclasses vs Dicts

The library returns `@dataclass` results (like `BeamDesignResult`) rather than plain dicts. Why?

| Aspect | `dict` | `@dataclass` |
|--------|--------|--------------|
| Memory | ~200–400 bytes per instance | ~100–200 bytes (with `__slots__`) |
| Access speed | Hash lookup (`O(1)` but slow constant) | Attribute lookup (faster) |
| Type safety | None — typos silently create new keys | AttributeError on typos |
| Autocomplete | No | Yes (IDE knows the fields) |
| Serialisation | Already a dict | `.to_dict()` method |

For 1000 beams, each with a result containing ~30 fields:
- Dict approach: ~400 KB
- Dataclass approach: ~200 KB

This difference matters more when you're holding results in memory for the React frontend to fetch via the API.

#### Generators for Large CSV Files

When importing a 10,000-row ETABS CSV, don't load everything into a list — use a generator:

```python
def stream_rows(path):
    with open(path) as f:
        for row in csv.DictReader(f):
            yield row

for row in stream_rows("huge_file.csv"):
    result = design_beam_is456(**adapt_row(row))
    write_result(result)  # Write immediately, don't accumulate
```

### 6. API Performance — Async vs Sync

FastAPI is async, but IS 456 math is CPU-bound. For a single user, calling `design_beam_is456()` directly in an async handler is fine. For concurrent users, solutions include:

1. **`run_in_executor`** — offload CPU work to a thread/process pool
2. **Streaming responses** — for batch designs, stream results via `StreamingResponse` or WebSocket
3. **Background tasks** — queue batch jobs, return a job ID, poll for status

The library's WebSocket endpoint (`/ws/design/{session}`) uses approach #3 for live design updates.

### 7. Benchmarking — Catching Regressions

A performance optimisation is worthless if someone accidentally regresses it next week. Use `pytest-benchmark`:

```bash
pip install pytest-benchmark
```

```python
# Python/tests/test_performance.py
from structural_lib import design_beam_is456

def test_single_design_performance(benchmark):
    """Single beam design should complete in under 5 ms."""
    result = benchmark(
        design_beam_is456,
        b_mm=300, d_mm=450, fck=25, fy=500,
        Mu_knm=120, Vu_kn=80, clear_cover_mm=25,
    )
    assert result["status"] == "OK"
```

Run with `--benchmark-only`. Save baselines with `--benchmark-save=baseline` and compare later with `--benchmark-compare`.

---

## 🏗️ Library Examples

### Example 1: Profile the Full Design Pipeline

```python
import cProfile
import pstats
from structural_lib import design_and_detail_beam_is456

profiler = cProfile.Profile()
profiler.enable()

result = design_and_detail_beam_is456(
    b_mm=300, d_mm=500, fck=25, fy=500,
    Mu_knm=150, Vu_kn=100, clear_cover_mm=30, span_mm=6000,
)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(15)  # Top 15 functions by cumulative time
```

### Example 2: Batch Design with the Library Module

```python
from structural_lib.services.batch import _design_single_beam

# The batch module's internal function handles param coercion
beams = [
    {"b_mm": 300, "d_mm": 450, "fck": 25, "fy": 500, "Mu_knm": 100, "Vu_kn": 60},
    {"width_mm": 350, "depth_mm": 500, "fck": 30, "fy": 500, "moment": 180, "shear": 90},
]

for i, beam in enumerate(beams):
    result = _design_single_beam(beam, idx=i, units="SI")
    print(f"Beam {i}: status={result.get('status')}")
```

Notice how `_pick_first()` handles different column name conventions (`b_mm` vs `width_mm`). This is the adapter pattern from Day 20.

### Example 3: Timing Comparison

```python
import time

from structural_lib import design_beam_is456

beam_params = dict(b_mm=300, d_mm=450, fck=25, fy=500,
                   Mu_knm=120, Vu_kn=80, clear_cover_mm=25)

# Sequential
start = time.perf_counter()
for _ in range(100):
    design_beam_is456(**beam_params)
seq_time = time.perf_counter() - start

print(f"Sequential (100 beams): {seq_time*1000:.1f} ms")
print(f"Per beam: {seq_time*10:.2f} ms")
```

> **Always use `time.perf_counter()`** — never `time.time()`. The latter has ~15 ms resolution on Windows and drifts with NTP clock adjustments. `perf_counter()` is monotonic and high-resolution on all platforms.

---

## 🎯 Simple Examples

### Example A: "Why is my loop slow?"

The fix is usually pre-converting data outside the loop:

```python
# Slow — string→float conversion happens 500 times inside the hot loop
results = []
for row in csv_data:
    r = design_beam_is456(
        b_mm=float(row["Width"]), d_mm=float(row["Depth"]),
        fck=25, fy=500, Mu_knm=float(row["Moment"]),
        Vu_kn=float(row["Shear"]), clear_cover_mm=25,
    )
    results.append(r)

# Fast — pre-convert, then loop does only math
params_list = [
    {"b_mm": float(r["Width"]), "d_mm": float(r["Depth"]),
     "fck": 25, "fy": 500, "Mu_knm": float(r["Moment"]),
     "Vu_kn": float(r["Shear"]), "clear_cover_mm": 25}
    for r in csv_data
]
results = [design_beam_is456(**p) for p in params_list]
```

### Example B: Quick Cache for Repeated Lookups

```python
from functools import lru_cache
from structural_lib.codes.is456.beam.shear import tau_c_is456

@lru_cache(maxsize=128)
def cached_tau_c(fck: int, pt_rounded: float) -> float:
    return tau_c_is456(fck=fck, pt_percent=pt_rounded)

# In your loop:
for beam in beams:
    pt = round(beam["pt_percent"], 2)  # Round for cache hits
    tc = cached_tau_c(beam["fck"], pt)
```

---

## 🔧 Exercise

### Task: Benchmark Single vs Batch Design

1. Create a list of 500 beam parameter dicts (vary `Mu_knm` from 50 to 300).
2. Time the sequential for-loop with `time.perf_counter()`.
3. Time the `ProcessPoolExecutor` approach with 4 workers.
4. Compare the speedup ratio.

```python
import matplotlib.pyplot as plt

labels = ["Sequential", "Parallel (4 workers)"]
times = [seq_ms, parallel_ms]
plt.bar(labels, times)
plt.ylabel("Time (ms)")
plt.title("500 Beam Designs: Sequential vs Parallel")
plt.show()
```

**Expected results:**
- Sequential: ~1000 ms
- Parallel (4 workers): ~350 ms
- Speedup: ~2.8× (not 4× due to process startup overhead and pickling cost)

**Bonus:** Try 2000 beams — the speedup ratio improves because process creation overhead is amortised.

---

## 💬 Can You Explain?

After completing this module, you should be able to answer:

1. Why is `ProcessPoolExecutor` better than `ThreadPoolExecutor` for IS 456 math?
2. What does Python's GIL prevent, and why doesn't it affect multi-process code?
3. When does caching help, and when does it waste memory?
4. Why do we use `time.perf_counter()` instead of `time.time()` for benchmarks?
5. What's the difference between streaming a batch response and returning it all at once?
6. How would you detect a performance regression between releases?
7. Why does the library use dataclasses instead of dicts for results?

---

## 📎 References

- **Library batch module:** `Python/structural_lib/services/batch.py`
- **Streaming router:** `fastapi_app/routers/streaming.py`
- **Python docs — cProfile:** https://docs.python.org/3/library/profile.html
- **Python docs — concurrent.futures:** https://docs.python.org/3/library/concurrent.futures.html
- **pytest-benchmark:** https://pytest-benchmark.readthedocs.io/
- **IS 456 Table 19:** Permissible shear stress $\tau_c$ (interpolated in `shear.py`)
- **Day 8:** Architecture layers — why separation enables independent optimisation
- **Day 20:** Data flow E2E — the full pipeline from CSV to 3D model
