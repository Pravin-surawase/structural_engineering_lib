"""
Test Configuration and Fixtures
================================

Common fixtures and mocks for Streamlit component testing.

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-002
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to Python path for imports to work
# Tests should be run from project root: pytest streamlit_app/tests/
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ============================================================================
# IMPORTANT: Save reference to real streamlit before mocking
# This is needed for AppTest-based tests in apptest/ subdirectory
# ============================================================================
import streamlit as _real_streamlit  # noqa: E402

# Store the real module so AppTest can use it
_REAL_STREAMLIT_MODULE = _real_streamlit


class MockSessionState(dict):
    """Session state mock supporting both dict and attribute access."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        # Allow normal attribute setting for dict internals
        if name in {"_MutableMapping__marker"}:
            super().__setattr__(name, value)
        else:
            self[name] = value


class MockStreamlit:
    """Enhanced Streamlit mock for testing"""

    # Mock session_state with dict + attribute access
    session_state = MockSessionState()

    # Call tracking attributes for test verification
    markdown_called = False
    markdown_calls = []
    empty_calls = []
    container_calls = []

    # Cache storage (cleared between tests)
    _cache_data_storage = {}
    _cache_resource_storage = {}

    @staticmethod
    def columns(num_cols):
        """Mock st.columns() - returns list of mock column objects

        Args:
            num_cols: Can be int (number of columns) or list (column widths)
        """
        if isinstance(num_cols, list):
            # If list passed (e.g. [1, 2, 1]), return that many columns
            count = len(num_cols)
        else:
            # If int passed, that's the count
            count = num_cols
        return [MagicMock() for _ in range(count)]

    @staticmethod
    def info(msg):
        """Mock st.info()"""
        pass

    @staticmethod
    def success(msg):
        """Mock st.success()"""
        pass

    @staticmethod
    def warning(msg):
        """Mock st.warning()"""
        pass

    @staticmethod
    def error(msg):
        """Mock st.error()"""
        pass

    @staticmethod
    def divider():
        """Mock st.divider()"""
        pass

    @staticmethod
    def subheader(text):
        """Mock st.subheader()"""
        pass

    @staticmethod
    def expander(label, expanded=False):
        """Mock st.expander() - returns context manager"""

        class MockExpander:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def markdown(self, text):
                pass

            def metric(self, label, value):
                pass

        return MockExpander()

    @staticmethod
    def markdown(text, **kwargs):
        """Mock st.markdown() accepting arbitrary kwargs (e.g. unsafe_allow_html)."""
        MockStreamlit.markdown_called = True
        MockStreamlit.markdown_calls.append({"text": text, "kwargs": kwargs})
        pass

    @staticmethod
    def caption(text):
        """Mock st.caption()"""
        pass

    @staticmethod
    def metric(label, value, delta=None, delta_color="normal"):
        """Mock st.metric()"""
        pass

    @staticmethod
    def progress(value):
        """Mock st.progress() - returns object that can update progress"""

        class ProgressBar:
            def progress(self, value):
                pass

            def empty(self):
                pass

        return ProgressBar()

    @staticmethod
    def empty():
        """Mock st.empty() returning a placeholder with container() and empty()."""
        MockStreamlit.empty_calls.append(True)
        placeholder = MagicMock()

        class ContainerCtx:
            def __enter__(self_inner):
                return placeholder

            def __exit__(self_inner, exc_type, exc, tb):
                pass

        placeholder.container.return_value = ContainerCtx()
        placeholder.empty = MagicMock()
        placeholder.markdown = MockStreamlit.markdown
        return placeholder

    @staticmethod
    def cache_data(func=None, **kwargs):
        """Mock st.cache_data decorator.

        Actually caches function results using args/kwargs as keys.
        Supports both @st.cache_data and @st.cache_data().
        """

        def decorator(f):
            import functools
            import json

            @functools.wraps(f)
            def wrapper(*args, **kw):
                # Create a cache key from function name and args
                # Use JSON serialization for unhashable types like dicts
                try:
                    key = (f.__name__, args, tuple(sorted(kw.items())))
                    hash(key)  # Test if hashable
                except TypeError:
                    # Fall back to JSON-based key for unhashable args
                    key = f.__name__ + json.dumps(
                        (args, kw), sort_keys=True, default=str
                    )

                if key not in MockStreamlit._cache_data_storage:
                    MockStreamlit._cache_data_storage[key] = f(*args, **kw)
                return MockStreamlit._cache_data_storage[key]

            wrapper.clear = lambda: MockStreamlit._cache_data_storage.clear()
            return wrapper

        if func is None:
            return decorator
        return decorator(func)

    @staticmethod
    def cache_resource(func=None, **kwargs):
        """Mock st.cache_resource decorator.

        Actually caches singleton resources using function name as key.
        """

        def decorator(f):
            import functools
            import json

            @functools.wraps(f)
            def wrapper(*args, **kw):
                # Create a cache key from function name and args
                # Use JSON serialization for unhashable types like dicts
                try:
                    key = (f.__name__, args, tuple(sorted(kw.items())))
                    hash(key)  # Test if hashable
                except TypeError:
                    # Fall back to JSON-based key for unhashable args
                    key = f.__name__ + json.dumps(
                        (args, kw), sort_keys=True, default=str
                    )

                if key not in MockStreamlit._cache_resource_storage:
                    MockStreamlit._cache_resource_storage[key] = f(*args, **kw)
                return MockStreamlit._cache_resource_storage[key]

            wrapper.clear = lambda: MockStreamlit._cache_resource_storage.clear()
            return wrapper

        if func is None:
            return decorator
        return decorator(func)

    @staticmethod
    def spinner(text="Loading..."):
        """Mock st.spinner() context manager"""

        class SpinnerContext:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        return SpinnerContext()

    @staticmethod
    def status(label, expanded=False, state="running"):
        """Mock st.status() context manager"""

        class StatusContext:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def update(self, **kwargs):
                pass

        return StatusContext()

    @staticmethod
    def tabs(labels):
        """Mock st.tabs() - returns list of tab contexts"""

        class TabContext:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def markdown(self, text, **kwargs):
                MockStreamlit.markdown(text, **kwargs)

            def metric(self, label, value, delta=None):
                pass

            def write(self, *args):
                pass

        return [TabContext() for _ in labels]

    @staticmethod
    def container():
        """Mock st.container() context manager"""
        MockStreamlit.container_calls.append(True)

        class ContainerContext:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def markdown(self, text, **kwargs):
                MockStreamlit.markdown(text, **kwargs)

            def write(self, *args):
                pass

        return ContainerContext()

    @staticmethod
    def plotly_chart(
        fig, width="stretch", use_container_width=None, key=None, **kwargs
    ):
        """Mock st.plotly_chart() - supports both old and new API."""
        pass

    @staticmethod
    def write(*args, **kwargs):
        """Mock st.write()"""
        pass

    @staticmethod
    def button(label, key=None, **kwargs):
        """Mock st.button() - returns False"""
        return False

    @staticmethod
    def selectbox(label, options, index=0, key=None, **kwargs):
        """Mock st.selectbox() - returns first option"""
        return options[index] if options else None

    @staticmethod
    def number_input(
        label, value=None, min_value=None, max_value=None, key=None, **kwargs
    ):
        """Mock st.number_input() - returns value or default"""
        return (
            value if value is not None else (min_value if min_value is not None else 0)
        )


