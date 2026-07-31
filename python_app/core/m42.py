"""
M42 底板程序 - 對應 VBA: X_M42底板程序
根據字母代碼執行對應的鋼板/螺栓/角鋼操作
"""
import json
from functools import lru_cache
from pathlib import Path

from .models import AnalysisResult
from .hardware_material import MaterialSpec
from .material_identity import canonical_material_id
from .plate import add_plate_entry
from .bolt import (
    add_bolt_entry,
    add_custom_entry,
    add_estimated_fastener_entry,
)
from .steel import add_steel_section_entry
from .component_roles import ComponentRole
from .source_profiles import normalize_source_profile
from data.m42_table import resolve_m42_data
from .parser import get_lookup_value


_DEFAULT_M42_PLATE_MATERIAL = MaterialSpec(
    name="A36/SS400",
    canonical_id=canonical_material_id("A36/SS400") or "UNRESOLVED_A36_SS400",
    source="core.m42.default_plate_material",
    requires_review=True,
)
_DEFAULT_M42_BOLT_MATERIAL = MaterialSpec(
    name="SUS304",
    canonical_id=canonical_material_id("SUS304") or "UNRESOLVED_SUS304",
    source="core.m42.default_bolt_material",
    requires_review=True,
)
_DEFAULT_M42_STEEL_MATERIAL = MaterialSpec(
    name="A36/SS400",
    canonical_id=canonical_material_id("A36/SS400") or "UNRESOLVED_A36_SS400",
    source="core.m42.default_steel_material",
    requires_review=True,
)
_DEFAULT_M42_SS304_PLATE_MATERIAL = MaterialSpec(
    name="SUS304",
    canonical_id=canonical_material_id("SUS304") or "UNRESOLVED_SUS304",
    source="core.m42.m42a_ss304_plate_material",
    requires_review=False,
)
_M42_PROFILE_CONFIG = (
    Path(__file__).resolve().parents[1] / "configs" / "m42_profiles.json"
)


@lru_cache(maxsize=1)
def _load_m42_profiles() -> dict:
    with _M42_PROFILE_CONFIG.open("r", encoding="utf-8") as stream:
        return json.load(stream)["profiles"]


def _source_m42_profile(source_profile: str) -> dict:
    profile_id = normalize_source_profile(source_profile)
    try:
        return _load_m42_profiles()[profile_id]
    except KeyError as exc:
        raise ValueError(f"M-42 尚未建立來源 profile: {profile_id}") from exc


def source_allows_m42_type(source_profile: str, letter: str) -> bool:
    """Return whether the source family's M-42 standard defines ``letter``."""

    return str(letter or "").strip().upper() in _source_m42_profile(
        source_profile
    )["allowed_types"]


def _source_fastener_spec(source_profile: str, pipe_size) -> tuple[str, str]:
    profile = _source_m42_profile(source_profile)
    token = str(pipe_size)
    if "*" in token or "x" in token.lower():
        row, _ = resolve_m42_data(token)
        drawn_spec = row["exp_bolt_spec"]
        group = {
            '5/8"': "1_6",
            '3/4"': "8_10",
            '7/8"': "12_plus",
        }[drawn_spec]
    else:
        size = float(get_lookup_value(pipe_size))
        if size <= 6:
            group = "1_6"
        elif size <= 10:
            group = "8_10"
        else:
            group = "12_plus"
    return profile["fastener_kind"], profile["fastener_specs"][group]


def _add_source_fastener(
    result: AnalysisResult,
    pipe_size,
    quantity: int,
    *,
    source_profile: str | None,
    material: str | MaterialSpec,
) -> None:
    if source_profile is None:
        add_bolt_entry(result, pipe_size, quantity, material=material)
        return

    kind, spec = _source_fastener_spec(source_profile, pipe_size)
    role = (
        ComponentRole.MACHINE_BOLT.value
        if kind.startswith("MACH.")
        else ComponentRole.EXPANSION_BOLT.value
    )
    entry = add_estimated_fastener_entry(
        result,
        name=kind,
        spec=spec,
        material=material,
        quantity=quantity,
        role=role,
        unit="SET",
    )
    if entry.unit_weight > 0:
        _append_warning_once(
            result,
            f"M-43 僅提供 {kind} 名義規格與數量；扣件已列理論估重，"
            "供應商成品重量待確認",
        )
    else:
        _append_warning_once(
            result,
            f"M-43 僅提供 {kind} 直徑／數量而未提供完整長度；"
            "扣件重量仍不計入",
        )


def _append_warning_once(result: AnalysisResult, warning: str | None) -> None:
    if warning and warning not in result.warnings:
        result.warnings.append(warning)


