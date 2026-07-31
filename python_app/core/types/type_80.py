"""Type 80 beam-mounted pipe shoe — source-aware D-95/D-96.

For 24-inch and smaller pipe, D-95 explicitly says that the upper shoe detail
comes from D-80.  This implementation reuses the already source-profiled Type
66 D-80 recipe, then adds the D-95 beam interface member.  Large-pipe D-96
assemblies stay blocked until their D-80B shaped plates are decomposed into
net cutting contours.
"""
from __future__ import annotations

from .. import pipe_shoe_engine
from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import extract_parts, get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _parse_size(fullstring: str) -> tuple[float, bool]:
    token, pad = extract_parts(get_part(fullstring, 2) or "")
    return get_lookup_value(token), pad.upper() == "(P)"


def _parse_symbols(fullstring: str) -> tuple[str, str]:
    token, material = extract_parts(get_part(fullstring, 3) or "")
    return token.upper(), material.upper()


def _explicit_dimension(fullstring: str, part: int, override_value) -> float | None:
    if override_value not in (None, ""):
        return float(override_value)
    token = get_part(fullstring, part)
    return float(token) if token and token.isdigit() else None


def _small_row(profile: dict, size: float) -> dict | None:
    for rule in profile["d95_rules"]:
        if size in [float(value) for value in rule["sizes"]]:
            return {
                key: value
                for key, value in rule.items()
                if key != "sizes"
            }
    return None


def _copy_subassembly(target: AnalysisResult, source: AnalysisResult):
    for entry in source.entries:
        target.add_entry(entry)
    target.warnings.extend(source.warnings)
    target.evidence.extend(source.evidence)


