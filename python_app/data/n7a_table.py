"""
N-7A Special U-Bolt Sub1 metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N7A_TABLE = build_metadata_component(
    component_id="N-7A",
    name_en="SPECIAL U-BOLT SUB1",
    category="component_cold",
    pdf_file="N-7A-SPECIAL U-BOLT SUB1.pdf",
    summary="Metadata-only entry for the N-7A cold-support U-bolt variant.",
)


def get_n7a_component() -> dict:
    return clone_metadata_component(N7A_TABLE)
