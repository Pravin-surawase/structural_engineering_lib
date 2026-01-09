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
from unittest.mock import MagicMock, Mock

# Add project root to Python path for imports to work
# Tests should be run from project root: pytest streamlit_app/tests/
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


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
        MockStreamlit.markdown_calls.append({'text': text, 'kwargs': kwargs})
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
        """Mock st.progress()"""
        pass

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

        Behaves as an identity decorator in tests, supports both
        @st.cache_data and @st.cache_data(). Marks functions as cached
        by setting __wrapped__ and clear attributes, so tests can detect it.
        """

        def decorator(f):
            setattr(f, "clear", lambda: None)
            return f

        if func is None:
            return decorator
        return decorator(func)

    # Add clear method to cache_data itself
    cache_data.clear = lambda: None

    @staticmethod
    def cache_resource(func=None, **kwargs):
        """Mock st.cache_resource decorator.

        Similar to cache_data but for singleton resources like
        database connections, theme objects, etc.
        """

        def decorator(f):
            setattr(f, "clear", lambda: None)
            return f

        if func is None:
            return decorator
        return decorator(func)

    # Add clear method to cache_resource itself
    cache_resource.clear = lambda: None

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
    def plotly_chart(fig, use_container_width=True, key=None, **kwargs):
        """Mock st.plotly_chart()"""
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
    def number_input(label, value=None, min_value=None, max_value=None, key=None, **kwargs):
        """Mock st.number_input() - returns value or default"""
        return value if value is not None else (min_value if min_value is not None else 0)


# Replace streamlit module with enhanced mock
sys.modules['streamlit'] = MockStreamlit()

# Attach a no-op clear() to mimic Streamlit's cache API on the decorator itself
MockStreamlit.cache_data.clear = lambda: None

import streamlit as st


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

    yield

    # Cleanup after test
    MockStreamlit.session_state.clear()
    MockStreamlit.markdown_called = False
    MockStreamlit.markdown_calls = []
    MockStreamlit.empty_calls = []
    MockStreamlit.container_calls = []