def _add_large_reference(
    result: AnalysisResult,
    *,
    profile: dict,
    profile_id: str,
    size: float,
    table_a_symbol: str,
    material_symbol: str,
    hops: float | None,
    lops: float | None,
):
    size_key = f"{size:g}"
    c_mm = profile["d96_c_by_size"].get(size_key)
    if c_mm is None:
        result.error = (
            f'Type 80 / {profile_id}: D-96 未表列 {size:g}"；'
            f"允許 {', '.join(profile['d96_c_by_size'])}\""
        )
        return

    blocker = (
        f"{profile['d96_drawing']} 的主 saddle 尺寸/輪廓引用來源別 D-80B；"
        "No.1 側板含 pipe-contact 斜面/曲線，No.2~No.5 亦非現有矩形 recipe。"
        "在各 piece 淨輪廓完成前，禁止沿用舊版矩形外包 BOM"
    )
    add_custom_entry(
        result,
        "LARGE PIPE SHOE ASSEMBLY",
        f'SEE D-80B / D-96; SIZE={size:g}"; C={c_mm}',
        profile["material_symbols"].get(material_symbol, "MATERIAL TBD"),
        1,
        0,
        "SET",
        remark=blocker,
        category="鋼板類",
        item_class="reference_only",
        manufacturing_type="shaped_plate",
    )
    shoe = result.entries[-1]
    shoe.geometry.component_id = "D96-D80B-LARGE-SHOE-ASSEMBLY"
    shoe.geometry.source_drawing = f"{profile['d96_drawing']} / {profile['d80b_drawing']}"
    shoe.geometry.source_revision = profile["revision"]
    shoe.geometry.shape_kind = "multi_piece_large_pipe_shoe"
    shoe.geometry.shape_spec = (
        f'D96/D80B; SIZE={size:g}; TYPE={table_a_symbol or "A"}; '
        f'HOPS={hops}; LOPS={lops}; C={c_mm}'
    )
    shoe.geometry.parameters = {
        "line_size_in": size,
        "insulation_type_symbol": table_a_symbol,
        "material_symbol": material_symbol,
        "HOPS_mm": hops,
        "LOPS_mm": lops,
        "C_mm": c_mm,
        "pipe_contact_angle_deg": 120,
        "inner_load_angle_deg": 90,
        "source_recipe": "D-80B",
    }
    if profile_id == "cw_e25_24_hp6":
        legacy = load_config("80", strict=True)["TYPE80_BIG_TABLE"].get(f"{size:.1f}")
        if legacy:
            shoe.geometry.parameters["d80b_dimension_row"] = legacy
    shoe.geometry.fabrication_ready = False
    shoe.geometry.fabrication_blockers = [blocker]
    set_remark(shoe, blocker)

    interface_blocker = profile["d96_interface_blocker"]
    add_custom_entry(
        result,
        "D-96 BEAM INTERFACE PARTS",
        profile["d96_interface_spec"],
        profile["material_symbols"].get(material_symbol, "MATERIAL TBD"),
        1,
        0,
        "SET",
        remark=interface_blocker,
        category="鋼板類",
        item_class="reference_only",
        manufacturing_type="plate_cut",
    )
    interface = result.entries[-1]
    interface.geometry.component_id = "D96-BEAM-INTERFACE-PARTS"
    interface.geometry.source_drawing = profile["d96_drawing"]
    interface.geometry.source_revision = profile["revision"]
    interface.geometry.shape_kind = "beam_interface_stop_parts"
    interface.geometry.parameters = {
        "line_size_in": size,
        "C_mm": c_mm,
        "source_profile": profile_id,
        "fireproofing_option": profile.get("fireproofing_option", False),
    }
    interface.geometry.fabrication_ready = False
    interface.geometry.fabrication_blockers = [interface_blocker]
    set_remark(interface, interface_blocker)

    result.warnings.extend([blocker, interface_blocker])
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["d96_drawing"],
        "source_revision": profile["revision"],
        "branch": "D-96",
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": [blocker, interface_blocker],
        "assembly_dimensions": shoe.geometry.parameters,
    }
    result.evidence.append(
        make_evidence(
            "type80_d96_row",
            shoe.geometry.parameters,
            "visual_transcription",
            source=profile["d96_drawing"],
            confidence=0.98,
        )
    )


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("80", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 80: 尚未建立來源 profile {profile_id}"
        return result

    size, pad_required = _parse_size(fullstring)
    table_a_symbol, material_symbol = _parse_symbols(fullstring)
    if table_a_symbol not in {"", "A", "B", "C"}:
        result.error = f"Type 80: D-80A Table A symbol {table_a_symbol!r} 無效"
        return result
    if material_symbol not in profile["material_symbols"]:
        result.error = (
            f"Type 80 / {profile_id}: material symbol {material_symbol!r} 無效；"
            f"允許 {sorted(profile['material_symbols'])}"
        )
        return result

    hops = _explicit_dimension(fullstring, 4, overrides.get("hops_mm"))
    lops = _explicit_dimension(fullstring, 5, overrides.get("lops_mm"))
    if size > 24:
        _add_large_reference(
            result,
            profile=profile,
            profile_id=profile_id,
            size=size,
            table_a_symbol=table_a_symbol,
            material_symbol=material_symbol,
            hops=hops,
            lops=lops,
        )
        return result

    row = _small_row(profile, size)
    if not row:
        result.error = (
            f'Type 80 / {profile_id}: D-95 未表列 {size:g}"；'
            "請依目前來源圖面選擇管徑"
        )
        return result

    # D-95 explicitly delegates the upper pipe-shoe recipe to D-80.  Reusing
    # the Type 66 engine keeps material symbols and source-specific D-80 rules
    # aligned instead of duplicating them here.
    d80 = pipe_shoe_engine.calculate(
        fullstring,
        "66",
        source_profile=profile_id,
    )
    d80_ready = not bool(d80.error)
    if d80.error:
        d80_blocker = f"Type 80 D-95 / D-80 subassembly：{d80.error}"
        add_custom_entry(
            result,
            "D-80 PIPE SHOE SUBASSEMBLY",
            f'SEE {profile["d80b_drawing"]}; SIZE={size:g}"',
            profile["material_symbols"][material_symbol],
            1,
            0,
            "SET",
            remark=d80_blocker,
            category="鋼板類",
            item_class="reference_only",
            manufacturing_type="shaped_plate",
        )
        d80_ref = result.entries[-1]
        d80_ref.geometry.component_id = "D95-D80-SHOE-REFERENCE"
        d80_ref.geometry.source_drawing = profile["d80b_drawing"]
        d80_ref.geometry.source_revision = profile["revision"]
        d80_ref.geometry.shape_kind = "d80_pipe_shoe_subassembly_reference"
        d80_ref.geometry.parameters = {
            "line_size_in": size,
            "HOPS_mm": hops,
            "LOPS_mm": lops,
            "pad_required": pad_required,
        }
        d80_ref.geometry.fabrication_ready = False
        d80_ref.geometry.fabrication_blockers = [d80_blocker]
        set_remark(d80_ref, d80_blocker)
        blockers = [d80_blocker]
    else:
        _copy_subassembly(result, d80)
        for entry in result.entries:
            entry.geometry.parameters.setdefault("parent_type", "80")
            entry.geometry.parameters.setdefault("parent_drawing", profile["d95_drawing"])
        blockers = list(d80.meta.get("fabrication", {}).get("blockers", []))
    member_kind = row["member_kind"]
    member_spec = row["member_spec"]
    if member_kind == "H Beam" and lops is not None:
        add_steel_section_entry(
            result,
            "H Beam",
            member_spec,
            lops,
            1,
            profile["material_symbols"][material_symbol],
        )
        member = result.entries[-1]
        member.geometry.component_id = "D95-BEAM-INTERFACE-MEMBER-C"
        member.geometry.source_drawing = profile["d95_drawing"]
        member.geometry.source_revision = profile["revision"]
        member.geometry.shape_kind = "field_cut_h_section"
        member.geometry.shape_spec = f"CUT FROM {row['full_section_spec']}; LOPS={lops:g}"
        member.geometry.parameters = {
            "line_size_in": size,
            "A_mm": row["A"],
            "B_mm": row["B"],
            "D_mm": row.get("D"),
            "E_mm": row.get("E"),
            "raw_section": row["full_section_spec"],
            "cut_length_mm": lops,
            "HOPS_mm": hops,
            "LOPS_mm": lops,
            "field_fit": True,
        }
        field_blocker = (
            "D-95 NOTE 2：LOPS 應配合 resting beam width 於現場切配；"
            "本列重量採編號明示 LOPS，shop drawing 發行前仍須現場確認"
        )
        member.geometry.fabrication_ready = False
        member.geometry.fabrication_blockers = [field_blocker]
        set_remark(member, field_blocker)
        blockers.append(field_blocker)
    elif member_kind == "H Beam":
        length_blocker = (
            "D-95 member C 為 H-section，但 designation 未明示 LOPS；"
            "LOPS 須配合 beam width in field，禁止套預設長度"
        )
        add_custom_entry(
            result,
            "MEMBER C",
            f"CUT FROM {row['full_section_spec']}; LOPS TBD",
            profile["material_symbols"][material_symbol],
            1,
            0,
            "PC",
            remark=length_blocker,
            category="型鋼類",
            item_class="reference_only",
            manufacturing_type="raw_cut",
        )
        member = result.entries[-1]
        member.geometry.component_id = "D95-BEAM-INTERFACE-MEMBER-C"
        member.geometry.source_drawing = profile["d95_drawing"]
        member.geometry.source_revision = profile["revision"]
        member.geometry.shape_kind = "field_cut_h_section"
        member.geometry.parameters = {
            "raw_section": row["full_section_spec"],
            "LOPS_mm": None,
        }
        member.geometry.fabrication_ready = False
        member.geometry.fabrication_blockers = [length_blocker]
        blockers.append(length_blocker)
    else:
        fabricated_blocker = (
            f'D-95 對 {size:g}" 指定 member C FAB. FROM 12t PLATE，'
            "但 D/E stiffener 與主板的完整片數/輪廓未形成可算 cutting recipe；"
            "舊版單一 LOPS×B×12 板已移除"
        )
        add_custom_entry(
            result,
            "FABRICATED MEMBER C",
            (
                f'12t PLATE ASSEMBLY; A={row["A"]}; B={row["B"]}; '
                f'D={row["D"]}; E={row["E"]}; LOPS={lops}'
            ),
            profile["material_symbols"][material_symbol],
            1,
            0,
            "SET",
            remark=fabricated_blocker,
            category="鋼板類",
            item_class="reference_only",
            manufacturing_type="plate_cut",
        )
        member = result.entries[-1]
        member.geometry.component_id = "D95-FABRICATED-MEMBER-C"
        member.geometry.source_drawing = profile["d95_drawing"]
        member.geometry.source_revision = profile["revision"]
        member.geometry.shape_kind = "multi_piece_beam_interface_member"
        member.geometry.parameters = {
            "line_size_in": size,
            "A_mm": row["A"],
            "B_mm": row["B"],
            "D_mm": row["D"],
            "E_mm": row["E"],
            "plate_thickness_mm": 12,
            "HOPS_mm": hops,
            "LOPS_mm": lops,
        }
        member.geometry.fabrication_ready = False
        member.geometry.fabrication_blockers = [fabricated_blocker]
        blockers.append(fabricated_blocker)

    if profile.get("fireproofing_option"):
        fireproofing_note = (
            "此來源 D-95 含 fireproofing beam 選配與 10t axial-stop plate；"
            "designation/overrides 未明示 beam fireproofing 尺寸時不自動加入"
        )
        result.warnings.append(fireproofing_note)
        blockers.append(fireproofing_note)
    result.warnings.extend(
        blocker for blocker in blockers if blocker not in result.warnings
    )
    result.meta["type_id"] = "80"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["d95_drawing"],
        "source_revision": profile["revision"],
        "branch": "D-95",
        "bom_ready": (
            lops is not None
            and member_kind == "H Beam"
            and d80_ready
            and bool(d80.meta.get("fabrication", {}).get("bom_ready", True))
        ),
        "fabrication_ready": False,
        "blockers": blockers,
        "d80_subassembly": d80.meta.get("fabrication", {}),
        "assembly_dimensions": {
            "line_size_in": size,
            "pad_required": pad_required,
            "table_a_symbol": table_a_symbol,
            "material_symbol": material_symbol,
            "HOPS_mm": hops,
            "LOPS_mm": lops,
            **row,
        },
    }
    result.evidence.append(
        make_evidence(
            "type80_d95_row",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=profile["d95_drawing"],
            confidence=0.99,
        )
    )
    return result
