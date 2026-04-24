"""N-23 Cradle No. of Cold Support metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N23_TABLE = build_metadata_component(
    component_id="N-23",
    name_en="CRADLE NO. OF COLD SUPPORT.4",
    category="component_cold",
    pdf_file="N-23-CRADLE NO. OF COLD SUPPORT.4.pdf",
    summary="Metadata-only intake entry for N-23 cold-support cradle.",
    notes=["Cradle dimensions require PDF visual transcription."],
)


def get_n23_component() -> dict:
    return clone_metadata_component(N23_TABLE)
