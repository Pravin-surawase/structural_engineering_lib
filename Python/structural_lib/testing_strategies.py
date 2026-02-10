"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.testing_strategies
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.testing_strategies."""

from __future__ import annotations

from structural_lib.services.testing_strategies import (  # noqa: F401, E402
    AREA_TOLERANCE,
    BeamDesignInvariants,
    BeamParameterRanges,
    BoundaryValueGenerator,
    FORCE_TOLERANCE,
    InvariantCheck,
    LENGTH_TOLERANCE,
    PropertyBasedTester,
    RATIO_TOLERANCE,
    RandomTestCase,
    RegressionBaseline,
    RegressionTestSuite,
    STRESS_TOLERANCE,
    T,
    ToleranceSpec,
    assert_beam_design_valid,
    create_test_case_id,
)
