"""Type 12 drawing-backed calculator.

Only the Chung Wei E25-24 D-12 source exists in the supplied drawing sets.
The lower supporting pipe is explicitly field-cut (NOTE 3); H alone does not
define a source-backed cut length.
"""
from __future__ import annotations

import re

from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import HardwareKind, MaterialSpec
from ..issues import register_source_envelope
from ..m42 import perform_action_by_letter
from ..material_specs import SUPPORT_PIPE_A53GRB, material_spec
from ..models import AnalysisEntry, AnalysisResult
from ..parser import get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence


_DESIGNATION_RE = re.compile(
    r"^(?P<h>\d+)(?P<letter>[A-Za-z])(?P<suffix>\((?:A|S)\))?$",
    re.IGNORECASE,
)


def _load_profile(source_profile: str | None) -> tuple[str, dict, dict, dict]:
    config = load_config("12", strict=True)
    if not config:
        raise FileNotFoundError(
            "Type 12 設定檔遺失或損毀 (configs/type_12.json)"
        )
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 12 尚未建立來源 profile: {profile_id}") from exc
    raw_table = config[profile["table_source"]]
    return (
        profile_id,
        profile,
        {float(key): value for key, value in raw_table.items()},
        config,
    )


def _parse_designation(fullstring: str) -> tuple[float, int, str, str]:
    line_size = float(get_lookup_value(get_part(fullstring, 2)))
    raw = str(get_part(fullstring, 3) or "").strip()
    match = _DESIGNATION_RE.fullmatch(raw)
    if not match:
        raise ValueError(
            "第三段格式應為 HH+M42 字母，並可選 (A)/(S)，例如 05B(A)"
        )
    return (
        line_size,
        int(match.group("h")) * 100,
        match.group("letter").upper(),
        (match.group("suffix") or "").upper(),
    )


def _plate_material(
    *,
    suffix: str,
    config: dict,
    overrides: dict,
) -> tuple[MaterialSpec, str, bool]:
    material_class = config["fabrication_contract"][
        "plate_material_symbols"
    ][suffix]
    override = str(overrides.get("plate_material") or "").strip()
    if override:
        return (
            material_spec(HardwareKind.SUPPORT_PLATE, override),
            material_class,
            True,
        )
    token = material_class.replace(" ", "_")
    return (
        MaterialSpec(
            name=material_class,
            canonical_id=f"UNRESOLVED_D12_{token}",
            source="D-12 NOTE 4 material class",
            requires_review=True,
        ),
        material_class,
        False,
    )


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
        line_size, h_value, letter, suffix = _parse_designation(fullstring)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        result.error = f"Type 12: {exc}"
        return result

    row = table.get(line_size)
    if row is None:
        result.error = (
            f'Type 12 / {profile_id}: 來源 D-12 未表列 {line_size:g}"'
        )
        return result
    if h_value <= 0:
        result.error = (
            f"Type 12 / {profile_id}: H={h_value}mm 超出來源限制 "
            f"0<H≤{profile['h_max_mm']}mm"
        )
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 12 / {profile_id}",
        source_ref="D-12 H上限",
        checks=(("H", h_value, int(profile["h_max_mm"]), True),),
    ):
        return result

    try:
        raw_cut = overrides.get("support_pipe_cut_length_mm")
        support_pipe_cut = (
            float(raw_cut) if raw_cut not in (None, "") else None
        )
        if support_pipe_cut is not None and support_pipe_cut <= 0:
            raise ValueError("support_pipe_cut_length_mm 必須大於 0")
        plate_material, material_class, material_ready = _plate_material(
            suffix=suffix,
            config=config,
            overrides=overrides,
        )
    except (TypeError, ValueError) as exc:
        result.error = f"Type 12 / {profile_id}: {exc}"
        return result

    fabrication = config["fabrication_contract"]
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
            "D-12 NOTE 3 指定現場切割；缺 support_pipe_cut_length_mm"
        )
    if fabrication["weep_hole_center_offset_mm"] is None:
        pipe_blockers.append("Ø6 weep hole 中心離底板尺寸未標示")
    support_pipe.geometry.component_id = "D12-SUPPORTING-PIPE-B"
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
    plate_p.geometry.component_id = "D12-PLATE-P"
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
        "plate_material_class": material_class,
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
    cover_plate.geometry.component_id = "D12-COVER-PLATE"
    cover_plate.geometry.source_drawing = profile["drawing"]
    cover_plate.geometry.source_revision = profile["revision"]
    cover_plate.geometry.fabrication_ready = True
    cover_plate.geometry.parameters = {
        "length_mm": cover["length_mm"],
        "width_mm": cover["width_mm"],
        "thickness_mm": cover["thickness_mm"],
        "quantity": cover["quantity"],
        "weld_mm": fabrication["weld_mm"],
        "plate_material_class": material_class,
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
        blockers.append(
            f"D-12 identifies only plate material class {material_class}; grade is missing"
        )

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"D-12/M42-{letter}/{material_class}",
        "bom_ready": support_pipe_cut is not None and material_ready,
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": {
            "H_mm": h_value,
            "supporting_pipe_cut_length_mm": support_pipe_cut,
            "pipe_center_spacing_C_mm": row["C"],
            "plate_P": {
                "length_mm": row["plate_len"],
                "width_mm": row["plate_wid"],
                "thickness_mm": row["plate_t"],
                "quantity": fabrication["plate_p_quantity"],
            },
            "cover_plate": cover,
            "weep_hole_diameter_mm": fabrication["weep_hole_diameter_mm"],
            "weep_hole_center_offset_mm": fabrication[
                "weep_hole_center_offset_mm"
            ],
        },
    }

    if letter in fabrication["paving_reference_lower_components"]:
        result.warnings.append(
            f"M42-{letter}: H 應從最低鋪面高程起算 (D-12 NOTE 5)"
        )
    if support_pipe_cut is None:
        result.warnings.append(
            "Type 12 supporting pipe 依 D-12 NOTE 3 現場切割；"
            "未提供 support_pipe_cut_length_mm，長度與重量暫不計入"
        )
    if not material_ready:
        result.warnings.append(
            f"D-12 尾碼只指定 {material_class} 類別，未指定牌號；"
            "出最終 BOM 前請以 plate_material 覆寫確認"
        )
    result.warnings.append(
        "D-12 標示 Ø6 weep hole 但未給孔中心離底板尺寸；"
        "加工圖保持 blocker"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type12_source_row",
                row,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.97,
                note="D-12 dimensions table A/B/C/P",
            ),
            make_evidence(
                "plate_P_quantity",
                fabrication["plate_p_quantity"],
                "pdf_visual",
                source=profile["drawing"],
                confidence=0.95,
                note="double side clamp plates in elevation/detail A",
            ),
            make_evidence(
                "supporting_pipe_cut_length_mm",
                support_pipe_cut,
                "pdf_visual",
                source=profile["drawing"],
                confidence=0.98 if support_pipe_cut is not None else 0.0,
                note="D-12 NOTE 3: dimension shall be cut to suit in field",
            ),
            make_evidence(
                "plate_material_class",
                material_class,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.98,
                note="D-12 NOTE 4 suffix map",
            ),
        ]
    )
    return result
