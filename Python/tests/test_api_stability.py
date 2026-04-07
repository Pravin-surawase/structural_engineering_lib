"""EA-9: Wheel API stability tests.

Verify that every name in structural_lib.__all__ is importable,
key functions are callable, and lazy-loaded modules resolve correctly.
"""

import pytest

import structural_lib

pytestmark = pytest.mark.repo_only


class TestAllExportsImportable:
    """Every name in __all__ must be accessible via getattr."""

    def test_all_exports_importable(self):
        """Every name in __all__ should be a non-None attribute."""
        missing = []
        for name in structural_lib.__all__:
            try:
                obj = getattr(structural_lib, name)
                if obj is None and name not in ("dxf_export", "reports"):
                    # dxf_export/reports can be None if optional deps missing
                    missing.append(f"{name} resolved to None")
            except AttributeError:
                missing.append(f"{name} raised AttributeError")
        assert (
            not missing
        ), f"{len(missing)} __all__ export(s) not importable:\n" + "\n".join(
            f"  - {m}" for m in missing
        )

    def test_all_count_minimum(self):
        """__all__ must have at least 90 entries (current: 104)."""
        assert len(structural_lib.__all__) >= 90, (
            f"Expected >= 90 exports in __all__, got {len(structural_lib.__all__)}. "
            "Did someone accidentally trim the public API?"
        )


class TestKeyFunctionsCallable:
    """Core API functions must be callable (not just importable)."""

    @pytest.mark.parametrize(
        "func_name",
        [
            "design_beam_is456",
            "detail_beam_is456",
            "design_and_detail_beam_is456",
            "check_beam_is456",
            "design_from_input",
            "compute_detailing",
            "build_detailing_input",
            "compute_bbs",
            "export_bbs",
            "compute_dxf",
            "compute_report",
            "compute_critical",
            "compute_hash",
            "verify_calculation",
            "generate_calculation_report",
            "create_calculation_certificate",
            "validate_job_spec",
            "validate_design_results",
            "check_beam_ductility",
            "check_beam_slenderness",
            "check_deflection_span_depth",
            "check_crack_width",
            "check_compliance_report",
            "enhanced_shear_strength_is456",
            "optimize_beam_cost",
            "suggest_beam_design_improvements",
            "smart_analyze_design",
            "design_torsion",
            "calculate_equivalent_shear",
            "calculate_equivalent_moment",
            "calculate_torsion_shear_stress",
            "calculate_torsion_stirrup_area",
            "calculate_longitudinal_torsion_steel",
            "validate_etabs_csv",
            "load_etabs_csv",
            "normalize_etabs_forces",
            "create_job_from_etabs",
            "create_jobs_from_etabs_csv",
            "compute_bmd_sfd",
            "compute_rebar_positions",
            "compute_stirrup_path",
            "compute_stirrup_positions",
            "compute_beam_outline",
            "beam_to_3d_geometry",
            "get_library_version",
            "calculate_additional_moment_is456",
            "calculate_effective_length_is456",
            "classify_column_is456",
            "min_eccentricity_is456",
            "design_column_axial_is456",
            "design_column_is456",
            "design_long_column_is456",
            "design_short_column_uniaxial_is456",
            "pm_interaction_curve_is456",
            "biaxial_bending_check_is456",
            "check_helical_reinforcement_is456",
            "detail_column_is456",
            "check_column_ductility_is13920",
        ],
    )
    def test_function_is_callable(self, func_name):
        """Each public function must be callable."""
        obj = getattr(structural_lib, func_name)
        assert callable(obj), f"{func_name} is not callable (type={type(obj).__name__})"


class TestKeyClassesInstantiable:
    """Core dataclasses / named types must be classes."""

    @pytest.mark.parametrize(
        "cls_name",
        [
            "BeamInput",
            "BeamGeometryInput",
            "MaterialsInput",
            "LoadsInput",
            "LoadCaseInput",
            "DetailingConfigInput",
            "ComplianceCaseResult",
            "ComplianceReport",
            "DesignAndDetailResult",
            "AuditTrail",
            "AuditLogEntry",
            "CalculationHash",
            "CalculationReport",
            "ProjectInfo",
            "InputSection",
            "ResultSection",
            "TorsionResult",
            "ETABSForceRow",
            "ETABSEnvelopeResult",
            "LoadDefinition",
            "CriticalPoint",
            "LoadDiagramResult",
            "Point3D",
            "BeamGeometry",
            "FrameType",
            "DesignDefaults",
            "RebarSegment",
            "RebarPath",
            "StirrupLoop",
            "Beam3DGeometry",
        ],
    )
    def test_type_is_class(self, cls_name):
        """Each exported type must be a class (callable for construction)."""
        obj = getattr(structural_lib, cls_name)
        assert isinstance(
            obj, type
        ), f"{cls_name} is not a type/class (got {type(obj).__name__})"


class TestLazyModulesLoad:
    """Lazy-loaded modules must resolve on first access."""

    @pytest.mark.parametrize(
        "mod_name",
        [
            "adapters",
            "etabs_import",
            "batch",
            "costing",
            "testing_strategies",
            "audit",
            "serialization",
        ],
    )
    def test_lazy_module_loads(self, mod_name):
        """Lazy module must be importable via getattr."""
        mod = getattr(structural_lib, mod_name)
        assert mod is not None, f"Lazy module {mod_name!r} resolved to None"
        # Must be an actual module object
        from types import ModuleType

        assert isinstance(
            mod, ModuleType
        ), f"{mod_name} is not a module (type={type(mod).__name__})"


class TestOptionalModules:
    """Optional modules (dxf_export, reports) must not crash on access."""

    def test_dxf_export_accessible(self):
        """dxf_export should be a module or None (if ezdxf missing)."""
        from types import ModuleType

        obj = structural_lib.dxf_export
        assert obj is None or isinstance(obj, ModuleType)

    def test_reports_accessible(self):
        """reports should be a module or None (if jinja2 missing)."""
        from types import ModuleType

        obj = structural_lib.reports
        assert obj is None or isinstance(obj, ModuleType)


class TestEagerModulesLoaded:
    """Eagerly-imported sub-modules must be present."""

    @pytest.mark.parametrize(
        "mod_name",
        [
            "api",
            "compliance",
            "detailing",
            "flexure",
            "imports",
            "inputs",
            "models",
            "rebar",
            "result_base",
            "serviceability",
            "shear",
            "types",
        ],
    )
    def test_eager_module_loaded(self, mod_name):
        """Eagerly-imported module must be accessible."""
        from types import ModuleType

        obj = getattr(structural_lib, mod_name)
        assert isinstance(
            obj, ModuleType
        ), f"{mod_name} is not a module (type={type(obj).__name__})"
