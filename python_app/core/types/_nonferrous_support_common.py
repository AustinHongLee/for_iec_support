"""Shared M-57/M-58/M-59 fabrication builders for Types 118~120."""

from __future__ import annotations

import math

from data.m57_table import get_m57_by_line_size
from data.m58_table import get_m58_by_line_size
from data.m59_table import get_m59_by_line_size

from ..bolt import add_custom_entry
from ..models import AnalysisResult, HolePattern, set_remark
from ..plate import add_plate_entry
from ._source_reference import add_reference


STEEL_DENSITY_KG_PER_MM3 = 7.85e-6


def _finish_plate(
    entry,
    *,
    component_id: str,
    drawing: str,
    revision: str,
    shape_kind: str,
    parameters: dict,
    fabrication_ready: bool = True,
):
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = shape_kind
    entry.geometry.parameters = parameters
    entry.geometry.fabrication_ready = fabrication_ready


def add_m57_saddle(
    result: AnalysisResult,
    *,
    line_size: float,
    pipe_od_mm: float,
    drawing: str,
    revision: str,
    component_prefix: str,
) -> tuple[dict, list[str]]:
    row = get_m57_by_line_size(line_size)
    if not row:
        raise ValueError(f'M-57 未表列 {line_size:g}"')
    dims = row["dimensions_mm"]
    width = dims["W"]
    thickness = dims["T"]
    lug_size = dims["A"]
    hole_dia = dims["H"]
    inside_dia = pipe_od_mm + 6
    neutral_developed = math.pi * (inside_dia + thickness)
    each_half_developed = neutral_developed / 2

    add_plate_entry(
        result,
        each_half_developed,
        width,
        thickness,
        "M-57 ROLLED SADDLE HALF",
        "CARBON STEEL",
        plate_qty=2,
        formula="2 * [PI * (inside_dia + T) / 2] * W * T",
        shape_spec=(
            f"HALF-SADDLE; DEVELOPED "
            f"{each_half_developed:.3f}x{width}x{thickness}t; QTY2"
        ),
        shape_kind="split_rolled_saddle",
    )
    _finish_plate(
        result.entries[-1],
        component_id=f"{component_prefix}-M57-ROLLED-SADDLE-HALVES",
        drawing=drawing,
        revision=revision,
        shape_kind="split_rolled_saddle",
        parameters={
            "line_size_in": line_size,
            "actual_pipe_od_mm": pipe_od_mm,
            "inside_diameter_D_mm": inside_dia,
            "thickness_T_mm": thickness,
            "axial_width_W_mm": width,
            "piece_count": 2,
            "each_piece_arc_deg": 180,
            "each_piece_developed_length_mm": each_half_developed,
            "neutral_developed_total_mm": neutral_developed,
            "roll_inside_diameter_mm": inside_dia,
        },
    )

    hole_area = math.pi * hole_dia**2 / 4
    net_area = lug_size**2 - hole_area
    add_plate_entry(
        result,
        lug_size,
        lug_size,
        thickness,
        "M-57 DRILLED LUG PLATES",
        "CARBON STEEL",
        plate_qty=4,
        gross_area_mm2=lug_size**2,
        cutout_area_mm2=hole_area,
        net_area_mm2=net_area,
        formula="A*A - PI*H^2/4",
        shape_spec=f"{lug_size}x{lug_size}x{thickness}t; DIA{hole_dia}; QTY4",
        shape_kind="drilled_saddle_lug",
    )
    lug = result.entries[-1]
    lug.geometry.holes = HolePattern(
        pattern="single_center",
        diameter=hole_dia,
        count=1,
        fastener_spec=row["machine_bolt_J"],
    )
    _finish_plate(
        lug,
        component_id=f"{component_prefix}-M57-DRILLED-LUGS",
        drawing=drawing,
        revision=revision,
        shape_kind="drilled_saddle_lug",
        parameters={
            "line_size_in": line_size,
            "piece_count": 4,
            "A_mm": lug_size,
            "thickness_T_mm": thickness,
            "hole_diameter_H_mm": hole_dia,
            "weld": "3 SIDES TYP.",
        },
    )

    bolt_blocker = (
        "M-57 給 machine-bolt 規格與材質，但沒有 finished bolt/nut "
        "source unit-weight；保留採購 reference"
    )
    add_reference(
        result,
        name="M-57 MACHINE BOLT / NUT SET",
        spec=f'{row["machine_bolt_J"]}; QTY2',
        material="A307 Gr.B / A563 Gr.A",
        quantity=row["machine_bolt_quantity"],
        category="螺栓類",
        component_id=f"{component_prefix}-M57-MACHINE-BOLTS",
        drawing=drawing,
        revision=revision,
        shape_kind="purchased_machine_bolt_set",
        parameters={
            "line_size_in": line_size,
            "bolt_spec": row["machine_bolt_J"],
            "quantity": row["machine_bolt_quantity"],
            "lug_plate_quantity": row["lug_plate_quantity"],
            "joint_basis": "four lugs form two opposed bolt-and-nut joints",
        },
        blocker=bolt_blocker,
        manufacturing_type="purchased",
    )

    rubber_neutral_developed = math.pi * (pipe_od_mm + 3)
    rubber_each_half_developed = rubber_neutral_developed / 2
    rubber_blocker = (
        "3 mm rubber/neoprene lining 的兩片半圓 neutral-line 展開尺寸可定義，"
        "但來源未給材料密度/供應單重與 seam/compression allowance；"
        "不得以鋼材密度計重，finished cut 需材料商確認"
    )
    add_reference(
        result,
        name="3MM RUBBER / NEOPRENE LINING",
        spec=(
            f"3t x {width}W x {rubber_each_half_developed:.3f} "
            "HALF-WRAP NEUTRAL DEVELOPED; QTY2"
        ),
        material="RUBBER OR NEOPRENE",
        quantity=2,
        category="墊片類",
        component_id=f"{component_prefix}-RUBBER-LINING",
        drawing=drawing,
        revision=revision,
        shape_kind="rolled_elastomer_lining",
        parameters={
            "actual_pipe_od_mm": pipe_od_mm,
            "thickness_mm": 3,
            "axial_width_mm": width,
            "inside_diameter_mm": pipe_od_mm,
            "outside_diameter_mm": pipe_od_mm + 6,
            "neutral_diameter_mm": pipe_od_mm + 3,
            "piece_count": 2,
            "each_piece_arc_deg": 180,
            "each_piece_neutral_developed_length_mm": (
                rubber_each_half_developed
            ),
            "neutral_developed_total_mm": rubber_neutral_developed,
        },
        blocker=rubber_blocker,
        manufacturing_type="raw_cut",
    )
    return row, [bolt_blocker, rubber_blocker]


