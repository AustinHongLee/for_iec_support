"""N-2 cold support layer-thickness lookup."""

from copy import deepcopy

from .cold_support_core_tables import (
    N2_LAYER_SYSTEMS,
    SOURCE_REVISION,
    SOURCE_STANDARD,
    get_n2_layer_system,
)


N2_TABLE = {
    "component_id": "N-2",
    "name_en": "COLD SUPPORT LAYER",
    "category": "component_cold",
    "pdf_file": "N-2-COLD SUPPORT LAYER.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "layer_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "source_transcribed": True,
    "total_thicknesses_mm": list(N2_LAYER_SYSTEMS),
    "notes": ["Layer system shall match the project cold-insulation system."],
}


def get_n2_component() -> dict:
    return deepcopy(N2_TABLE)


def get_n2_by_total_thickness(total_thickness_mm) -> dict | None:
    return get_n2_layer_system(total_thickness_mm)
