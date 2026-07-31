"""Traceable theoretical weights for dimensioned bolts, nuts and anchors.

The drawings usually release a nominal diameter/length but not a
manufacturer's finished mass.  Project drawings mix metric and imperial
diameters while normally retaining millimetres for an unsuffixed length.
This module provides an engineering estimate for MTO totals without claiming
supplier-product accuracy.  Every returned record contains the geometry
assumptions so a later supplier weight can replace it cleanly.
"""

from __future__ import annotations

from math import pi, sqrt
import re


STEEL_DENSITY_KG_PER_MM3 = 7.85e-6
STAINLESS_304_DENSITY_KG_PER_MM3 = 7.93e-6

_METRIC_SPEC = re.compile(
    r"(?:EB\d*\s*[-–]?\s*)?"
    r"M(?P<diameter>\d+(?:\.\d+)?)\s*"
    r"(?:[X×*]|-)\s*"
    r"(?P<length>\d+(?:\.\d+)?)\s*L?",
    re.IGNORECASE,
)
_IMPERIAL_SPEC = re.compile(
    r"(?:DIA\s*|EB\d*\s*[-–]?\s*)?"
    r"(?P<diameter>"
    r"\d+\s+\d+/\d+|\d+/\d+"
    r")\s*"
    r"(?P<diameter_unit>IN(?:CH(?:ES)?)?|[\"″])?\s*"
    r"(?:[X×*]|;?\s*L\s*=)\s*"
    r"(?P<length>\d+(?:\.\d+)?)\s*"
    r"(?P<length_unit>MM|IN(?:CH(?:ES)?)?|[\"″]|L)?",
    re.IGNORECASE,
)


def parse_metric_diameter_length(spec: str) -> tuple[float, float] | None:
    """Return nominal diameter/length from common project fastener strings."""

    match = _METRIC_SPEC.search(str(spec or "").strip())
    if not match:
        return None
    diameter = float(match.group("diameter"))
    length = float(match.group("length"))
    if diameter <= 0 or length <= 0:
        return None
    return diameter, length


def _fractional_inches(value: str) -> float | None:
    token = " ".join(str(value or "").strip().split())
    if not token:
        return None
    try:
        if " " in token:
            whole, fraction = token.split(" ", 1)
            numerator, denominator = fraction.split("/", 1)
            result = float(whole) + float(numerator) / float(denominator)
        else:
            numerator, denominator = token.split("/", 1)
            result = float(numerator) / float(denominator)
    except (ValueError, ZeroDivisionError):
        return None
    return result if result > 0 else None


def parse_imperial_diameter_length(
    spec: str,
) -> tuple[float, float] | None:
    """Return diameter/length in mm from project imperial spellings.

    An unsuffixed length is interpreted as millimetres because strings such
    as ``5/8"x40`` and ``EB-1/2; L=114`` come from metric-dimensioned project
    drawings.  A length explicitly suffixed with ``in`` or ``"`` is
    converted to millimetres.
    """

    match = _IMPERIAL_SPEC.search(str(spec or "").strip())
    if not match:
        return None
    diameter_in = _fractional_inches(match.group("diameter"))
    if diameter_in is None:
        return None
    length = float(match.group("length"))
    if length <= 0:
        return None
    length_unit = str(match.group("length_unit") or "").upper()
    if length_unit.startswith("IN") or length_unit in {'"', "″"}:
        length *= 25.4
    return diameter_in * 25.4, length


def parse_fastener_diameter_length(
    spec: str,
) -> tuple[float, float] | None:
    """Return nominal diameter/length in mm for supported project formats."""

    return (
        parse_metric_diameter_length(spec)
        or parse_imperial_diameter_length(spec)
    )


def fastener_density_for_material(material: object) -> float:
    """Return the explicit estimator density for common project materials."""

    name = getattr(material, "name", material)
    normalized = str(name or "").upper().replace(" ", "")
    if any(
        token in normalized
        for token in ("SUS304", "A240-304", "SS304", "STAINLESS")
    ):
        return STAINLESS_304_DENSITY_KG_PER_MM3
    return STEEL_DENSITY_KG_PER_MM3


def _cylinder_volume(diameter_mm: float, length_mm: float) -> float:
    return pi * diameter_mm**2 / 4 * length_mm


