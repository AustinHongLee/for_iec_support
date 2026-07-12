"""
N-8 Strap-1 metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N8_TABLE = build_metadata_component(
    component_id="N-8",
    name_en="STRAP-1",
    category="component_cold",
    pdf_file="N-8-STRAP-1.pdf",
    summary="Metadata-only entry for the first cold-support strap variant.",
)


def get_n8_component() -> dict:
    return clone_metadata_component(N8_TABLE)
