"""N-25 cradle selection lookup (large pipe, insulation 90~140 mm)."""

from .cold_support_core_tables import get_cradle_selection, get_selection_sheet_component


N25_TABLE = get_selection_sheet_component("N-25")


def get_n25_component() -> dict:
    return get_selection_sheet_component("N-25")


def get_n25_by_pipe_and_insulation(pipe_size_in, insulation_thickness_mm):
    row = get_cradle_selection(pipe_size_in, insulation_thickness_mm)
    return row if row and row["component_id"] == "N-25" else None
