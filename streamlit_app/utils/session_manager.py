"""
Session State Manager for Streamlit UI
========================================

Manages session state persistence across page navigation and browser refreshes.

Features:
- Persistent state management
- Cross-page data sharing
- Input history tracking
- Recent designs cache
- State validation
- State export/import
- Browser storage integration

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-010
"""

import streamlit as st
import json
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# State Data Classes
# =============================================================================

@dataclass
class BeamInputs:
    """Beam design input parameters"""
    span_mm: float = 5000.0
    b_mm: float = 300.0
    d_mm: float = 450.0
    D_mm: float = 500.0
    fck_mpa: float = 25.0
    fy_mpa: float = 500.0
    mu_knm: float = 120.0
    vu_kn: float = 80.0
    cover_mm: float = 30.0
    timestamp: str = ""

    def __post_init__(self):
        """Set timestamp if not provided"""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BeamInputs':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class DesignResult:
    """Design analysis result"""
    inputs: BeamInputs
    ast_mm2: float
    ast_provided_mm2: float
    num_bars: int
    bar_diameter_mm: int
    stirrup_diameter_mm: int
    stirrup_spacing_mm: int
    utilization_pct: float
    status: str  # "PASS" or "FAIL"
    compliance_checks: Dict[str, bool]
    cost_per_meter: float
    timestamp: str = ""

    def __post_init__(self):
        """Set timestamp if not provided"""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'inputs': self.inputs.to_dict(),
            'ast_mm2': self.ast_mm2,
            'ast_provided_mm2': self.ast_provided_mm2,
            'num_bars': self.num_bars,
            'bar_diameter_mm': self.bar_diameter_mm,
            'stirrup_diameter_mm': self.stirrup_diameter_mm,
            'stirrup_spacing_mm': self.stirrup_spacing_mm,
            'utilization_pct': self.utilization_pct,
            'status': self.status,
            'compliance_checks': self.compliance_checks,
            'cost_per_meter': self.cost_per_meter,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DesignResult':
        """Create from dictionary"""
        inputs = BeamInputs.from_dict(data['inputs'])
        return cls(
            inputs=inputs,
            ast_mm2=data['ast_mm2'],
            ast_provided_mm2=data['ast_provided_mm2'],
            num_bars=data['num_bars'],
            bar_diameter_mm=data['bar_diameter_mm'],
            stirrup_diameter_mm=data['stirrup_diameter_mm'],
            stirrup_spacing_mm=data['stirrup_spacing_mm'],
            utilization_pct=data['utilization_pct'],
            status=data['status'],
            compliance_checks=data['compliance_checks'],
            cost_per_meter=data['cost_per_meter'],
            timestamp=data.get('timestamp', '')
        )


# =============================================================================
# Session State Keys (Constants)
# =============================================================================

class StateKeys:
    """Session state key constants"""
    # Current inputs
    CURRENT_INPUTS = "current_inputs"

    # Current result
    CURRENT_RESULT = "current_result"

    # History
    INPUT_HISTORY = "input_history"
    RESULT_HISTORY = "result_history"

    # UI state
    SELECTED_TAB = "selected_tab"
    SHOW_ADVANCED = "show_advanced"
    COMPARE_MODE = "compare_mode"

    # Cache
    DESIGN_CACHE = "design_cache"

    # Settings
    USER_PREFERENCES = "user_preferences"


# =============================================================================
# Session State Manager
# =============================================================================

