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

from core.models import AnalysisResult
from core.parser import get_part, get_lookup_value, count_char
from core.plate import add_plate_entry
from core.steel import add_steel_section_entry
from data.pipe_table import get_pipe_details

# ── Spec loader ---------------------------------------------------------------

_SPEC_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "configs", "pipe_shoe_spec.json"
)

_SPEC = None


def get_spec() -> dict:
    global _SPEC
    if _SPEC is None:
        path = os.path.normpath(_SPEC_PATH)
        with open(path, encoding="utf-8") as f:
            _SPEC = json.load(f)
    return _SPEC


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


def _resolve_sizing(spec: dict, pipe_size: float, pipe_details: dict) -> dict:
    sizing = spec["sizing"]
    ctx = {}
    ctx["A"] = _lookup_range(sizing["A_by_size"], pipe_size)
    ctx["B"] = _lookup_range(sizing["B_by_size"], pipe_size)
    ctx["C"] = _lookup_range(sizing["C_by_size"], pipe_size)
    ctx["D"] = _lookup_range(sizing["D_by_size"], pipe_size)
    ctx["E"] = _lookup_range(sizing["E_by_size"], pipe_size)

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
                  pipe_details: dict) -> dict:
    return {
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
    return bool(eval(when, {"__builtins__": {}}, ns))


# ── Parse helpers -------------------------------------------------------------

def _get_pipe_size_str(fullstring: str) -> str:
    before = get_part(fullstring, 2)
    return before.split("(")[0] if "(" in before else before


def _get_pad_symbol(fullstring: str) -> str:
    part2 = get_part(fullstring, 2)
    if "(" in part2:
        return part2[part2.index("(") + 1: part2.index(")")]
    return "N/A"


def _get_material(fullstring: str) -> str:
    part3 = get_part(fullstring, 3)
    if not part3 or not part3.startswith("("):
        return "A36/SS400"
    return {"A": "A36/SS400", "S": "SUS304", "AS": "AS"}.get(
        part3.strip("()"), "A36/SS400"
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
        if _int(part4) and _int(part5):
            return int(part4), int(part5)
        if _int(part3) and _int(part4):
            return int(part3), int(part4)
        if _int(part4):
            return hops_default, int(part4)
    except (TypeError, ValueError):
        pass
    return hops_default, default_lops


# ── Main entry point ----------------------------------------------------------

def calculate(fullstring: str, type_id: str) -> AnalysisResult:
    spec = get_spec()
    result = AnalysisResult(fullstring=fullstring)

    variant = spec["variants"][type_id]
    angle_wedge = variant["angle_wedge"]

    pipe_size_str = _get_pipe_size_str(fullstring)
    pipe_size = get_lookup_value(pipe_size_str.replace("B", ""))
    pad_symbol = _get_pad_symbol(fullstring)
    material = "A36/SS400"
    if count_char(fullstring, "-") >= 2:
        material = _get_material(fullstring)

    pipe_details = get_pipe_details(pipe_size, "10S")
    ctx = _resolve_sizing(spec, pipe_size, pipe_details)
    if pipe_size >= 26:
        result.warnings.append(
            "Pipe shoe D-80B 26\"~50\" branch not fully hardened; current shared spec is provisional"
        )
    default_lops = ctx["D"]
    hops, lops = _parse_hops_lops(fullstring, pipe_size, default_lops)
    ns = _make_eval_ns(ctx, pipe_size, hops, lops, pipe_details)

    for comp in spec["components"]:
        if not _eval_cond(comp["when"], ns, angle_wedge, pad_symbol, ctx):
            continue

        name = comp["name"]
        qty = int(_eval_expr(comp.get("qty", 1), ns))

        if comp["id"] == "pad":
            pad_t = ctx["pad_t"]
            pad_len = round(_eval_expr(comp["length_expr"], ns))
            pad_w = round(_eval_expr(comp["width_expr"], ns))
            length_rule = "LOPS + E*2" if pipe_size <= 8 else "LOPS + E*2 + 25*2"
            result.warnings.append(
                "Pipe shoe pad width uses OD*pi/3 as practical calculation value"
            )
            add_plate_entry(result, pad_len, pad_w, pad_t, name,
                            plate_role="reinforcement_pad")
            result.entries[-1].remark = (
                "120deg pad; width=OD*pi/3; length_rule=" + length_rule + "; "
                "t=SCH10S(" + str(pad_t) + "mm); HOPS=" + str(hops)
            )

        elif comp["id"] == "wedge":
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
            length_rule = "LOPS/D" if pipe_size <= 8 else "LOPS+25*2"
            result.entries[-1].remark = (
                "MEMBER C, CUT FROM H" + c_spec + "; width=" + str(member_width) + "; "
                "L=" + length_rule + "; H=HOPS(" + str(hops) + "); "
                "[deep logic] 1 purchased H-beam split in half = 2 supports"
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

        elif comp["id"] == "gusset":
            d_t = ctx["B"]
            d_b = _eval_expr(comp["width_expr"], ns)
            d_l = round(_eval_expr(comp["length_expr"], ns))
            add_plate_entry(result, d_l, d_b, d_t, name,
                            plate_qty=qty, plate_role="generic_plate")
            result.entries[-1].remark = comp.get("remark", "")

    return result
