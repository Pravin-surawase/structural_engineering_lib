"""Source-checkout and installed-wheel version identity contracts."""

from __future__ import annotations

import sys
from importlib.metadata import version

import structural_lib
from structural_lib.core import version as runtime_version
from structural_lib.services.common_api import get_library_version


def test_runtime_identity_is_resolved_once_for_the_import(monkeypatch):
    identity = runtime_version.get_runtime_version_identity()

    def unexpected_lookup(_origin):
        raise AssertionError("Current package lookup repeated after import")

    monkeypatch.setattr(runtime_version, "_resolve_identity", unexpected_lookup)
    assert runtime_version.get_runtime_version_identity() is identity
    assert (
        get_library_version() == identity.package_version == structural_lib.__version__
    )


def test_source_checkout_version_cannot_be_relabelled_by_stale_metadata(
    tmp_path, monkeypatch
) -> None:
    origin = tmp_path / "structural_lib" / "__init__.py"
    origin.parent.mkdir()
    origin.write_text("", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "structural-lib-is456"\nversion = "0.23.1a2"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(runtime_version, "version", lambda _name: "0.23.1a1")

    identity = runtime_version.get_runtime_version_identity(origin)

    assert identity.execution_mode == "SOURCE_CHECKOUT"
    assert identity.package_version == "0.23.1a2"
    assert identity.distribution_version == "0.23.1a1"
    assert identity.metadata_matches_runtime is False


def _distribution(root, package_version, *, records_package):
    info = root / f"structural_lib_is456-{package_version}.dist-info"
    info.mkdir(parents=True)
    (info / "METADATA").write_text(
        "Metadata-Version: 2.1\n"
        "Name: structural-lib-is456\n"
        f"Version: {package_version}\n",
        encoding="utf-8",
    )
    if records_package:
        (info / "RECORD").write_text("structural_lib/__init__.py,,\n", encoding="utf-8")


def test_installed_metadata_follows_the_imported_package(tmp_path, monkeypatch):
    installed = tmp_path / "site-packages"
    origin = installed / "structural_lib" / "__init__.py"
    origin.parent.mkdir(parents=True)
    origin.write_text("", encoding="utf-8")
    _distribution(installed, "0.23.1a2", records_package=True)
    _distribution(installed, "1.0.0", records_package=False)

    shadow = tmp_path / "shadow"
    _distribution(shadow, "9.9.9", records_package=True)
    monkeypatch.setattr(sys, "path", [str(shadow), str(installed)])
    assert version("structural-lib-is456") == "9.9.9"

    identity = runtime_version.get_runtime_version_identity(origin)

    assert identity.execution_mode == "INSTALLED_DISTRIBUTION"
    assert identity.package_version == identity.distribution_version == "0.23.1a2"
    assert identity.source_version is None
    assert identity.metadata_matches_runtime is True


def test_uninstalled_source_fails_closed_to_development_identity(tmp_path, monkeypatch):
    origin = tmp_path / "detached" / "structural_lib" / "__init__.py"
    origin.parent.mkdir(parents=True)
    origin.write_text("", encoding="utf-8")
    shadow = tmp_path / "shadow"
    _distribution(shadow, "9.9.9", records_package=True)
    monkeypatch.setattr(sys, "path", [str(shadow)])

    identity = runtime_version.get_runtime_version_identity(origin)

    assert identity.execution_mode == "UNINSTALLED_SOURCE"
    assert identity.package_version == "0.0.0-dev"
    assert identity.distribution_version is None
    assert identity.metadata_matches_runtime is False