def add_m58_ubolt(
    result: AnalysisResult,
    *,
    line_size: float,
    pipe_od_mm: float,
    drawing: str,
    revision: str,
    component_prefix: str,
) -> tuple[dict, list[str]]:
    row = get_m58_by_line_size(line_size)
    if not row:
        raise ValueError(f'M-58 未表列 {line_size:g}"')
    rod_dia = row["rod_dia_mm"]
    b_mm = pipe_od_mm + 18
    centerline_span_mm = b_mm + rod_dia
    e_mm = row["dimensions_mm"]["E"]
    developed = math.pi * centerline_span_mm / 2 + 2 * e_mm
    weight = (
        math.pi * rod_dia**2 / 4
        * developed
        * STEEL_DENSITY_KG_PER_MM3
    )
    add_custom_entry(
        result,
        "M-58 TYPE-A U-BOLT",
        f"DIA{rod_dia:g}; B={b_mm:g}; E={e_mm}; DEV={developed:.3f}",
        "CARBON STEEL",
        1,
        round(weight, 2),
        "PC",
        category="螺栓類",
        item_class="fabricated_hardware",
        manufacturing_type="bend",
    )
    entry = result.entries[-1]
    entry.length = developed
    entry.geometry.component_id = f"{component_prefix}-M58-U-BOLT"
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "u_bolt_round_bar"
    entry.geometry.shape_spec = (
        f"ROD DIA{rod_dia:g}; INSIDE CLEAR B={b_mm:g}; "
        f"CENTERLINE SPAN={centerline_span_mm:g}; "
        f"E={e_mm}; DEVELOPED={developed:.3f}"
    )
    entry.geometry.parameters = {
        "line_size_in": line_size,
        "actual_pipe_od_mm": pipe_od_mm,
        "rod_diameter_mm": rod_dia,
        "inside_clear_B_mm": b_mm,
        "centerline_span_mm": centerline_span_mm,
        "D_mm": row["dimensions_mm"]["D"],
        "E_mm": e_mm,
        "developed_length_mm": developed,
        "bend_arc_deg": 180,
    }
    entry.geometry.fabrication_ready = True

    nut_blocker = (
        "M-58 指定 four finished hex nuts，但沒有 supplier unit-weight；"
        "U-bolt rod 重量可算，nuts 保留零重量採購 reference"
    )
    add_reference(
        result,
        name="M-58 FINISHED HEX NUTS",
        spec=f'FOR ROD {row["rod_dia_in"]:g}in; QTY4',
        material="CARBON STEEL",
        quantity=4,
        category="螺栓類",
        component_id=f"{component_prefix}-M58-HEX-NUTS",
        drawing=drawing,
        revision=revision,
        shape_kind="purchased_finished_hex_nut",
        parameters={
            "rod_diameter_mm": rod_dia,
            "quantity": 4,
        },
        blocker=nut_blocker,
        manufacturing_type="purchased",
    )
    return row, [nut_blocker]


