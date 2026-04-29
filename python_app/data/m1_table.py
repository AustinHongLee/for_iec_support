"""M-1 Special Base Plate metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M1_TABLE = build_metadata_component(
    component_id="M-1",
    name_en="SPECIAL BASE PLATE",
    category="component",
    pdf_file="M-1-SPECIAL BASE PLATE.pdf",
    summary="Metadata-only intake entry for M-1 special base plate.",
    notes=["Dimensions and weights require PDF visual transcription before lookup use."],
)


def get_m1_component() -> dict:
    return clone_metadata_component(M1_TABLE)
