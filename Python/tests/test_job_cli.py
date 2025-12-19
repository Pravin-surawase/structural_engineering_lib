import pytest

from structural_lib import job_cli


def test_job_cli_main_run_invokes_runner(monkeypatch, tmp_path):
    called = {}

    def _fake_run_job(*, job_path: str, out_dir: str) -> None:
        called["job_path"] = job_path
        called["out_dir"] = out_dir

    monkeypatch.setattr(job_cli.job_runner, "run_job", _fake_run_job)

    rc = job_cli.main(["run", "--job", "job.json", "--out", str(tmp_path)])
    assert rc == 0
    assert called["job_path"] == "job.json"
    assert called["out_dir"] == str(tmp_path)


def test_job_cli_requires_subcommand():
    with pytest.raises(SystemExit):
        job_cli.main([])


def test_job_cli_unreachable_guard(monkeypatch):
    class _Parser:
        def parse_args(self, _argv):
            # Force the post-parse unreachable guard without relying on argparse internals.
            return type("Args", (), {"cmd": "nope"})()

    monkeypatch.setattr(job_cli, "_build_parser", lambda: _Parser())

    with pytest.raises(AssertionError):
        job_cli.main(["anything"])
