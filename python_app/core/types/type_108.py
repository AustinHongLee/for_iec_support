"""Type 108 small-line dummy support (D-119/D-120)."""

from __future__ import annotations

from .. import m42
from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import extract_parts, get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


def _parse_height_lower(token: str) -> tuple[int, str] | None:
    value = token.upper()
    if len(value) < 2 or value[-1] not in {"G", "J", "R"}:
        return None
    if not value[:-1].isdigit():
        return None
    return int(value[:-1]) * 100, value[-1]


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("108", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 108: 尚未建立來源 profile {profile_id}"
        return result

    size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
    parsed = _parse_height_lower(get_part(fullstring, 3) or "")
    figure, symbol = extract_parts(get_part(fullstring, 4) or "")
    figure = figure.upper()
    if parsed is None or figure not in {"A", "B", "C"}:
        result.error = (
            "Type 108 格式應為 108-{LINE}B-{H/100}{G|J|R}-{A|B|C}[(A)|(S)]"
        )
        return result
    height, lower_type = parsed
    if symbol not in profile["material_symbols"]:
        result.error = (
            f"Type 108: material symbol {symbol!r} 無效；"
            f"允許 {sorted(profile['material_symbols'])}"
        )
        return result
    candidates = [
        row
        for row in profile["pipe_rows"]
        if size in [float(value) for value in row["line_sizes"]]
        and height <= row["H_max"]
    ]
    requested_b = overrides.get("supporting_pipe_size")
    if requested_b is not None:
        requested_size = get_lookup_value(requested_b)
        candidates = [
            row for row in candidates if float(row["pipe_size"]) == requested_size
        ]
    if not candidates:
        result.error = (
            f'Type 108: line {size:g}" / H={height} / supporting pipe '
            f"{requested_b!r} 不在 D-119 表列"
        )
        return result

    drawing = profile["geometry_drawing"]
    revision = profile["revision"]
    blockers: list[str] = []
    selected = candidates[0] if len(candidates) == 1 else None
    pipe_cut = overrides.get("supporting_pipe_cut_length_mm")
    if selected and pipe_cut:
        add_pipe_entry(
            result,
            selected["pipe_size"],
            selected["schedule"],
            float(pipe_cut),
            "A53 Gr.B",
        )
        pipe = result.entries[-1]
        pipe.geometry.component_id = "D119-SUPPORTING-PIPE-B"
        pipe.geometry.source_drawing = drawing
        pipe.geometry.source_revision = revision
        pipe.geometry.shape_kind = "field_cut_supporting_pipe"
        pipe.geometry.parameters = {
            "line_size_D_in": size,
            "supporting_pipe_B_in": selected["pipe_size"],
            "schedule": selected["schedule"],
            "assembly_H_mm": height,
            "cut_length_mm": float(pipe_cut),
        }
        pipe.geometry.fabrication_ready = False
        pipe_blocker = (
            "supporting pipe cut 已由 override 提供；upper branch fishmouth/"
            "elbow interface 仍需實際 pipe OD 與相貫線模板"
        )
        pipe.geometry.fabrication_blockers = [pipe_blocker]
        blockers.append(pipe_blocker)
    else:
        selection_text = (
            " / ".join(
                f'{row["pipe_size"]}" {row["schedule"]} (HMAX {row["H_max"]})'
                for row in candidates
            )
            if candidates
            else "NONE"
        )
        pipe_blocker = (
            "D-120 NOTE 3 要求現場切配，H 是組立控制高度而非 finished pipe cut；"
            f"可用 supporting pipe 選項：{selection_text}。"
            "若同時有兩個選項，必須明選 supporting_pipe_size"
        )
        add_reference(
            result,
            name="SUPPORTING PIPE B",
            spec=f"{selection_text}; CUT LENGTH TBD",
            material="A53 Gr.B",
            quantity=1,
            category="管路類",
            component_id="D119-SUPPORTING-PIPE-B",
            drawing=drawing,
            revision=revision,
            shape_kind="field_cut_supporting_pipe",
            parameters={
                "line_size_D_in": size,
                "assembly_H_mm": height,
                "candidate_rows": candidates,
                "cut_length_mm": None,
            },
            blocker=pipe_blocker,
            manufacturing_type="raw_cut",
        )
        blockers.append(pipe_blocker)

    plate_blocker = (
        "D-119 的 9t lug plate 與 6t spacer plate 雖有局部厚度/"
        "120x80 envelope，但 pipe cutout、lug 外形與分片方式未完整定義"
    )
    add_reference(
        result,
        name="LUG / SPACER PLATE ASSEMBLY",
        spec="LUG 9t + SPACER 6t; SPACER ENVELOPE 120x80",
        material="MULTI-MATERIAL; SEE D-120 NOTE 1",
        quantity=1,
        category="鋼板類",
        component_id="D119-LUG-SPACER-ASSEMBLY",
        drawing=drawing,
        revision=revision,
        shape_kind="pipe_intersection_lug_spacer_assembly",
        parameters={
            "line_size_D_in": size,
            "figure": figure,
            "lug_thickness_mm": 9,
            "spacer_thickness_mm": 6,
            "spacer_envelope_mm": [120, 80],
            "lug_material": profile["material_symbols"][symbol],
            "spacer_material": "CARBON STEEL GRADE TBD",
        },
        blocker=plate_blocker,
        manufacturing_type="shaped_plate",
    )
    blockers.append(plate_blocker)

    if figure == "C":
        add_plate_entry(
            result,
            210,
            65,
            9,
            "FIG-C FLAT BAR BRACE",
            profile["material_symbols"][symbol],
            shape_spec="FB65x9x210",
            shape_kind="flat_bar_brace",
        )
        brace = result.entries[-1]
        brace.geometry.component_id = "D119-FIG-C-FLAT-BAR"
        brace.geometry.source_drawing = drawing
        brace.geometry.source_revision = revision
        brace.geometry.parameters = {
            "cut_length_mm": 210,
            "width_mm": 65,
            "thickness_mm": 9,
            "figure": "C",
            "weld_mm": 6,
        }
        brace.geometry.fabrication_ready = True

    if selected:
        before = len(result.entries)
        m42.perform_action_by_letter(
            result,
            lower_type,
            selected["pipe_size"],
            source_profile=profile_id,
        )
        for index, entry in enumerate(result.entries[before:], start=1):
            entry.geometry.component_id = (
                entry.geometry.component_id
                or f"D119-M42-{lower_type}-{index}"
            )
            entry.geometry.source_drawing = profile["notes_drawing"]
            entry.geometry.source_revision = revision
    else:
        lower_blocker = (
            "M-42 lower component 尺寸取決於 supporting pipe B；"
            "D-119 有多個可用 B 時必須先明選，不能只由 line size/H 猜"
        )
        add_reference(
            result,
            name="M-42 LOWER COMPONENT",
            spec=f"TYPE-{lower_type}; SUPPORTING PIPE B TBD",
            material="A36/SS400",
            quantity=1,
            category="鋼板類",
            component_id="D119-M42-LOWER-COMPONENT",
            drawing=profile["notes_drawing"],
            revision=revision,
            shape_kind="m42_lower_component_reference",
            parameters={
                "lower_type": lower_type,
                "candidate_rows": candidates,
            },
            blocker=lower_blocker,
        )
        blockers.append(lower_blocker)

    result.warnings.extend(blockers)
    result.meta["type_id"] = "108"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": f"{drawing} / {profile['notes_drawing']}",
        "source_revision": revision,
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {
            "line_size_D_in": size,
            "assembly_H_mm": height,
            "lower_type": lower_type,
            "figure": figure,
            "material_symbol": symbol,
            "supporting_pipe": selected,
        },
    }
    result.evidence.append(
        make_evidence(
            "type108_d119_d120_branch",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=f"{drawing} / {profile['notes_drawing']}",
            confidence=0.99,
        )
    )
    return result
