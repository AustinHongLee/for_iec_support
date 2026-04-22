"""Hardware material resolution contract scaffold.

Phase 0B only defines the interface and default lookup behavior. Existing Type
calculators must not import this module until the material migration phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping


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


@dataclass(frozen=True)
class HardwareMaterialContext:
    """Parsed override context for future Type migration.

    Phase 1D-1 only centralizes parsing. Existing Type calculators continue to
    use their local parsing until follow-up phases opt in.
    """

    service: ServiceClass = ServiceClass.AMBIENT
    material_overrides: HardwareMaterialOverrides | None = None


class MaterialResolutionError(ValueError):
    """Raised when no material can be resolved for a hardware kind."""


def _first_present(overrides: Mapping[str, object], keys: Iterable[str]) -> object | None:
    for key in keys:
        value = overrides.get(key)
        if value is not None and value != "":
            return value
    return None


def _coerce_service_class(value: object) -> ServiceClass:
    if isinstance(value, ServiceClass):
        return value
    token = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    return ServiceClass(token)


def _coerce_hardware_kind(value: object) -> HardwareKind:
    if isinstance(value, HardwareKind):
        return value
    token = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    return HardwareKind(token)


def parse_service_class(
    overrides: Mapping[str, object] | None,
    *,
    keys: tuple[str, ...] = ("service", "service_class"),
    default: ServiceClass = ServiceClass.AMBIENT,
) -> ServiceClass:
    """Parse service class from override dict without consulting pipe material."""

    if not overrides:
        return default
    value = _first_present(overrides, keys)
    if value is None:
        return default
    return _coerce_service_class(value)


def parse_hardware_material_overrides(
    overrides: Mapping[str, object] | None,
    *,
    existing_key: str = "hardware_material_overrides",
    per_kind_key: str = "hardware_material_by_kind",
    all_hardware_keys: tuple[str, ...] = ("hardware_material",),
    legacy_material_keys: tuple[str, ...] = (),
    legacy_material_kinds: Iterable[HardwareKind] = (),
) -> HardwareMaterialOverrides | None:
    """Parse hardware-only material overrides.

    The parser intentionally ignores ``pipe_material``. Legacy material keys are
    opt-in and must be scoped to explicit hardware kinds so future migrations
    can preserve behavior without broad fallback.
    """

    if not overrides:
        return None

    existing = overrides.get(existing_key)
    if isinstance(existing, HardwareMaterialOverrides):
        return existing

    per_kind: dict[HardwareKind, str] = {}
    raw_per_kind = overrides.get(per_kind_key) or {}
    if not isinstance(raw_per_kind, Mapping):
        raise TypeError(f"{per_kind_key} must be a mapping")

    for key, material in raw_per_kind.items():
        if material is None or material == "":
            continue
        per_kind[_coerce_hardware_kind(key)] = str(material)

    legacy_material = _first_present(overrides, legacy_material_keys)
    if legacy_material is not None:
        for kind in legacy_material_kinds:
            per_kind.setdefault(kind, str(legacy_material))

    all_hardware = _first_present(overrides, all_hardware_keys)
    all_hardware_str = str(all_hardware) if all_hardware is not None else None
    if not per_kind and all_hardware_str is None:
        return None
    return HardwareMaterialOverrides(per_kind=per_kind, all_hardware=all_hardware_str)


def parse_hardware_material_context(
    overrides: Mapping[str, object] | None,
    *,
    service_keys: tuple[str, ...] = ("service", "service_class"),
    existing_key: str = "hardware_material_overrides",
    per_kind_key: str = "hardware_material_by_kind",
    all_hardware_keys: tuple[str, ...] = ("hardware_material",),
    legacy_material_keys: tuple[str, ...] = (),
    legacy_material_kinds: Iterable[HardwareKind] = (),
) -> HardwareMaterialContext:
    """Parse service and hardware material overrides as one future contract."""

    return HardwareMaterialContext(
        service=parse_service_class(overrides, keys=service_keys),
        material_overrides=parse_hardware_material_overrides(
            overrides,
            existing_key=existing_key,
            per_kind_key=per_kind_key,
            all_hardware_keys=all_hardware_keys,
            legacy_material_keys=legacy_material_keys,
            legacy_material_kinds=legacy_material_kinds,
        ),
    )


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
