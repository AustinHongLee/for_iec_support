"""Source-backed component resolution for DSP-500-006 cold supports."""

from __future__ import annotations

from copy import deepcopy
import re

from data.cold_support_core_tables import (
    LARGE_PIPE_SIZES,
    SMALL_PIPE_SIZES,
    get_cradle_candidates,
    get_n1_dimensions,
    get_n2_layer_system,
    get_n3_construction,
    get_n4_shield,
    get_n5_material_properties,
    resolve_cradle_designation,
)
from data.cold_restraint_tables import (
    get_n6_component,
    get_n7_by_cradle,
    get_n7a_by_cradle,
    get_n8_by_cradle,
    get_n8a_by_line_size,
)
from data.cold_interface_tables import (
    get_n11_by_size,
    get_n13_component,
    get_n14_component,
    get_n15_by_cradle,
    get_n16_by_cradle,
)
from data.n9_table import get_n9_lower_component
from data.n12_table import get_n12_clip
from data.n12a_table import get_n12a_clip_type3
from data.n27_pu_block_table import get_n27_pu_block
from data.n28_table import get_n28_by_number
from data.pipe_table import get_pipe_od

from ..bolt import add_custom_entry
from ..models import AnalysisResult, HolePattern, set_remark
from ._source_reference import add_reference


def _nested_value(parameters: dict, path: str):
    value = parameters
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def derive_insulation_thickness_mm(
    line_size_in: float,
    radial_dimension_b_mm: float,
) -> float:
    """Apply the host-drawing rule B = OD/2 + insulation + 60."""
    return radial_dimension_b_mm - get_pipe_od(line_size_in) / 2 - 60


def _infer_cradle_length_mm(parameters: dict, binding: dict):
    explicit = binding.get("cradle_length_mm")
    if explicit is not None:
        return explicit
    field = binding.get("cradle_length_field")
    if field:
        return _nested_value(parameters, field)

    code = parameters.get("cradle_length_code")
    for mapping_path in (
        "pipe_group_data.cradle_lengths_mm",
        "cradle_lengths_mm",
    ):
        mapping = _nested_value(parameters, mapping_path)
        if isinstance(mapping, dict) and code in mapping:
            return mapping[code]
    for scalar_path in (
        "pipe_group_data.cradle_length_mm",
        "cradle_length_mm",
    ):
        value = _nested_value(parameters, scalar_path)
        if value is not None:
            return value
    return None


