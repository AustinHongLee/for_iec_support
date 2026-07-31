"""Chung Wei PO1/PO2/PO3 platform-opening rules for legacy OPEN codes."""

from __future__ import annotations

from math import pi
import re

from companies.eko.parser import parse_inch
from core.bolt import add_custom_entry
from core.component_roles import ComponentRole
from core.issues import add_issue
from core.models import AnalysisResult, set_remark
from core.penetration_hole import parse_insulation
from core.truth import apply_truth_contract, make_evidence
from data.pipe_table import get_pipe_od


def _parse_size(fullstring: str) -> float:
    match = re.fullmatch(r"\s*OPEN-(.+?)\s*", str(fullstring or ""), re.I)
    if not match:
        raise ValueError('OPEN格式應為 OPEN-□"')
    token = match.group(1).strip()
    if token.upper().endswith("B"):
        token = token[:-1]
    size = parse_inch(token)
    if size is None or size <= 0:
        raise ValueError(f"OPEN: 無法解析公稱管徑 {match.group(1)!r}")
    return float(size)


def _select_at_least(required: float, values: list[float]) -> float | None:
    return next((float(value) for value in values if value + 1e-9 >= required), None)


def _add_flat_bar(
    result: AnalysisResult,
    *,
    name: str,
    width_mm: float,
    thickness_mm: float,
    cut_length_mm: float,
    quantity: int,
    material: str,
    component_id: str,
    drawing: str,
    revision: str,
    shape_kind: str,
    parameters: dict,
    source_total_weight_kg: float | None = None,
) -> None:
    density = 7.85e-6
    weight_per_m = width_mm * thickness_mm * density * 1000
    calculated_piece_weight = (
        width_mm * thickness_mm * cut_length_mm * density
    )
    piece_weight = (
        float(source_total_weight_kg) / quantity
        if source_total_weight_kg is not None
        else calculated_piece_weight
    )
    spec = f"FB{width_mm:g}×{thickness_mm:g}"
    add_custom_entry(
        result,
        name,
        spec,
        material,
        quantity,
        piece_weight,
        unit="PC",
        category="型鋼類",
        role=ComponentRole.OPENING_REINFORCEMENT.value,
        item_class="fabricated_part",
        manufacturing_type="bend_and_weld" if "ring" in shape_kind else "raw_cut",
    )
    entry = result.entries[-1]
    entry.length = cut_length_mm
    entry.weight_per_unit = weight_per_m
    entry.unit_weight = piece_weight
    entry.total_weight = piece_weight * quantity
    entry.weight_output = entry.total_weight
    entry.length_subtotal = cut_length_mm / 1000 * quantity
    entry.part_key = (
        f"{component_id.lower().replace('-', '_')}"
        f"_w{width_mm:g}_t{thickness_mm:g}_l{cut_length_mm:.3f}"
    )
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = shape_kind
    entry.geometry.shape_spec = (
        f"{spec}; CUT L={cut_length_mm:.3f}; QTY={quantity}"
    )
    entry.geometry.parameters = {
        "width_mm": width_mm,
        "thickness_mm": thickness_mm,
        "cut_length_mm": cut_length_mm,
        "quantity": quantity,
        **parameters,
    }
    entry.geometry.fabrication_ready = True
    set_remark(entry, entry.geometry.shape_spec)


