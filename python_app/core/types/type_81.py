"""Type 81/84/86 wrappers around the source-specific D-81 core."""

from __future__ import annotations

from .. import pipe_shoe_engine
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import extract_parts, get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference, retire_entry_weight


def _line_size(fullstring: str) -> float:
    token, _ = extract_parts(get_part(fullstring, 2) or "")
    return get_lookup_value(token)


def _annotate_d81_entries(
    result: AnalysisResult,
    *,
    drawing: str,
    revision: str,
    prefix: str,
) -> list[str]:
    blockers: list[str] = []
    for entry in result.entries:
        if entry.name == "PIPE CLAMP":
            blocker = (
                "M-4 只有 designation/尺寸與載重資料，沒有 finished clamp "
                "source unit-weight；舊集中估重已停用"
            )
            retire_entry_weight(entry, blocker=blocker)
            entry.geometry.component_id = f"{prefix}-D81-M4-PIPE-CLAMP"
            entry.geometry.shape_kind = "purchased_pipe_clamp"
            blockers.append(blocker)
        elif entry.name == "NON-ASBESTOS":
            blocker = (
                "M-47 長寬與 1.5t 可作採購尺寸，但來源未給 gasket material density/"
                "finished unit-weight；重量歸零待供應商"
            )
            retire_entry_weight(entry, blocker=blocker)
            entry.geometry.component_id = f"{prefix}-D81-M47-GASKET"
            entry.geometry.shape_kind = "purchased_non_asbestos_gasket"
            entry.geometry.parameters = {
                "developed_length_mm": entry.length,
                "width_mm": entry.width,
                "thickness_mm": 1.5,
            }
            blockers.append(blocker)
        else:
            field_blocker = (
                "LOPS 依 resting beam width 現場切配；本列備料重量可算，"
                "shop drawing 發行前需回填 field-confirmed cut length"
            )
            entry.geometry.component_id = f"{prefix}-MEMBER-C"
            entry.geometry.shape_kind = "field_cut_h_section"
            entry.geometry.fabrication_ready = False
            entry.geometry.fabrication_blockers = [field_blocker]
            entry.geometry.parameters.update(
                {"cut_length_mm": entry.length, "field_fit": True}
            )
            set_remark(entry, field_blocker)
            blockers.append(field_blocker)
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = revision
    return blockers


def calculate_d81_wrapper(
    fullstring: str,
    *,
    type_id: str,
    source_profile: str | None,
    extra_small_reference: dict | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config(type_id, strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type {type_id}: 尚未建立來源 profile {profile_id}"
        return result

    size = _line_size(fullstring)
    if size in [float(value) for value in profile["small_sizes"]]:
        drawing = profile["small_drawing"]
        try:
            base = pipe_shoe_engine.calculate(
                fullstring,
                "67",
                source_profile=profile_id,
            )
        except ValueError as exc:
            base = AnalysisResult(fullstring=fullstring, error=str(exc))
        if base.error:
            blocker = (
                f"{drawing} 引用 D-81，但此管徑的 D-81 fabricated member／"
                f"完整 clamp-shoe recipe 尚未核定：{base.error}"
            )
            add_reference(
                result,
                name="D-81 CLAMPED PIPE-SHOE ASSEMBLY",
                spec=f'SEE D-81; SIZE={size:g}"',
                material="PER PIPE / PROJECT SPECIFICATION",
                quantity=1,
                category="鋼板類",
                component_id=f"D{profile['small_detail_no']}-D81-ASSEMBLY-REFERENCE",
                drawing=drawing,
                revision=profile["revision"],
                shape_kind="clamped_pipe_shoe_assembly",
                parameters={"line_size_in": size, "source_detail": "D-81"},
                blocker=blocker,
            )
            blockers = [blocker]
        else:
            for entry in base.entries:
                result.add_entry(entry)
            result.warnings.extend(base.warnings)
            result.evidence.extend(base.evidence)
            blockers = _annotate_d81_entries(
                result,
                drawing=drawing,
                revision=profile["revision"],
                prefix=f"D{profile['small_detail_no']}",
            )

        if extra_small_reference:
            extra_blocker = extra_small_reference["blocker"]
            add_reference(
                result,
                name=extra_small_reference["name"],
                spec=extra_small_reference["spec"],
                material=extra_small_reference["material"],
                quantity=extra_small_reference.get("quantity", 1),
                category=extra_small_reference.get("category", "型鋼類"),
                component_id=extra_small_reference["component_id"],
                drawing=drawing,
                revision=profile["revision"],
                shape_kind=extra_small_reference["shape_kind"],
                parameters={
                    "line_size_in": size,
                    **extra_small_reference.get("parameters", {}),
                },
                blocker=extra_blocker,
                manufacturing_type=extra_small_reference.get(
                    "manufacturing_type", "raw_cut"
                ),
            )
            blockers.append(extra_blocker)
        branch = profile["small_detail_no"]
    elif size in [float(value) for value in profile["large_sizes"]]:
        drawing = profile["large_drawing"]
        blocker = (
            f"{drawing} 引用 D-81A 大管 clamp/saddle；No.1~No.10 多片輪廓、"
            "clamp 與 resting-beam interface 尚未形成完整 cutting recipe"
        )
        add_reference(
            result,
            name="D-81A LARGE CLAMPED SADDLE ASSEMBLY",
            spec=f'SEE D-81A; SIZE={size:g}"',
            material="PER PIPE / PROJECT SPECIFICATION",
            quantity=1,
            category="鋼板類",
            component_id=f"D{profile['large_detail_no']}-D81A-ASSEMBLY-REFERENCE",
            drawing=drawing,
            revision=profile["revision"],
            shape_kind="large_clamped_saddle_assembly",
            parameters={"line_size_in": size, "source_detail": "D-81A"},
            blocker=blocker,
        )
        blockers = [blocker]
        branch = profile["large_detail_no"]
    else:
        result.error = (
            f'Type {type_id} / {profile_id}: 來源圖未表列 {size:g}"'
        )
        return result

    result.warnings.extend(item for item in blockers if item not in result.warnings)
    result.meta["type_id"] = type_id
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f"D-{branch}",
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {"line_size_in": size},
    }
    result.evidence.append(
        make_evidence(
            f"type{type_id}_source_branch",
            {"line_size_in": size, "branch": f"D-{branch}"},
            "visual_transcription",
            source=drawing,
            confidence=0.98,
        )
    )
    return result


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    return calculate_d81_wrapper(
        fullstring,
        type_id="81",
        source_profile=source_profile,
    )
