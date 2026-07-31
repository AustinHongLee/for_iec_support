"""N-7A Type-SUB1 special U-bolt dimensional lookup."""

from copy import deepcopy

from .cold_restraint_tables import N7A_TABLE, get_n7a_by_cradle


def get_n7a_component() -> dict:
    return {
        "component_id": "N-7A",
        "name_en": "SPECIAL U-BOLT TYPE-SUB1",
        "category": "component_cold",
        "pdf_file": "N-7A-SPECIAL U-BOLT SUB1.pdf",
        "engineering_standard": "DSP-500-006",
        "revision": "0",
        "table_kind": "dimensional_lookup",
        "lookup_ready": True,
        "rod_weight_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "row_count": len(N7A_TABLE),
        "cradle_range": "CR2.5~CR29",
        "rows": deepcopy(N7A_TABLE),
    }


__all__ = ["N7A_TABLE", "get_n7a_component", "get_n7a_by_cradle"]
