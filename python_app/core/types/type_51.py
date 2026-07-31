"""Type 51 source-aware pipe saddle support (D-62/D-62A)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..issues import add_issue
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.steel_sections import get_section_details


_MEMBER_MATERIAL = "Carbon Steel (grade per project specification)"


def _size_key(value: float) -> str:
    return f"{value:g}"


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("51", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 51: 尚未建立來源 profile {profile_id}"
        return result
    overrides = overrides or {}
    token = get_part(fullstring, 2)
    size = get_lookup_value(token)
    requested_size = size
    resolved_size = size
    row = config["TYPE51_TABLE"].get(_size_key(resolved_size))
    substitute = profile.get("high_risk_size_substitutions", {}).get(
        _size_key(requested_size)
    )
    if row is None and substitute is not None:
        resolved_size = float(substitute)
        row = config["TYPE51_TABLE"].get(_size_key(resolved_size))
        if row is not None:
            add_issue(
                result,
                code="TYPE51_LINE_SIZE_SUBSTITUTION",
                severity="high",
                message=(
                    f"Type 51 / {profile_id}: {requested_size:g}吋不在D-62表內；"
                    f"依本專案決議暫用{resolved_size:g}吋列計算。"
                    "可顯示暫估BOM，但須工程確認3/4吋鞍座對1/2吋管線的"
                    "間隙、焊接與承載適用性後才可正式下料／出加工圖"
                ),
                scope="source_table_substitution",
                calculation_allowed=True,
                bom_allowed=False,
                fabrication_allowed=False,
                source=" / ".join(profile["drawings"]),
            )
    if not row:
        result.error = f"Type 51 / {profile_id}: 管徑 {token} 不在來源圖範圍"
        return result
    row = dict(row)
    row.update(
        profile.get("member_overrides", {}).get(_size_key(resolved_size), {})
    )
    drawing = " / ".join(profile["drawings"])
    revision = profile["revision"]
    blockers = []
    branch = ""

    if row["member"] is None:
        branch = "FLAT-BAR"
        add_plate_entry(
            result, row["H"], 50, 9, "FLAT BAR",
            material=_MEMBER_MATERIAL, plate_qty=2,
            plate_role="flat_bar",
        )
        entry = result.entries[-1]
        entry.geometry.component_id = "D62-FLAT-BAR"
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = revision
        entry.geometry.shape_kind = "rectangular_plate"
        entry.geometry.parameters = {
            "cut_length_mm": row["H"], "width_mm": 50,
            "thickness_mm": 9, "quantity": 2,
            "pipe_side_gap_mm": 3, "fillet_weld_mm": 6,
        }
        entry.geometry.fabrication_ready = True
        set_remark(entry, f'鞍座, {row["H"]}x50x9, 全焊接(6V), ×2')
    elif row["H"] is not None:
        branch = "ANGLE"
        details = get_section_details(row["member"].split("*")[0])
        if not details:
            result.error = f'Type 51: 型鋼表缺少 {row["member"]}'
            return result
        add_steel_section_entry(
            result, details["type"], details["size"][1:], row["H"],
            steel_qty=2, material=_MEMBER_MATERIAL,
        )
        entry = result.entries[-1]
        entry.geometry.component_id = "D62-MEMBER-M"
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = revision
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.parameters = {
            "cut_length_mm": row["H"], "quantity": 2,
            "pipe_side_gap_mm": 3, "fillet_weld_mm": 6,
        }
        entry.geometry.fabrication_ready = True
        set_remark(entry, f'MEMBER M {row["member"]}，H={row["H"]}mm ×2')
    else:
        branch = "CHANNEL-SADDLE"
        details = get_section_details(row["member"].split("*")[0])
        cut_length = overrides.get("member_cut_length_mm")
        blocker = "D-62A未給channel沿梁方向切長；須輸入member_cut_length_mm（實際梁寬/配置）"
        if not cut_length:
            add_custom_entry(
                result, "MEMBER M", row["member"], _MEMBER_MATERIAL,
                2, 0, "PC", remark=blocker, category="型鋼類",
                item_class="primary_structure", manufacturing_type="raw_cut",
            )
            entry = result.entries[-1]
            blockers.append(blocker)
        elif not details or float(cut_length) <= 0:
            result.error = "Type 51: member_cut_length_mm需為正值且型鋼須存在"
            return result
        else:
            add_steel_section_entry(
                result, details["type"], details["size"][1:], float(cut_length),
                steel_qty=2, material=_MEMBER_MATERIAL,
            )
            entry = result.entries[-1]
        entry.geometry.component_id = "D62A-MEMBER-M"
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = revision
        entry.geometry.shape_kind = "stock_section_with_pipe_contact"
        entry.geometry.parameters = {
            "cut_length_mm": float(cut_length or 0), "quantity": 2,
            "saddle_contact_angle_deg": profile["saddle_angle_deg"],
            "fillet_weld_mm": 6,
        }
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = [
            *( [blocker] if not cut_length else [] ),
            "channel與管線接觸端的cope/貼合輪廓及定位未完整尺寸化",
        ]
        blockers.extend(entry.geometry.fabrication_blockers)

        if profile["reinforcing_pad"] == "included_with_conflict":
            pad_blocker = (
                "中威D-62A畫出80°接觸弧，但其引用的D-91為120°；"
                "來源角度衝突未釐清前不得自動展開reinforcing pad"
            )
            add_custom_entry(
                result,
                "REINFORCING PAD",
                "SEE D-91",
                "Same as main pipe",
                1,
                0,
                "PC",
                remark=pad_blocker,
                category="鋼板類",
                item_class="reference_only",
                manufacturing_type="raw_cut",
            )
            p = result.entries[-1]
            p.geometry.component_id = "D91-REINFORCING-PAD-REFERENCE"
            p.geometry.source_drawing = drawing
            p.geometry.source_revision = revision
            p.geometry.shape_kind = "referenced_standard_component"
            p.geometry.parameters = {
                "d62a_contact_angle_deg": profile["saddle_angle_deg"],
                "d91_pad_angle_deg": 120,
                "d91_axial_length_mm": 400,
                "d91_min_thickness_mm": 12,
            }
            p.geometry.fabrication_blockers = [pad_blocker]
            blockers.append(pad_blocker)

    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": drawing,
        "source_revision": revision, "branch": branch,
        "bom_ready": not any(
            marker in item
            for item in blockers
            for marker in ("未給channel", "來源角度衝突")
        ),
        "fabrication_ready": not blockers, "blockers": list(dict.fromkeys(blockers)),
        "not_furnished": (
            ["D-91 reinforcing pad"] if profile["reinforcing_pad"] == "not_furnished" else []
        ),
    }
    result.warnings.extend(result.meta["fabrication"]["blockers"])
    result.evidence.append(make_evidence(
        "type51_member",
        {
            "requested_line_size": requested_size,
            "resolved_table_line_size": resolved_size,
            **row,
            "saddle_angle_deg": profile["saddle_angle_deg"],
        },
        "visual_transcription", source=drawing, confidence=0.96,
    ))
    return result
