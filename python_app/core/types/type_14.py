"""Type 14 drawing-backed calculator (Chung Wei D-14/D-15)."""
from __future__ import annotations

from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..issues import register_source_envelope
from ..models import AnalysisEntry, AnalysisResult, GeometryHints
from ..parser import get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _load_profile(source_profile):
    config = load_config("14", strict=True)
    if not config:
        raise FileNotFoundError("Type 14 設定檔遺失或損毀")
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 14 尚未建立來源 profile: {profile_id}") from exc
    table = {
        float(key): value
        for key, value in config[profile["table_source"]].items()
    }
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


def _h_max(limits, line_size, l_value):
    rows = limits.get(line_size, [])
    for l_max, h_max in rows:
        if l_value <= l_max:
            return h_max
    return None


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


def _anchor(result, spec, material, quantity, profile):
    entry = AnalysisEntry(
        name="EXP.BOLT",
        spec=spec,
        material=material.name,
        quantity=quantity,
        unit_weight=0,
        total_weight=0,
        weight_output=0,
        unit="EA",
        factor=1,
        qty_subtotal=quantity,
        category="螺栓類",
        role=ComponentRole.EXPANSION_BOLT.value,
        item_class="accessory",
        manufacturing_type="purchased",
        geometry=GeometryHints(
            role=ComponentRole.EXPANSION_BOLT.value,
            component_id="D14-ANCHOR-BOLT-J",
            source_drawing=profile["drawing"],
            source_revision=profile["revision"],
            shape_kind="purchased_anchor_bolt",
            shape_spec=spec,
            fabrication_ready=True,
            parameters={
                "spec": spec,
                "quantity": quantity,
                "unit_weight_status": "not provided by D-14",
            },
        ),
    )
    entry.material_canonical_id = material.canonical_id
    result.add_entry(entry)


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, table, limits, config = _load_profile(source_profile)
        line_size, l_value, h_value = _parse(fullstring)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 14: {exc}"
        return result

    row = table.get(line_size)
    if row is None:
        result.error = f'Type 14 / {profile_id}: D-14 未表列 {line_size:g}"'
        return result
    if l_value <= 0 or h_value <= 0:
        result.error = f"Type 14 / {profile_id}: L與H必須大於0"
        return result
    h_max = _h_max(limits, line_size, l_value)
    limit_rows = limits.get(line_size, [])
    if not limit_rows:
        result.error = (
            f'Type 14 / {profile_id}: D-15 未表列 {line_size:g}" L/H限制'
        )
        return result
    l_limit, h_at_l_limit = max(limit_rows, key=lambda item: item[0])
    if h_max is None:
        h_max = h_at_l_limit
    if not register_source_envelope(
        result,
        type_label=f"Type 14 / {profile_id}",
        source_ref="D-15 L/H上限",
        checks=(
            ("L", l_value, l_limit, True),
            ("H", h_value, h_max, True),
        ),
    ):
        return result

    material_context = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material", "upper_material"),
        legacy_material_kinds=(
            HardwareKind.SUPPORT_PIPE,
            HardwareKind.ANCHOR_BOLT,
        ),
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
    anchor_material = resolve_hardware_material(
        HardwareKind.ANCHOR_BOLT, service=service, overrides=material_overrides
    )

    fab = config["fabrication_contract"]
    channel_depth = int(row["member"][1:4])
    pipe_length = h_value - 2 * row["F"] - channel_depth
    member_cut = l_value - 2 * fab["stopper_thickness_mm"]
    if pipe_length <= 0 or member_cut <= 0:
        result.error = (
            f"Type 14 / {profile_id}: supporting pipe={pipe_length}mm、"
            f"member={member_cut}mm，切長無法製作"
        )
        return result

    raw_p = overrides.get("wing_plate_P_mm")
    wing_p = float(raw_p) if raw_p not in (None, "") else float(row["P"])
    if wing_p <= 0:
        result.error = "Type 14: wing_plate_P_mm 必須大於0"
        return result
    p_explicit = raw_p not in (None, "")

    add_pipe_entry(result, line_size, row["pipe_sch"], pipe_length, support_material)
    pipe = result.entries[-1]
    pipe_blockers = []
    if fab["weep_hole_center_offset_mm"] is None:
        pipe_blockers.append("Ø6 weep hole 中心離底板尺寸未標示")
    _decorate(
        pipe,
        profile,
        "D14-SUPPORTING-PIPE-A",
        "square_cut_pipe_with_weep_hole",
        f'{line_size:g}"*{row["pipe_sch"]}; CUT L={pipe_length}; DIA6 WEEP HOLE',
        {
            "H_mm": h_value,
            "cut_formula": "H - 2F - MEMBER_N_DEPTH",
            "F_mm": row["F"],
            "member_depth_mm": channel_depth,
            "cut_length_mm": pipe_length,
            "weep_hole_diameter_mm": fab["weep_hole_diameter_mm"],
            "weep_hole_center_offset_mm": fab["weep_hole_center_offset_mm"],
            "weld_mm": fab["weld_mm"],
        },
        not pipe_blockers,
        pipe_blockers,
    )

    channel_qty = 2 if line_size >= 10 else 1
    channel_dim = row["member"][1:].replace("X", "*")
    add_steel_section_entry(
        result, "Channel", channel_dim, member_cut,
        steel_qty=channel_qty, material=steel_material.name,
    )
    channel = result.entries[-1]
    channel.material_canonical_id = steel_material.canonical_id
    _decorate(
        channel,
        profile,
        "D14-MEMBER-N",
        "back_to_back_double_channel" if channel_qty == 2 else "single_channel",
        f'{row["member"]}; CUT L={member_cut}; QTY {channel_qty}',
        {
            "section": row["member"], "overall_L_mm": l_value,
            "cut_formula": "L - 2*STOPPER_T",
            "stopper_thickness_mm": fab["stopper_thickness_mm"],
            "cut_length_mm": member_cut,
            "quantity": channel_qty,
            "detail_a": channel_qty == 2,
            "weld_mm": fab["weld_mm"],
        },
    )

    wing_points = [
        [0, float(row["Q"])],
        [20.0, float(row["Q"])],
        [wing_p, 25.0],
        [wing_p, 0],
        [10.0, 0],
        [0, 10.0],
    ]
    wing_net_area = _polygon_area(wing_points)
    wing_gross_area = float(row["Q"]) * wing_p
    add_plate_entry(
        result, row["Q"], wing_p, row["F"], "Plate_WING",
        material=plate_material, plate_qty=fab["wing_quantity"],
        plate_role=ComponentRole.WING_PLATE.value,
        shape_spec=f'POLYGON Q{row["Q"]} P{wing_p:g} TOP20 LOWER25 C10 x{row["F"]}t',
        shape_kind="six_vertex_wing_plate",
        gross_area_mm2=wing_gross_area,
        cutout_area_mm2=wing_gross_area - wing_net_area,
        net_area_mm2=wing_net_area,
    )
    wing = result.entries[-1]
    wing_blockers = []
    if not p_explicit:
        wing_blockers.append("D-14 NOTE 3: P 現場切割，缺 wing_plate_P_mm")
    _decorate(
        wing, profile, "D14-WING-PLATE",
        "six_vertex_wing_plate",
        wing.geometry.shape_spec,
        {
            "Q_mm": row["Q"], "P_mm": wing_p, "thickness_mm": row["F"],
            "quantity": fab["wing_quantity"], "P_explicit": p_explicit,
            "polygon_points_mm": wing_points,
            "net_area_mm2": wing_net_area,
        },
        p_explicit, wing_blockers,
    )

    chamfer = fab["stopper_chamfer_mm"]
    net_area = row["M"] * row["K"] - 4 * chamfer * chamfer / 2
    add_plate_entry(
        result, row["M"], row["K"], fab["stopper_thickness_mm"],
        "Plate_STOPPER", material=plate_material,
        plate_qty=fab["stopper_quantity"],
        plate_role=ComponentRole.STOPPER_PLATE.value,
        shape_spec=f'{row["M"]}x{row["K"]}x6t; 4-C{chamfer}',
        shape_kind="four_chamfer_stopper_plate",
        gross_area_mm2=row["M"] * row["K"],
        cutout_area_mm2=row["M"] * row["K"] - net_area,
        net_area_mm2=net_area,
    )
    stopper = result.entries[-1]
    _decorate(
        stopper, profile, "D14-STOPPER-PLATE",
        "four_chamfer_stopper_plate",
        f'{row["M"]}x{row["K"]}x6t; 4-C{chamfer}; QTY {fab["stopper_quantity"]}',
        {
            "M_mm": row["M"], "K_mm": row["K"], "thickness_mm": 6,
            "chamfer_mm": chamfer, "chamfer_count": 4,
            "net_area_mm2": net_area, "quantity": fab["stopper_quantity"],
            "weld_mm": fab["weld_mm"],
        },
    )

    add_plate_entry(
        result, row["C"], row["C"], row["F"], "Plate_BASE",
        material=plate_material, bolt_switch=True, bolt_x=row["D"], bolt_y=row["D"],
        bolt_hole=row["E"], bolt_size=row["J"],
        plate_role=ComponentRole.BASE_PLATE.value,
        shape_spec=f'{row["C"]}SQx{row["F"]}t; 4-DIA{row["E"]} @ {row["D"]}SQ',
        shape_kind="square_four_hole_base_plate",
    )
    base = result.entries[-1]
    _decorate(
        base, profile, "D14-BASE-PLATE",
        "square_four_hole_base_plate", base.geometry.shape_spec,
        {
            "side_C_mm": row["C"], "thickness_F_mm": row["F"],
            "hole_diameter_E_mm": row["E"], "hole_pitch_D_mm": row["D"],
            "hole_count": 4, "anchor_spec_J": row["J"],
        },
    )

    add_plate_entry(
        result, row["B"], row["B"], row["F"], "Plate_TOP",
        material=plate_material, plate_role=ComponentRole.TOP_PLATE.value,
        shape_spec=f'{row["B"]}SQx{row["F"]}t',
        shape_kind="square_top_plate",
    )
    top = result.entries[-1]
    _decorate(
        top, profile, "D14-TOP-PLATE", "square_top_plate",
        top.geometry.shape_spec,
        {"side_B_mm": row["B"], "thickness_F_mm": row["F"], "weld_mm": 6},
    )
    _anchor(result, row["J"], anchor_material, fab["anchor_quantity"], profile)

    blockers = [
        "Ø6 weep hole center offset is not dimensioned",
        "EXP.BOLT finished unit weight is not provided",
    ]
    if not p_explicit:
        blockers.append("Wing Plate P is field-cut; wing_plate_P_mm is missing")
    if channel_qty == 2:
        blockers.append("DETAIL a does not dimension the spacing between double channels")
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f'D-14/{row["member"]}/QTY{channel_qty}',
        "bom_ready": p_explicit,
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": {
            "L_mm": l_value, "H_mm": h_value, "H_max_mm": h_max,
            "supporting_pipe_cut_length_mm": pipe_length,
            "member_cut_length_mm": member_cut,
            "wing_P_mm": wing_p, "wing_P_explicit": p_explicit,
            "member_N": row["member"], "member_quantity": channel_qty,
        },
    }
    if not p_explicit:
        result.warnings.append(
            f"D-14 NOTE 3 指定 Wing Plate P 現場切割；暫以表值 {wing_p:g}mm "
            "計算 polygon 估重，最終 BOM 需 wing_plate_P_mm"
        )
    if channel_qty == 2:
        result.warnings.append(
            "D-14 DETAIL a 的雙槽鐵間距未標示，單支切長可用但組立圖仍需補尺寸"
        )
    result.warnings.append(
        "D-14 EXP.BOLT 無成品單重，重量未計入；Ø6 孔定位仍有 blocker"
    )
    result.evidence.extend([
        make_evidence(
            "type14_source_row", row, "visual_transcription",
            source=profile["drawing"], confidence=0.97,
            note="D-14 standard dimension list",
        ),
        make_evidence(
            "type14_lh_limit", {"L": l_value, "H_max": h_max}, "visual_transcription",
            source=profile["limit_drawing"], confidence=0.98,
            note="D-15 L/H maximum table",
        ),
        make_evidence(
            "supporting_pipe_cut_length_mm", pipe_length, "formula",
            source=profile["drawing"], confidence=0.9,
            note="H - base F - top F - member depth",
        ),
        make_evidence(
            "member_cut_length_mm", member_cut, "formula",
            source=profile["drawing"], confidence=0.94,
            note="L is overall between outside stopper faces; member = L - 2*6t",
        ),
        make_evidence(
            "stopper_net_area_mm2", net_area, "formula",
            source=profile["drawing"], confidence=0.97,
            note="M*K minus four 10C triangles",
        ),
        make_evidence(
            "wing_plate_polygon", wing_points, "visual_transcription",
            source=profile["drawing"], confidence=0.97,
            note="Q/P/20/25/10C six-vertex contour",
        ),
    ])
    return result
