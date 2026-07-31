"""Type 77 large-pipe saddle — D-92."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import extract_parts, get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.type77_table import get_type77_data


_MATERIAL_SYMBOLS = {
    "": "CARBON STEEL / SAME OR SIMILAR TO PIPE",
    "(A)": "ALLOY STEEL / A/S PLATE",
    "(S)": "STAINLESS STEEL / S/S PLATE",
}


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("77", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 77: 尚未建立來源 profile {profile_id}"
        return result

    token, symbol = extract_parts(get_part(fullstring, 2) or "")
    part3 = get_part(fullstring, 3)
    if part3 and part3.startswith("("):
        symbol = part3
    symbol = symbol.upper()
    if not token or symbol not in _MATERIAL_SYMBOLS:
        result.error = "Type 77 格式應為 77-{line_size}B[(A|S)]"
        return result
    line_size = get_lookup_value(token)
    row = get_type77_data(line_size)
    if not row:
        result.error = f'Type 77: D-92 未表列 {line_size:g}"；允許 26,28,30,32,34,36,40"'
        return result

    material = str(overrides.get("saddle_material") or _MATERIAL_SYMBOLS[symbol])
    blocker = (
        "D-92 的 saddle 由多片斜板、120°/20°/30° 接觸輪廓與 reinforcing pad 組成；"
        "A/B/C/T/H 是組立尺寸，不是單一矩形板。舊版 C×H+A×B 外包重量已停用，"
        "需先把各 piece 的淨輪廓/片數建成 cutting recipe"
    )
    add_custom_entry(
        result,
        "SADDLE ASSEMBLY",
        f'A={row["A"]}; B={row["B"]}; C={row["C"]}; T={row["T"]}; H={row["H"]}',
        material,
        1,
        0,
        "SET",
        remark=blocker,
        category="鋼板類",
        item_class="reference_only",
        manufacturing_type="shaped_plate",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "D92-SADDLE-ASSEMBLY"
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = "multi_piece_large_pipe_saddle"
    entry.geometry.shape_spec = (
        f'D-92; A{row["A"]}; B{row["B"]}; C{row["C"]}; '
        f'T{row["T"]}; H{row["H"]}; MATERIAL={symbol or "CS"}'
    )
    entry.geometry.parameters = {
        "line_size_in": line_size,
        "A_mm": row["A"],
        "B_mm": row["B"],
        "C_mm": row["C"],
        "T_mm": row["T"],
        "H_mm": row["H"],
        "pipe_contact_angle_deg": 120,
        "lower_angle_deg": 20,
        "side_angle_deg": 30,
        "side_clearance_mm": 50,
        "reinforcing_pad_weep_hole_diameter_mm": 10,
        "reinforcing_pad_weep_hole_count": 2,
        "material_symbol": symbol,
        "material_rule": _MATERIAL_SYMBOLS[symbol],
        "fillet_weld_mm": 6,
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    set_remark(entry, blocker)

    result.warnings.append(blocker)
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": [blocker],
        "assembly_dimensions": entry.geometry.parameters,
    }
    result.evidence.append(
        make_evidence(
            "type77_d92_dimensions",
            entry.geometry.parameters,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
