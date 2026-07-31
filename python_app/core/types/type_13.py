"""Type 13 source-profile and fabrication calculator.

Only Chung Wei supplies D-13.  The assembly uses the source M-4 clamp and M-47
1.5 mm compressed gasket rather than welding to the supported line.
"""
from __future__ import annotations

import re

from data.m4_table import build_m4_item
from data.m47_table import build_m47_item

from ..component_roles import ComponentRole
from ..component_rules import component_or_estimated_clamp_weight
from ..config_loader import load_config
from ..hardware_material import HardwareKind, MaterialSpec
from ..issues import register_source_envelope
from ..m42 import perform_action_by_letter
from ..material_specs import SUPPORT_PIPE_A53GRB, material_spec
from ..models import AnalysisEntry, AnalysisResult, GeometryHints
from ..parser import get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence


_HEIGHT_RE = re.compile(r"^(?P<h>\d+)(?P<letter>[A-Za-z])$")


def _load_profile(source_profile: str | None) -> tuple[str, dict, dict, dict]:
    config = load_config("13", strict=True)
    if not config:
        raise FileNotFoundError(
            "Type 13 設定檔遺失或損毀 (configs/type_13.json)"
        )
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 13 尚未建立來源 profile: {profile_id}") from exc
    raw_table = config[profile["table_source"]]
    return (
        profile_id,
        profile,
        {float(key): value for key, value in raw_table.items()},
        config,
    )


def _parse_designation(fullstring: str) -> tuple[float, int, str]:
    line_size = float(get_lookup_value(get_part(fullstring, 2)))
    raw = str(get_part(fullstring, 3) or "").strip()
    match = _HEIGHT_RE.fullmatch(raw)
    if not match:
        raise ValueError("第三段格式應為 HH+M42 字母，例如 05B")
    return (
        line_size,
        int(match.group("h")) * 100,
        match.group("letter").upper(),
    )


def _plate_material(overrides: dict) -> tuple[MaterialSpec, bool]:
    override = str(overrides.get("plate_material") or "").strip()
    if override:
        return material_spec(HardwareKind.SUPPORT_PLATE, override), True
    return (
        MaterialSpec(
            name="CARBON STEEL",
            canonical_id="UNRESOLVED_D13_CARBON_STEEL",
            source="D-13 structural material class",
            requires_review=True,
        ),
        False,
    )


def _add_pipe_clamp(
    result: AnalysisResult,
    *,
    line_size: float,
    profile: dict,
) -> AnalysisEntry:
    item = build_m4_item(line_size)
    if not item:
        raise ValueError(f'M-4 無 {line_size:g}" PIPE CLAMP TYPE-A row')
    unit_weight = component_or_estimated_clamp_weight(
        item,
        line_size,
        component_id="M-4",
    )
    entry = AnalysisEntry(
        name="PIPE CLAMP",
        spec=item["designation"],
        material="CARBON STEEL",
        quantity=1,
        weight_per_unit=unit_weight,
        unit_weight=unit_weight,
        total_weight=unit_weight,
        weight_output=unit_weight,
        unit="SET",
        factor=1,
        qty_subtotal=1,
        category="管夾類",
        role=ComponentRole.CLAMP.value,
        item_class="accessory",
        manufacturing_type="purchased",
        geometry=GeometryHints(
            role=ComponentRole.CLAMP.value,
            component_id="M-4",
            source_drawing="PIPE-CLAMP_TYPE-A_M-4.pdf",
            source_revision="1",
            shape_kind="purchased_two_piece_pipe_clamp",
            shape_spec=item["designation"],
            fabrication_ready=True,
            parameters={
                key: item[key]
                for key in (
                    "designation",
                    "line_size",
                    "load_650f_kg",
                    "load_750f_kg",
                    "B",
                    "C",
                    "D",
                    "E",
                    "F",
                    "G",
                    "H",
                    "rod_size_a",
                )
            }
            | {
                "quantity": 1,
                "weight_basis": item["weight_basis"],
                "parent_source": profile["drawing"],
            },
        ),
    )
    entry.material_canonical_id = "UNRESOLVED_M4_CARBON_STEEL"
    result.add_entry(entry)
    result.warnings.append(
        "M-4 無 source unit-weight；PIPE CLAMP 重量為集中工程估算"
    )
    return entry


