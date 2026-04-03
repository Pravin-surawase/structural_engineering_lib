window.BENCHMARK_DATA = {
  "lastUpdate": 1775240116789,
  "repoUrl": "https://github.com/Pravin-surawase/structural_engineering_lib",
  "entries": {
    "IS 456 Performance Benchmarks": [
      {
        "commit": {
          "author": {
            "name": "Pravin Surawase",
            "username": "Pravin-surawase",
            "email": "125234565+Pravin-surawase@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "8019ec46a12d97c9f22d5cbdd8cd537ebbd0dede",
          "message": "TASK-671: Fix 4 known limitations — effective depth, serviceability, multi-layer rebar, failure story (TASK-671) (#501)\n\n* feat: fix 4 known limitations (TASK-671)\n\n* fix: use Field(default=) for mypy compatibility with SectionProperties",
          "timestamp": "2026-04-03T15:54:01Z",
          "url": "https://github.com/Pravin-surawase/structural_engineering_lib/commit/8019ec46a12d97c9f22d5cbdd8cd537ebbd0dede"
        },
        "date": 1775240115049,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_mu_lim",
            "value": 918545.4081916832,
            "unit": "iter/sec",
            "range": "stddev: 3.0992309276946623e-7",
            "extra": "mean: 1.0886778063249745 usec\nrounds: 103115"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_ast_required",
            "value": 520704.88428085065,
            "unit": "iter/sec",
            "range": "stddev: 5.757055865669603e-7",
            "extra": "mean: 1.9204736313950797 usec\nrounds: 82693"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_tv",
            "value": 1419102.2705031573,
            "unit": "iter/sec",
            "range": "stddev: 1.5777873367265542e-7",
            "extra": "mean: 704.6708477504161 nsec\nrounds: 178891"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_development_length",
            "value": 448004.38766622805,
            "unit": "iter/sec",
            "range": "stddev: 4.911350764174653e-7",
            "extra": "mean: 2.232120995977877 usec\nrounds: 57068"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_ec",
            "value": 3782306.751811154,
            "unit": "iter/sec",
            "range": "stddev: 3.637035802804555e-8",
            "extra": "mean: 264.38892073498556 nsec\nrounds: 174795"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_fcr",
            "value": 4252711.452446286,
            "unit": "iter/sec",
            "range": "stddev: 3.222113696065456e-8",
            "extra": "mean: 235.1440983433688 nsec\nrounds: 193837"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_singly_reinforced",
            "value": 207812.55615425744,
            "unit": "iter/sec",
            "range": "stddev: 8.168265283999031e-7",
            "extra": "mean: 4.81202877490092 usec\nrounds: 34961"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_shear",
            "value": 191144.87505270957,
            "unit": "iter/sec",
            "range": "stddev: 8.462966256332351e-7",
            "extra": "mean: 5.231633857430093 usec\nrounds: 27604"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_check_deflection_span_depth",
            "value": 307552.6283765797,
            "unit": "iter/sec",
            "range": "stddev: 6.96886496558833e-7",
            "extra": "mean: 3.251476032828957 usec\nrounds: 47419"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_beam_is456",
            "value": 61468.08088634021,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019161117133195646",
            "extra": "mean: 16.26860617056007 usec\nrounds: 8816"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_optimize_bar_arrangement",
            "value": 15951.849103088518,
            "unit": "iter/sec",
            "range": "stddev: 0.000004136221117988563",
            "extra": "mean: 62.688657191872814 usec\nrounds: 7001"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_batch_design_10_beams",
            "value": 388.85599146632615,
            "unit": "iter/sec",
            "range": "stddev: 0.0035772679508756303",
            "extra": "mean: 2.571646115645867 msec\nrounds: 147"
          }
        ]
      }
    ]
  }
}