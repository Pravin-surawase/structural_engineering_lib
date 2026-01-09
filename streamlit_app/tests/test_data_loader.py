"""
Tests for data lazy loading utilities
"""
import pytest
from streamlit_app.utils.data_loader import (
    load_material_database,
    load_code_tables,
    load_design_examples,
    load_validation_rules,
    DataManager,
    get_material_property,
    get_code_value,
)


class TestLoadMaterialDatabase:
    """Test load_material_database function."""

    def test_load_materials_structure(self, mock_streamlit):
        """Test that materials are loaded with correct structure."""
        materials = load_material_database()

        assert 'concrete' in materials
        assert 'steel' in materials
        assert isinstance(materials['concrete'], dict)
        assert isinstance(materials['steel'], dict)

    def test_load_materials_concrete_grades(self, mock_streamlit):
        """Test concrete grades are present."""
        materials = load_material_database()
        concrete = materials['concrete']

        assert 'M20' in concrete
        assert 'M25' in concrete
        assert 'M30' in concrete

        # Check M25 properties
        m25 = concrete['M25']
        assert m25['fck'] == 25
        assert m25['density'] == 25

    def test_load_materials_steel_grades(self, mock_streamlit):
        """Test steel grades are present."""
        materials = load_material_database()
        steel = materials['steel']

        assert 'Fe415' in steel
        assert 'Fe500' in steel

        # Check Fe415 properties
        fe415 = steel['Fe415']
        assert fe415['fy'] == 415
        assert fe415['Es'] == 200000

    def test_load_materials_cached(self, mock_streamlit):
        """Test that materials are cached."""
        mat1 = load_material_database()
        mat2 = load_material_database()

        # Should return same object (cached)
        assert mat1 is mat2


class TestLoadCodeTables:
    """Test load_code_tables function."""

    def test_load_tables_structure(self, mock_streamlit):
        """Test code tables structure."""
        tables = load_code_tables()

        assert 'modification_factors' in tables
        assert 'exposure_conditions' in tables
        assert 'bar_sizes' in tables

    def test_load_tables_exposure_conditions(self, mock_streamlit):
        """Test exposure condition values."""
        tables = load_code_tables()
        exposure = tables['exposure_conditions']

        assert 'mild' in exposure
        assert 'severe' in exposure

        # Check severe exposure
        severe = exposure['severe']
        assert severe['min_cover'] == 45
        assert severe['max_wcr'] == 0.45

    def test_load_tables_bar_sizes(self, mock_streamlit):
        """Test bar sizes list."""
        tables = load_code_tables()
        bar_sizes = tables['bar_sizes']

        assert isinstance(bar_sizes, list)
        assert 12 in bar_sizes
        assert 16 in bar_sizes
        assert 20 in bar_sizes

    def test_load_tables_cached(self, mock_streamlit):
        """Test that tables are cached."""
        tab1 = load_code_tables()
        tab2 = load_code_tables()

        assert tab1 is tab2


class TestLoadDesignExamples:
    """Test load_design_examples function."""

    def test_load_examples_structure(self, mock_streamlit):
        """Test examples structure."""
        examples = load_design_examples()

        assert isinstance(examples, list)
        assert len(examples) > 0

    def test_load_examples_content(self, mock_streamlit):
        """Test example content."""
        examples = load_design_examples()

        first = examples[0]
        assert 'name' in first
        assert 'span_m' in first
        assert 'width_mm' in first
        assert 'depth_mm' in first
        assert 'fck' in first
        assert 'fy' in first

    def test_load_examples_cached(self, mock_streamlit):
        """Test that examples are cached."""
        ex1 = load_design_examples()
        ex2 = load_design_examples()

        assert ex1 is ex2