def _add_gasket(
    result: AnalysisResult,
    *,
    line_size: float,
    thickness_mm: float,
    profile: dict,
) -> AnalysisEntry:
    item = build_m47_item(line_size, thickness_mm=thickness_mm)
    if not item:
        raise ValueError(f'M-47 無 {line_size:g}" COMPRESSED GASKET row')
    entry = AnalysisEntry(
        name="NON-ASBESTOS",
        spec=item["spec"],
        length=item["length_mm"],
        width=item["width_mm"],
        material=item["material"],
        quantity=1,
        weight_per_unit=item["unit_weight_kg"],
        unit_weight=item["unit_weight_kg"],
        total_weight=item["unit_weight_kg"],
        weight_output=item["unit_weight_kg"],
        unit="PC",
        factor=1,
        qty_subtotal=1,
        category="墊片類",
        role=ComponentRole.GASKET.value,
        item_class="accessory",
        manufacturing_type="purchased",
        geometry=GeometryHints(
            role=ComponentRole.GASKET.value,
            component_id="M-47",
            source_drawing=item["source_drawing"],
            source_revision=item["source_revision"],
            shape_kind="rectangular_wrap_gasket",
            shape_spec=item["spec"],
            fabrication_ready=True,
            parameters={
                "designation": item["designation"],
                "line_size": item["line_size"],
                "length_mm": item["length_mm"],
                "width_mm": item["width_mm"],
                "thickness_mm": item["thickness_mm"],
                "quantity": 1,
                "material": item["material"],
                "weight_basis": "geometry estimate; source density not provided",
                "parent_source": profile["drawing"],
            },
        ),
    )
    entry.material_canonical_id = "UNRESOLVED_GARLOCK_BLUE_GARD_3000"
    result.add_entry(entry)
    result.warnings.append(
        "M-47 尺寸/1.5t 已依原圖；來源未給密度/單重，重量採幾何估算"
    )
    return entry