def add_cold_support_core_reference(
    result: AnalysisResult,
    *,
    type_id: str,
    cradle_no: str,
    line_size_in,
    insulation_thickness_mm=None,
    cradle_length_mm=None,
    include_shield: bool = False,
    allow_unlisted_pipe_size: bool = False,
) -> tuple[dict, list[str]]:
    """Resolve N-1~N-5/N-20~N-26 without guessing ambiguous thickness."""
    candidates = get_cradle_candidates(cradle_no, line_size_in)
    n1 = get_n1_dimensions(cradle_no, line_size_in)
    table_pipe_sizes = (*SMALL_PIPE_SIZES, *LARGE_PIPE_SIZES)
    unlisted_host_pipe = (
        allow_unlisted_pipe_size
        and line_size_in not in table_pipe_sizes
        and n1 is not None
    )
    if not candidates and not unlisted_host_pipe:
        raise ValueError(
            f"N-20~N-26 無 {cradle_no}/{line_size_in:g}in 原圖組合"
        )
    selection = (
        resolve_cradle_designation(
            cradle_no,
            line_size_in,
            insulation_thickness_mm=insulation_thickness_mm,
        )
        if candidates
        else {
            "component_id": (
                "N-20~N-23"
                if line_size_in <= 24
                else "N-24~N-26"
            ),
            "engineering_standard": "DSP-500-006",
            "revision": "0",
            "cradle_no": cradle_no,
            "pipe_size_in": line_size_in,
            "insulation_thickness_mm": None,
            "candidate_insulation_thicknesses_mm": [],
            "selection_resolved": False,
            "F_mm": None,
            "H_mm": None,
            "polyurethane_density_kg_m3": (
                160
                if line_size_in <= 6
                else 224
                if line_size_in <= 24
                else 320
            ),
            "lookup_ready": False,
            "weight_ready": False,
            "fabrication_ready": False,
            "fabrication_blockers": [
                "host drawing accepts this nominal pipe size, but N-20~N-26 has no explicit F/H/load row",
                "insulation_thickness_mm cannot resolve a row absent from N-20~N-26",
            ],
        }
    )
    if selection is None:
        allowed = [
            row["insulation_thickness_mm"]
            for row in candidates
        ]
        raise ValueError(
            "insulation_thickness_mm="
            f"{insulation_thickness_mm!r} 與 {cradle_no}/"
            f"{line_size_in:g}in 不符；原圖候選為 {allowed}"
        )

    selected_thickness = selection["insulation_thickness_mm"]
    n2 = (
        get_n2_layer_system(selected_thickness)
        if selected_thickness is not None
        else None
    )
    n3 = (
        get_n3_construction(selected_thickness, cradle_length_mm)
        if selected_thickness is not None
        else {
            "component_id": "N-3",
            "lookup_ready": False,
            "total_insulation_thickness_mm": None,
            "fabrication_blockers": [
                "N-3 layer construction cannot resolve until insulation_thickness_mm selects one N-20~N-26 row"
            ],
        }
    )
    n4 = (
        get_n4_shield(cradle_no, cradle_length_mm)
        if include_shield
        else None
    )
    n5 = get_n5_material_properties(
        selection["polyurethane_density_kg_m3"]
    )
    assert n5 is not None

    resolved = {
        "selection": deepcopy(selection),
        "N-1": deepcopy(n1),
        "N-2": deepcopy(n2),
        "N-3": deepcopy(n3),
        "N-5": deepcopy(n5),
    }
    if n4 is not None:
        resolved["N-4"] = deepcopy(n4)

    blockers = []
    for component in (selection, n1, n2, n3, n4, n5):
        if component:
            blockers.extend(component.get("fabrication_blockers", []))
    blockers = list(dict.fromkeys(blockers))

    component_id = selection["component_id"]
    source_component = (
        component_id
        if component_id and "/" not in component_id
        else "N-20~N-26"
    )
    source_file = {
        "N-20": "N-20-CRADLE NO. OF COLD SUPPORT.1.pdf",
        "N-21": "N-21-CRADLE NO. OF COLD SUPPORT.2.pdf",
        "N-22": "N-22-CRADLE NO. OF COLD SUPPORT.3.pdf",
        "N-23": "N-23-CRADLE NO. OF COLD SUPPORT.4.pdf",
        "N-24": "N-24-CRADLE NO. OF COLD SUPPORT.5.pdf",
        "N-25": "N-25-CRADLE NO. OF COLD SUPPORT.6.pdf",
        "N-26": "N-26-CRADLE NO. OF COLD SUPPORT.7.pdf",
    }.get(component_id)
    source_drawing = (
        f"python_app/assets/Type/{source_file}"
        if source_file
        else "python_app/assets/Type/N-20-CRADLE NO. OF COLD SUPPORT.1.pdf"
    )
    thickness_spec = (
        f"{selected_thickness}t"
        if selected_thickness is not None
        else "INSULATION AMBIGUOUS"
    )
    f_h_spec = (
        f"F={selection['F_mm']}; H={selection['H_mm']}"
        if selection.get("F_mm") is not None
        else "F/H UNRESOLVED"
    )
    add_reference(
        result,
        name="COLD SUPPORT CORE LOOKUP",
        spec=(
            f"{cradle_no}; {line_size_in:g}in; {thickness_spec}; "
            f"{f_h_spec}"
        ),
        material="MULTI-MATERIAL COLD-SUPPORT CORE",
        quantity=1,
        category="冷保溫支撐類",
        component_id=source_component,
        drawing=source_drawing,
        revision="0",
        shape_kind="cold_support_core_lookup",
        parameters={
            "host_type_id": type_id,
            "cradle_length_mm": cradle_length_mm,
            "include_shield": include_shield,
            "resolved_components": deepcopy(resolved),
        },
        blocker="；".join(blockers),
        manufacturing_type="assembly",
    )
    return resolved, blockers


