"""
pipe_shoe_engine.py
-------------------
Declarative driver for the Pipe Shoe family (types 52/53/54/55/66/67).
Reads python_app/configs/pipe_shoe_spec.json and produces an AnalysisResult.

Spec grammar:
  sizing.<key>_by_size  : list of {lte|lt|else, v} range rules -> scalar value
  components[*].when    : expression string evaluated by _eval_cond
  components[*].*_expr  : Python-like expression string evaluated by _eval_expr
"""

from __future__ import annotations

import json
import os
from math import pi
from typing import Any

from core.models import AnalysisResult, set_remark
from core.clamp_gasket import (
    add_m4_pipe_clamp_entry,
    add_m47_gasket_entry,
)
from core.parser import get_part, get_lookup_value, count_char
from core.plate import add_plate_entry
from core.steel import add_steel_section_entry
from core.source_profiles import (
    DEFAULT_SOURCE_PROFILE,
    normalize_source_profile,
)
from data.pipe_table import get_pipe_details

# ── Spec loader ---------------------------------------------------------------

_SPEC_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "configs", "pipe_shoe_spec.json"
)
_FABRICATION_SPEC_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "configs", "type_66_fabrication.json"
)

_SPEC = None
_FABRICATION_SPEC = None

SEMI_ARCHIVED_TYPE_IDS: frozenset = frozenset({"54", "55", "67"})
SEMI_ARCHIVED_WARNING = (
    "Type {type_id} 為 clamp/gasket 系列，已暫定半封存/未完工建檔；"
    "目前僅開放已逐圖核定的 D-81 至 14 吋範圍；"
    "M-4 重量、M-47 厚度及 16 吋以上 D-81/D-81A 仍需後續補齊"
)


def get_spec() -> dict:
    global _SPEC
    if _SPEC is None:
        path = os.path.normpath(_SPEC_PATH)
        with open(path, encoding="utf-8") as f:
            _SPEC = json.load(f)
    return _SPEC


def get_fabrication_spec() -> dict:
    global _FABRICATION_SPEC
    if _FABRICATION_SPEC is None:
        path = os.path.normpath(_FABRICATION_SPEC_PATH)
        with open(path, encoding="utf-8") as f:
            _FABRICATION_SPEC = json.load(f)
    return _FABRICATION_SPEC


# ── Range-table helpers -------------------------------------------------------

def _lookup_range(rules: list, pipe_size: float) -> Any:
    for rule in rules:
        if "lte" in rule and pipe_size <= rule["lte"]:
            return rule["v"]
        if "lt" in rule and pipe_size < rule["lt"]:
            return rule["v"]
        if "else" in rule:
            return rule["v"]
    raise ValueError(f"No matching range rule for pipe_size={pipe_size}")


def _profile_spec(spec: dict, source_profile: str | None) -> dict:
    profile_id = normalize_source_profile(
        source_profile or DEFAULT_SOURCE_PROFILE
    )
    profile = spec.get("source_profiles", {}).get(profile_id)
    if profile is None:
        raise ValueError(
            f"Pipe shoe source profile {profile_id!r} 尚未建立 D-80 規則"
        )
    return {"id": profile_id, **profile}


def _lookup_group(groups: list[dict], pipe_size: float) -> dict:
    for group in groups:
        if "lte" in group and pipe_size <= group["lte"]:
            return group
        if "lt" in group and pipe_size < group["lt"]:
            return group
        if group.get("else"):
            return group
    raise ValueError(
        f"No matching source-profile group for pipe_size={pipe_size}"
    )


