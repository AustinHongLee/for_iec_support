"""
N-6 Special Base Plate metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N6_TABLE = build_metadata_component(
    component_id="N-6",
    name_en="SPECIAL BASE PLATE",
    category="component_cold",
    pdf_file="N-6-SPECIAL BASE PLATE.pdf",
    summary="Metadata-only entry for the special base plate used in the cold-support family.",
)


def get_n6_component() -> dict:
    return clone_metadata_component(N6_TABLE)
