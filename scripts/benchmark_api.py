#!/usr/bin/env python3
"""
API Performance Benchmark Script.

Supports two modes:
    --mode fastapi   Benchmark FastAPI endpoint latencies via TestClient
    --mode direct    Benchmark direct library API calls (no HTTP overhead)
    --mode all       Run both (default)

The FastAPI mode measures endpoint latencies and throughput for CI reporting.
The direct mode benchmarks structural_lib function latencies for V3 requirements.

Usage:
    python scripts/benchmark_api.py                     # Both modes
    python scripts/benchmark_api.py --mode fastapi      # FastAPI endpoints only
    python scripts/benchmark_api.py --mode direct       # Direct library calls only
    python scripts/benchmark_api.py --quick             # Quick smoke test
    python scripts/benchmark_api.py --output json       # JSON output for CI
    python scripts/benchmark_api.py --threshold 100     # Fail if p95 > 100ms

Exit Codes:
    0: All benchmarks passed
    1: Some benchmarks exceeded thresholds
    2: Error running benchmarks
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

# Add project root for imports
project_root = Path(__file__).parent.parent
PYTHON_DIR = project_root / "Python"
REPORT_PATH = project_root / "docs" / "reference" / "api-benchmark-report.json"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(PYTHON_DIR))


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""

    endpoint: str
    method: str
    iterations: int
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    std_dev_ms: float
    requests_per_sec: float
    errors: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "iterations": self.iterations,
            "min_ms": round(self.min_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "mean_ms": round(self.mean_ms, 2),
            "median_ms": round(self.median_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "p99_ms": round(self.p99_ms, 2),
            "std_dev_ms": round(self.std_dev_ms, 2),
            "requests_per_sec": round(self.requests_per_sec, 2),
            "errors": self.errors,
        }


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results."""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    results: list[BenchmarkResult] = field(default_factory=list)
    passed: bool = True
    threshold_ms: float | None = None
    failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "threshold_ms": self.threshold_ms,
            "passed": self.passed,
            "failures": self.failures,
            "summary": {
                "total_endpoints": len(self.results),
                "avg_p95_ms": round(
                    sum(r.p95_ms for r in self.results) / len(self.results), 2
                )
                if self.results
                else 0,
                "total_requests_per_sec": round(
                    sum(r.requests_per_sec for r in self.results), 2
                ),
            },
            "results": [r.to_dict() for r in self.results],
        }