def _resolve_sizing(
    spec: dict,
    pipe_size: float,
    pipe_details: dict,
    source_profile: str | None = None,
) -> dict:
    profile = _profile_spec(spec, source_profile)
    sizing = profile.get("sizing", spec["sizing"])
    ctx = {}
    ctx["A"] = _lookup_range(sizing["A_by_size"], pipe_size)
    ctx["B"] = _lookup_range(sizing["B_by_size"], pipe_size)
    ctx["C"] = _lookup_range(sizing["C_by_size"], pipe_size)
    ctx["D"] = _lookup_range(sizing["D_by_size"], pipe_size)
    ctx["E"] = _lookup_range(sizing["E_by_size"], pipe_size)
    ctx["source_profile"] = profile["id"]
    ctx["small_group_max"] = float(profile["small_group_max"])
    ctx["gusset_min"] = float(profile["gusset_min"])

    # pad thickness: sch10s_wall for <=8", fixed mm for larger
    pad_t_rules = sizing["pad_t_fallback_by_size"]
    matched = None
    for rule in pad_t_rules:
        if "lte" in rule and pipe_size <= rule["lte"]:
            matched = rule
            break
        if "lt" in rule and pipe_size < rule["lt"]:
            matched = rule
            break
        if "else" in rule:
            matched = rule
            break

    if matched is None:
        ctx["pad_t"] = 6
    elif matched.get("rule") == "sch10s_wall":
        ctx["pad_t"] = pipe_details["thickness_mm"]
    else:
        ctx["pad_t"] = matched["v"]

    # C_t: flange/web thickness of structural member
    c_spec = ctx["C"]
    if c_spec == "FB12":
        ctx["C_t"] = 12.0
    else:
        try:
            ctx["C_t"] = float(c_spec.split("*")[-1])
        except (TypeError, ValueError):
            ctx["C_t"] = 0.0

    return ctx


# ── Expression evaluator ------------------------------------------------------

def _make_eval_ns(ctx: dict, pipe_size: float, hops: int, lops: int,
                  type_id: str,
                  pipe_details: dict) -> dict:
    return {
        "type_id": type_id,
        "pipe_size": pipe_size,
        "HOPS": hops,
        "LOPS": lops,
        "OD": pipe_details["od_mm"],
        "pi": pi,
        "A": ctx["A"],
        "B": ctx["B"],
        "C": ctx["C"],
        "D": ctx["D"],
        "E": ctx["E"],
        "C_t": ctx["C_t"],
        "pad_t": ctx["pad_t"],
        "small_group_max": ctx["small_group_max"],
        "gusset_min": ctx["gusset_min"],
    }


def _eval_expr(expr, ns: dict) -> float:
    if isinstance(expr, (int, float)):
        return float(expr)
    return float(eval(str(expr), {"__builtins__": {}}, ns))


def _eval_cond(when: str, ns: dict, angle_wedge: bool,
               pad_symbol: str, ctx: dict) -> bool:
    if when in ("always", ""):
        return True
    mapping = {
        "angle_wedge":       angle_wedge,
        "pad_symbol != N/A": pad_symbol != "N/A",
        "C != FB12":         ctx["C"] != "FB12",
        "C == FB12":         ctx["C"] == "FB12",
        "pipe_size >= 10":   ns["pipe_size"] >= 10,
    }
    if when in mapping:
        return mapping[when]
    condition_ns = {
        **ns,
        "angle_wedge": angle_wedge,
        "pad_symbol": pad_symbol,
    }
    return bool(eval(when, {"__builtins__": {}}, condition_ns))


# ── Parse helpers -------------------------------------------------------------

def _get_pipe_size_str(fullstring: str) -> str:
    before = get_part(fullstring, 2)
    return before.split("(")[0] if "(" in before else before


def _get_pad_symbol(fullstring: str) -> str:
    part2 = get_part(fullstring, 2)
    if "(" in part2:
        return part2[part2.index("(") + 1: part2.index(")")]
    return "N/A"


def _type66_materials(
    fullstring: str,
    source_profile: str | None,
) -> tuple[str, str, dict]:
    """Return shoe material, reinforcing-pad material, and source contract."""
    profile_id = normalize_source_profile(
        source_profile or DEFAULT_SOURCE_PROFILE
    )
    fabrication_profile = get_fabrication_spec()["profiles"].get(profile_id)
    if fabrication_profile is None:
        return "A36/SS400", "A36/SS400", {}
    _, symbol = _designation_symbols(fullstring)
    contract = fabrication_profile["table_b_symbols"].get(symbol, {})
    shoe_material = contract.get("shoe_material", "A36/SS400")
    if profile_id == "ctci_20e4588":
        pad_material = {
            "R": "A516-60",
            "S": "SUS304",
        }.get(symbol, "A36/SS400")
    else:
        pad_material = shoe_material
    return shoe_material, pad_material, contract


def _get_material(
    fullstring: str,
    source_profile: str | None = None,
) -> str:
    return _type66_materials(fullstring, source_profile)[0]


def _designation_symbols(fullstring: str) -> tuple[str, str]:
    """Return the visible table/insulation symbol and parenthesized material symbol."""
    part3 = str(get_part(fullstring, 3) or "").strip()
    if "(" not in part3 or ")" not in part3:
        return part3, ""
    return (
        part3.split("(", 1)[0].strip(),
        part3.split("(", 1)[1].split(")", 1)[0].strip(),
    )


