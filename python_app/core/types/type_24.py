"""Type 24 Chung Wei-only single cantilever angle (D-26)."""
from __future__ import annotations

from ..config_loader import load_config
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import register_source_envelope
from ..models import AnalysisResult
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    profile_id = normalize_source_profile(source_profile)
    config = load_config("24", strict=True)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 24 / {profile_id}: 來源套圖沒有 D-26，暫不計算"
        return result
    parts = str(fullstring).split("-")
    if len(parts) != 3 or not parts[2].isdigit():
        result.error = "Type 24: 格式應為 24-{M}-{HH}"
        return result
    member = parts[1].upper()
    row = config["MEMBER_TABLE"].get(member)
    if not row:
        result.error = f"Type 24: D-26 未表列 MEMBER {member}"
        return result
    h_mm = int(parts[2]) * 100
    if h_mm <= 0:
        result.error = f"Type 24: H={h_mm}mm 超出 {member} H(MAX)={row['H_MAX']}mm"
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 24 / {profile_id}",
        source_ref=f"D-26 {member} H(MAX)",
        checks=(("H", h_mm, row["H_MAX"], True),),
    ):
        return result
    orientation = str(overrides.get("mounting_orientation") or "").strip().lower()
    shown = config["fabrication_contract"]["shown_mounting_orientations"]
    if orientation and orientation not in shown:
        result.error = f"Type 24: mounting_orientation須為 {'/'.join(shown)}"
        return result

    ctx = parse_hardware_material_context(overrides, legacy_material_keys=("material",), legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,))
    material = resolve_hardware_material(HardwareKind.STRUCTURAL_STRUT, service=ctx.service, overrides=ctx.material_overrides)
    add_steel_section_entry(result, row["section_type"], row["lookup_dim"], h_mm, material=material)
    entry = result.entries[-1]
    blockers = []
    if not orientation:
        blockers.append("designation未區分D-26所示三種安裝方向；缺mounting_orientation")
    blockers.append("designation不含supported line size；D-68 U-bolt孔徑與孔距無法展開")
    entry.geometry.component_id = "D26-MEMBER-M"
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = "single_angle_cantilever"
    entry.geometry.shape_spec = f'{row["full_spec"]}; CUT H={h_mm}'
    entry.geometry.parameters = {
        "cut_length_H_mm": h_mm, "H_MAX_mm": row["H_MAX"],
        "mounting_orientation": orientation or None, "shown_mounting_orientations": shown,
        "supported_line_center_from_free_end_mm": 100, "field_fillet_weld_mm": 6,
        "weld_all_around": True, "u_bolt_reference": "D-68", "u_bolt_furnished": False,
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = blockers
    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": profile["drawing"], "source_revision": profile["revision"],
        "branch": f"{member}/{orientation or 'orientation-unselected'}", "bom_ready": True,
        "fabrication_ready": False, "blockers": blockers,
    }
    result.warnings.append("D-26 member BOM可算；安裝方向與D-68孔位未齊，不能直接出加工圖")
    result.evidence.append(make_evidence("type24_member_row", row, "visual_transcription", source=profile["drawing"], confidence=0.99))
    return result
