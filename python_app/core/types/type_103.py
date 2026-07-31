"""Type 103 source-aware four-anchor support plate (D-112)."""

from __future__ import annotations

import math

from ..config_loader import load_config
from ..models import AnalysisResult, HolePattern
from ..parser import get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference, retire_entry_weight


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("103", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 103: 尚未建立來源 profile {profile_id}"
        return result

    support_no = get_part(fullstring, 2) or ""
    figure = (get_part(fullstring, 3) or "").upper()
    row = profile["rows"].get(support_no)
    if not row:
        result.error = (
            f"Type 103 / {profile_id}: D-112 未表列 support no. {support_no}"
        )
        return result
    if figure not in {"A", "B", "C"}:
        result.error = "Type 103 格式應為 103-{SUPPORT NO.}-{A|B|C}"
        return result

    drawing = profile["drawing"]
    revision = profile["revision"]
    plate_qty = 2 if figure == "C" else 1
    outside = row["A"] + 2 * row["B"]
    hole_dia = row.get("hole_diameter_mm")
    gross_area = outside**2
    cutout_area = (
        4 * math.pi * hole_dia**2 / 4
        if hole_dia is not None
        else 0
    )
    add_plate_entry(
        result,
        outside,
        outside,
        row["T"],
        "D-112 FOUR-HOLE SUPPORT PLATE",
        "A36/SS400",
        plate_qty=plate_qty,
        gross_area_mm2=gross_area,
        cutout_area_mm2=cutout_area,
        net_area_mm2=gross_area - cutout_area,
        formula=(
            "(A+2B)^2 - 4*PI*d^2/4"
            if hole_dia is not None
            else "(A+2B)^2 gross; drilled-hole diameter TBD"
        ),
        shape_spec=(
            f"{outside}x{outside}x{row['T']}t; "
            f"4-DIA{hole_dia if hole_dia is not None else 'TBD'}; "
            f"PITCH={row['A']}x{row['A']}; QTY{plate_qty}"
        ),
        shape_kind="four_anchor_support_plate",
    )
    plate = result.entries[-1]
    plate.geometry.component_id = "D112-FOUR-HOLE-SUPPORT-PLATE"
    plate.geometry.source_drawing = drawing
    plate.geometry.source_revision = revision
    if hole_dia is not None:
        plate.geometry.holes = HolePattern(
            pattern="rect",
            pitch_x=row["A"],
            pitch_y=row["A"],
            diameter=hole_dia,
            fastener_spec=row["anchor_spec"],
            count=4,
        )
    plate.geometry.parameters = {
        "support_no": support_no,
        "figure": figure,
        "piece_count": plate_qty,
        "A_mm": row["A"],
        "B_mm": row["B"],
        "outside_mm": outside,
        "thickness_T_mm": row["T"],
        "hole_diameter_mm": hole_dia,
        "hole_count_per_plate": 4,
        "anchor_spec": row["anchor_spec"],
    }
    plate.geometry.fabrication_ready = hole_dia is not None

    anchor_qty = 4 * plate_qty
    blockers: list[str] = []
    if hole_dia is None:
        hole_blocker = (
            "D-112 此來源的表格 d 是 expansion-bolt nominal size，"
            "不是已核定的 drilled-hole diameter；鋼板外框與孔距已知，"
            "但孔徑確認前不計淨重、不宣稱可加工"
        )
        retire_entry_weight(plate, blocker=hole_blocker)
        blockers.append(hole_blocker)
    anchor_blocker = (
        f"D-112 指定 {row['anchor_spec']} anchors、每片 4 組，但未提供 "
        "finished expansion/embedded bolt unit-weight；鋼板可加工，錨栓保留採購 reference"
    )
    add_reference(
        result,
        name="D-112 ANCHOR BOLT SET",
        spec=f"{row['anchor_spec']}; QTY{anchor_qty}",
        material=profile["anchor_material"],
        quantity=anchor_qty,
        category="螺栓類",
        component_id="D112-ANCHOR-BOLTS",
        drawing=drawing,
        revision=revision,
        shape_kind="purchased_anchor_bolt_set",
        parameters={
            "support_no": support_no,
            "figure": figure,
            "quantity": anchor_qty,
            "not_furnished": profile["anchors_not_furnished"],
        },
        blocker=anchor_blocker,
        manufacturing_type="purchased",
    )
    blockers.append(anchor_blocker)
    result.warnings.extend(blockers)
    result.meta["type_id"] = "103"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": revision,
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": plate.geometry.parameters,
        "not_furnished": profile["not_furnished_members"],
    }
    result.evidence.append(
        make_evidence(
            "type103_d112_row",
            plate.geometry.parameters,
            "visual_transcription",
            source=drawing,
            confidence=0.99,
        )
    )
    return result
