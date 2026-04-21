"""
Weight policy contract scaffold.

This module is intentionally additive in Phase 0A.  No existing calculator uses
it yet; later phases will migrate component tables and Type calculators to this
contract in small, reviewable steps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class WeightBasis(str, Enum):
    """How a component or BOM line weight was obtained."""

    SOURCE_UNIT_WEIGHT = "source_unit_weight"
    SOURCE_DIMENSION_GEOMETRY = "source_dimension_geometry"
    ENGINEERING_ESTIMATE = "engineering_estimate"
    NOT_AVAILABLE = "not_available"


class WeightPolicy(str, Enum):
    """Caller-side acceptance policy for WeightResult."""

    STRICT = "strict"
    SOURCE_OR_DIM = "source_or_dim"
    ANY_WITH_FLAG = "any_with_flag"
    ANY = "any"


@dataclass(frozen=True)
class WeightResult:
    """
    Traceable weight value.

    `value` may be None only when basis is NOT_AVAILABLE.  Engineering estimates
    must identify the estimator so reviewers can trace the decision later.
    """

    value: float | None
    basis: WeightBasis
    source_ref: str
    estimator_id: str | None = None
    estimator_version: str | None = None
    requires_review: bool = False
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.basis is WeightBasis.NOT_AVAILABLE:
            if self.value is not None:
                raise ValueError("WeightResult.value must be None when basis is NOT_AVAILABLE")
            return

        if self.value is None:
            raise ValueError("WeightResult.value is required unless basis is NOT_AVAILABLE")

        if self.basis is WeightBasis.ENGINEERING_ESTIMATE and not self.estimator_id:
            raise ValueError("ENGINEERING_ESTIMATE requires estimator_id")


def is_allowed_by_policy(weight: WeightResult, policy: WeightPolicy) -> bool:
    """Return whether a WeightResult is acceptable under the caller policy."""
    if policy is WeightPolicy.ANY:
        return True
    if policy is WeightPolicy.ANY_WITH_FLAG:
        return weight.basis is not WeightBasis.NOT_AVAILABLE
    if policy is WeightPolicy.SOURCE_OR_DIM:
        return weight.basis in {
            WeightBasis.SOURCE_UNIT_WEIGHT,
            WeightBasis.SOURCE_DIMENSION_GEOMETRY,
        }
    if policy is WeightPolicy.STRICT:
        return weight.basis is WeightBasis.SOURCE_UNIT_WEIGHT
    return False


def require_weight(weight: WeightResult, policy: WeightPolicy = WeightPolicy.SOURCE_OR_DIM) -> WeightResult:
    """Raise if the weight does not satisfy the given policy; otherwise return it."""
    if not is_allowed_by_policy(weight, policy):
        raise ValueError(f"WeightResult basis {weight.basis.value} is not allowed by policy {policy.value}")
    return weight
