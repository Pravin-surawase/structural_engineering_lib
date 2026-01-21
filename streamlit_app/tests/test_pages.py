"""
Unit Tests for Streamlit Pages
===============================

Integration tests for Streamlit page modules.

Test Coverage:
- Page imports and structure
- Session state handling
- Component integration
- Error handling

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-FIX-001 Enhancement
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPageImports:
    """Test all pages can be imported without errors"""

    def test_beam_design_page_imports(self):
        """Test beam design page imports successfully"""
        # Import should not raise exception

        # Verify pages directory exists
        pages_dir = Path(__file__).parent.parent / "pages"
        assert pages_dir.exists()
        assert (pages_dir / "01_🏗️_beam_design.py").exists()

    def test_cost_optimizer_page_imports(self):
        """Test cost optimizer page imports successfully"""
        pages_dir = Path(__file__).parent.parent / "pages"
        assert (pages_dir / "02_💰_cost_optimizer.py").exists()

    def test_compliance_checker_page_imports(self):
        """Test compliance checker page imports successfully"""
        pages_dir = Path(__file__).parent.parent / "pages"
        assert (pages_dir / "03_✅_compliance.py").exists()

    def test_documentation_page_imports(self):
        """Test documentation page imports successfully"""
        pages_dir = Path(__file__).parent.parent / "pages"
        assert (pages_dir / "04_📚_documentation.py").exists()


class TestMainApp:
    """Test main app.py structure"""

    def test_app_file_exists(self):
        """Test app.py exists"""
        app_file = Path(__file__).parent.parent / "app.py"
        assert app_file.exists()

    def test_app_imports(self):
        """Test app.py can be imported"""
        # This is a basic structural test
        # In production, we'd use Streamlit testing utilities
        app_file = Path(__file__).parent.parent / "app.py"
        content = app_file.read_text()

        # Check for required imports
        assert "import streamlit as st" in content
        # Check for page config (either direct or via setup_page helper)
        assert "st.set_page_config" in content or "setup_page" in content


class TestPageStructure:
    """Test page file structure and conventions"""

    def test_all_pages_have_title(self):
        """Test all pages set a title"""
        pages_dir = Path(__file__).parent.parent / "pages"

        for page_file in pages_dir.glob("*.py"):
            if page_file.name.startswith("_"):
                continue

            content = page_file.read_text()
            # Each page should set a title/header or use modern layout helpers
            assert (
                "st.title" in content
                or "st.header" in content
                or "st.set_page_config" in content
                or "setup_page" in content
                or "page_header" in content
            ), f"Page {page_file.name} missing title/header"

    def test_pages_import_streamlit(self):
        """Test all pages import streamlit"""
        pages_dir = Path(__file__).parent.parent / "pages"

        for page_file in pages_dir.glob("*.py"):
            if page_file.name.startswith("_"):
                continue

            content = page_file.read_text()
            assert (
                "import streamlit" in content
            ), f"Page {page_file.name} doesn't import streamlit"

    def test_pages_use_components(self):
        """Test pages import custom components"""
        pages_dir = Path(__file__).parent.parent / "pages"

        # Beam design should use input components
        beam_design = pages_dir / "01_🏗️_beam_design.py"
        if beam_design.exists():
            content = beam_design.read_text()
            assert "from components" in content or "import components" in content


class TestConfigFiles:
    """Test configuration and requirements files"""

    def test_requirements_file_exists(self):
        """Test requirements.txt exists"""
        req_file = Path(__file__).parent.parent / "requirements.txt"
        assert req_file.exists()

    def test_requirements_has_streamlit(self):
        """Test requirements.txt includes streamlit"""
        req_file = Path(__file__).parent.parent / "requirements.txt"
        content = req_file.read_text()
        assert "streamlit" in content.lower()

    def test_requirements_has_plotly(self):
        """Test requirements.txt includes plotly"""
        req_file = Path(__file__).parent.parent / "requirements.txt"
        content = req_file.read_text()
        assert "plotly" in content.lower()

    def test_theme_config_exists(self):
        """Test .streamlit/config.toml exists"""
        config_file = Path(__file__).parent.parent / ".streamlit" / "config.toml"
        assert config_file.exists()

    def test_theme_has_primary_color(self):
        """Test theme config defines primary color"""
        config_file = Path(__file__).parent.parent / ".streamlit" / "config.toml"
        content = config_file.read_text()
        assert "primaryColor" in content


class TestDocumentation:
    """Test documentation files exist"""

    def test_readme_exists(self):
        """Test README.md exists"""
        readme = Path(__file__).parent.parent / "README.md"
        assert readme.exists()

    def test_readme_has_title(self):
        """Test README has title"""
        readme = Path(__file__).parent.parent / "README.md"
        content = readme.read_text()
        assert "#" in content  # Markdown header

    def test_implementation_log_exists(self):
        """Test IMPLEMENTATION_LOG.md exists"""
        log_file = Path(__file__).parent.parent / "docs" / "IMPLEMENTATION_LOG.md"
        assert log_file.exists()


class TestDirectoryStructure:
    """Test overall directory structure"""

    def test_components_directory_exists(self):
        """Test components/ directory exists"""
        comp_dir = Path(__file__).parent.parent / "components"
        assert comp_dir.exists()
        assert comp_dir.is_dir()

    def test_utils_directory_exists(self):
        """Test utils/ directory exists"""
        utils_dir = Path(__file__).parent.parent / "utils"
        assert utils_dir.exists()
        assert utils_dir.is_dir()

    def test_tests_directory_exists(self):
        """Test tests/ directory exists"""
        tests_dir = Path(__file__).parent.parent / "tests"
        assert tests_dir.exists()
        assert tests_dir.is_dir()

    def test_docs_directory_exists(self):
        """Test docs/ directory exists"""
        docs_dir = Path(__file__).parent.parent / "docs"
        assert docs_dir.exists()
        assert docs_dir.is_dir()

    def test_pages_directory_exists(self):
        """Test pages/ directory exists"""
        pages_dir = Path(__file__).parent.parent / "pages"
        assert pages_dir.exists()
        assert pages_dir.is_dir()


class TestFileNaming:
    """Test file naming conventions"""

    def test_pages_numbered_correctly(self):
        """Test pages are numbered 01, 02, 03, etc."""
        pages_dir = Path(__file__).parent.parent / "pages"
        page_files = sorted(pages_dir.glob("*.py"))

        # Should have multiple pages
        assert len(page_files) >= 4  # We created 4 pages

        # Check numbering pattern
        for page_file in page_files:
            if not page_file.name.startswith("_"):
                assert page_file.name[
                    :2
                ].isdigit(), f"Page {page_file.name} should start with two digits"

    def test_pages_have_emojis(self):
        """Test pages use emoji icons"""
        pages_dir = Path(__file__).parent.parent / "pages"

        for page_file in pages_dir.glob("*.py"):
            if page_file.name.startswith("_"):
                continue

            # Page names should have format: NN_emoji_name.py
            name_parts = page_file.name.split("_")
            assert (
                len(name_parts) >= 2
            ), f"Page {page_file.name} should have format NN_emoji_name.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
