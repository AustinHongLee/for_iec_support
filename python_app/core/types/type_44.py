"""Type 44 source-aware vessel frame support (D-53)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..material_specs import ANCHOR_BOLT_SUS304, STRUCTURAL_A36_SS400, SUPPORT_PLATE_A36_SS400
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.steel_sections import get_section_details
from data.type44_table import get_type44_brace


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("44", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 44: 尚未建立來源 profile {profile_id}"
        return result
    parts = str(fullstring).split("-")
    if len(parts) not in (4, 5):
        result.error = "Type 44: 格式應為 44-{line size}B-{M}-{H} {A/B}[-{Q mm}]"
        return result
    line_size = get_lookup_value(parts[1])
    member = parts[2].upper()
    details = get_section_details(member)
    try:
        token = parts[3].split()
        h_mm = int(token[0])
        fig = token[1].upper() if len(token) > 1 else "A"
        q_mm = int(parts[4]) if len(parts) == 5 else config["TYPE44_PIPE_Q"][str(int(line_size))]
    except (KeyError, TypeError, ValueError):
        result.error = "Type 44: line size/H/Q無法依D-53解析"
        return result
    if member not in config["TYPE44_MEMBERS"] or not details:
        result.error = f"Type 44: D-53未支援MEMBER {member}"
        return result
    if fig not in ("A", "B") or h_mm <= 0 or q_mm <= 0:
        result.error = "Type 44: H/Q需大於0，FIG需為A/B"
        return result

    drawing = profile["drawing"]
    longitudinal = h_mm + q_mm + 3
    transverse = 2 * q_mm + 6
    blockers = [
        "D-53的MIN. CHANNEL REQUIRED圖表尚未完整轉成可驗證選型矩陣",
        "縱向member在vessel曲面端的實際端切/起點需設備幾何確認",
    ]
    for cid, role, length, qty, formula in (
        ("D53-LONGITUDINAL", "縱向member", longitudinal, 2, "H + Q + 3"),
        ("D53-TRANSVERSE", "橫向member", transverse, 2, "2Q + 6"),
    ):
        add_steel_section_entry(
            result, details["type"], details["size"][1:], length,
            material=STRUCTURAL_A36_SS400, steel_qty=qty,
        )
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.formula = formula
        entry.geometry.parameters = {
            "H_mm": h_mm, "Q_mm": q_mm, "quantity": qty,
            "figure": fig, "fillet_weld_mm": 6,
        }
        entry.geometry.fabrication_ready = cid == "D53-TRANSVERSE"
        if cid == "D53-LONGITUDINAL":
            entry.geometry.fabrication_blockers = [blockers[1]]
        set_remark(entry, f"{role}，{length}mm ×{qty}")

    if h_mm >= config["TYPE44_BRACE_H_MIN"]:
        brace = get_type44_brace(fig)
        add_steel_section_entry(
            result, "Angle", "50*50*6", brace["length"],
            material=STRUCTURAL_A36_SS400,
        )
        entry = result.entries[-1]
        entry.geometry.component_id = "D53-L50-BRACE"
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.parameters = {
            "figure": fig, "theta_deg": 30 if fig == "A" else 45,
            "cut_length_mm": brace["length"],
        }
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = ["斜撐兩端切角/貼合輪廓未完整尺寸化"]
        blockers.append("斜撐兩端切角/貼合輪廓未完整尺寸化")

    add_plate_entry(
        result, 90, 45, 6, "CLIP PLATE",
        material=SUPPORT_PLATE_A36_SS400, plate_qty=2,
        plate_role="generic_plate", bolt_switch=True,
        bolt_hole=16, bolt_size='1/2"x30',
    )
    plate = result.entries[-1]
    plate.geometry.component_id = "D53-CLIP-PLATE"
    plate.geometry.source_drawing = drawing
    plate.geometry.source_revision = profile["revision"]
    plate.geometry.shape_kind = "rectangular_plate"
    plate.geometry.holes.count = 1
    plate.geometry.parameters.update({"quantity": 2, "fillet_weld_mm": 6})
    plate.geometry.fabrication_ready = True

    add_custom_entry(
        result, name="M.BOLT", spec='1/2"x30',
        material=ANCHOR_BOLT_SUS304, quantity=2,
        unit_weight=0, unit="PC",
    )
    bolt = result.entries[-1]
    bolt.geometry.component_id = "D53-M-BOLT"
    bolt.geometry.source_drawing = drawing
    bolt.geometry.source_revision = profile["revision"]
    bolt.geometry.shape_kind = "purchased_fastener"
    bolt.geometry.parameters = {"spec": '1/2"x30', "quantity": 2, "hole_diameter_mm": 16}
    bolt.geometry.fabrication_ready = True
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f'{member}/FIG-{fig}/{"BRACED" if h_mm >= config["TYPE44_BRACE_H_MIN"] else "UNBRACED"}',
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": blockers,
        "longitudinal_cut_length_mm": longitudinal,
        "transverse_cut_length_mm": transverse,
        "Q_mm": q_mm,
    }
    result.warnings.extend(blockers)
    result.evidence.append(
        make_evidence(
            "type44_dimensions",
            {"line_size": line_size, "Q": q_mm, "H": h_mm, "member": member},
            "visual_transcription", source=drawing, confidence=0.95,
        )
    )
    return result