def _hex_prism_volume(across_flats_mm: float, height_mm: float) -> float:
    return sqrt(3) / 2 * across_flats_mm**2 * height_mm


def theoretical_hex_nut_weight(
    nominal_diameter_mm: float,
    *,
    density_kg_per_mm3: float = STEEL_DENSITY_KG_PER_MM3,
) -> float:
    """Estimate one finished hex nut from explicit proportional geometry."""

    diameter = float(nominal_diameter_mm)
    across_flats = 1.5 * diameter
    height = 0.8 * diameter
    bore = 0.85 * diameter
    net_volume = max(
        0.0,
        _hex_prism_volume(across_flats, height)
        - _cylinder_volume(bore, height),
    )
    return net_volume * density_kg_per_mm3


def estimate_u_bolt_assembly(
    nominal_diameter_mm: float,
    developed_length_mm: float,
    *,
    nut_count: int = 0,
    density_kg_per_mm3: float = STEEL_DENSITY_KG_PER_MM3,
) -> dict | None:
    """Estimate a U-bolt rod plus explicitly released/shown hex nuts.

    The caller must derive the centre-line developed length from its own
    source drawing.  This prevents a straight-bolt parser from treating a
    U-bolt leg dimension as the whole rod length.
    """

    diameter = float(nominal_diameter_mm)
    developed = float(developed_length_mm)
    nuts = max(0, int(nut_count))
    if diameter <= 0 or developed <= 0:
        return None
    rod = _cylinder_volume(diameter, developed) * density_kg_per_mm3
    nut_each = theoretical_hex_nut_weight(
        diameter,
        density_kg_per_mm3=density_kg_per_mm3,
    )
    nut_total = nuts * nut_each
    return {
        "unit_weight_kg": round(rod + nut_total, 3),
        "nominal_diameter_mm": diameter,
        "developed_length_mm": developed,
        "nut_count": nuts,
        "density_kg_per_mm3": density_kg_per_mm3,
        "components_kg": {
            "u_bolt_rod": round(rod, 6),
            "proportional_hex_nuts": round(nut_total, 6),
        },
        "weight_basis": (
            "engineering estimate from source-derived U-bolt centre-line "
            "development and proportional hex nuts"
        ),
        "requires_supplier_confirmation": True,
    }


def _hex_head_weight(
    nominal_diameter_mm: float,
    *,
    density_kg_per_mm3: float,
) -> float:
    diameter = float(nominal_diameter_mm)
    return (
        _hex_prism_volume(1.5 * diameter, 0.625 * diameter)
        * density_kg_per_mm3
    )


def _washer_weight(
    nominal_diameter_mm: float,
    *,
    density_kg_per_mm3: float,
) -> float:
    diameter = float(nominal_diameter_mm)
    volume = (
        pi
        / 4
        * ((2.0 * diameter) ** 2 - (1.1 * diameter) ** 2)
        * (0.15 * diameter)
    )
    return volume * density_kg_per_mm3


def _expansion_sleeve_weight(
    nominal_diameter_mm: float,
    length_mm: float,
    *,
    density_kg_per_mm3: float,
) -> float:
    """Conservative proportional sleeve envelope, not a product-catalog mass."""

    diameter = float(nominal_diameter_mm)
    sleeve_length = 0.45 * float(length_mm)
    volume = (
        pi
        / 4
        * ((1.5 * diameter) ** 2 - (1.1 * diameter) ** 2)
        * sleeve_length
    )
    return volume * density_kg_per_mm3


