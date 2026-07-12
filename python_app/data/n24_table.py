"""N-24 Cradle No. of Cold Support metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N24_TABLE = build_metadata_component(
    component_id="N-24",
    name_en="CRADLE NO. OF COLD SUPPORT.5",
    category="component_cold",
    pdf_file="N-24-CRADLE NO. OF COLD SUPPORT.5.pdf",
    summary="Metadata-only intake entry for N-24 cold-support cradle.",
    notes=["Cradle dimensions require PDF visual transcription."],
)


def get_n24_component() -> dict:
    return clone_metadata_component(N24_TABLE)
