"""Server-owned policy for the bounded ETABS live transport surface."""

from __future__ import annotations

from enum import Enum
from ipaddress import ip_address
from typing import Literal

from pydantic import BaseModel, ConfigDict

ETABS_LIVE_READ_SCOPE = "etabs:live:read"
ETABS_LIVE_MUTATION_SCOPE = "etabs:live:mutate"


class ETABSOperationClass(str, Enum):
    """Security class for one ETABS bridge operation."""

    OFFLINE = "OFFLINE"
    LIVE_READ = "LIVE_READ"
    LIVE_MUTATION = "LIVE_MUTATION"


class ETABSOperationPolicyV1(BaseModel):
    """Immutable route classification owned by the server."""

    model_config = ConfigDict(frozen=True)

    method: Literal["GET", "POST"]
    path: str
    operation_class: ETABSOperationClass
    required_scope: str | None = None


class ETABSLiveRoutePolicyV1(BaseModel):
    """Resolved startup policy for the complete ETABS bridge surface."""

    model_config = ConfigDict(frozen=True)

    schema_version: Literal["etabs-live-route-policy/v1"] = "etabs-live-route-policy/v1"
    live_bridge_enabled: bool
    live_mutation_enabled: bool
    bind_host: str
    operations: tuple[ETABSOperationPolicyV1, ...]


ETABS_OPERATION_POLICIES_V1 = (
    ETABSOperationPolicyV1(
        method="GET",
        path="/api/v1/etabs-bridge/v1/status",
        operation_class=ETABSOperationClass.OFFLINE,
    ),
    ETABSOperationPolicyV1(
        method="POST",
        path="/api/v1/etabs-bridge/v1/beam-demand",
        operation_class=ETABSOperationClass.OFFLINE,
    ),
    ETABSOperationPolicyV1(
        method="POST",
        path="/api/v1/etabs-bridge/v1/connect",
        operation_class=ETABSOperationClass.LIVE_READ,
        required_scope=ETABS_LIVE_READ_SCOPE,
    ),
    ETABSOperationPolicyV1(
        method="POST",
        path="/api/v1/etabs-bridge/v1/beam-baseline/preflight",
        operation_class=ETABSOperationClass.LIVE_READ,
        required_scope=ETABS_LIVE_READ_SCOPE,
    ),
    ETABSOperationPolicyV1(
        method="POST",
        path="/api/v1/etabs-bridge/v1/beam-baseline",
        operation_class=ETABSOperationClass.LIVE_READ,
        required_scope=ETABS_LIVE_READ_SCOPE,
    ),
    ETABSOperationPolicyV1(
        method="POST",
        path="/api/v1/etabs-bridge/v1/result-catalogue",
        operation_class=ETABSOperationClass.LIVE_READ,
        required_scope=ETABS_LIVE_READ_SCOPE,
    ),
    ETABSOperationPolicyV1(
        method="POST",
        path="/api/v1/etabs-bridge/v1/beam-pilot",
        operation_class=ETABSOperationClass.LIVE_MUTATION,
        required_scope=ETABS_LIVE_MUTATION_SCOPE,
    ),
)


def is_loopback_host(host: str) -> bool:
    """Return whether a bind or peer host is unambiguously loopback."""

    normalized = host.strip().strip("[]").lower()
    if normalized == "localhost":
        return True
    try:
        return ip_address(normalized).is_loopback
    except ValueError:
        return False


def build_etabs_live_route_policy_v1(
    *,
    live_bridge_enabled: bool,
    live_mutation_enabled: bool,
    bind_host: str,
) -> ETABSLiveRoutePolicyV1:
    """Build the immutable policy reported by the resolved settings."""

    return ETABSLiveRoutePolicyV1(
        live_bridge_enabled=live_bridge_enabled,
        live_mutation_enabled=live_mutation_enabled,
        bind_host=bind_host,
        operations=ETABS_OPERATION_POLICIES_V1,
    )