def add_cold_restraint_component(
    result: AnalysisResult,
    *,
    type_id: str,
    component_id: str,
    cradle_no: str | None = None,
    line_size_in=None,
) -> tuple[dict, list[str]]:
    """Add one source-selected N-6/N-7/N-7A/N-8/N-8A component."""
    if component_id == "N-6":
        row = get_n6_component()
    elif component_id == "N-7":
        row = get_n7_by_cradle(cradle_no)
    elif component_id == "N-7A":
        row = get_n7a_by_cradle(cradle_no)
    elif component_id == "N-8":
        row = get_n8_by_cradle(cradle_no)
    elif component_id == "N-8A":
        row = get_n8a_by_line_size(line_size_in)
    else:
        raise ValueError(f"unsupported cold restraint component: {component_id}")

    selection = cradle_no if cradle_no is not None else line_size_in
    if row is None:
        raise ValueError(
            f"{component_id} 無 {selection!r} 原圖列值"
        )

    blockers = list(row["fabrication_blockers"])
    drawing = f"python_app/assets/Type/{row['pdf_file']}"
    if component_id in {"N-7", "N-7A"}:
        rod_weight = row["rod_calculated_weight_kg"]
        add_custom_entry(
            result,
            f"{component_id} SPECIAL U-BOLT ROD",
            (
                f"{row['designation']}; DIA{row['rod_diameter_mm']:g}; "
                f"B={row['B_centerline_mm']}; "
                f"D={row['D_thread_length_mm']}; "
                f"E={row['E_leg_to_bend_center_mm']}; "
                f"DEV={row['rod_developed_length_mm']:.3f}"
            ),
            row["material"],
            1,
            round(rod_weight, 3),
            "PC",
            category="螺栓類",
            item_class="fabricated_hardware",
            manufacturing_type="bend_and_thread",
        )
        rod_entry = result.entries[-1]
        rod_entry.length = row["rod_developed_length_mm"]
        rod_entry.geometry.component_id = f"{component_id}-U-BOLT-ROD"
        rod_entry.geometry.source_drawing = drawing
        rod_entry.geometry.source_revision = row["revision"]
        rod_entry.geometry.shape_kind = "u_bolt_round_bar"
        rod_entry.geometry.shape_spec = (
            f"ROD DIA{row['rod_diameter_mm']:g}; "
            f"CENTERLINE B={row['B_centerline_mm']}; "
            f"E={row['E_leg_to_bend_center_mm']}; "
            f"THREAD D={row['D_thread_length_mm']}"
        )
        rod_entry.geometry.parameters = deepcopy(row)
        rod_entry.geometry.fabrication_ready = False
        rod_entry.geometry.fabrication_blockers = blockers[:2]
        set_remark(
            rod_entry,
            "；".join(blockers[:2]),
        )

        nut_blocker = blockers[1]
        add_reference(
            result,
            name=f"{component_id} FINISHED HEX NUTS",
            spec=(
                f"FOR {row['rod_diameter_in']:g}in ROD; "
                f"QTY{row['finished_hex_nuts_per_set']}"
            ),
            material=row["material"],
            quantity=row["finished_hex_nuts_per_set"],
            category="螺栓類",
            component_id=f"{component_id}-FINISHED-HEX-NUTS",
            drawing=drawing,
            revision=row["revision"],
            shape_kind="purchased_finished_hex_nut",
            parameters={
                "host_type_id": type_id,
                "rod_diameter_in": row["rod_diameter_in"],
                "quantity": row["finished_hex_nuts_per_set"],
            },
            blocker=nut_blocker,
            manufacturing_type="purchased",
        )
    else:
        name = (
            "N-6 SPECIAL BASE PLATE ASSEMBLY"
            if component_id == "N-6"
            else f"{component_id} COLD-SUPPORT STRAP"
        )
        spec = (
            "3in SCH40 PIPE / 3000# COUPLING / DIA150x12 BASE"
            if component_id == "N-6"
            else (
                f"{row['designation']}; R={row['R_mm']}; "
                f"A={row['A_mm']}; B={row['B_hole_pitch_mm']}; "
                f"T={row['thickness_mm']}"
            )
        )
        add_reference(
            result,
            name=name,
            spec=spec,
            material=(
                "MULTI-MATERIAL BASE ASSEMBLY"
                if component_id == "N-6"
                else row["material"]
            ),
            quantity=1,
            category="冷保溫支撐類",
            component_id=component_id,
            drawing=drawing,
            revision=row["revision"],
            shape_kind=(
                "threaded_special_base_assembly"
                if component_id == "N-6"
                else "formed_two_hole_strap"
            ),
            parameters={
                "host_type_id": type_id,
                **deepcopy(row),
            },
            blocker="；".join(blockers),
            manufacturing_type=(
                "assembly"
                if component_id == "N-6"
                else "formed_plate"
            ),
        )
    return deepcopy(row), blockers


