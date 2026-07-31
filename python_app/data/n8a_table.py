"""N-8A line-size-selected strap dimensional lookup."""

from copy import deepcopy

from .cold_restraint_tables import N8A_TABLE, get_n8a_by_line_size


def get_n8a_component() -> dict:
    return {
        "component_id": "N-8A",
        "name_en": "STRAP",
        "category": "component_cold",
        "pdf_file": "N-8A-STRAP-2.pdf",
        "engineering_standard": "DSP-500-006",
        "revision": "0",
        "table_kind": "dimensional_lookup",
        "lookup_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "row_count": len(N8A_TABLE),
        "line_size_range": '6"/8"/10"',
        "rows": deepcopy(N8A_TABLE),
    }


__all__ = ["N8A_TABLE", "get_n8a_component", "get_n8a_by_line_size"]
