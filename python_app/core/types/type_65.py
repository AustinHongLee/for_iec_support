"""Type 65 trapeze hanger — D-79.

The D-79 member/rod table is source truth.  H is an assembly dimension to the
top of member M, not a finished M-23 rod cut.  Rod weight is therefore emitted
only when ``rod_cut_length_mm`` is explicitly supplied.
"""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.m23_table import build_m23_item
from data.m28_table import get_m28_by_rod_size
from data.type65_table import get_type65_data, snap_l_bucket


def _section(member: str) -> tuple[str, str]:
    if member.startswith("L"):
        return "Angle", member[1:]
    if member.startswith("C"):
        return "Channel", member[1:]
    raise ValueError(f"Unsupported D-79 member {member}")


def _material(kind: HardwareKind, context) -> MaterialSpec:
    return resolve_hardware_material(
        kind,
        service=context.service,
        overrides=context.material_overrides,
    )


def _add_zero_hardware(
    result: AnalysisResult,
    *,
    name: str,
    spec: str,
    material: MaterialSpec,
    quantity: int,
    component_id: str,
    drawing: str,
    revision: str,
    blocker: str,
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
        category="螺栓類",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "standard_hardware_reference"
    entry.geometry.parameters = {"quantity": quantity, "spec": spec}
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    set_remark(entry, blocker)


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("65", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 65: 尚未建立來源 profile {profile_id}"
        return result

    part2 = get_part(fullstring, 2)
    part3 = get_part(fullstring, 3)
    if not part2 or not part3 or len(part3) != 4 or not part3.isdigit():
        result.error = "Type 65 格式應為 65-{D}B-{LLHH}"
        return result
    line_size = get_lookup_value(part2.replace("B", ""))
    l_mm = int(part3[:2]) * 100
    h_mm = int(part3[2:]) * 100
    if not 0 < l_mm <= 2500:
        result.error = f"Type 65: L={l_mm} mm 超出 D-79 0<L<=2500"
        return result
    if not 0 < h_mm <= 3000:
        result.error = f"Type 65: H={h_mm} mm 超出 D-79 0<H<=3000"
        return result

    row = get_type65_data(line_size)
    if not row:
        result.error = (
            f'Type 65: D-79 未表列 {line_size:g}"；'
            '允許 2,3,4,6,8,10,12,14,16,18,20,24"'
        )
        return result
    bucket = snap_l_bucket(l_mm)
    member = row["member_by_l"].get(bucket) if bucket else None
    if not member:
        result.error = f"Type 65: L={l_mm} mm 無 D-79 member 選型"
        return result

    context = parse_hardware_material_context(
        overrides,
        all_hardware_keys=("hardware_material", "material", "upper_material"),
    )
    member_material = _material(HardwareKind.STRUCTURAL_STRUT, context)
    rod_material = _material(HardwareKind.THREADED_ROD, context)
    bracket_material = _material(HardwareKind.BEAM_ATTACHMENT, context)
    nut_material = _material(HardwareKind.HEAVY_HEX_NUT, context)
    washer_material = _material(HardwareKind.HEAVY_HEX_NUT, context)
    stiffener_material = _material(HardwareKind.GUSSET_PLATE, context)
    blockers: list[str] = []

    section_type, section_dim = _section(member)
    add_steel_section_entry(
        result,
        section_type,
        section_dim,
        l_mm,
        1,
        member_material,
    )
    member_entry = result.entries[-1]
    member_entry.geometry.component_id = "D79-MEMBER-M"
    member_entry.geometry.source_drawing = profile["drawing"]
    member_entry.geometry.source_revision = profile["revision"]
    member_entry.geometry.shape_kind = "field_cut_structural_member"
    member_entry.geometry.shape_spec = f"{member}; CUT L={l_mm}"
    member_entry.geometry.parameters = {
        "member": member,
        "cut_length_mm": l_mm,
        "selection_bucket_mm": bucket,
        "rod_hole_diameter_rule": "A+3",
        "rod_hole_quantity": 2,
        "end_offset_mm": 60,
        "fillet_weld_Y_mm": row["weld_y"],
    }
    member_blockers = [
        "D-79 NOTE 2：member M 長度 L 應於現場切配；shop drawing 需回填現場確認長度"
    ]
    if member_entry.weight_per_unit <= 0:
        member_blockers.append(
            f"{member} 的來源每米重尚未建表，該 member 重量暫為 0"
        )
    member_entry.geometry.fabrication_ready = False
    member_entry.geometry.fabrication_blockers = member_blockers
    blockers.extend(member_blockers)
    set_remark(
        member_entry,
        f"D-79 依 next-greater L column={bucket} mm 選型；實切 L={l_mm} mm；"
        + "；".join(member_blockers),
    )

    rod_size = row["rod_size"]
    rod_cut = overrides.get("rod_cut_length_mm")
    if rod_cut not in (None, ""):
        rod_cut = int(rod_cut)
        rod_item = build_m23_item(rod_size, rod_cut)
        if rod_cut <= 0 or not rod_item:
            result.error = f"Type 65: rod_cut_length_mm / M-23 {rod_size} 無效"
            return result
        add_custom_entry(
            result,
            "WELDED EYE ROD",
            rod_item["designation"],
            rod_material,
            2,
            rod_item["unit_weight_kg"],
            "PC",
            category="螺栓類",
            item_class="primary_structure",
            manufacturing_type="raw_cut",
        )
        rod = result.entries[-1]
        rod.length = rod_cut
        rod.geometry.fabrication_ready = True
    else:
        rod_blocker = (
            "D-79 的 H 是上方支承面至 member M 上表的組立尺寸，"
            "未包含 M-28 take-off、穿板與螺帽餘長；需提供 rod_cut_length_mm"
        )
        add_custom_entry(
            result,
            "WELDED EYE ROD",
            f"M-23 {rod_size}; CUT LENGTH TBD",
            rod_material,
            2,
            0,
            "PC",
            category="螺栓類",
            item_class="reference_only",
            manufacturing_type="raw_cut",
        )
        rod = result.entries[-1]
        rod.geometry.fabrication_ready = False
        rod.geometry.fabrication_blockers = [rod_blocker]
        blockers.append(rod_blocker)
    rod.geometry.component_id = "D79-M23-WELDED-EYE-RODS"
    rod.geometry.source_drawing = profile["drawing"]
    rod.geometry.source_revision = profile["revision"]
    rod.geometry.shape_kind = "welded_eye_rod"
    rod.geometry.shape_spec = f"M-23 {rod_size}; QTY2"
    rod.geometry.parameters = {
        "rod_size": rod_size,
        "quantity": 2,
        "assembly_H_mm": h_mm,
        "cut_length_mm": rod_cut or None,
    }
    set_remark(
        rod,
        f"override cut length={rod_cut} mm"
        if rod_cut not in (None, "")
        else blockers[-1],
    )

    bracket = get_m28_by_rod_size(rod_size)
    bracket_blocker = "M-28 已有尺寸/載重查表，但來源未提供可採信單重；採購重量歸零待供應商"
    _add_zero_hardware(
        result,
        name="ANGLE BRACKET",
        spec=bracket["type"] if bracket else f"M-28 {rod_size}",
        material=bracket_material,
        quantity=2,
        component_id="D79-M28-ANGLE-BRACKETS",
        drawing="M-28",
        revision="",
        blocker=bracket_blocker,
    )
    blockers.append(bracket_blocker)

    nut_blocker = "D-79 每支 eye rod 標示 3 個 finished hex nuts；來源未給單重"
    _add_zero_hardware(
        result,
        name="FINISHED HEX NUT",
        spec=f'for {rod_size} rod',
        material=nut_material,
        quantity=6,
        component_id="D79-FINISHED-HEX-NUTS",
        drawing=profile["drawing"],
        revision=profile["revision"],
        blocker=nut_blocker,
    )
    blockers.append(nut_blocker)

    washer_blocker = "D-79 每支 eye rod 標示上下 washer；來源未給 washer 規格/單重"
    _add_zero_hardware(
        result,
        name="WASHER",
        spec=f'for {rod_size} rod',
        material=washer_material,
        quantity=4,
        component_id="D79-WASHERS",
        drawing=profile["drawing"],
        revision=profile["revision"],
        blocker=washer_blocker,
    )
    blockers.append(washer_blocker)

    if line_size >= 12:
        stiffener_blocker = (
            'D-79 僅標示 12" & larger 的 stiffener、60 mm 與三邊 6 mm 焊；'
            "未充分標示片數及完整輪廓，舊版依管徑遞增的自創尺寸已移除"
        )
        add_custom_entry(
            result,
            "STIFFENER SET",
            "SEE D-79 DETAIL; 60; 6 FILLET 3 SIDES",
            stiffener_material,
            1,
            0,
            "SET",
            remark=stiffener_blocker,
            category="鋼板類",
            item_class="reference_only",
            manufacturing_type="plate_cut",
        )
        stiffener = result.entries[-1]
        stiffener.geometry.component_id = "D79-STIFFENER-REFERENCE"
        stiffener.geometry.source_drawing = profile["drawing"]
        stiffener.geometry.source_revision = profile["revision"]
        stiffener.geometry.shape_kind = "member_end_stiffener"
        stiffener.geometry.parameters = {
            "applies_from_line_size_in": 12,
            "shown_length_mm": 60,
            "fillet_weld_mm": 6,
            "weld_sides": 3,
        }
        stiffener.geometry.fabrication_ready = False
        stiffener.geometry.fabrication_blockers = [stiffener_blocker]
        blockers.append(stiffener_blocker)

    result.warnings.extend(blockers)
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        # An explicit rod cut only resolves that one line.  Field-fit member
        # confirmation plus supplier weights for M-28/nuts/washers remain open.
        "bom_ready": not blockers,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {
            "line_size_in": line_size,
            "L_mm": l_mm,
            "H_mm": h_mm,
            "selection_bucket_mm": bucket,
            "member": member,
            "rod_size": rod_size,
            "weld_Y_mm": row["weld_y"],
        },
    }
    result.evidence.append(
        make_evidence(
            "type65_d79_row",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
