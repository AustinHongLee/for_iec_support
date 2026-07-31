"""Drawing-backed calculators for Chang Chun owner standard DES-M15172."""

from __future__ import annotations

from math import pi

from core.bolt import add_custom_entry
from core.component_roles import ComponentRole
from core.fastener_weight import (
    estimate_metric_fastener,
    fastener_density_for_material,
)
from core.issues import register_source_envelope
from core.models import AnalysisResult, set_remark
from core.plate import add_plate_entry
from core.steel import add_steel_section_entry
from core.truth import apply_truth_contract, make_evidence
from core.types._m26_common import add_m26_ubolt
from core.types._source_reference import add_reference
from data.m26_table import get_m26_by_line_size
from data.pipe_table import get_pipe_od


def _drawing(config: dict) -> tuple[str, str]:
    return config["drawing"], config.get("revision", "")


def _decorate(
    entry,
    *,
    component_id: str,
    drawing: str,
    revision: str,
    parameters: dict,
    ready: bool,
    blockers: list[str] | None = None,
    shape_kind: str = "",
) -> None:
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.parameters.update(parameters)
    entry.geometry.fabrication_ready = ready
    entry.geometry.fabrication_blockers = list(blockers or [])
    if shape_kind:
        entry.geometry.shape_kind = shape_kind


def _section(
    result: AnalysisResult,
    *,
    section_type: str,
    spec: str,
    length: float,
    quantity: int,
    material: str,
    name: str,
    component_id: str,
    drawing: str,
    revision: str,
    parameters: dict | None = None,
    ready: bool = True,
    blockers: list[str] | None = None,
    weight_kg_m: float | None = None,
) -> None:
    try:
        add_steel_section_entry(
            result,
            section_type,
            spec,
            length,
            steel_qty=quantity,
            material=material,
        )
    except ValueError:
        if weight_kg_m is None:
            add_custom_entry(
                result,
                name,
                spec,
                material,
                quantity,
                0,
                unit="M",
                remark="圖面有斷面但未提供可核定每米重",
                category="型鋼類",
                role=(
                    ComponentRole.H_SECTION.value
                    if section_type == "H Beam"
                    else ComponentRole.CHANNEL.value
                    if section_type == "Channel"
                    else ComponentRole.UNKNOWN.value
                    if section_type == "Round Bar"
                    else ComponentRole.ANGLE.value
                ),
                item_class="primary_structure",
                manufacturing_type="raw_cut",
            )
            entry = result.entries[-1]
            entry.length = length
            entry.length_subtotal = round(length / 1000 * quantity, 3)
        else:
            unit_weight = round(length / 1000 * weight_kg_m, 2)
            add_custom_entry(
                result,
                name,
                spec,
                material,
                quantity,
                unit_weight,
                unit="M",
                remark=f"核定每米重 {weight_kg_m:g} kg/m",
                category="型鋼類",
                role=(
                    ComponentRole.H_SECTION.value
                    if section_type == "H Beam"
                    else ComponentRole.CHANNEL.value
                    if section_type == "Channel"
                    else ComponentRole.UNKNOWN.value
                    if section_type == "Round Bar"
                    else ComponentRole.ANGLE.value
                ),
                item_class="primary_structure",
                manufacturing_type="raw_cut",
            )
            entry = result.entries[-1]
            entry.length = length
            entry.weight_per_unit = weight_kg_m
            entry.length_subtotal = round(length / 1000 * quantity, 3)
    entry = result.entries[-1]
    entry.name = name
    set_remark(entry, f"{name}，下料長 {length:g} mm，數量 {quantity}")
    _decorate(
        entry,
        component_id=component_id,
        drawing=drawing,
        revision=revision,
        parameters={
            "section_type": section_type,
            "section_spec": spec,
            "cut_length_mm": length,
            "quantity": quantity,
            **(parameters or {}),
        },
        ready=ready,
        blockers=blockers,
        shape_kind="linear_member",
    )


def _plate(
    result: AnalysisResult,
    *,
    name: str,
    a: float,
    b: float,
    thickness: float,
    quantity: int,
    material: str,
    component_id: str,
    drawing: str,
    revision: str,
    hole: dict | None = None,
    role: str = ComponentRole.GENERIC_PLATE.value,
    parameters: dict | None = None,
    ready: bool = True,
    blockers: list[str] | None = None,
    shape_kind: str = "rectangular_plate",
) -> None:
    hole = hole or {}
    add_plate_entry(
        result,
        a,
        b,
        thickness,
        name,
        material=material,
        plate_qty=quantity,
        bolt_switch=bool(hole),
        bolt_x=float(hole.get("pitch_x", 0)),
        bolt_y=float(hole.get("pitch_y", 0)),
        bolt_hole=float(hole.get("diameter", 0)),
        bolt_size=str(hole.get("fastener", "")),
        plate_role=role,
        notes_zh=f"{a:g}×{b:g}×{thickness:g}t，數量 {quantity}",
        shape_kind=shape_kind,
    )
    entry = result.entries[-1]
    if entry.geometry.holes is not None:
        entry.geometry.holes.count = int(hole.get("count", 4))
        entry.geometry.holes.pattern = str(hole.get("pattern", "rect"))
    _decorate(
        entry,
        component_id=component_id,
        drawing=drawing,
        revision=revision,
        parameters={
            "length_mm": a,
            "width_mm": b,
            "thickness_mm": thickness,
            "quantity": quantity,
            "hole_pattern": hole,
            **(parameters or {}),
        },
        ready=ready,
        blockers=blockers,
        shape_kind=shape_kind,
    )