class SessionStateManager:
    """
    Manages Streamlit session state.

    Features:
    - Initialize state on first load
    - Get/set state values safely
    - Persist inputs across pages
    - Track input/result history
    - Cache expensive computations
    - Export/import state
    """

    @staticmethod
    def initialize() -> None:
        """Initialize session state with default values."""
        # Current inputs
        if StateKeys.CURRENT_INPUTS not in st.session_state:
            st.session_state[StateKeys.CURRENT_INPUTS] = BeamInputs()

        # Current result
        if StateKeys.CURRENT_RESULT not in st.session_state:
            st.session_state[StateKeys.CURRENT_RESULT] = None

        # History (last 10 designs)
        if StateKeys.INPUT_HISTORY not in st.session_state:
            st.session_state[StateKeys.INPUT_HISTORY] = []

        if StateKeys.RESULT_HISTORY not in st.session_state:
            st.session_state[StateKeys.RESULT_HISTORY] = []

        # UI state
        if StateKeys.SELECTED_TAB not in st.session_state:
            st.session_state[StateKeys.SELECTED_TAB] = 0

        if StateKeys.SHOW_ADVANCED not in st.session_state:
            st.session_state[StateKeys.SHOW_ADVANCED] = False

        if StateKeys.COMPARE_MODE not in st.session_state:
            st.session_state[StateKeys.COMPARE_MODE] = False

        # Cache (keyed by input hash)
        if StateKeys.DESIGN_CACHE not in st.session_state:
            st.session_state[StateKeys.DESIGN_CACHE] = {}

        # User preferences
        if StateKeys.USER_PREFERENCES not in st.session_state:
            st.session_state[StateKeys.USER_PREFERENCES] = {
                'theme': 'light',
                'decimal_places': 2,
                'unit_system': 'SI',
                'show_formulas': True,
                'auto_save': True
            }

        logger.info("Session state initialized")

    @staticmethod
    def get_current_inputs() -> BeamInputs:
        """Get current beam inputs"""
        SessionStateManager.initialize()
        return st.session_state[StateKeys.CURRENT_INPUTS]

    @staticmethod
    def set_current_inputs(inputs: BeamInputs) -> None:
        """Set current beam inputs."""
        SessionStateManager.initialize()
        st.session_state[StateKeys.CURRENT_INPUTS] = inputs
        logger.debug(f"Updated current inputs: {inputs}")

    @staticmethod
    def get_current_result() -> Optional[DesignResult]:
        """Get current design result."""
        SessionStateManager.initialize()
        return st.session_state[StateKeys.CURRENT_RESULT]

    @staticmethod
    def set_current_result(result: DesignResult) -> None:
        """Set current design result."""
        SessionStateManager.initialize()
        st.session_state[StateKeys.CURRENT_RESULT] = result
        logger.debug(f"Updated current result: status={result.status}, util={result.utilization_pct}%")

    @staticmethod
    def add_to_history(inputs: BeamInputs, result: DesignResult) -> None:
        """Add design to history.

        Args:
            inputs: Beam inputs
            result: Design result
        """
        SessionStateManager.initialize()

        # Add to input history
        input_history = st.session_state[StateKeys.INPUT_HISTORY]
        input_history.append(inputs)

        # Keep only last 10
        if len(input_history) > 10:
            st.session_state[StateKeys.INPUT_HISTORY] = input_history[-10:]

        # Add to result history
        result_history = st.session_state[StateKeys.RESULT_HISTORY]
        result_history.append(result)

        # Keep only last 10
        if len(result_history) > 10:
            st.session_state[StateKeys.RESULT_HISTORY] = result_history[-10:]

        logger.info(f"Added design to history (total: {len(st.session_state[StateKeys.INPUT_HISTORY])})")

    @staticmethod
    def get_history() -> List[DesignResult]:
        """Get design history."""
        SessionStateManager.initialize()
        return st.session_state[StateKeys.RESULT_HISTORY]

    @staticmethod
    def clear_history() -> None:
        """Clear design history."""
        SessionStateManager.initialize()
        st.session_state[StateKeys.INPUT_HISTORY] = []
        st.session_state[StateKeys.RESULT_HISTORY] = []
        logger.info("Cleared design history")

    @staticmethod
    def cache_design(inputs: BeamInputs, result: DesignResult) -> None:
        """Cache design result.

        Args:
            inputs: Beam inputs (used as cache key)
            result: Design result to cache
        """
        SessionStateManager.initialize()

        # Create cache key from inputs
        key = SessionStateManager._input_hash(inputs)

        # Store in cache
        cache = st.session_state[StateKeys.DESIGN_CACHE]
        cache[key] = result

        # Limit cache size (keep last 20)
        if len(cache) > 20:
            # Remove oldest (first) entry
            oldest_key = next(iter(cache))
            del cache[oldest_key]

        logger.debug(f"Cached design result (cache size: {len(cache)})")

    @staticmethod
    def get_cached_design(inputs: BeamInputs) -> Optional[DesignResult]:
        """
        Get cached design result.

        Args:
            inputs: Beam inputs to look up

        Returns:
            Cached result if found, None otherwise
        """
        SessionStateManager.initialize()

        key = SessionStateManager._input_hash(inputs)
        cache = st.session_state[StateKeys.DESIGN_CACHE]

        if key in cache:
            logger.debug("Cache hit")
            return cache[key]

        logger.debug("Cache miss")
        return None

    @staticmethod
    def _input_hash(inputs: BeamInputs) -> str:
        """
        Create hash key from inputs.

        Args:
            inputs: Beam inputs

        Returns:
            Hash string
        """
        # Round to 2 decimal places to avoid precision issues
        return (
            f"{inputs.span_mm:.1f}_{inputs.b_mm:.1f}_{inputs.d_mm:.1f}_"
            f"{inputs.D_mm:.1f}_{inputs.fck_mpa:.1f}_{inputs.fy_mpa:.1f}_"
            f"{inputs.mu_knm:.2f}_{inputs.vu_kn:.2f}"
        )

    @staticmethod
    def export_state() -> Dict[str, Any]:
        """
        Export session state to dictionary.

        Returns:
            Dictionary with all exportable state
        """
        SessionStateManager.initialize()

        return {
            'current_inputs': st.session_state[StateKeys.CURRENT_INPUTS].to_dict(),
            'current_result': st.session_state[StateKeys.CURRENT_RESULT].to_dict()
                             if st.session_state[StateKeys.CURRENT_RESULT] else None,
            'input_history': [inp.to_dict() for inp in st.session_state[StateKeys.INPUT_HISTORY]],
            'result_history': [res.to_dict() for res in st.session_state[StateKeys.RESULT_HISTORY]],
            'preferences': st.session_state[StateKeys.USER_PREFERENCES],
            'export_timestamp': datetime.now().isoformat()
        }

    @staticmethod
    def import_state(state_dict: Dict[str, Any]) -> None:
        """Import session state from dictionary.

        Args:
            state_dict: Dictionary with state data
        """
        try:
            # Current inputs
            if 'current_inputs' in state_dict:
                st.session_state[StateKeys.CURRENT_INPUTS] = BeamInputs.from_dict(
                    state_dict['current_inputs']
                )

            # Current result
            if 'current_result' in state_dict and state_dict['current_result']:
                st.session_state[StateKeys.CURRENT_RESULT] = DesignResult.from_dict(
                    state_dict['current_result']
                )

            # History
            if 'input_history' in state_dict:
                st.session_state[StateKeys.INPUT_HISTORY] = [
                    BeamInputs.from_dict(inp) for inp in state_dict['input_history']
                ]

            if 'result_history' in state_dict:
                st.session_state[StateKeys.RESULT_HISTORY] = [
                    DesignResult.from_dict(res) for res in state_dict['result_history']
                ]

            # Preferences
            # Initialize preferences if needed
            if StateKeys.USER_PREFERENCES not in st.session_state:
                st.session_state[StateKeys.USER_PREFERENCES] = {}

            if "preferences" in state_dict:
                st.session_state[StateKeys.USER_PREFERENCES].update(
                    state_dict['preferences']
                )

            logger.info("Session state imported successfully")

        except Exception as e:
            logger.error(f"Failed to import state: {e}")
            raise

    @staticmethod
    def get_preference(key: str, default: Any = None) -> Any:
        """
        Get user preference.

        Args:
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value
        """
        SessionStateManager.initialize()
        return st.session_state[StateKeys.USER_PREFERENCES].get(key, default)

    @staticmethod
    def set_preference(key: str, value: Any) -> None:
        """Set user preference.

        Args:
            key: Preference key
            value: Preference value
        """
        SessionStateManager.initialize()
        st.session_state[StateKeys.USER_PREFERENCES][key] = value
        logger.debug(f"Updated preference: {key}={value}")

    @staticmethod
    def reset_to_defaults() -> None:
        """Reset all state to default values."""
        st.session_state.clear()
        SessionStateManager.initialize()
        logger.info("Session state reset to defaults")

    # =========================================================================
    # IMPL-006 Phase 3: State Optimization Enhancements
    # =========================================================================

    @staticmethod
    def minimize_state() -> None:
        """Remove non-essential state to reduce memory footprint.

        Keeps only current inputs, result, and recent history.
        """
        SessionStateManager.initialize()

        # Keep only last 5 in history (instead of 10)
        if len(st.session_state[StateKeys.INPUT_HISTORY]) > 5:
            st.session_state[StateKeys.INPUT_HISTORY] = st.session_state[StateKeys.INPUT_HISTORY][-5:]

        if len(st.session_state[StateKeys.RESULT_HISTORY]) > 5:
            st.session_state[StateKeys.RESULT_HISTORY] = st.session_state[StateKeys.RESULT_HISTORY][-5:]

        # Clear old cache entries (keep last 10)
        cache = st.session_state[StateKeys.DESIGN_CACHE]
        if len(cache) > 10:
            keys_to_keep = list(cache.keys())[-10:]
            st.session_state[StateKeys.DESIGN_CACHE] = {k: cache[k] for k in keys_to_keep}

        logger.info("State minimized - reduced memory footprint")

    @staticmethod
    def track_state_diff(old_inputs: BeamInputs, new_inputs: BeamInputs) -> Dict[str, Any]:
        """
        Track differences between input states.

        Args:
            old_inputs: Previous inputs
            new_inputs: New inputs

        Returns:
            Dictionary of changed fields
        """
        diff = {}

        for field in ['span_mm', 'b_mm', 'd_mm', 'D_mm', 'fck_mpa', 'fy_mpa', 'mu_knm', 'vu_kn', 'cover_mm']:
            old_val = getattr(old_inputs, field)
            new_val = getattr(new_inputs, field)

            if old_val != new_val:
                diff[field] = {
                    'old': old_val,
                    'new': new_val,
                    'change': new_val - old_val
                }

        return diff

    @staticmethod
    def clear_stale_state(max_age_minutes: int = 30) -> None:
        """Clear state that hasn't been accessed recently.

        Args:
            max_age_minutes: Maximum age for state entries
        """
        SessionStateManager.initialize()

        cutoff = datetime.now() - timedelta(minutes=max_age_minutes)

        # Clear stale history entries
        result_history = st.session_state[StateKeys.RESULT_HISTORY]
        fresh_results = []

        for result in result_history:
            try:
                result_time = datetime.fromisoformat(result.timestamp)
                if result_time > cutoff:
                    fresh_results.append(result)
            except (ValueError, AttributeError):
                # Keep if timestamp invalid (safer)
                fresh_results.append(result)

        if len(fresh_results) < len(result_history):
            st.session_state[StateKeys.RESULT_HISTORY] = fresh_results
            logger.info(f"Cleared {len(result_history) - len(fresh_results)} stale results")

    @staticmethod
    def compress_large_objects() -> None:
        """Compress large objects in state to reduce memory.

        Currently a placeholder for future implementation.
        """
        # In future: could use pickle + gzip for large objects
        # For now, just log state size
        SessionStateManager.initialize()

        cache_size = len(st.session_state.get(StateKeys.DESIGN_CACHE, {}))
        history_size = len(st.session_state.get(StateKeys.RESULT_HISTORY, []))

        logger.debug(f"State size - Cache: {cache_size}, History: {history_size}")

    @staticmethod
    def get_state_metrics() -> Dict[str, int]:
        """
        Get metrics about current state size.

        Returns:
            Dictionary with state metrics
        """
        SessionStateManager.initialize()

        return {
            'total_keys': len(st.session_state),
            'cache_entries': len(st.session_state.get(StateKeys.DESIGN_CACHE, {})),
            'history_entries': len(st.session_state.get(StateKeys.RESULT_HISTORY, [])),
            'input_history_entries': len(st.session_state.get(StateKeys.INPUT_HISTORY, [])),
        }

    @staticmethod
    def optimize_state_on_interval(interval_seconds: int = 300) -> None:
        """Periodically optimize state (call every 5 minutes).

        Args:
            interval_seconds: Optimization interval
        """
        # Check if enough time has passed
        last_optimize_key = '_last_state_optimize'

        if last_optimize_key not in st.session_state:
            st.session_state[last_optimize_key] = datetime.now()

        time_since_last = (datetime.now() - st.session_state[last_optimize_key]).total_seconds()

        if time_since_last >= interval_seconds:
            SessionStateManager.minimize_state()
            SessionStateManager.clear_stale_state()
            SessionStateManager.compress_large_objects()
            st.session_state[last_optimize_key] = datetime.now()
            logger.info("State optimization completed")


