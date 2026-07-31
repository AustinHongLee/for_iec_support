"""Type 129 twin H-section field support (D-139)."""

from __future__ import annotations

import math

from ..config_loader import load_config
from ..fastener_weight import apply_metric_fastener_estimate
from ..models import AnalysisResult, HolePattern, set_remark
from ..parser import get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from ._field_channel_support_common import parse_hundred_mm_token
from ._source_reference import add_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("129", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 129: 尚未建立來源 profile {profile_id}"
        return result
    length = parse_hundred_mm_token(get_part(fullstring, 2) or "", "L")
    width = parse_hundred_mm_token(get_part(fullstring, 3) or "", "W")
    if length is None or width is None:
        result.error = "Type 129 格式應為 129-{L/100}L-{W/100}W"
        return result
    if length <= 0 or length > profile["L_max_mm"]:
        result.error = f"Type 129: L 必須 0 < L <= {profile['L_max_mm']} mm"
        return result
    if width < profile["W_min_mm"]:
        result.error = f"Type 129: W 必須 >= {profile['W_min_mm']} mm"
        return result

    drawing = profile["drawing"]
    revision = profile["revision"]
    member = profile["member"]
    field_blocker = (
        "D-139 NOTE 3: length L shall be cut to suit by field；"
        "直料備料重可算，finished end cut/fit-up 發圖前需現場確認"
    )
    add_steel_section_entry(
        result,
        member["kind"],
        member["spec"],
        length,
        member["quantity"],
        member["material"],
    )
    beams = result.entries[-1]
    beams.geometry.component_id = "D139-TWIN-H-SECTIONS"
    beams.geometry.source_drawing = drawing
    beams.geometry.source_revision = revision
    beams.geometry.shape_kind = "twin_field_cut_h_sections"
    beams.geometry.shape_spec = (
        f"{member['source_spec']}; L={length}; QTY{member['quantity']}"
    )
    beams.geometry.parameters = {
        "cut_length_L_mm": length,
        "piece_count": member["quantity"],
        "source_section": member["source_spec"],
        "centerline_spacing_W_mm": width,
        "field_fit": True,
        "weld_mm": 6,
        "source_description_conflict": (
            "BOM description says CHANNEL, size/view are H150x150x7x10"
        ),
    }
    beams.geometry.fabrication_ready = False
    beams.geometry.fabrication_blockers = [field_blocker]
    set_remark(beams, field_blocker)

    c_star = width - 150
    plate_width = width + 330
    hole_pitch_y = width + 250
    plate = profile["base_plate"]
    gross_area = plate["length_mm"] * plate_width
    hole_area = (
        plate["holes_per_plate"]
        * math.pi
        * plate["hole_diameter_mm"] ** 2
        / 4
    )
    add_plate_entry(
        result,
        plate["length_mm"],
        plate_width,
        plate["thickness_mm"],
        "D-139 TWIN-BEAM BASE PLATES",
        plate["material"],
        plate_qty=plate["quantity"],
        gross_area_mm2=gross_area,
        cutout_area_mm2=hole_area,
        net_area_mm2=gross_area - hole_area,
        formula="170*(480+C*) - 4*PI*19^2/4; C*=W-150",
        shape_spec=(
            f"{plate['length_mm']}x{plate_width}x"
            f"{plate['thickness_mm']}t; 4-DIA19; "
            f"QTY{plate['quantity']}"
        ),
        shape_kind="four_anchor_twin_beam_base_plate",
    )
    base = result.entries[-1]
    base.geometry.component_id = "D139-BASE-PLATES"
    base.geometry.source_drawing = drawing
    base.geometry.source_revision = revision
    base.geometry.holes = HolePattern(
        pattern="rect",
        pitch_x=90,
        pitch_y=hole_pitch_y,
        diameter=19,
        fastener_spec=profile["anchor"]["spec"],
        count=4,
    )
    base.geometry.parameters = {
        "piece_count": plate["quantity"],
        "length_mm": plate["length_mm"],
        "width_mm": plate_width,
        "thickness_mm": plate["thickness_mm"],
        "hole_count_per_plate": 4,
        "hole_diameter_mm": 19,
        "hole_pitch_x_mm": 90,
        "hole_pitch_y_mm": hole_pitch_y,
        "edge_x_mm": 40,
        "edge_y_mm": 40,
        "centerline_spacing_W_mm": width,
        "C_star_mm": c_star,
        "C_star_formula": "W - 150",
        "plate_width_formula": "480 + C* = W + 330",
        "weld_mm": 6,
    }
    base.geometry.fabrication_ready = True

    anchor = profile["anchor"]
    anchor_blocker = (
        "D-139 specifies 8 EB2-M16x125L expansion bolts，"
        "重量依名義M×L與比例套管幾何估算；供應商成品重量仍待確認"
    )
    add_reference(
        result,
        name="EB2 EXPANSION BOLT",
        spec=anchor["spec"],
        material=anchor["material"],
        quantity=anchor["quantity"],
        category="螺栓類",
        component_id="D139-EB2-ANCHORS",
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
    nomenclature_warning = (
        "D-139 BOM description says CHANNEL，but the listed size "
        "H150x150x7x10 and drawn section are treated as H-section"
    )
    blockers = [field_blocker, anchor_blocker, nomenclature_warning]
    result.warnings.extend(blockers)
    parameters = {
        "L_mm": length,
        "W_mm": width,
        "L_max_mm": profile["L_max_mm"],
        "W_min_mm": profile["W_min_mm"],
        "C_star_mm": c_star,
        "base_plate_width_mm": plate_width,
        "member_section": member["source_spec"],
    }
    result.meta["type_id"] = "129"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": revision,
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": parameters,
    }
    result.evidence.append(
        make_evidence(
            "type129_d139_twin_support",
            parameters,
            "visual_transcription",
            source=drawing,
            confidence=0.99,
        )
    )
    return result
