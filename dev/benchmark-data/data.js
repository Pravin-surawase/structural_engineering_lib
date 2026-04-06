window.BENCHMARK_DATA = {
  "lastUpdate": 1775499687717,
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
            "name": "Pravin Surawase",
            "username": "Pravin-surawase",
            "email": "pravinsurawase@gmail.com"
          },
          "id": "9029c18a6e31f140b0a009b4e470f2bbb415f26f",
          "message": "chore(release): v0.21.5 — test coverage & regression prevention (#542)",
          "timestamp": "2026-04-06T16:34:32Z",
          "url": "https://github.com/Pravin-surawase/structural_engineering_lib/commit/9029c18a6e31f140b0a009b4e470f2bbb415f26f"
        },
        "date": 1775499685237,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_mu_lim",
            "value": 879786.6210925607,
            "unit": "iter/sec",
            "range": "stddev: 1.9747559063586375e-7",
            "extra": "mean: 1.136639244136439 usec\nrounds: 88747"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_ast_required",
            "value": 542454.4132252865,
            "unit": "iter/sec",
            "range": "stddev: 2.635387214746322e-7",
            "extra": "mean: 1.8434728810745067 usec\nrounds: 63240"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_tv",
            "value": 1611447.047632828,
            "unit": "iter/sec",
            "range": "stddev: 6.576317179722586e-8",
            "extra": "mean: 620.5602607103801 nsec\nrounds: 197045"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_calculate_development_length",
            "value": 505753.6463285078,
            "unit": "iter/sec",
            "range": "stddev: 2.338996406262129e-7",
            "extra": "mean: 1.9772472373841452 usec\nrounds: 31221"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_ec",
            "value": 4020192.2259018226,
            "unit": "iter/sec",
            "range": "stddev: 2.0862770740208615e-8",
            "extra": "mean: 248.74432460146275 nsec\nrounds: 151355"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_get_fcr",
            "value": 4528683.093704877,
            "unit": "iter/sec",
            "range": "stddev: 1.8158216537817524e-8",
            "extra": "mean: 220.81474444304922 nsec\nrounds: 195122"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_singly_reinforced",
            "value": 199123.45177281043,
            "unit": "iter/sec",
            "range": "stddev: 4.26801080366384e-7",
            "extra": "mean: 5.0220101705596605 usec\nrounds: 32053"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_shear",
            "value": 164974.74071318874,
            "unit": "iter/sec",
            "range": "stddev: 4.5797780907102474e-7",
            "extra": "mean: 6.061534000156523 usec\nrounds: 19794"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_check_deflection_span_depth",
            "value": 307693.2128469486,
            "unit": "iter/sec",
            "range": "stddev: 3.8511863695233304e-7",
            "extra": "mean: 3.249990439332231 usec\nrounds: 46022"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_design_beam_is456",
            "value": 58887.102376159855,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023111082499562705",
            "extra": "mean: 16.981647247850404 usec\nrounds: 12445"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_compute_detailing",
            "value": 49716.19884978925,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013557873877656243",
            "extra": "mean: 20.11416848302028 usec\nrounds: 12387"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_optimize_bar_arrangement",
            "value": 17662.091032362663,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017129567746147825",
            "extra": "mean: 56.61843765654228 usec\nrounds: 7579"
          },
          {
            "name": "tests/performance/test_benchmarks.py::test_benchmark_batch_design_10_beams",
            "value": 423.52243610098793,
            "unit": "iter/sec",
            "range": "stddev: 0.0028154152759549546",
            "extra": "mean: 2.3611500000003596 msec\nrounds: 120"
          }
        ]
      }
    ]
  }
}