"""Type 116C three-figure cold-support interface (C-62/C-63)."""

from __future__ import annotations

import re

from ..models import AnalysisResult
from ..parser import get_part
from ._cold_support_common import (
    add_cold_reference,
    finalize_cold_result,
    load_cold_profile,
    parse_pipe_size,
)
from ._cold_component_resolution import (
    add_n12_clip_reference,
    add_n28_wood_block_entry,
    add_cold_interface_component,
    add_cold_restraint_component,
    add_cold_support_core_reference,
)
from ._source_reference import add_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    loaded = load_cold_profile(result, "116C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    cradle_length_code = str(get_part(fullstring, 2) or "").strip().upper()
    cradle_no = str(get_part(fullstring, 3) or "").strip().upper()
    line_size = parse_pipe_size(get_part(fullstring, 4))
    c_figure = str(get_part(fullstring, 5) or "").strip().upper()
    match = re.fullmatch(r"(\d+)([ABC])", c_figure)
    if (
        not re.fullmatch(r"[A-Z]+", cradle_length_code)
        or not re.fullmatch(r"CR\d+(?:\.\d+)?", cradle_no)
        or line_size is None
        or not match
    ):
        result.error = (
            "Type 116C 格式應為 "
            "116C-{CRADLE LENGTH CODE}-{CR#}-{LINE}B-{C mm}{A|B|C}"
        )
        return result
    dim_c = int(match.group(1))
    figure = match.group(2)
    if dim_c <= 0:
        result.error = "Type 116C: C 必須 > 0 mm"
        return result
    figure_data = profile["figures"][figure]

    try:
        cold_core, core_blockers = add_cold_support_core_reference(
            result,
            type_id="116C",
            cradle_no=cradle_no,
            line_size_in=line_size,
            insulation_thickness_mm=(overrides or {}).get(
                "insulation_thickness_mm"
            ),
            allow_unlisted_pipe_size=True,
        )
    except ValueError as exc:
        result.error = f"Type 116C: {exc}"
        result.entries.clear()
        return result

    restraint_blockers = []
    clip_blockers = []
    figure_component_blockers = []
    if figure == "A":
        try:
            restraint, restraint_blockers = add_cold_restraint_component(
                result,
                type_id="116C",
                component_id="N-7",
                cradle_no=cradle_no,
            )
        except ValueError as exc:
            result.error = f"Type 116C: {exc}"
            result.entries.clear()
            return result
        cold_core["N-7"] = restraint
        clip, clip_blockers = add_cold_interface_component(
            result,
            type_id="116C",
            component_id="N-13",
            host_parameters={
                "line_size_in": line_size,
                "C_mm": dim_c,
                "insulation_thickness_mm": cold_core["selection"].get(
                    "insulation_thickness_mm"
                ),
                "B_mm": None,
                "theta_deg": None,
                "vessel_radius_mm": None,
            },
        )
        cold_core["N-13"] = clip
    elif figure == "B":
        selection = cold_core["selection"]
        insulation_thickness_mm = selection.get(
            "insulation_thickness_mm"
        )
        clip, clip_blockers = add_n12_clip_reference(
            result,
            clip_type=1,
            insulation_thickness_mm=insulation_thickness_mm,
        )
        wood, wood_blockers = add_n28_wood_block_entry(result, 1)
        cold_core["N-12"] = clip
        cold_core["N-28"] = [wood]
        figure_component_blockers.extend(wood_blockers)

        bolt_blocker = (
            "C-63 releases A193 Gr.B8 stud-bolt material, size and quantity "
            "but not finished supplier unit weight"
        )
        nut_blocker = (
            "C-63 releases two A194 Gr.8A nuts per stud bolt but not "
            "finished supplier unit weight"
        )
        stud_geometry = {
            "host_type_id": "116C",
            "figure": "B",
            "diameter_in": 0.75,
            "length_mm": 120,
            "quantity": 4,
            "hole_diameter_mm": 22,
            "hole_count": 4,
            "plate_width_mm": 180,
            "horizontal_edge_mm": 40,
            "horizontal_pitch_mm": 100,
            "vertical_edge_mm": 50,
            "vertical_pitch_mm": 200,
        }
        add_reference(
            result,
            name="C-63 STUD BOLT",
            spec='DIA3/4"x120; A193 Gr.B8',
            material="ASTM A193 Gr.B8",
            quantity=4,
            category="螺栓類",
            component_id="C-63-STUD-BOLTS",
            drawing=profile["drawing"],
            revision=profile["revision"],
            shape_kind="purchased_stud_bolt",
            parameters=stud_geometry,
            blocker=bolt_blocker,
            manufacturing_type="purchased",
        )
        add_reference(
            result,
            name="C-63 STUD-BOLT NUT",
            spec="A194 Gr.8A; 2 PER STUD",
            material="ASTM A194 Gr.8A",
            quantity=8,
            category="螺栓類",
            component_id="C-63-STUD-BOLT-NUTS",
            drawing=profile["drawing"],
            revision=profile["revision"],
            shape_kind="purchased_stud_bolt_nut",
            parameters={
                "host_type_id": "116C",
                "figure": "B",
                "quantity": 8,
                "nuts_per_stud": 2,
                "stud_component_id": "C-63-STUD-BOLTS",
            },
            blocker=nut_blocker,
            manufacturing_type="purchased",
        )
        figure_component_blockers.extend([bolt_blocker, nut_blocker])
        selection["source_core_polyurethane_density_kg_m3"] = (
            selection.get("polyurethane_density_kg_m3")
        )
        selection["polyurethane_density_kg_m3"] = 320
        selection["density_override_source"] = (
            "C-63 FIG-B: C-21 detail except polyurethane density 320 kg/m3"
        )

    blockers = [
        "C is an assembly dimension and does not define every finished member cut",
        f"FIG-{figure} references {figure_data['references']}；"
        "component recipes remain incomplete",
        *core_blockers,
        *restraint_blockers,
        *clip_blockers,
        *figure_component_blockers,
    ]
    parameters = {
        "cradle_length_code": cradle_length_code,
        "cradle_no": cradle_no,
        "line_size_in": line_size,
        "C_mm": dim_c,
        "figure": figure,
        "sections": figure_data["sections"],
        "references": figure_data["references"],
        "interface": figure_data["interface"],
        "cradle_length_reference": profile["cradle_length_reference"],
        "cradle_dimension_reference": profile["cradle_dimension_reference"],
        "weld_mm": profile["weld_mm"],
        "figure_B_fastener_geometry": (
            stud_geometry if figure == "B" else None
        ),
        "resolved_components": cold_core,
    }
    add_cold_reference(
        result,
        name=f"C-62/C-63 TYPE 116C FIG-{figure} ASSEMBLY",
        component_id=f"C62-C63-TYPE116C-FIG-{figure}",
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        spec=(
            f"{cradle_length_code}-{cradle_no}; {line_size:g}in; "
            f"C={dim_c}; FIG-{figure}"
        ),
    )
    return finalize_cold_result(
        result,
        type_id="116C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type116c_c62_c63_assembly",
    )
