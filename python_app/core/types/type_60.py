"""Type 60 large-bore side-support assemblies (D-71).

Each side of the pipe has one B x D base plate and two wing plates, so the
complete support contains two base plates and four wings.  Figure A wings use
the dimensioned A/B/C/25 profile.  Figure B additionally requires the 45/120
degree pipe-contact cut, which D-71 does not dimension well enough to emit a
net plate or weight.
"""
from __future__ import annotations

from math import sqrt

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence


_MATERIAL = "A283 Gr.C"


def _wing_geometry(row: dict) -> dict[str, float]:
    a = float(row["A"])
    b = float(row["B"])
    c = float(row["C"])
    cut_base = b - c
    cut_height = a - 25
    return {
        "gross_area": a * b,
        "cutout_area": cut_base * cut_height / 2,
        "net_area": a * b - cut_base * cut_height / 2,
        "cut_hypotenuse": sqrt(cut_base**2 + cut_height**2),
    }


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("60", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 60: 尚未建立來源 profile {profile_id}"
        return result

    size = get_lookup_value(get_part(fullstring, 2))
    fig = (get_part(fullstring, 3) or "").upper()
    if fig not in ("A", "B"):
        result.error = "Type 60: FIG僅允許A(保溫管)或B(裸管)"
        return result
    row = config["TYPE60_TABLE"].get(f"{size:g}{fig}")
    if not row:
        result.error = f"Type 60: D-71沒有 {size:g}吋 FIG-{fig} 尺寸列"
        return result

    drawing = profile["drawing"]
    revision = profile["revision"]
    blockers: list[str] = []

    # One rectangular base on each side of the pipe.
    add_plate_entry(
        result,
        row["B"],
        row["D"],
        row["T"],
        "SIDE SUPPORT BASE PLATE",
        material=_MATERIAL,
        plate_qty=2,
        plate_role="base_plate",
    )
    base = result.entries[-1]
    base.geometry.component_id = "D71-SIDE-BASE-PLATES"
    base.geometry.source_drawing = drawing
    base.geometry.source_revision = revision
    base.geometry.shape_kind = "rectangular_plate"
    base.geometry.parameters.update(
        {
            "radial_length_B_mm": row["B"],
            "axial_width_D_mm": row["D"],
            "thickness_mm": row["T"],
            "quantity": 2,
            "gusset_spacing_E_mm": row["E"],
            "edge_offset_F_mm": row["F"],
            "fillet_weld_mm": 6,
        }
    )
    base.geometry.fabrication_ready = True
    set_remark(base, f'左右base plate，B×D×T={row["B"]}×{row["D"]}×{row["T"]}，共2片')

    if fig == "A":
        geom = _wing_geometry(row)
        formula = (
            f'{row["A"]}×{row["B"]}'
            f'-({row["B"]}-{row["C"]})×({row["A"]}-25)/2'
        )
        add_plate_entry(
            result,
            row["A"],
            row["B"],
            row["T"],
            "SIDE SUPPORT WING PLATE",
            material=_MATERIAL,
            plate_qty=4,
            plate_role="side_plate",
            formula=formula,
            notes_zh="A/B/C/25翼形淨面積",
            shape_spec=(
                f'A{row["A"]} x B{row["B"]} x P25 '
                f'x C{row["C"]} x t{row["T"]}'
            ),
            shape_kind="wing",
            gross_area_mm2=geom["gross_area"],
            cutout_area_mm2=geom["cutout_area"],
            net_area_mm2=geom["net_area"],
        )
        wing = result.entries[-1]
        wing.geometry.component_id = "D71-FIG-A-WING-PLATES"
        wing.geometry.source_drawing = drawing
        wing.geometry.source_revision = revision
        wing.geometry.parameters.update(
            {
                "A_mm": row["A"],
                "B_mm": row["B"],
                "C_mm": row["C"],
                "toe_mm": 25,
                "thickness_mm": row["T"],
                "quantity": 4,
                "two_per_side": True,
                "fillet_weld_mm": 6,
            }
        )
        wing.geometry.fabrication_ready = True
        blocker = (
            "FIG-A個別base/wing下料已完整；與NOT FURNISHED D-80/D-80B shoe的最終貼合定位仍須專案shoe尺寸"
        )
        blockers.append(blocker)
    else:
        blocker = (
            "D-71 FIG-B四片wing須依裸管做45°配置及120°接觸切口；"
            "圖面未給可直接展開的切口座標/半徑基準，禁止以A×B外包重量代替"
        )
        add_custom_entry(
            result,
            "SIDE SUPPORT WING PLATE",
            (
                f'A{row["A"]}xB{row["B"]}xC{row["C"]}'
                f'xP25xt{row["T"]} / 45-120 CONTACT'
            ),
            _MATERIAL,
            4,
            0,
            "PC",
            remark=blocker,
            category="鋼板類",
            item_class="primary_structure",
            manufacturing_type="plate_cut",
        )
        wing = result.entries[-1]
        wing.geometry.component_id = "D71-FIG-B-WING-PLATES"
        wing.geometry.source_drawing = drawing
        wing.geometry.source_revision = revision
        wing.geometry.shape_kind = "pipe_contact_wing_plate"
        wing.geometry.parameters = {
            "A_mm": row["A"],
            "B_mm": row["B"],
            "C_mm": row["C"],
            "toe_mm": 25,
            "thickness_mm": row["T"],
            "quantity": 4,
            "two_per_side": True,
            "upper_angle_deg": 45,
            "pipe_contact_angle_deg": 120,
            "fillet_weld_mm": 6,
        }
        wing.geometry.fabrication_ready = False
        wing.geometry.fabrication_blockers = [blocker]
        blockers.append(blocker)

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": revision,
        "branch": f"FIG-{fig}",
        "bom_ready": fig == "A",
        "fabrication_ready": False,
        "blockers": blockers,
        "not_furnished": ["D-80 / D-80B pipe shoe"] if fig == "A" else [],
        "assembly_dimensions": row,
        "base_plate_quantity": 2,
        "wing_plate_quantity": 4,
    }
    result.warnings.extend(blockers)
    result.evidence.append(
        make_evidence(
            "type60_table_row",
            {"line_size": size, "figure": fig, **row},
            "visual_transcription",
            source=drawing,
            confidence=0.98,
        )
    )
    return result
