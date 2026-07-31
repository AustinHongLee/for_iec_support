"""Type 76 large-pipe 120-degree reinforcing pad — D-91."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.type76_table import get_type76_data


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("76", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 76: 尚未建立來源 profile {profile_id}"
        return result

    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 76 格式應為 76-{line_size}B"
        return result
    line_size = get_lookup_value(part2)
    row = get_type76_data(line_size)
    if not row:
        result.error = f'Type 76: D-91 未表列 {line_size:g}"；範圍 26"~42"'
        return result

    developed_width = overrides.get("pad_developed_width_mm")
    thickness = overrides.get("pad_thickness_mm")
    material = str(overrides.get("pad_material") or "SAME AS PIPE / C.S. PLATE")
    blockers: list[str] = []
    if developed_width not in (None, "") and thickness not in (None, ""):
        developed_width = float(developed_width)
        thickness = float(thickness)
        if developed_width <= 0 or thickness < row["thickness_mm"]:
            result.error = (
                f"Type 76: pad_developed_width_mm 必須>0，pad_thickness_mm "
                f"不得小於 D-91 的 {row['thickness_mm']} mm"
            )
            return result
        add_plate_entry(
            result,
            row["pad_length_mm"],
            developed_width,
            thickness,
            "PIPE PAD",
            material=material,
            plate_qty=1,
            plate_role="reinforcement_pad",
            formula="explicit developed width override",
            notes_zh="D-91 120° rolled pad；展開寬與實際厚度由本筆 override 提供",
            shape_spec=(
                f'DEVELOPED {row["pad_length_mm"]}x{developed_width:g}x{thickness:g}t; '
                "ROLL 120deg"
            ),
            shape_kind="rolled_arc_plate",
        )
        pad = result.entries[-1]
        pad.geometry.fabrication_ready = True
    else:
        blocker = (
            "D-91 允許 PAD 由 main pipe 切取或由 C/S plate 製作，12t 僅為最小值；"
            "圖面未給唯一展開寬/實際壁厚，舊版 OD 外圓弧×400×12t 只是推估，已停用。"
            "需提供 pad_developed_width_mm 與 pad_thickness_mm"
        )
        add_custom_entry(
            result,
            "PIPE PAD",
            (
                f'120deg x {row["pad_length_mm"]}L x '
                f'{row["thickness_mm"]}t MIN.; OD={row["od_mm"]}'
            ),
            material,
            1,
            0,
            "PC",
            remark=blocker,
            category="鋼板類",
            item_class="reference_only",
            manufacturing_type="shaped_plate",
        )
        pad = result.entries[-1]
        pad.geometry.fabrication_ready = False
        pad.geometry.fabrication_blockers = [blocker]
        blockers.append(blocker)

    pad.geometry.component_id = "D91-120DEG-PIPE-PAD"
    pad.geometry.source_drawing = profile["drawing"]
    pad.geometry.source_revision = profile["revision"]
    pad.geometry.shape_kind = "rolled_arc_plate_or_pipe_segment"
    pad.geometry.shape_spec = (
        f'120deg; axial L={row["pad_length_mm"]}; t>={row["thickness_mm"]}; '
        f'pipe OD={row["od_mm"]}'
    )
    pad.geometry.parameters = {
        "line_size_in": line_size,
        "pipe_od_mm": row["od_mm"],
        "contact_angle_deg": row["pad_angle_deg"],
        "axial_length_mm": row["pad_length_mm"],
        "minimum_thickness_mm": row["thickness_mm"],
        "developed_width_mm": developed_width,
        "actual_thickness_mm": thickness,
        "weld_mm": 6,
        "manufacturing_options": [
            "CUT FROM MAIN PIPE",
            "FABRICATED FROM CARBON STEEL PLATE",
        ],
    }
    set_remark(
        pad,
        "D-91 120°×400；6 mm weld"
        + (
            f"；override 展開寬={developed_width:g}、厚={thickness:g}"
            if developed_width not in (None, "")
            else f"；{blockers[-1]}"
        ),
    )
    if profile.get("special_weld_note"):
        result.warnings.append(profile["special_weld_note"])
    result.warnings.extend(blockers)
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": not blockers,
        "fabrication_ready": not blockers,
        "blockers": blockers,
        "assembly_dimensions": pad.geometry.parameters,
    }
    result.evidence.append(
        make_evidence(
            "type76_d91_geometry",
            {
                "line_size_in": line_size,
                "angle_deg": row["pad_angle_deg"],
                "length_mm": row["pad_length_mm"],
                "minimum_thickness_mm": row["thickness_mm"],
            },
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
