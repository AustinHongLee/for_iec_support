"""Type 47 lug-mounted vessel frame with source-specific D-80 ownership."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from .type_45 import _add_lug
from data.m34_table import get_m34_by_member
from data.m35_table import get_m35_by_member
from data.m36_table import get_m36_by_member


_FRAME_MATERIAL = "Carbon Steel (grade per project specification)"
_FASTENER_MATERIAL = "Not specified in D-57/D-58"
_LUG_MATERIAL = "Same as connected vessel/support metal"


def _set_lug_material(entry):
    entry.material = _LUG_MATERIAL
    entry.material_canonical_id = ""


def _add_d80_reference(result, profile, drawing, revision, line_size):
    if profile["d80_ownership"] == "not_furnished":
        return None
    blocker = (
        "D-57引用D-80且此來源未標示NOT FURNISHED；"
        "須接入同來源Type 66 BOM後才能取得完整重量"
    )
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
    entry.geometry.component_id = "D57-D80-REFERENCE"
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "referenced_standard_component"
    entry.geometry.parameters = {"line_size_in": line_size, "referenced_drawing": "D-80"}
    entry.geometry.fabrication_blockers = [blocker]
    return blocker


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("47", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 47: 尚未建立來源 profile {profile_id}"
        return result
    parts = str(fullstring).split("-")
    if len(parts) not in (4, 5):
        result.error = "Type 47: 格式應為 47-{line size}B-{M}-{H} {A/B}[-{Q mm}]"
        return result
    line_size = get_lookup_value(parts[1])
    member = parts[2].upper()
    row = profile["members"].get(member)
    try:
        token = parts[3].split()
        h_mm = int(token[0])
        fig = token[1].upper() if len(token) > 1 else "A"
        q_mm = int(parts[4]) if len(parts) == 5 else profile["pipe_q"][str(int(line_size))]
    except (KeyError, TypeError, ValueError):
        result.error = f"Type 47 / {profile_id}: line size/H/Q無法依來源圖解析"
        return result
    if not row:
        result.error = f"Type 47 / {profile_id}: 原圖未表列MEMBER {member}"
        return result
    if fig not in ("A", "B") or h_mm <= 0:
        result.error = "Type 47: H需大於0，FIG需為A/B"
        return result

    longitudinal = h_mm + q_mm + 50
    transverse = 2 * q_mm
    if longitudinal <= 0:
        result.error = f"Type 47: H+Q+50={longitudinal}mm，縱向member無有效長度"
        return result
    drawing = " / ".join(profile["drawings"])
    revision = profile["revision"]
    blockers = [
        "來源圖的MIN. CHANNEL REQUIRED圖表尚未完整轉成可驗證選型矩陣",
        "縱向member的設備曲面端切與實際起點需設備幾何確認",
    ]
    section = row["member_full"].removeprefix("C").replace("X", "*")
    for cid, role, length, qty, formula in (
        ("D57-LONGITUDINAL", "縱向member", longitudinal, 2, "H + Q + 50"),
        ("D57-TRANSVERSE", "橫向member", transverse, 2, "2Q"),
    ):
        add_steel_section_entry(
            result, "Channel", section, length,
            material=_FRAME_MATERIAL, steel_qty=qty,
        )
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = revision
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.formula = formula
        entry.geometry.parameters = {
            "H_mm": h_mm, "A_mm": row["A"], "Q_mm": q_mm,
            "quantity": qty, "figure": fig, "d80_clearance_mm": 3,
            "right_end_extension_mm": 50 if cid == "D57-LONGITUDINAL" else None,
        }
        entry.geometry.fabrication_ready = cid == "D57-TRANSVERSE"
        if cid == "D57-LONGITUDINAL":
            entry.geometry.fabrication_blockers = [blockers[1]]
        set_remark(entry, f"{role}，{length}mm ×{qty}")

    braced = (
        h_mm >= profile["brace_h_min"]
        if profile.get("brace_h_inclusive")
        else h_mm > profile["brace_h_min"]
    )
    if braced:
        brace_row = profile["brace"][fig]
        add_steel_section_entry(
            result, "Angle", "50*50*6", brace_row["length"],
            material=_FRAME_MATERIAL, steel_qty=2,
        )
        brace = result.entries[-1]
        brace.geometry.component_id = "D57-L50-BRACE"
        brace.geometry.source_drawing = drawing
        brace.geometry.source_revision = revision
        brace.geometry.shape_kind = "stock_section_cut"
        brace.geometry.parameters = {
            "figure": fig, "theta_deg": 30 if fig == "A" else 45,
            "cut_length_mm": brace_row["length"], "quantity": 2,
        }
        brace.geometry.fabrication_blockers = ["斜撐兩端切角/貼合輪廓未完整尺寸化"]
        blockers.append("斜撐兩端切角/貼合輪廓未完整尺寸化")

    clip_bolt_spec = profile["clip_bolt"]
    add_plate_entry(
        result, 90, 45, 6, "CLIP PLATE",
        material=_FRAME_MATERIAL, plate_qty=2,
        plate_role="generic_plate", bolt_switch=True,
        bolt_hole=16, bolt_size=clip_bolt_spec,
    )
    clip = result.entries[-1]
    clip.geometry.component_id = "D57-CLIP-PLATE"
    clip.geometry.source_drawing = drawing
    clip.geometry.source_revision = revision
    clip.geometry.shape_kind = "rectangular_plate"
    clip.geometry.holes.count = 1
    clip.geometry.parameters.update({"quantity": 2, "fillet_weld_mm": 6})
    clip.geometry.fabrication_ready = True
    add_custom_entry(
        result, "M.BOLT", clip_bolt_spec, _FASTENER_MATERIAL,
        2, 0, "PC",
    )
    cb = result.entries[-1]
    cb.geometry.component_id = "D57-M-BOLT"
    cb.geometry.source_drawing = drawing
    cb.geometry.source_revision = revision
    cb.geometry.shape_kind = "purchased_fastener"
    cb.geometry.parameters = {"spec": clip_bolt_spec, "quantity": 2}
    cb.geometry.fabrication_ready = True

    m34 = get_m34_by_member(member)
    if not m34:
        result.error = f"Type 47: M-34缺少 {member}"
        result.entries.clear()
        return result
    # D-57 Detail Z depicts the six-hole Type-C layout for every listed
    # member, including C100.  The generic M-34 member lookup otherwise
    # chooses the four-hole C100 variant.
    m34 = dict(m34)
    m34["D"] = None
    z_bolts = _add_lug(
        result, m34, label="TYPE-C", qty=2,
        drawing="LUG-PLATE_TYPE-C_M-34.pdf",
        component_id=f'M34-{m34["type"]}',
        bolt_spec=profile["detail_z_bolt"], hole_diameter=22,
    )
    _set_lug_material(result.entries[-1])
    add_custom_entry(
        result, "K BOLT", profile["detail_z_bolt"], _FASTENER_MATERIAL,
        z_bolts, 0, "PC",
    )
    zb = result.entries[-1]
    zb.geometry.component_id = "D57-DETAIL-Z-K-BOLT"
    zb.geometry.source_drawing = drawing
    zb.geometry.source_revision = revision
    zb.geometry.shape_kind = "purchased_fastener"
    zb.geometry.parameters = {"spec": profile["detail_z_bolt"], "quantity": z_bolts}
    zb.geometry.fabrication_ready = True

    y_bolts = 0
    if braced:
        lug = get_m36_by_member(member) if fig == "A" else get_m35_by_member(member)
        y_bolts = _add_lug(
            result, lug, label="TYPE-E" if fig == "A" else "TYPE-D", qty=2,
            drawing="LUG-PLATE_TYPE-D_E_M-35_M-36.pdf",
            component_id=f'{"M36" if fig == "A" else "M35"}-{lug["type"]}',
            bolt_spec=profile["detail_y_bolt"], hole_diameter=19,
        )
        _set_lug_material(result.entries[-1])
        add_custom_entry(
            result, "K BOLT", profile["detail_y_bolt"], _FASTENER_MATERIAL,
            y_bolts, 0, "PC",
        )
        yb = result.entries[-1]
        yb.geometry.component_id = "D57-DETAIL-Y-K-BOLT"
        yb.geometry.source_drawing = drawing
        yb.geometry.source_revision = revision
        yb.geometry.shape_kind = "purchased_fastener"
        yb.geometry.parameters = {"spec": profile["detail_y_bolt"], "quantity": y_bolts}
        yb.geometry.fabrication_ready = True

    d80_blocker = _add_d80_reference(
        result, profile, drawing, revision, line_size
    )
    if d80_blocker:
        blockers.append(d80_blocker)
    d80_not_furnished = profile["d80_ownership"] == "not_furnished"
    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": drawing,
        "source_revision": revision,
        "branch": f'{member}/FIG-{fig}/{"BRACED" if braced else "UNBRACED"}',
        "bom_ready": not bool(d80_blocker),
        "fabrication_ready": False, "blockers": blockers,
        "not_furnished": ["D-80 pipe-interface assembly"] if d80_not_furnished else [],
        "referenced_components": [] if d80_not_furnished else ["D-80"],
        "longitudinal_cut_length_mm": longitudinal,
        "transverse_cut_length_mm": transverse,
        "detail_z_bolt_quantity": z_bolts,
        "detail_y_bolt_quantity": y_bolts, "Q_mm": q_mm,
    }
    result.warnings.extend(blockers)
    result.evidence.append(make_evidence(
        "type47_dimensions",
        {
            "line_size": line_size, "Q": q_mm, "H": h_mm,
            "member": member, "A": row["A"],
            "longitudinal_cut_mm": longitudinal,
            "transverse_cut_mm": transverse,
            "d80_clearance_mm": 3,
            "right_end_extension_mm": 50,
            "brace_quantity": 2 if braced else 0,
        },
        "visual_transcription", source=drawing, confidence=0.95,
    ))
    return result
