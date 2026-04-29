"""M-9 Pipe Clamp F metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M9_TABLE = build_metadata_component(
    component_id="M-9",
    name_en="PIPE CLAMP F",
    category="component",
    pdf_file="M-9-PIPE CLAMP F.pdf",
    summary="Metadata-only intake entry for M-9 pipe clamp F.",
    notes=["Clamp dimensions and load data require PDF visual transcription."],
)


def get_m9_component() -> dict:
    return clone_metadata_component(M9_TABLE)
