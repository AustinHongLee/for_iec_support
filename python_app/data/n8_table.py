"""N-8 cradle-selected strap dimensional lookup."""

from copy import deepcopy

from .cold_restraint_tables import N8_TABLE, get_n8_by_cradle


def get_n8_component() -> dict:
    return {
        "component_id": "N-8",
        "name_en": "STRAP",
        "category": "component_cold",
        "pdf_file": "N-8-STRAP-1.pdf",
        "engineering_standard": "DSP-500-006",
        "revision": "0",
        "table_kind": "dimensional_lookup",
        "lookup_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "row_count": len(N8_TABLE),
        "cradle_range": "CR5~CR25",
        "rows": deepcopy(N8_TABLE),
    }


__all__ = ["N8_TABLE", "get_n8_component", "get_n8_by_cradle"]
