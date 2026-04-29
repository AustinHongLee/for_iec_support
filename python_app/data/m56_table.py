"""M-56 Pipe Clamp H metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M56_TABLE = build_metadata_component(
    component_id="M-56",
    name_en="PIPE CLAMP H",
    category="component",
    pdf_file="M-56-PIPE CLAMP H.pdf",
    summary="Metadata-only intake entry for M-56 pipe clamp H.",
    notes=["Clamp dimensions and load data require PDF visual transcription."],
)


def get_m56_component() -> dict:
    return clone_metadata_component(M56_TABLE)
