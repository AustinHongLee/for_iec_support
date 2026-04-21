"""Hardware material resolution contract scaffold.

Phase 0B only defines the interface and default lookup behavior. Existing Type
calculators must not import this module until the material migration phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class HardwareKind(str, Enum):
    """BOM hardware/material decision categories."""

    THREADED_ROD = "threaded_rod"
    HEAVY_HEX_NUT = "heavy_hex_nut"
    WELDLESS_EYE_NUT = "weldless_eye_nut"
    CLAMP_BODY = "clamp_body"
    U_BOLT = "u_bolt"
    CLEVIS = "clevis"
    TURNBUCKLE = "turnbuckle"
    UPPER_BRACKET = "upper_bracket"
    PLATE_LUG = "plate_lug"
    BEAM_ATTACHMENT = "beam_attachment"
    STRUCTURAL_STRUT = "structural_strut"
    SPRING_CAN = "spring_can"
    COLD_SHOE_INSULATION_CLAMP = "cold_shoe_insulation_clamp"
    EXPANSION_BOLT = "expansion_bolt"
    ANCHOR_BOLT = "anchor_bolt"
    PIPE_SHOE = "pipe_shoe"
    GUSSET_PLATE = "gusset_plate"


class ServiceClass(str, Enum):
    """Service-temperature class for hardware material defaults."""

    AMBIENT = "ambient"
    HOT = "hot"
    HIGH_TEMP = "high_temp"
    COLD = "cold"
    CRYO = "cryo"


@dataclass(frozen=True)
class MaterialSpec:
    """Resolved hardware material with provenance."""

    name: str
    source: str
    requires_review: bool = True
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class HardwareMaterialOverrides:
    """Explicit hardware-only overrides.

    Intentionally excludes pipe material. Hardware material must be selected by
    hardware kind and service class, not inferred from the process pipe.
    """

    per_kind: Mapping[HardwareKind, str] = field(default_factory=dict)
    all_hardware: str | None = None


class MaterialResolutionError(ValueError):
    """Raised when no material can be resolved for a hardware kind."""


def resolve_hardware_material(
    kind: HardwareKind,
    *,
    service: ServiceClass = ServiceClass.AMBIENT,
    overrides: HardwareMaterialOverrides | None = None,
) -> MaterialSpec:
    """Resolve hardware material without consulting pipe material.

    This scaffold resolver is intentionally isolated from existing Type
    calculators. It provides the future interface while preserving current
    runtime behavior until the migration phases opt in.
    """

    if overrides:
        if kind in overrides.per_kind:
            return MaterialSpec(
                name=overrides.per_kind[kind],
                source=f"override.per_kind.{kind.value}",
                requires_review=False,
            )
        if overrides.all_hardware:
            return MaterialSpec(
                name=overrides.all_hardware,
                source="override.all_hardware",
                requires_review=False,
            )

    from data.engineering_material_spec import DEFAULT_HARDWARE_MATERIAL

    per_service = DEFAULT_HARDWARE_MATERIAL.get(kind)
    if not per_service:
        raise MaterialResolutionError(f"No default hardware material for {kind.value}")

    material = per_service.get(service) or per_service.get("*")
    if not material:
        raise MaterialResolutionError(
            f"No default hardware material for {kind.value} under {service.value}"
        )

    return MaterialSpec(
        name=material,
        source="engineering_material_spec.DEFAULT_HARDWARE_MATERIAL",
        requires_review=True,
        notes=("Phase 0B scaffold default; review before production use.",),
    )
