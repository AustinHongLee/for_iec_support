"""Type 105 field-fit cross-member support (D-114/D-115)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from ._source_reference import add_reference


def _parse_l_figure(token: str) -> tuple[int, str] | None:
    value = token.upper()
    if len(value) < 2 or value[-1] not in "ABCDE" or not value[:-1].isdigit():
        return None
    return int(value[:-1]) * 100, value[-1]


def _add_member_m(
    result: AnalysisResult,
    *,
    row: dict,
    length: int,
    drawing: str,
    revision: str,
):
    member = row["member_m"]
    field_blocker = (
        "D-115 NOTE 1: member length shall be cut to suit in field；"
        "designation L 可列備料重，但 finished cut/端部 fit-up 發圖前需現場確認"
    )
    if member.get("weight_ready", True):
        add_steel_section_entry(
            result,
            member["kind"],
            member["spec"],
            length,
            1,
            "A36/SS400",
        )
        entry = result.entries[-1]
        entry.geometry.component_id = "D114-MEMBER-M"
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = revision
        entry.geometry.shape_kind = "field_fit_cross_member"
        entry.geometry.parameters = {
            "cut_length_mm": length,
            "source_section": member["source_spec"],
            "field_fit": True,
        }
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = [field_blocker]
        set_remark(entry, field_blocker)
    else:
        add_reference(
            result,
            name="MEMBER M",
            spec=f"{member['source_spec']}; L={length}",
            material="A36/SS400",
            quantity=1,
            category="型鋼類",
            component_id="D114-MEMBER-M",
            drawing=drawing,
            revision=revision,
            shape_kind="field_fit_cross_member",
            parameters={
                "cut_length_mm": length,
                "source_section": member["source_spec"],
                "field_fit": True,
            },
            blocker=(
                f"{field_blocker}；且 {member['source_spec']} 尚無核定 kg/m，"
                "不得用相近 H-section 代重"
            ),
            manufacturing_type="raw_cut",
        )
    return field_blocker


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("105", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 105: 尚未建立來源 profile {profile_id}"
        return result
    member_code = (get_part(fullstring, 2) or "").upper()
    parsed = _parse_l_figure(get_part(fullstring, 3) or "")
    if parsed is None:
        result.error = "Type 105 格式應為 105-{MEMBER M}-{L/100}{A|B|C|D|E}"
        return result
    length, figure = parsed
    row = profile["rows"].get(member_code)
    if not row:
        result.error = f"Type 105 / {profile_id}: D-115 未表列 {member_code}"
        return result
    max_l = 3000 if figure in {"D", "E"} else 2000
    if length <= 0 or length > max_l:
        result.error = f"Type 105 FIG-{figure}: L 必須 <= {max_l} mm"
        return result
    if figure in {"C", "E"} and not row.get("member_p"):
        result.error = (
            f"Type 105 / {profile_id}: {member_code} 的 FIG-{figure} "
            "需要 Member P，但 D-115 表列 NONE"
        )
        return result

    drawing = profile["geometry_drawing"]
    revision = profile["revision"]
    blockers = [
        _add_member_m(
            result,
            row=row,
            length=length,
            drawing=drawing,
            revision=revision,
        )
    ]

    if figure == "A":
        member_n = row["member_n"]
        if member_n["kind"] == "Plate":
            add_plate_entry(
                result,
                member_n["length_mm"],
                member_n["width_mm"],
                member_n["thickness_mm"],
                "MEMBER N",
                "A36/SS400",
                shape_spec=member_n["source_spec"],
                shape_kind="end_connection_plate",
            )
        else:
            add_steel_section_entry(
                result,
                member_n["kind"],
                member_n["spec"],
                member_n["length_mm"],
                1,
                "A36/SS400",
            )
        entry = result.entries[-1]
        entry.geometry.component_id = "D115-MEMBER-N"
        entry.geometry.source_drawing = profile["table_drawing"]
        entry.geometry.source_revision = revision
        entry.geometry.shape_kind = "end_connection_member_n"
        entry.geometry.parameters = {
            "source_spec": member_n["source_spec"],
            "cut_length_mm": member_n["length_mm"],
            "figure": figure,
            "weld_mm": 6,
            "weld_sides": 3,
        }
        entry.geometry.fabrication_ready = True
    elif figure in {"C", "E"}:
        member_p = row.get("member_p")
        p_blocker = (
            f"D-114 FIG-{figure} 的 Member P 只給 section {member_p} 與 "
            "300 MAX envelope，沒有 finished vertical cut length；不可用 300 直接算重"
        )
        add_reference(
            result,
            name="MEMBER P",
            spec=f"{member_p}; CUT LENGTH TBD",
            material="A36/SS400",
            quantity=1,
            category="型鋼類",
            component_id="D114-MEMBER-P",
            drawing=drawing,
            revision=revision,
            shape_kind="field_fit_vertical_member_p",
            parameters={
                "figure": figure,
                "source_spec": member_p,
                "maximum_envelope_mm": 300,
                "cut_length_mm": None,
            },
            blocker=p_blocker,
            manufacturing_type="raw_cut",
        )
        blockers.append(p_blocker)

    result.warnings.extend(blockers)
    result.meta["type_id"] = "105"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": f"{drawing} / {profile['table_drawing']}",
        "source_revision": revision,
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {
            "member_code": member_code,
            "L_mm": length,
            "figure": figure,
            "maximum_L_mm": max_l,
        },
    }
    result.evidence.append(
        make_evidence(
            "type105_d114_d115_branch",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=f"{drawing} / {profile['table_drawing']}",
            confidence=0.99,
        )
    )
    return result