def add_n11_expansion_bolt_reference(
    result: AnalysisResult,
    *,
    type_id: str,
    bolt_size,
    quantity: int,
) -> tuple[dict, list[str]]:
    """Add the purchased N-11 bolt selected by an N-9/N-10 row."""
    row = get_n11_by_size(bolt_size)
    if row is None:
        raise ValueError(f"N-11 無 expansion bolt {bolt_size!r} 原圖列值")
    blockers = list(row["fabrication_blockers"])
    add_reference(
        result,
        name="N-11 EXPANSION BOLT",
        spec=(
            f"{row['designation']}; L={row['overall_length_mm']}; "
            f"THREAD={row['thread_length_mm']}; "
            f"R.C. HOLE {row['r_c_hole_diameter_in']}in x "
            f"{row['r_c_hole_depth_mm']}L"
        ),
        material="PURCHASED CINCH BOLT / MATERIAL NOT SPECIFIED",
        quantity=quantity,
        category="螺栓類",
        component_id="N-11",
        drawing="python_app/assets/Type/N-11-EXPANSION BOLT.pdf",
        revision=row["revision"],
        shape_kind="purchased_expansion_bolt",
        parameters={
            "host_type_id": type_id,
            "quantity": quantity,
            **deepcopy(row),
        },
        blocker="；".join(blockers),
        manufacturing_type="purchased",
    )
    return deepcopy(row), blockers


