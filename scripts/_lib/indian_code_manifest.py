"""Build the deterministic Indian-code capability and traceability manifest.

Capability declarations and decorator registration are intentionally separate:
neither file existence nor a ``@clause`` decorator proves engineering
completeness, verification, or professional approval.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = REPO_ROOT / "Python"
MANIFEST_PATH = (
    REPO_ROOT / "docs" / "verification" / "indian-code-capability-coverage.json"
)
SCHEMA_VERSION = "1.0"

STANDARD_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "standard_id": "IS456",
        "namespace": "IS456:2000",
        "edition": "2000",
        "title": "Plain and reinforced concrete code of practice",
        "source_root": "Python/structural_lib/codes/is456",
    },
    {
        "standard_id": "IS13920",
        "namespace": "IS13920:2016",
        "edition": "2016",
        "title": "Ductile detailing of reinforced concrete structures",
        "source_root": "Python/structural_lib/codes/is13920",
    },
    {
        "standard_id": "IS875",
        "namespace": "IS875",
        "edition": "SERIES_NOT_SELECTED",
        "title": "Structural loading series",
        "source_root": None,
    },
    {
        "standard_id": "IS1893",
        "namespace": "IS1893",
        "edition": "EDITION_NOT_SELECTED",
        "title": "Earthquake-resistant design criteria",
        "source_root": None,
    },
)

_STANDARD_ALIASES = {
    "IS 456": "IS456:2000",
    "IS 456:2000": "IS456:2000",
    "IS 13920": "IS13920:2016",
    "IS 13920:2016": "IS13920:2016",
}

_IS456_EVIDENCE = {
    "beam": ("docs/verification/is456-library-first-evidence.md",),
    "column": ("docs/verification/is456-library-first-evidence.md",),
    "isolated_footing": ("docs/verification/footing-release-inclusion.json",),
    "solid_slab": ("docs/verification/is456-slab-evidence.md",),
    "stair": (
        "docs/verification/india-2a-staircase-scope-evidence.md",
        "docs/verification/india-2b-staircase-actions-evidence.md",
        "docs/verification/india-2c-staircase-design-evidence.md",
        "docs/verification/india-2d-staircase-publication-evidence.md",
    ),
    "wall": (
        "docs/verification/india-2-wall-g0-scope-evidence.md",
        "docs/verification/india-2-wall-a-axial-kernel-evidence.md",
        "docs/verification/india-2-wall-b-reinforcement-evidence.md",
        "docs/verification/india-2-wall-c-public-workflow-evidence.md",
        "docs/verification/india-2-wall-d-publication-evidence.md",
        "docs/verification/india-2-wall-family-acceptance-evidence.md",
    ),
    "deep_beam": (
        "docs/verification/india-2-deep-g0-scope-evidence.md",
        "docs/verification/india-2-deep-a-geometry-evidence.md",
        "docs/verification/india-2-deep-b-reinforcement-evidence.md",
        "docs/verification/india-2-deep-c-public-workflow-evidence.md",
        "docs/verification/india-2-deep-d-publication-evidence.md",
        "docs/verification/india-2-deep-family-acceptance-evidence.md",
    ),
    "flat_slab": (
        "docs/verification/india-2-flat-g0-scope-evidence.md",
        "docs/verification/india-2-flat-a-geometry-evidence.md",
        "docs/verification/india-2-flat-b-moment-evidence.md",
        "docs/verification/india-2-flat-c-reinforcement-evidence.md",
        "docs/verification/india-2-flat-d-punching-evidence.md",
        "docs/verification/india-2-flat-e-publication-evidence.md",
        "docs/verification/india-2-flat-family-acceptance-evidence.md",
    ),
    "combined_footing": (
        "docs/verification/india-2-foundation-combined-g0-scope-evidence.md",
        "docs/verification/india-2-foundation-combined-a-analysis-evidence.md",
        "docs/verification/india-2-foundation-combined-b-strength-evidence.md",
        "docs/verification/india-2-foundation-combined-c-public-workflow-evidence.md",
        "docs/verification/india-2-foundation-combined-d-publication-evidence.md",
        "docs/verification/india-2-foundation-combined-family-acceptance-evidence.md",
    ),
    "strap_footing": (
        "docs/verification/india-2-foundation-strap-g0-scope-evidence.md",
        "docs/verification/india-2-foundation-strap-a-analysis-evidence.md",
        "docs/verification/india-2-foundation-strap-b-strength-evidence.md",
        "docs/verification/india-2-foundation-strap-c-public-workflow-evidence.md",
        "docs/verification/india-2-foundation-strap-d-publication-evidence.md",
        "docs/verification/india-2-foundation-strap-family-acceptance-evidence.md",
    ),
}

_HELD_FAMILIES: dict[str, tuple[dict[str, Any], ...]] = {
    "IS456:2000": (
        {
            "family": "raft_foundation",
            "claim": "Raft-foundation design is not implemented.",
            "limitations": [
                "Soil-structure interaction remains outside the supported subset.",
                "INDIA-2 raft G0 is held until a controlled IS 2950 source and an independently replayable structural benchmark are bound.",
            ],
            "evidence": [
                "docs/verification/india-2-foundation-raft-g0-hold-evidence.md"
            ],
        },
        {
            "family": "pile_cap",
            "claim": "Pile-cap design is not implemented.",
            "limitations": [
                "Pile reactions and strut-and-tie behavior require a separate program.",
                "INDIA-2 pile-cap G0 is held until a controlled companion source and an independently replayable structural benchmark are bound.",
            ],
            "evidence": [
                "docs/verification/india-2-foundation-pile-cap-g0-hold-evidence.md"
            ],
        },
    ),
    "IS13920:2016": (
        {
            "family": "wall_detailing",
            "claim": "IS 13920 wall provisions are not implemented.",
            "limitations": [
                "Wall and boundary-element provisions require a separate packet."
            ],
        },
        {
            "family": "foundation_detailing",
            "claim": "IS 13920 foundation provisions are not implemented.",
            "limitations": [
                "Foundation capacity-design provisions require a separate packet."
            ],
        },
    ),
    "IS875": (
        {
            "family": "gravity_load_generation",
            "claim": "IS 875 gravity-load generation is not implemented.",
            "limitations": [
                "Applicable parts and editions must be selected before implementation."
            ],
        },
        {
            "family": "wind_load_generation",
            "claim": "IS 875 wind-load generation is not implemented.",
            "limitations": [
                "Wind inputs and pressure generation require a separate program."
            ],
        },
    ),
    "IS1893": (
        {
            "family": "equivalent_static_seismic",
            "claim": "IS 1893 equivalent-static force generation is not implemented.",
            "limitations": [
                "Edition, inputs, load combinations, and validation must be selected first."
            ],
        },
        {
            "family": "response_spectrum_analysis",
            "claim": "Response-spectrum and FEM analysis are not implemented.",
            "limitations": ["This remains a separate analysis program."],
        },
    ),
}

_IS13920_SUPPORTED: tuple[dict[str, Any], ...] = (
    {
        "family": "beam_detailing_checks",
        "claim": "Bounded beam geometry, longitudinal-steel, and confinement-spacing checks exist.",
        "workflows": ["check_beam_ductility"],
        "limitations": [
            "This is a bounded detailing check, not a complete seismic design workflow."
        ],
        "evidence": [
            "Python/structural_lib/codes/is13920/beam.py",
            "Python/tests/property/test_ductile_hypothesis.py",
        ],
    },
    {
        "family": "column_detailing_checks",
        "claim": "Bounded column geometry and special-confinement checks exist.",
        "workflows": ["check_column_ductility_is13920"],
        "limitations": [
            "This is a bounded detailing check, not a complete seismic design workflow."
        ],
        "evidence": [
            "Python/structural_lib/codes/is13920/column.py",
            "Python/tests/codes/is13920/test_column.py",
        ],
    },
    {
        "family": "beam_column_joint_scwb_check",
        "claim": "A pure-math strong-column weak-beam joint check exists.",
        "workflows": ["structural_lib.codes.is13920.joint.check_scwb"],
        "limitations": [
            "No complete joint design or public service workflow is claimed."
        ],
        "evidence": [
            "Python/structural_lib/codes/is13920/joint.py",
            "Python/tests/codes/is13920/test_joint.py",
        ],
    },
)


def _supported_family(
    namespace: str,
    family: str,
    claim: str,
    workflows: list[str],
    limitations: list[str],
    evidence: list[str],
) -> dict[str, Any]:
    return {
        "capability_id": f"{namespace}:{family}",
        "family": family,
        "scope_status": "SUPPORTED",
        "implementation_status": "IMPLEMENTED_BOUNDED",
        "claim": claim,
        "workflows": workflows,
        "limitations": limitations,
        "evidence": evidence,
        "qualified_review_required": True,
    }


def _held_family(namespace: str, definition: dict[str, Any]) -> dict[str, Any]:
    family = definition["family"]
    return {
        "capability_id": f"{namespace}:{family}",
        "family": family,
        "scope_status": "HELD",
        "implementation_status": definition.get(
            "implementation_status", "NOT_IMPLEMENTED"
        ),
        "claim": definition["claim"],
        "workflows": definition.get("workflows", []),
        "limitations": definition["limitations"],
        "evidence": definition.get("evidence", []),
        "qualified_review_required": True,
    }


def _build_capability_families() -> dict[str, list[dict[str, Any]]]:
    if str(PYTHON_ROOT) not in sys.path:
        sys.path.insert(0, str(PYTHON_ROOT))

    from structural_lib.services.capabilities import (  # noqa: PLC0415
        IS456_STANDARD_NAMESPACE,
        get_supported_is456_capabilities,
    )

    if IS456_STANDARD_NAMESPACE != "IS456:2000":
        raise ValueError(
            "Manifest namespace disagrees with the runtime IS 456 capability registry"
        )
    result: dict[str, list[dict[str, Any]]] = {
        item["namespace"]: [] for item in STANDARD_DEFINITIONS
    }
    for capability in get_supported_is456_capabilities():
        result["IS456:2000"].append(
            _supported_family(
                "IS456:2000",
                capability.element,
                capability.supported_case,
                list(capability.public_workflows),
                list(capability.held_cases),
                list(_IS456_EVIDENCE[capability.element]),
            )
        )

    for definition in _IS13920_SUPPORTED:
        result["IS13920:2016"].append(
            _supported_family(
                "IS13920:2016",
                definition["family"],
                definition["claim"],
                definition["workflows"],
                definition["limitations"],
                definition["evidence"],
            )
        )

    for namespace, definitions in _HELD_FAMILIES.items():
        result[namespace].extend(_held_family(namespace, item) for item in definitions)
    return result


def _decorator_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _discover_registrations() -> dict[str, dict[str, list[str]]]:
    registrations: dict[str, dict[str, list[str]]] = {}
    for definition in STANDARD_DEFINITIONS:
        source_root = definition["source_root"]
        if source_root is None:
            continue
        root = REPO_ROOT / source_root
        for path in sorted(root.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for decorator in node.decorator_list:
                    if (
                        not isinstance(decorator, ast.Call)
                        or _decorator_name(decorator.func) != "clause"
                    ):
                        continue
                    standard = "IS 456"
                    for keyword in decorator.keywords:
                        if (
                            keyword.arg == "standard"
                            and isinstance(keyword.value, ast.Constant)
                            and isinstance(keyword.value.value, str)
                        ):
                            standard = keyword.value.value
                    namespace = _STANDARD_ALIASES.get(standard)
                    if namespace is None:
                        raise ValueError(
                            f"Unsupported clause namespace {standard!r} in {path}"
                        )
                    module = (
                        path.relative_to(PYTHON_ROOT)
                        .with_suffix("")
                        .as_posix()
                        .replace("/", ".")
                    )
                    function = f"{module}.{node.name}"
                    for argument in decorator.args:
                        if not isinstance(argument, ast.Constant) or not isinstance(
                            argument.value, str
                        ):
                            raise ValueError(
                                f"Non-literal clause reference in {path}:{node.lineno}"
                            )
                        registrations.setdefault(namespace, {}).setdefault(
                            argument.value, []
                        ).append(function)
    return registrations


def _load_reference_metadata() -> dict[str, dict[str, dict[str, Any]]]:
    path = REPO_ROOT / "Python/structural_lib/codes/is456/clauses.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, dict[str, dict[str, Any]]] = {
        item["namespace"]: {} for item in STANDARD_DEFINITIONS
    }

    for reference, info in data.get("clauses", {}).items():
        if reference.startswith("IS13920_"):
            namespace = "IS13920:2016"
            bare_reference = reference.removeprefix("IS13920_")
        else:
            namespace = "IS456:2000"
            bare_reference = reference
        result[namespace][bare_reference] = {
            "reference_type": "clause",
            "title": info.get("title", ""),
            "category": info.get("category", "uncategorized"),
        }

    for group_name, reference_type in (
        ("annexures", "annexure"),
        ("tables", "table"),
        ("figures", "figure"),
    ):
        for reference, info in data.get(group_name, {}).items():
            result["IS456:2000"][reference] = {
                "reference_type": reference_type,
                "title": info.get("title", ""),
                "category": info.get("category", reference_type),
            }
    return result


def _reference_records(
    namespace: str,
    metadata: dict[str, dict[str, Any]],
    registrations: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    all_references = sorted(set(metadata) | set(registrations))
    for reference in all_references:
        known = reference in metadata
        registered = reference in registrations
        if known and registered:
            status = "REGISTERED"
        elif known:
            status = "METADATA_ONLY"
        else:
            status = "REGISTRATION_ONLY"
        info = metadata.get(reference, {})
        records.append(
            {
                "reference_id": f"{namespace}:{reference}",
                "reference": reference,
                "reference_type": info.get("reference_type", "clause"),
                "title": info.get("title", ""),
                "category": info.get("category", "unregistered_metadata"),
                "registration_status": status,
                "functions": sorted(set(registrations.get(reference, []))),
            }
        )

    known_count = len(metadata)
    registered_known = len(set(metadata) & set(registrations))
    summary = {
        "known_references": known_count,
        "registered_known_references": registered_known,
        "metadata_only_references": len(set(metadata) - set(registrations)),
        "registration_only_references": len(set(registrations) - set(metadata)),
        "registration_pct": (
            round(registered_known / known_count * 100, 1) if known_count else None
        ),
    }
    return records, summary


def build_manifest() -> dict[str, Any]:
    """Return the canonical deterministic manifest as JSON-native data."""
    capabilities = _build_capability_families()
    registrations = _discover_registrations()
    metadata = _load_reference_metadata()
    standards: list[dict[str, Any]] = []

    for definition in STANDARD_DEFINITIONS:
        namespace = definition["namespace"]
        families = capabilities[namespace]
        references, registration_summary = _reference_records(
            namespace,
            metadata.get(namespace, {}),
            registrations.get(namespace, {}),
        )
        supported = sum(item["scope_status"] == "SUPPORTED" for item in families)
        held = sum(item["scope_status"] == "HELD" for item in families)
        standards.append(
            {
                **definition,
                "status": "SUPPORTED_SUBSET" if supported else "HELD",
                "capability_summary": {
                    "supported_families": supported,
                    "held_families": held,
                    "total_declared_families": len(families),
                    "supported_pct": (
                        round(supported / len(families) * 100, 1) if families else 0.0
                    ),
                },
                "capability_families": families,
                "registration_summary": registration_summary,
                "references": references,
            }
        )

    all_families = [
        family for standard in standards for family in standard["capability_families"]
    ]
    supported_total = sum(item["scope_status"] == "SUPPORTED" for item in all_families)
    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": "INDIA-0-INDIAN-RC-TRUTH-BASELINE",
        "last_reconciled": "2026-08-15",
        "claim_boundaries": {
            "capability_status": "Declared bounded software scope, not whole-standard completeness or engineering approval.",
            "registration_status": "Decorator-to-identifier traceability only; it does not prove implementation, numerical verification, or provenance.",
            "professional_review": "Qualified structural-engineering review remains required before stable or engineering-use approval.",
        },
        "status_vocabularies": {
            "scope_status": ["SUPPORTED", "HELD"],
            "implementation_status": ["IMPLEMENTED_BOUNDED", "NOT_IMPLEMENTED"],
            "registration_status": ["REGISTERED", "METADATA_ONLY", "REGISTRATION_ONLY"],
        },
        "sources": [
            "Python/structural_lib/services/capabilities.py",
            "Python/structural_lib/codes/is456/clauses.json",
            "Python/structural_lib/codes/is456/**/*.py",
            "Python/structural_lib/codes/is13920/**/*.py",
        ],
        "capability_summary": {
            "supported_families": supported_total,
            "held_families": len(all_families) - supported_total,
            "total_declared_families": len(all_families),
            "supported_pct": round(supported_total / len(all_families) * 100, 1),
        },
        "standards": standards,
    }


def render_manifest(manifest: dict[str, Any] | None = None) -> str:
    """Serialize the manifest in its canonical committed form."""
    return json.dumps(manifest or build_manifest(), indent=2, ensure_ascii=False) + "\n"


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    """Load the committed manifest used by reporting consumers."""
    return json.loads(path.read_text(encoding="utf-8"))
