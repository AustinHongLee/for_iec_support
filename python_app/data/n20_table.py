"""N-20 cradle selection lookup (small pipe, insulation 25~75 mm)."""

from .cold_support_core_tables import get_cradle_selection, get_selection_sheet_component


N20_TABLE = get_selection_sheet_component("N-20")


def get_n20_component() -> dict:
    return get_selection_sheet_component("N-20")


def get_n20_by_pipe_and_insulation(pipe_size_in, insulation_thickness_mm):
    row = get_cradle_selection(pipe_size_in, insulation_thickness_mm)
    return row if row and row["component_id"] == "N-20" else None
