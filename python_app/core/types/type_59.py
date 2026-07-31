"""Type 59 complete source-aware support model (D-70).

The Detail-Z lug is fabricated by this Type.  Figure B also owns the D-68
U-bolt because D-70 does not mark it NOT FURNISHED.  Figure A ownership of
the pipe shoe and its L40 / 6t interface differs by source profile.
"""
from __future__ import annotations

from hashlib import sha1
from math import sqrt

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..issues import add_issue
from ..models import AnalysisResult, set_remark
from ..parser import extract_parts, get_lookup_value, get_part, parse_pipe_size
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.m26_table import get_m26_by_line_size
from data.type59_table import get_type59_dims
from ._m26_common import add_m26_ubolt


_LUG_DISPLAY_NAME = "TYPE 59 翼形角板"
_STANDARD_SIZES = {
    0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5,
    3, 3.5, 4, 5, 6, 8, 10, 12, 14,
}


def _fmt(value) -> str:
    return f"{float(value):g}"


def _dim_token(value) -> str:
    return _fmt(value).replace(".", "p")


def _lug_geometry(dims: dict) -> dict[str, float]:
    a = float(dims["A"])
    b = float(dims["B"])
    c = float(dims["C"])
    cut_base = b - c
    cut_height = a - 25
    return {
        "gross_area": a * b,
        "cut_base": cut_base,
        "cut_height": cut_height,
        "cut_hypotenuse": sqrt(cut_base**2 + cut_height**2),
        "cutout_area": cut_base * cut_height / 2,
        "net_area": a * b - cut_base * cut_height / 2,
    }


def _part_key(dims: dict, thickness: float) -> str:
    return (
        "59_lug_plate_wing"
        f"_a{_dim_token(dims['A'])}"
        f"_b{_dim_token(dims['B'])}"
        "_p25"
        f"_c{_dim_token(dims['C'])}"
        f"_t{_dim_token(thickness)}"
    )


def _stock_id(part_key: str, material: str) -> str:
    digest = sha1(f"{part_key}|material={material}".encode()).hexdigest()[:8].upper()
    return f"PL-{digest}"


