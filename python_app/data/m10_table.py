"""M-10 Pipe Clamp G metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M10_TABLE = build_metadata_component(
    component_id="M-10",
    name_en="PIPE CLAMP G",
    category="component",
    pdf_file="M-10-PIPE CLAMP G.pdf",
    summary="Metadata-only intake entry for M-10 pipe clamp G.",
    notes=["Clamp dimensions and load data require PDF visual transcription."],
)


def get_m10_component() -> dict:
    return clone_metadata_component(M10_TABLE)
