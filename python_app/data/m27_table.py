"""M-27 Angle Bracket metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M27_TABLE = build_metadata_component(
    component_id="M-27",
    name_en="ANGLE BRACKET",
    category="component",
    pdf_file="M-27-ANGLE BRACKET.pdf",
    summary="Metadata-only intake entry for M-27 angle bracket.",
    notes=["Bracket dimensions and loads require PDF visual transcription."],
)


def get_m27_component() -> dict:
    return clone_metadata_component(M27_TABLE)
