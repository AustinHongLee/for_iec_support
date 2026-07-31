"""N-5 molded Thermaform material-property lookup."""

from copy import deepcopy

from .cold_support_core_tables import (
    N5_MATERIAL_PROPERTIES,
    SOURCE_REVISION,
    SOURCE_STANDARD,
    get_n5_material_properties,
)


N5_TABLE = {
    "component_id": "N-5",
    "name_en": "MODLDED THERMAFORM",
    "category": "component_cold",
    "pdf_file": "N-5-MODLDED THERMAFORM.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "material_property_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "source_transcribed": True,
    "densities_kg_m3": list(N5_MATERIAL_PROPERTIES),
    "notes": [
        "Properties are source test data; finished molded volume remains unresolved.",
        "Allowable load must be adjusted for service temperature other than -160C.",
    ],
}


def get_n5_component() -> dict:
    return deepcopy(N5_TABLE)


def get_n5_by_density(density_kg_m3) -> dict | None:
    return get_n5_material_properties(density_kg_m3)
