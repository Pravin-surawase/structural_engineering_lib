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

    def get(self, key, default=None):
        """Enhanced get() with default handling"""
        return super().get(key, default)


class MockStreamlit:
    """Enhanced Streamlit mock for testing"""

    # Mock session_state with dict + attribute access
    session_state = MockSessionState()

    # Call tracking attributes
    markdown_called = False
    markdown_calls = []

    @staticmethod
    def columns(num_cols):
        """Mock st.columns() - returns list of mock column objects"""
        return [MagicMock() for _ in range(num_cols)]

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
        placeholder = MagicMock()

        class ContainerCtx:
            def __enter__(self_inner):
                return placeholder

            def __exit__(self_inner, exc_type, exc, tb):
                pass

        placeholder.container.return_value = ContainerCtx()
        placeholder.empty = MagicMock()
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

    @staticmethod
    def spinner(text):
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
            def update(self, label=None, state=None, expanded=None):
                pass
        return StatusContext()

    @staticmethod
    def tabs(labels):
        """Mock st.tabs() - returns list of tab context managers"""
        class TabContext:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def markdown(self, text):
                pass
            def write(self, text):
                pass
        return [TabContext() for _ in labels]

    @staticmethod
    def plotly_chart(fig, use_container_width=True, key=None, **kwargs):
        """Mock st.plotly_chart()"""
        pass

    @staticmethod
    def container():
        """Mock st.container() context manager"""
        class ContainerContext:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def markdown(self, text, **kwargs):
                pass
            def write(self, *args):
                pass
            def metric(self, label, value, delta=None):
                pass
        return ContainerContext()

    @staticmethod
    def write(*args, **kwargs):
        """Mock st.write()"""
        pass

    @staticmethod
    def button(label, key=None, help=None, on_click=None, disabled=False):
        """Mock st.button() - always returns False in tests"""
        return False

    @staticmethod
    def selectbox(label, options, index=0, key=None, help=None):
        """Mock st.selectbox() - returns first option"""
        return options[index] if options else None

    @staticmethod
    def number_input(label, min_value=None, max_value=None, value=None, key=None):
        """Mock st.number_input() - returns value or min_value"""
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
    # Reset session state
    MockStreamlit.session_state.clear()

    # Reset call tracking
    MockStreamlit.markdown_called = False
    MockStreamlit.markdown_calls = []

    yield MockStreamlit

    # Cleanup
    MockStreamlit.session_state.clear()
    MockStreamlit.markdown_called = False
    MockStreamlit.markdown_calls = []
