"""N-4 galvanized cold-insulation protection-shield lookup."""

from copy import deepcopy

from .cold_support_core_tables import (
    SOURCE_REVISION,
    SOURCE_STANDARD,
    get_n4_shield,
)


N4_TABLE = {
    "component_id": "N-4",
    "name_en": "COLD INSULATION PROTECTION",
    "category": "component_cold",
    "pdf_file": "N-4-COLD INSULATION PROTECTION.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "source_transcribed": True,
    "thickness_rules_mm": {
        "CR2.5~CR12": 1.6,
        "CR14~CR39": 3.0,
        "CR40~CR80": 5.0,
    },
    "notes": ["Shield axial length equals the host steel cradle length."],
}


def get_n4_component() -> dict:
    return deepcopy(N4_TABLE)


def get_n4_by_cradle(cradle_no, cradle_length_mm=None) -> dict | None:
    return get_n4_shield(cradle_no, cradle_length_mm)