def estimate_fastener(
    spec: str,
    *,
    kind: str = "machine_bolt_with_nut",
    washer_count: int | None = None,
    density_kg_per_mm3: float = STEEL_DENSITY_KG_PER_MM3,
) -> dict | None:
    """Estimate one fastener set when its nominal geometry is known.

    Supported kinds:

    - ``machine_bolt_with_nut``: shank + hex head + one nut.
    - ``foundation_bolt``: nominal bent/straight rod + one nut + one washer.
    - ``expansion_bolt``: nominal stud + nut + washer + proportional sleeve.
    - ``bolt_only``: shank + hex head.
    """

    parsed = parse_fastener_diameter_length(spec)
    if parsed is None:
        return None
    diameter, length = parsed
    normalized_kind = str(kind or "machine_bolt_with_nut").strip().lower()
    if washer_count is None:
        washer_count = 1 if "WASHER" in str(spec).upper() else 0
    washer_count = max(0, int(washer_count))

    shank = _cylinder_volume(diameter, length) * density_kg_per_mm3
    head = 0.0
    nut = 0.0
    sleeve = 0.0

    if normalized_kind == "bolt_only":
        head = _hex_head_weight(
            diameter,
            density_kg_per_mm3=density_kg_per_mm3,
        )
    elif normalized_kind == "foundation_bolt":
        nut = theoretical_hex_nut_weight(
            diameter,
            density_kg_per_mm3=density_kg_per_mm3,
        )
        washer_count = max(1, washer_count)
    elif normalized_kind == "expansion_bolt":
        nut = theoretical_hex_nut_weight(
            diameter,
            density_kg_per_mm3=density_kg_per_mm3,
        )
        washer_count = max(1, washer_count)
        sleeve = _expansion_sleeve_weight(
            diameter,
            length,
            density_kg_per_mm3=density_kg_per_mm3,
        )
    else:
        normalized_kind = "machine_bolt_with_nut"
        head = _hex_head_weight(
            diameter,
            density_kg_per_mm3=density_kg_per_mm3,
        )
        nut = theoretical_hex_nut_weight(
            diameter,
            density_kg_per_mm3=density_kg_per_mm3,
        )

    washer_each = _washer_weight(
        diameter,
        density_kg_per_mm3=density_kg_per_mm3,
    )
    washer_total = washer_each * washer_count
    total = shank + head + nut + washer_total + sleeve
    return {
        "unit_weight_kg": round(total, 3),
        "nominal_diameter_mm": diameter,
        "nominal_length_mm": length,
        "kind": normalized_kind,
        "washer_count": washer_count,
        "density_kg_per_mm3": density_kg_per_mm3,
        "components_kg": {
            "nominal_shank_or_rod": round(shank, 6),
            "proportional_hex_head": round(head, 6),
            "proportional_hex_nut": round(nut, 6),
            "proportional_washers": round(washer_total, 6),
            "proportional_expansion_sleeve": round(sleeve, 6),
        },
        "weight_basis": (
            "engineering estimate from nominal diameter/length geometry; "
            "hex/sleeve proportions are not supplier finished-product mass"
        ),
        "requires_supplier_confirmation": True,
    }


def estimate_metric_fastener(
    spec: str,
    *,
    kind: str = "machine_bolt_with_nut",
    washer_count: int | None = None,
    density_kg_per_mm3: float = STEEL_DENSITY_KG_PER_MM3,
) -> dict | None:
    """Backward-compatible alias; imperial project spellings are also read."""

    return estimate_fastener(
        spec,
        kind=kind,
        washer_count=washer_count,
        density_kg_per_mm3=density_kg_per_mm3,
    )


def apply_fastener_estimate(
    entry,
    *,
    kind: str,
    washer_count: int | None = None,
) -> dict | None:
    """Apply a theoretical dimensioned-fastener mass to a BOM entry."""

    estimate = estimate_fastener(
        getattr(entry, "spec", ""),
        kind=kind,
        washer_count=washer_count,
        density_kg_per_mm3=fastener_density_for_material(
            getattr(entry, "material", "")
        ),
    )
    if estimate is None:
        return None
    unit_weight = float(estimate["unit_weight_kg"])
    entry.unit_weight = unit_weight
    entry.total_weight = round(unit_weight * entry.quantity, 2)
    entry.weight_output = round(entry.factor * entry.total_weight, 2)
    entry.length = float(estimate["nominal_length_mm"])
    entry.density_g_cm3 = float(estimate["density_kg_per_mm3"]) * 1e6
    entry.density_source = "core.fastener_weight.nominal_geometry_estimate"
    entry.density_requires_review = True
    entry.geometry.parameters["weight_estimate"] = estimate
    return estimate


def apply_metric_fastener_estimate(
    entry,
    *,
    kind: str,
    washer_count: int | None = None,
) -> dict | None:
    """Backward-compatible alias for :func:`apply_fastener_estimate`."""

    return apply_fastener_estimate(
        entry,
        kind=kind,
        washer_count=washer_count,
    )
