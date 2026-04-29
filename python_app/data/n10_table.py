"""N-10 Lower Component of Base Cold Support metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N10_TABLE = build_metadata_component(
    component_id="N-10",
    name_en="LOWER COMPONENT OF BASE COLD SUPPORT.2",
    category="component_cold",
    pdf_file="N-10-LOWER COMPONENT OF BASE COLD SUPPORT.2.pdf",
    summary="Metadata-only intake entry for N-10 cold-support lower component.",
    notes=["Cold-support lower component dimensions require PDF visual transcription."],
)


def get_n10_component() -> dict:
    return clone_metadata_component(N10_TABLE)