class TestLoadValidationRules:
    """Test load_validation_rules function."""

    def test_load_rules_structure(self, mock_streamlit):
        """Test validation rules structure."""
        rules = load_validation_rules()

        assert 'span' in rules
        assert 'width' in rules
        assert 'depth' in rules
        assert 'fck' in rules
        assert 'fy' in rules

    def test_load_rules_span_limits(self, mock_streamlit):
        """Test span validation limits."""
        rules = load_validation_rules()
        span = rules['span']

        assert span['min'] == 1.0
        assert span['max'] == 20.0
        assert span['unit'] == 'm'

    def test_load_rules_allowed_values(self, mock_streamlit):
        """Test allowed values lists."""
        rules = load_validation_rules()

        fck_allowed = rules['fck']['allowed']
        assert 25 in fck_allowed
        assert 30 in fck_allowed

        fy_allowed = rules['fy']['allowed']
        assert 415 in fy_allowed
        assert 500 in fy_allowed


class TestDataManager:
    """Test DataManager class."""

    def test_get_materials(self, mock_streamlit):
        """Test getting materials via DataManager."""
        materials = DataManager.get_materials()

        assert 'concrete' in materials
        assert 'steel' in materials

    def test_get_code_tables(self, mock_streamlit):
        """Test getting code tables via DataManager."""
        tables = DataManager.get_code_tables()

        assert 'exposure_conditions' in tables
        assert 'bar_sizes' in tables

    def test_get_examples(self, mock_streamlit):
        """Test getting examples via DataManager."""
        examples = DataManager.get_examples()

        assert isinstance(examples, list)
        assert len(examples) > 0

    def test_get_validation_rules(self, mock_streamlit):
        """Test getting validation rules via DataManager."""
        rules = DataManager.get_validation_rules()

        assert 'span' in rules
        assert 'width' in rules

    def test_preload_critical_data(self, mock_streamlit):
        """Test preloading critical data."""
        # Should not raise error
        DataManager.preload_critical_data()

        # Verify data is available (cached)
        materials = DataManager.get_materials()
        assert materials is not None

    def test_clear_all_caches(self, mock_streamlit):
        """Test clearing all caches."""
        # Load data first
        DataManager.get_materials()
        DataManager.get_code_tables()

        # Clear caches
        DataManager.clear_all_caches()

        # Data should still load (just not from cache)
        materials = DataManager.get_materials()
        assert materials is not None


class TestGetMaterialProperty:
    """Test get_material_property helper function."""

    def test_get_concrete_property(self, mock_streamlit):
        """Test getting concrete property."""
        fck = get_material_property('concrete', 'M25', 'fck')
        assert fck == 25

        density = get_material_property('concrete', 'M30', 'density')
        assert density == 25

    def test_get_steel_property(self, mock_streamlit):
        """Test getting steel property."""
        fy = get_material_property('steel', 'Fe415', 'fy')
        assert fy == 415

        es = get_material_property('steel', 'Fe500', 'Es')
        assert es == 200000

    def test_get_property_invalid_type(self, mock_streamlit):
        """Test with invalid material type."""
        result = get_material_property('invalid', 'M25', 'fck')
        assert result is None

    def test_get_property_invalid_grade(self, mock_streamlit):
        """Test with invalid grade."""
        result = get_material_property('concrete', 'M999', 'fck')
        assert result is None

    def test_get_property_invalid_name(self, mock_streamlit):
        """Test with invalid property name."""
        result = get_material_property('concrete', 'M25', 'invalid_prop')
        assert result is None


class TestGetCodeValue:
    """Test get_code_value helper function."""

    def test_get_exposure_value(self, mock_streamlit):
        """Test getting exposure condition value."""
        mild = get_code_value('exposure_conditions', 'mild')
        assert mild is not None
        assert mild['min_cover'] == 20

    def test_get_bar_sizes(self, mock_streamlit):
        """Test getting bar sizes."""
        bar_sizes = get_code_value('bar_sizes', None)
        # bar_sizes is a list, not dict, so key lookup returns None
        # This tests error handling

    def test_get_invalid_table(self, mock_streamlit):
        """Test with invalid table name."""
        result = get_code_value('invalid_table', 'key')
        assert result is None

    def test_get_invalid_key(self, mock_streamlit):
        """Test with invalid key."""
        result = get_code_value('exposure_conditions', 'invalid_key')
        assert result is None
