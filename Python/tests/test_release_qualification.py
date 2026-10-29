"""The artifact gate must reject wrong versions, missing data and source drift."""

from __future__ import annotations

import argparse
import importlib
import io
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
qualification = importlib.import_module("_lib.release_qualification")
probe = importlib.import_module("_lib.release_qualification_probe")
release = importlib.import_module("release")


def pair(tmp_path, *, wheel_version="0.26.0", omit=None, drift=False, forbidden=False):
    source = tmp_path / "repo/Python"
    source.mkdir(parents=True)
    payload = dict.fromkeys(qualification.REQUIRED_RESOURCES, b"controlled fixture")
    payload["structural_lib/__init__.py"] = b'__version__="0.26.0"\n'
    for name, content in payload.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    if omit:
        del payload[omit]
    if drift:
        payload["structural_lib/__init__.py"] = b'__version__="different code"\n'
    if forbidden:
        payload["structural_lib/research/experiment.py"] = b"not distributable"
    wheel = tmp_path / "candidate.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "candidate.dist-info/METADATA",
            f"Name: structural-lib-is456\nVersion: {wheel_version}\n",
        )
        for name, content in payload.items():
            archive.writestr(name, content)
    sdist = tmp_path / "candidate.tar.gz"
    with tarfile.open(sdist, "w:gz") as archive:
        for name, content in {
            "PKG-INFO": b"Name: structural-lib-is456\nVersion: 0.26.0\n",
            **payload,
        }.items():
            info = tarfile.TarInfo("candidate-0.26.0/" + name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
    return source.parent, wheel, sdist


def test_wheel_sdist_and_source_must_share_complete_package_payload(tmp_path):
    repo, wheel, sdist = pair(tmp_path)
    result = qualification.inspect_distribution_pair(repo, wheel, sdist, "0.26.0")
    assert result["package_file_count"] == 4
    assert len(result["package_payload_sha256"]) == 64


@pytest.mark.parametrize(
    "change,error",
    [
        ({"wheel_version": "0.26.1"}, "Wheel version"),
        ({"omit": qualification.REQUIRED_RESOURCES[-1]}, "missing required"),
        ({"drift": True}, "frozen source"),
        ({"forbidden": True}, "Forbidden distribution"),
    ],
)
def test_candidate_identity_data_and_scope_fail_closed(tmp_path, change, error):
    repo, wheel, sdist = pair(tmp_path, **change)
    with pytest.raises(ValueError, match=error):
        qualification.inspect_distribution_pair(repo, wheel, sdist, "0.26.0")


def test_checkout_import_cannot_count_as_installed_artifact(tmp_path):
    with pytest.raises(AssertionError, match="Checkout/foreign package import"):
        probe.assert_installed(
            {
                "venv": str(tmp_path / "disposable"),
                "version": "0.26.0",
                "package_files": {},
            }
        )


@pytest.mark.parametrize(
    "overrides",
    [
        {"sdist": "candidate.tar.gz"},
        {
            "qualification": True,
            "source": "pypi",
            "sdist": "candidate.tar.gz",
            "receipt": "receipt.json",
        },
        {"qualification": True, "sdist": None, "receipt": "receipt.json"},
    ],
)
def test_qualification_options_never_silently_fall_back_to_other_verification(
    overrides,
):
    values = {
        "wheel_dir": "Python/dist",
        "job": "Python/examples/sample_job_is456.json",
        "version": "0.26.0",
        "source": "wheel",
        "qualification": False,
        "sdist": None,
        "receipt": None,
        "qualification_profiles": None,
    }
    assert release.cmd_verify(argparse.Namespace(**{**values, **overrides})) == 2
