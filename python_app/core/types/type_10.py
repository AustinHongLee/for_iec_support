"""Type 10 source-profile calculator.

Chung Wei D-10/D-10A is a two-plate, four-adjusting-bolt support.  CTCI
20E4588 D-10 is a different construction: one dummy leg with an annular base
washer resting on the M-1 special base plate.  They intentionally use separate
branches here.
"""
from __future__ import annotations

import math
import re

from ..bolt import add_custom_entry
from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..issues import register_host_m42_variance, register_source_envelope
from ..m42 import perform_action_by_letter, source_allows_m42_type
from ..material_specs import SUPPORT_PIPE_A53GRB, material_spec
from ..models import AnalysisEntry, AnalysisResult, GeometryHints
from ..parser import get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence


_HEIGHT_RE = re.compile(r"^(?P<h>\d+)(?P<letter>[A-Za-z])$")
_STEEL_DENSITY_KG_PER_MM3 = 7.85e-6
_M1_ASSEMBLY_MATERIAL = MaterialSpec(
    name="A53-B/A105/A283-C GALV.",
    canonical_id="ASSEMBLY_M1_MIXED_GALV",
    source="M1.pdf mixed-material assembly",
    requires_review=True,
)


def _load_profile(source_profile: str | None) -> tuple[str, dict, dict, dict]:
    config = load_config("10", strict=True)
    if not config:
        raise FileNotFoundError(
            "Type 10 設定檔遺失或損毀 (configs/type_10.json)"
        )
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 10 尚未建立來源 profile: {profile_id}") from exc
    if profile["table_source"] == "TYPE10_TABLE":
        raw_table = config["TYPE10_TABLE"]
    else:
        raw_table = config["source_tables"][profile["table_source"]]
    return (
        profile_id,
        profile,
        {float(k): v for k, v in raw_table.items()},
        config,
    )


def _parse_designation(fullstring: str) -> tuple[float, int, str]:
    line_size = float(get_lookup_value(get_part(fullstring, 2)))
    raw = str(get_part(fullstring, 3) or "").strip()
    match = _HEIGHT_RE.fullmatch(raw)
    if not match:
        raise ValueError("第三段格式應為 HH+M42 字母，例如 05B")
    return line_size, int(match.group("h")) * 100, match.group("letter").upper()


def _h_valid(h_value: int, profile: dict) -> bool:
    maximum = int(profile["h_max_mm"])
    if profile.get("h_max_inclusive"):
        return h_value <= maximum
    return h_value < maximum


def _remove_deleted_plate_a(
    result: AnalysisResult,
    *,
    start: int,
    letter: str,
    profile: dict,
) -> list[str]:
    if letter not in profile.get("delete_m42_plate_a_for", []):
        return []
    before = result.entries[:start]
    kept = []
    deleted = []
    for entry in result.entries[start:]:
        if entry.name.startswith("Plate_a_"):
            deleted.append(entry.name)
        else:
            kept.append(entry)
    result.entries = before + kept
    for index, entry in enumerate(result.entries, start=1):
        entry.item_no = index
    return deleted


def _nominal_metric_blank_weight(spec: str) -> float:
    diameter_text, length_text = spec.upper().split("*", 1)
    diameter = float(diameter_text.removeprefix("M"))
    length = float(length_text.removesuffix("L"))
    volume = math.pi * diameter**2 / 4 * length
    return round(volume * _STEEL_DENSITY_KG_PER_MM3, 2)


