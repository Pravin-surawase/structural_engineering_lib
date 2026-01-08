"""
Test Configuration and Fixtures
================================

Common fixtures and mocks for Streamlit component testing.

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-002
"""

import pytest
import sys
from unittest.mock import MagicMock, Mock


class MockStreamlit:
    """Enhanced Streamlit mock for testing"""

    # Mock session_state as a dictionary
    session_state = {}


    # Mock session_state as a dictionary
    session_state = {}


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
    def markdown(text):
        """Mock st.markdown()"""
        pass

    @staticmethod
    def caption(text):
        """Mock st.caption()"""
        pass

    @staticmethod
    def metric(label, value, delta=None, delta_color="normal"):
        """Mock st.metric()"""
        pass

    class cache_data:
        """Mock st.cache_data decorator that works with or without parentheses"""
        def __init__(self, func=None, **kwargs):
            """
            Allow both:
            @st.cache_data        # Called directly
            @st.cache_data()      # Called with parentheses
            """
            self.func = func

        def __call__(self, *args, **kwargs):
            """
            If initialized with a function, act as decorator
            If initialized without, return self to act as decorator factory
            """
            if self.func is not None:
                # Direct decoration: @st.cache_data
                return self.func(*args, **kwargs)
            else:
                # Decorator factory: @st.cache_data()
                # First call returns decorator, second call is the function
                if len(args) == 1 and callable(args[0]) and not kwargs:
                    # This is the function being decorated
                    return args[0]
                else:
                    # This is a call to the cached function - shouldn't happen in tests
                    raise TypeError(f"Unexpected call to cache_data: args={args}, kwargs={kwargs}")

        @staticmethod
        def clear():
            """Mock cache clear"""
            pass


# Replace streamlit module with enhanced mock
sys.modules['streamlit'] = MockStreamlit()
