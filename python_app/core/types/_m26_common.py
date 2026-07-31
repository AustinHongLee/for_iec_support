"""Shared M-26 U-bolt expansion for Type 57/58/59 source profiles."""

from __future__ import annotations

from copy import deepcopy

from ..bolt import add_custom_entry
from ..component_roles import ComponentRole
from ..fastener_weight import theoretical_hex_nut_weight
from ..models import AnalysisResult, set_remark


def add_m26_ubolt(
    result: AnalysisResult,
    *,
    row: dict,
    drawing: str,
    revision: str,
    component_prefix: str,
    host_note: str = "",
    host_parameters: dict | None = None,
) -> list[str]:
    """Add one fabricated M-26 rod plus the four source-required nuts."""
    blockers = list(row["fabrication_blockers"])
    developed = row["rod_developed_length_mm"]
    rod_diameter = row["rod_diameter_mm"]
    note_prefix = f"{host_note}；" if host_note else ""

    add_custom_entry(
        result,
        "M-26 U-BOLT ROD",
        (
            f"{row['type']}; DIA{rod_diameter:g}; "
            f"B={row['B_centerline_mm']}; "
            f"D={row['D_thread_length_mm']}; "
            f"E={row['E_leg_to_bend_center_mm']}; "
            f"DEV={developed:.3f}"
        ),
        row["material"],
        1,
        round(row["rod_calculated_weight_kg"], 3),
        "PC",
        category="螺栓類",
        item_class="fabricated_hardware",
        manufacturing_type="bend_and_thread",
    )
    rod = result.entries[-1]
    rod.length = developed
    rod.geometry.component_id = f"{component_prefix}-U-BOLT-ROD"
    rod.geometry.source_drawing = drawing
    rod.geometry.source_revision = revision
    rod.geometry.shape_kind = "u_bolt_round_bar"
    rod.geometry.shape_spec = (
        f"ROD DIA{rod_diameter:g}; CENTERLINE B={row['B_centerline_mm']}; "
        f"OVERALL C={row['C_overall_mm']}; "
        f"E={row['E_leg_to_bend_center_mm']}; "
        f"THREAD D={row['D_thread_length_mm']}; "
        f"NOMINAL DEVELOPED={developed:.3f}"
    )
    rod.geometry.parameters = {
        **deepcopy(row),
        **deepcopy(host_parameters or {}),
        "quantity": 1,
        "nominal_developed_length_only": True,
        "manufacturing_cut_allowance_released": False,
    }
    rod.geometry.fabrication_ready = False
    rod.geometry.fabrication_blockers = blockers[:2]
    set_remark(rod, note_prefix + "；".join(blockers[:2]))

    nut_blocker = blockers[2]
    nut_weight = round(theoretical_hex_nut_weight(rod_diameter), 3)
    add_custom_entry(
        result,
        "M-26 FINISHED HEX NUTS",
        f'FOR ROD {row["rod_size_a"]}; QTY4',
        row["material"],
        row["finished_hex_nuts_per_set"],
        nut_weight,
        unit="PC",
        remark=note_prefix + nut_blocker,
        category="螺栓類",
        role=ComponentRole.NUT.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    nut = result.entries[-1]
    nut.geometry.component_id = f"{component_prefix}-FINISHED-HEX-NUTS"
    nut.geometry.source_drawing = drawing
    nut.geometry.source_revision = revision
    nut.geometry.shape_kind = "purchased_finished_hex_nut"
    nut.geometry.shape_spec = f'FOR ROD {row["rod_size_a"]}; QTY4'
    nut.geometry.parameters = {
        **deepcopy(host_parameters or {}),
        "rod_diameter_in": row["rod_diameter_in"],
        "rod_diameter_mm": rod_diameter,
        "quantity": row["finished_hex_nuts_per_set"],
        "estimated_unit_weight_kg": nut_weight,
        "weight_basis": (
            "proportional finished-hex-nut geometry at 7.85 g/cm3; "
            "supplier finished mass not provided by M-26"
        ),
    }
    nut.geometry.fabrication_ready = False
    nut.geometry.fabrication_blockers = [note_prefix + nut_blocker]
    nut.density_g_cm3 = 7.85
    nut.density_source = "core.fastener_weight.proportional_hex_nut_estimate"
    nut.density_requires_review = True
    set_remark(nut, note_prefix + nut_blocker)
    return blockers