# =============================================================================
# Helper Functions
# =============================================================================

def load_last_design() -> Optional[BeamInputs]:
    """
    Load last design from history.

    Returns:
        Last beam inputs or None if history empty
    """
    history = SessionStateManager.get_history()
    if history:
        return history[-1].inputs
    return None


def save_design_to_file(filepath: str) -> None:
    """Save current design to JSON file.

    Args:
        filepath: Path to save file
    """
    state = SessionStateManager.export_state()
    with open(filepath, 'w') as f:
        json.dump(state, f, indent=2)
    logger.info(f"Design saved to {filepath}")


def load_design_from_file(filepath: str) -> None:
    """Load design from JSON file.

    Args:
        filepath: Path to load file
    """
    with open(filepath, 'r') as f:
        state = json.load(f)
    SessionStateManager.import_state(state)
    logger.info(f"Design loaded from {filepath}")


def compare_designs(result1: DesignResult, result2: DesignResult) -> Dict[str, Any]:
    """
    Compare two design results.

    Args:
        result1: First design result
        result2: Second design result

    Returns:
        Dictionary with comparison metrics
    """
    # Safe division for cost savings calculation (denominator validated)
    denominator = result1.cost_per_meter
    cost_savings_pct = (
        ((result1.cost_per_meter - result2.cost_per_meter) / denominator) * 100
    ) if denominator > 0 else 0.0
    return {
        'utilization_diff': result2.utilization_pct - result1.utilization_pct,
        'cost_diff': result2.cost_per_meter - result1.cost_per_meter,
        'cost_savings_pct': cost_savings_pct,
        'steel_area_diff': result2.ast_provided_mm2 - result1.ast_provided_mm2,
        'better_utilization': result2.utilization_pct > result1.utilization_pct,
        'more_economical': result2.cost_per_meter < result1.cost_per_meter
    }


def format_design_summary(result: DesignResult) -> str:
    """
    Format design result as text summary.

    Args:
        result: Design result

    Returns:
        Formatted text summary
    """
    inputs = result.inputs

    summary = f"""
    Design Summary
    ==============

    Geometry:
      Span: {inputs.span_mm:,.0f} mm
      Width: {inputs.b_mm:,.0f} mm
      Depth: {inputs.D_mm:,.0f} mm (d = {inputs.d_mm:,.0f} mm)

    Materials:
      Concrete: M{int(inputs.fck_mpa)}
      Steel: Fe{int(inputs.fy_mpa)}

    Loading:
      Moment: {inputs.mu_knm:,.1f} kNm
      Shear: {inputs.vu_kn:,.1f} kN

    Design:
      Main Steel: {result.num_bars}-{result.bar_diameter_mm}mm bars ({result.ast_provided_mm2:,.0f} mm²)
      Stirrups: {result.stirrup_diameter_mm}mm @ {result.stirrup_spacing_mm}mm c/c
      Utilization: {result.utilization_pct:.1f}%
      Status: {result.status}
      Cost: ₹{result.cost_per_meter:,.2f}/m

    Timestamp: {result.timestamp}
    """

    return summary.strip()
