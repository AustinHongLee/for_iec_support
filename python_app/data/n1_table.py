"""N-1 cold insulation support dimensional lookup."""

from copy import deepcopy

from .cold_support_core_tables import (
    CRADLE_RADII_MM,
    N1_LARGE_A_MM,
    SOURCE_REVISION,
    SOURCE_STANDARD,
    get_n1_dimensions,
)


N1_TABLE = {
    "component_id": "N-1",
    "name_en": "COLD INSULATION SUPPORT",
    "category": "component_cold",
    "pdf_file": "N-1-COLD INSULATION SUPPORT.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "source_transcribed": True,
    "cradle_count": len(CRADLE_RADII_MM),
    "large_pipe_A_row_count": len(N1_LARGE_A_MM),
    "notes": [
        "Small-pipe and 30in-and-larger tables have different T1 at CR41~CR44",
        "N-1 does not identify steel material grade or all host-specific developments",
    ],
}


def get_n1_component() -> dict:
    return deepcopy(N1_TABLE)


def get_n1_by_cradle(cradle_no, pipe_size_in) -> dict | None:
    return get_n1_dimensions(cradle_no, pipe_size_in)
