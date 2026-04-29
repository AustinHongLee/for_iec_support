"""
Type 62 hanger combination table (D-75/D-76).

The source PDF has no extractable text layer.  The table below is transcribed
from the rendered vector drawing:

- page 1: upper/lower part sketches and component callouts
- page 2: TYPE / M-NO. / GRINNELL FIG. NO. / range / temperature table

This table intentionally stores selection metadata only.  Weight precision still
depends on each M-series component table.
"""
from __future__ import annotations

from copy import deepcopy

from .component_size_utils import normalize_fractional_size, size_to_float


TYPE62_UPPER_FIGS = {"A", "C", "D"}
TYPE62_LOWER_FIGS = {"E", "G", "H", "J", "K", "L", "M", "N", "Q"}

TYPE62_PART_TABLE = {
    "A": {
        "role": "upper",
        "component_id": "M-31",
        "component_name": "STEEL WASHER PLATE",
        "grinnell_fig_no": "60",
        "pipe_size_min": None,
        "pipe_size_max": None,
        "max_temp_f": None,
        "max_insulation_thk_in": None,
        "remarks": "",
        "component_table_ready": False,
    },
    "C": {
        "role": "upper",
        "component_id": "M-28",
        "component_name": "BEAM ATTACHMENT A",
        "grinnell_fig_no": "66",
        "pipe_size_min": None,
        "pipe_size_max": None,
        "max_temp_f": 750,
        "max_insulation_thk_in": None,
        "remarks": "",
        "component_table_ready": True,
    },
    "D": {
        "role": "upper",
        "component_id": "M-28",
        "component_name": "BEAM ATTACHMENT A",
        "grinnell_fig_no": "66",
        "pipe_size_min": None,
        "pipe_size_max": None,
        "max_temp_f": 750,
        "max_insulation_thk_in": None,
        "remarks": "",
        "component_table_ready": True,
    },
    "E": {
        "role": "lower",
        "component_id": "M-3",
        "component_name": "ADJUSTABLE CLEVIS",
        "grinnell_fig_no": "260",
        "pipe_size_min": 0.5,
        "pipe_size_max": 30.0,
        "max_temp_f": 650,
        "max_insulation_thk_in": None,
        "remarks": "",
        "component_table_ready": False,
    },
    "G": {
        "role": "lower",
        "component_id": "M-4",
        "component_name": "PIPE CLAMP TYPE-A",
        "grinnell_fig_no": "212",
        "pipe_size_min": 0.5,
        "pipe_size_max": 24.0,
        "max_temp_f": 750,
        "max_insulation_thk_in": None,
        "remarks": "",
        "component_table_ready": True,
    },
    "H": {
        "role": "lower",
        "component_id": "M-5",
        "component_name": "PIPE CLAMP TYPE-B",
        "grinnell_fig_no": "216",
        "pipe_size_min": 3.0,
        "pipe_size_max": 42.0,
        "max_temp_f": 750,
        "max_insulation_thk_in": None,
        "remarks": "LOAD CAPACITY GREATER THAN FIG-G",
        "component_table_ready": True,
    },
    "J": {
        "role": "lower",
        "component_id": "M-6",
        "component_name": "PIPE CLAMP TYPE-C",
        "grinnell_fig_no": "295",
        "pipe_size_min": 0.75,
        "pipe_size_max": 24.0,
        "max_temp_f": 750,
        "max_insulation_thk_in": 4,
        "remarks": "",
        "component_table_ready": True,
    },
    "K": {
        "role": "lower",
        "component_id": "M-7",
        "component_name": "PIPE CLAMP TYPE-D",
        "grinnell_fig_no": "295H",
        "pipe_size_min": 6.0,
        "pipe_size_max": 36.0,
        "max_temp_f": 750,
        "max_insulation_thk_in": 4,
        "remarks": "LOAD CAPACITY GREATER THAN FIG-J",
        "component_table_ready": True,
    },
    "L": {
        "role": "lower",
        "component_id": "M-8",
        "component_name": "PIPE CLAMP TYPE-E",
        "grinnell_fig_no": "295A",
        "pipe_size_min": 1.5,
        "pipe_size_max": 10.0,
        "max_temp_f": 1050,
        "max_insulation_thk_in": 4,
        "remarks": "",
        "component_table_ready": False,
    },
    "M": {
        "role": "lower",
        "component_id": "M-9",
        "component_name": "PIPE CLAMP TYPE-F",
        "grinnell_fig_no": "224",
        "pipe_size_min": 4.0,
        "pipe_size_max": 16.0,
        "max_temp_f": 1050,
        "max_insulation_thk_in": 4,
        "remarks": "LOAD CAPACITY GREATER THAN FIG-L",
        "component_table_ready": False,
    },
    "N": {
        "role": "lower",
        "component_id": "M-10",
        "component_name": "PIPE CLAMP TYPE-G",
        "grinnell_fig_no": "246",
        "pipe_size_min": 10.0,
        "pipe_size_max": 24.0,
        "max_temp_f": 1075,
        "max_insulation_thk_in": 6,
        "remarks": "LOAD CAPACITY GREATER THAN FIG-M",
        "component_table_ready": False,
    },
    "Q": {
        "role": "lower",
        "component_id": "M-24",
        "component_name": "FORGED STEEL CLEVIS",
        "grinnell_fig_no": "299",
        "pipe_size_min": 2.0,
        "pipe_size_max": 24.0,
        "max_temp_f": 750,
        "max_insulation_thk_in": None,
        "remarks": "USES LUG PLATE TYPE-B (M-33)",
        "component_table_ready": True,
    },
}


def get_type62_part(fig: str) -> dict | None:
    row = TYPE62_PART_TABLE.get(str(fig).strip().upper())
    return deepcopy(row) if row else None


def get_type62_upper_part(fig: str) -> dict | None:
    row = get_type62_part(fig)
    return row if row and row["role"] == "upper" else None


def get_type62_lower_part(fig: str) -> dict | None:
    row = get_type62_part(fig)
    return row if row and row["role"] == "lower" else None


def validate_type62_lower_pipe_size(fig: str, line_size) -> tuple[bool, str]:
    row = get_type62_lower_part(fig)
    if not row:
        return False, f"FIG-{fig} is not a Type 62 lower part"

    size = size_to_float(normalize_fractional_size(line_size))
    if size is None:
        return False, f"Cannot parse line size {line_size!r}"

    min_size = row["pipe_size_min"]
    max_size = row["pipe_size_max"]
    if min_size is not None and size < min_size:
        return False, f"FIG-{fig} range is {min_size:g}\"~{max_size:g}\""
    if max_size is not None and size > max_size:
        return False, f"FIG-{fig} range is {min_size:g}\"~{max_size:g}\""
    return True, ""