def percentile(data: list[float], p: float) -> float:
    """Calculate percentile of sorted data."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_data) else f
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def benchmark_endpoint(
    client: TestClient,
    method: str,
    endpoint: str,
    iterations: int = 100,
    json_data: dict | None = None,
    warmup: int = 5,
) -> BenchmarkResult:
    """Benchmark a single endpoint."""
    latencies: list[float] = []
    errors = 0

    # Warmup runs
    for _ in range(warmup):
        if method == "GET":
            client.get(endpoint)
        elif method == "POST":
            client.post(endpoint, json=json_data or {})

    # Timed runs
    for _ in range(iterations):
        start = time.perf_counter()
        try:
            if method == "GET":
                resp = client.get(endpoint)
            elif method == "POST":
                resp = client.post(endpoint, json=json_data or {})
            else:
                raise ValueError(f"Unsupported method: {method}")

            if resp.status_code >= 400:
                errors += 1
        except Exception:
            errors += 1

        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

    # Calculate statistics
    return BenchmarkResult(
        endpoint=endpoint,
        method=method,
        iterations=iterations,
        min_ms=min(latencies),
        max_ms=max(latencies),
        mean_ms=statistics.mean(latencies),
        median_ms=statistics.median(latencies),
        p95_ms=percentile(latencies, 95),
        p99_ms=percentile(latencies, 99),
        std_dev_ms=statistics.stdev(latencies) if len(latencies) > 1 else 0,
        requests_per_sec=1000 / statistics.mean(latencies) if latencies else 0,
        errors=errors,
    )


def get_test_cases() -> list[dict[str, Any]]:
    """Get list of endpoints to benchmark."""
    # Standard beam design request
    beam_design_payload = {
        "width": 300,
        "depth": 450,
        "length": 5000,
        "Mu": 120,
        "Vu": 80,
        "fck": 25,
        "fy": 500,
    }

    # Beam check payload
    beam_check_payload = {
        "width": 300,
        "depth": 450,
        "provided_ast": 1200,
        "provided_stirrup_area": 100,
        "Mu": 120,
        "Vu": 80,
        "fck": 25,
        "fy": 500,
    }

    # Detailing payload
    detailing_payload = {
        "width": 300,
        "depth": 450,
        "ast_required": 800,
        "bar_diameter": 16,
        "fck": 25,
        "fy": 500,
    }

    # Optimization payload
    optimization_payload = {
        "width": 300,
        "depth": 450,
        "length": 5000,
        "Mu": 120,
        "fck": 25,
        "fy": 500,
        "concrete_cost": 5000,
        "steel_cost": 60000,
    }

    # Smart analysis payload
    smart_analysis_payload = {
        "width": 300,
        "depth": 450,
        "length": 5000,
        "Mu": 120,
        "Vu": 80,
        "fck": 25,
        "fy": 500,
    }

    # 3D geometry payload
    geometry_payload = {
        "width": 300,
        "depth": 450,
        "length": 5000,
    }

    return [
        # Health endpoints (fastest)
        {"method": "GET", "endpoint": "/health", "iterations": 500},
        {"method": "GET", "endpoint": "/health/ready", "iterations": 500},
        {"method": "GET", "endpoint": "/health/info", "iterations": 500},
        # Design endpoints
        {
            "method": "POST",
            "endpoint": "/api/v1/design/beam",
            "json_data": beam_design_payload,
            "iterations": 100,
        },
        {
            "method": "POST",
            "endpoint": "/api/v1/design/beam/check",
            "json_data": beam_check_payload,
            "iterations": 100,
        },
        {"method": "GET", "endpoint": "/api/v1/design/limits", "iterations": 200},
        # Detailing endpoints
        {
            "method": "POST",
            "endpoint": "/api/v1/detailing/beam",
            "json_data": detailing_payload,
            "iterations": 100,
        },
        {"method": "GET", "endpoint": "/api/v1/detailing/bar-areas", "iterations": 200},
        {
            "method": "GET",
            "endpoint": "/api/v1/detailing/development-length/16",
            "iterations": 200,
        },
        # Optimization endpoints
        {
            "method": "POST",
            "endpoint": "/api/v1/optimization/beam/cost",
            "json_data": optimization_payload,
            "iterations": 100,
        },
        {"method": "GET", "endpoint": "/api/v1/optimization/cost-rates", "iterations": 200},
        # Analysis endpoints
        {
            "method": "POST",
            "endpoint": "/api/v1/analysis/beam/smart",
            "json_data": smart_analysis_payload,
            "iterations": 100,
        },
        {"method": "GET", "endpoint": "/api/v1/analysis/code-clauses", "iterations": 200},
        # Geometry endpoints
        {
            "method": "POST",
            "endpoint": "/api/v1/geometry/beam/3d",
            "json_data": geometry_payload,
            "iterations": 100,
        },
        {"method": "GET", "endpoint": "/api/v1/geometry/materials", "iterations": 200},
    ]


def get_quick_test_cases() -> list[dict[str, Any]]:
    """Get minimal test cases for quick smoke test."""
    beam_design_payload = {
        "width": 300,
        "depth": 450,
        "length": 5000,
        "Mu": 120,
        "Vu": 80,
        "fck": 25,
        "fy": 500,
    }

    return [
        {"method": "GET", "endpoint": "/health", "iterations": 10},
        {
            "method": "POST",
            "endpoint": "/api/v1/design/beam",
            "json_data": beam_design_payload,
            "iterations": 10,
        },
    ]


def run_benchmarks(
    quick: bool = False,
    threshold_ms: float | None = None,
    verbose: bool = True,
) -> BenchmarkSuite:
    """Run all FastAPI benchmarks and return results."""
    # Lazy import — only needed for fastapi mode
    try:
        from fastapi.testclient import TestClient
        from fastapi_app.main import app
    except ImportError as e:
        print(f"Error importing FastAPI app: {e}", file=sys.stderr)
        sys.exit(2)

    client = TestClient(app)
    test_cases = get_quick_test_cases() if quick else get_test_cases()
    suite = BenchmarkSuite(threshold_ms=threshold_ms)

    if verbose:
        print(f"\n{'='*60}")
        print(f"API Performance Benchmark {'(quick mode)' if quick else ''}")
        print(f"{'='*60}\n")

    for case in test_cases:
        endpoint = case["endpoint"]
        method = case["method"]
        iterations = case.get("iterations", 100)
        json_data = case.get("json_data")

        if verbose:
            print(f"Benchmarking {method} {endpoint} ({iterations} iterations)...", end=" ")

        result = benchmark_endpoint(
            client=client,
            method=method,
            endpoint=endpoint,
            iterations=iterations,
            json_data=json_data,
        )
        suite.results.append(result)

        if verbose:
            print(f"p95={result.p95_ms:.1f}ms, mean={result.mean_ms:.1f}ms")

        # Check threshold
        if threshold_ms and result.p95_ms > threshold_ms:
            suite.passed = False
            suite.failures.append(
                f"{method} {endpoint}: p95={result.p95_ms:.1f}ms > {threshold_ms}ms"
            )

    return suite


def print_summary(suite: BenchmarkSuite) -> None:
    """Print human-readable summary for FastAPI benchmarks."""
    print(f"\n{'='*60}")
    print("FASTAPI BENCHMARK SUMMARY")
    print(f"{'='*60}")
    print(f"Timestamp: {suite.timestamp}")
    print(f"Endpoints tested: {len(suite.results)}")

    if suite.results:
        avg_p95 = sum(r.p95_ms for r in suite.results) / len(suite.results)
        total_rps = sum(r.requests_per_sec for r in suite.results)
        print(f"Average p95 latency: {avg_p95:.2f}ms")
        print(f"Total throughput: {total_rps:.2f} req/s")

    print(f"\n{'Endpoint':<45} {'p95 (ms)':<10} {'mean (ms)':<10} {'RPS':<10}")
    print("-" * 75)
    for r in suite.results:
        print(f"{r.method} {r.endpoint:<40} {r.p95_ms:<10.2f} {r.mean_ms:<10.2f} {r.requests_per_sec:<10.2f}")

    if suite.threshold_ms:
        print(f"\nThreshold: {suite.threshold_ms}ms")
        print(f"Status: {'PASSED' if suite.passed else 'FAILED'}")
        if suite.failures:
            print("\nFailures:")
            for f in suite.failures:
                print(f"  - {f}")


# ═══════════════════════════════════════════════════════════════════════════
# DIRECT LIBRARY BENCHMARKS (absorbed from benchmark_api_latency.py)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DirectBenchmarkConfig:
    """Configuration for a direct library benchmark test."""
    name: str
    function: str
    inputs: dict
    threshold_ms: float
    warmup_runs: int = 3
    iterations: int = 50


@dataclass
class DirectBenchmarkResult:
    """Result of a direct library benchmark."""
    name: str
    function: str
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    std_ms: float
    p95_ms: float
    p99_ms: float
    threshold_ms: float
    passed: bool
    iterations: int


# V3 Latency Requirements
V3_THRESHOLDS = {
    "design_beam_is456": 50.0,
    "check_shear_is456": 30.0,
    "detail_beam_is456": 80.0,
    "beam_to_3d_geometry": 100.0,
    "optimize_beam_cost": 200.0,
    "default": 100.0,
}

STANDARD_DIRECT_BENCHMARKS = [
    DirectBenchmarkConfig(
        name="Design beam - typical case",
        function="design_beam_is456",
        inputs={
            "units": "IS456",
            "case_id": "TEST-1",
            "mu_knm": 100.0,
            "vu_kn": 75.0,
            "b_mm": 300.0,
            "D_mm": 450.0,
            "d_mm": 420.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
        },
        threshold_ms=50.0,
    ),
    DirectBenchmarkConfig(
        name="Design beam - complex case",
        function="design_beam_is456",
        inputs={
            "units": "IS456",
            "case_id": "TEST-2",
            "mu_knm": 350.0,
            "vu_kn": 200.0,
            "b_mm": 400.0,
            "D_mm": 750.0,
            "d_mm": 700.0,
            "fck_nmm2": 35.0,
            "fy_nmm2": 500.0,
        },
        threshold_ms=75.0,
    ),
    DirectBenchmarkConfig(
        name="Design beam - minimum steel",
        function="design_beam_is456",
        inputs={
            "units": "IS456",
            "case_id": "TEST-3",
            "mu_knm": 25.0,
            "vu_kn": 20.0,
            "b_mm": 230.0,
            "D_mm": 400.0,
            "d_mm": 370.0,
            "fck_nmm2": 20.0,
            "fy_nmm2": 415.0,
        },
        threshold_ms=50.0,
    ),
]


def _load_direct_api():
    """Load structural_lib.api module for direct benchmarking."""
    try:
        from structural_lib import api
        return api
    except ImportError as e:
        print(f"❌ Cannot import structural_lib.api: {e}")
        sys.exit(2)


def _time_function(func: Callable, inputs: dict) -> float:
    """Time a single function call. Returns ms."""
    gc.disable()
    try:
        start = time.perf_counter()
        func(**inputs)
        end = time.perf_counter()
        return (end - start) * 1000.0
    finally:
        gc.enable()


def _run_direct_benchmark(api, config: DirectBenchmarkConfig) -> DirectBenchmarkResult:
    """Run a single direct library benchmark."""
    func = getattr(api, config.function, None)
    if func is None:
        return DirectBenchmarkResult(
            name=config.name, function=config.function,
            min_ms=float("inf"), max_ms=float("inf"),
            mean_ms=float("inf"), median_ms=float("inf"),
            std_ms=0.0, p95_ms=float("inf"), p99_ms=float("inf"),
            threshold_ms=config.threshold_ms, passed=False, iterations=0,
        )

    # Warmup
    for _ in range(config.warmup_runs):
        try:
            func(**config.inputs)
        except Exception:
            pass
    gc.collect()

    times = []
    for _ in range(config.iterations):
        try:
            t = _time_function(func, config.inputs)
            times.append(t)
        except Exception as e:
            print(f"⚠️  Error in {config.function}: {e}")

    if not times:
        return DirectBenchmarkResult(
            name=config.name, function=config.function,
            min_ms=float("inf"), max_ms=float("inf"),
            mean_ms=float("inf"), median_ms=float("inf"),
            std_ms=0.0, p95_ms=float("inf"), p99_ms=float("inf"),
            threshold_ms=config.threshold_ms, passed=False, iterations=0,
        )

    sorted_times = sorted(times)
    p95_idx = int(len(sorted_times) * 0.95)
    p99_idx = int(len(sorted_times) * 0.99)

    return DirectBenchmarkResult(
        name=config.name,
        function=config.function,
        min_ms=min(times),
        max_ms=max(times),
        mean_ms=statistics.mean(times),
        median_ms=statistics.median(times),
        std_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
        p95_ms=sorted_times[min(p95_idx, len(sorted_times) - 1)],
        p99_ms=sorted_times[min(p99_idx, len(sorted_times) - 1)],
        threshold_ms=config.threshold_ms,
        passed=statistics.median(times) <= config.threshold_ms,
        iterations=len(times),
    )


def run_direct_benchmarks(
    iterations: int = 50,
    threshold_override: float | None = None,
    function_filter: str | None = None,
    verbose: bool = True,
) -> tuple[list[DirectBenchmarkResult], bool]:
    """Run direct library benchmarks.

    Returns (results, all_passed).
    """
    api = _load_direct_api()
    benchmarks = [
        DirectBenchmarkConfig(
            name=b.name,
            function=b.function,
            inputs=b.inputs,
            threshold_ms=threshold_override if threshold_override else b.threshold_ms,
            warmup_runs=b.warmup_runs,
            iterations=iterations,
        )
        for b in STANDARD_DIRECT_BENCHMARKS
    ]

    if function_filter:
        benchmarks = [b for b in benchmarks if b.function == function_filter]

    if verbose:
        print(f"\n{'='*60}")
        print("Direct Library API Benchmarks (V3 Preparation)")
        print(f"{'='*60}")
        print(f"Running {len(benchmarks)} benchmarks, {iterations} iterations each...")

    results = []
    for bench in benchmarks:
        if verbose:
            print(f"\n⏱️  {bench.name}...")
        result = _run_direct_benchmark(api, bench)
        results.append(result)
        if verbose:
            status = "✅" if result.passed else "❌"
            print(f"   {status} median={result.median_ms:.3f}ms "
                  f"p95={result.p95_ms:.3f}ms (threshold={result.threshold_ms}ms)")

    all_passed = all(r.passed for r in results)
    return results, all_passed


def print_direct_summary(results: list[DirectBenchmarkResult]) -> None:
    """Print direct benchmark summary."""
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    print(f"\n{'='*60}")
    print("DIRECT LIBRARY BENCHMARK SUMMARY")
    print(f"{'='*60}")
    print(f"Total benchmarks: {len(results)}")
    print(f"Passed: {passed} ✅  Failed: {failed} ❌")
    print()
    print(f"{'Function':<30} {'Median (ms)':<15} {'Threshold':<12} {'Status'}")
    print("-" * 65)
    for r in results:
        status = "✅ PASS" if r.passed else "❌ FAIL"
        print(f"{r.function:<30} {r.median_ms:>10.2f}ms   {r.threshold_ms:>8.1f}ms   {status}")

    if failed == 0:
        print("\n✅ All functions meet V3 latency requirements!")
    else:
        print("\n⚠️  Some functions exceed latency thresholds.")


def _save_direct_report(results: list[DirectBenchmarkResult]) -> None:
    """Save direct benchmark report to JSON."""
    report = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "direct",
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
        },
        "results": [
            {
                "name": r.name,
                "function": r.function,
                "iterations": r.iterations,
                "threshold_ms": r.threshold_ms,
                "stats": {
                    "min_ms": round(r.min_ms, 3),
                    "mean_ms": round(r.mean_ms, 3),
                    "median_ms": round(r.median_ms, 3),
                    "p95_ms": round(r.p95_ms, 3),
                    "p99_ms": round(r.p99_ms, 3),
                    "max_ms": round(r.max_ms, 3),
                    "std_ms": round(r.std_ms, 3),
                },
                "passed": r.passed,
            }
            for r in results
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Report written to {REPORT_PATH}")


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Benchmark API performance (FastAPI endpoints and/or direct library calls)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/benchmark_api.py                     # Both modes\n"
            "  python scripts/benchmark_api.py --mode fastapi      # FastAPI only\n"
            "  python scripts/benchmark_api.py --mode direct       # Direct only\n"
            "  python scripts/benchmark_api.py --quick             # Quick test\n"
            "  python scripts/benchmark_api.py --mode direct -n 100\n"
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["fastapi", "direct", "all"],
        default="all",
        help="Benchmark mode (default: all)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick smoke test (fewer iterations)",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help="Fail if any p95 latency exceeds this value (ms)",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save JSON results to file",
    )
    # Direct-mode options
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=50,
        help="Number of iterations per benchmark (direct mode)",
    )
    parser.add_argument(
        "--function", "-f",
        type=str,
        help="Benchmark a specific function only (direct mode)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate JSON report (direct mode)",
    )

    args = parser.parse_args()
    overall_passed = True

    # ── FastAPI mode ───────────────────────────────────────────────────
    if args.mode in ("fastapi", "all"):
        suite = run_benchmarks(
            quick=args.quick,
            threshold_ms=args.threshold,
            verbose=(args.output == "text"),
        )
        if args.output == "json" and args.mode == "fastapi":
            print(json.dumps(suite.to_dict(), indent=2))
        elif args.output == "text":
            print_summary(suite)
        if not suite.passed:
            overall_passed = False

        if args.save and args.mode == "fastapi":
            output_path = Path(args.save)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(suite.to_dict(), f, indent=2)
            if args.output == "text":
                print(f"\nResults saved to: {output_path}")

    # ── Direct mode ────────────────────────────────────────────────────
    if args.mode in ("direct", "all"):
        direct_results, direct_passed = run_direct_benchmarks(
            iterations=args.iterations,
            threshold_override=args.threshold,
            function_filter=args.function,
            verbose=(args.output == "text"),
        )
        if args.output == "text":
            print_direct_summary(direct_results)
        if not direct_passed:
            overall_passed = False
        if args.report:
            _save_direct_report(direct_results)

    return 0 if overall_passed else 1


if __name__ == "__main__":
    sys.exit(main())
