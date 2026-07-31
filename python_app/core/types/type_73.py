"""Type 73 spring strap support — D-88/D-88A with M-53."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, HolePattern, set_remark
from ..parser import get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.type73_table import (
    build_type73_strap_item,
    get_type73_bolt_count,
    get_type73_data,
    get_type73_spring_data,
)


def _add_blocked_hardware(
    result: AnalysisResult,
    *,
    name: str,
    spec: str,
    material: str,
    quantity: int,
    component_id: str,
    drawing: str,
    revision: str,
    blocker: str,
    category: str = "螺栓類",
):
    add_custom_entry(
        result,
        name,
        spec,
        material,
        quantity,
        0,
        "PC",
        remark=blocker,
        category=category,
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "standard_component_reference"
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    set_remark(entry, blocker)
    return entry


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("73", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 73: 尚未建立來源 profile {profile_id}"
        return result

    part2 = get_part(fullstring, 2)
    mode = (get_part(fullstring, 3) or "").upper()
    if not part2 or mode not in {"S", "G"}:
        result.error = "Type 73 格式應為 73-{line_size}B-{S|G}"
        return result
    line_size = get_lookup_value(part2)
    row = get_type73_data(line_size)
    strap = build_type73_strap_item(line_size)
    if not row or not strap:
        result.error = f'Type 73: D-88/M-53 未表列 {line_size:g}"；範圍 1"~24"'
        return result

    add_plate_entry(
        result,
        strap["blank_length_mm"],
        strap["blank_width_mm"],
        strap["thickness_mm"],
        "STRAP",
        material=strap["material"],
        plate_qty=1,
        plate_role="strap",
        formula=(
            f'{strap["blank_length_mm"]:g}*{strap["blank_width_mm"]:g}'
            f'-{strap["hole_count"]}*PI*({strap["hole_diameter_mm"]:g}/2)^2'
        ),
        notes_zh="M-53 的 A 為平板總長；重量扣除 D+3 螺栓孔",
        shape_spec=strap["spec"],
        shape_kind="formed_spring_strap",
        gross_area_mm2=strap["gross_area_mm2"],
        cutout_area_mm2=strap["cutout_area_mm2"],
        net_area_mm2=strap["net_area_mm2"],
    )
    strap_entry = result.entries[-1]
    strap_entry.geometry.component_id = "D88-M53-STRAP"
    strap_entry.geometry.source_drawing = "TYPE-73_D-88.pdf / STRAP_TYPE-PUBS2_M-53.pdf"
    strap_entry.geometry.source_revision = profile["revision"]
    strap_entry.geometry.holes = HolePattern(
        pattern="single" if strap["hole_count"] == 2 else "rect",
        diameter=strap["hole_diameter_mm"],
        count=strap["hole_count"],
        fastener_spec=row["bolt_dia"],
    )
    strap_entry.geometry.parameters.update(
        {
            "line_size_in": line_size,
            "A_developed_length_mm": row["A"],
            "B_bend_span_mm": row["B"],
            "C_mm": row["C"],
            "E_mm": row["E"],
            "R_mm": row["R"],
            "bar_size": row["steel_bar_size"],
            "bolt_diameter": row["bolt_dia"],
            "hole_diameter_mm": strap["hole_diameter_mm"],
            "hole_count": strap["hole_count"],
            "bolt_arrangement": row["bolt_arrangement"],
        }
    )
    strap_entry.geometry.fabrication_ready = True
    set_remark(strap_entry, "M-53 平板 A×F×T 扣 D+3 孔；彎製尺寸 B/C/R 依 M-53")

    bolt_count = get_type73_bolt_count(line_size)
    spring = get_type73_spring_data(row["spring_mark"])
    spring_blocker = (
        "D-88A 有 spring coil 工程尺寸但無來源單重/端部製作公差；"
        "不再以理想螺旋線長估成品重量"
    )
    spring_entry = _add_blocked_hardware(
        result,
        name="SPRING COIL",
        spec=(
            f'{row["spring_mark"]}; wire={spring["wire_dia_mm"]} mm; '
            f'ID={spring["coil_id_mm"]} mm; free L={spring["free_length_mm"]} mm'
            if spring
            else row["spring_mark"]
        ),
        material=spring["material"] if spring else "ASTM A229 Class 1",
        quantity=bolt_count,
        component_id="D88A-SPRING-COILS",
        drawing="TYPE-73_D-88A.pdf",
        revision=profile["revision"],
        blocker=spring_blocker,
        category="彈簧類",
    )
    if spring:
        spring_entry.geometry.parameters = {
            key: value
            for key, value in spring.items()
            if key != "unit_weight_kg"
        } | {"quantity": bolt_count}

    stud_blocker = (
        "D-88 的 G 是 base 上表至上端組立高度，不是 stud bolt finished cut；"
        "需提供 stud_cut_length_mm 才能算重"
    )
    stud_entry = _add_blocked_hardware(
        result,
        name="STUD BOLT",
        spec=f'{row["bolt_dia"]}; CUT LENGTH TBD',
        material=str(overrides.get("stud_material") or "CARBON STEEL"),
        quantity=bolt_count,
        component_id="D88-STUD-BOLTS",
        drawing="TYPE-73_D-88.pdf",
        revision=profile["revision"],
        blocker=stud_blocker,
    )
    stud_entry.geometry.parameters = {
        "diameter": row["bolt_dia"],
        "quantity": bolt_count,
        "assembly_G_mm": row["G"],
        "cut_length_mm": overrides.get("stud_cut_length_mm"),
    }

    washer_blocker = "D-88 標示 washers，但未給 washer 規格、數量細分與單重"
    washer_entry = _add_blocked_hardware(
        result,
        name="WASHER",
        spec=f'for {row["bolt_dia"]} stud',
        material=str(overrides.get("washer_material") or "CARBON STEEL"),
        quantity=bolt_count * 2,
        component_id="D88-WASHERS",
        drawing="TYPE-73_D-88.pdf",
        revision=profile["revision"],
        blocker=washer_blocker,
    )
    washer_entry.geometry.parameters = {
        "stud_diameter": row["bolt_dia"],
        "provisional_quantity": bolt_count * 2,
    }

    blockers = [spring_blocker, stud_blocker, washer_blocker]
    if row["E"] is not None:
        gusset_blocker = (
            'M-53 對 6" & larger 僅標 E/H、12 mm R 及「same thickness as bar」；'
            "gusset 完整輪廓/片數不足，舊版 E×H/2 三角形重量已移除"
        )
        add_custom_entry(
            result,
            "GUSSET SET",
            (
                f'E={row["E"]}; H={row["H"]}; R12; '
                f't=same as {row["steel_bar_size"]}'
            ),
            strap["material"],
            1,
            0,
            "SET",
            remark=gusset_blocker,
            category="鋼板類",
            item_class="reference_only",
            manufacturing_type="plate_cut",
        )
        gusset = result.entries[-1]
        gusset.geometry.component_id = "M53-GUSSET-REFERENCE"
        gusset.geometry.source_drawing = "STRAP_TYPE-PUBS2_M-53.pdf"
        gusset.geometry.source_revision = profile["revision"]
        gusset.geometry.shape_kind = "formed_strap_gusset"
        gusset.geometry.parameters = {
            "E_mm": row["E"],
            "H_mm": row["H"],
            "radius_mm": 12,
            "thickness_rule": f"same as {row['steel_bar_size']}",
        }
        gusset.geometry.fabrication_ready = False
        gusset.geometry.fabrication_blockers = [gusset_blocker]
        blockers.append(gusset_blocker)

    slot_rule = "L=D+3" if mode == "G" else "L=2D"
    result.warnings.extend(blockers)
    result.warnings.append(
        f"{'GUIDE' if mode == 'G' else 'SLIDE'} support：D-88A detail C slot rule {slot_rule}"
    )
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "strap_blank_ready": True,
        "blockers": blockers,
        "not_furnished": ["STEEL MEMBER"],
        "assembly_dimensions": {
            "line_size_in": line_size,
            "mode": "GUIDE" if mode == "G" else "SLIDE",
            "slot_rule": slot_rule,
            **row,
        },
    }
    result.evidence.extend(
        [
            make_evidence(
                "type73_d88_row",
                row,
                "visual_transcription",
                source="TYPE-73_D-88.pdf",
                confidence=0.99,
            ),
            make_evidence(
                "m53_strap_blank",
                {
                    "A": strap["blank_length_mm"],
                    "F": strap["blank_width_mm"],
                    "T": strap["thickness_mm"],
                    "holes": strap["hole_count"],
                    "hole_diameter_mm": strap["hole_diameter_mm"],
                },
                "visual_transcription",
                source="STRAP_TYPE-PUBS2_M-53.pdf",
                confidence=0.99,
            ),
        ]
    )
    return result
