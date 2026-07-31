"""Type 56 drawing-truth model for pipe stops D-67/D-67A.

D-67 gives a trustworthy complete cut only for the <=2-1/2 inch
PL100x100x6 branch.  For larger branches the table selects a parent section
or a fabricated member, but the retained cut path / built-up plate breakdown
is not fully dimensioned.  Those members are therefore emitted as zero-weight
drawing references instead of invented rectangles or full parent-H weights.
"""
from __future__ import annotations

import math

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.type56_table import get_type56_data
from data.type76_table import get_type76_data


_STOP_MATERIAL = "Carbon Steel (grade per project specification)"


def _pipe_od_mm(size: float) -> float | None:
    row = get_type76_data(size)
    return float(row["od_mm"]) if row else None


def _add_unresolved_member(
    result: AnalysisResult,
    *,
    name: str,
    spec: str,
    quantity: int,
    drawing: str,
    revision: str,
    size: float,
    data: dict,
    blocker: str,
):
    add_custom_entry(
        result,
        name,
        spec,
        _STOP_MATERIAL,
        quantity,
        0,
        "PC",
        remark=blocker,
        category="型鋼類",
        item_class="primary_structure",
        manufacturing_type="raw_cut",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = f"D67-{size:g}-MEMBER-C-ASSEMBLY"
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "drawing_defined_fabricated_member"
    entry.geometry.parameters = {
        "line_size_in": size,
        "quantity": quantity,
        "A_mm": data["A"],
        "B_mm": data["B"],
        "parent_or_fabrication": data["C"],
        "D_mm": data["D"],
        "thickness_mm": data["E"],
        "pipe_radius_mm": data["R"],
        "fillet_weld_mm": 6,
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]


def _add_d91_reference(result, *, drawing, revision, size):
    od = _pipe_od_mm(size)
    developed = round(math.pi * od / 3, 1) if od else None
    blocker = (
        "D-67A引用D-91；120°與400mm已知，但pad須由main pipe切取或採同材質且12t MIN，"
        "未確認母管材質/實厚前不計重量亦不得下料"
    )
    add_custom_entry(
        result,
        "REINFORCING PAD",
        "D-91 / 120 DEG / L400 / t>=12",
        "Same as main pipe",
        1,
        0,
        "PC",
        remark=blocker,
        category="鋼板類",
        item_class="reference_only",
        manufacturing_type="raw_cut",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "D67A-D91-REINFORCING-PAD"
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = "rolled_pipe_pad"
    entry.geometry.parameters = {
        "line_size_in": size,
        "pipe_od_mm": od,
        "angle_deg": 120,
        "developed_width_mm": developed,
        "axial_length_mm": 400,
        "minimum_thickness_mm": 12,
        "material_rule": "cut from main pipe or same material plate",
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    return blocker


def calculate(fullstring: str, overrides=None, source_profile=None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("56", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 56: 尚未建立來源 profile {profile_id}"
        return result

    token = get_part(fullstring, 2)
    if not token:
        result.error = "Type 56: 缺少管徑"
        return result
    size = get_lookup_value(token)
    data = get_type56_data(size)
    if not data:
        result.error = f"Type 56: 管徑 {token} ({size}\") 不在D-67/D-67A範圍"
        return result

    drawing = profile["drawings"][0 if size <= 24 else 1]
    revision = profile["revision"]
    blockers: list[str] = []

    if size <= 2.5:
        branch = "PL100"
        add_plate_entry(
            result,
            100,
            100,
            6,
            "PIPE STOP PLATE",
            material=_STOP_MATERIAL,
            plate_qty=2,
            plate_role="generic_plate",
        )
        entry = result.entries[-1]
        entry.geometry.component_id = "D67-PL100-PIPE-STOPS"
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = revision
        entry.geometry.shape_kind = "rectangular_plate"
        entry.geometry.parameters.update(
            {
                "length_mm": 100,
                "width_mm": 100,
                "thickness_mm": 6,
                "quantity": 2,
                "pipe_gap_mm": 3,
                "fillet_weld_mm": 6,
            }
        )
        entry.geometry.fabrication_ready = True
        set_remark(entry, "D-67 PL100x100x6，左右各一，共2片")
    else:
        if size <= 4:
            branch = "PL6-FAB-REFERENCE"
            spec = "MEMBER C / FAB. FROM 6t PLATE"
            blocker = (
                "D-67只給A/B/D/E與FAB FROM 6t；Member C的組焊截面、各片展開尺寸及貼管輪廓未完整標註"
            )
        elif size <= 14:
            branch = "PARENT-H-CUT-REFERENCE"
            spec = f'MEMBER C / {data["C"]}'
            blocker = (
                "D-67只指定CUT FROM母H型鋼；保留部位、切割路徑及可用截面未完整標註，"
                "不得以兩支完整H型鋼重量代替"
            )
        elif size <= 24:
            branch = "PL12-FAB-REFERENCE"
            spec = "MEMBER C / FAB. FROM 12t PLATE"
            blocker = (
                "D-67只給A/B/D/E與FAB FROM 12t；左右Member C的built-up截面及各片展開尺寸未完整標註"
            )
        else:
            branch = "D67A-FAB-REFERENCE"
            spec = "D-67A SUPPORT MEMBER / FAB. FROM 12t PLATE"
            blocker = (
                "D-67A只給A/B/C/D/E/R外形控制尺寸；左右支撐組件的拆片、貼管/鞍座輪廓及組焊定位未完整標註"
            )
        _add_unresolved_member(
            result,
            name="MEMBER C ASSEMBLY",
            spec=spec,
            quantity=2,
            drawing=drawing,
            revision=revision,
            size=size,
            data=data,
            blocker=blocker,
        )
        blockers.append(blocker)
        if size >= 26:
            blockers.append(
                _add_d91_reference(
                    result, drawing=drawing, revision=revision, size=size
                )
            )

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": revision,
        "branch": branch,
        "bom_ready": size <= 2.5,
        "fabrication_ready": size <= 2.5,
        "blockers": blockers,
    }
    result.warnings.extend(blockers)
    result.evidence.append(
        make_evidence(
            "type56_table_row",
            {"line_size": size, **data},
            "visual_transcription",
            source=drawing,
            confidence=0.99,
        )
    )
    return result