def calculate(
    fullstring: str,
    config: dict,
    overrides: dict | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        line_size = _parse_size(fullstring)
        pipe_od = float(get_pipe_od(line_size))
        insulation_mm, insulation_label = parse_insulation(
            overrides.get("insulation")
        )
    except (TypeError, ValueError) as exc:
        result.error = f"OPEN/PO輸入無效: {exc}"
        return result

    flange_od = overrides.get("flange_od_mm")
    if flange_od not in (None, ""):
        try:
            diameter_d = float(flange_od)
        except (TypeError, ValueError):
            result.error = "OPEN/PO: flange_od_mm必須為正數"
            return result
        if diameter_d <= 0:
            result.error = "OPEN/PO: flange_od_mm必須為正數"
            return result
        diameter_basis = "flange_od_mm"
    else:
        diameter_d = pipe_od + 2 * insulation_mm
        diameter_basis = "pipe_od + 2*insulation"

    clearance = float(config["clearance_each_side_mm"])
    required_l = diameter_d + 2 * clearance
    surface = str(overrides.get("opening_surface") or "grating").strip().lower()
    if surface in {"checker", "checker_plate", "checked_plate"}:
        branch = "PO3"
        rule = config["po3"]
        selected_l = _select_at_least(required_l, rule["L_values_mm"])
    else:
        po1 = config["po1"]
        po2 = config["po2"]
        selected_l = _select_at_least(required_l, po1["L_values_mm"])
        if selected_l is not None:
            branch = "PO1"
            rule = po1
        else:
            selected_l = _select_at_least(required_l, po2["L_values_mm"])
            branch = "PO2"
            rule = po2

    if selected_l is None:
        result.error = (
            f"OPEN/PO: D={diameter_d:g}mm加兩側25mm後需L≥{required_l:g}mm，"
            "超出PO系列L≤600mm範圍"
        )
        return result

    drawing = config["drawing"]
    revision = config["revision"]
    material = str(config["material"])
    thickness = float(rule["thickness_mm"])
    source_weight = float(rule["total_weight_kg"][f"{selected_l:g}"])
    if branch == "PO1":
        widths = [float(value) for value in rule["flat_bar_widths_mm"]]
        for width in widths:
            _add_flat_bar(
                result,
                name=f"PO1 開孔補強扁鐵 FB{width:g}",
                width_mm=width,
                thickness_mm=thickness,
                cut_length_mm=selected_l,
                quantity=2,
                material=material,
                component_id=f"PO1-FB{width:g}",
                drawing=drawing,
                revision=revision,
                shape_kind="rectangular_opening_flat_bar",
                parameters={
                    "po_designation": f"PO1-{selected_l:g}",
                    "opening_L_mm": selected_l,
                    "opening_D_mm": diameter_d,
                    "fillet_weld_mm": 4,
                },
            )
    else:
        width = float(rule["flat_bar_width_mm"])
        developed = pi * (selected_l + thickness)
        _add_flat_bar(
            result,
            name=f"{branch} 環形開孔補強扁鐵",
            width_mm=width,
            thickness_mm=thickness,
            cut_length_mm=developed,
            quantity=1,
            material=material,
            component_id=f"{branch}-ROLLED-FLAT-BAR",
            drawing=drawing,
            revision=revision,
            shape_kind="rolled_flat_bar_ring",
            parameters={
                "po_designation": f"{branch}-{selected_l:g}",
                "opening_L_mm": selected_l,
                "opening_D_mm": diameter_d,
                "developed_length_formula": "pi * (L + t)",
                "fillet_weld_mm": 4,
            },
            source_total_weight_kg=source_weight,
        )

    add_issue(
        result,
        code="OPEN_ALIAS_TO_CW_PO",
        severity="high",
        message=(
            f'{fullstring}: 專案非標準OPEN碼依中威PO系列換算為'
            f'{branch}-{selected_l:g}；公稱{line_size:g}吋先換OD={pipe_od:g}mm，'
            f'D={diameter_d:g}mm，再加兩側各{clearance:g}mm選表列L。'
            "目前採用的是E19-06 SPECIAL SUPPORT Standard(R1)跨專案圖，"
            "可顯示暫估BOM，但須工程確認E25-24沿用性後才可正式下料／出加工圖"
        ),
        scope="cross_project_designation_alias",
        calculation_allowed=True,
        bom_allowed=False,
        fabrication_allowed=False,
        source=config["source_file"],
    )

    assembly = {
        "input_designation": fullstring,
        "resolved_po_designation": f"{branch}-{selected_l:g}",
        "line_size_in": line_size,
        "pipe_od_mm": pipe_od,
        "insulation_mm": insulation_mm,
        "insulation_label": insulation_label,
        "diameter_D_mm": diameter_d,
        "diameter_basis": diameter_basis,
        "clearance_each_side_mm": clearance,
        "minimum_required_L_mm": required_l,
        "selected_table_L_mm": selected_l,
        "surface": "checker_plate" if branch == "PO3" else "grating",
        "source_total_weight_kg": source_weight,
    }
    result.meta["fabrication"] = {
        "source_profile": "cw_e25_24_hp6",
        "source_drawing": drawing,
        "source_file": config["source_file"],
        "source_revision": revision,
        "branch": branch,
        "bom_ready": True,
        "fabrication_ready": True,
        "blockers": [],
        "assembly_dimensions": assembly,
    }
    result.meta["config_version"] = str(config.get("version") or "?")
    result.meta["config_updated"] = str(config.get("data_updated_at") or "")
    result.evidence.append(
        make_evidence(
            "cw_platform_opening",
            assembly,
            "user_confirmed_alias_plus_visual_transcription",
            source=f"{drawing} / {config['source_file']}",
            confidence=0.96,
            note="OPEN視為公稱管徑並依PO圖面由OD換算D/L",
        )
    )
    apply_truth_contract(
        result,
        type_id=branch,
        review_reasons=list(result.warnings),
    )
    return result
