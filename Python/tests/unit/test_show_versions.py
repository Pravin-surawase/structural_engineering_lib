"""Tests for show_versions() diagnostic utility (TASK-725).

show_versions() reports library version, Python version, platform,
registered design codes, and optional dependency versions — modelled
after sklearn.show_versions() and pd.show_versions().
"""

import pytest

from structural_lib import VersionInfo, show_versions


class TestShowVersionsDefault:
    """Default (print) mode of show_versions()."""

    def test_default_returns_none(self):
        """show_versions() without as_dict returns None."""
        result = show_versions()
        assert result is None

    def test_default_prints_to_stdout(self, capsys):
        """Default mode should print version info to stdout."""
        show_versions()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_stdout_contains_library_name(self, capsys):
        """Printed output should contain 'structural_lib'."""
        show_versions()
        captured = capsys.readouterr()
        assert "structural_lib" in captured.out

    def test_stdout_contains_python(self, capsys):
        """Printed output should contain Python version info."""
        show_versions()
        captured = capsys.readouterr()
        assert "Python" in captured.out

    def test_stdout_contains_platform(self, capsys):
        """Printed output should contain platform info."""
        show_versions()
        captured = capsys.readouterr()
        assert "Platform" in captured.out

    def test_stdout_contains_design_codes_section(self, capsys):
        """Printed output should list design codes."""
        show_versions()
        captured = capsys.readouterr()
        assert "Design Codes" in captured.out

    def test_stdout_contains_dependencies_section(self, capsys):
        """Printed output should list dependencies."""
        show_versions()
        captured = capsys.readouterr()
        assert "Dependencies" in captured.out

    def test_stdout_contains_is456(self, capsys):
        """Printed output should mention IS 456."""
        show_versions()
        captured = capsys.readouterr()
        assert "IS 456" in captured.out


class TestShowVersionsAsDict:
    """as_dict=True mode returns VersionInfo."""

    def test_returns_version_info(self):
        """as_dict=True should return a VersionInfo instance."""
        result = show_versions(as_dict=True)
        assert isinstance(result, VersionInfo)

    def test_does_not_return_none(self):
        """as_dict=True must not return None."""
        result = show_versions(as_dict=True)
        assert result is not None


class TestVersionInfoFields:
    """Verify all VersionInfo fields are populated correctly."""

    @pytest.fixture()
    def info(self):
        return show_versions(as_dict=True)

    def test_library_version_is_string(self, info):
        """library_version should be a non-empty string."""
        assert isinstance(info.library_version, str)
        assert len(info.library_version) > 0

    def test_library_version_has_dots(self, info):
        """library_version should look like a semver string."""
        assert "." in info.library_version

    def test_python_version_matches_runtime(self, info):
        """python_version should match the running interpreter."""
        import platform

        assert info.python_version == platform.python_version()

    def test_python_version_is_python3(self, info):
        """We require Python 3.x."""
        assert info.python_version.startswith("3.")

    def test_platform_is_nonempty(self, info):
        """platform should be a non-empty string."""
        assert isinstance(info.platform, str)
        assert len(info.platform) > 0

    def test_design_codes_is_tuple(self, info):
        """design_codes should be an immutable tuple."""
        assert isinstance(info.design_codes, tuple)

    def test_design_codes_contains_is456(self, info):
        """IS456 must be among the registered codes."""
        assert "IS456" in info.design_codes

    def test_dependencies_is_dict(self, info):
        """dependencies should be a dict."""
        assert isinstance(info.dependencies, dict)

    def test_pydantic_dependency_present(self, info):
        """pydantic is a required dependency and must have a version."""
        assert "pydantic" in info.dependencies
        assert info.dependencies["pydantic"] is not None

    def test_dependency_versions_are_strings_or_none(self, info):
        """Each dependency value is either a version string or None."""
        for pkg, ver in info.dependencies.items():
            assert ver is None or isinstance(
                ver, str
            ), f"{pkg} has unexpected version type: {type(ver)}"

    def test_expected_dependencies_listed(self, info):
        """All expected optional deps should be checked."""
        expected = {"pydantic", "numpy", "pandas", "hypothesis", "pytest"}
        for pkg in expected:
            assert pkg in info.dependencies, f"{pkg} missing from dependencies"


