"""
Data Lazy Loading Utilities
Load material databases, code tables, and large datasets on demand.
"""
from typing import Any, Dict, List, Optional
import streamlit as st


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_material_database() -> Dict[str, Any]:
    """
    Load material properties database only when needed.
    Cached to avoid repeated loads.

    Returns:
        Dict of material properties
    """
    # In real implementation, this would load from file/database
    materials = {
        "concrete": {
            "M20": {"fck": 20, "density": 25},
            "M25": {"fck": 25, "density": 25},
            "M30": {"fck": 30, "density": 25},
            "M35": {"fck": 35, "density": 25},
            "M40": {"fck": 40, "density": 25},
        },
        "steel": {
            "Fe415": {"fy": 415, "Es": 200000},
            "Fe500": {"fy": 500, "Es": 200000},
            "Fe550": {"fy": 550, "Es": 200000},
        }
    }
    return materials


@st.cache_data(ttl=3600)
def load_code_tables() -> Dict[str, Any]:
    """
    Load IS 456 code tables on demand.
    Tables for design constants, coefficients, etc.

    Returns:
        Dict of code tables
    """
    tables = {
        "modification_factors": {
            "short_term": 1.0,
            "long_term": 0.8,
        },
        "exposure_conditions": {
            "mild": {"min_cover": 20, "max_wcr": 0.55},
            "moderate": {"min_cover": 30, "max_wcr": 0.50},
            "severe": {"min_cover": 45, "max_wcr": 0.45},
            "very_severe": {"min_cover": 50, "max_wcr": 0.40},
            "extreme": {"min_cover": 75, "max_wcr": 0.40},
        },
        "bar_sizes": [8, 10, 12, 16, 20, 25, 32, 40],
    }
    return tables


@st.cache_data(ttl=1800)  # 30 min cache
def load_design_examples() -> List[Dict[str, Any]]:
    """
    Load design examples/templates lazily.

    Returns:
        List of example designs
    """
    examples = [
        {
            "name": "Typical Simply Supported Beam",
            "span_m": 6.0,
            "width_mm": 300,
            "depth_mm": 500,
            "fck": 25,
            "fy": 415,
        },
        {
            "name": "Heavy Load Beam",
            "span_m": 8.0,
            "width_mm": 400,
            "depth_mm": 700,
            "fck": 30,
            "fy": 500,
        },
    ]
    return examples


@st.cache_data
def load_validation_rules() -> Dict[str, Any]:
    """
    Load input validation rules lazily.

    Returns:
        Dict of validation rules
    """
    rules = {
        "span": {"min": 1.0, "max": 20.0, "unit": "m"},
        "width": {"min": 150, "max": 1000, "unit": "mm"},
        "depth": {"min": 200, "max": 2000, "unit": "mm"},
        "fck": {"allowed": [20, 25, 30, 35, 40, 45, 50]},
        "fy": {"allowed": [415, 500, 550]},
    }
    return rules


class DataManager:
    """Centralized data loading manager with lazy loading."""

    @staticmethod
    def get_materials() -> Dict[str, Any]:
        """Get materials (lazy loaded)."""
        return load_material_database()

    @staticmethod
    def get_code_tables() -> Dict[str, Any]:
        """Get code tables (lazy loaded)."""
        return load_code_tables()

    @staticmethod
    def get_examples() -> List[Dict[str, Any]]:
        """Get design examples (lazy loaded)."""
        return load_design_examples()

    @staticmethod
    def get_validation_rules() -> Dict[str, Any]:
        """Get validation rules (lazy loaded)."""
        return load_validation_rules()

    @staticmethod
    def preload_critical_data() -> None:
        """
        Preload critical data in background.
        Call at app startup for better perceived performance.
        """
        # Load in background (cached)
        load_material_database()
        load_code_tables()
        load_validation_rules()

    @staticmethod
    def clear_all_caches() -> None:
        """Clear all data caches."""
        load_material_database.clear()
        load_code_tables.clear()
        load_design_examples.clear()
        load_validation_rules.clear()


def get_material_property(material_type: str, grade: str, property_name: str) -> Optional[Any]:
    """
    Get specific material property with lazy loading.

    Args:
        material_type: 'concrete' or 'steel'
        grade: Material grade (e.g., 'M25', 'Fe415')
        property_name: Property to retrieve (e.g., 'fck', 'fy')

    Returns:
        Property value or None if not found
    """
    materials = load_material_database()

    if material_type not in materials:
        return None

    if grade not in materials[material_type]:
        return None

    return materials[material_type][grade].get(property_name)


def get_code_value(table_name: str, key: str) -> Optional[Any]:
    """
    Get value from code table with lazy loading.

    Args:
        table_name: Name of the code table
        key: Key to lookup

    Returns:
        Value or None if not found
    """
    tables = load_code_tables()

    if table_name not in tables:
        return None

    return tables[table_name].get(key)
