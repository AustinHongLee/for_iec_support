"""
N-3 Cold Support Layer Construction metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N3_TABLE = build_metadata_component(
    component_id="N-3",
    name_en="COLD SUPPORT LAYER CONSTRUCTION",
    category="component_cold",
    pdf_file="N-3-COLD SUPPORT LAYER CONSTRUCTION.pdf",
    summary="Metadata-only entry for N-2 layer construction/detail rules.",
)


def get_n3_component() -> dict:
    return clone_metadata_component(N3_TABLE)