def _add_adjusting_bolt_and_nuts(
    result: AnalysisResult,
    *,
    bolt_spec: str,
    bolt_material,
    nut_material,
) -> tuple[AnalysisEntry, AnalysisEntry]:
    bolt_dia = bolt_spec.split("*")[0]
    add_custom_entry(
        result,
        name="ADJ.BOLT",
        spec=bolt_spec,
        material=bolt_material,
        quantity=4,
        unit_weight=_nominal_metric_blank_weight(bolt_spec),
        unit="EA",
        role=ComponentRole.MACHINE_BOLT.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    bolt = result.entries[-1]
    bolt.geometry.component_id = "D10-ADJUSTING-BOLT"
    bolt.geometry.shape_kind = "purchased_full_thread_adjusting_bolt"
    bolt.geometry.shape_spec = bolt_spec
    bolt.geometry.fabrication_ready = True
    bolt.geometry.parameters = {
        "spec": bolt_spec,
        "quantity": 4,
        "weight_basis": "nominal solid-cylinder blank estimate",
    }

    add_custom_entry(
        result,
        name="HEX NUT",
        spec=bolt_dia,
        material=nut_material,
        quantity=16,
        unit_weight=0,
        unit="EA",
        role=ComponentRole.NUT.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    nut = result.entries[-1]
    nut.geometry.component_id = "D10-HEX-NUT"
    nut.geometry.shape_kind = "purchased_hex_nut"
    nut.geometry.shape_spec = bolt_dia
    nut.geometry.fabrication_ready = True
    nut.geometry.parameters = {"spec": bolt_dia, "quantity": 16}
    result.warnings.append(
        "D-10 未提供 adjustable bolt / HEX NUT 成品單重；"
        "bolt 以 nominal blank 概算，nut 重量未計入"
    )
    return bolt, nut


def _add_annular_base_washer(
    result: AnalysisResult,
    *,
    outer_diameter: float,
    inner_diameter: float,
    thickness: float,
    material,
) -> AnalysisEntry:
    material_name = material.name
    net_area = math.pi / 4 * (outer_diameter**2 - inner_diameter**2)
    unit_weight = round(
        net_area * thickness * _STEEL_DENSITY_KG_PER_MM3,
        2,
    )
    entry = AnalysisEntry(
        name="BASE WASHER",
        spec=f"OD{outer_diameter:g}/ID{inner_diameter:g}x{thickness:g}t",
        length=outer_diameter,
        width=outer_diameter,
        material=material_name,
        quantity=1,
        unit_weight=unit_weight,
        total_weight=unit_weight,
        weight_output=unit_weight,
        unit="PC",
        factor=1,
        qty_subtotal=1,
        category="鋼板類",
        role=ComponentRole.BASE_PLATE.value,
        item_class="fabricated_part",
        manufacturing_type="plate_cut",
        geometry=GeometryHints(
            role=ComponentRole.BASE_PLATE.value,
            shape_kind="annular_plate",
            shape_spec=(
                f"OD{outer_diameter:g}/ID{inner_diameter:g}x{thickness:g}t"
            ),
            gross_area_mm2=math.pi / 4 * outer_diameter**2,
            cutout_area_mm2=math.pi / 4 * inner_diameter**2,
            net_area_mm2=net_area,
        ),
    )
    entry.material_canonical_id = material.canonical_id
    result.add_entry(entry)
    return entry


def _add_m1_reference(result: AnalysisResult, config: dict) -> AnalysisEntry:
    m1 = config["fabrication_contract"]["legacy_m1"]
    entry = AnalysisEntry(
        name="SPECIAL BASE PLATE M-1",
        spec="M-1 REV.1",
        material=_M1_ASSEMBLY_MATERIAL.name,
        quantity=1,
        unit_weight=0,
        total_weight=0,
        weight_output=0,
        unit="SET",
        factor=1,
        qty_subtotal=1,
        category="組件類",
        role=ComponentRole.BASE_PLATE.value,
        item_class="fabricated_part",
        manufacturing_type="purchased",
        geometry=GeometryHints(
            role=ComponentRole.BASE_PLATE.value,
            component_id="M-1",
            source_drawing="M1.pdf",
            source_revision="1",
            shape_kind="threaded_special_base_plate_assembly",
            shape_spec="M-1: 3in threaded pipe + 3000# coupling + dia150x12t plate",
            fabrication_ready=True,
            parameters=dict(m1),
        ),
    )
    entry.material_canonical_id = _M1_ASSEMBLY_MATERIAL.canonical_id
    result.add_entry(entry)
    result.warnings.append(
        "M-1 幾何已建檔，但 3000# coupling/螺紋成品單重未提供；"
        "SPECIAL BASE PLATE M-1 重量未計入"
    )
    return entry


def _decorate_pipe(
    entry: AnalysisEntry,
    *,
    component_id: str,
    profile: dict,
    shape_kind: str,
    shape_spec: str,
    parameters: dict,
    ready: bool,
    blockers: list[str] | None = None,
) -> None:
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = shape_kind
    entry.geometry.shape_spec = shape_spec
    entry.geometry.parameters = parameters
    entry.geometry.fabrication_ready = ready
    entry.geometry.fabrication_blockers = list(blockers or [])


def _decorate_m42(entries, *, profile: dict) -> None:
    for entry in entries:
        entry.geometry.source_drawing = profile["m42_drawing"]
        entry.geometry.source_revision = profile["m42_revision"]
        entry.geometry.fabrication_ready = True
        if entry.category == "鋼板類":
            code = entry.name.split("_")[1].upper()
            entry.geometry.component_id = f"M42-PLATE-{code}"
            entry.geometry.shape_kind = "rectangular_base_plate"
            entry.geometry.shape_spec = (
                entry.geometry.shape_spec
                or f"{entry.length:g}x{entry.width:g}x{entry.spec}t"
            )
        elif entry.category == "螺栓類":
            entry.geometry.component_id = "M42-FASTENER"
            entry.geometry.shape_kind = "purchased_fastener"
        elif entry.category == "型鋼類":
            entry.geometry.component_id = "M42-ANGLE-RETAINER"
            entry.geometry.shape_kind = "stock_section_cut"


def _build_cw_branch(
    result: AnalysisResult,
    *,
    row: dict,
    profile_id: str,
    profile: dict,
    config: dict,
    line_size: float,
    h_value: int,
    letter: str,
    connection: str,
    connection_explicit: bool,
    upper_material,
    plate_material,
    bolt_material,
    nut_material,
) -> dict:
    upper_length = float(profile["upper_straight_length_mm"])
    if connection == "elbow":
        upper_length += float(row["L"])
    lower_length = h_value - float(profile["lower_pipe_deduction_mm"])
    if lower_length <= 0:
        raise ValueError(
            f"H={h_value}mm 導致下段 supporting pipe 切長 "
            f"{lower_length:g}mm"
        )

    add_pipe_entry(
        result,
        row["pipe_size_b"],
        row["pipe_sch"],
        upper_length,
        upper_material,
    )
    add_pipe_entry(
        result,
        row["pipe_size_b"],
        row["pipe_sch"],
        lower_length,
        SUPPORT_PIPE_A53GRB,
    )
    bolt_dia = row["bolt_spec"].split("*")[0]
    add_plate_entry(
        result,
        row["plate_w"],
        row["plate_w"],
        row["plate_t"],
        "Plate_F",
        material=plate_material,
        plate_qty=2,
        bolt_switch=True,
        bolt_x=row["W"],
        bolt_y=row["W"],
        bolt_hole=row["d_phi"],
        bolt_size=bolt_dia,
        plate_role="generic_plate",
        shape_spec=(
            f'{row["plate_w"]}x{row["plate_w"]}x{row["plate_t"]}t; '
            f'4-DIA{row["d_phi"]} @ {row["W"]}x{row["W"]}'
        ),
        shape_kind="square_four_hole_adjusting_plate",
    )
    plate = result.entries[-1]
    plate.geometry.component_id = "D10-PLATE-F"
    plate.geometry.source_drawing = profile["drawing"]
    plate.geometry.source_revision = profile["revision"]
    plate.geometry.fabrication_ready = True
    plate.geometry.parameters = {
        "side_mm": row["plate_w"],
        "thickness_mm": row["plate_t"],
        "hole_diameter_mm": row["d_phi"],
        "hole_pitch_x_mm": row["W"],
        "hole_pitch_y_mm": row["W"],
        "edge_offset_mm": config["fabrication_contract"][
            "cw_plate_edge_offset_mm"
        ],
        "quantity": 2,
    }
    _add_adjusting_bolt_and_nuts(
        result,
        bolt_spec=row["bolt_spec"],
        bolt_material=bolt_material,
        nut_material=nut_material,
    )

    m42_start = len(result.entries)
    perform_action_by_letter(
        result,
        letter,
        row["pipe_size_b"],
        source_profile=profile_id,
    )
    if result.error:
        raise ValueError(result.error)
    m42_end = len(result.entries)
    _decorate_m42(result.entries[m42_start:m42_end], profile=profile)

    cope = (
        f'upper dummy pipe to {connection} cope/fishmouth 輪廓未尺寸化'
    )
    _decorate_pipe(
        result.entries[0],
        component_id="D10-UPPER-DUMMY-PIPE",
        profile=profile,
        shape_kind=f"dummy_pipe_to_{connection}",
        shape_spec=(
            f'{row["pipe_size_b"]}"*{row["pipe_sch"]}; '
            f"CUT L={upper_length:g}"
        ),
        parameters={
            "supported_line_size_in": line_size,
            "connection": connection,
            "elbow_L_mm": row["L"] if connection == "elbow" else 0,
            "cut_length_mm": upper_length,
            "material_same_as_main": True,
            "field_weld_mm": config["fabrication_contract"]["field_weld_mm"],
        },
        ready=False,
        blockers=[cope],
    )
    weep = (
        "D-10 只標 Ø6 weep hole，未給孔中心相對 Plate F 的尺寸"
    )
    _decorate_pipe(
        result.entries[1],
        component_id="D10-LOWER-SUPPORTING-PIPE",
        profile=profile,
        shape_kind="square_cut_support_pipe_with_weep_hole",
        shape_spec=(
            f'{row["pipe_size_b"]}"*{row["pipe_sch"]}; '
            f"CUT L={lower_length:g}; WEEP HOLE DIA6"
        ),
        parameters={
            "H_mm": h_value,
            "cut_formula": "H - 300",
            "cut_length_mm": lower_length,
            "weep_hole_diameter_mm": 6,
        },
        ready=False,
        blockers=[weep],
    )
    blockers = [cope, weep]
    if not connection_explicit:
        blockers.append(
            "designation does not encode straight/elbow; connection must be confirmed"
        )
    return {
        "upper_length": upper_length,
        "lower_length": lower_length,
        "blockers": blockers,
        "bom_ready": connection_explicit,
        "branch": "four_bolt_double_plate",
        "m42_omitted": [],
    }


def _build_20e_branch(
    result: AnalysisResult,
    *,
    row: dict,
    profile_id: str,
    profile: dict,
    config: dict,
    line_size: float,
    h_value: int,
    letter: str,
    connection: str,
    connection_explicit: bool,
    upper_material,
    plate_material,
) -> dict:
    upper_length = float(profile["upper_straight_length_mm"])
    if connection == "elbow":
        upper_length += float(row["L"])
    lower_length = h_value - float(profile["lower_pipe_deduction_mm"])
    if lower_length <= 0:
        raise ValueError(
            f"H={h_value}mm 導致下段 supporting pipe 切長 "
            f"{lower_length:g}mm"
        )
    add_pipe_entry(
        result,
        row["pipe_size_b"],
        row["pipe_sch"],
        upper_length,
        upper_material,
    )
    add_pipe_entry(
        result,
        row["pipe_size_b"],
        row["pipe_sch"],
        lower_length,
        SUPPORT_PIPE_A53GRB,
    )
    washer = _add_annular_base_washer(
        result,
        outer_diameter=row["F"],
        inner_diameter=config["fabrication_contract"][
            "legacy_base_washer_inner_diameter_mm"
        ],
        thickness=config["fabrication_contract"][
            "legacy_base_washer_thickness_mm"
        ],
        material=plate_material,
    )
    washer.geometry.component_id = "D10-BASE-WASHER"
    washer.geometry.source_drawing = profile["drawing"]
    washer.geometry.source_revision = profile["revision"]
    washer.geometry.fabrication_ready = True
    washer.geometry.parameters = {
        "outer_diameter_F_mm": row["F"],
        "inner_diameter_mm": 95,
        "thickness_mm": 12,
        "weld_to_dummy_leg_mm": 6,
    }
    _add_m1_reference(result, config)

    m42_start = len(result.entries)
    perform_action_by_letter(
        result,
        letter,
        row["pipe_size_b"],
        source_profile=profile_id,
    )
    if result.error:
        raise ValueError(result.error)
    deleted = _remove_deleted_plate_a(
        result,
        start=m42_start,
        letter=letter,
        profile=profile,
    )
    m42_end = len(result.entries)
    _decorate_m42(result.entries[m42_start:m42_end], profile=profile)

    cope = (
        f'upper dummy pipe to {connection} cope/fishmouth 輪廓未尺寸化'
    )
    _decorate_pipe(
        result.entries[0],
        component_id="D10-UPPER-DUMMY-PIPE",
        profile=profile,
        shape_kind=f"dummy_pipe_to_{connection}",
        shape_spec=(
            f'{row["pipe_size_b"]}"*{row["pipe_sch"]}; '
            f"CUT L={upper_length:g}"
        ),
        parameters={
            "supported_line_size_in": line_size,
            "connection": connection,
            "elbow_L_mm": row["L"] if connection == "elbow" else 0,
            "cut_length_mm": upper_length,
            "material_same_as_main": True,
            "field_weld_mm": 6,
        },
        ready=False,
        blockers=[cope],
    )
    _decorate_pipe(
        result.entries[1],
        component_id="D10-LOWER-SUPPORTING-PIPE",
        profile=profile,
        shape_kind="square_cut_support_pipe_to_base_washer",
        shape_spec=(
            f'{row["pipe_size_b"]}"*{row["pipe_sch"]}; '
            f"CUT L={lower_length:g}"
        ),
        parameters={
            "H_mm": h_value,
            "cut_formula": "H - 200",
            "cut_length_mm": lower_length,
            "base_washer_weld_mm": 6,
        },
        ready=True,
    )
    blockers = [cope]
    if not connection_explicit:
        blockers.append(
            "designation does not encode straight/elbow; connection must be confirmed"
        )
    return {
        "upper_length": upper_length,
        "lower_length": lower_length,
        "blockers": blockers,
        "bom_ready": connection_explicit,
        "branch": "single_leg_base_washer_m1",
        "m42_omitted": deleted,
    }


def calculate(
    fullstring: str,
    connection: str = "elbow",
    upper_material: str = "SUS304",
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    connection = str(connection or "").strip().lower()
    try:
        profile_id, profile, table, config = _load_profile(source_profile)
        line_size, h_value, letter = _parse_designation(fullstring)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 10: {exc}"
        return result

    if connection not in {"elbow", "straight"}:
        result.error = "Type 10: connection 僅允許 elbow/straight"
        return result
    row = table.get(line_size)
    if row is None:
        result.error = (
            f'Type 10 / {profile_id}: 來源 D-10 未表列 {line_size:g}"'
        )
        return result
    if not _h_valid(h_value, profile):
        relation = "≤" if profile.get("h_max_inclusive") else "<"
        if not register_source_envelope(
            result,
            type_label=f"Type 10 / {profile_id}",
            source_ref=f"D-10 H{relation}{profile['h_max_mm']}mm",
            checks=(
                (
                    "H",
                    h_value,
                    int(profile["h_max_mm"]),
                    bool(profile.get("h_max_inclusive")),
                ),
            ),
        ):
            return result
    if letter not in profile["allowed_lower_components"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 10 / {profile_id}: M-42 下部構件 {letter} "
                "不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 10 / {profile_id}",
            source_ref="D-10",
            letter=letter,
            host_allowed=profile["allowed_lower_components"],
        )

    connection_explicit = "connection" in overrides
    if not connection_explicit:
        result.warnings.append(
            "Type 10 編碼未包含 straight/elbow；本筆沿用 elbow 預設，"
            "出加工圖前必須明確選擇主管接點"
        )

    material_context = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material", "upper_material"),
        legacy_material_kinds=(HardwareKind.SUPPORT_PIPE,),
    )
    service = material_context.service
    material_overrides = material_context.material_overrides
    upper_material_spec = material_spec(
        HardwareKind.SUPPORT_PIPE,
        upper_material,
    )
    plate_material = resolve_hardware_material(
        HardwareKind.SUPPORT_PLATE,
        service=service,
        overrides=material_overrides,
    )
    bolt_material = resolve_hardware_material(
        HardwareKind.ANCHOR_BOLT,
        service=service,
        overrides=material_overrides,
    )
    nut_material = resolve_hardware_material(
        HardwareKind.HEAVY_HEX_NUT,
        service=service,
        overrides=material_overrides,
    )

    try:
        if profile["branch"] == "four_bolt_double_plate":
            branch_data = _build_cw_branch(
                result,
                row=row,
                profile_id=profile_id,
                profile=profile,
                config=config,
                line_size=line_size,
                h_value=h_value,
                letter=letter,
                connection=connection,
                connection_explicit=connection_explicit,
                upper_material=upper_material_spec,
                plate_material=plate_material,
                bolt_material=bolt_material,
                nut_material=nut_material,
            )
        else:
            branch_data = _build_20e_branch(
                result,
                row=row,
                profile_id=profile_id,
                profile=profile,
                config=config,
                line_size=line_size,
                h_value=h_value,
                letter=letter,
                connection=connection,
                connection_explicit=connection_explicit,
                upper_material=upper_material_spec,
                plate_material=plate_material,
            )
    except ValueError as exc:
        result.entries.clear()
        result.error = f"Type 10 / {profile_id}: {exc}"
        return result

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f'D-10/{branch_data["branch"]}/{connection}/M42-{letter}',
        "bom_ready": branch_data["bom_ready"],
        "fabrication_ready": False,
        "blockers": branch_data["blockers"],
        "omitted_by_type10_m43_note": branch_data["m42_omitted"],
        "dimensions": {
            "H_mm": h_value,
            "upper_dummy_pipe_cut_length_mm": branch_data["upper_length"],
            "lower_supporting_pipe_cut_length_mm": branch_data["lower_length"],
            "pipe_size_B_in": row["pipe_size_b"],
            "elbow_L_mm": row["L"] if connection == "elbow" else 0,
        },
    }
    result.warnings.append(
        "Type 10 已依來源 construction branch 下料；"
        "上端 cope 與圖面未尺寸化細節仍保留 blocker"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type10_source_row",
                row,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.95,
                note=f"{profile_id} D-10 dimensions table",
            ),
            make_evidence(
                "type10_construction_branch",
                profile["branch"],
                "drawing_note",
                source=profile["drawing"],
                confidence=0.98,
                note="CW double Plate F vs 20E base washer/M-1",
            ),
        ]
    )
    return result
