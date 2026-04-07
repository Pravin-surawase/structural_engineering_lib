window.BENCHMARK_DATA = {
  "lastUpdate": 1775586108210,
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
          "id": "e08865a69444f79ebc9a5e3f56bc7222615cf5b1",
          "message": "docs: add SESSION_LOG entry for 2026-04-07 (CI fix)",
          "timestamp": "2026-04-07T15:40:20Z",
          "url": "https://github.com/Pravin-surawase/structural_engineering_lib/commit/e08865a69444f79ebc9a5e3f56bc7222615cf5b1"
        },
        "date": 1775586105432,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_mu_lim",
            "value": 812228.1858895704,
            "unit": "iter/sec",
            "range": "stddev: 3.4687850708920716e-7",
            "extra": "mean: 1.2311811106441446 usec\nrounds: 87245"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_ast_required",
            "value": 492980.1016493922,
            "unit": "iter/sec",
            "range": "stddev: 4.858517661091715e-7",
            "extra": "mean: 2.0284794389352467 usec\nrounds: 68503"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_tv",
            "value": 1401928.7432127586,
            "unit": "iter/sec",
            "range": "stddev: 1.078051754826322e-7",
            "extra": "mean: 713.3030154644878 nsec\nrounds: 198847"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_development_length",
            "value": 439961.61361806287,
            "unit": "iter/sec",
            "range": "stddev: 5.382380819866432e-7",
            "extra": "mean: 2.272925566793004 usec\nrounds: 55701"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_ec",
            "value": 3725948.9358278806,
            "unit": "iter/sec",
            "range": "stddev: 3.7819541777616115e-8",
            "extra": "mean: 268.3880045655556 nsec\nrounds: 180181"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_fcr",
            "value": 4191768.946335487,
            "unit": "iter/sec",
            "range": "stddev: 3.7434704910896593e-8",
            "extra": "mean: 238.56276736679783 nsec\nrounds: 197668"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_singly_reinforced",
            "value": 181370.64300712713,
            "unit": "iter/sec",
            "range": "stddev: 0.000001030367198001987",
            "extra": "mean: 5.513571454674195 usec\nrounds: 27339"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_shear",
            "value": 142134.72677390283,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010325394522229198",
            "extra": "mean: 7.035578304454226 usec\nrounds: 26116"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_check_deflection_span_depth",
            "value": 283811.34651920374,
            "unit": "iter/sec",
            "range": "stddev: 7.019362135892366e-7",
            "extra": "mean: 3.5234673041246296 usec\nrounds: 46642"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_beam_is456",
            "value": 48650.697041419255,
            "unit": "iter/sec",
            "range": "stddev: 0.000006719982905616018",
            "extra": "mean: 20.554690082829442 usec\nrounds: 8954"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_compute_detailing",
            "value": 43190.99126602932,
            "unit": "iter/sec",
            "range": "stddev: 0.0000038079170674837945",
            "extra": "mean: 23.152976365849756 usec\nrounds: 11255"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_optimize_bar_arrangement",
            "value": 16140.390132634559,
            "unit": "iter/sec",
            "range": "stddev: 0.000009875117442372396",
            "extra": "mean: 61.95637105314333 usec\nrounds: 7538"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_batch_design_10_beams",
            "value": 336.3992738954391,
            "unit": "iter/sec",
            "range": "stddev: 0.003029231373099173",
            "extra": "mean: 2.972658021583078 msec\nrounds: 139"
          }
        ]
      }
    ]
  }
}