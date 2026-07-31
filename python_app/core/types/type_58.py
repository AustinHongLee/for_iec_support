"""Type 58 source-aware U-bolt plate saddle (D-69)."""
from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.m26_table import get_m26_by_line_size
from ._m26_common import add_m26_ubolt


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("58", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 58: 尚未建立來源 profile {profile_id}"
        return result
    size = get_lookup_value(get_part(fullstring, 2))
    fig = (get_part(fullstring, 3) or "").upper()
    row = config["TYPE58_TABLE"].get(f"{size:g}")
    if not row:
        result.error = f"Type 58: 管徑不在D-69表列範圍"
        return result
    if fig not in ("A", "B"):
        result.error = "Type 58: designation必須明列FIG-A或FIG-B，不得缺省"
        return result
    drawing = profile["drawing"]
    add_plate_entry(
        result, row["plate_l"], row["plate_b"], row["plate_t"], "STEEL PLATE",
        material="Carbon Steel (grade not specified in D-69)", plate_qty=1,
        plate_role="generic_plate", bolt_switch=True,
        bolt_x=row["hole_pitch"], bolt_hole=row["hole_d"],
        bolt_size=row["rod_size"],
    )
    plate = result.entries[-1]
    plate.geometry.component_id = "D69-U-BOLT-PLATE"
    plate.geometry.source_drawing = drawing
    plate.geometry.source_revision = profile["revision"]
    plate.geometry.shape_kind = "rectangular_plate"
    plate.geometry.holes.pattern = "rect"
    plate.geometry.holes.count = 2
    plate.geometry.holes.pitch_x = row["hole_pitch"]
    plate.geometry.parameters = {
        "length_mm": row["plate_l"], "width_mm": row["plate_b"],
        "thickness_mm": row["plate_t"], "hole_count": 2,
        "hole_diameter_mm": row["hole_d"], "hole_pitch_mm": row["hole_pitch"],
        "figure": fig, "fig_b_fillet_weld_mm": row["x"] if fig == "B" else None,
    }
    plate.geometry.fabrication_ready = True
    set_remark(plate, f'D-69 FIG-{fig}；2-Ø{row["hole_d"]}，P={row["hole_pitch"]}mm')

    m26 = get_m26_by_line_size(size)
    if not m26:
        result.error = f"Type 58: M-26缺少 {size:g}吋U-bolt"
        result.entries.clear()
        return result
    blockers = add_m26_ubolt(
        result,
        row=m26,
        drawing=profile["m26_drawing"],
        revision=profile["revision"],
        component_prefix="D69-M26",
        host_note=f"D-69 FIG-{fig}",
        host_parameters={"figure": fig},
    )
    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": drawing,
        "source_revision": profile["revision"], "branch": f"FIG-{fig}",
        "bom_ready": False, "fabrication_ready": False, "blockers": blockers,
        "installation": (
            {"fig_b_fillet_weld_mm": row["x"]} if fig == "B"
            else {"existing_support": "steel plate"}
        ),
    }
    result.warnings.extend(blockers)
    result.evidence.append(make_evidence(
        "type58_table_row", {"line_size": size, **row},
        "visual_transcription", source=drawing, confidence=0.99,
    ))
    return result
