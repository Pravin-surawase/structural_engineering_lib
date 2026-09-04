import pytest

from structural_lib.beam import (
    BarPosition,
    CalculatedDeflectionBasis,
    CrackWidthCheckRequest,
    CrackWidthLimitRequest,
    DeflectionCheckRequest,
    DeflectionCriterion,
    DeflectionLimitRequest,
    DeflectionMethod,
    DeflectionScreeningBasis,
    ExposureClass,
    Face,
    LimitSource,
    SupportCondition,
    check_crack_width,
    check_deflection,
    crack_width_limit,
    deflection_limit,
)


def test_deflection_limits_distinguish_total_and_after_finishes() -> None:
    total = deflection_limit(
        DeflectionLimitRequest("IS456-WP04", 6000, DeflectionCriterion.TOTAL_FINAL)
    )
    finishes = deflection_limit(
        DeflectionLimitRequest("IS456-WP04", 6000, DeflectionCriterion.AFTER_FINISHES)
    )

    assert total.outputs["limit_mm"] == pytest.approx(24)
    assert finishes.outputs["limit_mm"] == pytest.approx(6000 / 350)


def test_limit_override_requires_one_explicit_source() -> None:
    result = deflection_limit(
        DeflectionLimitRequest(
            "IS456-WP04",
            6000,
            DeflectionCriterion.TOTAL_FINAL,
            LimitSource.CODE,
            project_limit_mm=20,
        )
    )

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "INPUT.CONFLICT"


def test_crack_limit_uses_exposure_and_harm_classification() -> None:
    mild = crack_width_limit(
        CrackWidthLimitRequest("IS456-WP04", ExposureClass.MILD, False)
    )
    weather = crack_width_limit(
        CrackWidthLimitRequest("IS456-WP04", ExposureClass.MODERATE, False)
    )
    aggressive = crack_width_limit(
        CrackWidthLimitRequest("IS456-WP04", ExposureClass.VERY_SEVERE, True)
    )

    assert mild.outputs["limit_mm"] == pytest.approx(0.3)
    assert weather.outputs["limit_mm"] == pytest.approx(0.2)
    assert aggressive.outputs["limit_mm"] == pytest.approx(0.1)


def test_crack_limit_override_cannot_weaken_exposure_ceiling() -> None:
    result = crack_width_limit(
        CrackWidthLimitRequest(
            "IS456-WP04",
            ExposureClass.VERY_SEVERE,
            True,
            LimitSource.PROJECT,
            project_limit_mm=0.2,
        )
    )

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "LIMIT.EXCEEDS_CODE"


def test_span_depth_screening_is_labeled_and_uses_explicit_factors() -> None:
    result = check_deflection(
        DeflectionCheckRequest(
            "IS456-WP04",
            DeflectionMethod.SPAN_DEPTH_SCREENING,
            screening=DeflectionScreeningBasis(
                5000,
                500,
                SupportCondition.SIMPLY_SUPPORTED,
                1.2,
                1.1,
                1,
                "topology:S1",
                "reviewed-figure-factors:1",
            ),
        )
    )

    assert result.engineering == "pass"
    assert result.outputs["result_kind"] == "screening_not_calculated_displacement"
    assert result.outputs["actual_span_depth_ratio"] == pytest.approx(10)
    assert result.outputs["allowable_span_depth_ratio"] == pytest.approx(26.4)
    assert "total_final_deflection_mm" not in result.outputs


def test_span_depth_screening_rejects_calculated_limit_inputs() -> None:
    result = check_deflection(
        DeflectionCheckRequest(
            "IS456-WP04",
            DeflectionMethod.SPAN_DEPTH_SCREENING,
            screening=DeflectionScreeningBasis(
                5000,
                500,
                SupportCondition.SIMPLY_SUPPORTED,
                1.2,
                1.1,
                1,
                "topology:S1",
                "reviewed-figure-factors:1",
            ),
            total_limit=DeflectionLimitRequest(
                "IS456-WP04", 5000, DeflectionCriterion.TOTAL_FINAL
            ),
        )
    )

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "INPUT.CONFLICT"


def _calculated_basis(*, duration: float | None = 1825) -> CalculatedDeflectionBasis:
    return CalculatedDeflectionBasis(
        service_action_snapshot_id="snapshot:SLS-1",
        total_service_action_row_ids=("row:total",),
        sustained_service_action_row_ids=("row:sustained",),
        analysis_result_id="analysis:SLS-1",
        reinforcement_revision_id="reinforcement:R1",
        effective_span_mm=6000,
        instantaneous_total_deflection_mm=8,
        instantaneous_sustained_deflection_mm=5,
        creep_multiplier=1.2,
        shrinkage_deflection_mm=1,
        finish_installation_age_days=90,
        deflection_at_finish_installation_mm=4,
        age_at_loading_days=28,
        assessment_age_days=1853,
        sustained_duration_days=duration,
        relative_humidity_percent=60,
        notional_size_mm=150,
        stiffness_method="effective-inertia:reviewed",
        cracking_method="cracked-section:reviewed",
        creep_method="creep-factor:reviewed",
        shrinkage_method="shrinkage-curvature:reviewed",
    )


