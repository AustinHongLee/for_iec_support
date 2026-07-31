"""Type 46 vessel-mounted four-channel frame (D-56).

The D-56 plan dimensions the two longitudinal cuts as H + Q + 50 and the
two transverse cuts as 2Q.  The repeated 3 mm callout is the D-80 interface
clearance; it is not stock added to either channel cut.
"""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.steel_sections import get_section_details


_FRAME_MATERIAL = "Carbon Steel (grade per project specification)"
_FASTENER_MATERIAL = "Not specified in D-56"


def _add_d80_reference(result, drawing, revision, line_size):
    blocker = "D-56引用D-80且未標示NOT FURNISHED；須接入同來源Type 66 BOM後才能取得完整重量"
    add_custom_entry(
        result,
        "D-80 PIPE SUPPORT INTERFACE",
        f'{line_size:g}"',
        "Per source D-80",
        1,
        0,
        "SET",
        remark=blocker,
        category="組件類",
        item_class="reference_only",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "D56-D80-REFERENCE"
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "referenced_standard_component"
    entry.geometry.parameters = {"line_size_in": line_size, "referenced_drawing": "D-80"}
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    return blocker


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("46", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 46: 尚未建立來源 profile {profile_id}"
        return result
    parts = str(fullstring).split("-")
    if len(parts) not in (4, 5):
        result.error = "Type 46: 格式應為 46-{line size}B-{M}-{H} {A/B}[-{Q mm}]"
        return result
    line_size = get_lookup_value(parts[1])
    member = parts[2].upper()
    details = get_section_details(member)
    try:
        token = parts[3].split()
        h_mm = int(token[0])
        fig = token[1].upper() if len(token) > 1 else "A"
        q_mm = int(parts[4]) if len(parts) == 5 else profile["pipe_q"][str(int(line_size))]
    except (KeyError, TypeError, ValueError):
        result.error = "Type 46: line size/H/Q無法依D-56解析"
        return result
    if member not in profile["members"] or not details:
        result.error = f"Type 46 / {profile_id}: D-56未表列MEMBER {member}"
        return result
    if fig not in ("A", "B") or h_mm <= 0 or q_mm <= 0:
        result.error = "Type 46: H/Q需大於0，FIG需為A/B"
        return result

    longitudinal = h_mm + q_mm + 50
    transverse = 2 * q_mm
    drawing = profile["drawing"]
    blockers = [
        "D-56的MIN. CHANNEL REQUIRED圖表尚未完整轉成可驗證選型矩陣",
        "縱向member的設備曲面端切與實際起點需設備幾何確認",
    ]
    for cid, role, length, qty, formula in (
        ("D56-LONGITUDINAL", "縱向member", longitudinal, 2, "H + Q + 50"),
        ("D56-TRANSVERSE", "橫向member", transverse, 2, "2Q"),
    ):
        add_steel_section_entry(
            result, details["type"], details["size"][1:], length,
            material=_FRAME_MATERIAL, steel_qty=qty,
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
            "d80_clearance_mm": 3,
            "right_end_extension_mm": 50 if cid == "D56-LONGITUDINAL" else None,
        }
        entry.geometry.fabrication_ready = cid == "D56-TRANSVERSE"
        if cid == "D56-LONGITUDINAL":
            entry.geometry.fabrication_blockers = [blockers[1]]
        set_remark(entry, f"{role}，{length}mm ×{qty}")

    braced = h_mm > profile["brace_h_min"]
    if braced:
        brace = profile["brace"][fig]
        add_steel_section_entry(
            result, "Angle", "50*50*6", brace["length"],
            material=_FRAME_MATERIAL, steel_qty=2,
        )
        entry = result.entries[-1]
        entry.geometry.component_id = "D56-L50-BRACE"
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.parameters = {
            "figure": fig, "theta_deg": 30 if fig == "A" else 45,
            "cut_length_mm": brace["length"], "quantity": 2,
        }
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = ["斜撐兩端切角/貼合輪廓未完整尺寸化"]
        blockers.append("斜撐兩端切角/貼合輪廓未完整尺寸化")

    add_plate_entry(
        result, 90, 45, 6, "CLIP PLATE",
        material=_FRAME_MATERIAL, plate_qty=2,
        plate_role="generic_plate", bolt_switch=True,
        bolt_hole=16, bolt_size='1/2"x30',
    )
    plate = result.entries[-1]
    plate.geometry.component_id = "D56-CLIP-PLATE"
    plate.geometry.source_drawing = drawing
    plate.geometry.source_revision = profile["revision"]
    plate.geometry.shape_kind = "rectangular_plate"
    plate.geometry.holes.count = 1
    plate.geometry.parameters.update({"quantity": 2, "fillet_weld_mm": 6})
    plate.geometry.fabrication_ready = True

    add_custom_entry(
        result, name="M.BOLT", spec='1/2"x30',
        material=_FASTENER_MATERIAL, quantity=2, unit_weight=0, unit="PC",
    )
    bolt = result.entries[-1]
    bolt.geometry.component_id = "D56-M-BOLT"
    bolt.geometry.source_drawing = drawing
    bolt.geometry.source_revision = profile["revision"]
    bolt.geometry.shape_kind = "purchased_fastener"
    bolt.geometry.parameters = {"spec": '1/2"x30', "quantity": 2, "hole_diameter_mm": 16}
    bolt.geometry.fabrication_ready = True
    d80_blocker = _add_d80_reference(
        result, drawing, profile["revision"], line_size
    )
    blockers.append(d80_blocker)

    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f'{member}/FIG-{fig}/{"BRACED" if braced else "UNBRACED"}',
        "bom_ready": False, "fabrication_ready": False, "blockers": blockers,
        "referenced_components": ["D-80"],
        "not_furnished": [],
        "longitudinal_cut_length_mm": longitudinal,
        "transverse_cut_length_mm": transverse, "Q_mm": q_mm,
    }
    result.warnings.extend(blockers)
    result.evidence.append(make_evidence(
        "type46_dimensions",
        {
            "line_size": line_size, "Q": q_mm, "H": h_mm, "member": member,
            "longitudinal_cut_mm": longitudinal,
            "transverse_cut_mm": transverse,
            "d80_clearance_mm": 3,
            "right_end_extension_mm": 50,
        },
        "visual_transcription", source=drawing, confidence=0.95,
    ))
    return result