def _type66_fabrication_context(
    fullstring: str,
    *,
    source_profile: str | None,
) -> dict:
    """Source-backed geometry contract for future Type 66 shop drawings."""
    spec = get_spec()
    fab_spec = get_fabrication_spec()
    profile = _profile_spec(spec, source_profile)
    profile_id = profile["id"]
    fabrication_profile = fab_spec["profiles"].get(profile_id)
    if fabrication_profile is None:
        raise ValueError(
            f"Type 66 / {profile_id} 尚未建立加工圖參數契約"
        )

    pipe_size_str = _get_pipe_size_str(fullstring)
    pipe_size = get_lookup_value(pipe_size_str.replace("B", ""))
    table_symbol, material_symbol = _designation_symbols(fullstring)
    result = {
        "contract_version": fab_spec["_version"],
        "source_profile": profile_id,
        "drawing_standard": fabrication_profile["drawing_standard"],
        "drawing_revision": fabrication_profile["revision"],
        "pipe_size_in": pipe_size,
        "table_symbol": table_symbol,
        "material_symbol": material_symbol,
        "fabrication_ready": False,
        "blockers": [],
        "dimensions": {},
        "component_contract_status": "",
    }

    if pipe_size <= 24:
        result["branch"] = "D-80"
        result["source_drawing"] = fabrication_profile["drawings"]["d80"]
        ready_lte = float(fabrication_profile["d80_fabrication_ready_lte"])
        if pipe_size <= ready_lte:
            result["fabrication_ready"] = True
            result["component_contract_status"] = "shop_drawing_parameters_ready"
        else:
            key = "10_14" if pipe_size <= 14 else "16_24"
            # 22A enters the reinforced branch from 6 inches.
            if profile_id == "ctci_22a_5123a" and pipe_size <= 14:
                key = "6_14"
            result["blockers"] = list(
                fabrication_profile["d80_blockers"].get(key, [])
            )
            result["component_contract_status"] = (
                "calculation_only_geometry_not_shop_drawing_ready"
            )
        return result

    branch_key = "d80c" if "d80c" in fabrication_profile and pipe_size >= 44 else "d80b"
    branch = fabrication_profile.get(branch_key)
    result["branch"] = branch_key.upper().replace("D80", "D-80")
    result["source_drawing"] = fabrication_profile["drawings"].get(branch_key, "")
    if branch is None:
        result["blockers"] = [
            f"{profile_id} supplied drawing set does not cover Type 66 {pipe_size:g} inch"
        ]
        result["component_contract_status"] = "unsupported_size"
        return result

    dimensions = branch["dimensions"].get(f"{pipe_size:g}")
    if dimensions is None:
        result["blockers"] = [
            f"{result['branch']} table has no row for {pipe_size:g} inch"
        ]
        result["component_contract_status"] = "unsupported_table_row"
        return result
    result["dimensions"] = {
        **branch.get("constants", {}),
        **dimensions,
    }
    result["insulation_types"] = list(branch["insulation_types"])
    result["blockers"] = list(branch.get("blockers", []))
    result["component_contract_status"] = branch["component_contract_status"]
    return result


def get_fabrication_context(
    fullstring: str,
    type_id: str,
    source_profile: str | None = None,
) -> dict | None:
    """Public CAD/shop-drawing contract API for drawing-backed Type families."""
    if str(type_id) != "66":
        return None
    return _type66_fabrication_context(
        fullstring,
        source_profile=source_profile,
    )


def _parse_hops_lops(fullstring: str, pipe_size: float,
                     default_lops: int) -> tuple:
    hops_default = 150
    part3 = get_part(fullstring, 3)
    part4 = get_part(fullstring, 4)
    part5 = get_part(fullstring, 5)

    def _int(v):
        return bool(v and str(v).strip().isdigit())

    try:
        # Explicit designation dimensions override D-80 table/default values.
        if _int(part4) and _int(part5):
            return int(part4), int(part5)
        if _int(part3) and _int(part4):
            return int(part3), int(part4)
        if _int(part4):
            return hops_default, int(part4)
    except (TypeError, ValueError):
        pass
    return hops_default, default_lops


