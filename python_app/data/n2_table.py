"""
N-2 Cold Support Layer metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N2_TABLE = build_metadata_component(
    component_id="N-2",
    name_en="COLD SUPPORT LAYER",
    category="component_cold",
    pdf_file="N-2-COLD SUPPORT LAYER.pdf",
    summary="Metadata-only entry for the cold-support insulation layer component.",
)


def get_n2_component() -> dict:
    return clone_metadata_component(N2_TABLE)
