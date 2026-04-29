"""Canonical material identity catalog.

Phase 2B introduces material identity as a lookup-only scaffold. Runtime BOM
output continues to use existing material strings until later migration phases
explicitly opt in.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class MaterialIdentity:
    """Canonical material record used to normalize equivalent material names."""

    canonical_id: str
    display_name: str
    family: str
    aliases: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


MATERIAL_CATALOG: Mapping[str, MaterialIdentity] = {
    "ASTM_A36_OR_JIS_SS400": MaterialIdentity(
        canonical_id="ASTM_A36_OR_JIS_SS400",
        display_name="A36 / SS400",
        family="carbon_steel",
        aliases=("A36/SS400", "A36 / SS400", "ASTM A36", "SS400", "A36"),
    ),
    "JIS_SUS304": MaterialIdentity(
        canonical_id="JIS_SUS304",
        display_name="SUS304",
        family="stainless_steel",
        aliases=("SUS304", "SS304", "304 SS"),
    ),
    "JIS_SUS316": MaterialIdentity(
        canonical_id="JIS_SUS316",
        display_name="SUS316",
        family="stainless_steel",
        aliases=("SUS316", "SS316", "316 SS"),
    ),
    "ASTM_A193_B7": MaterialIdentity(
        canonical_id="ASTM_A193_B7",
        display_name="A193 B7",
        family="alloy_steel_bolting",
        aliases=("A193 B7", "ASTM A193 B7"),
    ),
    "ASTM_A193_B16": MaterialIdentity(
        canonical_id="ASTM_A193_B16",
        display_name="A193 B16",
        family="alloy_steel_bolting",
        aliases=("A193 B16", "ASTM A193 B16"),
    ),
    "ASTM_A194_2H": MaterialIdentity(
        canonical_id="ASTM_A194_2H",
        display_name="A194 2H",
        family="alloy_steel_nut",
        aliases=("A194 2H", "ASTM A194 2H"),
    ),
    "ASTM_A194_4": MaterialIdentity(
        canonical_id="ASTM_A194_4",
        display_name="A194 4",
        family="alloy_steel_nut",
        aliases=("A194 4", "ASTM A194 4"),
    ),
    "ASTM_A194_4_S3": MaterialIdentity(
        canonical_id="ASTM_A194_4_S3",
        display_name="A194 4 / S3",
        family="alloy_steel_nut",
        aliases=("A194 4 / S3", "A194 4/S3", "ASTM A194 4 S3"),
    ),
    "ASTM_A320_L7": MaterialIdentity(
        canonical_id="ASTM_A320_L7",
        display_name="A320 L7",
        family="low_temperature_bolting",
        aliases=("A320 L7", "ASTM A320 L7"),
    ),
    "ASTM_SA_240": MaterialIdentity(
        canonical_id="ASTM_SA_240",
        display_name="SA-240",
        family="plate",
        aliases=("SA-240", "SA240", "ASTM SA-240"),
    ),
    "ASTM_SA_106_GR_B": MaterialIdentity(
        canonical_id="ASTM_SA_106_GR_B",
        display_name="SA-106 Gr.B",
        family="pipe",
        aliases=("SA-106 Gr.B", "SA106 Gr.B", "SA-106 Grade B", "ASTM A106 Grade B"),
    ),
    "NICKEL_ALLOY_INCONEL": MaterialIdentity(
        canonical_id="NICKEL_ALLOY_INCONEL",
        display_name="INCONEL",
        family="nickel_alloy",
        aliases=("INCONEL",),
        notes=("Generic override material identity; grade is unspecified.",),
    ),
}


def normalize_material_alias(material_name: str) -> str:
    """Return a stable comparison key for material aliases."""

    token = str(material_name).strip().upper()
    token = token.replace("-", "")
    token = token.replace(".", "")
    token = token.replace("/", " / ")
    token = " ".join(token.split())
    return token


def _build_alias_map() -> dict[str, str]:
    aliases: dict[str, str] = {}
    for canonical_id, identity in MATERIAL_CATALOG.items():
        aliases[normalize_material_alias(canonical_id)] = canonical_id
        aliases[normalize_material_alias(identity.display_name)] = canonical_id
        for alias in identity.aliases:
            aliases[normalize_material_alias(alias)] = canonical_id
    return aliases


MATERIAL_ALIAS_MAP: Mapping[str, str] = _build_alias_map()


def resolve_material_identity(material_name: str) -> MaterialIdentity | None:
    """Resolve a material string to a canonical identity if the alias is known."""

    canonical_id = MATERIAL_ALIAS_MAP.get(normalize_material_alias(material_name))
    if canonical_id is None:
        return None
    return MATERIAL_CATALOG[canonical_id]


def canonical_material_id(material_name: str) -> str | None:
    """Return the canonical id for a material string, or ``None`` if unknown."""

    identity = resolve_material_identity(material_name)
    return identity.canonical_id if identity else None
