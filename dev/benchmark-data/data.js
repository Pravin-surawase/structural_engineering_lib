window.BENCHMARK_DATA = {
  "lastUpdate": 1775672956399,
  "repoUrl": "https://github.com/Pravin-surawase/structural_engineering_lib",
  "entries": {
    "IS 456 Performance Benchmarks": [
      {
        "commit": {
          "author": {
            "name": "Pravin Surawase",
            "username": "Pravin-surawase",
            "email": "pravinsurawase@gmail.com"
          },
          "committer": {
            "name": "Pravin Surawase",
            "username": "Pravin-surawase",
            "email": "pravinsurawase@gmail.com"
          },
          "id": "fa854e0ff463ea5b50e3aae7c379b852d49b191a",
          "message": "docs(migration): add 10 innovation ideas with 3-agent review",
          "timestamp": "2026-04-08T06:58:44Z",
          "url": "https://github.com/Pravin-surawase/structural_engineering_lib/commit/fa854e0ff463ea5b50e3aae7c379b852d49b191a"
        },
        "date": 1775672954620,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_mu_lim",
            "value": 829820.9345094099,
            "unit": "iter/sec",
            "range": "stddev: 3.3404950876294155e-7",
            "extra": "mean: 1.2050792627823976 usec\nrounds: 92679"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_ast_required",
            "value": 509667.73936373147,
            "unit": "iter/sec",
            "range": "stddev: 5.785167804555246e-7",
            "extra": "mean: 1.9620625807087548 usec\nrounds: 72067"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_tv",
            "value": 1433654.5392889488,
            "unit": "iter/sec",
            "range": "stddev: 1.1518980515833915e-7",
            "extra": "mean: 697.5181067650867 nsec\nrounds: 196079"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_development_length",
            "value": 451633.56711558317,
            "unit": "iter/sec",
            "range": "stddev: 5.506919107580003e-7",
            "extra": "mean: 2.2141844026045954 usec\nrounds: 59305"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_ec",
            "value": 3778697.9489474487,
            "unit": "iter/sec",
            "range": "stddev: 3.550643870913151e-8",
            "extra": "mean: 264.6414223922155 nsec\nrounds: 173883"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_fcr",
            "value": 4189965.167576452,
            "unit": "iter/sec",
            "range": "stddev: 3.289224281485813e-8",
            "extra": "mean: 238.66546856722852 nsec\nrounds: 192679"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_singly_reinforced",
            "value": 179273.7326694149,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011999918910913776",
            "extra": "mean: 5.578062023419929 usec\nrounds: 33439"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_shear",
            "value": 143957.00794848017,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010406674574793068",
            "extra": "mean: 6.946518368580454 usec\nrounds: 27928"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_check_deflection_span_depth",
            "value": 281158.2194726443,
            "unit": "iter/sec",
            "range": "stddev: 7.056976592059165e-7",
            "extra": "mean: 3.556716221477197 usec\nrounds: 46642"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_beam_is456",
            "value": 48862.10884929661,
            "unit": "iter/sec",
            "range": "stddev: 0.000003018718521024076",
            "extra": "mean: 20.465756054128956 usec\nrounds: 7887"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_compute_detailing",
            "value": 43186.28299973022,
            "unit": "iter/sec",
            "range": "stddev: 0.000002396285809083077",
            "extra": "mean: 23.155500555726157 usec\nrounds: 10798"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_optimize_bar_arrangement",
            "value": 16026.760366302791,
            "unit": "iter/sec",
            "range": "stddev: 0.00000846222622106561",
            "extra": "mean: 62.3956418605072 usec\nrounds: 7310"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_batch_design_10_beams",
            "value": 342.29714281660205,
            "unit": "iter/sec",
            "range": "stddev: 0.0026903385500185745",
            "extra": "mean: 2.921438349649871 msec\nrounds: 143"
          }
        ]
      }
    ]
  }
}