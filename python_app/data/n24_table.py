"""N-24 cradle selection lookup (large pipe, insulation 25~75 mm)."""

from .cold_support_core_tables import get_cradle_selection, get_selection_sheet_component


N24_TABLE = get_selection_sheet_component("N-24")


def get_n24_component() -> dict:
    return get_selection_sheet_component("N-24")


def get_n24_by_pipe_and_insulation(pipe_size_in, insulation_thickness_mm):
    row = get_cradle_selection(pipe_size_in, insulation_thickness_mm)
    return row if row and row["component_id"] == "N-24" else None
