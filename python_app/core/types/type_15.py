"""Type 15 source-aware, drawing-backed calculator (three D-16 families)."""
from __future__ import annotations

import re

from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..issues import register_source_envelope
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _load_profile(source_profile):
    config = load_config("15", strict=True)
    if not config:
        raise FileNotFoundError("Type 15 設定檔遺失或損毀")
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 15 尚未建立來源 profile: {profile_id}") from exc
    table = {
        float(key): value
        for key, value in config[profile["table_source"]].items()
    }
    limits = None
    if profile.get("limit_source"):
        limits = {
            float(key): value
            for key, value in config[profile["limit_source"]].items()
        }
    return profile_id, profile, table, limits, config


def _parse(fullstring):
    line_size = float(get_lookup_value(get_part(fullstring, 2)))
    raw = str(get_part(fullstring, 3) or "")
    if len(raw) != 4 or not raw.isdigit():
        raise ValueError("第三段需為4碼數字 LLHH")
    return line_size, int(raw[:2]) * 100, int(raw[2:]) * 100


def _h_max(profile, limits, row, line_size, l_value):
    if limits is not None:
        for l_max, h_max in limits.get(line_size, []):
            if l_value <= l_max:
                return h_max
        return None
    if l_value > int(profile["l_max_mm"]):
        return None
    return int(row["H_MAX"])


def _member_geometry(profile, row):
    member = row["member"]
    if profile["member_family"] == "channel":
        match = re.fullmatch(r"C(\d+)X(\d+)X([\d.]+)", member)
        if not match:
            raise ValueError(f"無法解析 Channel 規格 {member}")
        depth, width, web = match.groups()
        return {
            "section_type": "Channel",
            "lookup_dim": f"{depth}*{width}*{web}",
            "depth_mm": float(depth),
            "full_spec": member,
        }
    match = re.fullmatch(r"H(\d+)X(\d+)X([\d.]+)X([\d.]+)", member)
    if not match:
        raise ValueError(f"無法解析 H Beam 規格 {member}")
    depth, width, web, flange = match.groups()
    return {
        "section_type": "H Beam",
        "lookup_dim": f"{depth}*{width}*{web}",
        "depth_mm": float(depth),
        "full_spec": member,
        "flange_thickness_mm": float(flange),
    }


def _polygon_area(points):
    pairs = zip(points, points[1:] + points[:1])
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in pairs)) / 2