def _decorate_m42(entries: list[AnalysisEntry], *, profile_id: str) -> None:
    for entry in entries:
        entry.geometry.source_drawing = (
            f"M-42/M-43 source profile {profile_id}"
        )
        entry.geometry.source_revision = "1"
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


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, table, config = _load_profile(source_profile)
        line_size, h_value, letter = _parse_designation(fullstring)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        result.error = f"Type 13: {exc}"
        return result

    row = table.get(line_size)
    if row is None:
        result.error = (
            f'Type 13 / {profile_id}: 來源 D-13 未表列 {line_size:g}"'
        )
        return result
    if h_value <= 0:
        result.error = (
            f"Type 13 / {profile_id}: H={h_value}mm 超出來源限制 "
            f"0<H≤{profile['h_max_mm']}mm"
        )
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 13 / {profile_id}",
        source_ref="D-13 H上限",
        checks=(("H", h_value, int(profile["h_max_mm"]), True),),
    ):
        return result

    fabrication = config["fabrication_contract"]
    try:
        raw_cut = overrides.get("support_pipe_cut_length_mm")
        support_pipe_cut = (
            float(raw_cut) if raw_cut not in (None, "") else None
        )
        if support_pipe_cut is not None and support_pipe_cut <= 0:
            raise ValueError("support_pipe_cut_length_mm 必須大於 0")
        plate_material, material_ready = _plate_material(overrides)
        _add_pipe_clamp(
            result,
            line_size=line_size,
            profile=profile,
        )
        _add_gasket(
            result,
            line_size=line_size,
            thickness_mm=float(fabrication["gasket_thickness_mm"]),
            profile=profile,
        )
    except (TypeError, ValueError) as exc:
        result.entries.clear()
        result.error = f"Type 13 / {profile_id}: {exc}"
        return result

    add_pipe_entry(
        result,
        row["pipe_size_b"],
        row["pipe_sch"],
        support_pipe_cut or 0,
        SUPPORT_PIPE_A53GRB,
    )
    support_pipe = result.entries[-1]
    pipe_blockers = []
    if support_pipe_cut is None:
        pipe_blockers.append(
            "D-13 NOTE 4 指定現場切割；缺 support_pipe_cut_length_mm"
        )
    if fabrication["weep_hole_center_offset_mm"] is None:
        pipe_blockers.append("Ø6 weep hole 中心離底板尺寸未標示")
    support_pipe.geometry.component_id = "D13-SUPPORTING-PIPE-B"
    support_pipe.geometry.source_drawing = profile["drawing"]
    support_pipe.geometry.source_revision = profile["revision"]
    support_pipe.geometry.shape_kind = "field_cut_pipe_with_weep_hole"
    support_pipe.geometry.shape_spec = (
        f'{row["pipe_size_b"]:g}"*{row["pipe_sch"]}; '
        + (
            "FIELD CUT TO SUIT"
            if support_pipe_cut is None
            else f"CUT L={support_pipe_cut:g}"
        )
        + "; DIA6 WEEP HOLE"
    )
    support_pipe.geometry.fabrication_ready = not pipe_blockers
    support_pipe.geometry.fabrication_blockers = pipe_blockers
    support_pipe.geometry.parameters = {
        "H_mm": h_value,
        "cut_length_mm": support_pipe_cut,
        "cut_basis": fabrication["supporting_pipe_cut_basis"],
        "weep_hole_diameter_mm": fabrication["weep_hole_diameter_mm"],
        "weep_hole_center_offset_mm": fabrication[
            "weep_hole_center_offset_mm"
        ],
        "bottom_weld_mm": fabrication["weld_mm"],
    }

    add_plate_entry(
        result,
        plate_a=row["plate_len"],
        plate_b=row["plate_wid"],
        plate_thickness=row["plate_t"],
        plate_name="Plate_P",
        material=plate_material,
        plate_qty=int(fabrication["plate_p_quantity"]),
        plate_role=ComponentRole.SIDE_PLATE.value,
        shape_spec=(
            f'{row["plate_len"]}x{row["plate_wid"]}x{row["plate_t"]}t'
        ),
        shape_kind="rectangular_double_clamp_plate",
    )
    plate_p = result.entries[-1]
    plate_p.geometry.component_id = "D13-PLATE-P"
    plate_p.geometry.source_drawing = profile["drawing"]
    plate_p.geometry.source_revision = profile["revision"]
    plate_p.geometry.fabrication_ready = True
    plate_p.geometry.parameters = {
        "length_mm": row["plate_len"],
        "width_mm": row["plate_wid"],
        "thickness_mm": row["plate_t"],
        "quantity": fabrication["plate_p_quantity"],
        "pipe_center_spacing_C_mm": row["C"],
        "weld_mm": fabrication["weld_mm"],
        "detail_A_applies": line_size >= 10,
        "plate_material_class": fabrication["plate_material_class"],
    }

    cover = fabrication["cover_plate"]
    add_plate_entry(
        result,
        plate_a=cover["length_mm"],
        plate_b=cover["width_mm"],
        plate_thickness=cover["thickness_mm"],
        plate_name="COVER_PL",
        material=plate_material,
        plate_qty=int(cover["quantity"]),
        plate_role=ComponentRole.COVER_PLATE.value,
        shape_spec=(
            f'{cover["length_mm"]}x{cover["width_mm"]}x'
            f'{cover["thickness_mm"]}t'
        ),
        shape_kind="square_cover_plate",
    )
    cover_plate = result.entries[-1]
    cover_plate.geometry.component_id = "D13-COVER-PLATE"
    cover_plate.geometry.source_drawing = profile["drawing"]
    cover_plate.geometry.source_revision = profile["revision"]
    cover_plate.geometry.fabrication_ready = True
    cover_plate.geometry.parameters = {
        **cover,
        "weld_mm": fabrication["weld_mm"],
        "plate_material_class": fabrication["plate_material_class"],
    }

    m42_start = len(result.entries)
    perform_action_by_letter(
        result,
        letter,
        row["pipe_size_b"],
        source_profile=profile_id,
    )
    if result.error:
        result.entries.clear()
        return result
    _decorate_m42(result.entries[m42_start:], profile_id=profile_id)

    blockers = []
    if support_pipe_cut is None:
        blockers.append(
            "lower supporting pipe is field-cut; measured cut length is missing"
        )
    blockers.append("Ø6 weep hole center offset from base plate is not dimensioned")
    if not material_ready:
        blockers.append("D-13 identifies carbon steel class but not plate grade")
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"D-13/M4/M47/M42-{letter}",
        "bom_ready": support_pipe_cut is not None and material_ready,
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": {
            "H_mm": h_value,
            "maximum_line_temperature_f": profile[
                "maximum_line_temperature_f"
            ],
            "supporting_pipe_cut_length_mm": support_pipe_cut,
            "pipe_center_spacing_C_mm": row["C"],
            "plate_P": {
                "length_mm": row["plate_len"],
                "width_mm": row["plate_wid"],
                "thickness_mm": row["plate_t"],
                "quantity": fabrication["plate_p_quantity"],
            },
            "cover_plate": cover,
            "gasket_thickness_mm": fabrication["gasket_thickness_mm"],
            "weep_hole_diameter_mm": fabrication["weep_hole_diameter_mm"],
            "weep_hole_center_offset_mm": fabrication[
                "weep_hole_center_offset_mm"
            ],
        },
    }

    if letter in fabrication["paving_reference_lower_components"]:
        result.warnings.append(
            f"M42-{letter}: H 應從最低鋪面高程起算 (D-13 NOTE 6)"
        )
    if support_pipe_cut is None:
        result.warnings.append(
            "Type 13 supporting pipe 依 D-13 NOTE 4 現場切割；"
            "未提供 support_pipe_cut_length_mm，長度與重量暫不計入"
        )
    if not material_ready:
        result.warnings.append(
            "D-13 結構板僅標 carbon steel 類別，未指定牌號；"
            "出最終 BOM 前請以 plate_material 覆寫確認"
        )
    result.warnings.append(
        "D-13 標示 Ø6 weep hole 但未給孔中心離底板尺寸；"
        "加工圖保持 blocker"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type13_source_row",
                row,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.97,
                note="D-13 dimensions table A/B/C/P",
            ),
            make_evidence(
                "M4_M47_components",
                {
                    "clamp": result.entries[0].geometry.parameters,
                    "gasket": result.entries[1].geometry.parameters,
                },
                "visual_transcription",
                source="PIPE-CLAMP_TYPE-A_M-4.pdf / COMPRESSED-GASKET_M-47.pdf",
                confidence=0.97,
                note="M-4 table and M-47 table/note 1",
            ),
            make_evidence(
                "supporting_pipe_cut_length_mm",
                support_pipe_cut,
                "pdf_visual",
                source=profile["drawing"],
                confidence=0.98 if support_pipe_cut is not None else 0.0,
                note="D-13 NOTE 4: dimension shall be cut to suit in field",
            ),
            make_evidence(
                "plate_P_quantity",
                fabrication["plate_p_quantity"],
                "pdf_visual",
                source=profile["drawing"],
                confidence=0.95,
                note="double side plates in elevation/detail A",
            ),
        ]
    )
    return result
