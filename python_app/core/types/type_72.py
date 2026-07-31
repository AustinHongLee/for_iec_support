"""Type 72 M-54 Fig.2 strap support — D-87."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, HolePattern, set_remark
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.m45_table import get_m45_by_type
from data.m54_table import build_m54_item
from data.type72_table import get_type72_data


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("72", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 72: 尚未建立來源 profile {profile_id}"
        return result

    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 72 格式應為 72-{line_size}B"
        return result
    line_size = get_lookup_value(part2)
    row = get_type72_data(line_size)
    strap = build_m54_item(line_size, fig_no=2)
    if not row or not strap:
        result.error = f'Type 72: D-87/M-54 未表列 {line_size:g}"；範圍 3/4"~4"'
        return result

    strap_blocker = (
        "M-54 的 B 是成形後外側跨距，不是已證實的平板展開長；"
        "缺 bend allowance/展開基準，舊版 B×C×T 重量已停用"
    )
    add_custom_entry(
        result,
        "STRAP",
        strap["spec"],
        strap["material"],
        1,
        0,
        "PC",
        remark=strap_blocker,
        category="鋼板類",
        item_class="reference_only",
        manufacturing_type="shaped_plate",
    )
    strap_entry = result.entries[-1]
    strap_entry.geometry.component_id = "D87-M54-FIG2-STRAP"
    strap_entry.geometry.source_drawing = "TYPE-72_D-87.pdf / STRAP_M-54.pdf"
    strap_entry.geometry.source_revision = profile["revision"]
    strap_entry.geometry.shape_kind = "formed_pipe_strap"
    strap_entry.geometry.shape_spec = (
        f'M-54 FIG.2; A={row["A"]}; B={row["B"]}; C={row["C"]}; '
        f'T={row["T"]}; H={row["H"]}; R={row["R"]}; D={row["D"]}'
    )
    strap_entry.geometry.holes = HolePattern(
        pattern="single",
        diameter=11,
        count=2,
        fastener_spec='EB-3/8"',
    )
    strap_entry.geometry.parameters = {
        **row,
        "figure": 2,
        "hole_count": 2,
        "hole_diameter_mm": 11,
    }
    strap_entry.geometry.fabrication_ready = False
    strap_entry.geometry.fabrication_blockers = [strap_blocker]
    set_remark(strap_entry, strap_blocker)

    bolt = get_m45_by_type("EB-3/8")
    bolt_blocker = (
        "D-87/M-45 定義 EB-3/8 規格與鑽孔資料，但未給材料與單重；"
        "移除舊版每組 1 kg placeholder"
    )
    add_custom_entry(
        result,
        "EXP. BOLT",
        bolt["type"] if bolt else "EB-3/8",
        str(overrides.get("expansion_bolt_material") or "MATERIAL TBD"),
        2,
        0,
        "SET",
        remark=bolt_blocker,
        manufacturing_type="purchased",
    )
    bolt_entry = result.entries[-1]
    bolt_entry.geometry.component_id = "D87-M45-EXPANSION-BOLTS"
    bolt_entry.geometry.source_drawing = "TYPE-72_D-87.pdf / M-45"
    bolt_entry.geometry.source_revision = profile["revision"]
    bolt_entry.geometry.shape_kind = "purchased_expansion_bolt"
    bolt_entry.geometry.parameters = {
        "designation": "EB-3/8",
        "quantity": 2,
        "hole_diameter_mm": 11,
        **(bolt or {}),
    }
    bolt_entry.geometry.fabrication_ready = False
    bolt_entry.geometry.fabrication_blockers = [bolt_blocker]
    set_remark(bolt_entry, bolt_blocker)

    blockers = [strap_blocker, bolt_blocker]
    result.warnings.extend(blockers)
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {"line_size_in": line_size, **row},
    }
    result.evidence.append(
        make_evidence(
            "type72_d87_m54_dimensions",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source="TYPE-72_D-87.pdf / STRAP_M-54.pdf",
            confidence=0.99,
        )
    )
    return result
