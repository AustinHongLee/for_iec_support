"""Type 79 U-band assembly — D-94 / M-55."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import extract_parts, get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.m55_table import get_m55_by_line_size


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("79", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 79: 尚未建立來源 profile {profile_id}"
        return result

    token, anchor = extract_parts(get_part(fullstring, 2) or "")
    part3 = get_part(fullstring, 3)
    if part3 and part3.startswith("("):
        anchor = part3
    if not token or anchor.upper() not in {"", "(A)"}:
        result.error = "Type 79 格式應為 79-{line_size}B[(A)]"
        return result
    line_size = get_lookup_value(token)
    row = get_m55_by_line_size(line_size)
    if not row:
        result.error = f'Type 79: D-94/M-55 未表列 {line_size:g}"；範圍 5"~24"'
        return result

    dims = row["dimensions_mm"]
    blocker = (
        "D-94/M-55 顯示的是 U-band、兩側立板/肋板與 base 的組立；"
        "B、E、T 不是單一平板的展開長×寬×厚。舊版 B×E×T 重量已停用，"
        "需先建立各 piece 的片數、淨輪廓與彎曲展開"
    )
    add_custom_entry(
        result,
        "U-BAND ASSEMBLY",
        (
            f'{row["designation"]}; A={dims["A"]}; B={dims["B"]}; '
            f'C={dims["C"]}; D={dims["D"]}; E={dims["E"]}; T={dims["T"]}'
        ),
        row["material"],
        1,
        0,
        "SET",
        remark=blocker,
        category="鋼板類",
        item_class="reference_only",
        manufacturing_type="shaped_plate",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "D94-M55-U-BAND-ASSEMBLY"
    entry.geometry.source_drawing = "TYPE-79_D-94.pdf / U-BAND_M-55.pdf"
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = "multi_piece_u_band_support"
    entry.geometry.shape_spec = (
        f'{row["designation"]}; A{dims["A"]}; B{dims["B"]}; C{dims["C"]}; '
        f'D{dims["D"]}; F{dims["F"]}; H{dims["H"]}; J{dims["J"]}; '
        f'T{dims["T"]}; E{dims["E"]}; R{dims["R"]}'
    )
    entry.geometry.parameters = {
        "line_size_in": line_size,
        **dims,
        "anchor_option": bool(anchor),
        "anchor_weld_mm": 6 if anchor else None,
        "typical_weld_mm": 6,
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    set_remark(
        entry,
        blocker + ("；(A) 表示 anchor type，增加 6 mm anchor weld" if anchor else ""),
    )

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
            "type79_d94_m55_dimensions",
            entry.geometry.parameters,
            "visual_transcription",
            source="TYPE-79_D-94.pdf / U-BAND_M-55.pdf",
            confidence=0.99,
        )
    )
    return result
