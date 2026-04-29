"""M-8 Pipe Clamp E metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M8_TABLE = build_metadata_component(
    component_id="M-8",
    name_en="PIPE CLAMP E",
    category="component",
    pdf_file="M-8-PIPE CLAMP E.pdf",
    summary="Metadata-only intake entry for M-8 pipe clamp E.",
    notes=["Clamp dimensions and load data require PDF visual transcription."],
)


def get_m8_component() -> dict:
    return clone_metadata_component(M8_TABLE)
