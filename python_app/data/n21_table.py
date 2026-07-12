"""N-21 Cradle No. of Cold Support metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N21_TABLE = build_metadata_component(
    component_id="N-21",
    name_en="CRADLE NO. OF COLD SUPPORT.2",
    category="component_cold",
    pdf_file="N-21-CRADLE NO. OF COLD SUPPORT.2.pdf",
    summary="Metadata-only intake entry for N-21 cold-support cradle.",
    notes=["Cradle dimensions require PDF visual transcription."],
)


def get_n21_component() -> dict:
    return clone_metadata_component(N21_TABLE)
