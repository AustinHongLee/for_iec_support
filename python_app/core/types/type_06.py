"""Type 06 source-aware two-line support (Chung Wei D-6 / M-37)."""
from __future__ import annotations

import math

from ..bolt import add_custom_entry
from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..models import AnalysisResult, HolePattern, set_remark
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.m37_table import get_m37_by_type


def _load(source_profile):
    config = load_config("06", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        raise ValueError(f"Type 06 尚未建立來源 profile: {profile_id}")
    return profile_id, profile, config


def _parse(fullstring):
    parts = str(fullstring).split("-")
    if len(parts) not in (3, 4):
        raise ValueError("格式應為 06-{M}-{HHLL}[-{AABB}]")
    member = parts[1].upper()
    hl = parts[2]
    if len(hl) != 4 or not hl.isdigit():
        raise ValueError("第三段需為4碼 HHLL，例如 0510")
    h_mm, l_mm = int(hl[:2]) * 100, int(hl[2:]) * 100
    if len(parts) == 4:
        ab = parts[3]
        if len(ab) != 4 or not ab.isdigit():
            raise ValueError("第四段需為4碼 AABB，例如 0401")
        a_mm, b_mm, explicit_ab = int(ab[:2]) * 100, int(ab[2:]) * 100, True
    else:
        a_mm = b_mm = l_mm / 2
        explicit_ab = False
    return member, h_mm, l_mm, a_mm, b_mm, explicit_ab


def _positive_override(overrides, key, default):
    raw = overrides.get(key)
    if raw in (None, ""):
        return float(default), False
    value = float(raw)
    if value <= 0:
        raise ValueError(f"{key} 必須大於0")
    return value, True


def _add_lug_plate(result, lug, row, material, profile):
    holes = row["hole_count"]
    outer_area = (lug["A"] + lug["C"]) * lug["B"] / 2
    hole_area = holes * math.pi * lug["J"] ** 2 / 4
    net_area = outer_area - hole_area
    outline = [
        [-lug["C"] / 2, 0],
        [lug["C"] / 2, 0],
        [lug["A"] / 2, lug["B"]],
        [-lug["A"] / 2, lug["B"]],
    ]
    add_plate_entry(
        result,
        lug["A"],
        lug["B"],
        lug["T"],
        "LUG PLATE TYPE-F",
        material=material,
        plate_qty=1,
        bolt_switch=True,
        bolt_x=lug.get("H") or 0,
        bolt_y=lug["F"],
        bolt_hole=lug["J"],
        bolt_size=row["K"],
        plate_role="lug_plate",
        shape_spec=(
            f'{row["lug_type"]}; TRAPEZOID TOP{lug["C"]} '
            f'BOTTOM{lug["A"]} H{lug["B"]} T{lug["T"]}; '
            f'{holes}-HOLE DIA{lug["J"]}'
        ),
        shape_kind="lug_plate_type_f_trapezoid",
        gross_area_mm2=lug["A"] * lug["B"],
        cutout_area_mm2=lug["A"] * lug["B"] - net_area,
        net_area_mm2=net_area,
    )
    plate = result.entries[-1]
    plate.geometry.component_id = f'M37-{row["lug_type"]}'
    plate.geometry.source_drawing = profile["lug_drawing"]
    plate.geometry.source_revision = profile["lug_revision"]
    plate.geometry.holes.count = holes
    plate.geometry.holes.pattern = "rect"
    plate.geometry.parameters.update(
        {
            "lgp_type": row["lug_type"],
            "outline_points_mm": outline,
            "A_bottom_width_mm": lug["A"],
            "B_height_mm": lug["B"],
            "C_top_width_mm": lug["C"],
            "E_top_margin_mm": lug["E"],
            "F_vertical_pitch_mm": lug["F"],
            "G_side_margin_mm": lug.get("G"),
            "H_horizontal_pitch_mm": lug.get("H"),
            "hole_count": holes,
            "hole_diameter_J_mm": lug["J"],
            "bolt_spec_K": row["K"],
            "net_area_mm2": net_area,
        }
    )
    plate.geometry.fabrication_ready = True
    return plate


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, config = _load(source_profile)
        member, h_mm, l_mm, a_mm, b_mm, explicit_ab = _parse(fullstring)
    except (TypeError, ValueError) as exc:
        result.error = f"Type 06: {exc}"
        return result

    row = config[profile["member_table"]].get(member)
    if not row:
        result.error = (
            f"Type 06 / {profile_id}: D-6未表列 MEMBER {member}；"
            f"可用 {sorted(config[profile['member_table']])}"
        )
        return result
    limits = config["constraints"]
    if h_mm <= 0 or h_mm > limits["H_max_mm"]:
        result.error = (
            f"Type 06 / {profile_id}: H={h_mm}mm 超出 D-6 "
            f"0<H≤{limits['H_max_mm']}mm"
        )
        return result
    if l_mm <= 0 or l_mm > limits["L_max_mm"]:
        result.error = (
            f"Type 06 / {profile_id}: L={l_mm}mm 超出 D-6 "
            f"0<L≤{limits['L_max_mm']}mm"
        )
        return result
    if a_mm <= 0 or b_mm <= 0:
        result.error = "Type 06: A/B 必須大於0"
        return result
    lug = get_m37_by_type(row["lug_type"])
    if not lug:
        result.error = f"Type 06: M-37無 {row['lug_type']}"
        return result
    if lug["J"] != row["J"]:
        result.error = (
            f"Type 06: D-6 J={row['J']} 與 M-37 J={lug['J']} 不一致"
        )
        return result

    try:
        vertical_cut, vertical_explicit = _positive_override(
            overrides, "vertical_cut_length_mm", h_mm
        )
        horizontal_cut, horizontal_explicit = _positive_override(
            overrides, "horizontal_cut_length_mm", l_mm
        )
    except (TypeError, ValueError) as exc:
        result.error = f"Type 06: {exc}"
        return result

    ctx = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material",),
        legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,),
    )
    steel_material = resolve_hardware_material(
        HardwareKind.STRUCTURAL_STRUT,
        service=ctx.service,
        overrides=ctx.material_overrides,
    )
    fab = config["fabrication_contract"]
    ab_consistent = math.isclose(a_mm + b_mm, l_mm, abs_tol=0.01)

    add_steel_section_entry(
        result,
        row["section_type"],
        row["lookup_dim"],
        vertical_cut,
        material=steel_material,
    )
    vertical = result.entries[-1]
    vertical.geometry.component_id = "D6-VERTICAL-MEMBER-C"
    vertical.geometry.source_drawing = profile["drawing"]
    vertical.geometry.source_revision = profile["revision"]
    vertical.geometry.shape_kind = "stock_section_with_m37_holes"
    vertical.geometry.shape_spec = (
        f'{row["full_spec"]}; CUT={vertical_cut:g}; '
        f'{row["hole_count"]}-HOLE DIA{row["J"]} FOR {row["K"]}'
    )
    vertical.geometry.holes = HolePattern(
        pattern="rect",
        pitch_x=lug.get("H") or 0,
        pitch_y=lug["F"],
        diameter=row["J"],
        fastener_spec=row["K"],
        count=row["hole_count"],
    )
    vertical.geometry.parameters = {
        "H_designation_mm": h_mm,
        "cut_length_mm": vertical_cut,
        "cut_length_explicit": vertical_explicit,
        "m37_lug_type": row["lug_type"],
        "hole_count": row["hole_count"],
        "hole_diameter_J_mm": row["J"],
        "hole_vertical_pitch_F_mm": lug["F"],
        "hole_horizontal_pitch_H_mm": lug.get("H"),
        "weld_mm": fab["weld_mm"],
    }
    vertical.geometry.fabrication_ready = False
    vertical.geometry.fabrication_blockers = [
        "D-6 H需現場切配",
        "D-6/M-37未把孔群相對垂直member切端的共同基準完整尺寸化",
    ]
    set_remark(vertical, f"H={h_mm}；下料={vertical_cut:g}；現場切配")

    add_steel_section_entry(
        result,
        row["section_type"],
        row["lookup_dim"],
        horizontal_cut,
        material=steel_material,
    )
    horizontal = result.entries[-1]
    horizontal.geometry.component_id = "D6-HORIZONTAL-MEMBER-C"
    horizontal.geometry.source_drawing = profile["drawing"]
    horizontal.geometry.source_revision = profile["revision"]
    horizontal.geometry.shape_kind = "stock_section_cut"
    horizontal.geometry.shape_spec = f'{row["full_spec"]}; CUT={horizontal_cut:g}'
    horizontal.geometry.parameters = {
        "L_designation_mm": l_mm,
        "cut_length_mm": horizontal_cut,
        "cut_length_explicit": horizontal_explicit,
        "A_mm": a_mm,
        "B_mm": b_mm,
        "A_B_explicit": explicit_ab,
        "A_plus_B_equals_L": ab_consistent,
        "weld_mm": fab["weld_mm"],
    }
    horizontal.geometry.fabrication_ready = horizontal_explicit and ab_consistent
    horizontal.geometry.fabrication_blockers = []
    if not horizontal_explicit:
        horizontal.geometry.fabrication_blockers.append("D-6 L需現場切配")
    if not ab_consistent:
        horizontal.geometry.fabrication_blockers.append(
            "A+B與L不一致；需確認兩管中心位置（D-6範例本身亦有此衝突）"
        )

    plate = _add_lug_plate(result, lug, row, steel_material, profile)

    bolt_material = str(
        overrides.get("k_bolt_material") or "NOT SPECIFIED IN D-6/M-37"
    )
    add_custom_entry(
        result,
        name="K BOLT",
        spec=row["K"],
        material=bolt_material,
        quantity=row["hole_count"],
        unit_weight=0,
        unit="PC",
        role=ComponentRole.MACHINE_BOLT.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    bolt = result.entries[-1]
    bolt.geometry.component_id = "D6-K-BOLT"
    bolt.geometry.source_drawing = profile["drawing"]
    bolt.geometry.source_revision = profile["revision"]
    bolt.geometry.shape_kind = "purchased_fastener"
    bolt.geometry.shape_spec = f'{row["K"]}; QTY {row["hole_count"]}'
    bolt.geometry.parameters = {
        "spec": row["K"],
        "quantity": row["hole_count"],
        "material_explicit": bool(overrides.get("k_bolt_material")),
        "unit_weight_status": "not provided",
    }
    bolt.geometry.fabrication_ready = bool(overrides.get("k_bolt_material"))
    bolt.geometry.fabrication_blockers = (
        []
        if bolt.geometry.fabrication_ready
        else ["D-6/M-37未指定K bolt材質與單重"]
    )

    blockers = [
        *vertical.geometry.fabrication_blockers,
        *horizontal.geometry.fabrication_blockers,
        *bolt.geometry.fabrication_blockers,
    ]
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": member,
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": {
            "H_mm": h_mm,
            "L_mm": l_mm,
            "A_mm": a_mm,
            "B_mm": b_mm,
            "A_plus_B_equals_L": ab_consistent,
            "vertical_cut_length_mm": vertical_cut,
            "horizontal_cut_length_mm": horizontal_cut,
            "lug_type": row["lug_type"],
            "lug_net_area_mm2": plate.geometry.parameters["net_area_mm2"],
        },
    }
    result.warnings.append(
        f"D-6 H/L需現場切配；已補回 {row['lug_type']} 與 "
        f"{row['hole_count']} 支 {row['K']} K bolt"
    )
    if not ab_consistent:
        result.warnings.append(
            f"D-6 A+B={a_mm:g}+{b_mm:g}≠L={l_mm:g}；"
            "原圖範例亦不一致，保留原編碼但組立圖需確認"
        )
    result.evidence.extend(
        [
            make_evidence(
                "type06_member_row",
                row,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.99,
            ),
            make_evidence(
                "m37_lug_row",
                lug,
                "visual_transcription",
                source=profile["lug_drawing"],
                confidence=0.99,
            ),
            make_evidence(
                "type06_designation_dimensions",
                {"H": h_mm, "L": l_mm, "A": a_mm, "B": b_mm},
                "formula",
                source=profile["drawing"],
                confidence=0.99 if ab_consistent else 0.6,
                note="D-6 sample A+B conflict preserved as blocker",
            ),
        ]
    )
    return result
