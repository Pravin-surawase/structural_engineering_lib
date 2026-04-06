"""Tests for check_code() self-validation utility (TASK-724).

check_code() validates that a design code implementation meets the library's
API contract: clause decorators, frozen results, named parameters, and
architecture boundary compliance.
"""

import pytest

from structural_lib import CheckCodeReport, check_code


class TestCheckCodeReturnType:
    """Verify check_code() returns a well-formed CheckCodeReport."""

    def test_returns_check_code_report(self):
        """check_code('IS456') returns a CheckCodeReport instance."""
        result = check_code("IS456")
        assert isinstance(result, CheckCodeReport)

    def test_report_has_code_id(self):
        """Report should carry the requested code_id."""
        result = check_code("IS456")
        assert result.code_id == "IS456"

    def test_report_has_all_bool_fields(self):
        """All six check booleans must be present."""
        result = check_code("IS456")
        for attr in (
            "all_importable",
            "all_decorated",
            "all_frozen",
            "all_results_valid",
            "all_params_named",
            "no_boundary_violations",
        ):
            assert isinstance(getattr(result, attr), bool), f"{attr} is not bool"

    def test_issues_is_tuple(self):
        """issues must be an immutable tuple of strings."""
        result = check_code("IS456")
        assert isinstance(result.issues, tuple)
        for issue in result.issues:
            assert isinstance(issue, str)


class TestCheckCodeIS456:
    """IS 456 specific validation checks."""

    def test_is456_importable(self):
        """IS 456 beam/column/footing modules should be importable."""
        result = check_code("IS456")
        assert result.all_importable is True

    def test_is456_no_boundary_violations(self):
        """IS 456 should have no architecture boundary violations."""
        result = check_code("IS456")
        assert result.no_boundary_violations is True

    def test_is456_has_issues_due_to_tech_debt(self):
        """IS 456 currently has tech-debt issues (unfrozen results, etc.)."""
        result = check_code("IS456")
        # Pre-existing tech debt means some checks fail; this test
        # documents the current state so regressions are detected.
        assert len(result.issues) > 0

    def test_is456_all_pass_is_false_currently(self):
        """all_pass reflects tech debt — currently False for IS456."""
        result = check_code("IS456")
        # When tech debt is resolved this will flip to True and the test
        # should be updated.  Until then, this guards against a false
        # positive that hides a regression in check logic.
        assert result.all_pass is False


class TestCheckCodeAllPassProperty:
    """Verify the all_pass computed property logic."""

    def test_all_pass_consistency(self):
        """all_pass == True only when ALL six checks are True."""
        result = check_code("IS456")
        expected = (
            result.all_importable
            and result.all_decorated
            and result.all_frozen
            and result.all_results_valid
            and result.all_params_named
            and result.no_boundary_violations
        )
        assert result.all_pass == expected

    def test_all_pass_false_when_any_check_fails(self):
        """If any individual check is False, all_pass must be False."""
        result = check_code("IS456")
        checks = [
            result.all_importable,
            result.all_decorated,
            result.all_frozen,
            result.all_results_valid,
            result.all_params_named,
            result.no_boundary_violations,
        ]
        if not all(checks):
            assert result.all_pass is False


class TestCheckCodeSummary:
    """Verify the summary() display method."""

    def test_summary_returns_string(self):
        """summary() should return a non-empty string."""
        result = check_code("IS456")
        s = result.summary()
        assert isinstance(s, str)
        assert len(s) > 0

    def test_summary_contains_code_id(self):
        """summary() should include the code_id in the output."""
        result = check_code("IS456")
        s = result.summary()
        assert "IS456" in s

    def test_summary_contains_pass_or_fail(self):
        """summary() should include PASS or FAIL status."""
        result = check_code("IS456")
        s = result.summary()
        assert "PASS" in s or "FAIL" in s

    def test_summary_lists_check_marks(self):
        """summary() should include ✓ or ✗ marks for each check."""
        result = check_code("IS456")
        s = result.summary()
        # At least one check mark of either kind should appear
        assert "✓" in s or "✗" in s

    def test_summary_lists_issues_when_present(self):
        """When issues exist, summary() should display them."""
        result = check_code("IS456")
        if result.issues:
            s = result.summary()
            assert "Issues" in s


