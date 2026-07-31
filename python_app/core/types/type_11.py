"""Type 11 source-profile calculator.

D-11 is a spring-supported dummy leg.  Chung Wei and CTCI 22A share the
general arrangement, but not the size range, lower-component letters, threaded
rod, or designation grammar.  In particular, the 22A designation carries the
installed spring length D as a fourth segment.

The drawing marks the lower 2-inch supporting pipe "cut to suit in field".
There is no source-backed H-391 formula, so its cut length is accepted only as
an explicit ``support_pipe_cut_length_mm`` override.
"""
from __future__ import annotations

import math
import re

from ..bolt import add_custom_entry
from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import HardwareKind, MaterialSpec
from ..issues import register_host_m42_variance
from ..m42 import perform_action_by_letter, source_allows_m42_type
from ..material_specs import SUPPORT_PIPE_A53GRB, material_spec
from ..models import AnalysisEntry, AnalysisResult, GeometryHints
from ..parser import get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence


_HEIGHT_RE = re.compile(r"^(?P<h>\d+)(?P<letter>[A-Za-z])$")
_STEEL_DENSITY_KG_PER_MM3 = 7.85e-6


def _load_profile(source_profile: str | None) -> tuple[str, dict, dict, dict]:
    config = load_config("11", strict=True)
    if not config:
        raise FileNotFoundError(
            "Type 11 設定檔遺失或損毀 (configs/type_11.json)"
        )
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 11 尚未建立來源 profile: {profile_id}") from exc
    if profile["table_source"] == "TYPE11_TABLE":
        raw_table = config["TYPE11_TABLE"]
    else:
        raw_table = config["source_tables"][profile["table_source"]]
    return (
        profile_id,
        profile,
        {float(key): value for key, value in raw_table.items()},
        config,
    )


def _parse_designation(fullstring: str) -> tuple[float, int, str, str]:
    line_size = float(get_lookup_value(get_part(fullstring, 2)))
    raw = str(get_part(fullstring, 3) or "").strip()
    match = _HEIGHT_RE.fullmatch(raw)
    if not match:
        raise ValueError("第三段格式應為 HH+M42 字母，例如 06G")
    installed_length_text = str(get_part(fullstring, 4) or "").strip()
    return (
        line_size,
        int(match.group("h")) * 100,
        match.group("letter").upper(),
        installed_length_text,
    )


def _material_from_source(
    item: dict,
    *,
    kind: HardwareKind,
    override: object = None,
) -> tuple[MaterialSpec, bool]:
    override_text = str(override or "").strip()
    if override_text:
        return (
            material_spec(kind, override_text),
            True,
        )
    return (
        MaterialSpec(
            name=item["material"],
            canonical_id=item["material_canonical_id"],
            source="D-11 source drawing",
            requires_review=not item["source_material_explicit"],
        ),
        bool(item["source_material_explicit"]),
    )


def _nominal_cylinder_weight(diameter_mm: float, length_mm: float) -> float:
    volume = math.pi * diameter_mm**2 / 4 * length_mm
    return round(volume * _STEEL_DENSITY_KG_PER_MM3, 2)


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