def add_m42_plate(
    result: AnalysisResult,
    plate_type: str,
    pipe_size,
    material: str | MaterialSpec | None = None,
):
    """
    依據板型代碼 (a/b/c/d/e) 新增 M42 鋼板
    對應 VBA: AddPlateEntry
    pipe_size 可以是數字(管徑)或含"*"的型鋼字串
    """
    s = str(pipe_size)
    if "*" in s or "x" in s:
        m42, warning = resolve_m42_data(s)
    else:
        size_val = get_lookup_value(pipe_size)
        m42, warning = resolve_m42_data(size_val)
    _append_warning_once(result, warning)

    require_drilling = plate_type in ("b", "c", "d")

    # 依據板型決定查表欄位 (對照 PDF M-43 表格)
    plate_size_map = {
        "a": "plate_a",      # B 欄: B×B
        "b": "plate_bc",     # C 欄: C×C
        "c": "plate_bc",     # C 欄: C×C
        "d": "plate_d",      # E 欄: E×E
        "e": "plate_e",      # G 欄: G×G
    }

    plate_size = m42[plate_size_map.get(plate_type, "plate_a")]
    plate_thickness = m42["plate_thickness"]
    plate_name = f"Plate_{plate_type}" + ("_有鑽孔" if require_drilling else "_無鑽孔")

    bolt_x = bolt_y = bolt_hole = 0
    bolt_size = ""
    if require_drilling:
        if plate_type in ("b", "c"):
            bolt_x = bolt_y = m42["plate_d_bc_bolt"]
        else:
            bolt_x = bolt_y = m42["plate_d_bolt"]
        bolt_hole = m42["bolt_hole_dia"]
        bolt_size = m42["exp_bolt_spec"]

    add_plate_entry(
        result, plate_size, plate_size, plate_thickness, plate_name,
        material=material or _DEFAULT_M42_PLATE_MATERIAL,
        bolt_switch=require_drilling,
        bolt_x=bolt_x, bolt_y=bolt_y,
        bolt_hole=bolt_hole, bolt_size=bolt_size,
        plate_role="base_plate",   # M42 底板
    )


def perform_action_by_letter(
    result: AnalysisResult,
    letter: str,
    pipe_size,
    *,
    plate_material: str | MaterialSpec | None = None,
    bolt_material: str | MaterialSpec | None = None,
    steel_material: str | MaterialSpec | None = None,
    source_profile: str | None = None,
):
    """
    根據字母代碼決定新增哪些鋼板/螺栓/角鋼
    對應 VBA: PerformActionByLetter
    """
    plate_material = plate_material or _DEFAULT_M42_PLATE_MATERIAL
    bolt_material = bolt_material or _DEFAULT_M42_BOLT_MATERIAL
    steel_material = steel_material or _DEFAULT_M42_STEEL_MATERIAL
    ss304_plate_material = _DEFAULT_M42_SS304_PLATE_MATERIAL
    if source_profile is not None:
        source_m42 = _source_m42_profile(source_profile)
        if letter.upper() not in source_m42["allowed_types"]:
            result.error = (
                f"M-42 型式 {letter.upper()} 不存在於 "
                f"{normalize_source_profile(source_profile)} 來源圖"
            )
            return

    def add_fastener():
        _add_source_fastener(
            result,
            pipe_size,
            4,
            source_profile=source_profile,
            material=bolt_material,
        )

    actions = {
        "A": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "B": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "d", pipe_size, plate_material),
            add_fastener()),
        "C": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "D": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "e", pipe_size, plate_material)),
        "E": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "d", pipe_size, plate_material),
            add_fastener(),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "F": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "G": lambda: (
            add_m42_plate(result, "b", pipe_size, plate_material),
            add_fastener()),
        "H": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "J": lambda: (
            add_m42_plate(result, "b", pipe_size, plate_material),
            add_fastener()),
        "K": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "L": lambda: (
            add_m42_plate(result, "c", pipe_size, plate_material),
            add_fastener()),
        "M": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "N": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "P": lambda: (
            add_m42_plate(result, "c", pipe_size, plate_material),
            add_fastener()),
        "R": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "S": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "e", pipe_size, plate_material),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "T": lambda: add_m42_plate(result, "a", pipe_size, ss304_plate_material),
        "U": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "d", pipe_size, ss304_plate_material),
            add_fastener()),
        "V": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "d", pipe_size, ss304_plate_material),
            add_fastener(),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "W": lambda: (
            add_m42_plate(result, "b", pipe_size, ss304_plate_material),
            add_fastener()),
        "X": lambda: (
            add_m42_plate(result, "c", pipe_size, ss304_plate_material),
            add_fastener()),
        "Y": lambda: add_m42_plate(result, "a", pipe_size, ss304_plate_material),
    }

    action = actions.get(letter.upper())
    if action:
        action()
    else:
        result.warnings.append(f"M-42 型式 '{letter}' 未定義，未新增底板組件")