def add_cold_interface_component(
    result: AnalysisResult,
    *,
    type_id: str,
    component_id: str,
    cradle_no: str | None = None,
    host_parameters: dict | None = None,
) -> tuple[dict, list[str]]:
    """Add N-13/N-14 clip or N-15/N-16 U-band source geometry."""
    if component_id == "N-13":
        row = get_n13_component()
    elif component_id == "N-14":
        row = get_n14_component()
    elif component_id == "N-15":
        row = get_n15_by_cradle(cradle_no)
    elif component_id == "N-16":
        row = get_n16_by_cradle(cradle_no)
    else:
        raise ValueError(
            f"unsupported cold interface component: {component_id}"
        )
    if row is None:
        raise ValueError(
            f"{component_id} 無 {cradle_no!r} 原圖列值"
        )

    drawing = f"python_app/assets/Type/{row['pdf_file']}"
    blockers = list(row.get("fabrication_blockers", []))
    if component_id in {"N-13", "N-14"}:
        elevation = row["elevation"]
        add_reference(
            result,
            name=row["name_en"],
            spec=(
                f"{row['designation']}; {row['clip_plate_quantity']} PL; "
                f"{row['plate_thickness_mm']}t; "
                f"{elevation['hole_count_per_plate']}-"
                f"DIA{elevation['hole_diameter_mm']} / PL"
            ),
            material=row["material"],
            quantity=1,
            category="冷保溫支撐類",
            component_id=component_id,
            drawing=drawing,
            revision=row["revision"],
            shape_kind="vessel_vendor_clip_pair",
            parameters={
                "host_type_id": type_id,
                "host_parameters": deepcopy(host_parameters or {}),
                **deepcopy(row),
            },
            blocker="；".join(blockers),
            manufacturing_type="vendor_furnished",
        )
        return deepcopy(row), blockers

    band_weight = (
        row["calculated_weight_kg"]
        if component_id == "N-15"
        else row["band_calculated_weight_kg"]
    )
    add_custom_entry(
        result,
        f"{component_id} U-BAND",
        (
            f"{row['designation']}; "
            f"{row['D_width_mm']}x{row['T_thickness_mm']}; "
            f"RG={row['RG_inside_radius_mm']}; "
            f"DEV={row['developed_length_mm']:.3f}"
        ),
        row["material"],
        1,
        round(band_weight, 3),
        "PC",
        category="冷保溫支撐類",
        item_class="fabricated_part",
        manufacturing_type="rolled_flat_bar",
    )
    band_entry = result.entries[-1]
    band_entry.length = row["developed_length_mm"]
    band_entry.geometry.component_id = f"{component_id}-U-BAND"
    band_entry.geometry.source_drawing = drawing
    band_entry.geometry.source_revision = row["revision"]
    band_entry.geometry.shape_kind = "semicircular_u_band_flat_bar"
    band_entry.geometry.shape_spec = (
        f"FLAT {row['D_width_mm']}x{row['T_thickness_mm']}; "
        f"INNER R{row['RG_inside_radius_mm']}; "
        f"W={row['W_outside_span_mm']}"
    )
    band_entry.geometry.parameters = deepcopy(row)
    band_fabrication_blockers = list(
        row.get("band_fabrication_blockers", blockers)
    )
    band_entry.geometry.fabrication_ready = row["fabrication_ready"]
    band_entry.geometry.fabrication_blockers = band_fabrication_blockers
    set_remark(
        band_entry,
        (
            "原圖 inner radius / thickness / straight legs 已足以放樣 "
            f"{row['developed_length_mm']:.3f} mm；"
            + "；".join(band_fabrication_blockers)
        ),
    )

    if component_id == "N-16":
        member = row["member_M"]
        member_unit_weight = (
            member["length_each_mm"]
            / 1000
            * member["weight_per_m_kg"]
        )
        add_custom_entry(
            result,
            "N-16 MEMBER M",
            (
                f"{member['spec']} x {member['length_each_mm']}L; "
                f"DIA{member['hole_diameter_J_mm']} HOLES"
            ),
            row["material"],
            member["quantity"],
            round(member_unit_weight, 3),
            "PC",
            category="型鋼類",
            item_class="fabricated_part",
            manufacturing_type="cut_drill_and_weld",
        )
        member_entry = result.entries[-1]
        member_entry.length = member["length_each_mm"]
        member_entry.geometry.component_id = "N-16-MEMBER-M"
        member_entry.geometry.source_drawing = drawing
        member_entry.geometry.source_revision = row["revision"]
        member_entry.geometry.shape_kind = "drilled_member_pair"
        member_entry.geometry.shape_spec = (
            f"{member['quantity']} x {member['spec']} x "
            f"{member['length_each_mm']}L"
        )
        member_entry.geometry.parameters = deepcopy(row)
        member_entry.geometry.fabrication_ready = False
        member_entry.geometry.fabrication_blockers = blockers
        set_remark(member_entry, "；".join(blockers))

        cradle_number = float(str(row["cradle_no"])[2:])
        bolt_quantity = 2 if cradle_number <= 25 else 4
        bolt_quantity_conflict = (
            "N-16 Section V-V depicts two holes per Member M and two "
            "members, while host C-24 says 2 REQ'D (TYP.) and C-25 says "
            "4 REQ'D (TYP.). The host 2/4 quantity is retained as "
            "provisional until owner confirmation."
        )
        blockers.append(bolt_quantity_conflict)
        add_reference(
            result,
            name="N-16 MACHINE BOLTS",
            spec=member["machine_bolt_K"],
            material="MATERIAL / GRADE NOT SPECIFIED",
            quantity=bolt_quantity,
            category="螺栓類",
            component_id="N-16-MACHINE-BOLTS",
            drawing=drawing,
            revision=row["revision"],
            shape_kind="purchased_machine_bolt",
            parameters={
                "host_type_id": type_id,
                "host_drawing_quantity": bolt_quantity,
                "quantity_status": "provisional_host_callout",
                "source_conflict": bolt_quantity_conflict,
                **deepcopy(member),
            },
            blocker=(
                "machine-bolt material/grade, nuts and finished unit "
                f"weights are not specified；{bolt_quantity_conflict}"
            ),
            manufacturing_type="purchased",
        )
    return deepcopy(row), blockers