class TestCheckCodeInvalidCode:
    """Error handling for unknown code IDs."""

    def test_invalid_code_raises_key_error(self):
        """An unregistered code_id should raise KeyError."""
        with pytest.raises(KeyError):
            check_code("NONEXISTENT")

    def test_invalid_code_error_message_includes_code(self):
        """KeyError message should include the bad code_id."""
        with pytest.raises(KeyError, match="NONEXISTENT"):
            check_code("NONEXISTENT")

    def test_invalid_code_error_mentions_available(self):
        """KeyError message should hint at available codes."""
        with pytest.raises(KeyError, match="Available"):
            check_code("NONEXISTENT")

    def test_empty_string_code_raises(self):
        """Empty string as code_id should raise KeyError."""
        with pytest.raises(KeyError):
            check_code("")


class TestCheckCodeReportFrozen:
    """Immutability of CheckCodeReport."""

    def test_report_is_frozen(self):
        """Cannot mutate fields on a frozen CheckCodeReport."""
        result = check_code("IS456")
        with pytest.raises(AttributeError):
            result.all_importable = False  # type: ignore[misc]

    def test_report_code_id_immutable(self):
        """Cannot change code_id after construction."""
        result = check_code("IS456")
        with pytest.raises(AttributeError):
            result.code_id = "ACI318"  # type: ignore[misc]

    def test_report_issues_immutable(self):
        """Cannot replace the issues tuple."""
        result = check_code("IS456")
        with pytest.raises(AttributeError):
            result.issues = ()  # type: ignore[misc]


class TestCheckCodeDictCompat:
    """Dict-style access on CheckCodeReport (via DictCompatMixin)."""

    def test_contains_check(self):
        """'key in report' should work for valid field names."""
        result = check_code("IS456")
        assert "code_id" in result
        assert "all_importable" in result
        assert "issues" in result

    def test_contains_false_for_nonexistent(self):
        """'bad_key in report' should return False."""
        result = check_code("IS456")
        assert "nonexistent_field" not in result

    def test_getitem_returns_value(self):
        """report['code_id'] should return the field value."""
        result = check_code("IS456")
        assert result["code_id"] == "IS456"

    def test_getitem_raises_for_missing(self):
        """report['bad'] should raise KeyError."""
        result = check_code("IS456")
        with pytest.raises(KeyError):
            result["nonexistent_field"]

    def test_get_with_default(self):
        """report.get('bad', default) should return default."""
        result = check_code("IS456")
        assert result.get("nonexistent_field", "fallback") == "fallback"

    def test_keys_returns_field_names(self):
        """keys() should return all dataclass field names."""
        result = check_code("IS456")
        k = result.keys()
        assert "code_id" in k
        assert "all_importable" in k
        assert "issues" in k

    def test_iteration(self):
        """Iterating over report yields field names."""
        result = check_code("IS456")
        field_names = list(result)
        assert "code_id" in field_names

    def test_items_returns_pairs(self):
        """items() should return (name, value) pairs."""
        result = check_code("IS456")
        items = dict(result.items())
        assert items["code_id"] == "IS456"


class TestCheckCodeToDict:
    """to_dict() serialization."""

    def test_to_dict_returns_dict(self):
        """to_dict() should return a plain dict."""
        result = check_code("IS456")
        d = result.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_includes_all_pass(self):
        """to_dict() should include the computed all_pass field."""
        result = check_code("IS456")
        d = result.to_dict()
        assert "all_pass" in d
        assert d["all_pass"] == result.all_pass

    def test_to_dict_issues_is_list(self):
        """to_dict() should serialize issues as a list (not tuple)."""
        result = check_code("IS456")
        d = result.to_dict()
        assert isinstance(d["issues"], list)

    def test_to_dict_code_id_matches(self):
        """to_dict()['code_id'] should match the report's code_id."""
        result = check_code("IS456")
        d = result.to_dict()
        assert d["code_id"] == "IS456"

    def test_to_dict_has_expected_keys(self):
        """to_dict() should have all expected top-level keys."""
        result = check_code("IS456")
        d = result.to_dict()
        expected_keys = {
            "code_id",
            "all_pass",
            "all_importable",
            "all_decorated",
            "all_frozen",
            "all_results_valid",
            "all_params_named",
            "no_boundary_violations",
            "issues",
        }
        assert set(d.keys()) == expected_keys