def add_m59_uband(
    result: AnalysisResult,
    *,
    line_size: float,
    pipe_od_mm: float,
    drawing: str,
    revision: str,
    component_prefix: str,
) -> tuple[dict, list[str]]:
    row = get_m59_by_line_size(line_size)
    if not row:
        raise ValueError(f'M-59 未表列 {line_size:g}"')
    dims = row["dimensions_mm"]
    strip_width = dims["D"]
    thickness = dims["T"]
    inner_radius = pipe_od_mm / 2 + dims["G"] + 3
    straight_h = inner_radius - 3
    outside_width = 2 * (inner_radius + thickness)
    developed = math.pi * (inner_radius + thickness / 2) + 2 * straight_h
    add_plate_entry(
        result,
        developed,
        strip_width,
        thickness,
        "M-59 TYPE-A U-BAND",
        "CARBON STEEL GALVANIZED",
        formula="PI*(R+T/2)+2*H",
        shape_spec=(
            f"{developed:.3f} DEVELOPED x {strip_width} x {thickness}t; "
            f"R={inner_radius:.3f}; H={straight_h:.3f}"
        ),
        shape_kind="formed_u_band",
    )
    entry = result.entries[-1]
    _finish_plate(
        entry,
        component_id=f"{component_prefix}-M59-U-BAND",
        drawing=drawing,
        revision=revision,
        shape_kind="formed_u_band",
        parameters={
            "line_size_in": line_size,
            "actual_pipe_od_mm": pipe_od_mm,
            "strip_width_D_mm": strip_width,
            "thickness_T_mm": thickness,
            "gap_G_mm": dims["G"],
            "inside_radius_R_mm": inner_radius,
            "straight_leg_H_mm": straight_h,
            "outside_width_W_mm": outside_width,
            "neutral_developed_length_mm": developed,
            "bend_arc_deg": 180,
            "finish": "GALVANIZED",
        },
    )
    set_remark(entry, "M-59 Rev.1 exact formula; form after flat cutting")
    return row, []


def add_small_guide_plate(
    result: AnalysisResult,
    *,
    line_size: float,
    pipe_od_mm: float,
    row: dict,
    drawing: str,
    revision: str,
    component_prefix: str,
):
    b_mm = row["B"]
    hole_dia = row["D"]
    edge_l = row["L"]
    ubolt_dia = row["u_bolt_dia_mm"]
    pitch_p = pipe_od_mm + 18 + ubolt_dia
    plate_length = pitch_p + 2 * edge_l
    gross = plate_length * b_mm
    holes = 2 * math.pi * hole_dia**2 / 4
    add_plate_entry(
        result,
        plate_length,
        b_mm,
        6,
        "6T GUIDE / ANCHOR PLATE",
        "CARBON STEEL (GRADE TBD)",
        gross_area_mm2=gross,
        cutout_area_mm2=holes,
        net_area_mm2=gross - holes,
        formula="(P+2L)*B - 2*PI*D^2/4",
        shape_spec=(
            f"{plate_length:.3f}x{b_mm}x6t; "
            f"2-DIA{hole_dia}; P={pitch_p:.3f}"
        ),
        shape_kind="two_hole_guide_plate",
    )
    entry = result.entries[-1]
    entry.geometry.holes = HolePattern(
        pattern="linear_2",
        pitch_x=pitch_p,
        pitch_y=0,
        diameter=hole_dia,
        count=2,
    )
    _finish_plate(
        entry,
        component_id=f"{component_prefix}-TWO-HOLE-PLATE",
        drawing=drawing,
        revision=revision,
        shape_kind="two_hole_guide_plate",
        parameters={
            "line_size_in": line_size,
            "actual_pipe_od_mm": pipe_od_mm,
            "plate_length_mm": plate_length,
            "plate_width_B_mm": b_mm,
            "plate_thickness_mm": 6,
            "hole_diameter_D_mm": hole_dia,
            "hole_pitch_P_mm": pitch_p,
            "edge_L_mm": edge_l,
            "u_bolt_diameter_mm": ubolt_dia,
        },
    )
    return entry
