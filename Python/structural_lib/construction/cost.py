"""AO20: explicit dated direct construction cost over current quantities."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation

from structural_lib.beam.semantics import (
    Diagnostic,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    rejected_result,
    semantic_hash,
)

from .contracts import (
    ConstructionCostOutput,
    ConstructionCostRequest,
    CostBasis,
    CostCategory,
    CostLine,
    WastePricingBasis,
)

ESTIMATE_COST_OPERATION = "structural.construction_cost.estimate/v1"
COST_METHOD_REVISION = "structural-construction-cost-wp07-v1"
_UNITS = {
    CostBasis.STEEL_SCHEDULED_MASS_KG: "kg",
    CostBasis.STEEL_STOCK_MASS_KG: "kg",
    CostBasis.CONCRETE_VOLUME_M3: "m3",
    CostBasis.FORMWORK_AREA_M2: "m2",
    CostBasis.COUPLER_COUNT: "count",
}


def _text(value: str | None) -> bool:
    return bool(value and value.strip())


def _provenance() -> Provenance:
    return Provenance(
        "construction-cost-wp07-v1",
        COST_METHOD_REVISION,
        (
            "PF5 AO20 dated explicit rate profile",
            "PF7 AR20 direct material, labour, plant, overhead, tax, and waste scope",
        ),
    )


def _error(code: str, message: str, field: str, remediation: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        ESTIMATE_COST_OPERATION,
        field,
        "construction-cost",
        remediation,
    )


def _reject(
    inputs: dict[str, dict[str, object]],
    code: str,
    message: str,
    field: str,
    remediation: str,
) -> OperationResult:
    return rejected_result(
        ESTIMATE_COST_OPERATION,
        inputs,
        (_error(code, message, field, remediation),),
        provenance=_provenance(),
    )


def _decimal(value: str) -> Decimal | None:
    if re.fullmatch(r"(?:0|[0-9]+)(?:\.[0-9]+)?", value) is None:
        return None
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError):
        return None
    if not result.is_finite() or result < 0:
        return None
    return result


def _money(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _quantity(value: float) -> Decimal:
    return Decimal(str(value))


def estimate_construction_cost(request: ConstructionCostRequest) -> OperationResult:
    """Price an explicitly declared scope with decimal arithmetic."""

    inputs = effective_inputs(request=request)
    quantities = request.quantities
    profile = request.rate_profile
    if (
        not all(
            _text(value)
            for value in (
                request.profile_id,
                request.project_basis_id,
                request.member_id,
                request.detail_revision_id,
                request.quantity_result_id,
                request.quantity_output_payload_id,
                profile.profile_id,
                profile.revision_id,
                profile.currency,
                profile.valuation_date,
                profile.time_zone,
                profile.geography,
                profile.source,
            )
        )
        or len(profile.currency) != 3
    ):
        return _reject(
            inputs,
            "COST.IDENTITY",
            "Costing requires complete currency, date, geography, source, profile, and result identities.",
            "request",
            "Supply a complete dated rate profile.",
        )
    try:
        date.fromisoformat(profile.valuation_date)
    except ValueError:
        return _reject(
            inputs,
            "COST.DATE",
            "Valuation date must be an ISO calendar date.",
            "rate_profile.valuation_date",
            "Supply YYYY-MM-DD.",
        )
    if (
        quantities.profile_id != request.profile_id
        or quantities.project_basis_id != request.project_basis_id
        or quantities.member_id != request.member_id
        or quantities.detail_revision_id != request.detail_revision_id
    ):
        return _reject(
            inputs,
            "COST.QUANTITY_STALE",
            "Cost must bind current quantities for the same project, member, and detail.",
            "quantities",
            "Recalculate quantities for the active detail.",
        )
    if request.quantity_output_payload_id != semantic_hash(
        "output_payload_id", quantities
    ):
        return _reject(
            inputs,
            "COST.QUANTITY_BINDING",
            "The quantity payload does not match its canonical output identity.",
            "quantity_output_payload_id",
            "Bind the unchanged AO04 output payload.",
        )

    included = profile.scope.included_categories
    excluded = profile.scope.excluded_categories
    all_categories = set(CostCategory)
    if (
        len(included) != len(set(included))
        or len(excluded) != len(set(excluded))
        or set(included) & set(excluded)
        or set(included) | set(excluded) != all_categories
    ):
        return _reject(
            inputs,
            "COST.SCOPE",
            "Every direct-cost category must be explicitly included or excluded exactly once.",
            "rate_profile.scope",
            "Declare material, formwork, coupler, labour, and plant scope.",
        )
    if not profile.rates or any(
        category not in {item.category for item in profile.rates}
        for category in included
    ):
        return _reject(
            inputs,
            "COST.RATE_MISSING",
            "Every included cost category requires at least one explicit rate.",
            "rate_profile.rates",
            "Add the missing in-scope rate or explicitly exclude its category.",
        )
    rate_ids = [item.rate_id for item in profile.rates]
    rate_keys = [(item.category, item.basis) for item in profile.rates]
    if len(rate_ids) != len(set(rate_ids)) or len(rate_keys) != len(set(rate_keys)):
        return _reject(
            inputs,
            "COST.RATE_DUPLICATE",
            "Rate identities and category/basis pairs must be unique.",
            "rate_profile.rates",
            "Remove overlapping rates that could price one scope twice.",
        )
    if any(
        not all(
            _text(value)
            for value in (item.rate_id, item.description, item.source_reference)
        )
        or item.category not in included
        or not isinstance(item.basis, CostBasis)
        or _decimal(item.unit_rate_decimal) is None
        for item in profile.rates
    ):
        return _reject(
            inputs,
            "COST.RATE_INVALID",
            "Rates require an included category, supported basis, nonnegative decimal rate, description, and source.",
            "rate_profile.rates",
            "Correct the priced line scope and decimal rate.",
        )

    permitted_bases = {
        CostCategory.MATERIAL: {
            CostBasis.STEEL_SCHEDULED_MASS_KG,
            CostBasis.STEEL_STOCK_MASS_KG,
            CostBasis.CONCRETE_VOLUME_M3,
        },
        CostCategory.FORMWORK: {CostBasis.FORMWORK_AREA_M2},
        CostCategory.COUPLER: {CostBasis.COUPLER_COUNT},
        CostCategory.LABOUR: set(CostBasis),
        CostCategory.PLANT: set(CostBasis),
    }
    if any(rate.basis not in permitted_bases[rate.category] for rate in profile.rates):
        return _reject(
            inputs,
            "COST.RATE_SCOPE",
            "A cost category may price only its declared physical quantity basis.",
            "rate_profile.rates",
            "Bind material, formwork, and coupler rates to their matching quantities.",
        )

    if profile.waste_pricing_basis is WastePricingBasis.SCHEDULED_STEEL:
        forbidden = CostBasis.STEEL_STOCK_MASS_KG
    elif profile.waste_pricing_basis is WastePricingBasis.PURCHASED_STOCK:
        forbidden = CostBasis.STEEL_SCHEDULED_MASS_KG
    else:
        return _reject(
            inputs,
            "COST.WASTE_POLICY",
            "A single supported steel waste pricing basis is required.",
            "rate_profile.waste_pricing_basis",
            "Choose scheduled steel or purchased stock.",
        )
    if any(item.basis is forbidden for item in profile.rates):
        return _reject(
            inputs,
            "COST.WASTE_DOUBLE_COUNT",
            "The selected steel waste basis conflicts with a supplied steel rate basis.",
            "rate_profile.rates",
            "Price steel from exactly one scheduled-or-purchased basis.",
        )
    required_bases: dict[CostCategory, set[CostBasis]] = {
        CostCategory.MATERIAL: {
            (
                CostBasis.STEEL_SCHEDULED_MASS_KG
                if profile.waste_pricing_basis is WastePricingBasis.SCHEDULED_STEEL
                else CostBasis.STEEL_STOCK_MASS_KG
            ),
            CostBasis.CONCRETE_VOLUME_M3,
        },
        CostCategory.FORMWORK: {CostBasis.FORMWORK_AREA_M2},
        CostCategory.COUPLER: {CostBasis.COUPLER_COUNT},
    }
    supplied_pairs = {(item.category, item.basis) for item in profile.rates}
    if any(
        any((category, basis) not in supplied_pairs for basis in bases)
        for category, bases in required_bases.items()
        if category in included
    ):
        return _reject(
            inputs,
            "COST.RATE_COVERAGE",
            "The included material, formwork, or coupler scope is missing a required physical quantity rate.",
            "rate_profile.rates",
            "Price every physical basis in the declared included scope.",
        )

    overhead_percent = _decimal(profile.overhead_percent_decimal)
    tax_percent = _decimal(profile.tax_percent_decimal)
    if overhead_percent is None or tax_percent is None:
        return _reject(
            inputs,
            "COST.PERCENT",
            "Overhead and tax treatments require explicit nonnegative decimal percentages.",
            "rate_profile",
            "Supply zero when the declared scope excludes an amount.",
        )
    basis_values = {
        CostBasis.STEEL_SCHEDULED_MASS_KG: quantities.steel_scheduled_mass_kg,
        CostBasis.STEEL_STOCK_MASS_KG: quantities.steel_stock_mass_kg,
        CostBasis.CONCRETE_VOLUME_M3: quantities.concrete_volume_m3,
        CostBasis.FORMWORK_AREA_M2: quantities.formwork_area_m2,
        CostBasis.COUPLER_COUNT: float(quantities.coupler_count),
    }
    lines: list[CostLine] = []
    line_amounts: list[Decimal] = []
    for rate in sorted(profile.rates, key=lambda item: item.rate_id):
        quantity = _quantity(basis_values[rate.basis])
        unit_rate = _decimal(rate.unit_rate_decimal)
        assert unit_rate is not None
        amount = (quantity * unit_rate).quantize(Decimal("0.01"))
        line_amounts.append(amount)
        lines.append(
            CostLine(
                rate.rate_id,
                rate.category,
                rate.basis,
                rate.description,
                request.quantity_result_id,
                format(quantity, "f"),
                _UNITS[rate.basis],
                format(unit_rate, "f"),
                _money(amount),
            )
        )
    subtotal = sum(line_amounts, Decimal(0))
    overhead = (subtotal * overhead_percent / Decimal(100)).quantize(Decimal("0.01"))
    pre_tax = subtotal + overhead
    tax = (pre_tax * tax_percent / Decimal(100)).quantize(Decimal("0.01"))
    total = pre_tax + tax
    output = ConstructionCostOutput(
        request.profile_id,
        request.project_basis_id,
        request.member_id,
        request.detail_revision_id,
        request.quantity_result_id,
        profile.profile_id,
        profile.revision_id,
        profile.currency.upper(),
        profile.valuation_date,
        profile.geography,
        profile.source,
        tuple(lines),
        included,
        excluded,
        _money(subtotal),
        _money(overhead),
        _money(pre_tax),
        _money(tax),
        _money(total),
    )
    return completed_result(
        ESTIMATE_COST_OPERATION, inputs, {"cost": output}, provenance=_provenance()
    )