# Add class-level clear methods for cache decorators
MockStreamlit.cache_data.clear = lambda: MockStreamlit._cache_data_storage.clear()
MockStreamlit.cache_resource.clear = (
    lambda: MockStreamlit._cache_resource_storage.clear()
)

# ============================================================================
# Streamlit Module Mocking
# ============================================================================
# Replace streamlit module with enhanced mock for unit tests.
# NOTE: AppTest-based tests in apptest/ subdirectory need the REAL streamlit
# module. They should restore it using _REAL_STREAMLIT_MODULE.
# ============================================================================
sys.modules["streamlit"] = MockStreamlit()

import streamlit as st


def get_real_streamlit():
    """Get the real streamlit module (for AppTest tests).

    Returns the actual streamlit module that was saved before mocking.
    Use this in AppTest-based tests that need the real streamlit.
    """
    return _REAL_STREAMLIT_MODULE


@pytest.fixture
def real_streamlit():
    """Pytest fixture providing the real streamlit module.

    Use this fixture in tests that need the real streamlit module
    instead of the mock (e.g., AppTest-based tests).
    """
    return _REAL_STREAMLIT_MODULE


@pytest.fixture
def clean_session_state():
    """Reset Streamlit session_state before and after each test."""
    st.session_state.clear()
    yield
    st.session_state.clear()


@pytest.fixture
def mock_streamlit():
    """Provide MockStreamlit instance for testing."""
    # Reset all tracking attributes
    MockStreamlit.session_state.clear()
    MockStreamlit.markdown_called = False
    MockStreamlit.markdown_calls = []
    MockStreamlit.empty_calls = []
    MockStreamlit.container_calls = []

    yield MockStreamlit

    # Cleanup after test
    MockStreamlit.session_state.clear()
    MockStreamlit.markdown_called = False
    MockStreamlit.markdown_calls = []
    MockStreamlit.empty_calls = []
    MockStreamlit.container_calls = []


@pytest.fixture(autouse=True)
def reset_all_mock_state():
    """Auto-reset all mock state before each test to prevent test pollution."""
    # Reset all tracking before test
    MockStreamlit.session_state.clear()
    MockStreamlit.markdown_called = False
    MockStreamlit.markdown_calls = []
    MockStreamlit.empty_calls = []
    MockStreamlit.container_calls = []

    # Clear cache storage
    MockStreamlit._cache_data_storage.clear()
    MockStreamlit._cache_resource_storage.clear()

    # Clear all cache decorators
    MockStreamlit.cache_data.clear()
    MockStreamlit.cache_resource.clear()

    yield

    # Cleanup after test
    MockStreamlit.session_state.clear()
    MockStreamlit.markdown_called = False
    MockStreamlit.markdown_calls = []
    MockStreamlit.empty_calls = []
    MockStreamlit.container_calls = []

    # Clear cache storage
    MockStreamlit._cache_data_storage.clear()
    MockStreamlit._cache_resource_storage.clear()

    # Clear all cache decorators
    MockStreamlit.cache_data.clear()
    MockStreamlit.cache_resource.clear()
