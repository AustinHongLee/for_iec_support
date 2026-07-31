"""Type 41 source-aware wall-mounted support (D-49)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..material_specs import EXPANSION_BOLT_SUS304, STRUCTURAL_A36_SS400, SUPPORT_PLATE_A36_SS400
from ..models import AnalysisResult, set_remark
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.m45_table import get_m45_by_dia


def _parse_member(spec):
    prefix = spec[0]
    section_type = {"L": "Angle", "C": "Channel", "H": "H Beam"}[prefix]
    return section_type, spec[1:]


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("41", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 41: 尚未建立來源 profile {profile_id}"
        return result
    parts = str(fullstring).split("-")
    if len(parts) != 2 or not parts[1].isdigit():
        result.error = "Type 41: 格式應為 41-{1..9}"
        return result
    row = config["TYPE41_TABLE"].get(fullstring)
    if not row:
        result.error = f"Type 41: D-49未表列 {fullstring}"
        return result

    drawing = profile["drawing"]
    main_len = row["L"] + 200
    m1_type, m1_dim = _parse_member(row["member1"])
    add_steel_section_entry(
        result, m1_type, m1_dim, main_len, material=STRUCTURAL_A36_SS400
    )
    main = result.entries[-1]
    main.geometry.component_id = "D49-MEMBER-1"
    main.geometry.source_drawing = drawing
    main.geometry.source_revision = profile["revision"]
    main.geometry.shape_kind = "stock_section_cut"
    main.geometry.shape_spec = f'{row["member1"]}; CUT L+200={main_len}'
    main.geometry.formula = "L + 200"
    main.geometry.parameters = {
        "L_mm": row["L"], "end_allowance_mm": 200,
        "weld_size_mm": row["weld_size"], "figure": row["fig"],
    }
    main.geometry.fabrication_ready = True
    set_remark(main, f"FIG-{row['fig']}主梁，L+200={main_len}mm")

    blockers = ["D-49只給base plate厚度，未給完整平面外形尺寸"]
    brace_len = None
    if row["member2"]:
        raw = overrides.get("brace_cut_length_mm")
        if raw not in (None, ""):
            try:
                brace_len = float(raw)
            except (TypeError, ValueError):
                brace_len = 0
            if brace_len <= 0:
                result.error = "Type 41: brace_cut_length_mm必須大於0"
                return result
        else:
            brace_len = 0
            blockers.append("FIG-B斜撐切長/兩端切角未由D-49尺寸化，需brace_cut_length_mm")
        m2_type, m2_dim = _parse_member(row["member2"])
        add_steel_section_entry(
            result, m2_type, m2_dim, brace_len, material=STRUCTURAL_A36_SS400
        )
        brace = result.entries[-1]
        brace.geometry.component_id = "D49-MEMBER-2"
        brace.geometry.source_drawing = drawing
        brace.geometry.source_revision = profile["revision"]
        brace.geometry.shape_kind = "stock_section_cut"
        brace.geometry.shape_spec = (
            f'{row["member2"]}; CUT={brace_len:g}'
            if brace_len else f'{row["member2"]}; CUT LENGTH TBD'
        )
        brace.geometry.formula = "user override" if brace_len else "not dimensioned"
        brace.geometry.parameters = {"brace_cut_length_mm": brace_len or None}
        brace.geometry.fabrication_ready = False
        brace.geometry.fabrication_blockers = [
            "兩端切角/貼合輪廓未標",
            *([] if brace_len else ["切長未標"]),
        ]
        set_remark(brace, "FIG-B斜撐；切長依現場/加工圖確認")

    plate_qty = 1 if row["fig"] == "A" else 2
    add_custom_entry(
        result, name="BASE PLATE",
        spec=f'{row["base_plate_t"]}t; PLAN SIZE TBD',
        material=SUPPORT_PLATE_A36_SS400, quantity=plate_qty,
        unit_weight=0, unit="PC",
    )
    plate = result.entries[-1]
    plate.role = "base_plate"
    plate.geometry.role = "base_plate"
    plate.geometry.component_id = "D49-BASE-PLATE"
    plate.geometry.source_drawing = drawing
    plate.geometry.source_revision = profile["revision"]
    plate.geometry.shape_kind = "partially_dimensioned_plate"
    plate.geometry.shape_spec = f'PLATE THK {row["base_plate_t"]}; PLAN SIZE TBD; QTY {plate_qty}'
    plate.geometry.parameters = {
        "thickness_mm": row["base_plate_t"], "quantity": plate_qty,
        "bolt_spacing_a_mm": row["bolt_dist"], "edge_b_mm": row["b"],
    }
    plate.geometry.fabrication_ready = False
    plate.geometry.fabrication_blockers = [blockers[0]]

    bolt_qty = plate_qty * 2
    m45 = get_m45_by_dia(row["exp_bolt_dia"])
    spec = f'EB-{row["exp_bolt_dia"]}'
    if m45:
        spec += f'; L={m45["L"]}'
    add_custom_entry(
        result, name="EXP.BOLT", spec=spec,
        material=EXPANSION_BOLT_SUS304, quantity=bolt_qty,
        unit_weight=0, unit="PC",
    )
    bolt = result.entries[-1]
    bolt.geometry.component_id = "M45-EXPANSION-BOLT"
    bolt.geometry.source_drawing = "M-45"
    bolt.geometry.source_revision = "1"
    bolt.geometry.shape_kind = "purchased_fastener"
    bolt.geometry.parameters = {
        "diameter": row["exp_bolt_dia"], "quantity": bolt_qty,
        "length_mm": m45["L"] if m45 else None,
    }
    bolt.geometry.fabrication_ready = m45 is not None
    bom_ready = not row["member2"] or bool(brace_len)
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f'{fullstring}/FIG-{row["fig"]}',
        "bom_ready": bom_ready,
        "fabrication_ready": False,
        "blockers": blockers,
        "main_cut_length_mm": main_len,
        "brace_cut_length_mm": brace_len,
        "base_plate_quantity": plate_qty,
        "expansion_bolt_quantity": bolt_qty,
    }
    result.warnings.extend(blockers)
    result.evidence.append(
        make_evidence("type41_series_row", row, "visual_transcription", source=drawing, confidence=0.99)
    )
    return result
