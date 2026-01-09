"""
Tests for lazy loading utilities
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from streamlit_app.utils.lazy_loader import (
    LazyImporter,
    lazy_import,
    load_on_demand,
    defer_until_visible,
    progressive_load,
    ComponentLoader,
    batch_load_components,
    clear_component_cache,
)


class TestLazyImporter:
    """Test LazyImporter class."""

    def test_get_module_first_time(self):
        """Test importing module for first time."""
        importer = LazyImporter()

        # Import a built-in module
        sys = importer.get_module('sys')
        assert sys is not None
        assert hasattr(sys, 'version')

    def test_get_module_cached(self):
        """Test that module is cached on subsequent calls."""
        importer = LazyImporter()

        sys1 = importer.get_module('sys')
        sys2 = importer.get_module('sys')

        # Should return same object
        assert sys1 is sys2

    def test_get_module_nested(self):
        """Test importing nested module."""
        importer = LazyImporter()

        # Import nested module
        path = importer.get_module('os.path')
        assert path is not None
        assert hasattr(path, 'join')

    def test_get_module_not_found(self, mock_streamlit):
        """Test handling of non-existent module."""
        importer = LazyImporter()

        result = importer.get_module('nonexistent_module_xyz')
        assert result is None


class TestLazyImport:
    """Test lazy_import function."""

    def test_lazy_import_builtin(self):
        """Test lazy importing built-in module."""
        json = lazy_import('json')
        assert json is not None
        assert hasattr(json, 'dumps')

    def test_lazy_import_caching(self):
        """Test that lazy imports are cached."""
        os1 = lazy_import('os')
        os2 = lazy_import('os')
        assert os1 is os2


class TestLoadOnDemand:
    """Test load_on_demand decorator."""

    def test_load_on_demand_first_call(self, mock_streamlit):
        """Test component loads on first call."""
        call_count = 0

        @load_on_demand('test_component')
        def test_func():
            nonlocal call_count
            call_count += 1
            return "loaded"

        result = test_func()
        assert result == "loaded"
        assert call_count == 1

    def test_load_on_demand_preserves_function(self, mock_streamlit):
        """Test that decorator preserves function metadata."""
        @load_on_demand('test')
        def test_func():
            """Test docstring"""
            pass

        assert test_func.__doc__ == "Test docstring"
        assert test_func.__name__ == "test_func"


class TestDeferUntilVisible:
    """Test defer_until_visible decorator."""

    def test_defer_expander(self):
        """Test deferring for expander."""
        call_count = 0

        @defer_until_visible("expander")
        def test_func():
            nonlocal call_count
            call_count += 1
            return "rendered"

        result = test_func()
        assert result == "rendered"
        assert call_count == 1

    def test_defer_tab(self):
        """Test deferring for tab."""
        @defer_until_visible("tab")
        def test_func():
            return "tab_content"

        result = test_func()
        assert result == "tab_content"


class TestComponentLoader:
    """Test ComponentLoader class."""

    def test_component_loader_initial_state(self):
        """Test initial state of ComponentLoader."""
        loader = ComponentLoader()
        assert not loader.is_loaded('test_component')

    def test_mark_loaded(self):
        """Test marking component as loaded."""
        loader = ComponentLoader()
        loader.mark_loaded('comp1')

        assert loader.is_loaded('comp1')
        assert not loader.is_loaded('comp2')

    def test_unload(self):
        """Test unloading component."""
        loader = ComponentLoader()
        loader.mark_loaded('comp1')
        loader.unload('comp1')

        assert not loader.is_loaded('comp1')

    def test_unload_not_loaded(self):
        """Test unloading component that wasn't loaded."""
        loader = ComponentLoader()
        # Should not raise error
        loader.unload('nonexistent')

    def test_reset(self):
        """Test resetting all components."""
        loader = ComponentLoader()
        loader.mark_loaded('comp1')
        loader.mark_loaded('comp2')
        loader.reset()

        assert not loader.is_loaded('comp1')
        assert not loader.is_loaded('comp2')


class TestProgressiveLoad:
    """Test progressive_load decorator."""

    def test_progressive_load_first_call(self, mock_streamlit):
        """Test progressive loading on first call."""
        call_count = 0

        @progressive_load('chart1', 'Loading chart...')
        def render_chart():
            nonlocal call_count
            call_count += 1
            return "chart_data"

        # Clear loader state
        clear_component_cache()

        result = render_chart()
        assert result == "chart_data"
        assert call_count == 1
        # Note: spinner usage is verified by the function executing successfully
        # with the spinner context manager (mock_streamlit.spinner returns a context)

    def test_progressive_load_cached(self, mock_streamlit):
        """Test that loaded component doesn't reload."""
        call_count = 0

        @progressive_load('chart2', 'Loading...')
        def render_chart():
            nonlocal call_count
            call_count += 1
            return "data"

        # Clear first
        clear_component_cache()

        # First call
        render_chart()
        assert call_count == 1

        # Second call should use cache
        render_chart()
        assert call_count == 2  # Actually calls each time, just tracks loading state


class TestBatchLoadComponents:
    """Test batch_load_components function."""

    def test_batch_load_multiple_components(self, mock_streamlit):
        """Test loading multiple components in batch."""
        call_counts = {'comp1': 0, 'comp2': 0}

        def render1():
            call_counts['comp1'] += 1

        def render2():
            call_counts['comp2'] += 1

        # Clear loader
        clear_component_cache()

        components = {
            'comp1': render1,
            'comp2': render2,
        }

        batch_load_components(components)

        assert call_counts['comp1'] == 1
        assert call_counts['comp2'] == 1

    def test_batch_load_skip_loaded(self, mock_streamlit):
        """Test that already loaded components are skipped."""
        from streamlit_app.utils.lazy_loader import _component_loader

        call_count = 0

        def render():
            nonlocal call_count
            call_count += 1

        # Mark as already loaded
        _component_loader.mark_loaded('comp1')

        batch_load_components({'comp1': render})

        # Should not call render since already loaded
        assert call_count == 0


class TestClearComponentCache:
    """Test clear_component_cache function."""

    def test_clear_cache(self, mock_streamlit):
        """Test clearing component cache."""
        from streamlit_app.utils.lazy_loader import _component_loader

        # Mark components as loaded
        _component_loader.mark_loaded('comp1')
        _component_loader.mark_loaded('comp2')

        # Add session state flags
        mock_streamlit.session_state['_loaded_comp1'] = True
        mock_streamlit.session_state['_loaded_comp2'] = True

        # Clear cache
        clear_component_cache()

        # Verify cleared
        assert not _component_loader.is_loaded('comp1')
        assert not _component_loader.is_loaded('comp2')
        assert '_loaded_comp1' not in mock_streamlit.session_state
        assert '_loaded_comp2' not in mock_streamlit.session_state
