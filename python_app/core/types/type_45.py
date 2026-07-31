"""Type 45 source-aware lug-mounted vessel frame (D-54/D-55)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..material_specs import ANCHOR_BOLT_SUS304, PLATE_LUG_A36_SS400, STRUCTURAL_A36_SS400, SUPPORT_PLATE_A36_SS400
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from ._lug_plate_common import lug_hole_count
from data.m34_table import get_m34_by_member
from data.m35_table import get_m35_by_member
from data.m36_table import get_m36_by_member
from data.steel_sections import get_section_details
from data.type45_table import get_type45_brace


def _add_lug(result, lug, *, label, qty, drawing, component_id, bolt_spec, hole_diameter=None):
    holes = lug_hole_count(lug)
    diameter = hole_diameter or lug["J"]
    add_plate_entry(
        result, lug["A"], lug["B"], lug["T"], f"LUG PLATE {label}",
        material=PLATE_LUG_A36_SS400, plate_qty=qty,
        plate_role="lug_plate", bolt_switch=True,
        bolt_x=2 * lug["E"] + lug["F"], bolt_y=2 * (lug.get("G") or 0),
        bolt_hole=diameter, bolt_size=bolt_spec,
    )
    entry = result.entries[-1]
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = "1"
    entry.geometry.shape_kind = "standard_lug_plate"
    entry.geometry.shape_spec = (
        f'{lug["type"]}; {lug["A"]}x{lug["B"]}x{lug["T"]}t; '
        f'{holes}-HOLE DIA{diameter}; QTY {qty}'
    )
    entry.geometry.holes.count = holes
    entry.geometry.parameters.update(
        {
            "lgp_type": lug["type"], "hole_count_per_plate": holes,
            "quantity": qty, "E_mm": lug["E"], "F_mm": lug["F"],
            "G_mm": lug.get("G"), "H_mm": lug.get("H"),
        }
    )
    entry.geometry.fabrication_ready = True
    return holes * qty


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("45", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 45: 尚未建立來源 profile {profile_id}"
        return result
    parts = str(fullstring).split("-")
    if len(parts) not in (4, 5):
        result.error = "Type 45: 格式應為 45-{line size}B-{M}-{H} {A/B}[-{Q mm}]"
        return result
    line_size = get_lookup_value(parts[1])
    member = parts[2].upper()
    details = get_section_details(member)
    row = config["TYPE45_MEMBER"].get(member)
    try:
        token = parts[3].split()
        h_mm = int(token[0])
        fig = token[1].upper() if len(token) > 1 else "A"
        q_mm = int(parts[4]) if len(parts) == 5 else config["TYPE45_PIPE_Q"][str(int(line_size))]
    except (KeyError, TypeError, ValueError):
        result.error = "Type 45: line size/H/Q無法依D-54/D-55解析"
        return result
    if not row or not details:
        result.error = f"Type 45: D-55未支援MEMBER {member}"
        return result
    if fig not in ("A", "B") or h_mm <= 0 or q_mm <= 0:
        result.error = "Type 45: H/Q需大於0，FIG需為A/B"
        return result
    longitudinal = h_mm - row["A"] + q_mm + 3
    transverse = 2 * q_mm + 6
    if longitudinal <= 0:
        result.error = f"Type 45: H-A+Q+3={longitudinal}mm，縱向member無有效長度"
        return result

    drawing = " / ".join(profile["drawings"])
    blockers = [
        "D-55的MIN. CHANNEL REQUIRED圖表尚未完整轉成可驗證選型矩陣",
        "H-A+Q+3的vessel端起點與實際曲面端切需設備幾何確認",
    ]
    for cid, role, length, qty, formula in (
        ("D54-LONGITUDINAL", "縱向member", longitudinal, 2, "H - A + Q + 3"),
        ("D54-TRANSVERSE", "橫向member", transverse, 2, "2Q + 6"),
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
            "H_mm": h_mm, "A_mm": row["A"], "Q_mm": q_mm,
            "quantity": qty, "figure": fig,
        }
        entry.geometry.fabrication_ready = cid == "D54-TRANSVERSE"
        if cid == "D54-LONGITUDINAL":
            entry.geometry.fabrication_blockers = [blockers[1]]
        set_remark(entry, f"{role}，{length}mm ×{qty}")

    braced = h_mm > config["TYPE45_BRACE_H_MIN"]
    if braced:
        brace_data = get_type45_brace(fig)
        add_steel_section_entry(
            result, "Angle", "50*50*6", brace_data["length"],
            material=STRUCTURAL_A36_SS400,
        )
        brace = result.entries[-1]
        brace.geometry.component_id = "D54-L50-BRACE"
        brace.geometry.source_drawing = drawing
        brace.geometry.source_revision = profile["revision"]
        brace.geometry.shape_kind = "stock_section_cut"
        brace.geometry.parameters = {
            "figure": fig, "theta_deg": 30 if fig == "A" else 45,
            "cut_length_mm": brace_data["length"],
        }
        brace.geometry.fabrication_ready = False
        brace.geometry.fabrication_blockers = ["斜撐兩端切角/貼合輪廓未完整尺寸化"]
        blockers.append("斜撐兩端切角/貼合輪廓未完整尺寸化")

    add_plate_entry(
        result, 90, 45, 6, "CLIP PLATE",
        material=SUPPORT_PLATE_A36_SS400, plate_qty=2,
        plate_role="generic_plate", bolt_switch=True,
        bolt_hole=16, bolt_size='1/2"x30',
    )
    clip = result.entries[-1]
    clip.geometry.component_id = "D54-CLIP-PLATE"
    clip.geometry.source_drawing = drawing
    clip.geometry.source_revision = profile["revision"]
    clip.geometry.shape_kind = "rectangular_plate"
    clip.geometry.holes.count = 1
    clip.geometry.parameters.update({"quantity": 2, "fillet_weld_mm": 6})
    clip.geometry.fabrication_ready = True
    add_custom_entry(
        result, name="M.BOLT", spec='1/2"x30',
        material=ANCHOR_BOLT_SUS304, quantity=2, unit_weight=0, unit="PC",
    )
    clip_bolt = result.entries[-1]
    clip_bolt.geometry.component_id = "D54-M-BOLT"
    clip_bolt.geometry.source_drawing = drawing
    clip_bolt.geometry.source_revision = profile["revision"]
    clip_bolt.geometry.shape_kind = "purchased_fastener"
    clip_bolt.geometry.parameters = {"spec": '1/2"x30', "quantity": 2}
    clip_bolt.geometry.fabrication_ready = True

    m34 = get_m34_by_member(member)
    if not m34:
        result.error = f"Type 45: M-34缺少 {member}"
        result.entries.clear()
        return result
    z_bolts = _add_lug(
        result, m34, label="TYPE-C", qty=2,
        drawing="LUG-PLATE_TYPE-C_M-34.pdf",
        component_id=f'M34-{m34["type"]}', bolt_spec=row["K"],
    )
    add_custom_entry(
        result, name="K BOLT", spec=row["K"],
        material=ANCHOR_BOLT_SUS304, quantity=z_bolts,
        unit_weight=0, unit="PC",
    )
    zbolt = result.entries[-1]
    zbolt.geometry.component_id = "D54-DETAIL-Z-K-BOLT"
    zbolt.geometry.source_drawing = drawing
    zbolt.geometry.source_revision = profile["revision"]
    zbolt.geometry.shape_kind = "purchased_fastener"
    zbolt.geometry.parameters = {"spec": row["K"], "quantity": z_bolts}
    zbolt.geometry.fabrication_ready = True

    y_bolts = 0
    if braced:
        my = get_m36_by_member(member) if fig == "A" else get_m35_by_member(member)
        if not my:
            result.error = f"Type 45: M-35/M-36缺少 {member}"
            result.entries.clear()
            return result
        y_bolts = _add_lug(
            result, my, label="TYPE-E" if fig == "A" else "TYPE-D", qty=1,
            drawing="LUG-PLATE_TYPE-D_E_M-35_M-36.pdf",
            component_id=f'{"M36" if fig == "A" else "M35"}-{my["type"]}',
            bolt_spec='5/8"x40', hole_diameter=19,
        )
        add_custom_entry(
            result, name="K BOLT", spec='5/8"x40',
            material=ANCHOR_BOLT_SUS304, quantity=y_bolts,
            unit_weight=0, unit="PC",
        )
        ybolt = result.entries[-1]
        ybolt.geometry.component_id = "D54-DETAIL-Y-K-BOLT"
        ybolt.geometry.source_drawing = drawing
        ybolt.geometry.source_revision = profile["revision"]
        ybolt.geometry.shape_kind = "purchased_fastener"
        ybolt.geometry.parameters = {"spec": '5/8"x40', "quantity": y_bolts, "hole_diameter_mm": 19}
        ybolt.geometry.fabrication_ready = True

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f'{member}/FIG-{fig}/{"BRACED" if braced else "UNBRACED"}',
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": blockers,
        "longitudinal_cut_length_mm": longitudinal,
        "transverse_cut_length_mm": transverse,
        "detail_z_bolt_quantity": z_bolts,
        "detail_y_bolt_quantity": y_bolts,
        "Q_mm": q_mm,
    }
    result.warnings.extend(blockers)
    result.evidence.append(
        make_evidence(
            "type45_dimensions",
            {"line_size": line_size, "Q": q_mm, "H": h_mm, "member": member, "A": row["A"]},
            "visual_transcription", source=drawing, confidence=0.95,
        )
    )
    return result
