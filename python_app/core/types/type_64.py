"""Type 64 pipe-to-pipe rod hanger — D-78.

D-78 dimensions H between pipe centrelines; H is not the M-22 finished cut
length.  The calculator therefore requires ``rod_cut_length_mm`` for a weighted
rod BOM and otherwise emits a zero-weight cut-length reference.
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
from ..truth import make_evidence
from data.m22_table import build_m22_item
from data.m25_table import build_m25_item
from data.m4_table import build_m4_item
from data.m6_table import build_m6_item
from data.type64_table import get_type64_figure, get_type64_rod


def _material(kind: HardwareKind, service, overrides) -> MaterialSpec:
    return resolve_hardware_material(kind, service=service, overrides=overrides)


def _add(
    result: AnalysisResult,
    *,
    name: str,
    spec: str,
    material: MaterialSpec,
    quantity: int,
    unit_weight: float,
    category: str = "螺栓類",
    item_class: str = "",
    manufacturing_type: str = "",
):
    add_custom_entry(
        result,
        name,
        spec,
        material,
        quantity,
        unit_weight,
        "PC",
        category=category,
        item_class=item_class,
        manufacturing_type=manufacturing_type,
    )


def _parse(fullstring: str, result: AnalysisResult) -> tuple[float, float, int, str] | None:
    part2 = get_part(fullstring, 2)
    part3 = get_part(fullstring, 3)
    part4 = get_part(fullstring, 4)
    if not part2 or not part3 or not part4:
        result.error = "Type 64 格式應為 64-{E}-{F}-{HH}{FIG}"
        return None
    token = part4.strip()
    if len(token) < 2 or not token[-1].isalpha() or not token[:-1].isdigit():
        result.error = f"Type 64: 無法解析 H/FIG {part4!r}"
        return None
    e_size = get_lookup_value(part2.replace("B", ""))
    f_size = get_lookup_value(part3.replace("B", ""))
    h_mm = int(token[:-1]) * 100
    return e_size, f_size, h_mm, token[-1].upper()


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("64", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 64: 尚未建立來源 profile {profile_id}"
        return result

    parsed = _parse(fullstring, result)
    if parsed is None:
        return result
    e_size, f_size, h_mm, fig = parsed
    if not 500 <= h_mm <= 3000:
        result.error = f"Type 64: H={h_mm} mm 超出 D-78 500~3000 mm"
        return result
    if f_size < 2:
        result.error = f'Type 64: supporting line F={f_size:g}"；D-78 限定 2" & larger'
        return result

    rod_info = get_type64_rod(e_size)
    fig_info = get_type64_figure(fig)
    if not rod_info:
        result.error = (
            f'Type 64: supported line E={e_size:g}" 不在 D-78 表列尺寸'
        )
        return result
    if not fig_info:
        result.error = "Type 64: FIG 僅允許 A/B/C/D"
        return result
    if rod_info["fig_bc_only"] and fig not in {"B", "C"}:
        result.error = (
            f'Type 64: D-78 以 * 標示 E={e_size:g}" 僅允許 FIG-B/C，'
            f"目前為 FIG-{fig}"
        )
        return result

    context = parse_hardware_material_context(
        overrides,
        all_hardware_keys=("hardware_material", "material", "upper_material"),
    )
    rod_material = _material(HardwareKind.THREADED_ROD, context.service, context.material_overrides)
    nut_material = _material(HardwareKind.HEAVY_HEX_NUT, context.service, context.material_overrides)
    eye_material = _material(HardwareKind.WELDLESS_EYE_NUT, context.service, context.material_overrides)
    clamp_material = _material(HardwareKind.CLAMP_BODY, context.service, context.material_overrides)
    rod_size = rod_info["g"]

    blockers: list[str] = []
    rod_cut = overrides.get("rod_cut_length_mm")
    if rod_cut not in (None, ""):
        rod_cut = int(rod_cut)
        if rod_cut <= 0:
            result.error = "Type 64: rod_cut_length_mm 必須大於 0"
            return result
        rod_item = build_m22_item(rod_size, rod_cut)
        if not rod_item:
            result.error = f"Type 64: M-22 無 {rod_size} rod 資料"
            return result
        _add(
            result,
            name="MACHINE THREADED ROD",
            spec=rod_item["designation"],
            material=rod_material,
            quantity=2,
            unit_weight=rod_item["unit_weight_kg"],
            item_class="primary_structure",
            manufacturing_type="raw_cut",
        )
        rod = result.entries[-1]
        rod.length = rod_cut
        rod.geometry.fabrication_ready = True
    else:
        rod_blocker = (
            "D-78 的 H 是上下管中心距，不是 M-22 finished cut length；"
            "需提供 rod_cut_length_mm，禁止直接把 H 當吊桿長度"
        )
        _add(
            result,
            name="MACHINE THREADED ROD",
            spec=f"M-22 {rod_size}; CUT LENGTH TBD",
            material=rod_material,
            quantity=2,
            unit_weight=0,
            item_class="reference_only",
            manufacturing_type="raw_cut",
        )
        rod = result.entries[-1]
        rod.geometry.fabrication_ready = False
        rod.geometry.fabrication_blockers = [rod_blocker]
        blockers.append(rod_blocker)
    rod.geometry.component_id = "D78-M22-RODS"
    rod.geometry.source_drawing = profile["drawing"]
    rod.geometry.source_revision = profile["revision"]
    rod.geometry.shape_kind = "machine_threaded_rod"
    rod.geometry.shape_spec = f"M-22 {rod_size}; QTY2"
    rod.geometry.parameters = {
        "rod_size": rod_size,
        "quantity": 2,
        "assembly_centerline_H_mm": h_mm,
        "cut_length_mm": rod_cut or None,
    }
    set_remark(rod, blockers[-1] if rod_cut in (None, "") else f"override cut length={rod_cut} mm")

    eye = build_m25_item(rod_size)
    if not eye:
        result.error = f"Type 64: M-25 無 {rod_size} eye nut 資料"
        return result
    _add(
        result,
        name="WELDLESS EYE NUT",
        spec=eye["designation"],
        material=eye_material,
        quantity=2,
        unit_weight=eye["unit_weight_kg"],
        manufacturing_type="purchased",
    )
    eye_entry = result.entries[-1]
    eye_entry.geometry.component_id = "D78-M25-EYE-NUTS"
    eye_entry.geometry.source_drawing = "M-25"
    eye_entry.geometry.shape_kind = "purchased_eye_nut"
    eye_entry.geometry.parameters = {"rod_size": rod_size, "quantity": 2}
    eye_entry.geometry.fabrication_ready = True

    nut_blocker = "D-78 標示 finished heavy hex nut，但來源未給單重；採購重量待供應商"
    _add(
        result,
        name="FINISHED HEAVY HEX NUT",
        spec=f"for {rod_size} rod",
        material=nut_material,
        quantity=2,
        unit_weight=0,
        manufacturing_type="purchased",
    )
    nut = result.entries[-1]
    nut.geometry.component_id = "D78-FINISHED-HEX-NUTS"
    nut.geometry.source_drawing = profile["drawing"]
    nut.geometry.source_revision = profile["revision"]
    nut.geometry.shape_kind = "purchased_finished_hex_nut"
    nut.geometry.parameters = {"rod_size": rod_size, "quantity": 2}
    nut.geometry.fabrication_ready = False
    nut.geometry.fabrication_blockers = [nut_blocker]
    set_remark(nut, nut_blocker)
    blockers.append(nut_blocker)

    clamp_specs = [
        ("UPPER CLAMP", f_size, fig_info["upper_clamp"], "upper"),
        ("LOWER CLAMP", e_size, fig_info["lower_clamp"], "lower"),
    ]
    for name, line_size, ref, position in clamp_specs:
        builder = build_m6_item if "M-6" in ref else build_m4_item
        component_id = "M-6" if builder is build_m6_item else "M-4"
        item = builder(line_size)
        designation = item["designation"] if item else f'{component_id}, {line_size:g}"'
        clamp_blocker = (
            f"{component_id} clamp 已可查 designation/尺寸，但 component table "
            "未有來源單重；本 Type 不再套用集中估重"
        )
        _add(
            result,
            name=name,
            spec=designation,
            material=clamp_material,
            quantity=1,
            unit_weight=0,
            manufacturing_type="purchased",
        )
        clamp = result.entries[-1]
        clamp.geometry.component_id = f"D78-{position.upper()}-{component_id}"
        clamp.geometry.source_drawing = component_id
        clamp.geometry.shape_kind = "standard_pipe_clamp_reference"
        clamp.geometry.parameters = {
            "position": position,
            "line_size_in": line_size,
            "component_ref": component_id,
            "figure": fig,
        }
        clamp.geometry.fabrication_ready = False
        clamp.geometry.fabrication_blockers = [clamp_blocker]
        set_remark(clamp, clamp_blocker)
        blockers.append(clamp_blocker)

    if f_size < e_size:
        load_warning = (
            f'supporting line F={f_size:g}" 小於 supported line E={e_size:g}"；'
            "D-78 NOTE 2 要求 supporting line 另行校核總支撐載重"
        )
        result.warnings.append(load_warning)
    result.warnings.extend(blockers)
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        # Even with an explicit rod cut, the finished nuts and M-4/M-6 clamp
        # source weights remain unresolved.  A partial weighted list must not
        # be advertised as a complete BOM.
        "bom_ready": not blockers,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {
            "E_in": e_size,
            "F_in": f_size,
            "H_mm": h_mm,
            "figure": fig,
            "rod_size": rod_size,
        },
    }
    result.evidence.append(
        make_evidence(
            "type64_d78_row",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