def _add_type52_retainer(
    result: AnalysisResult,
    *,
    profile: dict,
    pipe_size: float,
    material: str,
) -> None:
    """Add only the D-63 retainer pieces that are dimensioned on the source."""
    group = _lookup_group(profile["type52_retainer_groups"], pipe_size)
    for component in group.get("components", []):
        kind = component["kind"]
        quantity = int(component.get("qty", 1))
        if kind == "angle":
            add_steel_section_entry(
                result,
                "Angle",
                component["spec"],
                component["length"],
                quantity,
                material,
            )
            field_cut_zh = "；現場裁切" if component.get("cut_in_field") else ""
            field_cut_en = "; CUT IN FIELD" if component.get("cut_in_field") else ""
            set_remark(
                result.entries[-1],
                "Type 52 D-63 側擋角鋼；圖示為雙側 TYP."
                f"{field_cut_zh}；長度依圖面共同 150 mm（NOTE 2）",
                "TYPE-52 D-63 bilateral retainer angle"
                f"{field_cut_en}; L=150 mm per common NOTE 2",
            )
        elif kind == "plate":
            add_plate_entry(
                result,
                component["length"],
                component["width"],
                component["thickness"],
                component["name"],
                material,
                plate_qty=quantity,
                plate_role="stopper_plate",
                notes_zh=(
                    "Type 52 D-63 側擋板；數量依剖面雙側 TYP. 解讀，"
                    "需在製造前再由工程師確認"
                ),
            )
        else:
            raise ValueError(f"Unknown Type 52 retainer kind: {kind!r}")

    for callout in group.get("unresolved_callouts", []):
        result.warnings.append(callout)


def _add_type53_guide(
    result: AnalysisResult,
    *,
    profile: dict,
    pipe_size: float,
    material: str,
) -> None:
    """Add the dimensioned D-64 guide pieces for the selected source."""
    max_size = float(profile["type53_max_hardened_size"])
    if pipe_size > max_size:
        raise ValueError(
            f"Type 53 / {profile['id']} 在 {max_size:g} 吋以上的 guide "
            "雖有型鋼規格與數量，但圖面未給可信下料長度；為避免虛構重量，本筆暫不計算"
        )

    group = _lookup_group(profile["type53_guide_groups"], pipe_size)
    for component in group.get("components", []):
        kind = component["kind"]
        quantity = int(component.get("qty", 1))
        if kind == "angle":
            add_steel_section_entry(
                result,
                "Angle",
                component["spec"],
                component["length"],
                quantity,
                material,
            )
            set_remark(
                result.entries[-1],
                "Type 53 D-64 雙側 guide 角鋼；長度依 24 吋以下圖面 NOTE 2 採 150 mm",
                "TYPE-53 D-64 bilateral guide angle; L=150 mm per NOTE 2",
            )
            continue

        if kind not in {"plate", "triangle_plate"}:
            raise ValueError(f"Unknown Type 53 guide kind: {kind!r}")
        is_triangle = kind == "triangle_plate"
        length = float(component["length"])
        width = float(component["width"])
        net_area = length * width / 2 if is_triangle else 0
        add_plate_entry(
            result,
            length,
            width,
            component["thickness"],
            component["name"],
            material,
            plate_qty=quantity,
            plate_role="stopper_plate",
            shape_spec=(
                f"TRI {length:g}x{width:g}x{component['thickness']:g}t"
                if is_triangle
                else ""
            ),
            shape_kind="triangle" if is_triangle else "",
            gross_area_mm2=length * width,
            net_area_mm2=net_area,
            notes_zh=(
                "Type 53 D-64 guide 補強三角板，淨面積按直角三角形 1/2×L×W"
                if is_triangle
                else "Type 53 D-64 雙側 guide 板"
            ),
        )


