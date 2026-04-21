"""M-41 Lug Plate P metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M41_TABLE = build_metadata_component(
    component_id="M-41",
    name_en="LUG PLATE P",
    category="component",
    pdf_file="M-41-LUG PLATE P.pdf",
    summary="Metadata-only intake entry for M-41 lug plate P.",
    notes=["Referenced by Type 49 FIG-A; dimensions and weights require PDF visual transcription."],
)


def get_m41_component() -> dict:
    return clone_metadata_component(M41_TABLE)