def _hardware(
    result: AnalysisResult,
    *,
    name: str,
    spec: str,
    material: str,
    quantity: int,
    role: str,
    component_id: str,
    drawing: str,
    revision: str,
    note: str = "外購件單重待供應商資料",
) -> None:
    if role == ComponentRole.EXPANSION_BOLT.value:
        weight_kind = "expansion_bolt"
    elif "基礎" in name:
        weight_kind = "foundation_bolt"
    else:
        weight_kind = "machine_bolt_with_nut"
    estimate = estimate_metric_fastener(
        spec,
        kind=weight_kind,
        density_kg_per_mm3=fastener_density_for_material(material),
    )
    unit_weight = float(estimate["unit_weight_kg"]) if estimate else 0.0
    if estimate:
        note = (
            f"理論估重 {unit_weight:.3f} kg/組；"
            "依名義M×L及比例化頭部／螺帽／墊圈幾何，"
            "供應商成品重量確認後應覆蓋"
        )
    add_custom_entry(
        result,
        name,
        spec,
        material,
        quantity,
        unit_weight,
        unit="SET",
        remark=note,
        category="螺栓類" if role != ComponentRole.CLAMP.value else "管夾類",
        role=role,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    if estimate:
        entry.length = float(estimate["nominal_length_mm"])
        entry.density_g_cm3 = float(estimate["density_kg_per_mm3"]) * 1e6
        entry.density_source = "core.fastener_weight.nominal_geometry_estimate"
        entry.density_requires_review = True
    _decorate(
        entry,
        component_id=component_id,
        drawing=drawing,
        revision=revision,
        parameters={
            "spec": spec,
            "quantity": quantity,
            **({"weight_estimate": estimate} if estimate else {}),
        },
        ready=True,
        shape_kind="purchased_component",
    )


def _finalize(
    result: AnalysisResult,
    parsed: dict,
    config: dict,
    *,
    branch: str,
    assembly_dimensions: dict,
    blockers: list[str],
    weight_blockers: list[str],
    bom_ready: bool = True,
) -> AnalysisResult:
    drawing, revision = _drawing(config)
    warnings = list(dict.fromkeys([*blockers, *weight_blockers]))
    result.warnings.extend(item for item in warnings if item not in result.warnings)
    result.meta["fabrication"] = {
        "source_profile": "changchun_des_m15172",
        "source_drawing": drawing,
        "source_file": config["source_file"],
        "source_revision": revision,
        "branch": branch,
        "bom_ready": bool(bom_ready),
        "weight_complete": not weight_blockers,
        "fabrication_ready": not blockers,
        "blockers": list(blockers),
        "weight_blockers": list(weight_blockers),
        "assembly_dimensions": assembly_dimensions,
    }
    result.meta["config_version"] = str(config.get("version") or "?")
    result.meta["config_updated"] = str(config.get("data_updated_at") or "")
    result.evidence.append(
        make_evidence(
            f"{parsed['code'].lower()}_des_m15172",
            assembly_dimensions,
            "visual_transcription",
            source=f"{drawing} / {config['source_file']}",
            confidence=0.98,
            note="逐頁渲染後依圖面尺寸、BOM與稱呼代號轉錄",
        )
    )
    apply_truth_contract(
        result,
        type_id=parsed["code"],
        review_reasons=warnings,
    )
    return result


def calculate_s1(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    pipe = float(parsed["pipe"])
    height = int(parsed["H"])
    if not (config["pipe_min_in"] <= pipe <= config["pipe_max_in"]):
        result.error = f"S1: 管徑必須介於 {config['pipe_min_in']}~{config['pipe_max_in']} 吋"
        return result
    if height <= 0:
        result.error = "S1: H 必須大於 0 mm"
        return result
    row = next(
        (item for item in config["bands"] if pipe <= item["max_size"] + 1e-9),
        None,
    )
    if row is None:
        result.error = f"S1: 找不到 {pipe:g} 吋尺寸列"
        return result
    drawing, revision = _drawing(config)
    _plate(
        result,
        name="管蹄柱",
        a=row["stem_L"],
        b=height,
        thickness=row["stem_t"],
        quantity=1,
        material="A36",
        component_id="DES-M15172-S1-STEM",
        drawing=drawing,
        revision=revision,
        role=ComponentRole.SIDE_PLATE.value,
        parameters={"line_size_in": pipe, "h_rule": "insulation + 25 mm"},
    )
    _plate(
        result,
        name="底板",
        a=row["base_L"],
        b=row["base_W"],
        thickness=row["base_t"],
        quantity=1,
        material="A36",
        component_id="DES-M15172-S1-BASE",
        drawing=drawing,
        revision=revision,
        role=ComponentRole.BASE_PLATE.value,
    )
    if pipe >= config["stiffener_min_size_in"]:
        _plate(
            result,
            name="加強板",
            a=row["stiff_W"],
            b=height,
            thickness=row["stiff_t"],
            quantity=2,
            material="A36",
            component_id="DES-M15172-S1-STIFFENER",
            drawing=drawing,
            revision=revision,
            role=ComponentRole.WING_PLATE.value,
        )

    blockers = [
        "S1與管線的120°接觸曲面／焊接坡口未在DES-M15172給展開座標，平板下料可出圖但組立仍須依實際管外徑放樣"
    ]
    weight_blockers: list[str] = []
    if overrides.get("sus_pipe"):
        od = float(overrides.get("pipe_od_mm") or get_pipe_od(pipe))
        arc = pi * od / 3
        _plate(
            result,
            name="不銹鋼管補強板",
            a=row["reinf_L"],
            b=round(arc, 2),
            thickness=row["reinf_t"],
            quantity=1,
            material="A240-304",
            component_id="DES-M15172-S1-SS-REINFORCEMENT",
            drawing=drawing,
            revision=revision,
            role=ComponentRole.REINFORCEMENT_PAD.value,
            parameters={
                "pipe_od_mm": od,
                "contact_angle_deg": 120,
                "developed_width_formula": "pi * OD / 3",
            },
            ready=False,
            blockers=[
                "補強板彎曲中性層與回彈係數未指定；目前寬度為120°接觸弧幾何值"
            ],
            shape_kind="curved_reinforcement_strip",
        )
    else:
        blockers.append("尚未明確選擇是否為不銹鋼管線；A240-304補強板分支需由列別覆寫 sus_pipe 確認")

    return _finalize(
        result,
        parsed,
        config,
        branch="stiffened" if pipe >= 12 else "standard",
        assembly_dimensions={
            "line_size_in": pipe,
            "H_mm": height,
            "table_row": row,
            "stiffener_applies": pipe >= 12,
            "small_style_applies_through_in": 10,
        },
        blockers=blockers,
        weight_blockers=weight_blockers,
    )


def calculate_fs15(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    serial = str(parsed["serial"])
    row = config["serials"].get(serial)
    if row is None:
        result.error = f"FS15: 序號應為 {sorted(config['serials'])}"
        return result
    height = int(parsed["H"])
    if height <= 0 or height > row["H_max"]:
        result.error = f"FS15: 序號 {serial} 的 H 必須 0 < H <= {row['H_max']} mm"
        return result
    h1 = int(parsed["H1"] or config["default_H1_mm"])
    drawing, revision = _drawing(config)
    joint_blocker = "FS15角鋼轉角的實際接合是現場配切；圖面只給組立H與300臂長，轉角端切仍須加工圖確認"
    _section(
        result,
        section_type="Angle",
        spec=row["section"],
        length=height,
        quantity=1,
        material="A36",
        name="角鋼立柱",
        component_id="DES-M15172-FS15-COLUMN",
        drawing=drawing,
        revision=revision,
        parameters={"support_variant": parsed["variant"]},
        ready=False,
        blockers=[joint_blocker],
    )
    _section(
        result,
        section_type="Angle",
        spec=row["section"],
        length=300,
        quantity=1,
        material="A36",
        name="角鋼頂臂",
        component_id="DES-M15172-FS15-ARM",
        drawing=drawing,
        revision=revision,
        parameters={"pipe_center_from_tip_mm": 100},
        ready=False,
        blockers=[joint_blocker],
    )
    _plate(
        result,
        name="底板",
        a=260,
        b=260,
        thickness=9,
        quantity=1,
        material="A36",
        component_id="DES-M15172-FS15-BASE",
        drawing=drawing,
        revision=revision,
        hole=(
            {}
            if parsed["fix"] == "W"
            else {
                "count": 4,
                "diameter": 19,
                "pitch_x": 190,
                "pitch_y": 190,
                "fastener": row[config["fix_hardware"][parsed["fix"]]["field"]],
            }
        ),
        role=ComponentRole.BASE_PLATE.value,
    )
    if parsed["fix"] != "W":
        hardware = config["fix_hardware"][parsed["fix"]]
        _hardware(
            result,
            name=hardware["name"],
            spec=row[hardware["field"]],
            material=hardware["material"],
            quantity=4,
            role=hardware["role"],
            component_id=f"DES-M15172-FS15-{parsed['fix']}-FASTENER",
            drawing=drawing,
            revision=revision,
        )
    if parsed["fix"] in {"A", "E"}:
        add_reference(
            result,
            name="水泥墩",
            spec=f"CM1A-{h1}H1",
            material="混凝土",
            quantity=1,
            category="其他",
            component_id="DES-M15172-CM1A",
            drawing=drawing,
            revision=revision,
            shape_kind="concrete_pier_reference",
            parameters={"H1_mm": h1},
            blocker="CM1A水泥墩為引用標準件；本批未提供CM1A完整尺寸圖",
        )
    blockers = [joint_blocker]
    if parsed["variant"] == "V":
        pipe = overrides.get("pipe_size")
        add_reference(
            result,
            name="U型螺栓",
            spec=f"UB1-{pipe}\"" if pipe else "UB1-依現場管徑",
            material="",
            quantity=int(overrides.get("ubolt_qty", 1)),
            category="螺栓類",
            component_id="DES-M15172-UB1",
            drawing=drawing,
            revision=revision,
            shape_kind="purchased_u_bolt",
            parameters={"pipe_size_in": pipe, "quantity_rule": "site"},
            blocker="FS15V的UB1數量配合現場需要；本批未提供DES-M15172 UB1成品尺寸／重量",
            manufacturing_type="purchased",
        )
        blockers.append("FS15V需確認管徑與UB1現場數量")
    return _finalize(
        result,
        parsed,
        config,
        branch=f"{parsed['variant']}/{parsed['fix']}",
        assembly_dimensions={
            "serial": int(serial),
            "H_mm": height,
            "H1_mm": h1,
            "arm_mm": 300,
            "base_plate_mm": [260, 260, 9],
            "table_row": row,
        },
        blockers=blockers,
        weight_blockers=["固定螺栓已列理論估重；水泥墩／UB1仍須依實際選用資料確認"],
    )


def calculate_pu5(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    pipe = float(parsed["pipe"])
    length = int(parsed["L"])
    if pipe <= 0 or pipe > 2:
        result.error = "PU5: 僅適用 2 吋（含）以下水平管"
        return result
    if length <= 0:
        result.error = "PU5: L 必須大於 0 mm"
        return result
    drawing, revision = _drawing(config)
    _section(
        result,
        section_type="Angle",
        spec="75*75*9",
        length=length,
        quantity=1,
        material="A36",
        name="托撐角鋼",
        component_id="DES-M15172-PU5-ANGLE",
        drawing=drawing,
        revision=revision,
        parameters={
            "bottom_chamfer_mm": 20,
            "pipe_center_from_bottom_mm": 50,
        },
    )
    m26_row = get_m26_by_line_size(pipe)
    if m26_row is None:
        result.error = f"PU5: 中威 M-26 找不到 {pipe:g} 吋 U-bolt 尺寸列"
        return result
    ubolt_blockers = add_m26_ubolt(
        result,
        row=m26_row,
        drawing=config["ubolt_source_drawing"],
        revision=config.get("ubolt_source_revision", "1"),
        component_prefix="DES-M15172-PU5-CW-M26",
        host_note=(
            f"DES-M15172 PU5之UB1依本案中威M-26換算為{m26_row['type']}"
        ),
        host_parameters={
            "host_drawing": drawing,
            "line_size_in": pipe,
            "project_alias": f'UB1-{pipe:g}"',
        },
    )
    if parsed["fix"] in {"B", "E"}:
        fastener = config["fix_hardware"][parsed["fix"]]
        _plate(
            result,
            name="底板",
            a=150,
            b=150,
            thickness=6,
            quantity=1,
            material="A36",
            component_id="DES-M15172-PU5-BASE",
            drawing=drawing,
            revision=revision,
            hole={
                "count": 4,
                "diameter": 14,
                "pitch_x": 100,
                "pitch_y": 100,
                "fastener": fastener["spec"],
            },
            role=ComponentRole.BASE_PLATE.value,
        )
        _hardware(
            result,
            name=fastener["name"],
            spec=fastener["spec"],
            material=fastener["material"],
            quantity=4,
            role=fastener["role"],
            component_id=f"DES-M15172-PU5-{parsed['fix']}-FASTENER",
            drawing=drawing,
            revision=revision,
        )
    return _finalize(
        result,
        parsed,
        config,
        branch=parsed["fix"],
        assembly_dimensions={
            "line_size_in": pipe,
            "L_mm": length,
            "section": "L75x75x9",
            "base_plate_mm": [150, 150, 6]
            if parsed["fix"] in {"B", "E"}
            else None,
        },
        blockers=list(ubolt_blockers[:2]),
        weight_blockers=[
            "PU5的M-26螺帽與固定螺栓採理論估重；供應商成品重量待確認"
        ],
    )


def calculate_ss2(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    serial = str(parsed["serial"])
    row = config["serials"].get(serial)
    if row is None:
        result.error = f"SS2: 序號應為 {sorted(config['serials'])}"
        return result
    length = int(parsed["L"])
    if length < config["L_min_mm"]:
        result.error = f"SS2: L 必須至少 {config['L_min_mm']} mm"
        return result
    if not register_source_envelope(
        result,
        type_label="SS2",
        source_ref=config["drawing"],
        checks=[("L", length, config["L_max_mm"], True)],
        review_note=(
            "最大安全荷重只表列 L=300/400/500/600mm，"
            "超界承載力不得外推"
        ),
    ):
        return result
    drawing, revision = _drawing(config)
    _section(
        result,
        section_type="Channel",
        spec=row["section"],
        length=length,
        quantity=1,
        material="A36",
        name="懸臂槽鋼",
        component_id="DES-M15172-SS2-CHANNEL",
        drawing=drawing,
        revision=revision,
        parameters={"free_end_chamfer_mm": 20},
        weight_kg_m=row.get("weight_kg_m"),
    )
    fix = parsed["fix"]
    fastener = row[fix]
    extra = 50 if fix == "B" else 60
    hole_dia = row["d_B"] if fix == "B" else row["d_E"]
    _plate(
        result,
        name="底板",
        a=row["a"] + extra,
        b=row["b"] + extra,
        thickness=9,
        quantity=1,
        material="A36",
        component_id="DES-M15172-SS2-BASE",
        drawing=drawing,
        revision=revision,
        hole={
            "count": 4,
            "diameter": hole_dia,
            "pitch_x": row["a"],
            "pitch_y": row["b"],
            "fastener": fastener,
        },
        role=ComponentRole.BASE_PLATE.value,
        parameters={"edge_allowance_mm": extra / 2},
    )
    _hardware(
        result,
        name="螺栓連帽" if fix == "B" else "擴展螺栓",
        spec=fastener,
        material="A307 Gr.B 鍍鋅" if fix == "B" else "",
        quantity=4,
        role=(
            ComponentRole.MACHINE_BOLT.value
            if fix == "B"
            else ComponentRole.EXPANSION_BOLT.value
        ),
        component_id=f"DES-M15172-SS2-{fix}-FASTENER",
        drawing=drawing,
        revision=revision,
    )
    return _finalize(
        result,
        parsed,
        config,
        branch=fix,
        assembly_dimensions={
            "serial": int(serial),
            "L_mm": length,
            "line_size_max_in": 12,
            "table_row": row,
            "safe_load_status": (
                "not_extrapolated"
                if result.meta.get("source_envelope")
                else "drawing_table_only"
            ),
            "plate_outer_mm": [row["a"] + extra, row["b"] + extra, 9],
        },
        blockers=[],
        weight_blockers=["固定螺栓已列理論估重；供應商成品重量待確認"],
    )


def _calculate_ss_frame(
    parsed: dict,
    config: dict,
    overrides: dict,
    *,
    top_frame: bool,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    code = parsed["code"]
    serial = str(parsed["serial"])
    row = config["serials"].get(serial)
    if row is None:
        result.error = f"{code}: 序號應為 {sorted(config['serials'])}"
        return result
    height = int(parsed["H"])
    span = int(parsed["L"])
    if height <= 0 or span <= 0:
        result.error = f"{code}: H、L 必須大於 0 mm"
        return result
    if not register_source_envelope(
        result,
        type_label=code,
        source_ref=config["drawing"],
        checks=[
            ("H", height, config["H_max_mm"], True),
            ("L", span, config["L_max_mm"], True),
        ],
        review_note=(
            "最大安全負荷只表列 L=300/500/700/900/1100/1300mm，"
            "且圖面 H 上限為 600mm；超界承載力不得外推"
        ),
    ):
        return result
    drawing, revision = _drawing(config)
    corner = (
        f"{code}角鋼框架的H/L為組立尺寸；轉角斜切、焊接收縮與實際端切"
        "仍須加工圖確認"
    )
    horizontal_name = "頂部水平角鋼" if top_frame else "底部水平角鋼"
    _section(
        result,
        section_type="Angle",
        spec=row["section"],
        length=span,
        quantity=1,
        material="A36",
        name=horizontal_name,
        component_id=f"DES-M15172-{code}-HORIZONTAL",
        drawing=drawing,
        revision=revision,
        ready=False,
        blockers=[corner],
        parameters={"assembly_span_L_mm": span},
    )
    _section(
        result,
        section_type="Angle",
        spec=row["section"],
        length=height,
        quantity=2,
        material="A36",
        name="垂直角鋼",
        component_id=f"DES-M15172-{code}-VERTICALS",
        drawing=drawing,
        revision=revision,
        ready=False,
        blockers=[corner],
        parameters={"assembly_height_H_mm": height},
    )
    if code == "SS5":
        _section(
            result,
            section_type="Round Bar",
            spec="13",
            length=25,
            quantity=2,
            material="A36",
            name="圓棒止擋",
            component_id="DES-M15172-SS5-ROUND-STOPS",
            drawing=drawing,
            revision=revision,
            parameters={
                "diameter_mm": 13,
                "projection_mm": 25,
                "end_offset_mm": 20,
            },
            weight_kg_m=1.04,
        )
    fix = parsed["fix"]
    if fix in {"B", "E"}:
        fastener = row[fix]
        _plate(
            result,
            name="底板",
            a=row["c"],
            b=row["b"],
            thickness=9,
            quantity=2,
            material="A36",
            component_id=f"DES-M15172-{code}-BASE-PLATES",
            drawing=drawing,
            revision=revision,
            hole={
                "count": 2,
                "diameter": row["hole_dia"],
                "pitch_x": 0,
                "pitch_y": row["b"] - 2 * row["a"],
                "fastener": fastener,
            },
            role=ComponentRole.BASE_PLATE.value,
            parameters={"hole_edge_mm": row["a"], "one_hole_column": True},
        )
        _hardware(
            result,
            name="螺栓連帽" if fix == "B" else "擴展螺栓",
            spec=fastener,
            material="A307-B 鍍鋅" if fix == "B" else "",
            quantity=4,
            role=(
                ComponentRole.MACHINE_BOLT.value
                if fix == "B"
                else ComponentRole.EXPANSION_BOLT.value
            ),
            component_id=f"DES-M15172-{code}-{fix}-FASTENER",
            drawing=drawing,
            revision=revision,
        )
    return _finalize(
        result,
        parsed,
        config,
        branch=fix,
        assembly_dimensions={
            "serial": int(serial),
            "H_mm": height,
            "L_mm": span,
            "table_row": row,
            "safe_load_status": (
                "not_extrapolated"
                if result.meta.get("source_envelope")
                else "drawing_table_only"
            ),
            "frame_members": {"vertical_qty": 2, "horizontal_qty": 1},
        },
        blockers=[corner],
        weight_blockers=["固定螺栓已列理論估重；供應商成品重量待確認"] if fix in {"B", "E"} else [],
    )


def calculate_ss5(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    return _calculate_ss_frame(parsed, config, overrides, top_frame=True)


def calculate_ss6(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    return _calculate_ss_frame(parsed, config, overrides, top_frame=False)


def calculate_ss13(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    length = int(parsed["L"])
    maximum = config["variant_L_max"][parsed["variant"]]
    if length <= 0:
        result.error = f"SS13{parsed['variant']}: L 必須大於 0 mm"
        return result
    if not register_source_envelope(
        result,
        type_label=f"SS13{parsed['variant']}",
        source_ref=config["drawing"],
        checks=[("L", length, maximum, True)],
        review_note="圖示最大支撐重量 220kg 不得套用到超界尺寸",
    ):
        return result
    drawing, revision = _drawing(config)
    _section(
        result,
        section_type="Angle",
        spec="75*75*9",
        length=length,
        quantity=1,
        material="A36",
        name="懸臂角鋼",
        component_id="DES-M15172-SS13-ANGLE",
        drawing=drawing,
        revision=revision,
        parameters={
            "orientation": parsed["variant"],
            "max_load_kg": (
                None if result.meta.get("source_envelope") else 220
            ),
            "safe_load_status": (
                "not_extrapolated"
                if result.meta.get("source_envelope")
                else "drawing_limit"
            ),
        },
    )
    _plate(
        result,
        name="端部止擋板",
        a=50,
        b=50,
        thickness=3,
        quantity=1,
        material="A283 Gr.C",
        component_id="DES-M15172-SS13-END-STOP",
        drawing=drawing,
        revision=revision,
        role=ComponentRole.STOPPER_PLATE.value,
        parameters={"projection_mm": 25, "joint": "tack weld"},
    )
    if parsed["fix"] == "B":
        _plate(
            result,
            name="底板",
            a=215,
            b=170,
            thickness=9,
            quantity=1,
            material="A283 Gr.C",
            component_id="DES-M15172-SS13-BASE",
            drawing=drawing,
            revision=revision,
            hole={
                "count": 4,
                "diameter": 15,
                "pitch_x": 145,
                "pitch_y": 100,
                "fastener": "M12x50L",
            },
            role=ComponentRole.BASE_PLATE.value,
            parameters={"angle_orientation": parsed["variant"]},
        )
        _hardware(
            result,
            name="螺栓連帽",
            spec="M12x50L",
            material="A307 Gr.B",
            quantity=4,
            role=ComponentRole.MACHINE_BOLT.value,
            component_id="DES-M15172-SS13-B-FASTENER",
            drawing=drawing,
            revision=revision,
        )
    return _finalize(
        result,
        parsed,
        config,
        branch=f"{parsed['variant']}/{parsed['fix']}",
        assembly_dimensions={
            "orientation": parsed["variant"],
            "fix": parsed["fix"],
            "L_mm": length,
            "L_max_mm": maximum,
            "max_load_kg": (
                None if result.meta.get("source_envelope") else 220
            ),
            "safe_load_status": (
                "not_extrapolated"
                if result.meta.get("source_envelope")
                else "drawing_limit"
            ),
        },
        blockers=[],
        weight_blockers=["M12x50螺栓連帽已列理論估重；供應商成品重量待確認"]
        if parsed["fix"] == "B"
        else [],
    )


def calculate_ss17(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    height = int(parsed["H"])
    length = int(parsed["L"])
    if height <= 0 or length <= 0:
        result.error = "SS17: H、L 必須大於 0 mm"
        return result
    if not register_source_envelope(
        result,
        type_label="SS17",
        source_ref=config["drawing"],
        checks=[
            ("H", height, config["H_max_mm"], True),
            ("L", length, config["L_max_mm"], True),
        ],
        review_note="圖示最大支撐重量 1500kg 不得套用到超界尺寸",
    ):
        return result
    drawing, revision = _drawing(config)
    field = "SS17的L與H依圖面需配合現場切割；稱呼代號只能作名目下料，正式加工圖須回填實測完成長"
    _section(
        result,
        section_type="H Beam",
        spec="150*150*7",
        length=height,
        quantity=2,
        material="A36",
        name="H型鋼立柱",
        component_id="DES-M15172-SS17-COLUMNS",
        drawing=drawing,
        revision=revision,
        ready=False,
        blockers=[field],
    )
    _section(
        result,
        section_type="H Beam",
        spec="150*150*7",
        length=length,
        quantity=1,
        material="A36",
        name="H型鋼橫樑",
        component_id="DES-M15172-SS17-BEAM",
        drawing=drawing,
        revision=revision,
        ready=False,
        blockers=[field],
    )
    if parsed["fix"] == "B":
        _plate(
            result,
            name="底板",
            a=290,
            b=195,
            thickness=12,
            quantity=2,
            material="A283 Gr.C",
            component_id="DES-M15172-SS17-BASE-PLATES",
            drawing=drawing,
            revision=revision,
            hole={
                "count": 4,
                "diameter": 19,
                "pitch_x": 185,
                "pitch_y": 125,
                "fastener": "M16x60L",
            },
            role=ComponentRole.BASE_PLATE.value,
        )
        _hardware(
            result,
            name="螺栓連帽",
            spec="M16x60L",
            material="A307 Gr.B",
            quantity=8,
            role=ComponentRole.MACHINE_BOLT.value,
            component_id="DES-M15172-SS17-B-FASTENER",
            drawing=drawing,
            revision=revision,
        )
    return _finalize(
        result,
        parsed,
        config,
        branch=parsed["fix"],
        assembly_dimensions={
            "H_mm": height,
            "L_mm": length,
            "section": "H150x150x7",
            "max_load_kg": (
                None if result.meta.get("source_envelope") else 1500
            ),
            "safe_load_status": (
                "not_extrapolated"
                if result.meta.get("source_envelope")
                else "drawing_limit"
            ),
            "base_plate_mm": [290, 195, 12]
            if parsed["fix"] == "B"
            else None,
        },
        blockers=[field],
        weight_blockers=["M16x60螺栓連帽已列理論估重；供應商成品重量待確認"]
        if parsed["fix"] == "B"
        else [],
    )


def calculate_ss20(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    height = int(parsed["H"])
    length = int(parsed["L"])
    if height <= 0 or length < config["L_min_mm"]:
        result.error = (
            f"SS20: H 必須大於 0，L 必須至少 {config['L_min_mm']} mm"
        )
        return result
    if not register_source_envelope(
        result,
        type_label="SS20",
        source_ref=config["drawing"],
        checks=[
            ("H", height, config["H_max_mm"], True),
            ("L", length, config["L_max_mm"], True),
        ],
    ):
        return result
    drawing, revision = _drawing(config)
    joint = "SS20的H為現場切長，且L/H角鋼轉角接合端切未完全尺寸化；正式加工圖須回填完成長與接合細節"
    _section(
        result,
        section_type="Angle",
        spec="75*75*9",
        length=length,
        quantity=1,
        material="A36",
        name="水平角鋼",
        component_id="DES-M15172-SS20-HORIZONTAL",
        drawing=drawing,
        revision=revision,
        ready=False,
        blockers=[joint],
    )
    _section(
        result,
        section_type="Angle",
        spec="75*75*9",
        length=height,
        quantity=1,
        material="A36",
        name="垂直角鋼",
        component_id="DES-M15172-SS20-VERTICAL",
        drawing=drawing,
        revision=revision,
        ready=False,
        blockers=[joint],
    )
    if parsed["fix"] == "B":
        _plate(
            result,
            name="底板",
            a=215,
            b=170,
            thickness=9,
            quantity=1,
            material="A283 Gr.C",
            component_id="DES-M15172-SS20-BASE",
            drawing=drawing,
            revision=revision,
            hole={
                "count": 4,
                "diameter": 15,
                "pitch_x": 145,
                "pitch_y": 100,
                "fastener": "M12x50L",
            },
            role=ComponentRole.BASE_PLATE.value,
        )
        _hardware(
            result,
            name="螺栓連帽",
            spec="M12x50L",
            material="A307 Gr.B",
            quantity=4,
            role=ComponentRole.MACHINE_BOLT.value,
            component_id="DES-M15172-SS20-B-FASTENER",
            drawing=drawing,
            revision=revision,
        )
    return _finalize(
        result,
        parsed,
        config,
        branch=parsed["fix"],
        assembly_dimensions={
            "H_mm": height,
            "L_mm": length,
            "line_size_max_in": 4,
            "base_plate_mm": [215, 170, 9]
            if parsed["fix"] == "B"
            else None,
        },
        blockers=[joint],
        weight_blockers=["M12x50螺栓連帽已列理論估重；供應商成品重量待確認"]
        if parsed["fix"] == "B"
        else [],
    )


def calculate_s2(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    pipe = float(parsed["pipe"])
    row = next(
        (item for item in config["table"] if abs(item["size"] - pipe) < 1e-9),
        None,
    )
    if row is None:
        result.error = f"S2: DES-M15172沒有 {pipe:g} 吋尺寸列"
        return result
    drawing, revision = _drawing(config)
    variant = parsed["variant"]
    add_reference(
        result,
        name="管夾",
        spec=f"CL3-{pipe:g}\"",
        material="",
        quantity=2,
        category="管夾類",
        component_id="DES-M15172-S2-CL3",
        drawing=drawing,
        revision=revision,
        shape_kind="pipe_clamp_reference",
        parameters={"line_size_in": pipe, "quantity": 2},
        blocker="S2指定CL3管夾兩組，但本批未提供CL3完整成品尺寸／重量",
        manufacturing_type="purchased",
    )
    plate_blocker = (
        "S2補強板與兩支補強支柱只給A/B/C/D/E組立尺寸，"
        "未給各片完整輪廓／折彎展開，禁止以外包矩形代算"
    )
    add_reference(
        result,
        name="補強板",
        spec=f"A{row['A']} B{row['B']} C{row['C']} D{row['D']} E{row['E']}",
        material="A36",
        quantity=1,
        category="鋼板類",
        component_id="DES-M15172-S2-REINFORCEMENT-PLATE",
        drawing=drawing,
        revision=revision,
        shape_kind="formed_reinforcement_plate",
        parameters=row,
        blocker=plate_blocker,
        manufacturing_type="plate_cut",
    )
    add_reference(
        result,
        name="補強支柱",
        spec=f"A{row['A']} B{row['B']} C{row['C']} D{row['D']} E{row['E']}",
        material="A36",
        quantity=2,
        category="鋼板類",
        component_id="DES-M15172-S2-REINFORCEMENT-POSTS",
        drawing=drawing,
        revision=revision,
        shape_kind="formed_reinforcement_posts",
        parameters=row,
        blocker=plate_blocker,
        manufacturing_type="plate_cut",
    )
    if variant in {"A", "G"}:
        _section(
            result,
            section_type="Angle",
            spec="25*25*3",
            length=100,
            quantity=2,
            material="A36",
            name="上導架",
            component_id="DES-M15172-S2-UPPER-GUIDES",
            drawing=drawing,
            revision=revision,
            weight_kg_m=1.12,
        )
    if variant in {"A", "D"}:
        _section(
            result,
            section_type="Angle",
            spec="50*50*6",
            length=100,
            quantity=2,
            material="A36",
            name="下導架",
            component_id="DES-M15172-S2-LOWER-GUIDES",
            drawing=drawing,
            revision=revision,
        )
    blockers = [plate_blocker, "S2的CL3管夾成品圖尚未提供"]
    return _finalize(
        result,
        parsed,
        config,
        branch=variant,
        assembly_dimensions={
            "variant": variant,
            "line_size_in": pipe,
            "table_row": row,
            "upper_guides": variant in {"A", "G"},
            "lower_guides": variant in {"A", "D"},
            "pvc_liner_2mm": variant == "D",
        },
        blockers=blockers,
        weight_blockers=["CL3與未展開補強板／支柱重量尚未計入"],
        bom_ready=True,
    )


CALCULATORS = {
    "FS15": calculate_fs15,
    "PU5": calculate_pu5,
    "S1": calculate_s1,
    "S2": calculate_s2,
    "SS2": calculate_ss2,
    "SS5": calculate_ss5,
    "SS6": calculate_ss6,
    "SS13": calculate_ss13,
    "SS17": calculate_ss17,
    "SS20": calculate_ss20,
}
