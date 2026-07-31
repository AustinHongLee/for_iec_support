"""Type 49 source-aware riser support (D-60 + M-11/M-12/M-41)."""

from __future__ import annotations

from copy import deepcopy
import re

from data.m11_table import get_m11_by_line_size
from data.m12_table import get_m12_by_line_size
from data.m41_table import get_m41_by_line_size

from ..bolt import add_custom_entry
from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..fastener_weight import apply_fastener_estimate
from ..models import AnalysisResult
from ..parser import get_lookup_value
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


_RELEASED_D60_DESIGNATION = re.compile(
    r"^49-(?P<size>.+?)B-(?P<figure>[AB])"
    r"(?P<symbol>\([AB]\))?$",
    re.IGNORECASE,
)


def _parse_designation(fullstring: str) -> tuple[float, str, str, str]:
    """Return line size, figure, material symbol and input form.

    Released D-60 form:
        49-{LINE SIZE}B-{FIG}{MATERIAL SYMBOL}
        example: 49-3/4B-A(A)

    Ambiguous two-segment legacy strings such as ``49-10B`` are rejected:
    in the released syntax that string is missing its required FIG segment,
    while the old parser silently interpreted the pipe-size suffix B as FIG-B.
    """
    match = _RELEASED_D60_DESIGNATION.fullmatch(fullstring.strip())
    if not match:
        raise ValueError(
            "Type 49格式應為49-{size}B-{A/B}{material symbol}；"
            "FIG段不得省略，例如49-10B-A"
        )
    size = get_lookup_value(match.group("size"))
    if size <= 0:
        raise ValueError("Type 49管徑無法解析")
    return (
        size,
        match.group("figure").upper(),
        (match.group("symbol") or "").upper(),
        "released_d60",
    )


def _clamp_parameters(row: dict) -> dict:
    keys = (
        "designation",
        "variant",
        "line_size_in",
        "pipe_od_mm",
        "maximum_recommended_load_kg",
        "installed_overall_dimension_name",
        "installed_overall_mm",
        "calculated_installed_overall_mm",
        "source_L_vs_sketch_gap_mm",
        "stock_thickness_mm",
        "stock_width_mm",
        "strip_piece_quantity",
        "inner_bend_radius_mm",
        "neutral_radius_mm",
        "left_straight_projection_mm",
        "right_straight_projection_mm",
        "source_sketch_left_straight_projection_mm",
        "source_sketch_right_straight_projection_mm",
        "straight_projection_total_mm",
        "straight_dimension_basis",
        "straight_split_released",
        "developed_length_formula",
        "developed_length_each_mm",
        "calculated_strip_weight_each_kg",
        "known_two_strip_weight_kg",
        "fastener",
        "reference",
    )
    return {
        key: deepcopy(row[key])
        for key in keys
        if key in row
    }


