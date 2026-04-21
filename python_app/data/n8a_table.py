"""
N-8A Strap-2 metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N8A_TABLE = build_metadata_component(
    component_id="N-8A",
    name_en="STRAP-2",
    category="component_cold",
    pdf_file="N-8A-STRAP-2.pdf",
    summary="Metadata-only entry for the second cold-support strap variant.",
)


def get_n8a_component() -> dict:
    return clone_metadata_component(N8A_TABLE)