def add_n27_pu_block_entry(
    result: AnalysisResult,
    block_no,
):
    row = get_n27_pu_block(block_no)
    if not row:
        raise ValueError(f"N-27 無 PU block {block_no!r}")
    add_custom_entry(
        result,
        "PU BLOCK",
        (
            f"{row['block_no']} "
            f"{row['L1_mm']}x{row['W1_mm']}x{row['T1_mm']}"
        ),
        row["material"],
        1,
        row["unit_weight_kg"],
        "PC",
        category="冷保溫支撐類",
        item_class="fabricated_part",
        manufacturing_type="shaped_block",
    )
    entry = result.entries[-1]
    entry.weight_per_unit = row["unit_weight_kg"]
    entry.geometry.component_id = row["component_id"]
    entry.geometry.source_drawing = (
        "python_app/assets/Type/N27-PU BLOCK.pdf"
    )
    entry.geometry.source_revision = row["revision"]
    entry.geometry.shape_kind = (
        "drilled_rectangular_block"
        if row["hole_count"]
        else "rectangular_block"
    )
    entry.geometry.shape_spec = (
        f"{row['block_no']} "
        f"{row['L1_mm']}x{row['W1_mm']}x{row['T1_mm']}"
    )
    if row["hole_count"]:
        x_values = sorted(
            {center["x_mm"] for center in row["hole_centers_mm"]}
        )
        y_values = sorted(
            {center["y_mm"] for center in row["hole_centers_mm"]}
        )
        entry.geometry.holes = HolePattern(
            pattern="rect" if row["hole_count"] == 4 else "linear",
            pitch_x=(
                x_values[-1] - x_values[0]
                if len(x_values) > 1
                else 0
            ),
            pitch_y=(
                y_values[-1] - y_values[0]
                if len(y_values) > 1
                else 0
            ),
            diameter=row["hole_diameter_mm"],
            count=row["hole_count"],
        )
    entry.geometry.parameters = deepcopy(row)
    entry.geometry.fabrication_ready = True
    entry.geometry.fabrication_blockers = []
    set_remark(
        entry,
        "N-27 尺寸、孔位與 320 kg/m³ 密度均已依原圖精算",
    )
    return row


