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

    # Track if markdown was called (for accessibility tests)
    markdown_called = False

    @staticmethod
    def columns(num_cols):
        """Mock st.columns() - returns list of mock column objects"""
        # Handle both int and list[int] arguments
        if isinstance(num_cols, list):
            count = len(num_cols)
        else:
            count = num_cols
        return [MagicMock() for _ in range(count)]

    @staticmethod
    def info(msg):
        """Mock st.info()"""
        pass

    @staticmethod
    def button(label, key=None, **kwargs):
        """Mock st.button() - returns False by default"""
        return False

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
    """Provide MockStreamlit instance with reset state."""
    MockStreamlit.markdown_called = False
    MockStreamlit.session_state.clear()
    yield MockStreamlit
    MockStreamlit.markdown_called = False
    MockStreamlit.session_state.clear()
