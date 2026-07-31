"""Type 36 source-aware member with M-34 lug plate (D-41)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..issues import register_source_envelope
from ..models import AnalysisResult, set_remark
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from ._lug_plate_common import lug_hole_count
from data.m34_table import get_m34_by_member


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("36", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 36: 尚未建立來源 profile {profile_id}"
        return result
    parts = str(fullstring).split("-")
    if len(parts) != 3 or not parts[2].isdigit():
        result.error = "Type 36: 格式應為 36-{M}-{HH}"
        return result
    member, h_mm = parts[1].upper(), int(parts[2]) * 100
    row = config[profile["table"]].get(member)
    if not row:
        result.error = f"Type 36 / {profile_id}: D-41未表列 MEMBER {member}"
        return result
    if h_mm <= 0:
        result.error = (
            f"Type 36 / {profile_id}: H={h_mm}超出{member} "
            f"0<H≤{row['H_MAX']}mm"
        )
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 36 / {profile_id}",
        source_ref=f"D-41 {member} H(MAX)",
        checks=(("H", h_mm, row["H_MAX"], True),),
    ):
        return result
    lug = get_m34_by_member(member)
    if not lug:
        result.error = f"Type 36: M-34無 {member} Lug Plate Type-C"
        return result
    holes = lug_hole_count(lug)

    ctx = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material",),
        legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,),
    )
    material = resolve_hardware_material(
        HardwareKind.STRUCTURAL_STRUT,
        service=ctx.service,
        overrides=ctx.material_overrides,
    )
    bolt_material = resolve_hardware_material(
        HardwareKind.ANCHOR_BOLT,
        service=ctx.service,
        overrides=ctx.material_overrides,
    )
    add_steel_section_entry(
        result, row["section_type"], row["lookup_dim"], h_mm, material=material
    )
    member_entry = result.entries[-1]
    member_entry.geometry.component_id = "D41-MEMBER"
    member_entry.geometry.source_drawing = profile["drawing"]
    member_entry.geometry.source_revision = profile["revision"]
    member_entry.geometry.shape_kind = "stock_section_cut"
    member_entry.geometry.shape_spec = f'{row["full_spec"]}; CUT H={h_mm}'
    member_entry.geometry.parameters = {"H_mm": h_mm, "fillet_weld_mm": 6}
    member_entry.geometry.fabrication_ready = True
    set_remark(member_entry, f"固定構件H={h_mm}")

    add_plate_entry(
        result,
        lug["A"],
        lug["B"],
        lug["T"],
        "LUG PLATE TYPE-C",
        material=material,
        plate_qty=1,
        bolt_switch=True,
        bolt_x=2 * lug["E"] + lug["F"],
        bolt_y=2 * (lug.get("G") or 0),
        bolt_hole=lug["J"],
        bolt_size=lug["K"],
        plate_role="lug_plate",
    )
    plate = result.entries[-1]
    plate.geometry.component_id = f'M34-{lug["type"]}'
    plate.geometry.source_drawing = "LUG-PLATE_TYPE-C_M-34.pdf"
    plate.geometry.source_revision = "1"
    plate.geometry.shape_kind = "lug_plate_type_c"
    plate.geometry.shape_spec = (
        f'{lug["type"]}; {lug["A"]}x{lug["B"]}x{lug["T"]}t; '
        f'{holes}-HOLE DIA{lug["J"]}'
    )
    plate.geometry.holes.count = holes
    plate.geometry.parameters.update(
        {
            "lgp_type": lug["type"],
            "hole_count": holes,
            "hole_diameter_mm": lug["J"],
            "E_mm": lug["E"],
            "F_mm": lug["F"],
            "G_mm": lug.get("G"),
            "H_mm": lug.get("H"),
        }
    )
    plate.geometry.fabrication_ready = True

    add_custom_entry(
        result,
        name="K BOLT",
        spec=lug["K"],
        material=bolt_material,
        quantity=holes,
        unit_weight=0,
        unit="PC",
    )
    bolt = result.entries[-1]
    bolt.geometry.component_id = "D41-K-BOLT"
    bolt.geometry.source_drawing = profile["drawing"]
    bolt.geometry.source_revision = profile["revision"]
    bolt.geometry.shape_kind = "purchased_fastener"
    bolt.geometry.parameters = {"spec": lug["K"], "quantity": holes}
    bolt.geometry.fabrication_ready = False
    bolt.geometry.fabrication_blockers = ["原圖/M-34未給bolt長度與單重"]
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": member,
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": ["K bolt長度/採購完整規格未標"],
    }
    result.warnings.append("K bolt數已按M-34孔數計；長度與單重未由原圖提供")
    result.evidence.extend(
        [
            make_evidence("type36_member_row", row, "visual_transcription", source=profile["drawing"], confidence=0.99),
            make_evidence("m34_lug_row", lug, "visual_transcription", source="LUG-PLATE_TYPE-C_M-34.pdf", confidence=0.99),
        ]
    )
    return result
