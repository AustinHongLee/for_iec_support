"""Project-list UB1 alias resolved against Chung Wei M-26."""

from __future__ import annotations

import re

from companies.eko.parser import parse_inch
from core.issues import add_issue
from core.models import AnalysisResult
from core.truth import apply_truth_contract, make_evidence
from core.types._m26_common import add_m26_ubolt
from data.m26_table import get_m26_by_line_size


def _parse_size(fullstring: str) -> float:
    match = re.fullmatch(r"\s*UB1-(.+?)\s*", str(fullstring or ""), re.I)
    if not match:
        raise ValueError('UB1專案別名格式應為 UB1-□"')
    token = match.group(1).strip()
    if token.upper().endswith("B"):
        token = token[:-1]
    size = parse_inch(token)
    if size is None or size <= 0:
        raise ValueError(f"UB1: 無法解析管徑 {match.group(1)!r}")
    return float(size)


def calculate(
    fullstring: str,
    config: dict,
    overrides: dict | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    try:
        size = _parse_size(fullstring)
    except ValueError as exc:
        result.error = str(exc)
        return result

    row = get_m26_by_line_size(size)
    if row is None:
        result.error = f'M-26: 找不到 {size:g}" U-bolt表列資料'
        return result

    blockers = add_m26_ubolt(
        result,
        row=row,
        drawing=config["drawing"],
        revision=config["revision"],
        component_prefix="M26-PROJECT-ALIAS",
        host_note=f'專案清單 {fullstring} → {row["type"]}',
        host_parameters={
            "project_alias": fullstring,
            "resolved_designation": row["type"],
            "line_size_in": size,
        },
    )
    add_issue(
        result,
        code="UB1_ALIAS_TO_CW_M26",
        severity="warning",
        message=(
            f'{fullstring}: 本專案的UB1清單碼依中威M-26解析為'
            f'{row["type"]}；並非益高UB1。rod名義幾何可計，'
            "四只螺帽已列理論估重；材料grade、螺紋class／runout、"
            "製造切斷餘量與供應商螺帽成品重仍須補齊後才可正式加工"
        ),
        scope="source_designation_alias",
        calculation_allowed=True,
        bom_allowed=False,
        fabrication_allowed=False,
        source=config["drawing"],
    )

    assembly = {
        "project_alias": fullstring,
        "resolved_designation": row["type"],
        "line_size_in": size,
        "rod_size_a": row["rod_size_a"],
        "B_mm": row["B_centerline_mm"],
        "C_mm": row["C_overall_mm"],
        "D_mm": row["D_thread_length_mm"],
        "E_mm": row["E_leg_to_bend_center_mm"],
        "rod_developed_length_mm": row["rod_developed_length_mm"],
        "finished_hex_nuts": row["finished_hex_nuts_per_set"],
    }
    result.meta["fabrication"] = {
        "source_profile": "cw_e25_24_hp6",
        "source_drawing": config["drawing"],
        "source_file": config["source_file"],
        "source_revision": config["revision"],
        "branch": "M-26-PROJECT-ALIAS",
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": list(blockers),
        "assembly_dimensions": assembly,
    }
    result.meta["config_version"] = str(config.get("version") or "?")
    result.meta["config_updated"] = str(config.get("data_updated_at") or "")
    result.warnings.extend(
        blocker for blocker in blockers if blocker not in result.warnings
    )
    result.evidence.append(
        make_evidence(
            "m26_project_alias",
            assembly,
            "user_confirmed_alias_plus_visual_transcription",
            source=f"{config['drawing']} / {config['source_file']}",
            confidence=0.98,
            note="本專案UB1清單碼由使用者確認隸屬中威M-26",
        )
    )
    apply_truth_contract(
        result,
        type_id="M-26",
        review_reasons=list(result.warnings),
    )
    return result
