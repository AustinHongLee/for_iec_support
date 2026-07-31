"""Type 57 source-aware U-bolt assembly support (D-68/M-26)."""
from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import extract_parts, get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.m26_table import get_m26_by_line_size
from ._m26_common import add_m26_ubolt


def _add_assembly(result, spec, material, drawing, revision, params, blocker):
    add_custom_entry(
        result,
        "U-BOLT ASSEMBLY",
        spec,
        material,
        1,
        0,
        "SET",
        remark="含1支U-bolt及4只finished hex nuts",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "D68-U-BOLT-ASSEMBLY"
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "purchased_fastener"
    entry.geometry.parameters = params
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    set_remark(entry, blocker)


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("57", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 57: 尚未建立來源 profile {profile_id}"
        return result
    raw_size = get_part(fullstring, 2)
    raw_mode = get_part(fullstring, 3)
    mode, symbol = extract_parts(raw_mode or "")
    mode = mode.upper()
    size = get_lookup_value(raw_size)
    if mode not in ("A", "B"):
        result.error = "Type 57: D-68模式僅允許A(SLIDE)或B(FIXED)"
        return result
    drawing = profile["drawing"]
    revision = profile["revision"]

    if profile["kind"] == "m26":
        if symbol:
            result.error = f"Type 57 / {profile_id}: 來源圖未定義材質後綴 {symbol}"
            return result
        row = get_m26_by_line_size(size)
        if not row or size > profile["max_size"]:
            result.error = f"Type 57 / {profile_id}: 管徑不在D-68/M-26表列範圍"
            return result
        material = "Carbon Steel"
        ub_spec = row["type"]
        rod = row["rod_size_a"]
        params = {
            **row,
            "quantity": 1,
            "mode": mode,
            "finished_hex_nut_quantity": 4,
        }
        blockers = add_m26_ubolt(
            result,
            row=row,
            drawing=profile.get("m26_drawing", drawing),
            revision=revision,
            component_prefix="D68-M26",
            host_note=f"D-68 FIG-{mode}",
            host_parameters={"mode": mode},
        )
    else:
        row = profile["table"].get(f"{size:g}")
        if not row:
            result.error = f"Type 57 / {profile_id}: 管徑不在D-68公制表列範圍"
            return result
        if symbol not in ("", "(S)"):
            result.error = f"Type 57 / {profile_id}: 僅允許空白或(S)後綴"
            return result
        material = "Stainless Steel" if symbol == "(S)" else "Carbon Steel"
        ub_spec = row["u_bolt"]
        rod = row["rod"]
        params = {
            "line_size_in": size, "rod_size": rod, "C_mm": row["C"],
            "hole_diameter_mm": row["H"], "quantity": 1, "mode": mode,
            "finished_hex_nut_quantity": 4,
        }
        metric_blocker = (
            "20E D-68只給U-bolt規格、孔距與孔徑，未給腿長/螺紋長/彎曲展開；"
            "組件重量與加工圖皆須供應商資料"
        )
        _add_assembly(
            result, ub_spec, material, drawing, revision, params, metric_blocker
        )
        blockers = [metric_blocker]
    source_conflict = profile["kind"] == "metric" and size == 0.25
    if source_conflict:
        blockers.append(
            "20E D-68頁首寫1/2~6吋但表格明列1/4吋；原圖自相矛盾，1/4吋須專案確認"
        )

    if profile["kind"] == "metric" and symbol == "(S)":
        shim_t = profile["shim_thickness_mm"]
        add_plate_entry(
            result, row["shim_l"], row["shim_w"], shim_t, "SHIM PLATE",
            material="A240-304", plate_qty=1, plate_role="generic_plate",
            bolt_switch=True, bolt_x=row["C"], bolt_hole=row["H"],
            bolt_size=rod,
        )
        shim = result.entries[-1]
        shim.geometry.component_id = "D68-SS-SHIM-PLATE"
        shim.geometry.source_drawing = drawing
        shim.geometry.source_revision = revision
        shim.geometry.shape_kind = "rectangular_plate"
        shim.geometry.holes.pattern = "rect"
        shim.geometry.holes.count = 2
        shim.geometry.holes.pitch_x = row["C"]
        shim.geometry.parameters.update({
            "length_mm": row["shim_l"], "width_mm": row["shim_w"],
            "thickness_mm": shim_t, "gauge": profile["shim_gauge"],
            "hole_count": 2,
            "hole_diameter_mm": row["H"], "hole_pitch_mm": row["C"],
        })
        shim.geometry.fabrication_ready = True
        set_remark(
            shim,
            f'20E4588 D-68：不鏽鋼管線用{profile["shim_gauge"]} shim plate',
        )

    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": drawing,
        "source_revision": revision, "branch": f'FIG-{mode}/{symbol or "CS"}',
        "bom_ready": not blockers and not source_conflict,
        "fabrication_ready": False,
        "blockers": blockers,
    }
    result.warnings.extend(blockers)
    result.evidence.append(make_evidence(
        "type57_selection", {"line_size": size, "mode": mode, "material_symbol": symbol, **params},
        "visual_transcription", source=drawing, confidence=0.97,
    ))
    return result
