"""Shared helpers for hardware material specifications."""

from __future__ import annotations

from .hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)


def material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


SUPPORT_PIPE_A53GRB = material_spec(HardwareKind.SUPPORT_PIPE, "A53Gr.B")
STRUCTURAL_A36_SS400 = material_spec(HardwareKind.STRUCTURAL_STRUT, "A36/SS400")
SUPPORT_PLATE_A36_SS400 = material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")
PLATE_LUG_A36_SS400 = material_spec(HardwareKind.PLATE_LUG, "A36/SS400")
ANCHOR_BOLT_SUS304 = material_spec(HardwareKind.ANCHOR_BOLT, "SUS304")
EXPANSION_BOLT_SUS304 = material_spec(HardwareKind.EXPANSION_BOLT, "SUS304")
U_BOLT_A36_SS400 = material_spec(HardwareKind.U_BOLT, "A36/SS400")
THREADED_ROD_A307_HDG = material_spec(HardwareKind.THREADED_ROD, "A307Gr.B(HDG)")
HEAVY_HEX_NUT_A307_HDG = material_spec(HardwareKind.HEAVY_HEX_NUT, "A307Gr.B(HDG)")
CLAMP_BODY_A36_SS400 = material_spec(HardwareKind.CLAMP_BODY, "A36/SS400")
COLD_SHOE_INSULATION_CLAMP_M47 = material_spec(
    HardwareKind.COLD_SHOE_INSULATION_CLAMP,
    "M-47",
)
