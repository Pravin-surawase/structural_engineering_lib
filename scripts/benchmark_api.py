#!/usr/bin/env python3
"""
API Performance Benchmark Script.

Measures FastAPI endpoint latencies and throughput for CI reporting.
Outputs JSON metrics suitable for trend analysis and regression detection.

Usage:
    python scripts/benchmark_api.py                 # Run all benchmarks
    python scripts/benchmark_api.py --quick         # Quick smoke test
    python scripts/benchmark_api.py --output json   # JSON output for CI
    python scripts/benchmark_api.py --threshold 100 # Fail if p95 > 100ms

Exit Codes:
    0: All benchmarks passed
    1: Some benchmarks exceeded thresholds
    2: Error running benchmarks
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient


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
    """Run all benchmarks and return results."""
    # Import FastAPI app
    try:
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
    """Print human-readable summary."""
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
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


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Benchmark FastAPI endpoint performance"
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

    args = parser.parse_args()

    # Run benchmarks
    suite = run_benchmarks(
        quick=args.quick,
        threshold_ms=args.threshold,
        verbose=(args.output == "text"),
    )

    # Output results
    if args.output == "json":
        print(json.dumps(suite.to_dict(), indent=2))
    else:
        print_summary(suite)

    # Save if requested
    if args.save:
        output_path = Path(args.save)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(suite.to_dict(), f, indent=2)
        if args.output == "text":
            print(f"\nResults saved to: {output_path}")

    return 0 if suite.passed else 1


if __name__ == "__main__":
    sys.exit(main())
