"""
Tests for Comprehensive Validator and Auto-Fixer
=================================================

Author: Agent 6 (Final Session)
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from comprehensive_validator import ComprehensiveValidator, ValidationRunner
from autonomous_fixer import AutoFixer, AutoFixRunner


@pytest.fixture
def temp_py_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestComprehensiveValidator:
    """Test ComprehensiveValidator class."""

    def test_validator_initialization(self):
        """Test validator can be initialized."""
        validator = ComprehensiveValidator()
        assert validator is not None
        assert not validator.strict_mode

    def test_validator_strict_mode(self):
        """Test strict mode initialization."""
        validator = ComprehensiveValidator(strict_mode=True)
        assert validator.strict_mode

    def test_validate_syntax_error(self, temp_py_file):
        """Test detection of syntax errors."""
        with open(temp_py_file, 'w') as f:
            f.write("def broken(\n")

        validator = ComprehensiveValidator()
        result = validator.validate_file(temp_py_file)

        assert not result.passed
        assert result.errors > 0


class TestAutoFixer:
    """Test AutoFixer class."""

    def test_fixer_initialization(self):
        """Test fixer can be initialized."""
        fixer = AutoFixer()
        assert fixer is not None
        assert not fixer.dry_run

    def test_fixer_dry_run_mode(self):
        """Test dry run mode."""
        fixer = AutoFixer(dry_run=True)
        assert fixer.dry_run


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