def _calculate_d81(
    fullstring: str,
    *,
    type_id: str,
    source_profile: str | None,
) -> AnalysisResult:
    """Drawing-backed D-81 core for Type 67 and the Type 54 / D-65 variant."""
    spec = get_spec()
    profile = _profile_spec(spec, source_profile)
    if "d81_default_lops_by_size" not in profile:
        raise ValueError(
            f"Type {type_id} / {profile['id']} 沒有供應 D-81 基準圖，暫不計算"
        )

    result = AnalysisResult(fullstring=fullstring)
    result.warnings.append(SEMI_ARCHIVED_WARNING.format(type_id=type_id))

    pipe_size_str = _get_pipe_size_str(fullstring)
    pipe_size = get_lookup_value(pipe_size_str.replace("B", ""))
    pad_symbol = _get_pad_symbol(fullstring)
    if pad_symbol != "N/A":
        result.warnings.append(
            f"Type {type_id} 為 D-81 clamp + gasket 系列，不接受 (P)；已忽略 pad 標記"
        )
    max_size = float(profile["d81_max_hardened_size"])
    if pipe_size > max_size:
        raise ValueError(
            f"Type {type_id} / {profile['id']} 目前只完成 D-81 至 {max_size:g} 吋；"
            "16–24 吋 fabricated 12t 與 26 吋以上 D-81A 尚未核定"
        )

    pipe_details = get_pipe_details(pipe_size, "10S")
    ctx = _resolve_sizing(
        spec,
        pipe_size,
        pipe_details,
        source_profile=profile["id"],
    )
    default_lops = _lookup_range(
        profile["d81_default_lops_by_size"],
        pipe_size,
    )
    hops, lops = _parse_hops_lops(
        fullstring,
        pipe_size,
        default_lops,
    )
    material = "A36/SS400"

    if type_id == "54":
        _add_type54_retainer(
            result,
            profile=profile,
            pipe_size=pipe_size,
            material=material,
        )
    elif type_id == "55":
        _add_type55_guide(
            result,
            profile=profile,
            pipe_size=pipe_size,
            material=material,
        )

    add_m4_pipe_clamp_entry(result, pipe_size)
    add_m47_gasket_entry(result, pipe_size)

    c_spec = ctx["C"]
    if c_spec == "FB12":
        raise ValueError(
            "Type 67 D-81 fabricated 12t member 尚未核定，不可沿用 D-80 板件 recipe"
        )
    add_steel_section_entry(
        result,
        "H Beam",
        c_spec,
        lops,
        1,
        material,
    )
    set_remark(
        result.entries[-1],
        (
            f"Type {type_id} D-81 MEMBER C；A={ctx['A']}，B={ctx['B']}，"
            f"HOPS={hops}，LOPS={lops}；由 H{c_spec} 裁切"
        ),
        (
            f"TYPE-{type_id} D-81 MEMBER C; A={ctx['A']}; B={ctx['B']}; "
            f"HOPS={hops}; LOPS={lops}; CUT FROM H{c_spec}"
        ),
    )
    result.warnings.append(
        f"Type {type_id} D-81 的 clamp/gasket 已接 M-4/M-47；"
        "M-4 重量與 M-47 厚度仍含集中估算"
    )
    return result


def _add_type54_retainer(
    result: AnalysisResult,
    *,
    profile: dict,
    pipe_size: float,
    material: str,
) -> None:
    """Add source-specific D-65 side retainers on top of the D-81 core."""
    groups = profile.get("type54_retainer_groups")
    if not groups:
        raise ValueError(
            f"Type 54 / {profile['id']} 沒有供應 D-65 基準圖，暫不計算"
        )
    group = _lookup_group(groups, pipe_size)
    for component in group.get("components", []):
        quantity = int(component.get("qty", 1))
        if component["kind"] == "angle":
            add_steel_section_entry(
                result,
                "Angle",
                component["spec"],
                component["length"],
                quantity,
                material,
            )
            set_remark(
                result.entries[-1],
                "Type 54 D-65 雙側止擋角鋼；現場裁切；長度依圖面 NOTE 2 / 側視圖採 150 mm",
                "TYPE-54 D-65 bilateral retainer angle; CUT IN FIELD; L=150 mm",
            )
            continue
        if component["kind"] != "plate":
            raise ValueError(
                f"Unknown Type 54 retainer kind: {component['kind']!r}"
            )
        add_plate_entry(
            result,
            component["length"],
            component["width"],
            component["thickness"],
            component["name"],
            material,
            plate_qty=quantity,
            plate_role="stopper_plate",
            notes_zh=(
                "Type 54 D-65 大管徑止擋底板；150 mm 長度依側視圖與 NOTE 2，"
                "雙側數量依 TYP. 解讀"
            ),
        )


def _add_type55_guide(
    result: AnalysisResult,
    *,
    profile: dict,
    pipe_size: float,
    material: str,
) -> None:
    """Add D-66 guide angles; keep unresolved shaped pieces warning-only."""
    groups = profile.get("type55_guide_groups")
    if not groups:
        raise ValueError(
            f"Type 55 / {profile['id']} 沒有供應 D-66 基準圖，暫不計算"
        )
    group = _lookup_group(groups, pipe_size)
    for component in group.get("components", []):
        if component["kind"] != "angle":
            raise ValueError(
                f"Unknown Type 55 guide kind: {component['kind']!r}"
            )
        add_steel_section_entry(
            result,
            "Angle",
            component["spec"],
            component["length"],
            int(component.get("qty", 1)),
            material,
        )
        set_remark(
            result.entries[-1],
            "Type 55 D-66 雙側導向角鋼；長度依圖面 NOTE 2 / 側視圖採 150 mm",
            "TYPE-55 D-66 bilateral guide angle; L=150 mm",
        )
    result.warnings.extend(group.get("unresolved_callouts", []))