def _decorate(entry, profile, component_id, kind, spec, params, ready=True, blockers=None):
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = kind
    entry.geometry.shape_spec = spec
    entry.geometry.parameters = params
    entry.geometry.fabrication_ready = ready
    entry.geometry.fabrication_blockers = list(blockers or [])


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, table, limits, config = _load_profile(source_profile)
        line_size, l_value, h_value = _parse(fullstring)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 15: {exc}"
        return result

    row = table.get(line_size)
    if row is None:
        result.error = (
            f'Type 15 / {profile_id}: D-16 未表列 {line_size:g}" supporting pipe'
        )
        return result
    if l_value <= 0 or h_value <= 0:
        result.error = f"Type 15 / {profile_id}: L與H必須大於0"
        return result
    h_max = _h_max(profile, limits, row, line_size, l_value)
    if limits is not None:
        limit_rows = limits.get(line_size, [])
        if not limit_rows:
            result.error = (
                f'Type 15 / {profile_id}: D-16 未表列 {line_size:g}" L/H限制'
            )
            return result
        l_limit, h_at_l_limit = max(limit_rows, key=lambda item: item[0])
        if h_max is None:
            h_max = h_at_l_limit
        checks = (
            ("L", l_value, l_limit, True),
            ("H", h_value, h_max, True),
        )
    else:
        h_max = int(row["H_MAX"])
        checks = (
            ("L", l_value, int(profile["l_max_mm"]), True),
            ("H", h_value, h_max, True),
        )
    if not register_source_envelope(
        result,
        type_label=f"Type 15 / {profile_id}",
        source_ref="D-16 L/H上限",
        checks=checks,
    ):
        return result

    material_context = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material", "upper_material"),
        legacy_material_kinds=(HardwareKind.SUPPORT_PIPE,),
    )
    service = material_context.service
    material_overrides = material_context.material_overrides
    support_material = resolve_hardware_material(
        HardwareKind.SUPPORT_PIPE, service=service, overrides=material_overrides
    )
    steel_material = resolve_hardware_material(
        HardwareKind.STRUCTURAL_STRUT, service=service, overrides=material_overrides
    )
    plate_material = resolve_hardware_material(
        HardwareKind.SUPPORT_PLATE, service=service, overrides=material_overrides
    )

    fab = config["fabrication_contract"]
    try:
        member_geo = _member_geometry(profile, row)
    except ValueError as exc:
        result.error = f"Type 15 / {profile_id}: {exc}"
        return result

    reinforcement_t = float(row.get("T", 0))
    pipe_length = (
        h_value
        - 2 * float(row["F"])
        - member_geo["depth_mm"]
        - reinforcement_t
    )
    member_cut = l_value - 2 * fab["stopper_thickness_mm"]
    if pipe_length <= 0 or member_cut <= 0:
        result.error = (
            f"Type 15 / {profile_id}: supporting pipe={pipe_length:g}mm、"
            f"member={member_cut:g}mm，切長無法製作"
        )
        return result

    raw_p = overrides.get("wing_plate_P_mm")
    wing_p = float(raw_p) if raw_p not in (None, "") else float(row["P"])
    if wing_p <= fab["wing_top_land_mm"]:
        result.error = (
            "Type 15: wing_plate_P_mm 必須大於 "
            f'{fab["wing_top_land_mm"]}mm'
        )
        return result
    p_explicit = raw_p not in (None, "")

    add_pipe_entry(result, line_size, row["pipe_sch"], pipe_length, support_material)
    pipe = result.entries[-1]
    pipe_blockers = []
    if fab["weep_hole_center_offset_mm"] is None:
        pipe_blockers.append("Ø6 weep hole 中心離底板尺寸未標示")
    cut_formula = "H - 2F - MEMBER_N_DEPTH"
    if reinforcement_t:
        cut_formula += " - REINF_T"
    _decorate(
        pipe,
        profile,
        "D16-SUPPORTING-PIPE-A",
        "square_cut_pipe_with_weep_hole",
        f'{line_size:g}"*{row["pipe_sch"]}; CUT L={pipe_length:g}; DIA6 WEEP HOLE',
        {
            "H_mm": h_value,
            "cut_formula": cut_formula,
            "F_mm": row["F"],
            "member_depth_mm": member_geo["depth_mm"],
            "reinforcement_T_mm": reinforcement_t,
            "cut_length_mm": pipe_length,
            "weep_hole_diameter_mm": fab["weep_hole_diameter_mm"],
            "weep_hole_center_offset_mm": fab["weep_hole_center_offset_mm"],
            "weld_mm": fab["weld_member_and_pipe_mm"],
        },
        not pipe_blockers,
        pipe_blockers,
    )

    member_qty = 2 if (
        profile["member_family"] == "channel" and line_size >= 10
    ) else 1
    add_steel_section_entry(
        result,
        member_geo["section_type"],
        member_geo["lookup_dim"],
        member_cut,
        steel_qty=member_qty,
        material=steel_material,
    )
    member = result.entries[-1]
    member_kind = (
        "back_to_back_double_channel"
        if member_qty == 2
        else "single_channel"
        if profile["member_family"] == "channel"
        else "single_h_beam"
    )
    _decorate(
        member,
        profile,
        "D16-MEMBER-N",
        member_kind,
        f'{row["member"]}; CUT L={member_cut:g}; QTY {member_qty}',
        {
            "section": row["member"],
            "overall_L_mm": l_value,
            "cut_formula": "L - 2*STOPPER_T",
            "stopper_thickness_mm": fab["stopper_thickness_mm"],
            "cut_length_mm": member_cut,
            "quantity": member_qty,
            "detail_o": member_qty == 2,
            "weld_mm": fab["weld_member_and_pipe_mm"],
        },
    )

    wing_points = [
        [0, float(row["Q"])],
        [float(fab["wing_top_land_mm"]), float(row["Q"])],
        [wing_p, float(fab["wing_lower_right_vertical_mm"])],
        [wing_p, 0],
        [float(fab["wing_bottom_left_chamfer_mm"]), 0],
        [0, float(fab["wing_bottom_left_chamfer_mm"])],
    ]
    wing_net_area = _polygon_area(wing_points)
    wing_gross_area = float(row["Q"]) * wing_p
    add_plate_entry(
        result,
        row["Q"],
        wing_p,
        row["F"],
        "Plate_WING",
        material=plate_material,
        plate_qty=fab["wing_quantity"],
        plate_role=ComponentRole.WING_PLATE.value,
        shape_spec=(
            f'POLYGON Q{row["Q"]} P{wing_p:g} TOP20 LOWER25 C10 '
            f'x{row["F"]}t'
        ),
        shape_kind="six_vertex_wing_plate",
        gross_area_mm2=wing_gross_area,
        cutout_area_mm2=wing_gross_area - wing_net_area,
        net_area_mm2=wing_net_area,
    )
    wing = result.entries[-1]
    wing_blockers = []
    if not p_explicit:
        wing_blockers.append("D-16 NOTE 3: P 現場切割，缺 wing_plate_P_mm")
    _decorate(
        wing,
        profile,
        "D16-WING-PLATE",
        "six_vertex_wing_plate",
        wing.geometry.shape_spec,
        {
            "Q_mm": row["Q"],
            "P_mm": wing_p,
            "thickness_F_mm": row["F"],
            "quantity": fab["wing_quantity"],
            "P_explicit": p_explicit,
            "polygon_points_mm": wing_points,
            "net_area_mm2": wing_net_area,
        },
        p_explicit,
        wing_blockers,
    )

    chamfer = float(fab["stopper_chamfer_mm"])
    stopper_gross_area = float(row["M"]) * float(row["K"])
    stopper_net_area = stopper_gross_area - 4 * chamfer * chamfer / 2
    stopper_points = [
        [chamfer, 0],
        [float(row["K"]) - chamfer, 0],
        [float(row["K"]), chamfer],
        [float(row["K"]), float(row["M"]) - chamfer],
        [float(row["K"]) - chamfer, float(row["M"])],
        [chamfer, float(row["M"])],
        [0, float(row["M"]) - chamfer],
        [0, chamfer],
    ]
    add_plate_entry(
        result,
        row["M"],
        row["K"],
        fab["stopper_thickness_mm"],
        "Plate_STOPPER",
        material=plate_material,
        plate_qty=fab["stopper_quantity"],
        plate_role=ComponentRole.STOPPER_PLATE.value,
        shape_spec=f'{row["M"]}x{row["K"]}x6t; 4-C{chamfer:g}',
        shape_kind="eight_vertex_chamfered_stopper",
        gross_area_mm2=stopper_gross_area,
        cutout_area_mm2=stopper_gross_area - stopper_net_area,
        net_area_mm2=stopper_net_area,
    )
    stopper = result.entries[-1]
    _decorate(
        stopper,
        profile,
        "D16-STOPPER-PLATE",
        "eight_vertex_chamfered_stopper",
        stopper.geometry.shape_spec,
        {
            "M_mm": row["M"],
            "K_mm": row["K"],
            "thickness_mm": fab["stopper_thickness_mm"],
            "quantity": fab["stopper_quantity"],
            "polygon_points_mm": stopper_points,
            "net_area_mm2": stopper_net_area,
            "weld_mm": fab["weld_member_and_pipe_mm"],
        },
    )

    add_plate_entry(
        result,
        row["D"],
        row["D"],
        row["F"],
        "Plate_BASE",
        material=plate_material,
        plate_role=ComponentRole.BASE_PLATE.value,
        shape_spec=f'{row["D"]}SQx{row["F"]}t',
        shape_kind="square_base_plate",
    )
    base = result.entries[-1]
    base_weld = (
        fab["weld_base_to_existing_steel_cw_mm"]
        if profile["member_family"] == "channel"
        else fab["weld_base_to_existing_steel_ctci_mm"]
    )
    _decorate(
        base,
        profile,
        "D16-BASE-PLATE",
        "square_base_plate",
        base.geometry.shape_spec,
        {
            "side_D_mm": row["D"],
            "thickness_F_mm": row["F"],
            "weld_to_existing_steel_mm": base_weld,
        },
    )

    add_plate_entry(
        result,
        row["B"],
        row["B"],
        row["F"],
        "Plate_TOP",
        material=plate_material,
        plate_role=ComponentRole.TOP_PLATE.value,
        shape_spec=f'{row["B"]}SQx{row["F"]}t',
        shape_kind="square_top_plate",
    )
    top = result.entries[-1]
    _decorate(
        top,
        profile,
        "D16-TOP-PLATE",
        "square_top_plate",
        top.geometry.shape_spec,
        {
            "side_B_mm": row["B"],
            "thickness_F_mm": row["F"],
            "weld_mm": fab["weld_member_and_pipe_mm"],
        },
    )

    if profile["reinforcement_plate"]:
        add_plate_entry(
            result,
            row["I"],
            row["J"],
            row["T"],
            "Plate_REINFORCEMENT",
            material=plate_material,
            plate_role=ComponentRole.REINFORCEMENT_PAD.value,
            shape_spec=f'{row["I"]}x{row["J"]}x{row["T"]}t',
            shape_kind="rectangular_reinforcement_plate",
        )
        reinforcement = result.entries[-1]
        _decorate(
            reinforcement,
            profile,
            "D16-REINFORCEMENT-PLATE",
            "rectangular_reinforcement_plate",
            reinforcement.geometry.shape_spec,
            {
                "I_mm": row["I"],
                "J_mm": row["J"],
                "T_mm": row["T"],
                "quantity": 1,
                "location": "centered between MEMBER N and B SQ PLATE",
                "weld_mm": fab["weld_member_and_pipe_mm"],
                "weld_sides": 3,
            },
        )

    blockers = ["Ø6 weep hole center offset is not dimensioned"]
    if not p_explicit:
        blockers.append("Wing Plate P is field-cut; wing_plate_P_mm is missing")
    if member_qty == 2:
        blockers.append("DETAIL o does not dimension the spacing between double channels")
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f'{profile["member_family"]}/{row["member"]}/QTY{member_qty}',
        "bom_ready": p_explicit,
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": {
            "L_overall_mm": l_value,
            "H_overall_mm": h_value,
            "H_max_mm": h_max,
            "supporting_pipe_cut_length_mm": pipe_length,
            "member_cut_length_mm": member_cut,
            "wing_P_mm": wing_p,
            "wing_P_explicit": p_explicit,
            "member_N": row["member"],
            "member_quantity": member_qty,
            "reinforcement_plate": profile["reinforcement_plate"],
        },
    }
    if not p_explicit:
        result.warnings.append(
            f"D-16 NOTE 3 指定 Wing Plate P 現場切割；暫以表值 {wing_p:g}mm "
            "計算 polygon 估重，最終 BOM 需 wing_plate_P_mm"
        )
    if member_qty == 2:
        result.warnings.append(
            "D-16 DETAIL o 的雙槽鐵間距未標示，單支切長可用但組立圖仍需補尺寸"
        )
    result.warnings.append("D-16 Ø6 weep hole 未標中心高度，暫不能直接出完整加工圖")
    result.evidence.extend([
        make_evidence(
            "type15_source_row",
            row,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.98,
            note="D-16 standard dimension list",
        ),
        make_evidence(
            "type15_lh_limit",
            {"L": l_value, "H_max": h_max},
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.98,
            note="D-16 L/H maximum",
        ),
        make_evidence(
            "member_cut_length_mm",
            member_cut,
            "formula",
            source=profile["drawing"],
            confidence=0.94,
            note="L is overall between outside stopper faces; member = L - 2*6t",
        ),
        make_evidence(
            "supporting_pipe_cut_length_mm",
            pipe_length,
            "formula",
            source=profile["drawing"],
            confidence=0.93,
            note=cut_formula,
        ),
        make_evidence(
            "wing_plate_polygon",
            wing_points,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.97,
            note="Q/P/20/25/10C six-vertex contour",
        ),
    ])
    return result