def _add_clamp_entry(result: AnalysisResult, row: dict) -> None:
    variant = row["variant"]
    add_custom_entry(
        result,
        name=f"RISER CLAMP TYPE-{variant}",
        spec=(
            f"{row['designation']}; "
            f"FB {row['stock_thickness_mm']}x{row['stock_width_mm']} "
            f"x2; {row['fastener']['source_bolt_spec']} x2"
        ),
        material="Carbon Steel (grade not specified)",
        quantity=1,
        unit_weight=row["known_two_strip_weight_kg"],
        unit="SET",
        remark=(
            "重量僅含2片彎製扁鋼毛重；螺栓/螺帽、孔洞與端部圓角未計"
        ),
        category="組件類",
        role=ComponentRole.CLAMP.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.length = row["developed_length_each_mm"]
    entry.width = row["stock_width_mm"]
    entry.geometry.component_id = row["component_id"]
    entry.geometry.source_drawing = row["source_drawing"]
    entry.geometry.source_revision = row["revision"]
    entry.geometry.shape_kind = "formed_riser_clamp_strip_set"
    entry.geometry.shape_spec = (
        f"2 x FB{row['stock_thickness_mm']}x"
        f"{row['stock_width_mm']}; "
        f"DEV={row['developed_length_each_mm']:.2f} mm each; "
        f"180deg around OD{row['pipe_od_mm']:g}"
    )
    entry.geometry.gross_area_mm2 = (
        2
        * row["developed_length_each_mm"]
        * row["stock_width_mm"]
    )
    entry.geometry.parameters = _clamp_parameters(row)
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = list(
        row["fabrication_blockers"]
    )


def _add_clamp_fastener_reference(
    result: AnalysisResult,
    row: dict,
) -> str:
    component_id = f"{row['component_id']}-FASTENERS"
    blocker = (
        f"{row['component_id']} shows two bolt-and-nut positions and releases "
        f"{row['fastener']['source_bolt_spec']}, but bolt/nut grade, nut "
        "scope, hole layout and supplier finished unit weight are not supplied；"
        "nominal geometry is retained for theoretical MTO weight"
    )
    entry = add_reference(
        result,
        name=f"{row['component_id']} BOLT WITH NUT",
        spec=row["fastener"]["source_bolt_spec"],
        material="GRADE / COATING NOT SPECIFIED",
        quantity=row["fastener"]["assembly_positions_shown"],
        category="螺栓類",
        component_id=component_id,
        drawing=row["source_drawing"],
        revision=row["revision"],
        shape_kind="purchased_riser_clamp_fastener",
        parameters=deepcopy(row["fastener"]),
        blocker=blocker,
        manufacturing_type="purchased",
    )
    apply_fastener_estimate(
        entry,
        kind="machine_bolt_with_nut",
    )
    return component_id


def _add_lug_entry(
    result: AnalysisResult,
    row: dict,
) -> None:
    add_custom_entry(
        result,
        name="LUG PLATE TYPE-P BLANK",
        spec=(
            f"{row['designation']}; "
            f"{row['A_height_mm']}x{row['C_overall_width_mm']}"
            f"x{row['T_thickness_mm']}t polygon"
        ),
        material=row["material_class"],
        quantity=row["quantity"],
        unit_weight=row["calculated_blank_weight_each_kg"],
        unit="PC",
        remark=(
            "M-41梯形面輪廓blank已計重；管面端坡口/三維貼合尚未釋出"
        ),
        category="鋼板類",
        role=ComponentRole.LUG_PLATE.value,
        item_class="fabricated_part",
        manufacturing_type="shaped_plate",
    )
    entry = result.entries[-1]
    entry.length = row["A_height_mm"]
    entry.width = row["C_overall_width_mm"]
    entry.geometry.component_id = row["component_id"]
    entry.geometry.source_drawing = row["source_drawing"]
    entry.geometry.source_revision = row["revision"]
    entry.geometry.shape_kind = (
        "m41_polygon_blank_with_unreleased_pipe_end_prep"
    )
    entry.geometry.shape_spec = (
        f"{row['designation']}: A{row['A_height_mm']} "
        f"B{row['B_left_vertical_mm']} "
        f"C{row['C_overall_width_mm']} "
        f"D{row['D_top_width_mm']} "
        f"S{row['S_pipe_end_land_mm']} "
        f"T{row['T_thickness_mm']}"
    )
    entry.geometry.gross_area_mm2 = row["gross_area_mm2"]
    entry.geometry.cutout_area_mm2 = (
        row["triangular_cutout_area_mm2"]
    )
    entry.geometry.net_area_mm2 = row["net_area_mm2"]
    entry.geometry.parameters = {
        key: deepcopy(row[key])
        for key in (
            "type_no",
            "designation",
            "line_size_min_in",
            "line_size_max_in",
            "A_height_mm",
            "B_left_vertical_mm",
            "C_overall_width_mm",
            "D_top_width_mm",
            "S_pipe_end_land_mm",
            "T_thickness_mm",
            "quantity",
            "material_class",
            "material_designation_suffix",
            "polygon_points_mm",
            "gross_area_mm2",
            "triangular_cutout_area_mm2",
            "net_area_mm2",
            "calculated_blank_weight_each_kg",
            "calculated_blank_weight_total_kg",
            "pipe_end_source_callouts",
            "blank_ready",
            "fabrication_ready",
        )
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = list(
        row["fabrication_blockers"]
    )


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("49", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 49: 尚未建立來源 profile {profile_id}"
        return result

    try:
        size, figure, material_symbol, input_form = _parse_designation(
            fullstring
        )
    except ValueError as exc:
        result.error = str(exc)
        return result

    material = config["TYPE49_MATERIAL_MAP"].get(material_symbol)
    if material is None:
        result.error = (
            f"Type 49: D-60不支援材質符號 {material_symbol}"
        )
        return result

    clamp_row = (
        get_m11_by_line_size(size)
        if figure == "A"
        else get_m12_by_line_size(size)
    )
    if clamp_row is None:
        result.error = (
            f"Type 49: M-1{'1' if figure == 'A' else '2'}"
            f"未表列 {size:g} 吋，不允許區間內插"
        )
        return result

    _add_clamp_entry(result, clamp_row)
    fastener_component_id = _add_clamp_fastener_reference(
        result,
        clamp_row,
    )
    component_rows = {
        clamp_row["component_id"]: clamp_row["designation"],
        fastener_component_id: clamp_row["fastener"]["source_bolt_spec"],
    }
    referenced_components = [
        clamp_row["component_id"],
        fastener_component_id,
    ]
    blockers = list(clamp_row["fabrication_blockers"])
    known_weight_scope = [
        (
            f"{clamp_row['component_id']} two formed flat-bar strips; "
            "dimensioned fasteners included by theoretical estimate"
        )
    ]

    lug_row = None
    if figure == "A" and size >= 3:
        lug_row = get_m41_by_line_size(size, material)
        if lug_row is None:
            result.error = (
                f"Type 49: M-41未表列 {size:g} 吋或材質 {material}"
            )
            result.entries.clear()
            return result
        _add_lug_entry(result, lug_row)
        component_rows["M-41"] = lug_row["designation"]
        referenced_components.append("M-41")
        blockers.extend(lug_row["fabrication_blockers"])
        known_weight_scope.append(
            "M-41 polygon plate blanks; pipe-end preparation deduction excluded"
        )
    elif figure == "B" and size >= 3:
        ambiguity_blocker = (
            "D-60 FIG-B depicts two lug-like vertical plates, but only "
            "FIG-A labels M-41 and the cited NOTE 2 is missing; do not add "
            "or omit M-41 for FIG-B without owner/design confirmation"
        )
        add_reference(
            result,
            name="D-60 FIG-B LUG-PLATE AMBIGUITY",
            spec="FIG-B >=3in; OWNER/DESIGN CONFIRMATION REQUIRED",
            material="NOT RELEASED",
            quantity=1,
            category="組件類",
            component_id="D-60-FIG-B-LUG-AMBIGUITY",
            drawing=profile["drawing"],
            revision=profile["revision"],
            shape_kind="source_conflict_reference",
            parameters={
                "line_size_in": size,
                "figure": "B",
                "drawing_depicts_lug_like_plates": True,
                "explicit_m41_callout": False,
                "missing_note": "NOTE 2",
            },
            blocker=ambiguity_blocker,
            manufacturing_type="design_confirmation",
        )
        referenced_components.append("D-60-FIG-B-LUG-AMBIGUITY")
        component_rows["D-60-FIG-B-LUG-AMBIGUITY"] = "UNRESOLVED"
        blockers.append(ambiguity_blocker)
        result.warnings.append(ambiguity_blocker)

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "input_form": input_form,
        "branch": f"FIG-{figure}",
        "line_size_in": size,
        "bom_ready": False,
        "known_material_weight_ready": True,
        "blank_ready": bool(lug_row),
        "fabrication_ready": False,
        "blockers": list(dict.fromkeys(blockers)),
        "referenced_components": referenced_components,
        "component_rows": component_rows,
        "known_weight_scope": known_weight_scope,
        "excluded_weight_scope": [
            "M-11/M-12 supplier finished-weight variance and hole deductions",
            "M-41 pipe-end preparation deduction and weld metal",
        ],
        "lug_plate_material_class": material if lug_row else None,
    }
    result.warnings.append(
        "Type 49目前重量含可證實鋼材與M-11/M-12扣件名義幾何理論估重；"
        "螺栓螺帽供應商成品重量、孔洞扣重及整組重量仍待確認"
    )
    if material_symbol and lug_row is None:
        result.warnings.append(
            "D-60材質符號只控制plate；此分支沒有已釋出的M-41 plate，"
            "因此材質符號不改變目前BOM"
        )
    if lug_row:
        result.warnings.append(
            "M-41已計梯形plate blank；管面端坡口、三維貼合與焊材未計"
        )
    result.evidence.append(
        make_evidence(
            "type49_branch",
            {
                "line_size": size,
                "figure": figure,
                "material_symbol": material_symbol,
                "components": referenced_components,
                "component_rows": component_rows,
            },
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