# ── Main entry point ----------------------------------------------------------

def calculate(
    fullstring: str,
    type_id: str,
    source_profile: str | None = None,
) -> AnalysisResult:
    if type_id == "85":
        raise ValueError(
            "Type 85 D-105/D-106 雖引用 D-80/D-80B，但另含保溫鞍座與 "
            "A/B/C insulation class；三套來源的分段與適用上限不同，"
            "專屬構件尺寸尚未核定，不可沿用 Type 52 recipe"
        )
    if type_id in {"54", "55", "67"}:
        return _calculate_d81(
            fullstring,
            type_id=type_id,
            source_profile=source_profile,
        )

    spec = get_spec()
    result = AnalysisResult(fullstring=fullstring)
    if type_id in SEMI_ARCHIVED_TYPE_IDS:
        result.warnings.append(SEMI_ARCHIVED_WARNING.format(type_id=type_id))

    variant = spec["variants"][type_id]
    angle_wedge = variant["angle_wedge"]

    pipe_size_str = _get_pipe_size_str(fullstring)
    pipe_size = get_lookup_value(pipe_size_str.replace("B", ""))
    fabrication_context = None
    if type_id == "66":
        fabrication_context = _type66_fabrication_context(
            fullstring,
            source_profile=source_profile,
        )
        result.meta["fabrication"] = fabrication_context
        if not fabrication_context["fabrication_ready"]:
            blockers = "；".join(fabrication_context["blockers"])
            result.error = (
                f"Type 66 / {fabrication_context['source_profile']} / "
                f"{fabrication_context['branch']} 尚未達可出加工圖程度：{blockers}"
            )
            return result
    pad_symbol = _get_pad_symbol(fullstring)
    if type_id in {"54", "55"} and pad_symbol != "N/A":
        result.warnings.append(
            f"Type {type_id} 為 D-81 clamp + gasket 系列，不接受 (P)；已忽略 pad 標記"
        )
        pad_symbol = "N/A"
    material = "A36/SS400"
    pad_material = material
    if count_char(fullstring, "-") >= 2:
        material, pad_material, _ = _type66_materials(
            fullstring,
            source_profile,
        )

    pipe_details = get_pipe_details(pipe_size, "10S")
    ctx = _resolve_sizing(
        spec, pipe_size, pipe_details, source_profile=source_profile
    )
    profile = _profile_spec(spec, ctx["source_profile"])
    if pipe_size >= 26:
        result.warnings.append(
            "Pipe shoe D-80B 26\"~50\" branch not fully hardened; current shared spec is provisional"
        )
    default_lops = ctx["D"]
    hops, lops = _parse_hops_lops(fullstring, pipe_size, default_lops)
    ns = _make_eval_ns(ctx, pipe_size, hops, lops, type_id, pipe_details)

    # E 值最低限制：2" 以下管徑 E 規格表原為 0，修正為 25mm
    if pipe_size < 2 and ctx["E"] == 25:
        result.warnings.append(
            f"{pipe_size}" + '" 管徑 E 值依規格表應為 0，已修正為 25 mm（最低限值），請工程師確認'
        )

    for comp in spec["components"]:
        if not _eval_cond(comp["when"], ns, angle_wedge, pad_symbol, ctx):
            continue

        name = comp["name"]
        qty = int(_eval_expr(comp.get("qty", 1), ns))

        if comp["id"] == "pad":
            pad_t = ctx["pad_t"]
            pad_len = round(_eval_expr(comp["length_expr"], ns))
            pad_w = round(_eval_expr(comp["width_expr"], ns))
            length_rule = (
                "LOPS + E*2"
                if pipe_size <= ctx["small_group_max"]
                else "LOPS + E*2 + 25*2"
            )
            result.warnings.append(
                "Pipe shoe pad width uses OD*pi/3 as practical calculation value"
            )
            add_plate_entry(result, pad_len, pad_w, pad_t, name, pad_material,
                            plate_role="reinforcement_pad")
            _en = ("120deg pad; width=OD*pi/3; length_rule=" + length_rule + "; "
                   "t=SCH10S(" + str(pad_t) + "mm); HOPS=" + str(hops))
            set_remark(
                result.entries[-1],
                f"120°弧形墊板；寬=OD×π/3；長度規則={length_rule}；板厚=SCH10S({pad_t}mm)；HOPS={hops}",
                _en,
            )

        elif comp["id"] == "wedge":
            if type_id == "52":
                _add_type52_retainer(
                    result,
                    profile=profile,
                    pipe_size=pipe_size,
                    material=material,
                )
            elif type_id == "53":
                _add_type53_guide(
                    result,
                    profile=profile,
                    pipe_size=pipe_size,
                    material=material,
                )
            else:
                length = int(_eval_expr(comp["length"], ns))
                add_steel_section_entry(result, "Angle",
                                        comp["spec"], length, qty, material)
                result.entries[-1].remark = comp.get("remark", "")

        elif comp["id"] == "beam":
            c_spec = ctx["C"]
            beam_l = round(_eval_expr(comp["length_expr"], ns))
            add_steel_section_entry(result, "H Beam", c_spec,
                                    beam_l, 1, material)
            member_width = c_spec.split("*")[1] if "*" in c_spec else str(ctx["A"])
            length_rule = (
                "LOPS/D"
                if pipe_size <= ctx["small_group_max"]
                else "LOPS+25*2"
            )
            _en = ("MEMBER C, CUT FROM H" + c_spec + "; width=" + str(member_width) + "; "
                   "L=" + length_rule + "; H=HOPS(" + str(hops) + "); "
                   "[deep logic] 1 purchased H-beam split in half = 2 supports")
            set_remark(
                result.entries[-1],
                f"C構件，由H{c_spec}裁切；羼寬={member_width}；長度規則={length_rule}；H=HOPS({hops})；"
                f"《購買逻輯》1支 H型鵋對分 = 2 組支撐",
                _en,
            )

        elif comp["id"] in ("fab_bottom", "fab_web"):
            t = int(comp["thickness"])
            if "width_expr" in comp:
                w = round(_eval_expr(comp["width_expr"], ns))
            else:
                w = int(comp["width"])
            beam_l = round(_eval_expr(comp["length_expr"], ns))
            add_plate_entry(result, w, beam_l, t, name, material)
            tmpl = comp.get("remark_template", "")
            remark = tmpl.replace("{A+70}", str(w)).replace("{LOPS+50}", str(beam_l))
            result.entries[-1].remark = remark

        elif comp["id"] in ("gusset", "type54_stopper"):
            if "thickness_ref" in comp:
                d_t = ctx[comp["thickness_ref"]]
            else:
                d_t = _eval_expr(comp["thickness"], ns)
            if "width_expr" in comp:
                d_b = _eval_expr(comp["width_expr"], ns)
            else:
                d_b = _eval_expr(comp["width"], ns)
            if "length_expr" in comp:
                d_l = round(_eval_expr(comp["length_expr"], ns))
            else:
                d_l = round(_eval_expr(comp["length"], ns))
            add_plate_entry(result, d_l, d_b, d_t, name,
                            plate_qty=qty,
                            plate_role=comp.get("role", "generic_plate"))
            result.entries[-1].remark = comp.get("remark", "")

    if fabrication_context is not None:
        fabrication_profile = get_fabrication_spec()["profiles"][
            fabrication_context["source_profile"]
        ]
        weld_rule = next(
            (
                rule["rule"]
                for rule in fabrication_profile["weld_rules"]
                if pipe_size <= float(rule["lte"])
            ),
            "",
        )
        full_section_spec = {
            "200*100*5.5": "H200*100*5.5*8",
            "200*200*8": "H200*200*8*12",
        }.get(ctx["C"], ctx["C"])
        fabrication_context["dimensions"].update(
            {
                "A_mm": ctx["A"],
                "B_mm": ctx["B"],
                "E_mm": ctx["E"],
                "HOPS_mm": hops,
                "LOPS_mm": lops,
                "OD_mm": pipe_details["od_mm"],
                "saddle_angle_deg": 120,
                "minimum_clearance_mm": 25,
                "member_c_full_spec": full_section_spec,
            }
        )
        fabrication_context["weld_rule"] = weld_rule
        fabrication_context["special_fabrication"] = list(
            fabrication_profile.get("special_fabrication", [])
        )
        material_symbol = fabrication_context["material_symbol"]
        fabrication_context["material_contract"] = (
            fabrication_profile["table_b_symbols"].get(material_symbol)
            or {
                "unresolved_symbol": material_symbol,
            }
        )

        for entry in result.entries:
            entry.geometry.source_drawing = fabrication_context["source_drawing"]
            entry.geometry.source_revision = fabrication_context["drawing_revision"]
            entry.geometry.fabrication_ready = True
            if entry.name == "H型鋼":
                entry.geometry.component_id = "D80-MEMBER-C"
                entry.geometry.shape_kind = "pipe_shoe_h_section_cut"
                entry.geometry.shape_spec = (
                    f"CUT FROM {full_section_spec}; L={entry.length:g}; "
                    f"HOPS={hops:g}; PIPE OD={pipe_details['od_mm']:g}; "
                    "SADDLE=120deg"
                )
                entry.geometry.formula = (
                    "section per D-80 table C; cut length=LOPS/D"
                )
                entry.geometry.parameters = {
                    "raw_section": full_section_spec,
                    "cut_length_mm": entry.length,
                    "hops_mm": hops,
                    "pipe_od_mm": pipe_details["od_mm"],
                    "saddle_angle_deg": 120,
                    "weld_rule": weld_rule,
                }
            elif entry.role == "reinforcement_pad":
                entry.geometry.component_id = "D80-REINFORCING-PAD"
                entry.geometry.shape_kind = "rolled_arc_plate"
                entry.geometry.shape_spec = (
                    f"DEVELOPED {entry.length:g}x{entry.width:g}x{entry.spec}t; "
                    "ROLL 120deg; WEEP HOLE DIA6"
                )
                entry.geometry.formula = (
                    "developed width=OD*pi/3; length per source D-80 E/LOPS rule"
                )
                entry.geometry.parameters = {
                    "developed_length_mm": entry.length,
                    "developed_width_mm": entry.width,
                    "thickness_mm": float(entry.spec),
                    "roll_angle_deg": 120,
                    "weep_hole_diameter_mm": 6,
                    "pipe_od_mm": pipe_details["od_mm"],
                }

    return result


