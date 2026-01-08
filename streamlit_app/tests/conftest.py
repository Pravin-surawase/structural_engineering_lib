"""
Test Configuration and Fixtures
================================

Common fixtures and mocks for Streamlit component testing.

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-002
"""

import pytest
import sys
from unittest.mock import MagicMock

# Mock Streamlit before imports
sys.modules['streamlit'] = MagicMock()
