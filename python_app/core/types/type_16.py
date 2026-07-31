"""Type 16 source-aware D-18 calculator."""
from __future__ import annotations

from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence


def _load(source_profile):
    config = load_config("16", strict=True)
    if not config:
        raise FileNotFoundError("Type 16 設定檔遺失或損毀")
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 16 尚未建立來源 profile: {profile_id}") from exc
    table = {float(key): value for key, value in config["TYPE16_TABLE"].items()}
    return profile_id, profile, table, config


def _positive_override(overrides, key, required=False):
    raw = overrides.get(key)
    if raw in (None, ""):
        if required:
            raise ValueError(f"缺少 {key}")
        return None
    value = float(raw)
    if value <= 0:
        raise ValueError(f"{key} 必須大於0")
    return value


def _decorate(entry, profile, component_id, kind, spec, params, ready, blockers=None):
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
        profile_id, profile, table, config = _load(source_profile)
        line_size = float(get_lookup_value(get_part(fullstring, 2)))
        h_raw = str(get_part(fullstring, 3) or "")
        if not h_raw.isdigit():
            raise ValueError("第三段 H 需為數字（100mm 單位）")
        h_mm = int(h_raw) * 100
        c_raw = get_part(fullstring, 4)
        if c_raw not in (None, "") and not profile["allows_c_suffix"]:
            raise ValueError("中威 D-18 designation 不含 C 修改段")
        if c_raw not in (None, ""):
            if not str(c_raw).isdigit():
                raise ValueError("第四段 C 需為數字（100mm 單位）")
            c_mm = int(c_raw) * 100
        else:
            c_mm = int(profile["default_overhang_C_mm"])
        field_cut_override = _positive_override(
            overrides, "dummy_pipe_cut_length_mm"
        )
        nominal_cut_length = h_mm + c_mm
        cut_length = field_cut_override or nominal_cut_length
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 16: {exc}"
        return result

    row = table.get(line_size)
    if row is None:
        result.error = f'Type 16 / {profile_id}: D-18 未表列 {line_size:g}"'
        return result

    material_context = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material", "upper_material"),
        legacy_material_kinds=(HardwareKind.SUPPORT_PIPE,),
    )
    service = material_context.service
    pipe_material = resolve_hardware_material(
        HardwareKind.SUPPORT_PIPE,
        service=service,
        overrides=material_context.material_overrides,
    )
    plate_material = resolve_hardware_material(
        HardwareKind.SUPPORT_PLATE,
        service=service,
        overrides=material_context.material_overrides,
    )
    fab = config["fabrication_contract"]
    special_mode = overrides.get("special_main_line")
    connection_layout = str(overrides.get("connection_layout") or "").strip()

    if special_mode is True:
        try:
            special_cut = _positive_override(
                overrides, "special_main_line_piece_cut_length_mm", required=True
            )
        except ValueError as exc:
            result.error = f"Type 16 / {profile_id}: {exc}"
            return result
        main_material_name = str(
            overrides.get("main_line_material")
            or overrides.get("upper_material")
            or ""
        ).strip()
        if not main_material_name:
            result.error = (
                f"Type 16 / {profile_id}: special_main_line=true 時缺 main_line_material"
            )
            return result
        if cut_length is not None and special_cut >= cut_length:
            result.error = (
                "Type 16: special_main_line_piece_cut_length_mm "
                "必須小於 dummy_pipe_cut_length_mm"
            )
            return result
        main_material = resolve_hardware_material(
            HardwareKind.SUPPORT_PIPE,
            service=service,
            overrides=HardwareMaterialOverrides(
                per_kind={HardwareKind.SUPPORT_PIPE: main_material_name}
            ),
        )
        add_pipe_entry(
            result, row["pipe_size_B"], row["pipe_schedule_B"], special_cut,
            main_material,
        )
        special = result.entries[-1]
        _decorate(
            special, profile, "D18-PIPE-B-SPECIAL-MAIN-LINE-SEGMENT",
            "shop_fabricated_pipe_segment_with_main_line",
            f'{row["pipe_size_B"]}"*{row["pipe_schedule_B"]}; CUT L={special_cut:g}',
            {
                "cut_length_mm": special_cut,
                "material_basis": "D-18 NOTE 2 same as main line",
                "fabricated_with_main_line_in_shop": True,
                "connection_layout": connection_layout or None,
                "weld_mm": fab["fillet_weld_mm"],
            },
            False,
            ["主管接合 cope/fishmouth 輪廓未尺寸化"],
        )
        remaining_length = 0 if cut_length is None else cut_length - special_cut
        pipe_component_id = "D18-PIPE-B-OUTBOARD-SEGMENT"
    else:
        remaining_length = cut_length or 0
        pipe_component_id = "D18-PIPE-B"

    pipe_blockers = []
    if field_cut_override is None:
        pipe_blockers.append("D-18 Hx 最終現場修切長度尚未回填")
    if not connection_layout:
        pipe_blockers.append("四種主管接合外形未選 connection_layout")
    pipe_blockers.append("主管接合 cope/fishmouth 輪廓未尺寸化")
    add_pipe_entry(
        result, row["pipe_size_B"], row["pipe_schedule_B"], remaining_length,
        pipe_material,
    )
    pipe = result.entries[-1]
    _decorate(
        pipe, profile, pipe_component_id,
        "field_cut_dummy_pipe_with_cover_end",
        f'{row["pipe_size_B"]}"*{row["pipe_schedule_B"]}; CUT L={remaining_length:g}',
        {
            "H_mm": h_mm,
            "C_overhang_mm": c_mm,
            "nominal_cut_length_mm": nominal_cut_length,
            "total_cut_length_mm": cut_length,
            "field_cut_override_mm": field_cut_override,
            "cut_length_formula": "H + C",
            "cut_length_basis": (
                "field override"
                if field_cut_override is not None
                else "designation nominal H + C"
            ),
            "segment_cut_length_mm": remaining_length,
            "field_cut": True,
            "connection_layout": connection_layout or None,
            "weld_mm": fab["fillet_weld_mm"],
            "pipe_weld_limit": fab["pipe_weld_limit"],
        },
        not pipe_blockers,
        pipe_blockers,
    )

    side = row["cover_side_mm"]
    add_plate_entry(
        result, side, side, fab["cover_plate_thickness_mm"],
        "COVER PLATE", material=plate_material,
        plate_role=ComponentRole.COVER_PLATE.value,
        shape_spec=f'{side}SQx{fab["cover_plate_thickness_mm"]}t',
        shape_kind="square_cover_plate",
    )
    cover = result.entries[-1]
    _decorate(
        cover, profile, "D18-COVER-PLATE",
        "square_cover_plate", cover.geometry.shape_spec,
        {
            "side_mm": side,
            "dimension_symbol": profile["cover_dimension_name"],
            "thickness_mm": fab["cover_plate_thickness_mm"],
            "quantity": fab["cover_plate_quantity"],
            "weld_mm": fab["fillet_weld_mm"],
        },
        True,
    )

    blockers = []
    if field_cut_override is None:
        blockers.append(
            "D-18 Hx uses nominal H + C；final field-trim length is not confirmed"
        )
    if special_mode is None:
        blockers.append("special_main_line must be explicitly confirmed true/false")
    if not connection_layout:
        blockers.append("connection_layout/attachment cope is unresolved")
    else:
        blockers.append("attachment cope/fishmouth geometry is not dimensioned")
    if special_mode is True and fab["weep_hole_center_offset_mm"] is None:
        blockers.append("Ø6 weep-hole center offset is not dimensioned")
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": "special_split" if special_mode is True else "normal_single_pipe",
        "bom_ready": special_mode is not None,
        "fabrication_ready": not blockers,
        "blockers": blockers,
        "dimensions": {
            "H_mm": h_mm,
            "C_overhang_mm": c_mm,
            "nominal_cut_length_mm": nominal_cut_length,
            "dummy_pipe_cut_length_mm": cut_length,
            "field_cut_override_mm": field_cut_override,
            "cut_length_formula": "H + C",
            "pipe_size_B": row["pipe_size_B"],
            "cover_side_mm": side,
        },
        "not_furnished": ["D-80 interface"],
    }
    if field_cut_override is None:
        result.warnings.append(
            f"D-18 Pipe B 依 designation 採名義下料 H+C="
            f"{h_mm}+{c_mm}={nominal_cut_length}mm；"
            "NOTE 3 要求 Hx 最終現場修切，實測後可覆寫"
        )
    if special_mode is None:
        result.warnings.append(
            "尚未確認是否屬 D-18 NOTE 2 特殊主管，BOM 尚不能決定是否分成同主管材 shop segment"
        )
    result.evidence.extend([
        make_evidence(
            "type16_source_row", row, "visual_transcription",
            source=profile["drawing"], confidence=0.99,
            note="D-18 A/B/cover table",
        ),
        make_evidence(
            "type16_H_C", {"H_mm": h_mm, "C_mm": c_mm},
            "designation", source=profile["drawing"], confidence=0.99,
        ),
        make_evidence(
            "type16_nominal_pipe_cut",
            {
                "formula": "H + C",
                "H_mm": h_mm,
                "C_mm": c_mm,
                "nominal_cut_length_mm": nominal_cut_length,
                "field_cut_override_mm": field_cut_override,
            },
            "drawing_dimension_chain",
            source=profile["drawing"],
            confidence=0.99,
            note="D-18 shows H followed by fixed/modified C to the cover plate",
        ),
        make_evidence(
            "d80_interface", "not furnished", "drawing_note",
            source=profile["drawing"], confidence=0.99,
        ),
    ])
    return result
