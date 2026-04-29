"""N-26 Cradle No. of Cold Support metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N26_TABLE = build_metadata_component(
    component_id="N-26",
    name_en="CRADLE NO. OF COLD SUPPORT.7",
    category="component_cold",
    pdf_file="N-26-CRADLE NO. OF COLD SUPPORT.7.pdf",
    summary="Metadata-only intake entry for N-26 cold-support cradle.",
    notes=["Cradle dimensions require PDF visual transcription."],
)


def get_n26_component() -> dict:
    return clone_metadata_component(N26_TABLE)
