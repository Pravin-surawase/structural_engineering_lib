window.BENCHMARK_DATA = {
  "lastUpdate": 1775412750364,
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
          "id": "3839a969e53f5061df1451860b4f26e4c88685fd",
          "message": "TASK-RELEASE-0214: v0.21.4 release — P0/P1 sprint + external audit fixes (#533)\n\n* chore(release): bump version to 0.21.4\n\n* fix(docs): use HEAD ref in CHANGELOG compare link until tag exists\n\n* fix(docs): correct GitHub username casing in CHANGELOG compare link",
          "timestamp": "2026-04-05T17:23:22Z",
          "url": "https://github.com/Pravin-surawase/structural_engineering_lib/commit/3839a969e53f5061df1451860b4f26e4c88685fd"
        },
        "date": 1775412748948,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_mu_lim",
            "value": 824313.091224178,
            "unit": "iter/sec",
            "range": "stddev: 3.9391182681265386e-7",
            "extra": "mean: 1.213131285486333 usec\nrounds: 87245"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_ast_required",
            "value": 502774.9623948829,
            "unit": "iter/sec",
            "range": "stddev: 5.588911197838879e-7",
            "extra": "mean: 1.9889614137439744 usec\nrounds: 58337"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_tv",
            "value": 1410400.45702889,
            "unit": "iter/sec",
            "range": "stddev: 1.1768121187809769e-7",
            "extra": "mean: 709.0184883423619 nsec\nrounds: 190877"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_development_length",
            "value": 449387.62184464076,
            "unit": "iter/sec",
            "range": "stddev: 5.885521039179124e-7",
            "extra": "mean: 2.2252504327894314 usec\nrounds: 61234"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_ec",
            "value": 3747209.748639547,
            "unit": "iter/sec",
            "range": "stddev: 3.9215330412948265e-8",
            "extra": "mean: 266.86523228731926 nsec\nrounds: 174826"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_fcr",
            "value": 4239622.302239561,
            "unit": "iter/sec",
            "range": "stddev: 3.613109940566232e-8",
            "extra": "mean: 235.8700678293334 nsec\nrounds: 193424"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_singly_reinforced",
            "value": 177405.00616796417,
            "unit": "iter/sec",
            "range": "stddev: 0.000001834205144722733",
            "extra": "mean: 5.636819510342432 usec\nrounds: 30722"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_shear",
            "value": 144621.58109604695,
            "unit": "iter/sec",
            "range": "stddev: 0.000001173884175510444",
            "extra": "mean: 6.91459734032277 usec\nrounds: 26469"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_check_deflection_span_depth",
            "value": 284338.508810829,
            "unit": "iter/sec",
            "range": "stddev: 7.344853787075491e-7",
            "extra": "mean: 3.5169348118981025 usec\nrounds: 41572"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_beam_is456",
            "value": 51781.175885849516,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027041364554686933",
            "extra": "mean: 19.312037297192294 usec\nrounds: 10966"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_compute_detailing",
            "value": 43651.467171604985,
            "unit": "iter/sec",
            "range": "stddev: 0.00000301644229492899",
            "extra": "mean: 22.90873743301105 usec\nrounds: 11399"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_optimize_bar_arrangement",
            "value": 16301.709856925398,
            "unit": "iter/sec",
            "range": "stddev: 0.000005349887872098909",
            "extra": "mean: 61.343258392933144 usec\nrounds: 7864"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_batch_design_10_beams",
            "value": 329.8374523031625,
            "unit": "iter/sec",
            "range": "stddev: 0.0030215431239515233",
            "extra": "mean: 3.0317963985511054 msec\nrounds: 138"
          }
        ]
      }
    ]
  }
}