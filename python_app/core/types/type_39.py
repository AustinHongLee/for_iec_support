"""Type 39 source-aware vessel braced support (D-45)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..issues import register_source_envelope
from ..models import AnalysisResult, set_remark
from ..parser import get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from ..trunnion_engine import ANCHOR_BOLT_MATERIAL, PLATE_LUG_MATERIAL, STRUCTURAL_MATERIAL
from ._lug_plate_common import lug_hole_count
from data.m34_table import get_m34_by_member
from data.m35_table import get_m35_by_member
from data.m36_table import get_m36_by_member
from data.steel_sections import get_section_details
from data.type39_table import get_type39_data, get_type39_formula


def _decorate_lug(entry, lug, *, component_id, drawing):
    holes = lug_hole_count(lug)
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = "1"
    entry.geometry.shape_kind = "standard_lug_plate"
    entry.geometry.shape_spec = (
        f'{lug["type"]}; {lug["A"]}x{lug["B"]}x{lug["T"]}t; '
        f'{holes}-HOLE DIA{lug["J"]}'
    )
    entry.geometry.holes.count = holes
    entry.geometry.parameters.update(
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
    entry.geometry.fabrication_ready = True
    return holes


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("39", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 39: 尚未建立來源 profile {profile_id}"
        return result

    member = (get_part(fullstring, 2) or "").upper()
    token = (get_part(fullstring, 3) or "").split()
    if len(token) != 2:
        result.error = "Type 39: 格式應為 39-{M}-{H} {A/B}[-{L×100}]"
        return result
    try:
        h_mm = int(token[0])
        l_mm = int(get_part(fullstring, 4)) * 100 if get_part(fullstring, 4) else 200
    except (TypeError, ValueError):
        result.error = "Type 39: H/L必須為正整數"
        return result
    fig = token[1].upper()
    row = get_type39_data(member)
    formula = get_type39_formula(member, fig)
    details = get_section_details(member)
    if fig not in ("A", "B") or not row or not formula or not details:
        result.error = f"Type 39: 無效的MEMBER/FIG {member}/FIG-{fig}"
        return result
    if h_mm <= 0 or l_mm <= 0:
        result.error = f"Type 39 / {profile_id}: H={h_mm}超出{member} 0<H≤{row['H_MAX']}mm，且L需大於0"
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 39 / {profile_id}",
        source_ref=f"D-45 {member} H(MAX)",
        checks=(("H", h_mm, row["H_MAX"], True),),
    ):
        return result

    s_mm = round(formula["s_coeff"] * h_mm + formula["s_offset"])
    n_mm = round(formula["n_coeff"] * h_mm + formula["n_offset"])
    theta = 30 if fig == "A" else 45
    m34 = get_m34_by_member(member)
    mz = get_m36_by_member(member) if fig == "A" else get_m35_by_member(member)
    if not m34 or not mz:
        result.error = f"Type 39: M-34/M-{'36' if fig == 'A' else '35'}缺少 {member}"
        return result
    drawing = profile["drawing"]
    blockers = ["斜撐兩端切角/貼合輪廓未在D-45完整尺寸化"]
    for cid, role, length, formula_text in (
        ("D45-MAIN-BEAM", "主梁", h_mm + l_mm, "H + L"),
        ("D45-BRACE", "斜撐", n_mm, "N(member, H, figure)"),
    ):
        add_steel_section_entry(
            result, details["type"], details["size"][1:], length,
            material=STRUCTURAL_MATERIAL,
        )
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.shape_spec = f'{details["size"]}; CUT={length}'
        entry.geometry.formula = formula_text
        entry.geometry.parameters = {
            "H_mm": h_mm, "L_mm": l_mm, "S_mm": s_mm, "N_mm": n_mm,
            "figure": fig, "theta_deg": theta,
        }
        entry.geometry.fabrication_ready = cid == "D45-MAIN-BEAM"
        if cid == "D45-BRACE":
            entry.geometry.fabrication_blockers = blockers[:]
        set_remark(entry, f"{role}，下料長度{length}mm")

    add_plate_entry(
        result, m34["A"], m34["B"], m34["T"], "LUG PLATE TYPE-C",
        material=PLATE_LUG_MATERIAL, plate_role="lug_plate",
        bolt_switch=True, bolt_x=2 * m34["E"] + m34["F"],
        bolt_y=2 * (m34.get("G") or 0), bolt_hole=m34["J"],
        bolt_size=profile["bolt_spec"],
    )
    y_holes = _decorate_lug(
        result.entries[-1], m34, component_id=f'M34-{m34["type"]}',
        drawing="LUG-PLATE_TYPE-C_M-34.pdf",
    )
    m_ref = "M-36" if fig == "A" else "M-35"
    label = "TYPE-E" if fig == "A" else "TYPE-D"
    add_plate_entry(
        result, mz["A"], mz["B"], mz["T"], f"LUG PLATE {label}",
        material=PLATE_LUG_MATERIAL, plate_role="lug_plate",
        bolt_switch=True, bolt_x=2 * mz["E"] + mz["F"],
        bolt_y=2 * (mz.get("G") or 0), bolt_hole=mz["J"],
        bolt_size=profile["bolt_spec"],
    )
    z_holes = _decorate_lug(
        result.entries[-1], mz, component_id=f'{m_ref}-{mz["type"]}',
        drawing=f"LUG-PLATE_{label}_{m_ref}.pdf",
    )
    bolt_qty = y_holes + z_holes
    add_custom_entry(
        result, name="K BOLT", spec=profile["bolt_spec"],
        material=ANCHOR_BOLT_MATERIAL, quantity=bolt_qty,
        unit_weight=0, unit="PC",
    )
    bolt = result.entries[-1]
    bolt.geometry.component_id = "D45-K-BOLT"
    bolt.geometry.source_drawing = drawing
    bolt.geometry.source_revision = profile["revision"]
    bolt.geometry.shape_kind = "purchased_fastener"
    bolt.geometry.parameters = {"spec": profile["bolt_spec"], "quantity": bolt_qty}
    bolt.geometry.fabrication_ready = True
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f"{member}/FIG-{fig}",
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": blockers,
        "S_mm": s_mm,
        "N_mm": n_mm,
        "bolt_quantity": bolt_qty,
    }
    result.warnings.append("斜撐BOM長度可算；端切/貼合輪廓仍需加工圖確認")
    result.evidence.extend(
        [
            make_evidence("type39_member_row", row, "visual_transcription", source=drawing, confidence=0.99),
            make_evidence("type39_formula", formula, "visual_transcription", source=drawing, confidence=0.99),
        ]
    )
    return result