class TestVersionInfoFrozen:
    """Immutability of VersionInfo."""

    def test_cannot_mutate_library_version(self):
        """Cannot set library_version on frozen VersionInfo."""
        info = show_versions(as_dict=True)
        with pytest.raises(AttributeError):
            info.library_version = "hacked"  # type: ignore[misc]

    def test_cannot_mutate_python_version(self):
        """Cannot set python_version on frozen VersionInfo."""
        info = show_versions(as_dict=True)
        with pytest.raises(AttributeError):
            info.python_version = "2.7"  # type: ignore[misc]

    def test_cannot_mutate_design_codes(self):
        """Cannot replace design_codes tuple."""
        info = show_versions(as_dict=True)
        with pytest.raises(AttributeError):
            info.design_codes = ("ACI318",)  # type: ignore[misc]


class TestVersionInfoToString:
    """to_string() display method."""

    def test_to_string_returns_str(self):
        """to_string() should return a string."""
        info = show_versions(as_dict=True)
        s = info.to_string()
        assert isinstance(s, str)

    def test_to_string_contains_library_name(self):
        """to_string() should contain 'structural_lib'."""
        info = show_versions(as_dict=True)
        assert "structural_lib" in info.to_string()

    def test_to_string_contains_python(self):
        """to_string() should contain 'Python'."""
        info = show_versions(as_dict=True)
        assert "Python" in info.to_string()

    def test_to_string_contains_pydantic(self):
        """to_string() should list pydantic in output."""
        info = show_versions(as_dict=True)
        assert "pydantic" in info.to_string()

    def test_to_string_matches_default_print(self, capsys):
        """to_string() output should match what default mode prints."""
        info = show_versions(as_dict=True)
        show_versions()  # prints to stdout
        captured = capsys.readouterr()
        # stdout has trailing newline from print()
        assert captured.out.strip() == info.to_string().strip()


class TestVersionInfoDictCompat:
    """Dict-style access on VersionInfo (via DictCompatMixin)."""

    @pytest.fixture()
    def info(self):
        return show_versions(as_dict=True)

    def test_contains_check(self, info):
        """'key in info' should work for valid fields."""
        assert "library_version" in info
        assert "python_version" in info
        assert "dependencies" in info

    def test_contains_false_for_nonexistent(self, info):
        """'bad_key in info' should return False."""
        assert "nonexistent_field" not in info

    def test_getitem_returns_value(self, info):
        """info['python_version'] should return the field value."""
        assert info["python_version"] == info.python_version

    def test_getitem_raises_for_missing(self, info):
        """info['bad'] should raise KeyError."""
        with pytest.raises(KeyError):
            info["nonexistent_field"]

    def test_get_with_default(self, info):
        """info.get('bad', default) should return default."""
        assert info.get("nonexistent_field", "fallback") == "fallback"

    def test_keys_returns_public_fields(self, info):
        """keys() should return public field names only."""
        k = info.keys()
        assert "library_version" in k
        assert "dependencies" in k
        # Internal display helpers should be excluded
        for key in k:
            assert not key.startswith("_"), f"Internal field leaked: {key}"

    def test_iteration_yields_field_names(self, info):
        """Iterating over info yields field names."""
        field_names = list(info)
        assert "library_version" in field_names


class TestVersionInfoToDict:
    """to_dict() serialization."""

    def test_to_dict_returns_dict(self):
        """to_dict() should return a plain dict."""
        info = show_versions(as_dict=True)
        d = info.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_has_expected_keys(self):
        """to_dict() should have all expected keys."""
        info = show_versions(as_dict=True)
        d = info.to_dict()
        expected = {
            "library_version",
            "python_version",
            "platform",
            "design_codes",
            "dependencies",
        }
        assert set(d.keys()) == expected

    def test_to_dict_design_codes_is_list(self):
        """to_dict() should serialize design_codes as a list."""
        info = show_versions(as_dict=True)
        d = info.to_dict()
        assert isinstance(d["design_codes"], list)

    def test_to_dict_dependencies_is_dict(self):
        """to_dict() should keep dependencies as a dict."""
        info = show_versions(as_dict=True)
        d = info.to_dict()
        assert isinstance(d["dependencies"], dict)

    def test_to_dict_values_match_attributes(self):
        """to_dict() values should match attribute values."""
        info = show_versions(as_dict=True)
        d = info.to_dict()
        assert d["library_version"] == info.library_version
        assert d["python_version"] == info.python_version
        assert d["platform"] == info.platform