def _add_threaded_rod(
    result: AnalysisResult,
    *,
    profile: dict,
    material: MaterialSpec,
) -> AnalysisEntry:
    item = profile["threaded_rod"]
    unit_weight = _nominal_cylinder_weight(
        float(item["diameter_mm"]),
        float(item["length_mm"]),
    )
    add_custom_entry(
        result,
        name="M.B.(FULL THREADED)",
        spec=item["spec"],
        material=material,
        quantity=1,
        unit_weight=unit_weight,
        unit="EA",
        category="螺栓類",
        role=ComponentRole.MACHINE_BOLT.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.length = float(item["length_mm"])
    entry.geometry = GeometryHints(
        role=ComponentRole.MACHINE_BOLT.value,
        component_id="D11-FULL-THREADED-MB",
        source_drawing=profile["drawing"],
        source_revision=profile["revision"],
        shape_kind="purchased_full_thread_machine_bolt",
        shape_spec=item["spec"],
        fabrication_ready=True,
        parameters={
            "nominal_diameter_mm": item["diameter_mm"],
            "length_mm": item["length_mm"],
            "thread": "FULL THREADED",
            "quantity": 1,
            "weight_basis": "nominal solid-cylinder blank estimate",
        },
    )
    return entry


def _add_heavy_hex_nuts(
    result: AnalysisResult,
    *,
    profile: dict,
    material: MaterialSpec,
) -> AnalysisEntry:
    item = profile["heavy_hex_nut"]
    add_custom_entry(
        result,
        name="HEAVY HEX NUT",
        spec=item["spec"],
        material=material,
        quantity=int(item["quantity"]),
        unit_weight=0,
        unit="EA",
        category="螺栓類",
        role=ComponentRole.NUT.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.geometry = GeometryHints(
        role=ComponentRole.NUT.value,
        component_id="D11-HEAVY-HEX-NUT",
        source_drawing=profile["drawing"],
        source_revision=profile["revision"],
        shape_kind="purchased_heavy_hex_nut",
        shape_spec=item["spec"],
        fabrication_ready=True,
        parameters={
            "spec": item["spec"],
            "quantity": item["quantity"],
            "unit_weight_status": "not provided by D-11",
        },
    )
    return entry


def _add_washers(
    result: AnalysisResult,
    *,
    profile: dict,
    fabrication: dict,
) -> AnalysisEntry:
    washer = fabrication["washer"]
    outer = float(washer["outer_diameter_mm"])
    inner = float(washer["inner_diameter_mm"])
    thickness = float(washer["thickness_mm"])
    quantity = int(washer["quantity"])
    net_area = math.pi / 4 * (outer**2 - inner**2)
    unit_weight = round(
        net_area * thickness * _STEEL_DENSITY_KG_PER_MM3,
        2,
    )
    material = MaterialSpec(
        name=washer["material"],
        canonical_id="UNRESOLVED_WROUGHT_STEEL",
        source="D-11 washer callout",
        requires_review=False,
    )
    entry = AnalysisEntry(
        name="WASHER",
        spec=f"OD{outer:g}/ID{inner:g}*{thickness:g}t",
        length=outer,
        width=outer,
        material=material.name,
        quantity=quantity,
        weight_per_unit=unit_weight,
        unit_weight=unit_weight,
        total_weight=round(unit_weight * quantity, 2),
        weight_output=round(unit_weight * quantity, 2),
        unit="EA",
        factor=1,
        qty_subtotal=quantity,
        category="鋼板類",
        role=ComponentRole.WASHER.value,
        item_class="fabricated_part",
        manufacturing_type="plate_cut",
        geometry=GeometryHints(
            role=ComponentRole.WASHER.value,
            component_id="D11-WROUGHT-STEEL-WASHER",
            source_drawing=profile["drawing"],
            source_revision=profile["revision"],
            shape_kind="annular_plate",
            shape_spec=f"OD{outer:g}/ID{inner:g}x{thickness:g}t",
            gross_area_mm2=math.pi / 4 * outer**2,
            cutout_area_mm2=math.pi / 4 * inner**2,
            net_area_mm2=net_area,
            fabrication_ready=True,
            parameters={
                "outer_diameter_mm": outer,
                "inner_diameter_mm": inner,
                "thickness_mm": thickness,
                "quantity": quantity,
                "weight_basis": "exact annular geometry",
            },
        ),
    )
    entry.material_canonical_id = material.canonical_id
    result.add_entry(entry)
    return entry


def _add_spring(
    result: AnalysisResult,
    *,
    profile: dict,
    spring: dict,
    installed_length_mm: float | None,
) -> AnalysisEntry:
    add_custom_entry(
        result,
        name="SPRING",
        spec=(
            f'{spring["spring_mark"]} '
            f'({spring["wire_mm"]}W×{spring["id_mm"]}ID)'
        ),
        material=MaterialSpec(
            name=spring["material"],
            canonical_id="UNRESOLVED_ASTM_A229",
            source="D-11 spring table",
            requires_review=False,
        ),
        quantity=int(spring["quantity"]),
        unit_weight=float(spring["unit_weight_kg"]),
        unit="EA",
        category="彈簧類",
        role=ComponentRole.UNKNOWN.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.geometry = GeometryHints(
        component_id=f'D11-SPRING-{spring["spring_mark"]}',
        source_drawing=profile["drawing"],
        source_revision=profile["revision"],
        shape_kind="purchased_compression_spring",
        shape_spec=(
            f'{spring["spring_mark"]}; WIRE {spring["wire_mm"]}; '
            f'ID {spring["id_mm"]}; FREE L {spring["free_len_mm"]}'
        ),
        fabrication_ready=True,
        parameters={
            "spring_mark": spring["spring_mark"],
            "wire_diameter_mm": spring["wire_mm"],
            "inside_diameter_mm": spring["id_mm"],
            "active_coils": spring["active_coils"],
            "inactive_coils": spring["inactive_coils"],
            "spring_constant_kg_per_mm": spring["spring_k_kg_per_mm"],
            "free_length_mm": spring["free_len_mm"],
            "maximum_recommended_deflection_mm": spring["max_defl_mm"],
            "installed_length_D_mm": installed_length_mm,
            "quantity": spring["quantity"],
            "weight_basis": "six-coil nominal wire-blank estimate",
        },
    )
    return entry


def _installed_length(
    *,
    profile: dict,
    suffix: str,
    overrides: dict,
    spring: dict,
) -> float | None:
    override = overrides.get("spring_installed_length_mm")
    if profile["designation_requires_installed_length"]:
        if not suffix:
            raise ValueError(
                "此來源料號必須包含彈簧安裝長度 D，例如 11-2B-06G-88"
            )
        try:
            value = float(suffix)
        except ValueError as exc:
            raise ValueError("第四段 D 必須是 mm 數值") from exc
        if override not in (None, "") and float(override) != value:
            raise ValueError("第四段 D 與 spring_installed_length_mm 覆寫不一致")
    else:
        if suffix:
            raise ValueError("中威 D-11 料號不包含第四段 D；請使用列覆寫")
        value = float(override) if override not in (None, "") else None

    if value is None:
        return None
    minimum = float(spring["free_len_mm"]) - float(spring["max_defl_mm"])
    maximum = float(spring["free_len_mm"])
    if not minimum <= value <= maximum:
        raise ValueError(
            f"彈簧安裝長度 D={value:g}mm 超出 D-11 建議範圍 "
            f"{minimum:g}–{maximum:g}mm"
        )
    return value


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
        line_size, h_value, letter, suffix = _parse_designation(fullstring)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 11: {exc}"
        return result

    if connection not in {"elbow", "straight"}:
        result.error = "Type 11: connection 僅允許 elbow/straight"
        return result
    row = table.get(line_size)
    if row is None:
        result.error = (
            f'Type 11 / {profile_id}: 來源 D-11 未表列 {line_size:g}"'
        )
        return result
    if h_value not in profile["allowed_h_mm"]:
        result.error = (
            f"Type 11 / {profile_id}: H={h_value}mm 不在來源表列 "
            f"{profile['allowed_h_mm']}"
        )
        return result
    if letter not in profile["allowed_lower_components"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 11 / {profile_id}: M-42 {letter} 不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 11 / {profile_id}",
            source_ref="D-11",
            letter=letter,
            host_allowed=profile["allowed_lower_components"],
        )

    spring = dict(config["TYPE11_SPRING_TABLE"][row["spring_mark"]])
    spring["spring_mark"] = row["spring_mark"]
    try:
        installed_length = _installed_length(
            profile=profile,
            suffix=suffix,
            overrides=overrides,
            spring=spring,
        )
        raw_lower_cut = overrides.get("support_pipe_cut_length_mm")
        lower_cut = (
            float(raw_lower_cut)
            if raw_lower_cut not in (None, "")
            else None
        )
        if lower_cut is not None and lower_cut <= 0:
            raise ValueError("support_pipe_cut_length_mm 必須大於 0")
    except (TypeError, ValueError) as exc:
        result.error = f"Type 11 / {profile_id}: {exc}"
        return result

    connection_explicit = "connection" in overrides
    upper_length = float(config["fabrication_contract"]["upper_straight_tail_mm"])
    if connection == "elbow":
        upper_length += float(row["L"])

    upper_material_spec = material_spec(
        HardwareKind.SUPPORT_PIPE,
        upper_material,
    )
    rod_material, rod_material_ready = _material_from_source(
        profile["threaded_rod"],
        kind=HardwareKind.THREADED_ROD,
        override=overrides.get("threaded_rod_material"),
    )
    nut_material, nut_material_ready = _material_from_source(
        profile["heavy_hex_nut"],
        kind=HardwareKind.HEAVY_HEX_NUT,
        override=overrides.get("heavy_hex_nut_material"),
    )

    add_pipe_entry(
        result,
        config["fabrication_contract"]["upper_pipe_size_in"],
        config["fabrication_contract"]["upper_pipe_schedule"],
        upper_length,
        upper_material_spec,
    )
    add_pipe_entry(
        result,
        config["fabrication_contract"]["supporting_pipe_size_in"],
        config["fabrication_contract"]["supporting_pipe_schedule"],
        lower_cut or 0,
        SUPPORT_PIPE_A53GRB,
    )

    m42_start = len(result.entries)
    perform_action_by_letter(
        result,
        letter,
        config["fabrication_contract"]["supporting_pipe_size_in"],
        source_profile=profile_id,
    )
    if result.error:
        result.entries.clear()
        return result
    m42_end = len(result.entries)

    _add_threaded_rod(result, profile=profile, material=rod_material)
    _add_heavy_hex_nuts(result, profile=profile, material=nut_material)
    _add_washers(
        result,
        profile=profile,
        fabrication=config["fabrication_contract"],
    )
    _add_spring(
        result,
        profile=profile,
        spring=spring,
        installed_length_mm=installed_length,
    )

    cope_blocker = (
        f'1.5" SCH.80 upper dummy pipe 的 {connection} cope/fishmouth '
        "輪廓未由 D-11 尺寸化"
    )
    upper_blockers = [cope_blocker]
    if not connection_explicit:
        upper_blockers.append(
            "connection 使用預設 elbow，而非由編碼或專案列明確指定"
        )
    _decorate_pipe(
        result.entries[0],
        component_id="D11-UPPER-DUMMY-PIPE",
        profile=profile,
        shape_kind=f"dummy_pipe_to_{connection}",
        shape_spec=(
            f'1.5"*SCH.80; CUT L={upper_length:g}; TOP COPE TO '
            f"{connection.upper()}"
        ),
        parameters={
            "supported_line_size_in": line_size,
            "connection": connection,
            "elbow_L_mm": row["L"] if connection == "elbow" else 0,
            "straight_tail_mm": config["fabrication_contract"][
                "upper_straight_tail_mm"
            ],
            "cut_length_mm": upper_length,
            "material_same_as_main": True,
            "field_weld_mm": config["fabrication_contract"]["field_weld_mm"],
        },
        ready=False,
        blockers=upper_blockers,
    )
    lower_blockers = []
    if lower_cut is None:
        lower_blockers.append(
            "D-11 NOTE 4 指定現場切割；缺 support_pipe_cut_length_mm"
        )
    _decorate_pipe(
        result.entries[1],
        component_id="D11-LOWER-SUPPORTING-PIPE",
        profile=profile,
        shape_kind="field_cut_supporting_pipe",
        shape_spec=(
            '2"*SCH.40; FIELD CUT TO SUIT'
            if lower_cut is None
            else f'2"*SCH.40; CUT L={lower_cut:g}'
        ),
        parameters={
            "H_mm": h_value,
            "cut_length_mm": lower_cut,
            "cut_basis": config["fabrication_contract"][
                "supporting_pipe_cut_basis"
            ],
            "minimum_base_clearance_mm": config["fabrication_contract"][
                "minimum_base_clearance_mm"
            ],
            "top_joint": "lower washer / threaded rod assembly",
            "bottom_joint": f"M42-{letter}",
        },
        ready=lower_cut is not None,
        blockers=lower_blockers,
    )
    _decorate_m42(
        result.entries[m42_start:m42_end],
        profile_id=profile_id,
    )

    blockers = [cope_blocker]
    if not connection_explicit:
        blockers.append(
            "designation does not encode straight/elbow; connection must be confirmed"
        )
    if lower_cut is None:
        blockers.append(
            "lower supporting pipe is field-cut; measured cut length is missing"
        )
    if installed_length is None:
        blockers.append(
            "spring installed length D must be set before assembly/fabrication drawing"
        )
    if not rod_material_ready:
        blockers.append("threaded rod material is not specified by Chung Wei D-11")
    if not nut_material_ready:
        blockers.append("heavy hex nut material is not specified by Chung Wei D-11")

    bom_ready = (
        connection_explicit
        and lower_cut is not None
        and installed_length is not None
        and rod_material_ready
        and nut_material_ready
    )
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"D-11/{connection}/M42-{letter}/{row['spring_mark']}",
        "bom_ready": bom_ready,
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": {
            "H_mm": h_value,
            "elbow_L_mm": row["L"] if connection == "elbow" else 0,
            "upper_dummy_pipe_cut_length_mm": upper_length,
            "lower_supporting_pipe_cut_length_mm": lower_cut,
            "spring_installed_length_D_mm": installed_length,
            "minimum_base_clearance_mm": config["fabrication_contract"][
                "minimum_base_clearance_mm"
            ],
            "threaded_rod_spec": profile["threaded_rod"]["spec"],
            "washer": config["fabrication_contract"]["washer"],
            "spring_mark": row["spring_mark"],
        },
    }

    if not connection_explicit:
        result.warnings.append(
            "Type 11 編碼未包含 straight/elbow；本筆沿用 elbow 預設，"
            "出加工圖前必須明確選擇主管接點"
        )
    if lower_cut is None:
        result.warnings.append(
            "Type 11 下立管依 D-11 NOTE 4 為現場切割；"
            "未提供 support_pipe_cut_length_mm，因此長度與重量暫不計入"
        )
    if installed_length is None:
        result.warnings.append(
            "中威 D-11 料號未編入彈簧安裝長度 D；"
            "出組立/加工圖前需提供 spring_installed_length_mm"
        )
    if not rod_material_ready or not nut_material_ready:
        result.warnings.append(
            "中威 D-11 未標全牙螺桿/重型螺帽材質；"
            "目前保留 SOURCE UNSPECIFIED，不由主管材質推定"
        )
    result.warnings.append(
        "D-11 未提供全牙螺桿/螺帽成品單重；"
        "螺桿採 nominal blank 概算，螺帽重量未計入"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type11_source_row",
                row,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.96,
                note=f"{profile_id} D-11 size/spring table",
            ),
            make_evidence(
                "type11_source_profile",
                {
                    "allowed_h_mm": profile["allowed_h_mm"],
                    "allowed_lower_components": profile[
                        "allowed_lower_components"
                    ],
                    "threaded_rod": profile["threaded_rod"],
                    "designation_requires_installed_length": profile[
                        "designation_requires_installed_length"
                    ],
                },
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.96,
                note="D-11 callouts and designation note",
            ),
            make_evidence(
                "upper_dummy_pipe_cut_length_mm",
                upper_length,
                "formula",
                source=profile["drawing"],
                confidence=0.9,
                note="straight=100; elbow=L+100",
            ),
            make_evidence(
                "lower_supporting_pipe_cut_length_mm",
                lower_cut,
                "pdf_visual",
                source=profile["drawing"],
                confidence=0.98 if lower_cut is not None else 0.0,
                note="D-11 NOTE 4: cut to suit in field; no H-391 formula",
            ),
            make_evidence(
                "spring_and_washer_quantities",
                {"spring": 1, "washer": 2},
                "pdf_visual",
                source=profile["drawing"],
                confidence=0.98,
                note="one compression spring between two annular washers",
            ),
        ]
    )
    return result
