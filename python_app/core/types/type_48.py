"""Type 48 drain-hub offset/bent plate blank (D-59)."""
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import extract_parts, get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("48", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 48: 尚未建立來源 profile {profile_id}"
        return result
    raw = get_part(fullstring, 2)
    token, symbol = extract_parts(raw or "")
    size = get_lookup_value(token)
    row = config["TYPE48_TABLE"].get(f"{size:g}")
    material = config["TYPE48_MATERIAL_MAP"].get(symbol)
    if not raw or not row:
        result.error = f"Type 48: 管徑 {token or '(空白)'} 不在D-59範圍 (1/2~6吋)"
        return result
    if material is None:
        result.error = f"Type 48: D-59不支援材質符號 {symbol}"
        return result
    drawing = profile["drawing"]
    add_plate_entry(
        result, row["plate_a"], row["plate_b"], row["plate_t"], "PLATE",
        material=material, plate_qty=1, plate_role="generic_plate",
    )
    plate = result.entries[-1]
    plate.geometry.component_id = "D59-OFFSET-PLATE"
    plate.geometry.source_drawing = drawing
    plate.geometry.source_revision = profile["revision"]
    plate.geometry.shape_kind = "bent_offset_plate_blank"
    plate.geometry.parameters = {
        "blank_length_mm": row["plate_a"], "blank_width_mm": row["plate_b"],
        "thickness_mm": row["plate_t"], "upper_leg_mm": 100,
        "lower_offset_mm": 20, "fillet_weld_mm": 6,
    }
    blockers = [
        "D-59只給PLATE SIZE與100/20配置，未給折彎線、彎曲半徑及各腿完整尺寸；150x100只能作備料blank",
        "板與管線/Drain Hub的三維定位及管壁貼合焊口需專案管線模型確認",
    ]
    plate.geometry.fabrication_ready = False
    plate.geometry.fabrication_blockers = blockers[:]
    set_remark(
        plate,
        "D-59偏移/折彎板備料；blank 150x100，圖示100/20配置，6mm焊",
    )
    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": drawing,
        "source_revision": profile["revision"], "branch": f'{size:g}in/{symbol or "CS"}',
        "bom_ready": True, "fabrication_ready": False, "blockers": blockers,
        "blank_ready": True,
    }
    result.warnings.extend(blockers)
    result.evidence.append(make_evidence(
        "type48_plate", row, "visual_transcription", source=drawing, confidence=0.98,
    ))
    return result