def _calculated_request(
    basis: CalculatedDeflectionBasis,
) -> DeflectionCheckRequest:
    return DeflectionCheckRequest(
        "IS456-WP04",
        DeflectionMethod.CALCULATED_COMPONENTS,
        calculated=basis,
        total_limit=DeflectionLimitRequest(
            "IS456-WP04", 6000, DeflectionCriterion.TOTAL_FINAL
        ),
        after_finishes_limit=DeflectionLimitRequest(
            "IS456-WP04", 6000, DeflectionCriterion.AFTER_FINISHES
        ),
    )


def test_calculated_deflection_retains_short_long_term_and_finish_components() -> None:
    result = check_deflection(_calculated_request(_calculated_basis()))

    assert result.engineering == "pass"
    assert result.outputs["instantaneous_total_deflection_mm"] == 8
    assert result.outputs["creep_additional_deflection_mm"] == pytest.approx(6)
    assert result.outputs["shrinkage_deflection_mm"] == 1
    assert result.outputs["total_final_deflection_mm"] == pytest.approx(15)
    assert result.outputs["after_finishes_deflection_mm"] == pytest.approx(11)
    assert result.outputs["total_limit_mm"] == pytest.approx(24)
    assert result.outputs["after_finishes_limit_mm"] == pytest.approx(6000 / 350)
    assert result.outputs["service_action_snapshot_id"] == "snapshot:SLS-1"
    assert result.outputs["total_service_action_row_ids"] == ["row:total"]
    assert result.outputs["sustained_service_action_row_ids"] == ["row:sustained"]


def test_calculated_deflection_missing_duration_is_not_evaluated() -> None:
    result = check_deflection(_calculated_request(_calculated_basis(duration=None)))

    assert result.execution == "completed"
    assert result.engineering == "not_evaluated"
    assert result.completeness == "partial"
    assert result.diagnostics[0].code == "EVIDENCE.REQUIRED"


def _bars(left_x: float, right_x: float) -> tuple[BarPosition, ...]:
    return (
        BarPosition("BL", 20, left_x, 450, Face.BOTTOM),
        BarPosition("BR", 20, right_x, 450, Face.BOTTOM),
    )


def _crack_request(
    bars: tuple[BarPosition, ...],
    exposure: ExposureClass = ExposureClass.MILD,
    mean_strain: float | None = 0.0006,
) -> CrackWidthCheckRequest:
    return CrackWidthCheckRequest(
        "IS456-WP04",
        "M1",
        "S1@2500",
        "action:SLS-1",
        "reinforcement:R1",
        300,
        500,
        200,
        Face.BOTTOM,
        bars,
        150,
        200,
        415,
        200_000,
        mean_strain,
        CrackWidthLimitRequest(
            "IS456-WP04",
            exposure,
            exposure is not ExposureClass.MILD,
        ),
    )


def test_annex_f_crack_width_uses_actual_bar_surface_geometry() -> None:
    result = check_crack_width(_crack_request(_bars(75, 225)))

    assert result.engineering == "pass"
    assert result.outputs["effective_depth_mm"] == pytest.approx(450)
    assert result.outputs["cmin_mm"] == pytest.approx(40)
    assert result.outputs["acr_mm"] == pytest.approx((75**2 + 50**2) ** 0.5 - 10)
    assert result.outputs["calculated_crack_width_mm"] == pytest.approx(
        0.11379830508373975
    )
    assert result.outputs["nearest_bar_id"] == "BL"


def test_equal_steel_area_with_different_spacing_changes_crack_width() -> None:
    wide = check_crack_width(_crack_request(_bars(75, 225)))
    close = check_crack_width(_crack_request(_bars(130, 170)))

    assert (
        wide.outputs["calculated_crack_width_mm"]
        > close.outputs["calculated_crack_width_mm"]
    )
    assert wide.outputs["effective_depth_mm"] == close.outputs["effective_depth_mm"]


def test_aggressive_exposure_can_make_completed_crack_check_fail() -> None:
    result = check_crack_width(
        _crack_request(_bars(75, 225), ExposureClass.VERY_SEVERE)
    )

    assert result.execution == "completed"
    assert result.engineering == "fail"
    assert result.outputs["limit_mm"] == pytest.approx(0.1)
    assert result.diagnostics[0].code == "CRACK_WIDTH.LIMIT_EXCEEDED"


def test_missing_actual_bars_is_not_evaluated() -> None:
    result = check_crack_width(_crack_request(()))

    assert result.execution == "completed"
    assert result.engineering == "not_evaluated"
    assert result.diagnostics[0].code == "EVIDENCE.REQUIRED"


def test_missing_mean_strain_is_not_inferred_from_stress() -> None:
    result = check_crack_width(_crack_request(_bars(75, 225), mean_strain=None))

    assert result.execution == "completed"
    assert result.engineering == "not_evaluated"
    assert result.diagnostics[0].code == "EVIDENCE.REQUIRED"


def test_invalid_bar_face_is_rejected_as_geometry() -> None:
    invalid = BarPosition("BL", 20, 75, 450, "bottom")  # type: ignore[arg-type]
    result = check_crack_width(_crack_request((invalid, *_bars(130, 170))))

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "BAR.GEOMETRY"