def _add_d68_assembly(result, *, profile, size, material_symbol, drawing, revision):
    if profile["d68_kind"] == "m26":
        row = get_m26_by_line_size(size)
        if not row:
            raise ValueError(f"M-26缺少{size:g}吋U-bolt")
        return add_m26_ubolt(
            result,
            row=row,
            drawing=profile["d68_drawing"],
            revision=revision,
            component_prefix="D70-D68-M26",
            host_note="D-70 FIG-B",
            host_parameters={"figure": "B"},
        )
    else:
        d68_profile = load_config("57", strict=True)["source_profiles"]["ctci_20e4588"]
        row = d68_profile["table"].get(f"{size:g}")
        if not row:
            raise ValueError(f"20E D-68缺少{size:g}吋U-bolt")
        spec = row["u_bolt"]
        material = "Stainless Steel" if material_symbol == "(S)" else "Carbon Steel"
        params = {
            "line_size_in": size,
            "rod_size": row["rod"],
            "C_mm": row["C"],
            "hole_diameter_mm": row["H"],
            "finished_hex_nut_quantity": 4,
        }
    add_custom_entry(
        result,
        "D-68 U-BOLT ASSEMBLY",
        spec,
        material,
        1,
        0,
        "SET",
        remark="D-70 FIG-B furnished item；含4只finished hex nuts",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "D70-D68-U-BOLT-ASSEMBLY"
    entry.geometry.source_drawing = profile["d68_drawing"]
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "purchased_fastener"
    entry.geometry.parameters = params
    metric_blocker = (
        "20E D-68只給U-bolt規格、孔距與孔徑，未給腿長/螺紋長/彎曲展開；"
        "組件重量與加工圖皆須供應商資料"
    )
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [metric_blocker]
    set_remark(entry, metric_blocker)
    return [metric_blocker]


def _add_20e_fig_a_interface(result, *, profile, size, drawing, revision):
    if size <= 8:
        add_steel_section_entry(
            result,
            "Angle",
            "40*40*5",
            150,
            material="Carbon Steel (grade per project specification)",
            steel_qty=2,
        )
        entry = result.entries[-1]
        entry.name = "L40 INTERFACE ANGLE"
        entry.geometry.component_id = "D70-20E-L40-INTERFACE"
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = revision
        entry.geometry.shape_kind = "field_cut_stock_section"
        entry.geometry.parameters = {
            "cut_length_mm": 150,
            "quantity": 2,
            "fillet_weld_mm": 5,
            "cut_in_field": True,
        }
        entry.geometry.fabrication_ready = True
        return None

    blocker = (
        "20E D-70 FIG-A 10~14吋畫出2片6t interface plate，但只給40(TYP.)與D配置，"
        "未給完整平面尺寸；不得補成任意矩形重量"
    )
    add_custom_entry(
        result,
        "6t INTERFACE PLATE",
        "D-70 / DIMENSIONS INCOMPLETE",
        "Carbon Steel (grade per project specification)",
        2,
        0,
        "PC",
        remark=blocker,
        category="鋼板類",
        item_class="primary_structure",
        manufacturing_type="plate_cut",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "D70-20E-6T-INTERFACE-PLATES"
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "drawing_defined_plate"
    entry.geometry.parameters = {
        "line_size_in": size,
        "thickness_mm": 6,
        "quantity": 2,
        "shown_width_mm": 40,
    }
    entry.geometry.fabrication_blockers = [blocker]
    return blocker


def calculate(fullstring: str, overrides=None, source_profile=None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("59", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 59: 尚未建立來源 profile {profile_id}"
        return result
    overrides = overrides or {}

    part2 = get_part(fullstring, 2)
    part3 = get_part(fullstring, 3)
    if not part2:
        result.error = "Type 59: 缺少管徑欄位"
        return result
    size_text = parse_pipe_size(part2)
    size = get_lookup_value(part2)
    if size not in _STANDARD_SIZES:
        result.error = f"Type 59: {size:g}吋不是D-70表列標準管徑"
        return result

    fig, material_symbol = extract_parts(part3 or "")
    fig = fig.upper()
    if fig not in ("A", "B"):
        result.error = "Type 59: FIG僅允許A或B"
        return result
    if size < profile["min_size"] or size > 14:
        result.error = f"Type 59 / {profile_id}: 管徑不在來源D-70範圍"
        return result
    if fig == "B" and size > profile["fig_b_max"]:
        result.error = (
            f"Type 59 / {profile_id}: D-70 FIG-B只適用至"
            f'{profile["fig_b_max"]:g}吋'
        )
        return result
    if fig == "A" and material_symbol:
        result.error = "Type 59: D-70 TABLE A材質符號僅用於FIG-B"
        return result

    material_info = profile["material_map"].get(material_symbol)
    if not material_info:
        result.error = f"Type 59 / {profile_id}: D-70不支援材質符號 {material_symbol}"
        return result
    material = material_info["material"]
    dims = get_type59_dims(size_text)
    if not dims:
        result.error = f"Type 59: 管徑 {size:g}吋沒有Detail Z尺寸群組"
        return result

    thickness = dims["T"]
    if material_symbol == "(S)":
        if dims.get("S_T") is None:
            fallback = profile.get("high_risk_stainless_thickness_fallback_mm")
            if fallback is None:
                result.error = (
                    "Type 59: D-70的10~14吋不鏽鋼板厚欄空白，"
                    "此來源未核准替代厚度"
                )
                return result
            fallback_value = float(fallback)
            thickness = (
                int(fallback_value)
                if fallback_value.is_integer()
                else fallback_value
            )
            add_issue(
                result,
                code="TYPE59_STAINLESS_THICKNESS_SUBSTITUTION",
                severity="high",
                message=(
                    f"Type 59 / {profile_id}: D-70的10~14吋不鏽鋼厚度欄空白；"
                    f"依本專案決議暫借碳鋼T={thickness:g}mm作為"
                    f"{material}角板厚度。材料仍為{material}，"
                    "正式BOM／強度確認／下料／加工圖須工程覆核"
                ),
                scope="material_thickness_substitution",
                calculation_allowed=True,
                bom_allowed=False,
                fabrication_allowed=False,
                source=profile["drawing"],
            )
        else:
            thickness = dims["S_T"]

    geom = _lug_geometry(dims)
    formula = (
        f"{_fmt(dims['A'])}×{_fmt(dims['B'])}"
        f" - ({_fmt(dims['B'])}-{_fmt(dims['C'])})"
        f"×({_fmt(dims['A'])}-25)/2"
    )
    qty = dims["plate_qty"]
    add_plate_entry(
        result,
        dims["A"],
        dims["B"],
        thickness,
        _LUG_DISPLAY_NAME,
        material,
        qty,
        plate_role="lug_plate",
        formula=formula,
        notes_zh=f"Detail Z淨面積{_fmt(geom['net_area'])}mm2",
        shape_spec=(
            f"A{_fmt(dims['A'])} x B{_fmt(dims['B'])}"
            f" x P25 x C{_fmt(dims['C'])} x t{_fmt(thickness)}"
        ),
        shape_kind="wing",
        gross_area_mm2=geom["gross_area"],
        cutout_area_mm2=geom["cutout_area"],
        net_area_mm2=geom["net_area"],
    )
    lug = result.entries[-1]
    lug.part_key = _part_key(dims, thickness)
    lug.stock_id = _stock_id(lug.part_key, material)
    lug.geometry.component_id = "D70-DETAIL-Z-LUG"
    lug.geometry.source_drawing = profile["drawing"]
    lug.geometry.source_revision = profile["revision"]
    lug.geometry.parameters.update(
        {
            "A_mm": dims["A"],
            "B_mm": dims["B"],
            "toe_mm": 25,
            "C_mm": dims["C"],
            "D_mm": dims["D"],
            "thickness_mm": thickness,
            "quantity": qty,
            "figure": fig,
        }
    )
    lug.geometry.fabrication_ready = True
    set_remark(
        lug,
        (
            f"Detail Z 翼形角板；淨面積 {formula}"
            f" = {_fmt(geom['net_area'])} mm2"
        ),
        lug.geometry.shape_spec,
    )

    blockers: list[str] = []
    not_furnished: list[str] = []
    referenced: list[str] = []
    if fig == "B":
        try:
            d68_blockers = _add_d68_assembly(
                result,
                profile=profile,
                size=size,
                material_symbol=material_symbol,
                drawing=profile["drawing"],
                revision=profile["revision"],
            )
        except ValueError as exc:
            result.error = f"Type 59: {exc}"
            result.entries.clear()
            return result
        blockers.extend(d68_blockers)
        referenced.append("D-68")
        if profile.get("conditional_d91_pad"):
            pad_decision = overrides.get("reinforcing_pad_required")
            if pad_decision is None:
                blockers.append(
                    "20E D-70 FIG-B註記PAD IF REQ'D SEE D-91；"
                    "須以reinforcing_pad_required明確確認是否需要"
                )
            elif pad_decision:
                blockers.append(
                    "20E D-70要求D-91 pad，但該來源D-91標準範圍為26~42吋，"
                    "與Type 59 FIG-B <=6吋衝突，須工程確認"
                )
                referenced.append("D-91")
    else:
        not_furnished.append(f'{profile["pipe_shoe"]} pipe shoe')
        if profile["fig_a_interface"] == "not_furnished":
            not_furnished.append("L40x40x5x150 interface angles")
        else:
            interface_blocker = _add_20e_fig_a_interface(
                result,
                profile=profile,
                size=size,
                drawing=profile["drawing"],
                revision=profile["revision"],
            )
            if interface_blocker:
                blockers.append(interface_blocker)

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"FIG-{fig}",
        "bom_ready": not blockers,
        "fabrication_ready": not blockers,
        "blockers": blockers,
        "not_furnished": not_furnished,
        "referenced_components": referenced,
        "reinforcing_pad_required": overrides.get("reinforcing_pad_required"),
    }
    result.warnings.extend(blockers)
    result.evidence.append(
        make_evidence(
            "type59_support",
            {
                "size": size,
                "figure": fig,
                "material_symbol": material_symbol,
                "material": material,
                "thickness": thickness,
                **dims,
            },
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