def add_n28_wood_block_entry(
    result: AnalysisResult,
    block_no,
) -> tuple[dict, list[str]]:
    row = get_n28_by_number(block_no)
    if not row:
        raise ValueError(f"N-28 無 wood block {block_no!r}")
    warnings = [
        "N-28 identifies WHITE OAK but supplies no density；"
        f"{row['block_no']} weight remains zero"
    ]
    warnings.extend(row["fabrication_blockers"])
    add_custom_entry(
        result,
        "WOOD BLOCK",
        (
            f"{row['block_no']} "
            f"{row['L1_mm']}x{row['W1_mm']}x{row['T1_mm']}"
        ),
        row["material"],
        1,
        0,
        "PC",
        category="冷保溫支撐類",
        item_class="fabricated_part",
        manufacturing_type="shaped_block",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = row["component_id"]
    entry.geometry.source_drawing = (
        "python_app/assets/Type/N-28-WOOD BLOCK.pdf"
    )
    entry.geometry.source_revision = row["revision"]
    entry.geometry.shape_kind = "drilled_wood_block"
    entry.geometry.shape_spec = (
        f"{row['block_no']} "
        f"{row['L1_mm']}x{row['W1_mm']}x{row['T1_mm']}"
    )
    x_values = sorted(
        {center["x_mm"] for center in row["hole_centers_mm"]}
    )
    y_values = sorted(
        {center["y_mm"] for center in row["hole_centers_mm"]}
    )
    entry.geometry.holes = HolePattern(
        pattern="rect" if row["hole_count"] == 4 else "linear",
        pitch_x=x_values[-1] - x_values[0],
        pitch_y=(
            y_values[-1] - y_values[0]
            if len(y_values) > 1
            else 0
        ),
        diameter=row["hole_diameter_mm"],
        count=row["hole_count"],
    )
    entry.geometry.parameters = deepcopy(row)
    entry.geometry.fabrication_ready = row["fabrication_ready"]
    entry.geometry.fabrication_blockers = list(
        row["fabrication_blockers"]
    )
    set_remark(entry, "；".join(warnings))
    return row, warnings


def add_n9_lower_component_reference(
    result: AnalysisResult,
    *,
    type_id: str,
    lower_type: str,
    supporting_pipe,
) -> tuple[dict, list[str]]:
    row = get_n9_lower_component(
        lower_type,
        supporting_pipe,
        host_type=type_id,
    )
    if not row:
        raise ValueError(
            f"N-9 lower type {lower_type!r} / supporting pipe "
            f"{supporting_pipe!r} 無原圖列值"
        )
    blockers = list(row["fabrication_blockers"])
    n11_row = None
    n11_blockers = []
    if row["lower_type"] in {"B", "E", "G"}:
        n11_row = get_n11_by_size(
            row["dimension_row"]["expansion_bolt_J"]
        )
        if n11_row is None:
            raise ValueError(
                "N-11 無 N-10 指定的 expansion-bolt 尺寸 "
                f"{row['dimension_row']['expansion_bolt_J']!r}"
            )
        row["N-11"] = deepcopy(n11_row)
        n11_blockers = list(n11_row["fabrication_blockers"])
        blockers.extend(n11_blockers)
    elif row["lower_type"] == "J":
        blockers.append(
            "N-9 Type-J Plate b has expansion-bolt holes, but N-11 Note "
            "lists B/E/G/L/M and omits J；hardware source remains unresolved"
        )
    add_reference(
        result,
        name=f"N-9 LOWER COMPONENT TYPE-{row['lower_type']}",
        spec=(
            f"TYPE-{row['lower_type']}; supporting pipe "
            f"{row['supporting_pipe_size_in']:g}in"
        ),
        material="NOT SPECIFIED IN N-9/N-10",
        quantity=1,
        category="冷保溫支撐類",
        component_id="N-9",
        drawing=(
            "python_app/assets/Type/"
            "N-9-LOWER COMPONENT OF BASE COLD SUPPORT.1.pdf"
        ),
        revision=row["revision"],
        shape_kind="cold_lower_component_lookup",
        parameters=deepcopy(row),
        blocker="；".join(blockers),
        manufacturing_type="assembly",
    )
    if n11_row is not None:
        add_n11_expansion_bolt_reference(
            result,
            type_id=type_id,
            bolt_size=n11_row["diameter_in"],
            quantity=4,
        )
    return row, blockers


def add_n12_clip_reference(
    result: AnalysisResult,
    *,
    clip_type: int,
    insulation_thickness_mm,
) -> tuple[dict, list[str]]:
    if clip_type == 3:
        row = get_n12a_clip_type3(insulation_thickness_mm)
        component_id = "N-12A"
        drawing = "python_app/assets/Type/N-12A-VESSEL CLIPS.2.pdf"
    else:
        row = get_n12_clip(clip_type, insulation_thickness_mm)
        component_id = "N-12"
        drawing = "python_app/assets/Type/N-12-VESSEL CLIPS.1.pdf"
    if not row:
        unresolved = {
            "component_id": component_id,
            "clip_type": clip_type,
            "insulation_thickness_mm": insulation_thickness_mm,
            "lookup_ready": False,
        }
        blockers = [
            "N-12A Note 2 requires insulation thickness from 0 through "
            "300 mm to resolve clip A and plate thickness"
        ]
        add_reference(
            result,
            name=f"VESSEL CLIP TYPE {clip_type}",
            spec=f"N-12 CLIP TYPE {clip_type}; INSULATION REQUIRED",
            material="SAME AS CONNECTED VESSEL MATERIAL",
            quantity=1,
            category="冷保溫支撐類",
            component_id=component_id,
            drawing=drawing,
            revision="0",
            shape_kind="vessel_clip_lookup",
            parameters=unresolved,
            blocker="；".join(blockers),
            manufacturing_type="assembly",
        )
        return unresolved, blockers
    blockers = list(row["fabrication_blockers"])
    add_reference(
        result,
        name=f"VESSEL CLIP TYPE {clip_type}",
        spec=(
            f"N-12 CLIP TYPE {clip_type}; A={row['A_mm']}; "
            f"{row['plate_thickness_mm']}t"
        ),
        material="SAME AS CONNECTED VESSEL MATERIAL",
        quantity=1,
        category="冷保溫支撐類",
        component_id=component_id,
        drawing=drawing,
        revision=row["revision"],
        shape_kind="vessel_clip_lookup",
        parameters=deepcopy(row),
        blocker="；".join(blockers),
        manufacturing_type="assembly",
    )
    return row, blockers


def resolve_generic_component_bindings(
    result: AnalysisResult,
    *,
    type_id: str,
    profile: dict,
    parameters: dict,
    overrides: dict | None = None,
) -> list[str]:
    """Resolve declarative source components used by Type 01C~26C."""
    blockers = []
    resolved = {}
    overrides = overrides or {}
    for binding in profile.get("component_bindings", []):
        when = binding.get("when", {})
        if any(
            parameters.get(field) not in (
                expected
                if isinstance(expected, list)
                else [expected]
            )
            for field, expected in when.items()
        ):
            continue
        component_id = binding["component_id"]
        if component_id == "N-9":
            supporting_pipe = (
                binding.get("supporting_pipe")
                or _nested_value(
                    parameters,
                    binding["supporting_pipe_field"],
                )
            )
            row, row_blockers = add_n9_lower_component_reference(
                result,
                type_id=type_id,
                lower_type=parameters["lower_component"],
                supporting_pipe=supporting_pipe,
            )
        elif component_id == "N27-PU BLOCK":
            block_no = (
                binding.get("block_no")
                or _nested_value(
                    parameters,
                    binding["block_no_field"],
                )
            )
            row = add_n27_pu_block_entry(result, block_no)
            row_blockers = []
        elif component_id == "COLD-SUPPORT-CORE":
            cradle_length_mm = _infer_cradle_length_mm(
                parameters,
                binding,
            )
            row, row_blockers = add_cold_support_core_reference(
                result,
                type_id=type_id,
                cradle_no=parameters["cradle_no"],
                line_size_in=parameters["line_size_in"],
                insulation_thickness_mm=overrides.get(
                    "insulation_thickness_mm"
                ),
                cradle_length_mm=cradle_length_mm,
                include_shield=binding.get("include_shield", False),
                allow_unlisted_pipe_size=binding.get(
                    "allow_unlisted_pipe_size",
                    False,
                ),
            )
            selection = row["selection"]
            parameters["cold_support_core"] = deepcopy(row)
            b_formula = (
                _nested_value(parameters, "pipe_group_data.B_formula")
                or parameters.get("dimension_B_formula")
            )
            formula_match = re.fullmatch(
                r"F\s*\+\s*(\d+)",
                str(b_formula or ""),
            )
            if formula_match and selection.get("F_mm") is not None:
                parameters["dimension_B_mm"] = (
                    selection["F_mm"]
                    + int(formula_match.group(1))
                )
        elif component_id in {"N-6", "N-7", "N-7A", "N-8", "N-8A"}:
            row, row_blockers = add_cold_restraint_component(
                result,
                type_id=type_id,
                component_id=component_id,
                cradle_no=parameters.get("cradle_no"),
                line_size_in=parameters.get("line_size_in"),
            )
        elif component_id in {"N-13", "N-14", "N-15", "N-16"}:
            row, row_blockers = add_cold_interface_component(
                result,
                type_id=type_id,
                component_id=component_id,
                cradle_no=parameters.get("cradle_no"),
            )
        else:
            raise ValueError(
                f"unsupported cold component binding: {component_id}"
            )
        resolved[component_id] = deepcopy(row)
        blockers.extend(row_blockers)
    if resolved:
        parameters["resolved_components"] = resolved
    return blockers
