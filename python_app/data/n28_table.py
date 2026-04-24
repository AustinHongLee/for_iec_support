"""N-28 Wood Block metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N28_TABLE = build_metadata_component(
    component_id="N-28",
    name_en="WOOD BLOCK",
    category="component_cold",
    pdf_file="N-28-WOOD BLOCK.pdf",
    summary="Metadata-only intake entry for N-28 wood block.",
    notes=["Wood block dimensions and material assumptions require PDF visual transcription."],
)


def get_n28_component() -> dict:
    return clone_metadata_component(N28_TABLE)