# ── Public context API (for Inventor parameter export) -----------------------

#: Pipe Shoe type ids supported by this engine
PIPE_SHOE_TYPE_IDS: frozenset = frozenset({"52", "53", "54", "55", "66", "67", "85"})


def get_sizing_context(
    fullstring: str,
    type_id: str,
    source_profile: str | None = None,
) -> "dict | None":
    """回傳 Pipe Shoe 計算用的尺寸字典，供 Inventor 參數匯出使用。
    若 type_id 不屬於 Pipe Shoe 家族則回傳 None。
    """
    spec = get_spec()
    if type_id not in spec.get("variants", {}):
        return None

    pipe_size_str = _get_pipe_size_str(fullstring)
    pipe_size = get_lookup_value(pipe_size_str.replace("B", ""))
    pipe_details = get_pipe_details(pipe_size, "10S")
    ctx = _resolve_sizing(
        spec, pipe_size, pipe_details, source_profile=source_profile
    )
    default_lops = ctx["D"]
    hops, lops = _parse_hops_lops(fullstring, pipe_size, default_lops)

    c_spec = ctx["C"]
    c_parts = c_spec.split("*") if "*" in c_spec else []

    def _safe_int(lst, i):
        try:
            return int(lst[i])
        except (IndexError, ValueError):
            return 0

    def _safe_float(lst, i):
        try:
            return float(lst[i])
        except (IndexError, ValueError):
            return 0.0

    return {
        "designation":   fullstring,
        "type_id":       type_id,
        "source_profile": ctx["source_profile"],
        "pipe_size_in":  pipe_size,
        "pipe_size_str": pipe_size_str,
        "OD_mm":         pipe_details["od_mm"],
        "wall_mm":       pipe_details["thickness_mm"],
        "HOPS_mm":       hops,
        "LOPS_mm":       lops,
        "E_mm":          ctx["E"],
        "A_mm":          ctx["A"],
        "B_mm":          ctx["B"],
        "D_mm":          ctx["D"],
        "pad_t_mm":      ctx["pad_t"],
        "C_spec":        c_spec,
        "is_fabricated": c_spec == "FB12",
        "C_H_mm":        _safe_int(c_parts, 0) if c_spec != "FB12" else 0,
        "C_B_mm":        _safe_int(c_parts, 1) if c_spec != "FB12" else 0,
        "C_t_mm":        _safe_float(c_parts, -1) if c_spec != "FB12" else 12.0,
    }
