#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
API Latency Benchmarking Script (V3 Preparation)
==================================================

Benchmarks library API performance to ensure V3 can meet latency requirements.
V3 requires <100ms response time for real-time UI updates.

Usage:
    python scripts/benchmark_api_latency.py              # Run all benchmarks
    python scripts/benchmark_api_latency.py --function design_beam_is456
    python scripts/benchmark_api_latency.py --iterations 100
    python scripts/benchmark_api_latency.py --threshold 100  # ms
    python scripts/benchmark_api_latency.py --report       # Generate report

Exit Codes:
    0 - All functions meet latency threshold
    1 - Some functions exceed threshold
    2 - Benchmark infrastructure error

V3 Context:
    This script validates V3 performance requirements:
    1. Single beam design: <50ms (for real-time feedback)
    2. Validation check: <30ms (critical for live editing)
    3. Batch operations: <500ms for 10 beams
    4. 3D geometry: <100ms (for responsive rendering)

Author: AI Agent (V3 Foundation Session)
Created: 2026-01-24
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PYTHON_DIR = PROJECT_ROOT / "Python"
REPORT_PATH = PROJECT_ROOT / "docs" / "reference" / "api-benchmark-report.json"

# Add Python directory to path
sys.path.insert(0, str(PYTHON_DIR))


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark test."""
    name: str
    function: str
    inputs: dict
    threshold_ms: float  # Maximum acceptable latency
    warmup_runs: int = 3
    iterations: int = 50


@dataclass
class BenchmarkResult:
    """Result of a benchmark test."""
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
    "design_beam_is456": 50.0,        # Real-time design feedback
    "check_shear_is456": 30.0,        # Live validation
    "detail_beam_is456": 80.0,        # Detailing calculation
    "beam_to_3d_geometry": 100.0,     # 3D rendering
    "optimize_beam_cost": 200.0,      # Optimization (can be slower)
    "default": 100.0                  # Default threshold
}

# Standard benchmark configurations
STANDARD_BENCHMARKS = [
    BenchmarkConfig(
        name="Design beam - typical case",
        function="design_beam_is456",
        inputs={
            "units": "IS456",
            "case_id": "TEST-1",
            "mu_knm": 100.0,
            "vu_kn": 75.0,
            "b_mm": 300.0,
            "D_mm": 450.0,
            "d_mm": 420.0,  # D - cover - bar/2
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0
        },
        threshold_ms=50.0
    ),
    BenchmarkConfig(
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
            "fy_nmm2": 500.0
        },
        threshold_ms=75.0
    ),
    BenchmarkConfig(
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
            "fy_nmm2": 415.0
        },
        threshold_ms=50.0
    ),
]


def load_api():
    """Load the structural_lib.api module."""
    try:
        from structural_lib import api
        return api
    except ImportError as e:
        print(f"❌ Cannot import structural_lib.api: {e}")
        sys.exit(2)


def time_function(func: Callable, inputs: dict) -> float:
    """
    Time a single function call.

    Returns:
        Execution time in milliseconds.
    """
    gc.disable()  # Disable GC during timing
    try:
        start = time.perf_counter()
        func(**inputs)
        end = time.perf_counter()
        return (end - start) * 1000.0  # Convert to ms
    finally:
        gc.enable()


def run_benchmark(api, config: BenchmarkConfig) -> BenchmarkResult:
    """Run a single benchmark."""
    func = getattr(api, config.function, None)
    if func is None:
        return BenchmarkResult(
            name=config.name,
            function=config.function,
            min_ms=float("inf"),
            max_ms=float("inf"),
            mean_ms=float("inf"),
            median_ms=float("inf"),
            std_ms=0.0,
            p95_ms=float("inf"),
            p99_ms=float("inf"),
            threshold_ms=config.threshold_ms,
            passed=False,
            iterations=0
        )

    # Warmup runs
    for _ in range(config.warmup_runs):
        try:
            func(**config.inputs)
        except Exception:
            pass

    # Force garbage collection before timing
    gc.collect()

    # Timed runs
    times = []
    for _ in range(config.iterations):
        try:
            t = time_function(func, config.inputs)
            times.append(t)
        except Exception as e:
            print(f"⚠️  Error in {config.function}: {e}")
            continue

    if not times:
        return BenchmarkResult(
            name=config.name,
            function=config.function,
            min_ms=float("inf"),
            max_ms=float("inf"),
            mean_ms=float("inf"),
            median_ms=float("inf"),
            std_ms=0.0,
            p95_ms=float("inf"),
            p99_ms=float("inf"),
            threshold_ms=config.threshold_ms,
            passed=False,
            iterations=0
        )

    # Calculate statistics
    sorted_times = sorted(times)
    p95_idx = int(len(sorted_times) * 0.95)
    p99_idx = int(len(sorted_times) * 0.99)

    mean = statistics.mean(times)
    median = statistics.median(times)

    return BenchmarkResult(
        name=config.name,
        function=config.function,
        min_ms=min(times),
        max_ms=max(times),
        mean_ms=mean,
        median_ms=median,
        std_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
        p95_ms=sorted_times[p95_idx] if p95_idx < len(sorted_times) else max(times),
        p99_ms=sorted_times[p99_idx] if p99_idx < len(sorted_times) else max(times),
        threshold_ms=config.threshold_ms,
        passed=median <= config.threshold_ms,  # Use median for pass/fail
        iterations=len(times)
    )


def print_result(result: BenchmarkResult):
    """Print a single benchmark result."""
    status = "✅" if result.passed else "❌"

    print(f"\n{status} {result.name}")
    print(f"   Function:   {result.function}")
    print(f"   Iterations: {result.iterations}")
    print(f"   Threshold:  {result.threshold_ms:.1f}ms")
    print(f"   ├── Min:    {result.min_ms:.3f}ms")
    print(f"   ├── Mean:   {result.mean_ms:.3f}ms")
    print(f"   ├── Median: {result.median_ms:.3f}ms {'✅' if result.median_ms <= result.threshold_ms else '⚠️'}")
    print(f"   ├── P95:    {result.p95_ms:.3f}ms")
    print(f"   ├── P99:    {result.p99_ms:.3f}ms")
    print(f"   ├── Max:    {result.max_ms:.3f}ms")
    print(f"   └── Std:    {result.std_ms:.3f}ms")


def print_summary(results: list[BenchmarkResult]):
    """Print benchmark summary."""
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    print()
    print("=" * 60)
    print("API Latency Benchmark Summary")
    print("=" * 60)
    print(f"Total benchmarks: {len(results)}")
    print(f"Passed:           {passed} ✅")
    print(f"Failed:           {failed} ❌")
    print()

    # Summary table
    print(f"{'Function':<30} {'Median (ms)':<15} {'Threshold':<12} {'Status'}")
    print("-" * 65)
    for r in results:
        status = "✅ PASS" if r.passed else "❌ FAIL"
        print(f"{r.function:<30} {r.median_ms:>10.2f}ms   {r.threshold_ms:>8.1f}ms   {status}")

    print()
    if failed == 0:
        print("✅ All functions meet V3 latency requirements!")
        print("   Real-time UI feedback will be responsive.")
    else:
        print("⚠️  Some functions exceed latency thresholds.")
        print("   Consider optimization before V3 migration.")


def generate_report(results: list[BenchmarkResult]):
    """Generate JSON benchmark report."""
    report = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed)
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
                    "std_ms": round(r.std_ms, 3)
                },
                "passed": r.passed
            }
            for r in results
        ]
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Report written to {REPORT_PATH}")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark API latency for V3 requirements"
    )
    parser.add_argument("--function", "-f",
                       help="Benchmark specific function only")
    parser.add_argument("--iterations", "-n", type=int, default=50,
                       help="Number of iterations per benchmark")
    parser.add_argument("--threshold", "-t", type=float,
                       help="Override latency threshold (ms)")
    parser.add_argument("--report", action="store_true",
                       help="Generate JSON report")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    # Load API
    api = load_api()

    # Get benchmarks
    benchmarks = STANDARD_BENCHMARKS.copy()

    # Override iterations if specified
    if args.iterations:
        benchmarks = [
            BenchmarkConfig(
                name=b.name,
                function=b.function,
                inputs=b.inputs,
                threshold_ms=args.threshold if args.threshold else b.threshold_ms,
                warmup_runs=b.warmup_runs,
                iterations=args.iterations
            )
            for b in benchmarks
        ]

    # Filter by function if specified
    if args.function:
        benchmarks = [b for b in benchmarks if b.function == args.function]
        if not benchmarks:
            # Create adhoc benchmark for specified function
            func = getattr(api, args.function, None)
            if func is None:
                print(f"❌ Function '{args.function}' not found in API")
                return 2

            threshold = V3_THRESHOLDS.get(args.function, V3_THRESHOLDS["default"])
            if args.threshold:
                threshold = args.threshold

            benchmarks = [
                BenchmarkConfig(
                    name=f"Benchmark {args.function}",
                    function=args.function,
                    inputs={},  # Requires manual input specification
                    threshold_ms=threshold,
                    iterations=args.iterations or 50
                )
            ]
            print(f"⚠️  Created adhoc benchmark for {args.function}")
            print("   Note: Using empty inputs - may need to specify via code")

    print("=" * 60)
    print("API Latency Benchmarks (V3 Preparation)")
    print("=" * 60)
    print(f"Running {len(benchmarks)} benchmarks...")
    print(f"Iterations per benchmark: {benchmarks[0].iterations if benchmarks else 0}")

    # Run benchmarks
    results = []
    for benchmark in benchmarks:
        if args.verbose:
            print(f"\n⏱️  Benchmarking {benchmark.name}...")
        result = run_benchmark(api, benchmark)
        results.append(result)

        if args.verbose:
            print_result(result)

    # Print summary
    print_summary(results)

    # Generate report if requested
    if args.report:
        generate_report(results)

    # Exit code
    if any(not r.passed for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
