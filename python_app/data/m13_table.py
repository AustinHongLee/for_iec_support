"""M-13 Pipe Roll A metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M13_TABLE = build_metadata_component(
    component_id="M-13",
    name_en="PIPE ROLL A",
    category="component",
    pdf_file="M-13-PIPE ROLL A.pdf",
    summary="Metadata-only intake entry for M-13 pipe roll A.",
    notes=["Roll assembly dimensions and weight require PDF visual transcription."],
)


def get_m13_component() -> dict:
    return clone_metadata_component(M13_TABLE)
