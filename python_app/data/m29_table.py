"""M-29 Beam Attachment B metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M29_TABLE = build_metadata_component(
    component_id="M-29",
    name_en="BEAM ATTACHMENT B",
    category="component",
    pdf_file="M-29-BEAM ATTACHMENT B.pdf",
    summary="Metadata-only intake entry for M-29 beam attachment B.",
    notes=["Beam attachment dimensions, rod sizes, and weights require PDF visual transcription."],
)


def get_m29_component() -> dict:
    return clone_metadata_component(M29_TABLE)
