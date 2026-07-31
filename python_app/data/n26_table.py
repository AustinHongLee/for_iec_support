"""N-26 cradle selection lookup (large pipe, insulation 150~200 mm)."""

from .cold_support_core_tables import get_cradle_selection, get_selection_sheet_component


N26_TABLE = get_selection_sheet_component("N-26")


def get_n26_component() -> dict:
    return get_selection_sheet_component("N-26")


def get_n26_by_pipe_and_insulation(pipe_size_in, insulation_thickness_mm):
    row = get_cradle_selection(pipe_size_in, insulation_thickness_mm)
    return row if row and row["component_id"] == "N-26" else None
