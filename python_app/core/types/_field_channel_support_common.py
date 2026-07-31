"""Shared D-137/D-138 field-cut channel support builder."""

from __future__ import annotations

import math

from ..fastener_weight import apply_metric_fastener_estimate
from ..models import AnalysisResult, HolePattern, set_remark
from ..plate import add_plate_entry
from ..steel import add_steel_section_entry
from ._source_reference import add_reference


def parse_hundred_mm_token(token: str, suffix: str) -> int | None:
    value = str(token or "").strip().upper()
    if not value.endswith(suffix) or not value[: -len(suffix)].isdigit():
        return None
    return int(value[: -len(suffix)]) * 100


def add_field_channel_support(
    result: AnalysisResult,
    *,
    type_id: str,
    length_mm: int,
    profile: dict,
) -> list[str]:
    drawing = profile["drawing"]
    revision = profile["revision"]
    member = profile["member"]
    blockers: list[str] = []
    field_blocker = (
        f"D-{profile['detail_no']} NOTE: length L shall be cut to suit by field；"
        "designation L 可作備料基準，但 finished end cut/現場 fit-up 發圖前需確認"
    )
    if member["weight_ready"]:
        add_steel_section_entry(
            result,
            member["kind"],
            member["spec"],
            length_mm,
            member["quantity"],
            member["material"],
        )
        section = result.entries[-1]
        section.geometry.component_id = f"D{profile['detail_no']}-MEMBER-1"
        section.geometry.source_drawing = drawing
        section.geometry.source_revision = revision
        section.geometry.shape_kind = "field_cut_cross_channel"
        section.geometry.shape_spec = (
            f"{member['source_spec']}; L={length_mm}; "
            f"QTY{member['quantity']}"
        )
        section.geometry.parameters = {
            "cut_length_L_mm": length_mm,
            "piece_count": member["quantity"],
            "source_section": member["source_spec"],
            "field_fit": True,
            "end_offset_each_mm": 50,
            "weld_mm": 6,
        }
        section.geometry.fabrication_ready = False
        section.geometry.fabrication_blockers = [field_blocker]
        set_remark(section, field_blocker)
    else:
        section_blocker = (
            f"{field_blocker}；{member['source_spec']} 尚無核定 kg/m，"
            "不得套用相近 Channel 單重"
        )
        add_reference(
            result,
            name="FIELD-CUT CHANNEL MEMBER",
            spec=(
                f"{member['source_spec']}; L={length_mm}; "
                f"QTY{member['quantity']}"
            ),
            material=member["material"],
            quantity=member["quantity"],
            category="型鋼類",
            component_id=f"D{profile['detail_no']}-MEMBER-1",
            drawing=drawing,
            revision=revision,
            shape_kind="field_cut_cross_channel",
            parameters={
                "cut_length_L_mm": length_mm,
                "piece_count": member["quantity"],
                "source_section": member["source_spec"],
                "field_fit": True,
                "end_offset_each_mm": 50,
                "weld_mm": 6,
            },
            blocker=section_blocker,
            manufacturing_type="raw_cut",
        )
        field_blocker = section_blocker
    blockers.append(field_blocker)

    plate = profile["base_plate"]
    gross_area = plate["length_mm"] * plate["width_mm"]
    hole_area = (
        plate["holes_per_plate"]
        * math.pi
        * plate["hole_diameter_mm"] ** 2
        / 4
    )
    add_plate_entry(
        result,
        plate["length_mm"],
        plate["width_mm"],
        plate["thickness_mm"],
        f"D-{profile['detail_no']} FOUR-HOLE BASE PLATES",
        plate["material"],
        plate_qty=plate["quantity"],
        gross_area_mm2=gross_area,
        cutout_area_mm2=hole_area,
        net_area_mm2=gross_area - hole_area,
        formula="170*W - 4*PI*19^2/4 per plate",
        shape_spec=(
            f"{plate['length_mm']}x{plate['width_mm']}x"
            f"{plate['thickness_mm']}t; "
            f"4-DIA{plate['hole_diameter_mm']}; "
            f"QTY{plate['quantity']}"
        ),
        shape_kind="four_anchor_base_plate",
    )
    base = result.entries[-1]
    base.geometry.component_id = f"D{profile['detail_no']}-BASE-PLATES"
    base.geometry.source_drawing = drawing
    base.geometry.source_revision = revision
    base.geometry.holes = HolePattern(
        pattern="rect",
        pitch_x=plate["pitch_x_mm"],
        pitch_y=plate["pitch_y_mm"],
        diameter=plate["hole_diameter_mm"],
        fastener_spec=profile["anchor"]["spec"],
        count=plate["holes_per_plate"],
    )
    base.geometry.parameters = {
        "piece_count": plate["quantity"],
        "length_mm": plate["length_mm"],
        "width_mm": plate["width_mm"],
        "thickness_mm": plate["thickness_mm"],
        "hole_count_per_plate": plate["holes_per_plate"],
        "hole_diameter_mm": plate["hole_diameter_mm"],
        "hole_pitch_x_mm": plate["pitch_x_mm"],
        "hole_pitch_y_mm": plate["pitch_y_mm"],
        "edge_x_mm": 40,
        "edge_y_mm": 40,
        "channel_end_offset_each_mm": 50,
        "weld_mm": 6,
    }
    base.geometry.fabrication_ready = True

    anchor = profile["anchor"]
    anchor_blocker = (
        f"D-{profile['detail_no']} specifies {anchor['quantity']} "
        f"{anchor['spec']} expansion bolts；重量依名義M×L與比例套管幾何估算，"
        "EB2供應商成品重量仍待確認"
    )
    add_reference(
        result,
        name="EB2 EXPANSION BOLT",
        spec=anchor["spec"],
        material=anchor["material"],
        quantity=anchor["quantity"],
        category="螺栓類",
        component_id=f"D{profile['detail_no']}-EB2-ANCHORS",
        drawing=drawing,
        revision=revision,
        shape_kind="purchased_expansion_bolt",
        parameters={
            "quantity": anchor["quantity"],
            "bolt_spec": anchor["spec"],
            "not_furnished": anchor["not_furnished"],
        },
        blocker=anchor_blocker,
        manufacturing_type="purchased",
    )
    apply_metric_fastener_estimate(
        result.entries[-1],
        kind="expansion_bolt",
    )
    blockers.append(anchor_blocker)
    return blockers
