"""N-3 cold support layer-construction rules."""

from copy import deepcopy

from .cold_support_core_tables import (
    SOURCE_REVISION,
    SOURCE_STANDARD,
    get_n3_construction,
)


N3_TABLE = {
    "component_id": "N-3",
    "name_en": "COLD SUPPORT LAYER CONSTRUCTION",
    "category": "component_cold",
    "pdf_file": "N-3-COLD SUPPORT LAYER CONSTRUCTION.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "construction_rule_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "source_transcribed": True,
    "axial_rules": {
        "jacket": "L + 100 mm",
        "foam_and_vapor_barrier": "L + 150 mm",
        "inner_layer_foam_for_multilayer": "L + 200 mm",
    },
    "notes": ["Dimensions/information not shown are delegated to C-14."],
}


def get_n3_component() -> dict:
    return deepcopy(N3_TABLE)


def get_n3_by_total_thickness(total_thickness_mm, cradle_length_mm=None) -> dict:
    return get_n3_construction(total_thickness_mm, cradle_length_mm)
