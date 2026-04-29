"""M-30 Beam Attachment C metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M30_TABLE = build_metadata_component(
    component_id="M-30",
    name_en="BEAM ATTACHMENT C",
    category="component",
    pdf_file="M-30-BEAM ATTACHMENT C.pdf",
    summary="Metadata-only intake entry for M-30 beam attachment C.",
    notes=["Beam attachment dimensions, rod sizes, and weights require PDF visual transcription."],
)


def get_m30_component() -> dict:
    return clone_metadata_component(M30_TABLE)
