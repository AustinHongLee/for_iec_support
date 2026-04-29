"""N-22 Cradle No. of Cold Support metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N22_TABLE = build_metadata_component(
    component_id="N-22",
    name_en="CRADLE NO. OF COLD SUPPORT.3",
    category="component_cold",
    pdf_file="N-22-CRADLE NO. OF COLD SUPPORT.3.pdf",
    summary="Metadata-only intake entry for N-22 cold-support cradle.",
    notes=["Cradle dimensions require PDF visual transcription."],
)


def get_n22_component() -> dict:
    return clone_metadata_component(N22_TABLE)
