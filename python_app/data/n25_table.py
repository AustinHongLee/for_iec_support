"""N-25 Cradle No. of Cold Support metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N25_TABLE = build_metadata_component(
    component_id="N-25",
    name_en="CRADLE NO. OF COLD SUPPORT.6",
    category="component_cold",
    pdf_file="N-25-CRADLE NO. OF COLD SUPPORT.6.pdf",
    summary="Metadata-only intake entry for N-25 cold-support cradle.",
    notes=["Cradle dimensions require PDF visual transcription."],
)


def get_n25_component() -> dict:
    return clone_metadata_component(N25_TABLE)
