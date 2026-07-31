"""N-23 cradle selection lookup (small pipe, insulation 215~265 mm)."""

from .cold_support_core_tables import get_cradle_selection, get_selection_sheet_component


N23_TABLE = get_selection_sheet_component("N-23")


def get_n23_component() -> dict:
    return get_selection_sheet_component("N-23")


def get_n23_by_pipe_and_insulation(pipe_size_in, insulation_thickness_mm):
    row = get_cradle_selection(pipe_size_in, insulation_thickness_mm)
    return row if row and row["component_id"] == "N-23" else None
