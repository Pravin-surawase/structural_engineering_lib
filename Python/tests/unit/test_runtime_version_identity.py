"""Source-checkout and installed-wheel version identity contracts."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError

from structural_lib.core import version as runtime_version


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


def test_installed_distribution_metadata_is_authoritative_without_source_project(
    tmp_path, monkeypatch
) -> None:
    origin = tmp_path / "site-packages" / "structural_lib" / "__init__.py"
    origin.parent.mkdir(parents=True)
    origin.write_text("", encoding="utf-8")
    monkeypatch.setattr(runtime_version, "version", lambda _name: "0.23.1a2")

    identity = runtime_version.get_runtime_version_identity(origin)

    assert identity.execution_mode == "INSTALLED_DISTRIBUTION"
    assert identity.package_version == "0.23.1a2"
    assert identity.source_version is None
    assert identity.metadata_matches_runtime is True


def test_uninstalled_source_fails_closed_to_development_identity(
    tmp_path, monkeypatch
) -> None:
    origin = tmp_path / "structural_lib" / "__init__.py"
    origin.parent.mkdir()
    origin.write_text("", encoding="utf-8")

    def missing_distribution(_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr(runtime_version, "version", missing_distribution)

    identity = runtime_version.get_runtime_version_identity(origin)

    assert identity.execution_mode == "UNINSTALLED_SOURCE"
    assert identity.package_version == "0.0.0-dev"
    assert identity.metadata_matches_runtime is False
