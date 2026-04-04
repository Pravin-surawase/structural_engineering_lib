window.BENCHMARK_DATA = {
  "lastUpdate": 1775326286073,
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
          "id": "eedc444a66ecb3985e4b1c1dd230c2f8d0867378",
          "message": "TASK-AUDIT-P2B1: P2 Batch 1: S-15 error sanitize, S-18 float-inf JSON, SM-6 ShearResult frozen, SM-8 bearing tolerance, SM-10 ColumnAxialResult frozen, API-8 BarAreasResponse, API-10 DXF MIME (#515)\n\n* fix(audit): P2 Batch 1 — error sanitize, frozen dataclasses, float tolerance, API typing, DXF MIME\n\n* fix: move _sanitize_float below imports to resolve E402 lint",
          "timestamp": "2026-04-04T17:42:04Z",
          "url": "https://github.com/Pravin-surawase/structural_engineering_lib/commit/eedc444a66ecb3985e4b1c1dd230c2f8d0867378"
        },
        "date": 1775326284778,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_mu_lim",
            "value": 899905.7438860631,
            "unit": "iter/sec",
            "range": "stddev: 3.349452374771001e-7",
            "extra": "mean: 1.111227488872001 usec\nrounds: 71731"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_ast_required",
            "value": 513322.21974458155,
            "unit": "iter/sec",
            "range": "stddev: 4.967756293167379e-7",
            "extra": "mean: 1.9480941239940466 usec\nrounds: 72617"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_tv",
            "value": 1492785.38386755,
            "unit": "iter/sec",
            "range": "stddev: 1.0368040827668294e-7",
            "extra": "mean: 669.8886596874175 nsec\nrounds: 182883"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_development_length",
            "value": 457379.6727333244,
            "unit": "iter/sec",
            "range": "stddev: 4.364695456039702e-7",
            "extra": "mean: 2.186367387129272 usec\nrounds: 46681"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_ec",
            "value": 2678026.9868377973,
            "unit": "iter/sec",
            "range": "stddev: 1.9800580656624223e-7",
            "extra": "mean: 373.40923183929357 nsec\nrounds: 197707"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_fcr",
            "value": 4553426.544248571,
            "unit": "iter/sec",
            "range": "stddev: 3.117893176657137e-8",
            "extra": "mean: 219.61483078344574 nsec\nrounds: 190549"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_singly_reinforced",
            "value": 188482.48184644233,
            "unit": "iter/sec",
            "range": "stddev: 8.980148949280736e-7",
            "extra": "mean: 5.305532854850167 usec\nrounds: 19784"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_shear",
            "value": 154277.1875979397,
            "unit": "iter/sec",
            "range": "stddev: 9.011937264319604e-7",
            "extra": "mean: 6.481839704040305 usec\nrounds: 24330"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_check_deflection_span_depth",
            "value": 301401.57330592576,
            "unit": "iter/sec",
            "range": "stddev: 6.235493078379223e-7",
            "extra": "mean: 3.3178327141145663 usec\nrounds: 43058"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_beam_is456",
            "value": 57631.28272035673,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014482279258792733",
            "extra": "mean: 17.35168736139854 usec\nrounds: 9906"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_compute_detailing",
            "value": 44048.563487370106,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017634781375692895",
            "extra": "mean: 22.702215936888077 usec\nrounds: 11031"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_optimize_bar_arrangement",
            "value": 16448.26628259343,
            "unit": "iter/sec",
            "range": "stddev: 0.000004904377783557272",
            "extra": "mean: 60.79668111029194 usec\nrounds: 7385"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_batch_design_10_beams",
            "value": 396.8861757083064,
            "unit": "iter/sec",
            "range": "stddev: 0.0030204157490637943",
            "extra": "mean: 2.5196140888891914 msec\nrounds: 135"
          }
        ]
      }
    ]
  }
}