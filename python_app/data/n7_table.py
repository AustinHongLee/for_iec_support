"""N-7 Type-SUB special U-bolt dimensional lookup."""

from copy import deepcopy

from .cold_restraint_tables import N7_TABLE, get_n7_by_cradle


def get_n7_component() -> dict:
    return {
        "component_id": "N-7",
        "name_en": "SPECIAL U-BOLT TYPE-SUB",
        "category": "component_cold",
        "pdf_file": "N-7-SPECIAL U-BOLT SUB.pdf",
        "engineering_standard": "DSP-500-006",
        "revision": "0",
        "table_kind": "dimensional_lookup",
        "lookup_ready": True,
        "rod_weight_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "row_count": len(N7_TABLE),
        "cradle_range": "CR2.5~CR29",
        "rows": deepcopy(N7_TABLE),
    }


__all__ = ["N7_TABLE", "get_n7_component", "get_n7_by_cradle"]
