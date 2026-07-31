"""Type 82 / 82A pipe guide and fixed-stop supports (D-99/D-100A)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from ._source_reference import add_reference


def calculate_family(
    fullstring: str,
    *,
    type_id: str,
    source_profile: str | None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("82", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type {type_id}: 尚未建立來源 profile {profile_id}"
        return result

    size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
    row = config["TYPE82_TABLE"].get(f"{size:g}")
    if not row:
        result.error = f'Type {type_id}: D-{profile["small_detail_no"]} 未表列 {size:g}"'
        return result

    fixed = type_id == "82A"
    prefix = "fixed_" if fixed else ""
    branch_prefix = "large" if row["branch"] == "large" else "small"
    drawing = profile[f"{prefix}{branch_prefix}_drawing"]
    detail_no = profile[f"{prefix}{branch_prefix}_detail_no"]
    blockers: list[str] = []

    guide = row.get("guide_angle")
    if guide:
        add_steel_section_entry(
            result,
            "Angle",
            guide["spec"],
            guide["length_mm"],
            2,
            "A36/SS400",
        )
        angle = result.entries[-1]
        angle.geometry.component_id = f"D{detail_no}-MEMBER-M-GUIDE-ANGLES"
        angle.geometry.source_drawing = drawing
        angle.geometry.source_revision = profile["revision"]
        angle.geometry.shape_kind = (
            "fixed_pipe_stop_angles" if fixed else "pipe_guide_angles"
        )
        angle.geometry.shape_spec = (
            f'L{guide["spec"]}x{guide["length_mm"]}L; QTY2; '
            f'CLEARANCE={0 if fixed else 3}'
        )
        angle.geometry.parameters = {
            "line_size_in": size,
            "quantity": 2,
            "cut_length_mm": guide["length_mm"],
            "pipe_clearance_mm": 0 if fixed else 3,
            "fixed_to_pipe": fixed,
            "fillet_weld_mm": 6,
        }
        angle.geometry.fabrication_ready = True
        set_remark(
            angle,
            (
                "D-100A fixed Member M；兩側 6 mm weld"
                if fixed
                else "D-99 guide Member M；兩側保留 3 mm clearance"
            ),
        )

    member = row["member_c"]
    member_blocker = (
        f"D-{detail_no} 的 Member C / large saddle 由多片板或切割母型鋼形成；"
        "A/B/D/E 是組立控制尺寸，圖面未完整定義各 piece 的淨輪廓、"
        "切割方向與片數，禁止把外框直接算重"
    )
    add_reference(
        result,
        name=(
            "FIXED SUPPORT ASSEMBLY"
            if fixed
            else "GUIDE SUPPORT ASSEMBLY"
        ),
        spec=member["spec"],
        material=member.get("material", "A36/SS400"),
        quantity=1,
        category="鋼板類",
        component_id=f"D{detail_no}-MEMBER-C-ASSEMBLY-REFERENCE",
        drawing=drawing,
        revision=profile["revision"],
        shape_kind=(
            "fixed_multi_piece_support"
            if fixed
            else "guided_multi_piece_support"
        ),
        parameters={
            "line_size_in": size,
            "A_mm": row.get("A"),
            "B_mm": row.get("B"),
            "D_mm": row.get("D"),
            "E_mm": row.get("E"),
            "member_c_source": member["spec"],
            "pipe_contact_angle_deg": row.get("pipe_contact_angle_deg"),
            "reinforcing_pad_reference": row.get("reinforcing_pad_reference"),
            "fixed_to_pipe": fixed,
        },
        blocker=member_blocker,
        manufacturing_type="shaped_plate",
    )
    blockers.append(member_blocker)

    result.warnings.extend(blockers)
    result.meta["type_id"] = type_id
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f"D-{detail_no}",
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {
            "line_size_in": size,
            "fixed_to_pipe": fixed,
            **{key: row.get(key) for key in ("A", "B", "D", "E")},
        },
    }
    result.evidence.append(
        make_evidence(
            f"type{type_id}_dimension_row",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=drawing,
            confidence=0.99,
        )
    )
    return result


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    return calculate_family(
        fullstring,
        type_id="82",
        source_profile=source_profile,
    )
